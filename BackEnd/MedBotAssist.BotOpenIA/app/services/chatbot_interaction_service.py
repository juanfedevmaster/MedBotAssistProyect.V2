from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.database import ChatbotInteraction
from app.core.config import settings
from datetime import datetime
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class ChatbotInteractionService:
    """Service for managing chatbot interactions in the database."""
    
    def __init__(self):
        self.engine = None
        self._session_factory = None
        # Don't initialize connection immediately to avoid startup errors
        # Connection will be established when first needed
        
    def _get_database_service(self):
        """Get the main database service instance."""
        from app.services.database_service import DatabaseService
        db_service = DatabaseService()
        db_service._ensure_connection()
        return db_service.engine if db_service.engine else None
    
    def _initialize_connection(self):
        """Initialize database connection using the same logic as DatabaseService."""
        drivers_to_try = [
            "ODBC Driver 18 for SQL Server",
            "ODBC Driver 17 for SQL Server", 
            "ODBC Driver 13 for SQL Server",
            "SQL Server Native Client 11.0",
            "SQL Server"
        ]
        
        for driver in drivers_to_try:
            try:
                # Create connection string
                connection_string = (
                    f"mssql+pyodbc://{settings.DB_USER}:{settings.DB_PASSWORD}@"
                    f"{settings.DB_SERVER}/{settings.DB_DATABASE}?"
                    f"driver={driver.replace(' ', '+')}&"
                    f"TrustServerCertificate=yes&"
                    f"Encrypt=yes"
                )
                
                self.engine = create_engine(
                    connection_string,
                    echo=False,
                    pool_pre_ping=True,
                    pool_recycle=3600
                )
                
                # Test connection
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                
                self._session_factory = sessionmaker(bind=self.engine)
                logger.info(f"ChatbotInteractionService: Database connection initialized with driver: {driver}")
                
                # Ensure the table exists
                self._ensure_table_exists()
                return
                
            except Exception as e:
                logger.warning(f"ChatbotInteractionService: Failed to connect with driver {driver}: {e}")
                continue
        
        # If all drivers failed
        logger.error("ChatbotInteractionService: Could not connect to database with any available ODBC driver")
        self.engine = None
        self._session_factory = None
    
    def _ensure_table_exists(self):
        """Ensure the ChatbotInteractions table exists."""
        if not self.engine:
            return
            
        try:
            create_table_sql = """
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ChatbotInteractions' AND xtype='U')
            CREATE TABLE ChatbotInteractions (
                InteractionId int IDENTITY(1,1) PRIMARY KEY,
                UserId nvarchar(255) NOT NULL,
                Timestamp datetime2 NOT NULL DEFAULT GETDATE(),
                InteractionType nvarchar(100) NOT NULL,
                UserMessage nvarchar(max) NOT NULL,
                BotResponse nvarchar(max) NOT NULL,
                ConversationId nvarchar(255) NULL
            );
            
            -- Create indexes if they don't exist
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_ChatbotInteractions_UserId')
                CREATE INDEX IX_ChatbotInteractions_UserId ON ChatbotInteractions(UserId);
                
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_ChatbotInteractions_Timestamp')
                CREATE INDEX IX_ChatbotInteractions_Timestamp ON ChatbotInteractions(Timestamp);
                
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_ChatbotInteractions_ConversationId')
                CREATE INDEX IX_ChatbotInteractions_ConversationId ON ChatbotInteractions(ConversationId);
            """
            
            with self.engine.connect() as conn:
                conn.execute(text(create_table_sql))
                conn.commit()
            
            logger.info("ChatbotInteractionService: Table and indexes ensured")
            
        except Exception as e:
            logger.error(f"ChatbotInteractionService: Failed to ensure table exists: {e}")
    
    def _get_session(self):
        """Get a database session using the main database engine."""
        if not self.engine:
            self.engine = self._get_database_service()
            if self.engine:
                self._session_factory = sessionmaker(bind=self.engine)
                self._ensure_table_exists()
        
        if not self._session_factory:
            raise Exception("Database connection not available")
        return self._session_factory()
    
    def save_interaction(
        self,
        user_id: str,
        user_message: str,
        bot_response: str,
        interaction_type: Optional[str] = None,
        conversation_id: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> Optional[int]:
        """
        Save a chatbot interaction to the database.
        
        Args:
            user_id: User ID from JWT token
            user_message: Original user message
            bot_response: Agent's response
            interaction_type: Type of interaction (if None, will be auto-classified)
            conversation_id: Optional conversation ID
            timestamp: Optional timestamp (defaults to current time)
            
        Returns:
            Interaction ID if successful, None if failed
        """
        try:
            # Auto-classify interaction type if not provided
            if not interaction_type:
                interaction_type = self.classify_interaction_type(user_message, bot_response)
            
            with self._get_session() as session:
                interaction = ChatbotInteraction(
                    UserId=user_id,
                    Timestamp=timestamp or datetime.utcnow(),
                    InteractionType=interaction_type,
                    UserMessage=user_message,
                    BotResponse=bot_response,
                    ConversationId=conversation_id
                )
                
                session.add(interaction)
                session.commit()
                session.refresh(interaction)
                
                interaction_id = interaction.InteractionId
                logger.info(f"Saved chatbot interaction {interaction_id} for user {user_id} (type: {interaction_type})")
                return interaction_id
                
        except Exception as e:
            logger.error(f"Failed to save chatbot interaction: {e}")
            logger.info(f"Interaction details - User: {user_id}, Type: {interaction_type}, ConvId: {conversation_id}")
            return None
    
    def get_interaction_by_id(self, interaction_id: int) -> Optional[dict]:
        """
        Get a chatbot interaction by ID.
        
        Args:
            interaction_id: Interaction ID
            
        Returns:
            Interaction data as dictionary or None if not found
        """
        try:
            with self._get_session() as session:
                interaction = session.query(ChatbotInteraction).filter(
                    ChatbotInteraction.InteractionId == interaction_id
                ).first()
                
                if interaction:
                    return interaction.to_dict()
                return None
                
        except Exception as e:
            logger.error(f"Failed to get chatbot interaction {interaction_id}: {e}")
            return None
    
    def get_user_interactions(
        self, 
        user_id: str, 
        limit: int = 50, 
        conversation_id: Optional[str] = None
    ) -> list:
        """
        Get chatbot interactions for a specific user.
        
        Args:
            user_id: User ID
            limit: Maximum number of interactions to return
            conversation_id: Optional conversation ID filter
            
        Returns:
            List of interaction dictionaries
        """
        try:
            with self._get_session() as session:
                query = session.query(ChatbotInteraction).filter(
                    ChatbotInteraction.UserId == user_id
                )
                
                if conversation_id:
                    query = query.filter(ChatbotInteraction.ConversationId == conversation_id)
                
                interactions = query.order_by(
                    ChatbotInteraction.Timestamp.desc()
                ).limit(limit).all()
                
                return [interaction.to_dict() for interaction in interactions]
                
        except Exception as e:
            logger.error(f"Failed to get user interactions for {user_id}: {e}")
            return []
    
    def classify_interaction_type(self, user_message: str, bot_response: str) -> str:
        """
        Classify the interaction type based on the message content.
        
        Args:
            user_message: User's message
            bot_response: Bot's response
            
        Returns:
            Interaction type as string
        """
        message_lower = user_message.lower()
        response_lower = bot_response.lower()
        
        # Classification based on keywords in the message
        if any(keyword in message_lower for keyword in ['appointment', 'cita', 'consulta', 'agenda']):
            return 'Appointment'
        elif any(keyword in message_lower for keyword in ['summary', 'resumen', 'estadistic', 'count', 'total']):
            return 'Summary'
        elif any(keyword in message_lower for keyword in ['history', 'historial', 'medical', 'médico']):
            return 'MedicalHistory'
        elif any(keyword in message_lower for keyword in ['diagnosis', 'diagnóstico', 'disease', 'enfermedad']):
            return 'Diagnosis'
        elif any(keyword in message_lower for keyword in ['search', 'buscar', 'find', 'encontrar', 'patient', 'paciente']):
            return 'PatientSearch'
        elif any(keyword in message_lower for keyword in ['create', 'crear', 'new', 'nuevo']):
            return 'PatientCreation'
        elif any(keyword in message_lower for keyword in ['update', 'actualizar', 'modify', 'modificar']):
            return 'PatientUpdate'
        else:
            return 'General'

# Global instance
chatbot_interaction_service = ChatbotInteractionService()
