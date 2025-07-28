---
title: mcp-user-id-configuration-fix
type: note
permalink: docs/05-troubleshooting/mcp-user-id-configuration-fix
tags:
- '[''bug-fix'
- mcp-rag-server
- r-id-configuration'
- search-memories'
- '''troubleshooting'']'
---

# MCP User ID Configuration Fix

## Problem Description

The user reported two issues with the MCP RAG server:

1. **Missing `search_memories` method**: The server was trying to call `search_memories` on MemoryTools, but this method didn't exist, causing an AttributeError.

2. **User ID not being respected**: The system was defaulting to "default" instead of using the configured `MCP_USER_ID` environment variable (e.g., "remind_tools").

## Root Cause Analysis

### Issue 1: Missing search_memories Method
- The server.py file had a tool registered called `search_memories` that called `self.memory_tools.search_memories()`
- However, the MemoryTools class only had `get_memory_context` and `search_memories_advanced` methods
- No `search_memories` method existed, causing the AttributeError

### Issue 2: User ID Configuration Problem
- Tools were hardcoded to use `"default"` as the default user_id parameter
- The configuration system was properly set up with `MCP_USER_ID` in Mem0Config
- However, the tools weren't using the configured default user_id from the environment

## Solutions Implemented

### Fix 1: Added Missing search_memories Method

Added the missing `search_memories` method to `src/mcp_rag_server/tools/memory_tools.py`:

```python
async def search_memories(
    self, 
    query: str, 
    user_id: str, 
    limit: int = 5, 
    memory_type: Optional[str] = None
) -> Dict[str, Any]:
    """Search for relevant memories for a user."""
    if not self.mem0_service:
        return {"success": False, "error": "Mem0 service not initialized"}
    
    try:
        # Validate input
        if not user_id or not query:
            return {"success": False, "error": "User ID and query are required"}
        
        # Use the mem0 service search_memories method
        memories = await self.mem0_service.search_memories(
            user_id, query, limit, memory_type
        )
        
        return {
            "success": True,
            "memories": memories,
            "user_id": user_id,
            "query": query,
            "count": len(memories),
            "limit": limit,
            "memory_type": memory_type
        }
    except Exception as e:
        logger.error(f"Error searching memories: {e}")
        return {"success": False, "error": str(e)}
```

### Fix 2: Updated User ID Handling

Modified all MCP tools in `src/mcp_rag_server/server.py` to:

1. **Change default parameters**: Changed from `user_id: str = "default"` to `user_id: str = None`
2. **Use configured default**: Added logic to use `config.mem0.default_user_id` when no user_id is provided

#### Tools Updated:
- `add_document`
- `delete_document`
- `ask_question`
- `add_memory`
- `search_memories`
- `get_user_memories`
- `create_session`
- `list_sessions`
- `context_analysis`
- `fetch_web_content`
- `call_external_api`
- `batch_add_documents`

#### Example Pattern Applied:
```python
# Before
async def search_memories(query: str, user_id: str = "default", limit: int = 5, memory_type: str = None) -> dict:

# After
async def search_memories(query: str, user_id: str = None, limit: int = 5, memory_type: str = None) -> dict:
    # ...
    # Use configured default user_id if none provided
    effective_user_id = user_id or config.mem0.default_user_id
    
    result = await self.memory_tools.search_memories(
        query, effective_user_id, limit, memory_type
    )
```

## Configuration Validation

The validation schemas in `src/mcp_rag_server/validation.py` were already properly configured to use `config.mem0.default_user_id` as the default:

```python
class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=5000, description="Question to ask")
    user_id: str = Field(default=config.mem0.default_user_id, min_length=1, max_length=100, description="User ID")
    # ...
```

## Testing Recommendations

1. **Test with MCP_USER_ID=remind_tools**:
   ```bash
   MCP_USER_ID=remind_tools python -m src.run_server
   ```

2. **Verify search_memories works**:
   ```python
   # Should now work without AttributeError
   result = await client.call("search_memories", {
       "query": "test query",
       "user_id": "remind_tools",
       "limit": 5
   })
   ```

3. **Verify user_id defaults correctly**:
   ```python
   # Should use MCP_USER_ID from environment
   result = await client.call("search_memories", {
       "query": "test query",
       "limit": 5
   })
   ```

## Impact

- ✅ **Fixed AttributeError**: `search_memories` method now exists and works correctly
- ✅ **Respects MCP_USER_ID**: Tools now use the configured default user_id from environment variables
- ✅ **Backward Compatible**: Existing code that explicitly passes user_id still works
- ✅ **Consistent Behavior**: All tools now follow the same pattern for user_id handling

## Related Files

- `src/mcp_rag_server/tools/memory_tools.py` - Added missing method
- `src/mcp_rag_server/server.py` - Updated tool registrations
- `src/mcp_rag_server/config.py` - Configuration already correct
- `src/mcp_rag_server/validation.py` - Validation schemas already correct