from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import os
from typing import Optional
import asyncio

class MongoDBClient:
    """Singleton MongoDB client to prevent reinitialization"""
    
    _instance: Optional['MongoDBClient'] = None
    _client: Optional[AsyncIOMotorClient] = None
    _database = None
    
    def __new__(cls) -> 'MongoDBClient':
        if cls._instance is None:
            cls._instance = super(MongoDBClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Only initialize once
        if self._client is None:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize MongoDB client with connection string from environment or default"""
        # Get connection string from environment or use default local MongoDB
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        database_name = os.getenv("DATABASE_NAME", "chatbot_db")
        
        try:
            self._client = AsyncIOMotorClient(mongo_url)
            self._database = self._client[database_name]
            print(f"MongoDB client initialized successfully with database: {database_name}")
        except Exception as e:
            print(f"Failed to initialize MongoDB client: {e}")
            raise
    
    @property
    def client(self) -> AsyncIOMotorClient:
        """Get the MongoDB client instance"""
        if self._client is None:
            raise RuntimeError("MongoDB client not initialized")
        return self._client
    
    @property
    def database(self):
        """Get the database instance"""
        if self._database is None:
            raise RuntimeError("Database not initialized")
        return self._database
    
    async def ping(self) -> bool:
        """Test database connection"""
        try:
            await self._client.admin.command('ping')
            return True
        except ConnectionFailure:
            return False
    
    async def close(self):
        """Close the database connection"""
        if self._client:
            self._client.close()
            print("MongoDB connection closed")
    
    def get_collection(self, collection_name: str):
        """Get a specific collection from the database"""
        return self._database[collection_name]

# Global instance - will be created only once
mongodb_client = MongoDBClient()