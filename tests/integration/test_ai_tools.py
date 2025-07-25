"""
Integration tests for AdvancedAITools MCP tools.

These tests verify that the AdvancedAITools properly integrate with the underlying
AI services and expose their functionality as MCP tools.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from src.mcp_rag_server.tools.ai_tools import AdvancedAITools
from src.mcp_rag_server.services.reasoning_service import AdvancedReasoningEngine, ReasoningConfig
from src.mcp_rag_server.services.context_service import EnhancedContextService, ContextConfig


class TestAdvancedAIToolsIntegration:
    """Test AdvancedAITools integration with underlying AI services."""

    @pytest.fixture
    def reasoning_config(self):
        """Create reasoning configuration for testing."""
        return ReasoningConfig(
            max_reasoning_steps=5,
            confidence_threshold=0.7,
            enable_abductive=True,
            enable_planning=True
        )

    @pytest.fixture
    def context_config(self):
        """Create context configuration for testing."""
        return ContextConfig(
            max_context_depth=5,
            confidence_threshold=0.6,
            enable_temporal_analysis=True,
            enable_semantic_analysis=True,
            enable_relationship_mapping=True,
            context_timeout=30
        )

    @pytest.fixture
    def reasoning_engine(self, reasoning_config):
        """Create reasoning engine for testing."""
        return AdvancedReasoningEngine(reasoning_config)

    @pytest.fixture
    def context_service(self, context_config):
        """Create context service for testing."""
        return EnhancedContextService(context_config)

    @pytest.fixture
    def ai_tools(self, reasoning_engine, context_service):
        """Create AdvancedAITools instance for testing."""
        return AdvancedAITools(reasoning_engine, context_service)

    @pytest.mark.asyncio
    async def test_advanced_reasoning_tool(self, ai_tools):
        """Test advanced reasoning tool integration."""
        query = "If all mammals have lungs and dogs are mammals, what can we conclude?"
        context = {
            "facts": ["All mammals have lungs", "Dogs are mammals"],
            "rules": ["If X is a mammal, then X has lungs"]
        }

        result = await ai_tools.advanced_reasoning(query, context)

        assert result["success"] is True
        assert "reasoning_result" in result
        assert "query" in result
        assert "timestamp" in result
        assert result["reasoning_result"]["success"] is True

    @pytest.mark.asyncio
    async def test_chain_of_thought_reasoning_tool(self, ai_tools):
        """Test chain-of-thought reasoning tool integration."""
        query = "Analyze the relationship between mammals and breathing systems"
        context = {
            "facts": ["All mammals have lungs", "Dogs are mammals", "Cats are mammals"],
            "observations": ["Dogs breathe through their lungs", "Cats breathe through their lungs"]
        }

        result = await ai_tools.chain_of_thought_reasoning(query, context)

        assert result["success"] is True
        assert "chain_of_thought_result" in result
        assert "query" in result
        assert "timestamp" in result
        assert result["chain_of_thought_result"]["success"] is True

    @pytest.mark.asyncio
    async def test_multi_hop_reasoning_tool(self, ai_tools):
        """Test multi-hop reasoning tool integration."""
        query = "What are the implications of mammal breathing patterns?"
        context = {
            "facts": ["All mammals have lungs", "Lungs require oxygen", "Oxygen comes from air"],
            "observations": ["Mammals need to breathe continuously"]
        }

        result = await ai_tools.multi_hop_reasoning(query, context)

        assert result["success"] is True
        assert "multi_hop_result" in result
        assert "query" in result
        assert "timestamp" in result
        assert result["multi_hop_result"]["success"] is True

    @pytest.mark.asyncio
    async def test_analyze_context_tool(self, ai_tools):
        """Test context analysis tool integration."""
        query = "What are the key entities and relationships in this text?"
        additional_context = {
            "text": "The cat sat on the mat. The dog chased the cat.",
            "domain": "pet_behavior"
        }

        result = await ai_tools.analyze_context(query, additional_context)

        assert result["success"] is True
        assert "context_analysis" in result
        assert "query" in result
        assert "timestamp" in result
        assert result["context_analysis"]["success"] is True

    @pytest.mark.asyncio
    async def test_extract_relevant_context_tool(self, ai_tools):
        """Test relevant context extraction tool integration."""
        query = "Find information about cat behavior"
        context_data = {
            "documents": [
                {"content": "Cats are independent animals", "type": "behavior"},
                {"content": "Dogs are social animals", "type": "behavior"},
                {"content": "Cats hunt small prey", "type": "behavior"}
            ]
        }

        result = await ai_tools.extract_relevant_context(query, context_data)

        assert result["success"] is True
        assert "relevant_context" in result
        assert "query" in result
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_map_relationships_tool(self, ai_tools):
        """Test relationship mapping tool integration."""
        query = "Map relationships between animals and their behaviors"
        context = {
            "entities": ["cat", "dog", "hunting", "socializing", "sleeping"],
            "text": "Cats hunt prey. Dogs socialize with humans. Both animals sleep."
        }

        result = await ai_tools.map_relationships(query, context)

        assert result["success"] is True
        assert "relationship_mapping" in result
        assert "entities" in result
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_analyze_semantic_context_tool(self, ai_tools):
        """Test semantic context analysis tool integration."""
        query = "Analyze the semantic meaning of animal behavior patterns"
        context = {
            "text": "Cats exhibit hunting behavior while dogs show pack behavior",
            "domain": "animal_psychology"
        }

        result = await ai_tools.analyze_semantic_context(query, context)

        assert result["success"] is True
        assert "semantic_analysis" in result
        assert "query" in result
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_contextual_question_answering_tool(self, ai_tools):
        """Test contextual question answering tool integration."""
        question = "Why do cats hunt?"
        context = {
            "facts": ["Cats are natural predators", "Hunting is instinctive behavior"],
            "observations": ["Cats stalk their prey", "Cats use stealth to approach"]
        }

        result = await ai_tools.contextual_question_answering(question, context)

        assert result["success"] is True
        assert "answer" in result
        assert "reasoning_result" in result
        assert "context_analysis" in result
        assert "question" in result
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_advanced_query_understanding_tool(self, ai_tools):
        """Test advanced query understanding tool integration."""
        query = "What are the implications of predator-prey relationships in ecosystems?"
        context = {
            "domain": "ecology",
            "background": "Ecosystems depend on balanced predator-prey dynamics"
        }

        result = await ai_tools.advanced_query_understanding(query, context)

        assert result["success"] is True
        assert "query_understanding" in result
        assert "query" in result
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_get_reasoning_history_tool(self, ai_tools):
        """Test reasoning history retrieval tool integration."""
        # First, perform some reasoning to generate history
        await ai_tools.advanced_reasoning("Test query", {"test": "context"})
        
        result = await ai_tools.get_reasoning_history()

        assert result["success"] is True
        assert "reasoning_history" in result
        assert "limit" in result
        assert "timestamp" in result
        assert isinstance(result["reasoning_history"], list)

    @pytest.mark.asyncio
    async def test_get_context_history_tool(self, ai_tools):
        """Test context history retrieval tool integration."""
        # First, perform some context analysis to generate history
        await ai_tools.analyze_context("Test query", {"test": "context"})
        
        result = await ai_tools.get_context_history()

        assert result["success"] is True
        assert "context_history" in result
        assert "limit" in result
        assert "timestamp" in result
        assert isinstance(result["context_history"], list)

    @pytest.mark.asyncio
    async def test_clear_ai_history_tool(self, ai_tools):
        """Test AI history clearing tool integration."""
        # First, perform some operations to generate history
        await ai_tools.advanced_reasoning("Test query", {"test": "context"})
        await ai_tools.analyze_context("Test query", {"test": "context"})
        
        # Clear history
        result = await ai_tools.clear_ai_history()

        assert result["success"] is True
        assert "message" in result
        
        # Verify history is cleared
        reasoning_history = await ai_tools.get_reasoning_history()
        context_history = await ai_tools.get_context_history()
        
        assert len(reasoning_history["reasoning_history"]) == 0
        assert len(context_history["context_history"]) == 0

    @pytest.mark.asyncio
    async def test_error_handling_in_tools(self, ai_tools):
        """Test error handling in AI tools."""
        # Test with invalid input - the tools should handle this gracefully
        result = await ai_tools.advanced_reasoning("", {})
        
        # The tools should still return success=True but with empty results
        assert result["success"] is True
        assert "reasoning_result" in result

    @pytest.mark.asyncio
    async def test_tool_parameter_validation(self, ai_tools):
        """Test parameter validation in AI tools."""
        # Test with missing required parameters
        result = await ai_tools.analyze_context("", None)
        
        # The tools should handle this gracefully
        assert result["success"] is True
        assert "context_analysis" in result

    @pytest.mark.asyncio
    async def test_tool_response_structure(self, ai_tools):
        """Test that all tools return consistent response structures."""
        tools_to_test = [
            ("advanced_reasoning", "Test query", {"test": "context"}),
            ("chain_of_thought_reasoning", "Test query", {"test": "context"}),
            ("multi_hop_reasoning", "Test query", {"test": "context"}),
            ("analyze_context", "Test query", {"test": "context"}),
            ("extract_relevant_context", "Test query", {"test": "context"}),
            ("map_relationships", "Test query", {"test": "context"}),
            ("analyze_semantic_context", "Test query", {"test": "context"}),
            ("contextual_question_answering", "Test question", {"test": "context"}),
            ("advanced_query_understanding", "Test query", {"test": "context"})
        ]

        for tool_name, query, context in tools_to_test:
            tool_method = getattr(ai_tools, tool_name)
            result = await tool_method(query, context)
            
            # All tools should return a dict with at least success and some data
            assert isinstance(result, dict)
            assert "success" in result
            assert isinstance(result["success"], bool)

    @pytest.mark.asyncio
    async def test_tool_integration_with_real_services(self, reasoning_config, context_config):
        """Test that tools work with real service instances."""
        reasoning_engine = AdvancedReasoningEngine(reasoning_config)
        context_service = EnhancedContextService(context_config)
        ai_tools = AdvancedAITools(reasoning_engine, context_service)

        # Test a complete workflow
        query = "If all mammals have lungs and cats are mammals, what can we conclude?"
        context = {
            "facts": ["All mammals have lungs", "Cats are mammals"],
            "rules": ["If X is a mammal, then X has lungs"]
        }

        # Test reasoning
        reasoning_result = await ai_tools.advanced_reasoning(query, context)
        assert reasoning_result["success"] is True

        # Test context analysis
        context_result = await ai_tools.analyze_context(query, context)
        assert context_result["success"] is True

        # Test that both services are properly integrated
        assert ai_tools.reasoning_service is reasoning_engine
        assert ai_tools.context_service is context_service 