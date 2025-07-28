"""
Document processing service for chunking and preprocessing documents.

This service handles document ingestion, chunking, and preprocessing
for optimal storage and retrieval in the RAG system.
"""

import logging
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from ..utils.text_splitter import SimpleTextSplitter
import tiktoken

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Service for processing and chunking documents."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        max_chunks_per_document: int = 50
    ):
        """Initialize the document processor."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_chunks_per_document = max_chunks_per_document
        
        # Initialize text splitter
        self.text_splitter = SimpleTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
            length_function=len
        )
        
        # Initialize tokenizer for token counting
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            logger.warning(f"Could not initialize tiktoken: {e}")
            self.tokenizer = None
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Fallback: rough estimation (1 token ≈ 4 characters)
            return len(text) // 4
    
    def generate_chunk_id(self, content: str, index: int) -> str:
        """Generate a unique ID for a chunk."""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return f"{content_hash}_{index}"
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for better chunking."""
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Remove special characters that might interfere with chunking
        text = text.replace("\x00", "")  # Remove null bytes
        
        return text.strip()
    
    def chunk_document(
        self, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None,
        document_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Chunk a document into smaller pieces."""
        try:
            # Preprocess the content
            processed_content = self.preprocess_text(content)
            
            if not processed_content:
                logger.warning("Empty content after preprocessing")
                return []
            
            # Split the text into chunks
            chunks = self.text_splitter.split_text(processed_content)
            
            # Limit the number of chunks if needed
            if len(chunks) > self.max_chunks_per_document:
                logger.warning(f"Document has {len(chunks)} chunks, limiting to {self.max_chunks_per_document}")
                chunks = chunks[:self.max_chunks_per_document]
            
            # Create chunk documents
            chunk_documents = []
            for i, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue
                
                # Generate chunk metadata
                chunk_metadata = metadata.copy() if metadata else {}
                chunk_metadata.update({
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "chunk_size": len(chunk),
                    "token_count": self.count_tokens(chunk),
                    "document_id": document_id,
                    "processed_at": datetime.now().isoformat()
                })
                
                chunk_doc = {
                    "id": self.generate_chunk_id(chunk, i),
                    "content": chunk,
                    "metadata": chunk_metadata,
                    "document_id": document_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
                
                chunk_documents.append(chunk_doc)
            
            logger.info(f"Created {len(chunk_documents)} chunks from document")
            return chunk_documents
            
        except Exception as e:
            logger.error(f"Error chunking document: {e}")
            raise
    
    def process_documents(
        self, 
        documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process multiple documents and return all chunks."""
        all_chunks = []
        
        for doc in documents:
            try:
                content = doc.get("content", "")
                metadata = doc.get("metadata", {})
                document_id = doc.get("id")
                
                if not content:
                    logger.warning(f"Skipping document {document_id}: empty content")
                    continue
                
                chunks = self.chunk_document(content, metadata, document_id)
                all_chunks.extend(chunks)
                
            except Exception as e:
                logger.error(f"Error processing document {doc.get('id', 'unknown')}: {e}")
                continue
        
        logger.info(f"Processed {len(documents)} documents into {len(all_chunks)} chunks")
        return all_chunks
    
    def validate_document(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validate a document and return validation results."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "stats": {}
        }
        
        try:
            # Check content length
            if not content or not content.strip():
                validation_result["valid"] = False
                validation_result["errors"].append("Empty content")
                return validation_result
            
            # Count tokens
            token_count = self.count_tokens(content)
            validation_result["stats"]["token_count"] = token_count
            validation_result["stats"]["character_count"] = len(content)
            
            # Check if content is too large
            if token_count > 100000:  # 100k tokens limit
                validation_result["warnings"].append(f"Large document: {token_count} tokens")
            
            # Estimate chunks
            estimated_chunks = max(1, token_count // self.chunk_size)
            validation_result["stats"]["estimated_chunks"] = estimated_chunks
            
            if estimated_chunks > self.max_chunks_per_document:
                validation_result["warnings"].append(
                    f"Document may exceed chunk limit: {estimated_chunks} chunks"
                )
            
            # Validate metadata
            if metadata:
                if not isinstance(metadata, dict):
                    validation_result["errors"].append("Metadata must be a dictionary")
                else:
                    # Check for required fields
                    required_fields = ["source", "user_id"]
                    for field in required_fields:
                        if field not in metadata:
                            validation_result["warnings"].append(f"Missing metadata field: {field}")
            
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Validation error: {str(e)}")
        
        return validation_result
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "max_chunks_per_document": self.max_chunks_per_document,
            "tokenizer_available": self.tokenizer is not None
        }