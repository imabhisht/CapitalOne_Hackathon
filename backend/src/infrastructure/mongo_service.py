from pymongo import MongoClient, DESCENDING, ASCENDING
from pymongo.errors import OperationFailure
from typing import Optional
import os
import threading
import time
import logging

# Set up logging for index creation feedback
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoService:
    _instance: Optional['MongoService'] = None
    _client: Optional[MongoClient] = None
    
    def __new__(cls) -> 'MongoService':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def initialize(self, connection_string: str) -> None:
        """
        Initialize the MongoDB client and create necessary indexes.
        This should be called once during application startup.
        """
        if self._client is None:
            self._client = MongoClient(connection_string)
            # Create indexes after client initialization
            await self._create_indexes()

    async def _create_indexes(self) -> None:
        """
        Create indexes for the chat_messages collection using created_at and updated_at.
        This method will create indexes if they don't exist, or ignore if they already exist.
        """
        try:
            chat_messages_collection = self.get_collection("chat_messages")

            # Index 1: session_id (for filtering messages by session)
            try:
                chat_messages_collection.create_index("session_id", name="idx_session_id")
                logger.info("Created index: idx_session_id")
            except OperationFailure as e:
                if "already exists" in str(e):
                    logger.info("Index idx_session_id already exists")
                else:
                    raise

            # Index 2: Compound index on session_id + created_at (descending)
            # Most important for getting latest messages in a session
            try:
                chat_messages_collection.create_index([
                    ("session_id", ASCENDING),
                    ("created_at", DESCENDING)
                ], name="idx_session_created_at")
                logger.info("Created index: idx_session_created_at")
            except OperationFailure as e:
                if "already exists" in str(e):
                    logger.info("Index idx_session_created_at already exists")
                else:
                    raise

            # Index 3: message_type (for filtering by message type)
            try:
                chat_messages_collection.create_index("message_type", name="idx_message_type")
                logger.info("Created index: idx_message_type")
            except OperationFailure as e:
                if "already exists" in str(e):
                    logger.info("Index idx_message_type already exists")
                else:
                    raise

            # Index 4: Compound index on session_id + message_type + created_at
            # For queries like "get all AI messages in session ordered by time"
            try:
                chat_messages_collection.create_index([
                    ("session_id", ASCENDING),
                    ("message_type", ASCENDING),
                    ("created_at", DESCENDING)
                ], name="idx_session_type_created_at")
                logger.info("Created index: idx_session_type_created_at")
            except OperationFailure as e:
                if "already exists" in str(e):
                    logger.info("Index idx_session_type_created_at already exists")
                else:
                    raise

            # Index 5: created_at (for global chronological queries)
            try:
                chat_messages_collection.create_index([("created_at", DESCENDING)], name="idx_created_at")
                logger.info("Created index: idx_created_at")
            except OperationFailure as e:
                if "already exists" in str(e):
                    logger.info("Index idx_created_at already exists")
                else:
                    raise

            # Index 6: updated_at (for tracking modifications)
            try:
                chat_messages_collection.create_index([("updated_at", DESCENDING)], name="idx_updated_at")
                logger.info("Created index: idx_updated_at")
            except OperationFailure as e:
                if "already exists" in str(e):
                    logger.info("Index idx_updated_at already exists")
                else:
                    raise

            # Index 7: language_type (sparse, since it can be null)
            try:
                chat_messages_collection.create_index("language_type", sparse=True, name="idx_language_type")
                logger.info("Created index: idx_language_type (sparse)")
            except OperationFailure as e:
                if "already exists" in str(e):
                    logger.info("Index idx_language_type already exists")
                else:
                    raise

            # Index 8: Compound index on session_id + language_type + created_at
            try:
                chat_messages_collection.create_index([
                    ("session_id", ASCENDING),
                    ("language_type", ASCENDING),
                    ("created_at", DESCENDING)
                ], sparse=True, name="idx_session_language_created_at")
                logger.info("Created index: idx_session_language_created_at (sparse)")
            except OperationFailure as e:
                if "already exists" in str(e):
                    logger.info("Index idx_session_language_created_at already exists")
                else:
                    raise

            logger.info("All indexes for chat_messages collection have been processed")

        except Exception as e:
            logger.error(f"Error creating indexes: {str(e)}")
            raise

    @property
    def client(self) -> MongoClient:
        """
        Return the MongoDB client.
        Raises an exception if initialize() hasn't been called yet.
        """
        if self._client is None:
            raise RuntimeError("MongoService not initialized. Call initialize() first.")
        return self._client
    
    def get_database(self, db_name: str):
        """Get a database from the client."""
        return self.client[db_name]
    
    def get_collection(self, collection_name: str):
        """Get a collection from the capital_one database."""
        return self.get_database("capital_one")[collection_name]

# Create a global instance
mongo_service = MongoService()

# Example usage:
# mongo_service.initialize("mongodb://localhost:27017/")
# 
# Example document structure for chat_messages:
# {
#     "_id": "550e8400-e29b-41d4-a716-446655440000",  # UUID
#     "session_id": "user123_session_456",
#     "message_type": "user",  # or "ai", "system", etc.
#     "content": "Hello, how are you?",
#     "timestamp": datetime.utcnow(),
#     "language_type": None,  # or "en", "es", "fr", etc. (null by default)
#     "refined_query": None,  # processed/refined version of user query (null by default)
#     "translated_query": None,  # translated version of the query (null by default)
#     "metadata": {
#         "user_id": "user123",
#         "model": "gpt-4",  # for AI messages
#         # other relevant metadata
#     }
# }