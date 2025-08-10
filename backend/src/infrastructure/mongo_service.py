from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import DESCENDING, ASCENDING
from pymongo.errors import OperationFailure
from typing import Optional, Dict, List, Tuple
import logging

# Set up logging for index creation feedback
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoService:
    _instance: Optional['MongoService'] = None
    _client: Optional[AsyncIOMotorClient] = None
    
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
            self._client = AsyncIOMotorClient(connection_string)
            # Create indexes after client initialization
            await self._create_indexes()

    async def _get_existing_indexes(self, collection) -> Dict[str, dict]:
        """
        Get all existing indexes for a collection.
        Returns a dictionary with index names as keys and index info as values.
        """
        try:
            existing_indexes = {}
            async for index_info in collection.list_indexes():
                existing_indexes[index_info['name']] = index_info
            return existing_indexes
        except Exception as e:
            logger.error(f"Error fetching existing indexes: {str(e)}")
            return {}

    def _define_required_indexes(self) -> List[Tuple[str, list, dict]]:
        """
        Define all required indexes for the chat_messages collection.
        Returns a list of tuples: (index_name, keys, options)
        """
        return [
            # Index 1: session_id (for filtering messages by session)
            ("idx_session_id", [("session_id", ASCENDING)], {}),
            
            # Index 2: Compound index on session_id + created_at (descending)
            ("idx_session_created_at", [("session_id", ASCENDING), ("created_at", DESCENDING)], {}),
            
            # Index 3: message_type (for filtering by message type)
            ("idx_message_type", [("message_type", ASCENDING)], {}),
            
            # Index 4: Compound index on session_id + message_type + created_at
            ("idx_session_type_created_at", [
                ("session_id", ASCENDING),
                ("message_type", ASCENDING),
                ("created_at", DESCENDING)
            ], {}),
            
            # Index 5: created_at (for global chronological queries)
            ("idx_created_at", [("created_at", DESCENDING)], {}),
            
            # Index 6: updated_at (for tracking modifications)
            ("idx_updated_at", [("updated_at", DESCENDING)], {}),
            
            # Index 7: language_type (sparse, since it can be null)
            ("idx_language_type", [("language_type", ASCENDING)], {"sparse": True}),
            
            # Index 8: Compound index on session_id + language_type + created_at
            ("idx_session_language_created_at", [
                ("session_id", ASCENDING),
                ("language_type", ASCENDING),
                ("created_at", DESCENDING)
            ], {"sparse": True})
        ]

    async def _create_indexes(self) -> None:
        """
        Create indexes for the chat_messages collection only if they don't exist.
        This method first checks existing indexes and only creates missing ones.
        """
        try:
            chat_messages_collection = self.get_collection("chat_messages")
            
            # Get existing indexes
            existing_indexes = await self._get_existing_indexes(chat_messages_collection)
            logger.info(f"Found {len(existing_indexes)} existing indexes: {list(existing_indexes.keys())}")
            
            # Get required indexes
            required_indexes = self._define_required_indexes()
            
            # Track what we're creating
            created_count = 0
            skipped_count = 0
            
            # Create only missing indexes
            for index_name, keys, options in required_indexes:
                if index_name in existing_indexes:
                    logger.info(f"Index {index_name} already exists - skipping")
                    skipped_count += 1
                else:
                    try:
                        # Add the name to options
                        options_with_name = {**options, "name": index_name}
                        await chat_messages_collection.create_index(keys, **options_with_name)
                        logger.info(f"Created index: {index_name}")
                        created_count += 1
                    except OperationFailure as e:
                        if "already exists" in str(e):
                            # Race condition - index was created between our check and creation
                            logger.info(f"Index {index_name} was created concurrently")
                            skipped_count += 1
                        else:
                            logger.error(f"Failed to create index {index_name}: {str(e)}")
                            raise
            
            logger.info(f"Index creation summary: {created_count} created, {skipped_count} skipped")

        except Exception as e:
            logger.error(f"Error in index creation process: {str(e)}")
            raise

    async def verify_indexes(self) -> Dict[str, bool]:
        """
        Verify that all required indexes exist.
        Returns a dictionary with index names as keys and existence status as values.
        """
        try:
            chat_messages_collection = self.get_collection("chat_messages")
            existing_indexes = await self._get_existing_indexes(chat_messages_collection)
            required_indexes = self._define_required_indexes()
            
            verification_result = {}
            for index_name, _, _ in required_indexes:
                verification_result[index_name] = index_name in existing_indexes
            
            return verification_result
        except Exception as e:
            logger.error(f"Error verifying indexes: {str(e)}")
            return {}

    async def get_index_info(self) -> Dict[str, dict]:
        """
        Get detailed information about all indexes in the chat_messages collection.
        """
        try:
            chat_messages_collection = self.get_collection("chat_messages")
            return await self._get_existing_indexes(chat_messages_collection)
        except Exception as e:
            logger.error(f"Error getting index info: {str(e)}")
            return {}

    @property
    def client(self) -> AsyncIOMotorClient:
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
    
    def is_connected(self) -> bool:
        """
        Check if the MongoDB client is connected.
        """
        return self._client is not None

# Create a global instance
mongo_service = MongoService()