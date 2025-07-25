"""
Session management tools for MCP RAG Server.

This module provides FastMCP tools for creating, managing, and monitoring
user sessions in the RAG system.
"""

import logging
import json
from typing import Dict, List, Any, Optional

from ..validation import validate_session_creation, validate_session_id, validate_user_id
from ..services.session_service import SessionService

logger = logging.getLogger(__name__)


class SessionTools:
    """Session management tools for MCP RAG Server."""
    
    def __init__(self, session_service: SessionService):
        """Initialize session tools."""
        self.session_service = session_service
    
    async def create_session(
        self, 
        user_id: str, 
        session_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new session for a user."""
        try:
            # Validate input
            validated_params = validate_session_creation({
                "user_id": user_id,
                "session_name": session_name,
                "metadata": metadata or {}
            })
            
            # Create session
            session_id = await self.session_service.create_session(
                user_id=validated_params.user_id,
                session_name=validated_params.session_name,
                metadata=validated_params.metadata
            )
            
            return {
                "success": True,
                "session_id": session_id,
                "message": f"Session created successfully for user {user_id}"
            }
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create session: {str(e)}"
            }
    
    async def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get information about a specific session."""
        try:
            # Validate input
            validated_params = validate_session_id({"session_id": session_id})
            
            # Get session info
            session = await self.session_service.get_session(validated_params.session_id)
            if not session:
                return {
                    "success": False,
                    "error": "Session not found",
                    "message": f"Session {session_id} not found or expired"
                }
            
            # Get session stats
            stats = await self.session_service.get_session_stats(validated_params.session_id)
            
            return {
                "success": True,
                "session": session,
                "statistics": stats,
                "message": "Session information retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"Error getting session info: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get session info: {str(e)}"
            }
    
    async def list_user_sessions(
        self, 
        user_id: str, 
        include_expired: bool = False
    ) -> Dict[str, Any]:
        """List all sessions for a user."""
        try:
            # Validate input
            validated_params = validate_user_id({"user_id": user_id})
            
            # Get user sessions
            sessions = await self.session_service.get_user_sessions(
                user_id=validated_params.user_id,
                include_expired=include_expired
            )
            
            return {
                "success": True,
                "sessions": sessions,
                "count": len(sessions),
                "message": f"Found {len(sessions)} sessions for user {user_id}"
            }
            
        except Exception as e:
            logger.error(f"Error listing user sessions: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to list user sessions: {str(e)}"
            }
    
    async def expire_session(self, session_id: str) -> Dict[str, Any]:
        """Manually expire a session."""
        try:
            # Validate input
            validated_params = validate_session_id({"session_id": session_id})
            
            # Expire session
            success = await self.session_service.expire_session(validated_params.session_id)
            
            if success:
                return {
                    "success": True,
                    "message": f"Session {session_id} expired successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Session not found",
                    "message": f"Failed to expire session {session_id}. Session may not exist."
                }
            
        except Exception as e:
            logger.error(f"Error expiring session: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to expire session: {str(e)}"
            }
    
    async def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get session statistics."""
        try:
            # Validate input
            validated_params = validate_session_id({"session_id": session_id})
            
            # Get session stats
            stats = await self.session_service.get_session_stats(validated_params.session_id)
            
            if not stats:
                return {
                    "success": False,
                    "error": "Statistics not found",
                    "message": f"No statistics found for session {session_id}"
                }
            
            return {
                "success": True,
                "statistics": stats,
                "message": "Session statistics retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"Error getting session stats: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get session stats: {str(e)}"
            }
    
    async def get_system_session_stats(self) -> Dict[str, Any]:
        """Get overall system session statistics."""
        try:
            # Get system stats
            stats = await self.session_service.get_system_stats()
            
            return {
                "success": True,
                "statistics": stats,
                "message": "System session statistics retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"Error getting system session stats: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get system session stats: {str(e)}"
            } 