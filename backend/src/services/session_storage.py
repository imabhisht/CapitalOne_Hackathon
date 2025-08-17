"""
Session Storage Service for managing user session data including location.
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

class SessionStorageService:
    """
    Simple in-memory session storage service.
    In production, this could be backed by Redis or database.
    """
    
    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        
    async def store_location(self, session_id: str, user_id: str, latitude: float, longitude: float):
        """Store location data for a session"""
        async with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = {}
            
            self._sessions[session_id].update({
                'user_id': user_id,
                'location': {
                    'latitude': latitude,
                    'longitude': longitude,
                    'timestamp': datetime.now().isoformat()
                }
            })
            
            logger.info(f"Stored location for session {session_id}: lat={latitude}, lon={longitude}")
    
    async def get_location(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get location data for a session"""
        async with self._lock:
            session_data = self._sessions.get(session_id, {})
            location = session_data.get('location')
            
            if location:
                logger.info(f"Retrieved location for session {session_id}: {location}")
                return location
            
            logger.warning(f"No location found for session {session_id}")
            return None
    
    def get_location_sync(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get location data for a session synchronously"""
        # For synchronous access, we don't need the lock since this is primarily read-only
        session_data = self._sessions.get(session_id, {})
        location = session_data.get('location')
        
        if location:
            logger.info(f"Retrieved location for session {session_id}: {location}")
            return location
        
        logger.warning(f"No location found for session {session_id}")
        return None
    
    async def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get all session data"""
        async with self._lock:
            return self._sessions.get(session_id)
    
    async def store_session_data(self, session_id: str, data: Dict[str, Any]):
        """Store arbitrary session data"""
        async with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = {}
            
            self._sessions[session_id].update(data)
    
    async def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Clean up old sessions (run periodically)"""
        async with self._lock:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            
            sessions_to_remove = []
            for session_id, session_data in self._sessions.items():
                location = session_data.get('location', {})
                timestamp_str = location.get('timestamp')
                
                if timestamp_str:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str)
                        if timestamp < cutoff_time:
                            sessions_to_remove.append(session_id)
                    except (ValueError, TypeError):
                        # Invalid timestamp, remove session
                        sessions_to_remove.append(session_id)
            
            for session_id in sessions_to_remove:
                del self._sessions[session_id]
                logger.info(f"Cleaned up old session: {session_id}")

# Global instance
session_storage = SessionStorageService()
