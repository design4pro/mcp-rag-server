"""
Simple text splitter implementation.

This module provides a lightweight text splitting functionality to replace
the langchain dependency for document chunking.
"""

import re
from typing import List, Callable


class SimpleTextSplitter:
    """
    A simple text splitter that splits text into chunks based on separators.
    
    This is a lightweight replacement for langchain's RecursiveCharacterTextSplitter.
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: List[str] = None,
        length_function: Callable[[str], int] = None
    ):
        """
        Initialize the text splitter.
        
        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Number of characters to overlap between chunks
            separators: List of separators to use for splitting (in order of preference)
            length_function: Function to calculate text length (defaults to len)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", " ", ""]
        self.length_function = length_function or len
    
    def split_text(self, text: str) -> List[str]:
        """
        Split text into chunks.
        
        Args:
            text: The text to split
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        # If text is already smaller than chunk size, return it as is
        if self.length_function(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Split by the first separator that works
        for separator in self.separators:
            if separator in text:
                # Split the text by this separator
                parts = text.split(separator)
                
                for part in parts:
                    part_with_sep = part + separator if separator else part
                    
                    # If adding this part would exceed chunk size
                    if (self.length_function(current_chunk) + 
                        self.length_function(part_with_sep)) > self.chunk_size:
                        
                        # If we have a current chunk, add it to chunks
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            
                            # Start new chunk with overlap
                            if self.chunk_overlap > 0 and chunks:
                                # Get the end of the previous chunk for overlap
                                overlap_text = chunks[-1][-self.chunk_overlap:]
                                current_chunk = overlap_text + part_with_sep
                            else:
                                current_chunk = part_with_sep
                        else:
                            # If no current chunk, start with this part
                            current_chunk = part_with_sep
                    else:
                        # Add to current chunk
                        current_chunk += part_with_sep
                
                # Add the last chunk if it exists
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                break
        else:
            # If no separator worked, split by character count
            chunks = self._split_by_char_count(text)
        
        # Filter out empty chunks and ensure no chunk exceeds max size
        final_chunks = []
        for chunk in chunks:
            chunk = chunk.strip()
            if chunk:
                # If chunk is still too large, split it further
                if self.length_function(chunk) > self.chunk_size:
                    sub_chunks = self._split_by_char_count(chunk)
                    final_chunks.extend(sub_chunks)
                else:
                    final_chunks.append(chunk)
        
        return final_chunks
    
    def _split_by_char_count(self, text: str) -> List[str]:
        """
        Split text by character count when no separators work.
        
        Args:
            text: The text to split
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # If this is not the first chunk and we have overlap
            if start > 0 and self.chunk_overlap > 0:
                start = start - self.chunk_overlap
            
            # Ensure we don't go beyond text length
            if end > len(text):
                end = len(text)
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end
            
            # If we're at the end, break
            if start >= len(text):
                break
        
        return chunks
    
    def split_documents(self, documents: List[dict]) -> List[dict]:
        """
        Split a list of documents into chunks.
        
        Args:
            documents: List of documents with 'content' and optional 'metadata' keys
            
        Returns:
            List of document chunks
        """
        all_chunks = []
        
        for doc in documents:
            content = doc.get('content', '')
            metadata = doc.get('metadata', {})
            
            if not content:
                continue
            
            # Split the content
            text_chunks = self.split_text(content)
            
            # Create chunk documents
            for i, chunk in enumerate(text_chunks):
                chunk_metadata = metadata.copy()
                chunk_metadata['chunk_index'] = i
                chunk_metadata['total_chunks'] = len(text_chunks)
                
                all_chunks.append({
                    'content': chunk,
                    'metadata': chunk_metadata
                })
        
        return all_chunks 