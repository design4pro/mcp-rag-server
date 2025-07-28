"""
Advanced Features for MCP RAG Server.

This module provides advanced features including:
- Batch processing for documents and memories
- Real-time streaming capabilities
- WebSocket integration
- Callback systems
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, AsyncGenerator
from datetime import datetime
import json
import uuid
from dataclasses import dataclass
from enum import Enum

from ..services.rag_service import RAGService
from ..services.mem0_service import Mem0Service
from ..services.session_service import SessionService

logger = logging.getLogger(__name__)


class StreamType(Enum):
    """Typy strumieniowania."""
    DOCUMENT_UPDATES = "document_updates"
    MEMORY_UPDATES = "memory_updates"
    SESSION_UPDATES = "session_updates"
    RAG_QUERIES = "rag_queries"
    SYSTEM_EVENTS = "system_events"


@dataclass
class StreamEvent:
    """Event strumieniowania."""
    event_id: str
    event_type: str
    timestamp: str
    data: Dict[str, Any]
    user_id: str
    session_id: Optional[str] = None


class AdvancedFeatures:
    """Zaawansowane funkcje dla MCP RAG Server."""
    
    def __init__(
        self, 
        rag_service: RAGService,
        mem0_service: Mem0Service,
        session_service: SessionService
    ):
        self.rag_service = rag_service
        self.mem0_service = mem0_service
        self.session_service = session_service
        self._active_streams = {}
        self._stream_subscribers = {}
        self._batch_processing_queue = asyncio.Queue()
        self._processing_task = None
    
    async def batch_add_documents(
        self, 
        documents: List[Dict[str, Any]], 
        user_id: str = "default",
        batch_size: int = 10,
        parallel_processing: bool = True
    ) -> Dict[str, Any]:
        """Wsadowe dodawanie dokumentów do RAG systemu."""
        try:
            if not documents:
                return {
                    "success": False,
                    "error": "No documents provided",
                    "total_documents": 0
                }
            
            total_documents = len(documents)
            successful = []
            failed = []
            
            if parallel_processing:
                # Przetwarzanie równoległe
                semaphore = asyncio.Semaphore(batch_size)
                
                async def process_document(doc: Dict[str, Any]) -> Dict[str, Any]:
                    async with semaphore:
                        try:
                            content = doc.get("content", "")
                            metadata = doc.get("metadata", {})
                            
                            result = await self.rag_service.add_document(
                                content, metadata, user_id
                            )
                            
                            return {
                                "success": True,
                                "document_id": result.get("document_id"),
                                "original_index": documents.index(doc)
                            }
                        except Exception as e:
                            return {
                                "success": False,
                                "error": str(e),
                                "original_index": documents.index(doc)
                            }
                
                # Utwórz zadania dla wszystkich dokumentów
                tasks = [process_document(doc) for doc in documents]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Przetwórz wyniki
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        failed.append({
                            "index": i,
                            "error": str(result)
                        })
                    elif result.get("success"):
                        successful.append(result)
                    else:
                        failed.append({
                            "index": i,
                            "error": result.get("error", "Unknown error")
                        })
            else:
                # Przetwarzanie sekwencyjne
                for i, doc in enumerate(documents):
                    try:
                        content = doc.get("content", "")
                        metadata = doc.get("metadata", {})
                        
                        result = await self.rag_service.add_document(
                            content, metadata, user_id
                        )
                        
                        successful.append({
                            "success": True,
                            "document_id": result.get("document_id"),
                            "original_index": i
                        })
                    except Exception as e:
                        failed.append({
                            "index": i,
                            "error": str(e)
                        })
            
            # Wyślij event strumieniowania
            await self._emit_stream_event(
                StreamType.DOCUMENT_UPDATES,
                {
                    "operation": "batch_add_documents",
                    "total_documents": total_documents,
                    "successful": len(successful),
                    "failed": len(failed),
                    "batch_size": batch_size,
                    "parallel_processing": parallel_processing
                },
                user_id
            )
            
            return {
                "success": True,
                "total_documents": total_documents,
                "successful": len(successful),
                "failed": len(failed),
                "results": {
                    "successful": successful,
                    "failed": failed
                },
                "processing_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "total_documents": len(documents) if documents else 0
            }
    
    async def batch_process_memories(
        self, 
        memories: List[Dict[str, Any]], 
        user_id: str = "default",
        batch_size: int = 20,
        memory_type: str = "conversation"
    ) -> Dict[str, Any]:
        """Wsadowe przetwarzanie pamięci."""
        try:
            if not memories:
                return {
                    "success": False,
                    "error": "No memories provided",
                    "total_memories": 0
                }
            
            total_memories = len(memories)
            successful = []
            failed = []
            
            # Przetwarzanie wsadowe
            for i in range(0, total_memories, batch_size):
                batch = memories[i:i + batch_size]
                
                # Przetwórz batch równolegle
                async def process_memory(memory: Dict[str, Any]) -> Dict[str, Any]:
                    try:
                        content = memory.get("content", "")
                        metadata = memory.get("metadata", {})
                        session_id = memory.get("session_id")
                        
                        memory_id = await self.mem0_service.add_memory(
                            user_id, content, memory_type, metadata, session_id=session_id
                        )
                        
                        return {
                            "success": True,
                            "memory_id": memory_id,
                            "original_index": memories.index(memory)
                        }
                    except Exception as e:
                        return {
                            "success": False,
                            "error": str(e),
                            "original_index": memories.index(memory)
                        }
                
                tasks = [process_memory(memory) for memory in batch]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Przetwórz wyniki batch
                for result in batch_results:
                    if isinstance(result, Exception):
                        failed.append({
                            "error": str(result)
                        })
                    elif result.get("success"):
                        successful.append(result)
                    else:
                        failed.append(result)
            
            # Wyślij event strumieniowania
            await self._emit_stream_event(
                StreamType.MEMORY_UPDATES,
                {
                    "operation": "batch_process_memories",
                    "total_memories": total_memories,
                    "successful": len(successful),
                    "failed": len(failed),
                    "memory_type": memory_type,
                    "batch_size": batch_size
                },
                user_id
            )
            
            return {
                "success": True,
                "total_memories": total_memories,
                "successful": len(successful),
                "failed": len(failed),
                "results": {
                    "successful": successful,
                    "failed": failed
                },
                "processing_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "total_memories": len(memories) if memories else 0
            }
    
    async def start_streaming(
        self, 
        stream_type: StreamType,
        user_id: str = "default",
        session_id: Optional[str] = None,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Uruchom strumieniowanie w czasie rzeczywistym."""
        try:
            stream_id = str(uuid.uuid4())
            
            # Utwórz stream
            stream_config = {
                "stream_id": stream_id,
                "stream_type": stream_type.value,
                "user_id": user_id,
                "session_id": session_id,
                "callback_url": callback_url,
                "started_at": datetime.now().isoformat(),
                "active": True
            }
            
            self._active_streams[stream_id] = stream_config
            
            # Dodaj subscriber
            if stream_id not in self._stream_subscribers:
                self._stream_subscribers[stream_id] = []
            
            # Uruchom background task dla streamingu
            asyncio.create_task(self._stream_processor(stream_id, stream_type))
            
            logger.info(f"Started streaming {stream_type.value} for user {user_id}")
            
            return {
                "success": True,
                "stream_id": stream_id,
                "stream_type": stream_type.value,
                "user_id": user_id,
                "session_id": session_id,
                "callback_url": callback_url,
                "started_at": stream_config["started_at"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stream_type": stream_type.value
            }
    
    async def stop_streaming(self, stream_id: str) -> Dict[str, Any]:
        """Zatrzymaj strumieniowanie."""
        try:
            if stream_id not in self._active_streams:
                return {
                    "success": False,
                    "error": f"Stream {stream_id} not found"
                }
            
            # Oznacz stream jako nieaktywny
            self._active_streams[stream_id]["active"] = False
            self._active_streams[stream_id]["stopped_at"] = datetime.now().isoformat()
            
            # Wyczyść subscribers
            if stream_id in self._stream_subscribers:
                del self._stream_subscribers[stream_id]
            
            logger.info(f"Stopped streaming {stream_id}")
            
            return {
                "success": True,
                "stream_id": stream_id,
                "stopped_at": self._active_streams[stream_id]["stopped_at"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stream_id": stream_id
            }
    
    async def subscribe_to_updates(
        self, 
        stream_id: str,
        callback: Callable[[StreamEvent], None]
    ) -> Dict[str, Any]:
        """Subskrybuj do aktualizacji strumienia."""
        try:
            if stream_id not in self._active_streams:
                return {
                    "success": False,
                    "error": f"Stream {stream_id} not found"
                }
            
            if not self._active_streams[stream_id]["active"]:
                return {
                    "success": False,
                    "error": f"Stream {stream_id} is not active"
                }
            
            # Dodaj callback do subscribers
            if stream_id not in self._stream_subscribers:
                self._stream_subscribers[stream_id] = []
            
            self._stream_subscribers[stream_id].append(callback)
            
            return {
                "success": True,
                "stream_id": stream_id,
                "subscribers_count": len(self._stream_subscribers[stream_id])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stream_id": stream_id
            }
    
    async def get_stream_status(self, stream_id: str) -> Dict[str, Any]:
        """Pobierz status strumienia."""
        try:
            if stream_id not in self._active_streams:
                return {
                    "success": False,
                    "error": f"Stream {stream_id} not found"
                }
            
            stream_config = self._active_streams[stream_id]
            subscribers_count = len(self._stream_subscribers.get(stream_id, []))
            
            return {
                "success": True,
                "stream_id": stream_id,
                "stream_type": stream_config["stream_type"],
                "user_id": stream_config["user_id"],
                "session_id": stream_config["session_id"],
                "active": stream_config["active"],
                "started_at": stream_config["started_at"],
                "stopped_at": stream_config.get("stopped_at"),
                "subscribers_count": subscribers_count,
                "callback_url": stream_config.get("callback_url")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stream_id": stream_id
            }
    
    async def list_active_streams(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Lista aktywnych strumieni."""
        try:
            active_streams = []
            
            for stream_id, config in self._active_streams.items():
                if config["active"] and (user_id is None or config["user_id"] == user_id):
                    active_streams.append({
                        "stream_id": stream_id,
                        "stream_type": config["stream_type"],
                        "user_id": config["user_id"],
                        "session_id": config["session_id"],
                        "started_at": config["started_at"],
                        "subscribers_count": len(self._stream_subscribers.get(stream_id, []))
                    })
            
            return {
                "success": True,
                "active_streams": active_streams,
                "total_count": len(active_streams)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _emit_stream_event(
        self, 
        stream_type: StreamType, 
        data: Dict[str, Any], 
        user_id: str,
        session_id: Optional[str] = None
    ):
        """Wyślij event do wszystkich aktywnych strumieni danego typu."""
        try:
            event = StreamEvent(
                event_id=str(uuid.uuid4()),
                event_type=stream_type.value,
                timestamp=datetime.now().isoformat(),
                data=data,
                user_id=user_id,
                session_id=session_id
            )
            
            # Znajdź wszystkie aktywne strumienie danego typu
            for stream_id, config in self._active_streams.items():
                if (config["active"] and 
                    config["stream_type"] == stream_type.value and
                    (config["user_id"] == user_id or config["user_id"] == "all")):
                    
                    # Wyślij do wszystkich subscribers
                    if stream_id in self._stream_subscribers:
                        for callback in self._stream_subscribers[stream_id]:
                            try:
                                await callback(event)
                            except Exception as e:
                                logger.error(f"Error in stream callback: {e}")
                    
                    # Wyślij do callback URL jeśli skonfigurowany
                    if config.get("callback_url"):
                        await self._send_webhook_event(config["callback_url"], event)
            
        except Exception as e:
            logger.error(f"Error emitting stream event: {e}")
    
    async def _stream_processor(self, stream_id: str, stream_type: StreamType):
        """Background processor dla strumieni."""
        try:
            while (stream_id in self._active_streams and 
                   self._active_streams[stream_id]["active"]):
                
                # Przetwarzaj różne typy strumieni
                if stream_type == StreamType.SYSTEM_EVENTS:
                    # System events - sprawdź co 30 sekund
                    await asyncio.sleep(30)
                    await self._emit_stream_event(
                        StreamType.SYSTEM_EVENTS,
                        {
                            "operation": "system_heartbeat",
                            "timestamp": datetime.now().isoformat(),
                            "active_streams": len(self._active_streams)
                        },
                        "system"
                    )
                else:
                    # Inne typy - sprawdź co 5 sekund
                    await asyncio.sleep(5)
                    
        except Exception as e:
            logger.error(f"Error in stream processor: {e}")
        finally:
            # Oznacz stream jako nieaktywny
            if stream_id in self._active_streams:
                self._active_streams[stream_id]["active"] = False
    
    async def _send_webhook_event(self, callback_url: str, event: StreamEvent):
        """Wyślij event do webhook URL."""
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                await client.post(
                    callback_url,
                    json={
                        "event_id": event.event_id,
                        "event_type": event.event_type,
                        "timestamp": event.timestamp,
                        "data": event.data,
                        "user_id": event.user_id,
                        "session_id": event.session_id
                    },
                    timeout=10.0
                )
        except Exception as e:
            logger.error(f"Error sending webhook event: {e}")
    
    async def cleanup(self):
        """Wyczyść wszystkie zasoby."""
        try:
            # Zatrzymaj wszystkie aktywne strumienie
            for stream_id in list(self._active_streams.keys()):
                await self.stop_streaming(stream_id)
            
            # Wyczyść kolekcje
            self._active_streams.clear()
            self._stream_subscribers.clear()
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}") 