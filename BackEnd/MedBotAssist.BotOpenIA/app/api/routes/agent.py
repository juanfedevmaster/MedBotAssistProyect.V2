from fastapi import APIRouter, HTTPException, Depends, status, Header
from fastapi.security import HTTPBearer
from app.models.schemas import (
    AgentQueryRequest,
    AgentQueryResponse,
    ConversationHistoryResponse,
    ErrorResponse
)
from app.agents.medical_agent import MedicalQueryAgent
from app.services.jwt_service import JWTService
from app.services.chatbot_interaction_service import ChatbotInteractionService
import time
from typing import Dict, Any, Optional
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

# Global instances
medical_agent = None
jwt_service = JWTService()
interaction_service = ChatbotInteractionService()

def get_medical_agent() -> MedicalQueryAgent:
    """Dependency to get or create medical agent instance."""
    global medical_agent
    if medical_agent is None:
        medical_agent = MedicalQueryAgent()
    return medical_agent

@router.post(
    "/chat",
    response_model=AgentQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat with the medical query agent",
    description="Send natural language queries to the medical agent for patient information",
    responses={
        200: {"description": "Successful agent response"},
        400: {"model": ErrorResponse, "description": "Bad request"},
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid JWT token"},
        403: {"model": ErrorResponse, "description": "Forbidden - Insufficient permissions"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def chat_with_agent(
    request: AgentQueryRequest,
    agent: MedicalQueryAgent = Depends(get_medical_agent),
    authorization: str = Header(None, alias="Authorization")
) -> AgentQueryResponse:
    """
    Chat with the medical query agent using natural language.
    
    The agent can help you with:
    - Searching for patients by description
    - Getting patient database summaries  
    - Filtering patients by demographics
    - Answering questions about patient data
    
    Examples:
    - "Show me all male patients aged 45"
    - "Find patients with type O+ blood"
    - "How many patients do we have?"
    - "Search for patients with diabetes"
    
    **Authentication Required:** Valid JWT token with appropriate permissions.
    """
    try:
        # Validate JWT token
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header required"
            )
            
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format. Expected 'Bearer <token>'"
            )
            
        token = authorization.split(" ")[1]
        
        # 1. Decode and validate JWT token
        try:
            user_permissions = jwt_service.get_user_permissions(token)
            username = jwt_service.extract_username(token)
            user_id = jwt_service.extract_user_id(token)
            
            logger.info(f"User '{username}' authenticated successfully with {len(user_permissions)} permissions")
            
        except Exception as e:
            logger.error(f"JWT validation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid JWT token: {str(e)}"
            )
        
        start_time = time.time()

        # 2. Generate conversation ID if not provided
        conversation_id = request.conversation_id or f"conv_{uuid.uuid4().hex[:8]}"
        
        # 3. Process query with agent - pass user permissions context
        result = await agent.query(
            message=request.message,
            conversation_id=conversation_id,
            user_permissions=user_permissions,
            username=username,
            jwt_token=token
        )
        
        # 4. Get available tools
        available_tools = [tool["name"] for tool in agent.get_available_tools()]
        
        response = AgentQueryResponse(
            response=result["response"],
            conversation_id=conversation_id,
            agent_used_tools=result.get("agent_used_tools", False),
            available_tools=available_tools,
            status=result.get("status", "success")
        )
        
        # 5. Save interaction to database
        try:
            interaction_id = interaction_service.save_interaction(
                user_id=user_id,
                user_message=request.message,
                bot_response=result["response"],
                conversation_id=conversation_id
            )
            if interaction_id:
                logger.info(f"Interaction {interaction_id} saved for user '{username}' in conversation '{conversation_id}'")
            else:
                logger.warning(f"Failed to save interaction for user '{username}' - no interaction ID returned")
        except Exception as e:
            logger.error(f"Failed to save interaction to database: {e}")
            # We don't want to fail the request if logging fails
        
        processing_time = (time.time() - start_time) * 1000
        logger.info(f"Agent query processed in {processing_time:.2f}ms")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in agent chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing agent query: {str(e)}"
        )

