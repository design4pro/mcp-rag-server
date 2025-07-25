"""
Unit tests for AdvancedReasoningEngine service.

Tests all reasoning types and functionality including:
- Deductive reasoning
- Inductive reasoning
- Abductive reasoning
- Planning reasoning
- Chain-of-thought reasoning
- Multi-hop reasoning
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any

from src.mcp_rag_server.services.reasoning_service import (
    AdvancedReasoningEngine, 
    ReasoningConfig, 
    ReasoningType,
    ReasoningStep
)


class TestAdvancedReasoningEngine:
    """Test cases for AdvancedReasoningEngine."""
    
    @pytest.fixture
    def reasoning_config(self):
        """Create a test reasoning configuration."""
        return ReasoningConfig(
            max_reasoning_steps=5,
            confidence_threshold=0.7,
            max_planning_depth=3,
            enable_abductive=True,
            enable_planning=True,
            reasoning_timeout=10
        )
    
    @pytest.fixture
    def reasoning_engine(self, reasoning_config):
        """Create a test reasoning engine instance."""
        return AdvancedReasoningEngine(reasoning_config)
    
    @pytest.fixture
    def sample_context(self):
        """Create a sample context for testing."""
        return {
            "facts": [
                "All mammals have lungs",
                "Dogs are mammals",
                "Cats are mammals"
            ],
            "rules": [
                "If X is a mammal, then X has lungs",
                "If X has lungs, then X can breathe air"
            ],
            "patterns": [
                {"type": "biological", "description": "Mammals have common characteristics", "confidence": 0.9}
            ],
            "observations": [
                "Dogs breathe through their nose",
                "Cats also breathe through their nose"
            ]
        }
    
    @pytest.mark.asyncio
    async def test_deductive_reasoning(self, reasoning_engine, sample_context):
        """Test deductive reasoning functionality."""
        query = "If dogs are mammals, then do they have lungs?"
        
        result = await reasoning_engine.reason(query, sample_context)
        
        assert result["success"] is True
        assert result["reasoning_type"] == "deductive"
        assert "premises" in result
        assert "conclusion" in result
        assert "confidence" in result
        assert result["confidence"] > 0.0
        assert "processing_time" in result
        assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_inductive_reasoning(self, reasoning_engine, sample_context):
        """Test inductive reasoning functionality."""
        query = "Based on the patterns, what can we generalize about mammals?"
        
        result = await reasoning_engine.reason(query, sample_context)
        
        assert result["success"] is True
        assert result["reasoning_type"] == "inductive"
        assert "patterns" in result
        assert "generalization" in result
        assert "confidence" in result
        assert result["confidence"] > 0.0
    
    @pytest.mark.asyncio
    async def test_abductive_reasoning(self, reasoning_engine, sample_context):
        """Test abductive reasoning functionality."""
        query = "Why do dogs and cats breathe through their nose?"
        
        result = await reasoning_engine.reason(query, sample_context)
        
        assert result["success"] is True
        assert result["reasoning_type"] == "abductive"
        assert "observations" in result
        assert "hypotheses" in result
        assert "best_hypothesis" in result
        assert "confidence" in result
        assert result["confidence"] > 0.0
    
    @pytest.mark.asyncio
    async def test_planning_reasoning(self, reasoning_engine, sample_context):
        """Test planning reasoning functionality."""
        query = "How to plan a study of mammal breathing patterns?"
        
        result = await reasoning_engine.reason(query, sample_context)
        
        assert result["success"] is True
        assert result["reasoning_type"] == "planning"
        assert "goal" in result
        assert "plan" in result
        assert "plan_validity" in result
        assert "confidence" in result
        assert result["confidence"] > 0.0
        assert isinstance(result["plan"], list)
        assert len(result["plan"]) > 0
    
    @pytest.mark.asyncio
    async def test_chain_of_thought_reasoning(self, reasoning_engine, sample_context):
        """Test chain-of-thought reasoning functionality."""
        query = "Analyze the relationship between mammals and breathing systems"
        
        result = await reasoning_engine.chain_of_thought_reasoning(query, sample_context)
        
        assert result["success"] is True
        assert result["reasoning_type"] == "chain_of_thought"
        assert "reasoning_chain" in result
        assert "final_result" in result
        assert "total_steps" in result
        assert isinstance(result["reasoning_chain"], list)
        assert len(result["reasoning_chain"]) > 0
        
        # Check that each step has required fields
        for step in result["reasoning_chain"]:
            assert "step_id" in step
            assert "reasoning_type" in step
            assert "premises" in step
            assert "conclusion" in step
            assert "confidence" in step
            assert "timestamp" in step
    
    @pytest.mark.asyncio
    async def test_multi_hop_reasoning(self, reasoning_engine, sample_context):
        """Test multi-hop reasoning functionality."""
        query = "What are the implications of mammal breathing patterns for evolution?"
        
        result = await reasoning_engine.multi_hop_reasoning(query, sample_context, max_hops=3)
        
        assert result["success"] is True
        assert result["reasoning_type"] == "multi_hop"
        assert "hops" in result
        assert "final_context" in result
        assert "total_hops" in result
        assert isinstance(result["hops"], list)
        assert len(result["hops"]) > 0
        
        # Check that each hop has required fields
        for hop in result["hops"]:
            assert "hop_number" in hop
            assert "reasoning" in hop
            assert "new_context" in hop
            assert "confidence" in hop
    
    @pytest.mark.asyncio
    async def test_query_type_analysis(self, reasoning_engine):
        """Test query type analysis functionality."""
        # Test deductive indicators
        deductive_query = "If X then Y, therefore Z"
        reasoning_type = await reasoning_engine._analyze_query_type(deductive_query)
        assert reasoning_type == ReasoningType.DEDUCTIVE
        
        # Test inductive indicators
        inductive_query = "Probably this will happen"
        reasoning_type = await reasoning_engine._analyze_query_type(inductive_query)
        assert reasoning_type == ReasoningType.INDUCTIVE
        
        # Test abductive indicators
        abductive_query = "Explain why this happened"
        reasoning_type = await reasoning_engine._analyze_query_type(abductive_query)
        assert reasoning_type == ReasoningType.ABDUCTIVE
        
        # Test planning indicators
        planning_query = "How to plan this process"
        reasoning_type = await reasoning_engine._analyze_query_type(planning_query)
        assert reasoning_type == ReasoningType.PLANNING
    
    @pytest.mark.asyncio
    async def test_premise_extraction(self, reasoning_engine, sample_context):
        """Test premise extraction functionality."""
        premises = reasoning_engine._extract_premises(sample_context)
        
        assert isinstance(premises, list)
        assert len(premises) > 0
        assert all(isinstance(premise, str) for premise in premises)
        
        # Check that facts and rules are included
        expected_premises = sample_context["facts"] + sample_context["rules"]
        assert len(premises) >= len(expected_premises)
    
    @pytest.mark.asyncio
    async def test_pattern_extraction(self, reasoning_engine, sample_context):
        """Test pattern extraction functionality."""
        patterns = reasoning_engine._extract_patterns(sample_context)
        
        assert isinstance(patterns, list)
        assert len(patterns) > 0
        assert all(isinstance(pattern, dict) for pattern in patterns)
    
    @pytest.mark.asyncio
    async def test_observation_extraction(self, reasoning_engine, sample_context):
        """Test observation extraction functionality."""
        query = "I observe that dogs breathe through their nose"
        observations = reasoning_engine._extract_observations(query, sample_context)
        
        assert isinstance(observations, list)
        assert len(observations) > 0
    
    @pytest.mark.asyncio
    async def test_goal_extraction(self, reasoning_engine):
        """Test goal extraction functionality."""
        query = "My goal is to understand mammal breathing"
        goal = reasoning_engine._extract_goal(query)
        
        assert isinstance(goal, str)
        assert len(goal) > 0
    
    @pytest.mark.asyncio
    async def test_logical_rules_application(self, reasoning_engine, sample_context):
        """Test logical rules application."""
        query = "What follows from the premises?"
        premises = reasoning_engine._extract_premises(sample_context)
        
        conclusion = await reasoning_engine._apply_logical_rules(query, premises)
        
        assert isinstance(conclusion, str)
        assert len(conclusion) > 0
    
    @pytest.mark.asyncio
    async def test_pattern_generalization(self, reasoning_engine, sample_context):
        """Test pattern generalization."""
        query = "What can we generalize?"
        patterns = reasoning_engine._extract_patterns(sample_context)
        
        generalization = await reasoning_engine._generalize_from_patterns(query, patterns)
        
        assert isinstance(generalization, str)
        assert len(generalization) > 0
    
    @pytest.mark.asyncio
    async def test_hypothesis_generation(self, reasoning_engine, sample_context):
        """Test hypothesis generation."""
        observations = reasoning_engine._extract_observations("Dogs breathe through nose", sample_context)
        
        hypotheses = await reasoning_engine._generate_hypotheses(observations, sample_context)
        
        assert isinstance(hypotheses, list)
        assert len(hypotheses) > 0
        assert all(isinstance(hypothesis, str) for hypothesis in hypotheses)
    
    @pytest.mark.asyncio
    async def test_plan_generation(self, reasoning_engine, sample_context):
        """Test plan generation."""
        goal = "Study mammal breathing patterns"
        
        plan = await reasoning_engine._generate_plan(goal, sample_context)
        
        assert isinstance(plan, list)
        assert len(plan) > 0
        assert all(isinstance(step, str) for step in plan)
    
    @pytest.mark.asyncio
    async def test_plan_validation(self, reasoning_engine, sample_context):
        """Test plan validation."""
        plan = ["Step 1", "Step 2", "Step 3"]
        
        validity = await reasoning_engine._validate_plan(plan, sample_context)
        
        assert isinstance(validity, bool)
    
    @pytest.mark.asyncio
    async def test_query_decomposition(self, reasoning_engine):
        """Test query decomposition."""
        query = "Analyze the complex relationship between mammals and breathing"
        
        steps = await reasoning_engine._decompose_query(query)
        
        assert isinstance(steps, list)
        assert len(steps) > 0
        assert all(isinstance(step, str) for step in steps)
    
    @pytest.mark.asyncio
    async def test_confidence_calculations(self, reasoning_engine):
        """Test confidence calculation methods."""
        # Test logical confidence
        premises = ["A", "B", "C"]
        conclusion = "D"
        confidence = reasoning_engine._calculate_logical_confidence(premises, conclusion)
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0
        
        # Test pattern confidence
        patterns = [{"type": "test", "confidence": 0.8}]
        generalization = "Test generalization"
        confidence = reasoning_engine._calculate_pattern_confidence(patterns, generalization)
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0
        
        # Test hypothesis confidence
        hypothesis = "Test hypothesis"
        observations = ["obs1", "obs2"]
        confidence = reasoning_engine._calculate_hypothesis_confidence(hypothesis, observations)
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0
        
        # Test plan confidence
        plan = ["step1", "step2"]
        plan_validity = True
        confidence = reasoning_engine._calculate_plan_confidence(plan, plan_validity)
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_temporal_pattern_analysis(self, reasoning_engine):
        """Test temporal pattern analysis."""
        episodes = [
            {"event_data": "Event 1", "timestamp": "2023-01-01"},
            {"event_data": "Event 2", "timestamp": "2023-01-02"}
        ]
        
        patterns = reasoning_engine._analyze_temporal_patterns(episodes)
        
        assert isinstance(patterns, list)
        assert len(patterns) > 0
    
    @pytest.mark.asyncio
    async def test_reasoning_history(self, reasoning_engine, sample_context):
        """Test reasoning history functionality."""
        # Perform some reasoning
        await reasoning_engine.reason("Test query 1", sample_context)
        await reasoning_engine.reason("Test query 2", sample_context)
        
        # Get history
        history = reasoning_engine.get_reasoning_history()
        
        assert isinstance(history, list)
        assert len(history) >= 2
        
        # Test history clearing
        reasoning_engine.clear_history()
        history_after_clear = reasoning_engine.get_reasoning_history()
        assert len(history_after_clear) == 0
    
    @pytest.mark.asyncio
    async def test_error_handling(self, reasoning_engine):
        """Test error handling in reasoning."""
        # Test with invalid context
        result = await reasoning_engine.reason("Test query", None)
        
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_configuration_options(self):
        """Test different configuration options."""
        # Test with disabled abductive reasoning
        config = ReasoningConfig(enable_abductive=False)
        engine = AdvancedReasoningEngine(config)
        
        query = "Why does this happen?"
        context = {"observations": ["obs1"]}
        
        result = await engine.reason(query, context)
        
        # Should fall back to general reasoning
        assert result["success"] is True
        assert result["reasoning_type"] == "general"
        
        # Test with disabled planning
        config = ReasoningConfig(enable_planning=False)
        engine = AdvancedReasoningEngine(config)
        
        query = "How to plan this?"
        result = await engine.reason(query, context)
        
        # Should fall back to general reasoning
        assert result["success"] is True
        assert result["reasoning_type"] == "general"


class TestReasoningStep:
    """Test cases for ReasoningStep class."""
    
    def test_reasoning_step_creation(self):
        """Test ReasoningStep creation and properties."""
        step = ReasoningStep(
            step_id="test_step",
            reasoning_type=ReasoningType.DEDUCTIVE,
            premises=["A", "B"],
            conclusion="C",
            confidence=0.8
        )
        
        assert step.step_id == "test_step"
        assert step.reasoning_type == ReasoningType.DEDUCTIVE
        assert step.premises == ["A", "B"]
        assert step.conclusion == "C"
        assert step.confidence == 0.8
        assert isinstance(step.timestamp, datetime)
        assert isinstance(step.metadata, dict)
    
    def test_reasoning_step_to_dict(self):
        """Test ReasoningStep to_dict conversion."""
        step = ReasoningStep(
            step_id="test_step",
            reasoning_type=ReasoningType.INDUCTIVE,
            premises=["A"],
            conclusion="B",
            confidence=0.7
        )
        
        step_dict = step.to_dict()
        
        assert isinstance(step_dict, dict)
        assert step_dict["step_id"] == "test_step"
        assert step_dict["reasoning_type"] == "inductive"
        assert step_dict["premises"] == ["A"]
        assert step_dict["conclusion"] == "B"
        assert step_dict["confidence"] == 0.7
        assert "timestamp" in step_dict
        assert "metadata" in step_dict


class TestReasoningConfig:
    """Test cases for ReasoningConfig."""
    
    def test_reasoning_config_defaults(self):
        """Test ReasoningConfig default values."""
        config = ReasoningConfig()
        
        assert config.max_reasoning_steps == 10
        assert config.confidence_threshold == 0.7
        assert config.max_planning_depth == 5
        assert config.enable_abductive is True
        assert config.enable_planning is True
        assert config.reasoning_timeout == 30
    
    def test_reasoning_config_custom_values(self):
        """Test ReasoningConfig with custom values."""
        config = ReasoningConfig(
            max_reasoning_steps=5,
            confidence_threshold=0.8,
            max_planning_depth=3,
            enable_abductive=False,
            enable_planning=False,
            reasoning_timeout=15
        )
        
        assert config.max_reasoning_steps == 5
        assert config.confidence_threshold == 0.8
        assert config.max_planning_depth == 3
        assert config.enable_abductive is False
        assert config.enable_planning is False
        assert config.reasoning_timeout == 15 