# src/models/chat_message.py

from src.infrastructure.mongo_service import mongo_service
from uuid import uuid4
from datetime import datetime
from typing import Optional, Dict, Any, Literal

# LangChain message types
MessageType = Literal["human", "ai", "system", "function", "tool"]

class ChatMessage:
    def __init__(
        self, 
        session_id: str, 
        content: str, 
        message_type: MessageType, 
        message_id: Optional[str] = None,
        language_type: str = "en", 
        metadata: Optional[Dict[str, Any]] = None, 
        refined_query: Optional[str] = None, 
        translated_query: Optional[str] = None
    ):
        self.db = mongo_service.get_collection("chat_messages")
        self.id = message_id or str(uuid4())  # Generate ID if not provided
        self.session_id = session_id
        self.content = content
        self.message_type = message_type
        self.language_type = language_type
        self.metadata = metadata or {}
        self.refined_query = refined_query
        self.translated_query = translated_query
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    async def sync_to_db(self) -> bool:
        """
        Upsert the chat message to the database.
        
        Returns:
            bool: True if operation was successful, False otherwise
        """
        try:
            # Update the updated_at timestamp
            self.updated_at = datetime.utcnow()
            
            result = await self.db.update_one(
                {"_id": self.id},
                {
                    "$set": {
                        "session_id": self.session_id,
                        "content": self.content,
                        "message_type": self.message_type,
                        "language_type": self.language_type,
                        "metadata": self.metadata,
                        "refined_query": self.refined_query,
                        "translated_query": self.translated_query,
                        "updated_at": self.updated_at
                    },
                    "$setOnInsert": {
                        "created_at": self.created_at
                    }
                },
                upsert=True
            )
            
            return result.acknowledged
            
        except Exception as e:
            # Log the error or handle it according to your application's error handling strategy
            print(f"Error syncing chat message to DB: {e}")
            return False

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the ChatMessage instance to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the chat message
        """
        return {
            "_id": self.id,
            "session_id": self.session_id,
            "content": self.content,
            "message_type": self.message_type,
            "language_type": self.language_type,
            "metadata": self.metadata,
            "refined_query": self.refined_query,
            "translated_query": self.translated_query,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_langchain_message(cls, langchain_msg, session_id: str, **kwargs) -> 'ChatMessage':
        """
        Create a ChatMessage from a LangChain message object.
        
        Args:
            langchain_msg: LangChain message (HumanMessage, AIMessage, SystemMessage, etc.)
            session_id (str): Session ID for this message
            **kwargs: Additional parameters for ChatMessage constructor
            
        Returns:
            ChatMessage: New ChatMessage instance
        """
        # Map LangChain message types to our types
        message_type_mapping = {
            'HumanMessage': 'human',
            'AIMessage': 'ai', 
            'SystemMessage': 'system',
            'FunctionMessage': 'function',
            'ToolMessage': 'tool'
        }
        
        msg_class_name = langchain_msg.__class__.__name__
        message_type = message_type_mapping.get(msg_class_name, 'human')
        
        return cls(
            session_id=session_id,
            content=langchain_msg.content,
            message_type=message_type,
            metadata=getattr(langchain_msg, 'additional_kwargs', {}),
            **kwargs
        )

    def to_langchain_message(self):
        """
        Convert ChatMessage to appropriate LangChain message type.
        
        Returns:
            LangChain message object (HumanMessage, AIMessage, etc.)
        """
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        
        message_classes = {
            'human': HumanMessage,
            'ai': AIMessage,
            'system': SystemMessage,
        }
        
        message_class = message_classes.get(self.message_type, HumanMessage)
        return message_class(
            content=self.content,
            additional_kwargs=self.metadata or {}
        )
    async def find_by_id(cls, message_id: str) -> Optional['ChatMessage']:
        """
        Find a chat message by its ID.
        
        Args:
            message_id (str): The message ID to search for
            
        Returns:
            Optional[ChatMessage]: ChatMessage instance if found, None otherwise
        """
        db = mongo_service.get_collection("chat_messages")
        document = await db.find_one({"_id": message_id})
        
        if document:
            # Create instance without calling __init__ to avoid generating new timestamps
            instance = cls.__new__(cls)
            instance.db = db
            instance.id = document["_id"]
            instance.session_id = document["session_id"]
            instance.content = document["content"]
            instance.message_type = document["message_type"]
            instance.language_type = document.get("language_type", "en")
            instance.metadata = document.get("metadata", {})
            instance.refined_query = document.get("refined_query")
            instance.translated_query = document.get("translated_query")
            instance.created_at = document.get("created_at", datetime.utcnow())
            instance.updated_at = document.get("updated_at", datetime.utcnow())
            return instance
        
        return None

    @classmethod
    async def find_by_session(cls, session_id: str, limit: int = 50) -> list['ChatMessage']:
        """
        Find all chat messages for a given session.
        
        Args:
            session_id (str): The session ID to search for
            limit (int): Maximum number of messages to return
            
        Returns:
            list[ChatMessage]: List of ChatMessage instances
        """
        db = mongo_service.get_collection("chat_messages")
        cursor = db.find({"session_id": session_id}).sort("created_at", 1).limit(limit)
        
        messages = []
        async for document in cursor:
            instance = cls.__new__(cls)
            instance.db = db
            instance.id = document["_id"]
            instance.session_id = document["session_id"]
            instance.content = document["content"]
            instance.message_type = document["message_type"]
            instance.language_type = document.get("language_type", "en")
            instance.metadata = document.get("metadata", {})
            instance.refined_query = document.get("refined_query")
            instance.translated_query = document.get("translated_query")
            instance.created_at = document.get("created_at", datetime.utcnow())
            instance.updated_at = document.get("updated_at", datetime.utcnow())
            messages.append(instance)
        
        return messages

    async def delete(self) -> bool:
        """
        Delete the chat message from the database.
        
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            result = await self.db.delete_one({"_id": self.id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting chat message: {e}")
            return False

    def __repr__(self) -> str:
        return f"ChatMessage(id='{self.id}', session_id='{self.session_id}', message_type='{self.message_type}')"