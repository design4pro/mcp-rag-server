"""
Example usage of Advanced Features for MCP RAG Server.

This example demonstrates how to use the advanced features:
- Batch processing for documents
- Batch processing for memories
- Real-time streaming
- WebSocket integration
"""

import asyncio
import json
from typing import Dict, Any, List


async def example_batch_add_documents():
    """Example: Batch add multiple documents to RAG system."""
    print("📦 Example: Batch adding documents...")
    
    # Example documents
    documents = [
        {
            "content": "Python is a high-level programming language known for its simplicity and readability.",
            "metadata": {"topic": "programming", "language": "python", "type": "introduction"}
        },
        {
            "content": "Machine learning is a subset of artificial intelligence that enables computers to learn without being explicitly programmed.",
            "metadata": {"topic": "ai", "category": "machine_learning", "type": "definition"}
        },
        {
            "content": "The Model Context Protocol (MCP) is a standardized way to provide context and tools to LLMs.",
            "metadata": {"topic": "mcp", "category": "protocol", "type": "definition"}
        },
        {
            "content": "FastMCP is a Pythonic framework for building MCP servers and clients with minimal boilerplate.",
            "metadata": {"topic": "fastmcp", "category": "framework", "type": "description"}
        },
        {
            "content": "Vector databases like Qdrant are optimized for storing and searching high-dimensional vector embeddings.",
            "metadata": {"topic": "vector_database", "category": "database", "type": "explanation"}
        }
    ]
    
    print(f"📄 Processing {len(documents)} documents in batch...")
    
    # This would be called via MCP tool
    # result = await batch_add_documents(documents, user_id="example_user", batch_size=3, parallel_processing=True)
    
    # Simulated result
    result = {
        "success": True,
        "total_documents": len(documents),
        "successful": 4,
        "failed": 1,
        "results": {
            "successful": [
                {"document_id": "doc_001", "original_index": 0},
                {"document_id": "doc_002", "original_index": 1},
                {"document_id": "doc_003", "original_index": 2},
                {"document_id": "doc_004", "original_index": 3}
            ],
            "failed": [
                {"index": 4, "error": "Content too long"}
            ]
        },
        "processing_time": "2025-01-25T10:00:00Z"
    }
    
    print(f"✅ Successful: {result['successful']}")
    print(f"❌ Failed: {result['failed']}")
    print(f"📊 Success rate: {result['successful']}/{result['total_documents']} ({result['successful']/result['total_documents']*100:.1f}%)")
    
    # Show successful documents
    for doc in result['results']['successful']:
        original_doc = documents[doc['original_index']]
        print(f"   📄 {doc['document_id']}: {original_doc['metadata']['topic']}")


async def example_batch_process_memories():
    """Example: Batch process multiple memories."""
    print("\n🧠 Example: Batch processing memories...")
    
    # Example memories
    memories = [
        {
            "content": "User asked about Python programming basics",
            "metadata": {"context": "learning", "topic": "python"},
            "session_id": "session_001"
        },
        {
            "content": "User requested help with machine learning algorithms",
            "metadata": {"context": "research", "topic": "ml"},
            "session_id": "session_001"
        },
        {
            "content": "User discussed MCP protocol implementation",
            "metadata": {"context": "development", "topic": "mcp"},
            "session_id": "session_002"
        },
        {
            "content": "User asked about vector database optimization",
            "metadata": {"context": "optimization", "topic": "database"},
            "session_id": "session_002"
        },
        {
            "content": "User requested code review for FastMCP integration",
            "metadata": {"context": "code_review", "topic": "fastmcp"},
            "session_id": "session_003"
        }
    ]
    
    print(f"🧠 Processing {len(memories)} memories in batch...")
    
    # This would be called via MCP tool
    # result = await batch_process_memories(memories, user_id="example_user", batch_size=2, memory_type="conversation")
    
    # Simulated result
    result = {
        "success": True,
        "total_memories": len(memories),
        "successful": 5,
        "failed": 0,
        "results": {
            "successful": [
                {"memory_id": "mem_001", "original_index": 0},
                {"memory_id": "mem_002", "original_index": 1},
                {"memory_id": "mem_003", "original_index": 2},
                {"memory_id": "mem_004", "original_index": 3},
                {"memory_id": "mem_005", "original_index": 4}
            ],
            "failed": []
        },
        "processing_time": "2025-01-25T10:00:00Z"
    }
    
    print(f"✅ Successful: {result['successful']}")
    print(f"❌ Failed: {result['failed']}")
    print(f"📊 Success rate: 100%")
    
    # Show successful memories
    for mem in result['results']['successful']:
        original_mem = memories[mem['original_index']]
        print(f"   🧠 {mem['memory_id']}: {original_mem['metadata']['topic']}")


