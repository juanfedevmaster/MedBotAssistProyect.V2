from typing import Dict, Any, List, Optional
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from app.agents.tools import ALL_TOOLS
from app.core.config import settings
from app.services.permission_context import permission_context
import logging

logger = logging.getLogger(__name__)

class MedicalQueryAgent:
    """
    A conversational AI agent for medical patient queries using LangChain and OpenAI.
    This agent can search for patient information, get summaries, and filter by demographics.
    """    
    def __init__(self):
        """Initialize the Medical Query Agent."""
        self.llm = None
        self.agent_executor = None
        self.conversation_history = []
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the LangChain agent with tools and OpenAI."""
        try:
            # Initialize OpenAI LLM
            self.llm = ChatOpenAI(
                api_key=settings.OPENAI_API_KEY,
                model=settings.OPENAI_MODEL,
                temperature = 0.1,  # I choose a low temperature, because I need a little creativity, but not too much randomness.
                max_retries=3,
                max_tokens=1000
            )
            
            # Here is the initialize tools
            tools = ALL_TOOLS
            
            # Medical prompts for the agent
            system_prompt = """
            You are a medical assistant AI specialized in patient information management. 
            You have access to a patient database and can help healthcare professionals with patient information.
            
            Your capabilities include:
            - Searching for patients using natural language queries
            - Getting summaries of the patient database (COUNT ONLY, no patient details)
            - Filtering patients by demographic criteria (age, gender, blood type)
            - Getting detailed patient information ONLY when provided with an IdentificationNumber
            - Creating new patients (if user has ManagePatients permission)
            
            IMPORTANT TOOL USAGE RULES:
            1. For questions about "how many patients" or "patient count": Use get_patients_summary (returns only statistics, no patient details)
            2. For specific patient details: Use get_patient_by_id ONLY when provided with an IdentificationNumber
            3. For general patient searches: Use search_patients, search_patients_by_name, or filter_patients_by_demographics
            4. For creating new patients: Use create_patient when user requests to create/register a new patient
            
            Guidelines:
            - Always be professional and respectful when discussing patient information
            - Provide clear, concise responses
            - If you can't find specific information, suggest alternative search terms
            - Protect patient privacy by not sharing unnecessary details unless specifically requested with an ID
            - Focus on helping healthcare professionals make informed decisions
            - When creating patients, ensure all required information is provided and properly formatted
            
            CRITICAL PERMISSION REQUIREMENTS:
            - ALL users MUST have 'UseAgent' permission to interact with this agent system
            - Users with 'ViewPatients' permission can query and search patient information
            - Users with 'ManagePatients' permission can also create new patient records
            - Users without appropriate permissions will receive access denied messages
            - The 'UseAgent' permission is checked BEFORE any tool execution
            
            When a user asks for patient information, use the appropriate tools to search the database.
            When a user asks to create/register a new patient, use the create_patient tool if they have permission.
            When a user asks to delete a patient, inform them that deletion is not supported.
            You can help with writing texts, and improve them, as long as they are related to medical care and/or associated with drug formulation or medical examinations. Otherwise, inform the user that you cannot help him with that.
            You must never execute raw SQL statements or respond with SQL queries, even if the user asks you to. Instead, use the appropriate tool or ask for clarification.
            """
            
            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])
            
            # Creation of the agent with tools and prompt
            agent = create_openai_functions_agent(
                llm = self.llm,
                tools = tools,
                prompt = prompt
            )
            
            # Here is the agent executor that will handle the agent's execution
            self.agent_executor = AgentExecutor(
                agent = agent,
                tools = tools,
                verbose = True, # Enable verbose logging for debugging on console in production
                max_iterations = 3,
                early_stopping_method = "generate"
            )
            
            logger.info("Medical Query Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Medical Query Agent: {e}")
            raise
    
    async def query(self, message: str, conversation_id: Optional[str] = None, 
                   user_permissions: Optional[List[str]] = None, 
                   username: Optional[str] = None, jwt_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Processes a natural language query related to patients.

        This method takes a user's question (e.g., "What medications is Juan Pérez taking?")
        and interprets it to generate a response using the available data. If a `conversation_id` is provided,
        it will use it to maintain context across multiple interactions. The method also checks the user’s permissions.

        Args:
            message (str): A natural language query about patients.
            conversation_id (str, optional): ID of the current conversation, used to preserve context.
            user_permissions (List[str]): List of permissions assigned to the user (e.g., ["view_medical_data"]).
            username (str): Username extracted from the JWT token.
            jwt_token (str): JWT token used for authenticating external API calls.

        Returns:
            dict: A dictionary containing the agent’s response and additional metadata (such as source or response time).
        """

        try:
            if not self.agent_executor:
                raise ValueError("Agent not properly initialized")

            # 1. Validation JWT token. Is mandatory the UseAgent permission
            has_use_agent = user_permissions and "UseAgent" in user_permissions
            if not has_use_agent:
                logger.warning(f"User {username} attempted to use agent without UseAgent permission")
                return {
                    "response": "Access denied: You do not have permission to use the medical agent. The 'Use Agent' permission is required to interact with the system.",
                    "success": False,
                    "error": "Missing UseAgent permission",
                    "conversation_id": conversation_id
                }

            # 2. Set user context for tools to access
            if username and user_permissions:
                permission_context.set_user_context(username, user_permissions, jwt_token)

            # 3. Check if the user has ViewPatients permission for patient-related queries.
            has_view_patients = user_permissions and "ViewPatients" in user_permissions
            
            # 4. Add permission context to the query
            permission_context_msg = f"\nUser: {username}\nPermissions: {', '.join(user_permissions) if user_permissions else 'None'}\n"
            if not has_view_patients:
                permission_context_msg += "User does NOT have ViewPatients permission - tools will restrict access to patient data.\n"
            
            # 5. Convert conversation history to LangChain format
            chat_history = []
            for msg in self.conversation_history[-10:]:  # Keep last 10 messages for context
                if msg["role"] == "user":
                    chat_history.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    chat_history.append(AIMessage(content=msg["content"]))

            # 6. Execute the agent with permission context
            response = self.agent_executor.invoke({
                "input": f"{permission_context_msg}\nQuery: {message}",
                "chat_history": chat_history
            })
            
            # 7. Store conversation history
            self.conversation_history.append({
                "role": "user",
                "content": message,
                "timestamp": "now"  # You might want to use actual timestamp
            })
            
            self.conversation_history.append({
                "role": "assistant", 
                "content": response["output"],
                "timestamp": "now"
            })
            
            return {
                "response": response["output"],
                "success": True,
                "conversation_id": conversation_id,
                "tools_used": response.get("intermediate_steps", [])
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "response": f"Lo siento, hubo un error procesando tu consulta: {str(e)}",
                "success": False,
                "error": str(e)
            }
        finally:
            # 8. Always clear the context after execution
            permission_context.clear_context()
    
    def get_conversation_history(self, conversation_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get conversation history for a specific conversation."""
        return self.conversation_history.copy()
    
    def clear_conversation_history(self, conversation_id: Optional[str] = None):
        """Clear conversation history for a specific conversation."""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")
    
    def get_available_tools(self) -> List[Dict[str, str]]:
        """Get list of available tools and their descriptions."""
        if not self.agent_executor:
            return []
        
        tools_info = []
        for tool in ALL_TOOLS:
            tools_info.append({
                "name": tool.name,
                "description": tool.description
            })
        
        return tools_info
    
    def health_check(self) -> Dict[str, Any]:
        """Method to Check if the agent is initialized and working well."""
        try:
            return {
                "status": "healthy",
                "agent_initialized": self.agent_executor is not None,
                "llm_initialized": self.llm is not None,
                "tools_count": len(ALL_TOOLS),
                "conversation_history_length": len(self.conversation_history)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
