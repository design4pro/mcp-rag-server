"""
Qdrant vector database service.

This service handles all interactions with Qdrant vector database including
document storage, retrieval, and similarity search.
"""

import logging
import uuid
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, 
    Filter, FieldCondition, MatchValue
)

from ..config import QdrantConfig

logger = logging.getLogger(__name__)


class QdrantService:
    """Service for interacting with Qdrant vector database."""
    
    def __init__(self, config: QdrantConfig):
        """Initialize the Qdrant service."""
        self.config = config
        self.client: Optional[QdrantClient] = None
    
    async def initialize(self):
        """Initialize the Qdrant client and create collection if needed."""
        try:
            # Initialize client (no API key needed for local Docker)
            self.client = QdrantClient(url=self.config.url)
            
            # Check if collection exists, create if not
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.config.collection_name not in collection_names:
                await self._create_collection()
                logger.info(f"Created collection: {self.config.collection_name}")
            else:
                logger.info(f"Using existing collection: {self.config.collection_name}")
            
        except Exception as e:
            logger.error(f"Error initializing Qdrant service: {e}")
            raise
    
    async def _create_collection(self):
        """Create the documents collection."""
        try:
            self.client.create_collection(
                collection_name=self.config.collection_name,
                vectors_config=VectorParams(
                    size=self.config.vector_size,
                    distance=Distance.COSINE
                )
            )
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise
    
    async def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Add documents to the vector database."""
        if not self.client:
            raise RuntimeError("Qdrant client not initialized")
        
        try:
            points = []
            document_ids = []
            
            for doc in documents:
                doc_id = str(uuid.uuid4())
                document_ids.append(doc_id)
                
                point = PointStruct(
                    id=doc_id,
                    vector=doc["embedding"],
                    payload={
                        "content": doc["content"],
                        "metadata": doc.get("metadata", {}),
                        "document_id": doc_id,
                        "created_at": doc.get("created_at"),
                        "user_id": doc.get("user_id", "default")
                    }
                )
                points.append(point)
            
            # Insert points
            self.client.upsert(
                collection_name=self.config.collection_name,
                points=points
            )
            
            logger.info(f"Added {len(documents)} documents to Qdrant")
            return document_ids
            
        except Exception as e:
            logger.error(f"Error adding documents to Qdrant: {e}")
            raise
    
    async def search_documents(
        self, 
        query_embedding: List[float], 
        limit: int = 5,
        user_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        if not self.client:
            raise RuntimeError("Qdrant client not initialized")
        
        try:
            # Build filter if needed
            query_filter = None
            if user_id or filters:
                conditions = []
                
                if user_id:
                    conditions.append(
                        FieldCondition(
                            key="user_id",
                            match=MatchValue(value=user_id)
                        )
                    )
                
                if filters:
                    for key, value in filters.items():
                        conditions.append(
                            FieldCondition(
                                key=f"metadata.{key}",
                                match=MatchValue(value=value)
                            )
                        )
                
                query_filter = Filter(must=conditions)
            
            # Perform search using query_points (new API)
            results = self.client.query_points(
                collection_name=self.config.collection_name,
                query_vector=query_embedding,
                limit=limit,
                with_payload=True,
                query_filter=query_filter
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.id,
                    "score": result.score,
                    "content": result.payload.get("content", ""),
                    "metadata": result.payload.get("metadata", {}),
                    "document_id": result.payload.get("document_id"),
                    "created_at": result.payload.get("created_at"),
                    "user_id": result.payload.get("user_id")
                })
            
            logger.debug(f"Found {len(formatted_results)} similar documents")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching documents in Qdrant: {e}")
            raise
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document from the vector database."""
        if not self.client:
            raise RuntimeError("Qdrant client not initialized")
        
        try:
            self.client.delete(
                collection_name=self.config.collection_name,
                points_selector=[document_id]
            )
            
            logger.info(f"Deleted document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        if not self.client:
            raise RuntimeError("Qdrant client not initialized")
        
        try:
            results = self.client.retrieve(
                collection_name=self.config.collection_name,
                ids=[document_id],
                with_payload=True
            )
            
            if results:
                result = results[0]
                return {
                    "id": result.id,
                    "content": result.payload.get("content", ""),
                    "metadata": result.payload.get("metadata", {}),
                    "document_id": result.payload.get("document_id"),
                    "created_at": result.payload.get("created_at"),
                    "user_id": result.payload.get("user_id")
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting document {document_id}: {e}")
            return None
    
    async def cleanup(self):
        """Cleanup resources."""
        # No specific cleanup needed for Qdrant client
        pass