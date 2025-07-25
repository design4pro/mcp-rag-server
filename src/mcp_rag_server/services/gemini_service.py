"""
Gemini API service for embeddings and text generation.

This service handles all interactions with Google's Gemini API including
text generation and embedding creation.
"""

import logging
from typing import List, Optional
from google import genai
from google.genai import types

from ..config import GeminiConfig

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Gemini API."""
    
    def __init__(self, config: GeminiConfig):
        """Initialize the Gemini service."""
        self.config = config
        self.client: Optional[genai.Client] = None
    
    async def initialize(self):
        """Initialize the Gemini client."""
        try:
            # Initialize the client
            self.client = genai.Client(api_key=self.config.api_key)
            
            logger.info(f"Gemini service initialized")
            
        except Exception as e:
            logger.error(f"Error initializing Gemini service: {e}")
            raise
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        if not self.client:
            raise RuntimeError("Gemini client not initialized")
        
        try:
            # Use the new API format
            result = self.client.models.embed_content(
                model=self.config.embedding_model,
                contents=texts
            )
            
            # Extract embeddings from the result
            embeddings = [embedding.values for embedding in result.embeddings]
            
            logger.debug(f"Generated embeddings for {len(texts)} texts")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    async def generate_text(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate text using the Gemini model."""
        if not self.client:
            raise RuntimeError("Gemini client not initialized")
        
        try:
            # Prepare the content
            if context:
                full_prompt = f"Context: {context}\n\nQuestion: {prompt}"
            else:
                full_prompt = prompt
            
            # Generate response using the new API format
            response = self.client.models.generate_content(
                model=self.config.model,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=self.config.max_tokens,
                    temperature=self.config.temperature
                )
            )
            
            logger.debug(f"Generated text response for prompt: {prompt[:50]}...")
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise
    
    async def generate_text_with_structured_output(self, prompt: str, schema: dict) -> dict:
        """Generate structured text output using Gemini."""
        if not self.client:
            raise RuntimeError("Gemini client not initialized")
        
        try:
            # Generate structured response
            response = self.client.models.generate_content(
                model=self.config.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=self.config.max_tokens,
                    temperature=self.config.temperature
                )
            )
            
            # For now, return the text response
            # TODO: Implement proper structured output parsing
            return {"text": response.text}
            
        except Exception as e:
            logger.error(f"Error generating structured text: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup resources."""
        # No specific cleanup needed for Gemini client
        pass