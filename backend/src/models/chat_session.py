# src/models/chat_session.py

from src.infrastructure.mongo_service import mongo_service
from src.models.chat_message import ChatMessage
from uuid import uuid4
from datetime import datetime
from typing import Optional, Dict, Any, List

class ChatSession:
    def __init__(
        self, 
        user_id: str,  # user_id is now required
        session_id: Optional[str] = None,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        refresh: bool = False
    ):
        self.db = mongo_service.get_collection("chat_sessions")
        self.user_id = user_id
        
        # Array to hold ChatMessage objects
        self._messages: List[ChatMessage] = []
        self._messages_loaded = False
        self._is_new_session = False
        
        if session_id:
            # Existing session - load from database
            self.id = session_id
            self._load_session_from_db()
            # Load latest messages if refresh is True or this is an existing session
            if refresh:
                self._load_latest_messages()
        else:
            # New session - generate new ID and set defaults
            self.id = str(uuid4())
            self._is_new_session = True
            self.title = title or f"Chat Session {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
            self.metadata = metadata or {}
            self.created_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()
            # No need to fetch messages for new session
            self._messages_loaded = True

    async def _load_session_from_db(self) -> bool:
        """
        Load session details from database based on session_id and user_id.
        
        Returns:
            bool: True if session was found and loaded, False otherwise
        """
        try:
            document = await self.db.find_one({
                "_id": self.id,
                "user_id": self.user_id
            })
            
            if document:
                self.title = document.get("title", f"Chat Session {document.get('created_at', datetime.utcnow()).strftime('%Y-%m-%d %H:%M')}")
                self.metadata = document.get("metadata", {})
                self.created_at = document.get("created_at", datetime.utcnow())
                self.updated_at = document.get("updated_at", datetime.utcnow())
                return True
            else:
                # Session not found, treat as new session
                self._is_new_session = True
                self.title = f"Chat Session {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
                self.metadata = {}
                self.created_at = datetime.utcnow()
                self.updated_at = datetime.utcnow()
                return False
                
        except Exception as e:
            print(f"Error loading session from DB: {e}")
            # Treat as new session on error
            self._is_new_session = True
            self.title = f"Chat Session {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
            self.metadata = {}
            self.created_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()
            return False

    async def _load_latest_messages(self, limit: int = 10) -> None:
        """
        Load the latest messages from the database.
        
        Args:
            limit (int): Number of latest messages to load (default: 10)
        """
        try:
            # Fetch latest messages from database
            latest_messages = await ChatMessage.find_by_session(self.id, limit=limit)
            
            # Sort messages by created_at to ensure correct order
            # Oldest first, newest last (as requested)
            latest_messages.sort(key=lambda msg: msg.created_at)
            
            # Keep only the latest 'limit' messages if we have more
            if len(latest_messages) > limit:
                latest_messages = latest_messages[-limit:]
            
            self._messages = latest_messages
            self._messages_loaded = True
            
        except Exception as e:
            print(f"Error loading latest messages: {e}")
            self._messages = []
            self._messages_loaded = True

    async def get_messages(self, refresh: bool = False, limit: int = 10) -> List[ChatMessage]:
        """
        Get the messages in this session.
        
        Args:
            refresh (bool): If True, forcefully fetch latest messages from DB
            limit (int): Number of latest messages to return
            
        Returns:
            List[ChatMessage]: Array of ChatMessage objects, ordered from oldest to newest
        """
        # Don't load messages for new sessions unless refresh is explicitly True
        if self._is_new_session and not refresh:
            return []
            
        if refresh or not self._messages_loaded:
            await self._load_latest_messages(limit)
        
        return self._messages.copy()  # Return a copy to prevent external modification

    async def add_message(
        self, 
        content: str, 
        message_type: str, 
        language_type: str = "en",
        metadata: Optional[Dict[str, Any]] = None,
        refined_query: Optional[str] = None,
        translated_query: Optional[str] = None,
        sync_to_db: bool = True
    ) -> ChatMessage:
        """
        Add a new message to the session.
        
        Args:
            content (str): Message content
            message_type (str): Type of message ('human', 'ai', 'system', etc.)
            language_type (str): Language type (default: 'en')
            metadata (Optional[Dict]): Additional metadata
            refined_query (Optional[str]): Refined query if applicable
            translated_query (Optional[str]): Translated query if applicable
            sync_to_db (bool): Whether to sync the message to database immediately
            
        Returns:
            ChatMessage: The created ChatMessage object
        """
        # Create new message
        message = ChatMessage(
            session_id=self.id,
            content=content,
            message_type=message_type,
            language_type=language_type,
            metadata=metadata,
            refined_query=refined_query,
            translated_query=translated_query
        )
        
        # Sync to database if requested
        if sync_to_db:
            await message.sync_to_db()
        
        # Add to local messages array
        self._messages.append(message)
        
        # Keep only latest 10 messages in memory
        if len(self._messages) > 10:
            self._messages = self._messages[-10:]
        
        # Update session's updated_at timestamp
        self.updated_at = datetime.utcnow()
        await self.sync_to_db()
        
        return message

    async def add_langchain_message(self, langchain_msg, sync_to_db: bool = True, **kwargs) -> ChatMessage:
        """
        Add a LangChain message to the session.
        
        Args:
            langchain_msg: LangChain message object
            sync_to_db (bool): Whether to sync the message to database immediately
            **kwargs: Additional parameters for ChatMessage creation
            
        Returns:
            ChatMessage: The created ChatMessage object
        """
        # Create ChatMessage from LangChain message
        message = ChatMessage.from_langchain_message(langchain_msg, self.id, **kwargs)
        
        # Sync to database if requested
        if sync_to_db:
            await message.sync_to_db()
        
        # Add to local messages array
        self._messages.append(message)
        
        # Keep only latest 10 messages in memory
        if len(self._messages) > 10:
            self._messages = self._messages[-10:]
        
        # Update session's updated_at timestamp
        self.updated_at = datetime.utcnow()
        await self.sync_to_db()
        
        return message

    async def get_latest_message(self) -> Optional[ChatMessage]:
        """
        Get the latest message in the session.
        
        Returns:
            Optional[ChatMessage]: Latest message or None if no messages exist
        """
        if not self._messages_loaded:
            await self._load_latest_messages()
        
        return self._messages[-1] if self._messages else None

    async def get_messages_by_type(self, message_type: str) -> List[ChatMessage]:
        """
        Get messages of a specific type.
        
        Args:
            message_type (str): Type of messages to filter ('human', 'ai', 'system', etc.)
            
        Returns:
            List[ChatMessage]: Filtered messages
        """
        if not self._messages_loaded:
            await self._load_latest_messages()
        
        return [msg for msg in self._messages if msg.message_type == message_type]

    def get_message_count(self) -> int:
        """
        Get the number of messages currently loaded in the session.
        
        Returns:
            int: Number of messages
        """
        return len(self._messages)

    async def clear_messages(self, delete_from_db: bool = False) -> bool:
        """
        Clear all messages from the session.
        
        Args:
            delete_from_db (bool): If True, also delete messages from database
            
        Returns:
            bool: True if operation was successful
        """
        try:
            if delete_from_db:
                # Delete all messages from database
                db = mongo_service.get_collection("chat_messages")
                await db.delete_many({"session_id": self.id})
            
            # Clear local messages array
            self._messages.clear()
            
            return True
        except Exception as e:
            print(f"Error clearing messages: {e}")
            return False

    async def sync_to_db(self) -> bool:
        """
        Sync the chat session to the database.
        
        Returns:
            bool: True if operation was successful, False otherwise
        """
        try:
            self.updated_at = datetime.utcnow()
            
            result = await self.db.update_one(
                {"_id": self.id},
                {
                    "$set": {
                        "user_id": self.user_id,
                        "title": self.title,
                        "metadata": self.metadata,
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
            print(f"Error syncing chat session to DB: {e}")
            return False

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the ChatSession instance to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the chat session
        """
        return {
            "_id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "metadata": self.metadata,
            "message_count": len(self._messages),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    async def find_by_user_and_session(cls, user_id: str, session_id: str, refresh: bool = False) -> Optional['ChatSession']:
        """
        Find a chat session by user_id and session_id.
        
        Args:
            user_id (str): The user ID
            session_id (str): The session ID to search for
            refresh (bool): Whether to load latest messages immediately
            
        Returns:
            Optional[ChatSession]: ChatSession instance if found, None otherwise
        """
        db = mongo_service.get_collection("chat_sessions")
        document = await db.find_one({
            "_id": session_id,
            "user_id": user_id
        })
        
        if document:
            # Create instance using constructor with existing session_id
            instance = cls(
                user_id=user_id,
                session_id=session_id,
                refresh=refresh
            )
            return instance
        
        return None

    @classmethod
    async def find_by_user(cls, user_id: str, limit: int = 20) -> List['ChatSession']:
        """
        Find all chat sessions for a given user.
        
        Args:
            user_id (str): The user ID to search for
            limit (int): Maximum number of sessions to return
            
        Returns:
            List[ChatSession]: List of ChatSession instances
        """
        db = mongo_service.get_collection("chat_sessions")
        cursor = db.find({"user_id": user_id}).sort("updated_at", -1).limit(limit)
        
        sessions = []
        async for document in cursor:
            instance = cls.__new__(cls)
            instance.db = db
            instance.id = document["_id"]
            instance.user_id = document.get("user_id")
            instance.title = document.get("title", f"Chat Session {document.get('created_at', datetime.utcnow()).strftime('%Y-%m-%d %H:%M')}")
            instance.metadata = document.get("metadata", {})
            instance.created_at = document.get("created_at", datetime.utcnow())
            instance.updated_at = document.get("updated_at", datetime.utcnow())
            instance._messages = []
            instance._messages_loaded = False
            sessions.append(instance)
        
        return sessions

    async def delete(self, delete_messages: bool = True) -> bool:
        """
        Delete the chat session from the database.
        
        Args:
            delete_messages (bool): If True, also delete all messages in this session
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            # Delete messages if requested
            if delete_messages:
                msg_db = mongo_service.get_collection("chat_messages")
                await msg_db.delete_many({"session_id": self.id})
            
            # Delete the session
            result = await self.db.delete_one({"_id": self.id})
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"Error deleting chat session: {e}")
            return False

    def __repr__(self) -> str:
        return f"ChatSession(id='{self.id}', user_id='{self.user_id}', message_count={len(self._messages)})"

    def __len__(self) -> int:
        """Return the number of messages in the session."""
        return len(self._messages)

    def __getitem__(self, index: int) -> ChatMessage:
        """Get a message by index."""
        return self._messages[index]

    def __iter__(self):
        """Make the session iterable over messages."""
        return iter(self._messages)# src/models/chat_session.py

from src.infrastructure.mongo_service import mongo_service
from src.models.chat_message import ChatMessage
from uuid import uuid4
from datetime import datetime
from typing import Optional, Dict, Any, List

class ChatSession:
    def __init__(
        self, 
        user_id: str,  # user_id is now required
        session_id: Optional[str] = None,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        refresh: bool = False
    ):
        self.db = mongo_service.get_collection("chat_sessions")
        self.user_id = user_id
        
        # Array to hold ChatMessage objects
        self._messages: List[ChatMessage] = []
        self._messages_loaded = False
        self._is_new_session = False
        
        if session_id:
            # Existing session - load from database
            self.id = session_id
            self._load_session_from_db()
            # Load latest messages if refresh is True or this is an existing session
            if refresh:
                self._load_latest_messages()
        else:
            # New session - generate new ID and set defaults
            self.id = str(uuid4())
            self._is_new_session = True
            self.title = title or f"Chat Session {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
            self.metadata = metadata or {}
            self.created_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()
            # No need to fetch messages for new session
            self._messages_loaded = True

    async def _load_session_from_db(self) -> bool:
        """
        Load session details from database based on session_id and user_id.
        
        Returns:
            bool: True if session was found and loaded, False otherwise
        """
        try:
            document = await self.db.find_one({
                "_id": self.id,
                "user_id": self.user_id
            })
            
            if document:
                self.title = document.get("title", f"Chat Session {document.get('created_at', datetime.utcnow()).strftime('%Y-%m-%d %H:%M')}")
                self.metadata = document.get("metadata", {})
                self.created_at = document.get("created_at", datetime.utcnow())
                self.updated_at = document.get("updated_at", datetime.utcnow())
                return True
            else:
                # Session not found, treat as new session
                self._is_new_session = True
                self.title = f"Chat Session {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
                self.metadata = {}
                self.created_at = datetime.utcnow()
                self.updated_at = datetime.utcnow()
                return False
                
        except Exception as e:
            print(f"Error loading session from DB: {e}")
            # Treat as new session on error
            self._is_new_session = True
            self.title = f"Chat Session {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
            self.metadata = {}
            self.created_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()
            return False

    async def _load_latest_messages(self, limit: int = 10) -> None:
        """
        Load the latest messages from the database.
        
        Args:
            limit (int): Number of latest messages to load (default: 10)
        """
        try:
            # Fetch latest messages from database
            latest_messages = await ChatMessage.find_by_session(self.id, limit=limit)
            
            # Sort messages by created_at to ensure correct order
            # Oldest first, newest last (as requested)
            latest_messages.sort(key=lambda msg: msg.created_at)
            
            # Keep only the latest 'limit' messages if we have more
            if len(latest_messages) > limit:
                latest_messages = latest_messages[-limit:]
            
            self._messages = latest_messages
            self._messages_loaded = True
            
        except Exception as e:
            print(f"Error loading latest messages: {e}")
            self._messages = []
            self._messages_loaded = True

    async def get_messages(self, refresh: bool = False, limit: int = 10) -> List[ChatMessage]:
        """
        Get the messages in this session.
        
        Args:
            refresh (bool): If True, forcefully fetch latest messages from DB
            limit (int): Number of latest messages to return
            
        Returns:
            List[ChatMessage]: Array of ChatMessage objects, ordered from oldest to newest
        """
        # Don't load messages for new sessions unless refresh is explicitly True
        if self._is_new_session and not refresh:
            return []
            
        if refresh or not self._messages_loaded:
            await self._load_latest_messages(limit)
        
        return self._messages.copy()  # Return a copy to prevent external modification

    async def add_message(
        self, 
        content: str, 
        message_type: str, 
        language_type: str = "en",
        metadata: Optional[Dict[str, Any]] = None,
        refined_query: Optional[str] = None,
        translated_query: Optional[str] = None,
        sync_to_db: bool = True
    ) -> ChatMessage:
        """
        Add a new message to the session.
        
        Args:
            content (str): Message content
            message_type (str): Type of message ('human', 'ai', 'system', etc.)
            language_type (str): Language type (default: 'en')
            metadata (Optional[Dict]): Additional metadata
            refined_query (Optional[str]): Refined query if applicable
            translated_query (Optional[str]): Translated query if applicable
            sync_to_db (bool): Whether to sync the message to database immediately
            
        Returns:
            ChatMessage: The created ChatMessage object
        """
        # Create new message
        message = ChatMessage(
            session_id=self.id,
            content=content,
            message_type=message_type,
            language_type=language_type,
            metadata=metadata,
            refined_query=refined_query,
            translated_query=translated_query
        )
        
        # Sync to database if requested
        if sync_to_db:
            await message.sync_to_db()
        
        # Add to local messages array
        self._messages.append(message)
        
        # Keep only latest 10 messages in memory
        if len(self._messages) > 10:
            self._messages = self._messages[-10:]
        
        # Update session's updated_at timestamp
        self.updated_at = datetime.utcnow()
        await self.sync_to_db()
        
        return message

    async def add_langchain_message(self, langchain_msg, sync_to_db: bool = True, **kwargs) -> ChatMessage:
        """
        Add a LangChain message to the session.
        
        Args:
            langchain_msg: LangChain message object
            sync_to_db (bool): Whether to sync the message to database immediately
            **kwargs: Additional parameters for ChatMessage creation
            
        Returns:
            ChatMessage: The created ChatMessage object
        """
        # Create ChatMessage from LangChain message
        message = ChatMessage.from_langchain_message(langchain_msg, self.id, **kwargs)
        
        # Sync to database if requested
        if sync_to_db:
            await message.sync_to_db()
        
        # Add to local messages array
        self._messages.append(message)
        
        # Keep only latest 10 messages in memory
        if len(self._messages) > 10:
            self._messages = self._messages[-10:]
        
        # Update session's updated_at timestamp
        self.updated_at = datetime.utcnow()
        await self.sync_to_db()
        
        return message

    async def get_latest_message(self) -> Optional[ChatMessage]:
        """
        Get the latest message in the session.
        
        Returns:
            Optional[ChatMessage]: Latest message or None if no messages exist
        """
        if not self._messages_loaded:
            await self._load_latest_messages()
        
        return self._messages[-1] if self._messages else None

    async def get_messages_by_type(self, message_type: str) -> List[ChatMessage]:
        """
        Get messages of a specific type.
        
        Args:
            message_type (str): Type of messages to filter ('human', 'ai', 'system', etc.)
            
        Returns:
            List[ChatMessage]: Filtered messages
        """
        if not self._messages_loaded:
            await self._load_latest_messages()
        
        return [msg for msg in self._messages if msg.message_type == message_type]

    def get_message_count(self) -> int:
        """
        Get the number of messages currently loaded in the session.
        
        Returns:
            int: Number of messages
        """
        return len(self._messages)

    async def clear_messages(self, delete_from_db: bool = False) -> bool:
        """
        Clear all messages from the session.
        
        Args:
            delete_from_db (bool): If True, also delete messages from database
            
        Returns:
            bool: True if operation was successful
        """
        try:
            if delete_from_db:
                # Delete all messages from database
                db = mongo_service.get_collection("chat_messages")
                await db.delete_many({"session_id": self.id})
            
            # Clear local messages array
            self._messages.clear()
            
            return True
        except Exception as e:
            print(f"Error clearing messages: {e}")
            return False

    async def sync_to_db(self) -> bool:
        """
        Sync the chat session to the database.
        
        Returns:
            bool: True if operation was successful, False otherwise
        """
        try:
            self.updated_at = datetime.utcnow()
            
            result = await self.db.update_one(
                {"_id": self.id},
                {
                    "$set": {
                        "user_id": self.user_id,
                        "title": self.title,
                        "metadata": self.metadata,
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
            print(f"Error syncing chat session to DB: {e}")
            return False

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the ChatSession instance to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the chat session
        """
        return {
            "_id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "metadata": self.metadata,
            "message_count": len(self._messages),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    async def find_by_user_and_session(cls, user_id: str, session_id: str, refresh: bool = False) -> Optional['ChatSession']:
        """
        Find a chat session by user_id and session_id.
        
        Args:
            user_id (str): The user ID
            session_id (str): The session ID to search for
            refresh (bool): Whether to load latest messages immediately
            
        Returns:
            Optional[ChatSession]: ChatSession instance if found, None otherwise
        """
        db = mongo_service.get_collection("chat_sessions")
        document = await db.find_one({
            "_id": session_id,
            "user_id": user_id
        })
        
        if document:
            # Create instance using constructor with existing session_id
            instance = cls(
                user_id=user_id,
                session_id=session_id,
                refresh=refresh
            )
            return instance
        
        return None

    @classmethod
    async def find_by_user(cls, user_id: str, limit: int = 20) -> List['ChatSession']:
        """
        Find all chat sessions for a given user.
        
        Args:
            user_id (str): The user ID to search for
            limit (int): Maximum number of sessions to return
            
        Returns:
            List[ChatSession]: List of ChatSession instances
        """
        db = mongo_service.get_collection("chat_sessions")
        cursor = db.find({"user_id": user_id}).sort("updated_at", -1).limit(limit)
        
        sessions = []
        async for document in cursor:
            instance = cls.__new__(cls)
            instance.db = db
            instance.id = document["_id"]
            instance.user_id = document.get("user_id")
            instance.title = document.get("title", f"Chat Session {document.get('created_at', datetime.utcnow()).strftime('%Y-%m-%d %H:%M')}")
            instance.metadata = document.get("metadata", {})
            instance.created_at = document.get("created_at", datetime.utcnow())
            instance.updated_at = document.get("updated_at", datetime.utcnow())
            instance._messages = []
            instance._messages_loaded = False
            sessions.append(instance)
        
        return sessions

    async def delete(self, delete_messages: bool = True) -> bool:
        """
        Delete the chat session from the database.
        
        Args:
            delete_messages (bool): If True, also delete all messages in this session
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            # Delete messages if requested
            if delete_messages:
                msg_db = mongo_service.get_collection("chat_messages")
                await msg_db.delete_many({"session_id": self.id})
            
            # Delete the session
            result = await self.db.delete_one({"_id": self.id})
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"Error deleting chat session: {e}")
            return False

    def __repr__(self) -> str:
        return f"ChatSession(id='{self.id}', user_id='{self.user_id}', message_count={len(self._messages)})"

    def __len__(self) -> int:
        """Return the number of messages in the session."""
        return len(self._messages)

    def __getitem__(self, index: int) -> ChatMessage:
        """Get a message by index."""
        return self._messages[index]

    def __iter__(self):
        """Make the session iterable over messages."""
        return iter(self._messages)