async def example_streaming():
    """Example: Real-time streaming functionality."""
    print("\n📡 Example: Real-time streaming...")
    
    # Example stream types
    stream_types = [
        "document_updates",
        "memory_updates", 
        "system_events"
    ]
    
    for stream_type in stream_types:
        print(f"\n📡 Starting {stream_type} stream...")
        
        # This would be called via MCP tool
        # result = await start_streaming(stream_type, user_id="example_user", callback_url="https://webhook.site/example")
        
        # Simulated result
        result = {
            "success": True,
            "stream_id": f"stream_{stream_type}_{hash(stream_type)}",
            "stream_type": stream_type,
            "user_id": "example_user",
            "callback_url": "https://webhook.site/example",
            "started_at": "2025-01-25T10:00:00Z"
        }
        
        print(f"✅ Stream started: {result['stream_id']}")
        print(f"   Type: {result['stream_type']}")
        print(f"   Callback: {result['callback_url']}")
        
        # Simulate some events
        await asyncio.sleep(0.1)  # Simulate time passing
        
        # Check stream status
        # status = await get_stream_status(result['stream_id'])
        status = {
            "success": True,
            "stream_id": result['stream_id'],
            "active": True,
            "subscribers_count": 1,
            "started_at": result['started_at']
        }
        
        print(f"📊 Status: Active, {status['subscribers_count']} subscribers")
        
        # Stop stream
        # stop_result = await stop_streaming(result['stream_id'])
        stop_result = {
            "success": True,
            "stream_id": result['stream_id'],
            "stopped_at": "2025-01-25T10:01:00Z"
        }
        
        print(f"🛑 Stream stopped: {stop_result['stopped_at']}")


async def example_list_active_streams():
    """Example: List all active streams."""
    print("\n📋 Example: Listing active streams...")
    
    # This would be called via MCP tool
    # result = await list_active_streams(user_id="example_user")
    
    # Simulated result
    result = {
        "success": True,
        "active_streams": [
            {
                "stream_id": "stream_doc_123",
                "stream_type": "document_updates",
                "user_id": "example_user",
                "session_id": "session_001",
                "started_at": "2025-01-25T09:00:00Z",
                "subscribers_count": 2
            },
            {
                "stream_id": "stream_mem_456",
                "stream_type": "memory_updates",
                "user_id": "example_user",
                "session_id": "session_002",
                "started_at": "2025-01-25T09:30:00Z",
                "subscribers_count": 1
            },
            {
                "stream_id": "stream_sys_789",
                "stream_type": "system_events",
                "user_id": "system",
                "session_id": None,
                "started_at": "2025-01-25T08:00:00Z",
                "subscribers_count": 5
            }
        ],
        "total_count": 3
    }
    
    print(f"📊 Active streams: {result['total_count']}")
    
    for stream in result['active_streams']:
        print(f"   📡 {stream['stream_id']}")
        print(f"      Type: {stream['stream_type']}")
        print(f"      User: {stream['user_id']}")
        print(f"      Subscribers: {stream['subscribers_count']}")
        print(f"      Started: {stream['started_at']}")


async def example_stream_events():
    """Example: Simulate stream events."""
    print("\n🎯 Example: Stream events simulation...")
    
    # Simulate different types of events
    events = [
        {
            "event_type": "document_updates",
            "data": {
                "operation": "document_added",
                "document_id": "doc_123",
                "user_id": "example_user",
                "timestamp": "2025-01-25T10:00:00Z"
            }
        },
        {
            "event_type": "memory_updates",
            "data": {
                "operation": "memory_added",
                "memory_id": "mem_456",
                "user_id": "example_user",
                "memory_type": "conversation",
                "timestamp": "2025-01-25T10:01:00Z"
            }
        },
        {
            "event_type": "system_events",
            "data": {
                "operation": "system_heartbeat",
                "active_streams": 3,
                "memory_usage": "45%",
                "timestamp": "2025-01-25T10:02:00Z"
            }
        }
    ]
    
    for event in events:
        print(f"\n📡 Event: {event['event_type']}")
        print(f"   Operation: {event['data']['operation']}")
        print(f"   Timestamp: {event['data']['timestamp']}")
        
        if event['event_type'] == "document_updates":
            print(f"   Document ID: {event['data']['document_id']}")
        elif event['event_type'] == "memory_updates":
            print(f"   Memory ID: {event['data']['memory_id']}")
            print(f"   Type: {event['data']['memory_type']}")
        elif event['event_type'] == "system_events":
            print(f"   Active Streams: {event['data']['active_streams']}")
            print(f"   Memory Usage: {event['data']['memory_usage']}")


async def main():
    """Run all advanced features examples."""
    print("🚀 Advanced Features Examples for MCP RAG Server")
    print("=" * 50)
    
    await example_batch_add_documents()
    await example_batch_process_memories()
    await example_streaming()
    await example_list_active_streams()
    await example_stream_events()
    
    print("\n✅ All advanced features examples completed!")


if __name__ == "__main__":
    asyncio.run(main()) 