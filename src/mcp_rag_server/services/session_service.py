"""
Session management service for MCP RAG Server.

This service handles user session creation, tracking, expiration,
and session-based memory organization.
"""

import logging
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import asyncio

from ..config import ServerConfig

logger = logging.getLogger(__name__)


class SessionService:
    """Service for managing user sessions."""
    
    def __init__(self, config: ServerConfig):
        """Initialize the session service."""
        self.config = config
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.user_sessions: Dict[str, List[str]] = {}
        self.session_stats: Dict[str, Dict[str, Any]] = {}
        self.storage_path = Path("./data/session_data")
        self._initialized = False
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def initialize(self):
        """Initialize the session service."""
        try:
            # Create storage directory
            self.storage_path.mkdir(parents=True, exist_ok=True)
            
            # Load existing sessions
            await self._load_sessions()
            
            # Start cleanup task
            self._start_cleanup_task()
            
            self._initialized = True
            logger.info("Session service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing session service: {e}")
            raise
    
    async def _load_sessions(self):
        """Load sessions from storage."""
        try:
            sessions_file = self.storage_path / "sessions.json"
            if sessions_file.exists():
                with open(sessions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.sessions = data.get("sessions", {})
                    self.user_sessions = data.get("user_sessions", {})
                    self.session_stats = data.get("session_stats", {})
                    
            logger.debug(f"Loaded {len(self.sessions)} sessions from storage")
            
        except Exception as e:
            logger.error(f"Error loading sessions: {e}")
            self.sessions = {}
            self.user_sessions = {}
            self.session_stats = {}
    
    async def _save_sessions(self):
        """Save sessions to storage."""
        try:
            sessions_file = self.storage_path / "sessions.json"
            data = {
                "sessions": self.sessions,
                "user_sessions": self.user_sessions,
                "session_stats": self.session_stats,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(sessions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error saving sessions: {e}")
            raise
    
    def _start_cleanup_task(self):
        """Start the session cleanup task."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.debug("Session cleanup task started")
    
    async def _cleanup_loop(self):
        """Background task for session cleanup."""
        while True:
            try:
                await self.cleanup_expired_sessions()
                # Run cleanup every 5 minutes
                await asyncio.sleep(300)
            except Exception as e:
                logger.error(f"Error in session cleanup loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def create_session(
        self, 
        user_id: str, 
        session_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new session for a user."""
        if not self._initialized:
            raise RuntimeError("Session service not initialized")
        
        try:
            session_id = str(uuid.uuid4())
            now = datetime.now()
            
            # Create session data
            session_data = {
                "id": session_id,
                "user_id": user_id,
                "name": session_name or f"Session {now.strftime('%Y-%m-%d %H:%M')}",
                "created_at": now.isoformat(),
                "last_activity": now.isoformat(),
                "status": "active",
                "metadata": metadata or {},
                "interaction_count": 0,
                "memory_count": 0
            }
            
            # Store session
            self.sessions[session_id] = session_data
            
            # Add to user sessions
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = []
            self.user_sessions[user_id].append(session_id)
            
            # Initialize session stats
            self.session_stats[session_id] = {
                "created_at": now.isoformat(),
                "interactions": 0,
                "memories_created": 0,
                "last_interaction": now.isoformat()
            }
            
            # Limit sessions per user
            max_sessions = getattr(self.config, 'max_sessions_per_user', 10)
            if len(self.user_sessions[user_id]) > max_sessions:
                # Remove oldest session
                oldest_session_id = self.user_sessions[user_id].pop(0)
                await self.expire_session(oldest_session_id)
            
            # Save to storage
            await self._save_sessions()
            
            logger.info(f"Created session {session_id} for user {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID."""
        if not self._initialized:
            raise RuntimeError("Session service not initialized")
        
        try:
            session = self.sessions.get(session_id)
            if session and session["status"] == "active":
                # Update last activity
                session["last_activity"] = datetime.now().isoformat()
                await self._save_sessions()
                return session
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting session: {e}")
            return None
    
    async def update_session(
        self, 
        session_id: str, 
        updates: Dict[str, Any]
    ) -> bool:
        """Update session data."""
        if not self._initialized:
            raise RuntimeError("Session service not initialized")
        
        try:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            
            # Update allowed fields
            allowed_fields = ["name", "metadata", "interaction_count", "memory_count"]
            for field, value in updates.items():
                if field in allowed_fields:
                    session[field] = value
            
            # Always update last activity
            session["last_activity"] = datetime.now().isoformat()
            
            await self._save_sessions()
            logger.debug(f"Updated session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating session: {e}")
            return False
    
    async def expire_session(self, session_id: str) -> bool:
        """Mark a session as expired."""
        if not self._initialized:
            raise RuntimeError("Session service not initialized")
        
        try:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            session["status"] = "expired"
            session["expired_at"] = datetime.now().isoformat()
            
            # Note: We keep expired sessions in user_sessions for include_expired=True queries
            # They will be removed during cleanup after 7 days
            
            await self._save_sessions()
            logger.info(f"Expired session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error expiring session: {e}")
            return False
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and old session data."""
        if not self._initialized:
            raise RuntimeError("Session service not initialized")
        
        try:
            cleaned_count = 0
            now = datetime.now()
            
            # Get session timeout (default: 24 hours)
            timeout_hours = getattr(self.config, 'session_timeout_hours', 24)
            timeout_delta = timedelta(hours=timeout_hours)
            
            # Find sessions to expire
            sessions_to_expire = []
            for session_id, session in self.sessions.items():
                if session["status"] == "active":
                    last_activity = datetime.fromisoformat(session["last_activity"])
                    if now - last_activity > timeout_delta:
                        sessions_to_expire.append(session_id)
            
            # Expire old sessions
            for session_id in sessions_to_expire:
                await self.expire_session(session_id)
                cleaned_count += 1
            
            # Clean up old expired sessions (older than 7 days)
            old_sessions = []
            cleanup_delta = timedelta(days=7)
            
            for session_id, session in self.sessions.items():
                if session["status"] == "expired":
                    expired_at = datetime.fromisoformat(session["expired_at"])
                    if now - expired_at > cleanup_delta:
                        old_sessions.append(session_id)
            
            # Remove old sessions
            for session_id in old_sessions:
                del self.sessions[session_id]
                if session_id in self.session_stats:
                    del self.session_stats[session_id]
                cleaned_count += 1
            
            if cleaned_count > 0:
                await self._save_sessions()
                logger.info(f"Cleaned up {cleaned_count} sessions")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning up sessions: {e}")
            return 0
    
    async def get_user_sessions(
        self, 
        user_id: str, 
        include_expired: bool = False
    ) -> List[Dict[str, Any]]:
        """Get all sessions for a user."""
        if not self._initialized:
            raise RuntimeError("Session service not initialized")
        
        try:
            session_ids = self.user_sessions.get(user_id, [])
            sessions = []
            
            for session_id in session_ids:
                session = self.sessions.get(session_id)
                if session and (include_expired or session["status"] == "active"):
                    sessions.append(session)
            
            # Sort by last activity (newest first)
            sessions.sort(key=lambda x: x["last_activity"], reverse=True)
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            return []
    
    async def get_session_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a session."""
        if not self._initialized:
            raise RuntimeError("Session service not initialized")
        
        try:
            stats = self.session_stats.get(session_id)
            if not stats:
                return None
            
            # Add current session info
            session = self.sessions.get(session_id)
            if session:
                stats["session_info"] = {
                    "name": session["name"],
                    "status": session["status"],
                    "created_at": session["created_at"],
                    "last_activity": session["last_activity"]
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting session stats: {e}")
            return None
    
    async def record_interaction(self, session_id: str) -> bool:
        """Record an interaction in a session."""
        if not self._initialized:
            raise RuntimeError("Session service not initialized")
        
        try:
            if session_id not in self.sessions:
                return False
            
            # Update session
            session = self.sessions[session_id]
            session["interaction_count"] += 1
            session["last_activity"] = datetime.now().isoformat()
            
            # Update stats
            if session_id in self.session_stats:
                self.session_stats[session_id]["interactions"] += 1
                self.session_stats[session_id]["last_interaction"] = datetime.now().isoformat()
            
            await self._save_sessions()
            return True
            
        except Exception as e:
            logger.error(f"Error recording interaction: {e}")
            return False
    
    async def record_memory_creation(self, session_id: str) -> bool:
        """Record memory creation in a session."""
        if not self._initialized:
            raise RuntimeError("Session service not initialized")
        
        try:
            if session_id not in self.sessions:
                return False
            
            # Update session
            session = self.sessions[session_id]
            session["memory_count"] += 1
            
            # Update stats
            if session_id in self.session_stats:
                self.session_stats[session_id]["memories_created"] += 1
            
            await self._save_sessions()
            return True
            
        except Exception as e:
            logger.error(f"Error recording memory creation: {e}")
            return False
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system session statistics."""
        if not self._initialized:
            raise RuntimeError("Session service not initialized")
        
        try:
            active_sessions = sum(1 for s in self.sessions.values() if s["status"] == "active")
            expired_sessions = sum(1 for s in self.sessions.values() if s["status"] == "expired")
            total_users = len(self.user_sessions)
            
            total_interactions = sum(
                stats.get("interactions", 0) 
                for stats in self.session_stats.values()
            )
            
            total_memories = sum(
                stats.get("memories_created", 0) 
                for stats in self.session_stats.values()
            )
            
            return {
                "active_sessions": active_sessions,
                "expired_sessions": expired_sessions,
                "total_users": total_users,
                "total_interactions": total_interactions,
                "total_memories": total_memories,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {}
    
    async def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up session service")
        
        # Stop cleanup task
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Save final state
        await self._save_sessions() 