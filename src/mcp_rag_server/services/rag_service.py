"""
RAG (Retrieval-Augmented Generation) service.

This service orchestrates the entire RAG pipeline including document ingestion,
embedding generation, vector storage, retrieval, and response generation.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from .gemini_service import GeminiService
from .qdrant_service import QdrantService
from .mem0_service import Mem0Service
from .session_service import SessionService
from .document_processor import DocumentProcessor

logger = logging.getLogger(__name__)


class RAGService:
    """Main RAG service that orchestrates all components."""
    
    def __init__(
        self,
        gemini_service: GeminiService,
        qdrant_service: QdrantService,
        mem0_service: Optional[Mem0Service] = None,
        session_service: Optional[SessionService] = None,
        document_processor: Optional[DocumentProcessor] = None
    ):
        """Initialize the RAG service."""
        self.gemini_service = gemini_service
        self.qdrant_service = qdrant_service
        self.mem0_service = mem0_service
        self.session_service = session_service
        self.document_processor = document_processor or DocumentProcessor()
        self._initialized = False
    
    async def initialize(self):
        """Initialize the RAG service."""
        try:
            # Verify all required services are initialized
            if not self.gemini_service:
                raise RuntimeError("Gemini service is required")
            if not self.qdrant_service:
                raise RuntimeError("Qdrant service is required")
            
            self._initialized = True
            logger.info("RAG service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing RAG service: {e}")
            raise
    
    async def add_document(
        self, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None,
        user_id: str = "default"
    ) -> Dict[str, Any]:
        """Add a document to the RAG system (with chunking and batch embedding)."""
        if not self._initialized:
            raise RuntimeError("RAG service not initialized")
        try:
            document_id = str(uuid.uuid4())
            doc_metadata = metadata or {}
            doc_metadata.update({
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "document_id": document_id
            })
            # Chunk document
            chunks = self.document_processor.chunk_document(content, doc_metadata, document_id)
            if not chunks:
                raise ValueError("No valid chunks produced from document")
            # Batch embedding
            chunk_texts = [chunk["content"] for chunk in chunks]
            embeddings = await self.gemini_service.generate_embeddings(chunk_texts)
            # Prepare chunk docs for Qdrant
            chunk_documents = []
            for chunk, embedding in zip(chunks, embeddings):
                chunk_doc = {
                    "content": chunk["content"],
                    "embedding": embedding,
                    "metadata": chunk["metadata"],
                    "document_id": document_id,
                    "created_at": chunk["metadata"].get("processed_at"),
                    "user_id": user_id,
                    "chunk_index": chunk["chunk_index"],
                    "total_chunks": chunk["total_chunks"]
                }
                chunk_documents.append(chunk_doc)
            # Store all chunks in Qdrant
            chunk_ids = await self.qdrant_service.add_documents(chunk_documents)
            logger.info(f"Added document {document_id} as {len(chunk_documents)} chunks to RAG system")
            return {
                "id": document_id,
                "success": True,
                "metadata": doc_metadata,
                "chunks": len(chunk_documents)
            }
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            raise
    
    async def search_documents(
        self, 
        query: str, 
        limit: int = 5,
        user_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for documents using semantic search (returns top chunks grouped by document_id)."""
        if not self._initialized:
            raise RuntimeError("RAG service not initialized")
        try:
            query_embeddings = await self.gemini_service.generate_embeddings([query])
            query_embedding = query_embeddings[0]
            results = await self.qdrant_service.search_documents(
                query_embedding=query_embedding,
                limit=limit,
                user_id=user_id,
                filters=filters
            )
            # Group by document_id
            doc_groups = {}
            for chunk in results:
                doc_id = chunk.get("metadata", {}).get("document_id") or chunk.get("document_id")
                if doc_id not in doc_groups:
                    doc_groups[doc_id] = {
                        "document_id": doc_id,
                        "chunks": [],
                        "score": chunk["score"],
                        "metadata": chunk.get("metadata", {})
                    }
                doc_groups[doc_id]["chunks"].append(chunk)
                # Use best score for doc
                if chunk["score"] > doc_groups[doc_id]["score"]:
                    doc_groups[doc_id]["score"] = chunk["score"]
            # Sort by score
            grouped_results = sorted(doc_groups.values(), key=lambda x: x["score"], reverse=True)
            return grouped_results[:limit]
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise
    
    async def ask_question(
        self, 
        question: str, 
        user_id: str = "default",
        session_id: Optional[str] = None,
        use_memory: bool = True,
        max_context_docs: int = 3
    ) -> str:
        """Ask a question using RAG with optional memory context."""
        if not self._initialized:
            raise RuntimeError("RAG service not initialized")
        
        try:
            # Record interaction if session is provided
            if session_id and self.session_service:
                await self.session_service.record_interaction(session_id)
            
            # Get relevant memories if available
            memory_context = ""
            if use_memory and self.mem0_service:
                # Generate embedding for the question
                question_embedding = await self.gemini_service.generate_embeddings([question])
                query_embedding = question_embedding[0] if question_embedding else None
                
                # Use session-aware memory search if session is provided
                if session_id:
                    memories = await self.mem0_service.search_memories_by_session(
                        user_id=user_id,
                        session_id=session_id,
                        query=question,
                        query_embedding=query_embedding,
                        limit=3
                    )
                else:
                    # Use hybrid memory search for non-session queries
                    memories = await self.mem0_service.search_memories_hybrid(
                        user_id=user_id,
                        query=question,
                        query_embedding=query_embedding,
                        limit=3
                    )
                
                if memories:
                    # Format memory context with length management
                    memory_context = await self.mem0_service.format_memory_context(memories)
                    memory_context += "\n"
            
            # Search for relevant documents
            relevant_docs = await self.search_documents(
                query=question,
                limit=max_context_docs,
                user_id=user_id
            )
            
            # Prepare context from documents
            document_context = ""
            if relevant_docs:
                document_context = "Relevant documents:\n"
                for i, doc in enumerate(relevant_docs, 1):
                    # Handle grouped results from search_documents
                    if "chunks" in doc and doc["chunks"]:
                        # Use the first chunk's content
                        content = doc["chunks"][0]["content"]
                    else:
                        # Fallback to direct content field
                        content = doc.get("content", "No content available")
                    document_context += f"{i}. {content[:200]}...\n"
                document_context += "\n"
            
            # Generate response
            full_context = memory_context + document_context
            response = await self.gemini_service.generate_text(
                prompt=question,
                context=full_context if full_context.strip() else None
            )
            
            # Store the interaction in memory with embedding
            if use_memory and self.mem0_service:
                # Generate embedding for the memory content
                memory_content = f"Q: {question}\nA: {response}"
                memory_embedding = await self.gemini_service.generate_embeddings([memory_content])
                embedding = memory_embedding[0] if memory_embedding else None
                
                # Add memory with session context if available
                if session_id:
                    await self.mem0_service.add_memory_with_session(
                        user_id=user_id,
                        content=memory_content,
                        session_id=session_id,
                        memory_type="conversation",
                        embedding=embedding
                    )
                    # Record memory creation in session
                    if self.session_service:
                        await self.session_service.record_memory_creation(session_id)
                else:
                    await self.mem0_service.add_memory(
                        user_id=user_id,
                        content=memory_content,
                        memory_type="conversation",
                        embedding=embedding
                    )
            
            logger.info(f"Generated RAG response for user {user_id} with enhanced memory context")
            return response
            
        except Exception as e:
            logger.error(f"Error asking question: {e}")
            raise
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document from the RAG system."""
        if not self._initialized:
            raise RuntimeError("RAG service not initialized")
        
        try:
            success = await self.qdrant_service.delete_document(document_id)
            if success:
                logger.info(f"Deleted document {document_id} from RAG system")
            return success
            
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID."""
        if not self._initialized:
            raise RuntimeError("RAG service not initialized")
        
        try:
            return await self.qdrant_service.get_document(document_id)
            
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            return None
    
    async def list_documents(self, user_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """List documents in the RAG system."""
        if not self._initialized:
            raise RuntimeError("RAG service not initialized")
        
        try:
            return await self.qdrant_service.list_documents(user_id=user_id, limit=limit)
            
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            raise
    
    async def get_system_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get system statistics."""
        if not self._initialized:
            raise RuntimeError("RAG service not initialized")
        
        try:
            stats = {
                "total_documents": 0,
                "memory_stats": None,
                "user_id": user_id
            }
            
            # Get document count
            documents = await self.list_documents(user_id=user_id, limit=1000)
            stats["total_documents"] = len(documents)
            
            # Get memory stats if available
            if self.mem0_service and user_id:
                memory_stats = await self.mem0_service.get_memory_stats(user_id)
                stats["memory_stats"] = memory_stats
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {"error": str(e)}
    
    async def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up RAG service")
        # No specific cleanup needed for RAG service
        pass