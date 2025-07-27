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
            
            # Build collection name with prefix for project isolation
            self.collection_name = self._get_collection_name()
            
            # Check if collection exists, create if not
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                await self._create_collection()
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Using existing collection: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Error initializing Qdrant service: {e}")
            raise
    
    def _get_collection_name(self) -> str:
        """Get collection name with prefix for project isolation."""
        if self.config.collection_prefix:
            return f"{self.config.collection_prefix}_{self.config.collection_name}"
        return self.config.collection_name
    
    async def _create_collection(self):
        """Create the documents collection."""
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
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
                collection_name=self.collection_name,
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
                collection_name=self.collection_name,
                query=query_embedding,
                limit=limit,
                with_payload=True,
                query_filter=query_filter
            )
            
            # Format results
            formatted_results = []
            for result in results:
                # Handle different result formats
                if hasattr(result, 'id'):
                    # ScoredPoint format
                    formatted_results.append({
                        "id": result.id,
                        "score": result.score,
                        "content": result.payload.get("content", ""),
                        "metadata": result.payload.get("metadata", {}),
                        "document_id": result.payload.get("document_id"),
                        "created_at": result.payload.get("created_at"),
                        "user_id": result.payload.get("user_id")
                    })
                elif isinstance(result, tuple) and len(result) >= 2:
                    # Tuple format (id, score, payload)
                    point_id, score, payload = result[0], result[1], result[2] if len(result) > 2 else {}
                    formatted_results.append({
                        "id": point_id,
                        "score": score,
                        "content": payload.get("content", ""),
                        "metadata": payload.get("metadata", {}),
                        "document_id": payload.get("document_id"),
                        "created_at": payload.get("created_at"),
                        "user_id": payload.get("user_id")
                    })
                else:
                    # Fallback format
                    logger.warning(f"Unexpected result format: {type(result)}")
                    continue
            
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
                collection_name=self.collection_name,
                points_selector=[document_id]
            )
            
            logger.info(f"Deleted document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID."""
        if not self.client:
            raise RuntimeError("Qdrant client not initialized")
        
        try:
            results = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[document_id],
                with_payload=True
            )
            
            if results and len(results) > 0:
                result = results[0]
                return {
                    "id": result.id,
                    "content": result.payload.get("content", ""),
                    "metadata": result.payload.get("metadata", {}),
                    "document_id": result.payload.get("document_id"),
                    "created_at": result.payload.get("created_at"),
                    "user_id": result.payload.get("user_id")
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting document from Qdrant: {e}")
            raise
    
    async def list_documents(self, user_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """List documents in the collection with optional user filtering."""
        if not self.client:
            raise RuntimeError("Qdrant client not initialized")
        
        try:
            # Build filter if user_id is specified
            query_filter = None
            if user_id:
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key="user_id",
                            match=MatchValue(value=user_id)
                        )
                    ]
                )
            
            # Get all points from collection
            results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=query_filter,
                limit=limit,
                with_payload=True
            )
            
            # Format results
            documents = []
            for result in results[0]:  # scroll returns (points, next_page_offset)
                documents.append({
                    "id": result.id,
                    "content": result.payload.get("content", ""),
                    "metadata": result.payload.get("metadata", {}),
                    "document_id": result.payload.get("document_id"),
                    "created_at": result.payload.get("created_at"),
                    "user_id": result.payload.get("user_id")
                })
            
            logger.info(f"Listed {len(documents)} documents from Qdrant")
            return documents
            
        except Exception as e:
            logger.error(f"Error listing documents from Qdrant: {e}")
            raise
    
    async def get_document_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics about documents in the collection."""
        if not self.client:
            raise RuntimeError("Qdrant client not initialized")
        
        try:
            # Get collection info
            collection_info = self.client.get_collection(self.collection_name)
            
            # Get document count
            total_documents = collection_info.points_count
            
            # Get user-specific count if user_id is specified
            user_documents = None
            if user_id:
                user_filter = Filter(
                    must=[
                        FieldCondition(
                            key="user_id",
                            match=MatchValue(value=user_id)
                        )
                    ]
                )
                
                # Count documents for specific user
                user_results = self.client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=user_filter,
                    limit=0  # We only need count
                )
                user_documents = len(user_results[0])
            
            stats = {
                "collection_name": self.collection_name,
                "total_documents": total_documents,
                "vector_size": self.config.vector_size,
                "distance_metric": self.config.distance_metric
            }
            
            if user_documents is not None:
                stats["user_documents"] = user_documents
            
            logger.info(f"Retrieved document stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting document stats from Qdrant: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.client:
            self.client.close()