"""
Basic usage example for MCP RAG Server.

This example demonstrates how to use the RAG server for document management
and question answering.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp_rag_server import MCPRAGServer
from mcp_rag_server.config import config


async def main():
    """Main example function."""
    print("🚀 Starting MCP RAG Server Example")
    
    # Initialize the server
    server = MCPRAGServer()
    
    try:
        # Initialize services
        await server.initialize_services()
        print("✅ Services initialized successfully")
        
        # Example documents
        documents = [
            {
                "content": """
                Python is a high-level, interpreted programming language known for its simplicity and readability. 
                It was created by Guido van Rossum and first released in 1991. Python supports multiple programming 
                paradigms including procedural, object-oriented, and functional programming.
                """,
                "metadata": {"source": "wikipedia", "topic": "programming", "language": "python"}
            },
            {
                "content": """
                Machine learning is a subset of artificial intelligence that enables computers to learn and make 
                decisions without being explicitly programmed. It uses algorithms and statistical models to analyze 
                and draw inferences from patterns in data.
                """,
                "metadata": {"source": "wikipedia", "topic": "ai", "field": "machine_learning"}
            },
            {
                "content": """
                The Model Context Protocol (MCP) is an open protocol that standardizes how applications provide 
                context to Large Language Models (LLMs). It enables secure, standardized connections between 
                AI models and various data sources and tools.
                """,
                "metadata": {"source": "mcp_docs", "topic": "ai", "protocol": "mcp"}
            }
        ]
        
        # Add documents to the system
        print("\n📚 Adding documents to the RAG system...")
        for i, doc in enumerate(documents, 1):
            result = await server.rag_service.add_document(
                content=doc["content"],
                metadata=doc["metadata"],
                user_id="example_user"
            )
            print(f"  ✅ Document {i} added: {result['id']}")
        
        # Search for documents
        print("\n🔍 Searching for documents...")
        search_results = await server.rag_service.search_documents(
            query="programming languages",
            limit=3,
            user_id="example_user"
        )
        
        print(f"  Found {len(search_results)} relevant documents:")
        for i, result in enumerate(search_results, 1):
            print(f"    {i}. Score: {result['score']:.3f} - {result['content'][:100]}...")
        
        # Ask questions using RAG
        questions = [
            "What is Python?",
            "How does machine learning work?",
            "What is the Model Context Protocol?",
            "What are the benefits of Python for programming?"
        ]
        
        print("\n❓ Asking questions using RAG...")
        for i, question in enumerate(questions, 1):
            print(f"\n  Question {i}: {question}")
            answer = await server.rag_service.ask_question(
                question=question,
                user_id="example_user",
                use_memory=True,
                max_context_docs=2
            )
            print(f"  Answer: {answer}")
        
        # Get system statistics
        print("\n📊 System Statistics:")
        stats = await server.rag_service.get_system_stats(user_id="example_user")
        print(f"  Total documents: {stats['total_documents']}")
        if stats.get('memory_stats'):
            print(f"  Memory entries: {stats['memory_stats'].get('total_memories', 0)}")
        
        # List all documents
        print("\n📋 All documents in system:")
        all_docs = await server.rag_service.list_documents(user_id="example_user")
        for i, doc in enumerate(all_docs, 1):
            print(f"  {i}. {doc['metadata'].get('topic', 'Unknown topic')} - {doc['content'][:50]}...")
        
        print("\n✅ Example completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during example: {e}")
        raise
    
    finally:
        # Cleanup
        await server.cleanup_services()
        print("🧹 Services cleaned up")


if __name__ == "__main__":
    # Check if required environment variables are set
    required_vars = ["GEMINI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file or environment")
        sys.exit(1)
    
    # Run the example
    asyncio.run(main())