@router.get(
    "/tools",
    summary="Get available agent tools",
    description="List all tools available to the medical query agent"
)
async def get_agent_tools(
    agent: MedicalQueryAgent = Depends(get_medical_agent)
) -> Dict[str, Any]:
    """
    Get a list of all tools available to the medical agent.
    """
    try:
        tools = agent.get_available_tools()
        
        return {
            "tools": tools,
            "total_tools": len(tools),
            "agent_type": "medical_query_agent",
            "capabilities": [
                "Patient search and retrieval",
                "Database statistics and summaries", 
                "Demographic filtering",
                "Natural language query processing"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting agent tools: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting agent tools: {str(e)}"
        )

@router.get(
    "/conversation/{conversation_id}",
    response_model=ConversationHistoryResponse,
    summary="Get conversation history",
    description="Retrieve conversation history for a specific conversation ID"
)
async def get_conversation_history(
    conversation_id: str,
    agent: MedicalQueryAgent = Depends(get_medical_agent)
) -> ConversationHistoryResponse:
    """
    Get conversation history for a specific conversation.
    """
    try:
        history = agent.get_conversation_history(conversation_id)
        
        return ConversationHistoryResponse(
            conversation_id=conversation_id,
            messages=history,
            total_messages=len(history)
        )
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting conversation history: {str(e)}"
        )

@router.delete(
    "/conversation/{conversation_id}",
    summary="Clear conversation history",
    description="Clear conversation history for a specific conversation ID"
)
async def clear_conversation_history(
    conversation_id: str,
    agent: MedicalQueryAgent = Depends(get_medical_agent)
) -> Dict[str, Any]:
    """
    Clear conversation history for a specific conversation.
    """
    try:
        agent.clear_conversation_history(conversation_id)
        
        return {
            "message": f"Conversation history cleared for conversation {conversation_id}",
            "conversation_id": conversation_id,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error clearing conversation history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing conversation history: {str(e)}"
        )

@router.post(
    "/health",
    summary="Check agent health",
    description="Check if the medical query agent is working properly"
)
async def check_agent_health(
    agent: MedicalQueryAgent = Depends(get_medical_agent)
) -> Dict[str, Any]:
    """
    Check the health status of the medical query agent.
    """
    try:
        # 1. Test basic agent functionality
        test_query = "How many patients are in the database?"
        result = await agent.query(test_query, "health_check")
        
        return {
            "status": "healthy" if result["status"] == "success" else "unhealthy",
            "agent_initialized": agent.agent_executor is not None,
            "llm_configured": agent.llm is not None,
            "tools_available": len(agent.get_available_tools()),
            "test_query_successful": result["status"] == "success",
            "message": "Medical query agent is operational"
        }
        
    except Exception as e:
        logger.error(f"Agent health check failed: {e}")
        return {
            "status": "unhealthy",
            "agent_initialized": False,
            "llm_configured": False,
            "tools_available": 0,
            "test_query_successful": False,
            "error": str(e),
            "message": "Medical query agent has issues"
        }

@router.post(
    "/permissions",
    summary="Get user permissions from JWT",
    description="Extract username from JWT and retrieve user permissions from database"
)
async def get_user_permissions(authorization: str = Header(...)) -> Dict[str, Any]:
    """
    Obtains user permissions from the database using the JWT.
    
    Headers:
        Authorization: Bearer {jwt_token}
    
    Returns:
        User information and permissions
    """
    try:
        # 1. Extract token from Authorization header
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format. Expected 'Bearer {token}'"
            )
        
        token = authorization.replace("Bearer ", "")
        
        # 2. Get full token information and permissions
        token_info = jwt_service.get_token_info(token)
        
        return {
            "status": "success",
            "user_info": {
                "username": token_info["username"],
                "total_permissions": token_info["total_permissions"]
            },
            "permissions": token_info["permissions"],
            "permission_names": token_info["permission_names"],
            "token_claims": {
                "issuer": token_info["token_payload"].get("iss"),
                "audience": token_info["token_payload"].get("aud"),
                "expires": token_info["token_payload"].get("exp"),
                "subject": token_info["token_payload"].get("sub")
            },
            "message": f"Found {token_info['total_permissions']} permissions for user '{token_info['username']}'"
        }
        
    except HTTPException as e:
        # Re-raise HTTPExceptions (JWT errors, etc.) to be handled by FastAPI
        logger.error(f"JWT error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error getting user permissions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user permissions: {str(e)}"
        )


