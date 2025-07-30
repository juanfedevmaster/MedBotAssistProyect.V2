from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class ChatbotInteraction(Base):
    """
    Model for storing chatbot interactions in the database.
    
    Table: ChatbotInteractions
    """
    __tablename__ = "ChatbotInteractions"
    
    InteractionId = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    UserId = Column(String(255), nullable=False, index=True)
    Timestamp = Column(DateTime, nullable=False, default=func.now(), index=True)
    InteractionType = Column(String(100), nullable=False)
    UserMessage = Column(Text, nullable=False)
    BotResponse = Column(Text, nullable=False)
    ConversationId = Column(String(255), nullable=True, index=True)
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            'interaction_id': self.InteractionId,
            'user_id': self.UserId,
            'timestamp': self.Timestamp,
            'interaction_type': self.InteractionType,
            'user_message': self.UserMessage,
            'bot_response': self.BotResponse,
            'conversation_id': self.ConversationId
        }
