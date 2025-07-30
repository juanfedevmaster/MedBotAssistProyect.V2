from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    database_status: str = Field(..., description="Database connection status")
    openai_status: str = Field(..., description="OpenAI connection status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")

# Chatbot Interaction Schemas
class ChatbotInteractionCreate(BaseModel):
    user_id: str = Field(..., description="User ID from JWT token")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Interaction timestamp")
    interaction_type: str = Field(..., description="Type of interaction (Appointment, Summary, etc.)")
    user_message: str = Field(..., description="Original user message")
    bot_response: str = Field(..., description="Agent's response")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID")

class ChatbotInteractionResponse(BaseModel):
    interaction_id: int = Field(..., description="Interaction ID")
    user_id: str = Field(..., description="User ID")
    timestamp: datetime = Field(..., description="Interaction timestamp")
    interaction_type: str = Field(..., description="Type of interaction")
    user_message: str = Field(..., description="User message")
    bot_response: str = Field(..., description="Bot response")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID")

# Agent Schemas
class AgentQueryRequest(BaseModel):
    message: str = Field(
        ...,
        description="Natural language message to the medical agent",
        min_length=1,
        max_length=2000,
        example="Show me all male patients aged 45"
    )
    
    conversation_id: Optional[str] = Field(
        default=None,
        description="Optional conversation ID to maintain context",
        example="conv_123456"
    )

class AgentQueryResponse(BaseModel):
    response: str = Field(..., description="Agent's response to the query")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID")
    agent_used_tools: bool = Field(..., description="Whether the agent used tools to answer")
    available_tools: List[str] = Field(default=[], description="List of available tools")
    status: str = Field(..., description="Response status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

class ConversationHistoryResponse(BaseModel):
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID")
    messages: List[Dict[str, Any]] = Field(..., description="Conversation messages")
    total_messages: int = Field(..., description="Total number of messages")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
