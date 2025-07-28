"""
HTTP Integration Tools for MCP RAG Server.

This module provides MCP tools for HTTP integration including:
- Web content fetching
- External API calls
- HTTP response processing
- Automatic RAG integration
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx
from urllib.parse import urlparse
import json

from ..services.rag_service import RAGService
from ..services.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)


class HTTPIntegrationTools:
    """HTTP integration tools for MCP RAG Server."""
    
    def __init__(self, rag_service: RAGService, document_processor: DocumentProcessor):
        self.rag_service = rag_service
        self.document_processor = document_processor
        self.client = httpx.AsyncClient(timeout=30.0)
        self._active_streams = {}
    
    async def fetch_web_content(
        self, 
        url: str, 
        user_id: str = "default",
        auto_add_to_rag: bool = True,
        extract_metadata: bool = True
    ) -> Dict[str, Any]:
        """Pobierz zawartość z URL i opcjonalnie dodaj do RAG systemu."""
        try:
            # Walidacja URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return {
                    "success": False,
                    "error": "Invalid URL format",
                    "url": url
                }
            
            # Pobierz zawartość
            response = await self.client.get(url)
            response.raise_for_status()
            
            content = response.text
            content_type = response.headers.get("content-type", "")
            
            # Ekstrakcja metadanych
            metadata = {}
            if extract_metadata:
                metadata = {
                    "source_url": url,
                    "content_type": content_type,
                    "content_length": len(content),
                    "fetch_timestamp": datetime.now().isoformat(),
                    "domain": parsed_url.netloc,
                    "path": parsed_url.path
                }
            
            # Automatyczne dodanie do RAG
            if auto_add_to_rag and self.rag_service:
                try:
                    # Przetwórz zawartość przez document processor
                    processed_content = await self.document_processor.process_content(
                        content, metadata
                    )
                    
                    # Dodaj do RAG systemu
                    rag_result = await self.rag_service.add_document(
                        processed_content,
                        metadata,
                        user_id
                    )
                    
                    return {
                        "success": True,
                        "url": url,
                        "content_length": len(content),
                        "content_type": content_type,
                        "rag_integration": {
                            "added_to_rag": True,
                            "document_id": rag_result.get("document_id"),
                            "chunks_created": rag_result.get("chunks_created", 0)
                        },
                        "metadata": metadata
                    }
                except Exception as rag_error:
                    logger.warning(f"Failed to add content to RAG: {rag_error}")
                    return {
                        "success": True,
                        "url": url,
                        "content_length": len(content),
                        "content_type": content_type,
                        "rag_integration": {
                            "added_to_rag": False,
                            "error": str(rag_error)
                        },
                        "metadata": metadata
                    }
            else:
                return {
                    "success": True,
                    "url": url,
                    "content_length": len(content),
                    "content_type": content_type,
                    "rag_integration": {
                        "added_to_rag": False
                    },
                    "metadata": metadata
                }
                
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"HTTP error {e.response.status_code}: {e.response.text}",
                "url": url,
                "status_code": e.response.status_code
            }
        except httpx.RequestError as e:
            return {
                "success": False,
                "error": f"Request error: {str(e)}",
                "url": url
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url
            }
    
    async def call_external_api(
        self, 
        endpoint: str, 
        method: str = "GET", 
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        user_id: str = "default",
        auto_add_response_to_rag: bool = False
    ) -> Dict[str, Any]:
        """Wywołaj zewnętrzne API i opcjonalnie przetwórz odpowiedź."""
        try:
            # Przygotuj nagłówki
            request_headers = {
                "User-Agent": "MCP-RAG-Server/1.0",
                "Accept": "application/json"
            }
            if headers:
                request_headers.update(headers)
            
            # Wykonaj żądanie
            if method.upper() == "GET":
                response = await self.client.get(endpoint, headers=request_headers)
            elif method.upper() == "POST":
                response = await self.client.post(endpoint, json=data, headers=request_headers)
            elif method.upper() == "PUT":
                response = await self.client.put(endpoint, json=data, headers=request_headers)
            elif method.upper() == "DELETE":
                response = await self.client.delete(endpoint, headers=request_headers)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported HTTP method: {method}",
                    "endpoint": endpoint
                }
            
            response.raise_for_status()
            
            # Przetwórz odpowiedź
            response_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
            
            # Automatyczne dodanie odpowiedzi do RAG
            if auto_add_response_to_rag and self.rag_service:
                try:
                    metadata = {
                        "api_endpoint": endpoint,
                        "method": method,
                        "response_timestamp": datetime.now().isoformat(),
                        "status_code": response.status_code,
                        "content_type": response.headers.get("content-type", "")
                    }
                    
                    # Konwertuj odpowiedź na tekst jeśli to JSON
                    if isinstance(response_data, dict):
                        content = json.dumps(response_data, indent=2)
                    else:
                        content = str(response_data)
                    
                    # Dodaj do RAG
                    rag_result = await self.rag_service.add_document(
                        content,
                        metadata,
                        user_id
                    )
                    
                    return {
                        "success": True,
                        "endpoint": endpoint,
                        "method": method,
                        "status_code": response.status_code,
                        "response_data": response_data,
                        "rag_integration": {
                            "added_to_rag": True,
                            "document_id": rag_result.get("document_id")
                        }
                    }
                except Exception as rag_error:
                    logger.warning(f"Failed to add API response to RAG: {rag_error}")
                    return {
                        "success": True,
                        "endpoint": endpoint,
                        "method": method,
                        "status_code": response.status_code,
                        "response_data": response_data,
                        "rag_integration": {
                            "added_to_rag": False,
                            "error": str(rag_error)
                        }
                    }
            else:
                return {
                    "success": True,
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": response.status_code,
                    "response_data": response_data
                }
                
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"HTTP error {e.response.status_code}: {e.response.text}",
                "endpoint": endpoint,
                "method": method,
                "status_code": e.response.status_code
            }
        except httpx.RequestError as e:
            return {
                "success": False,
                "error": f"Request error: {str(e)}",
                "endpoint": endpoint,
                "method": method
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "endpoint": endpoint,
                "method": method
            }
    
    async def batch_fetch_urls(
        self, 
        urls: List[str], 
        user_id: str = "default",
        max_concurrent: int = 5,
        auto_add_to_rag: bool = True
    ) -> Dict[str, Any]:
        """Pobierz zawartość z wielu URL-i równolegle."""
        try:
            # Ogranicz liczbę równoczesnych żądań
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def fetch_single_url(url: str) -> Dict[str, Any]:
                async with semaphore:
                    return await self.fetch_web_content(url, user_id, auto_add_to_rag)
            
            # Wykonaj wszystkie żądania równolegle
            tasks = [fetch_single_url(url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Przetwórz wyniki
            successful = []
            failed = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed.append({
                        "url": urls[i],
                        "error": str(result)
                    })
                elif result.get("success"):
                    successful.append(result)
                else:
                    failed.append({
                        "url": urls[i],
                        "error": result.get("error", "Unknown error")
                    })
            
            return {
                "success": True,
                "total_urls": len(urls),
                "successful": len(successful),
                "failed": len(failed),
                "results": {
                    "successful": successful,
                    "failed": failed
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "total_urls": len(urls)
            }
    
    async def process_http_response(
        self, 
        response_data: Any, 
        processing_type: str = "extract_text",
        user_id: str = "default"
    ) -> Dict[str, Any]:
        """Przetwórz odpowiedź HTTP i dodaj do RAG systemu."""
        try:
            if processing_type == "extract_text":
                # Ekstrakcja tekstu z HTML
                if isinstance(response_data, str):
                    # Prosta ekstrakcja tekstu (można rozszerzyć o BeautifulSoup)
                    import re
                    text_content = re.sub(r'<[^>]+>', '', response_data)
                    text_content = re.sub(r'\s+', ' ', text_content).strip()
                    
                    metadata = {
                        "processing_type": "extract_text",
                        "original_length": len(response_data),
                        "extracted_length": len(text_content),
                        "processing_timestamp": datetime.now().isoformat()
                    }
                    
                    # Dodaj do RAG
                    if self.rag_service:
                        rag_result = await self.rag_service.add_document(
                            text_content,
                            metadata,
                            user_id
                        )
                        
                        return {
                            "success": True,
                            "processing_type": processing_type,
                            "extracted_text_length": len(text_content),
                            "rag_integration": {
                                "added_to_rag": True,
                                "document_id": rag_result.get("document_id")
                            }
                        }
            
            elif processing_type == "json_to_text":
                # Konwersja JSON na tekst
                if isinstance(response_data, dict):
                    text_content = json.dumps(response_data, indent=2)
                    
                    metadata = {
                        "processing_type": "json_to_text",
                        "original_keys": list(response_data.keys()),
                        "processing_timestamp": datetime.now().isoformat()
                    }
                    
                    # Dodaj do RAG
                    if self.rag_service:
                        rag_result = await self.rag_service.add_document(
                            text_content,
                            metadata,
                            user_id
                        )
                        
                        return {
                            "success": True,
                            "processing_type": processing_type,
                            "converted_text_length": len(text_content),
                            "rag_integration": {
                                "added_to_rag": True,
                                "document_id": rag_result.get("document_id")
                            }
                        }
            
            return {
                "success": False,
                "error": f"Unsupported processing type: {processing_type}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "processing_type": processing_type
            }
    
    async def cleanup(self):
        """Wyczyść zasoby HTTP client."""
        await self.client.aclose() 