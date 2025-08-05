from pymongo import MongoClient
from typing import List, Dict, Optional
from datetime import datetime
import logging
from .config import Config

logger = logging.getLogger(__name__)

class ChatStorage:
    """MongoDB storage for chat history"""
    
    def __init__(self):
        self.client = MongoClient(Config.MONGODB_URI)
        self.db = self.client[Config.MONGODB_DATABASE]
        self.collection = self.db[Config.MONGODB_COLLECTION]
        
    def save_message(self, session_id: str, message: Dict) -> bool:
        """Save a message to MongoDB"""
        try:
            message_doc = {
                "session_id": session_id,
                "role": message.get("role", "user"),
                "content": message.get("content", ""),
                "timestamp": message.get("timestamp", datetime.now().isoformat()),
                "metadata": message.get("metadata", {})
            }
            
            result = self.collection.insert_one(message_doc)
            return result.inserted_id is not None
            
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            return False
    
    def get_chat_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Retrieve chat history for a session"""
        try:
            cursor = self.collection.find(
                {"session_id": session_id},
                {"_id": 0}  # Exclude MongoDB _id
            ).sort("timestamp", -1).limit(limit)
            
            messages = list(cursor)
            messages.reverse()  # Return in chronological order
            return messages
            
        except Exception as e:
            logger.error(f"Error retrieving chat history: {e}")
            return []
    
    def clear_session(self, session_id: str) -> bool:
        """Clear all messages for a session"""
        try:
            result = self.collection.delete_many({"session_id": session_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error clearing session: {e}")
            return False
    
    def close(self):
        """Close MongoDB connection"""
        self.client.close()

# Global instance
chat_storage = ChatStorage() 