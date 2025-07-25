"""
Unit tests for EnhancedContextService.

Tests all context understanding functionality including:
- Context analysis
- Entity extraction
- Relationship mapping
- Semantic analysis
- Temporal analysis
- Conceptual analysis
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any

from src.mcp_rag_server.services.context_service import (
    EnhancedContextService,
    ContextConfig,
    ContextType,
    ContextEntity,
    ContextRelationship
)


class TestEnhancedContextService:
    """Test cases for EnhancedContextService."""
    
    @pytest.fixture
    def context_config(self):
        """Create a test context configuration."""
        return ContextConfig(
            max_context_depth=3,
            confidence_threshold=0.6,
            enable_temporal_analysis=True,
            enable_semantic_analysis=True,
            enable_relationship_mapping=True,
            context_timeout=10
        )
    
    @pytest.fixture
    def context_service(self, context_config):
        """Create a test context service instance."""
        return EnhancedContextService(context_config)
    
    @pytest.fixture
    def sample_context(self):
        """Create a sample context for testing."""
        return {
            "entities": [
                {
                    "entity_id": "entity_1",
                    "entity_type": "concept",
                    "name": "Machine Learning",
                    "properties": {"domain": "AI", "confidence": 0.9},
                    "relationships": [],
                    "confidence": 0.9,
                    "timestamp": datetime.now()
                },
                {
                    "entity_id": "entity_2",
                    "entity_type": "concept",
                    "name": "Neural Networks",
                    "properties": {"domain": "AI", "confidence": 0.8},
                    "relationships": [],
                    "confidence": 0.8,
                    "timestamp": datetime.now()
                }
            ],
            "relationships": [
                {
                    "relationship_id": "rel_1",
                    "source_entity": "entity_1",
                    "target_entity": "entity_2",
                    "relationship_type": "includes",
                    "properties": {"confidence": 0.7},
                    "confidence": 0.7,
                    "timestamp": datetime.now()
                }
            ],
            "patterns": [
                {"type": "technological", "description": "AI technologies", "confidence": 0.8}
            ],
            "observations": [
                "Machine learning is used in neural networks",
                "Both are part of AI field"
            ]
        }
    
    @pytest.mark.asyncio
    async def test_analyze_context(self, context_service, sample_context):
        """Test context analysis functionality."""
        query = "How do machine learning and neural networks relate?"
        user_id = "test_user"
        
        result = await context_service.analyze_context(query, user_id, sample_context)
        
        assert result["success"] is True
        assert "entities" in result
        assert "relationships" in result
        assert "context_types" in result
        assert "metadata" in result
        assert "processing_time" in result
        assert "timestamp" in result
        assert "user_id" in result
        assert result["user_id"] == user_id
        
        # Check context types
        context_types = result["context_types"]
        assert "temporal" in context_types
        assert "semantic" in context_types
        assert "conceptual" in context_types
    
    @pytest.mark.asyncio
    async def test_extract_relevant_context(self, context_service, sample_context):
        """Test relevant context extraction."""
        query = "What is machine learning?"
        relevance_threshold = 0.5
        
        result = await context_service.extract_relevant_context(
            query, sample_context, relevance_threshold
        )
        
        assert result["success"] is True
        assert "relevant_context" in result
        assert "relevance_threshold" in result
        assert "query_entities" in result
        assert "query_keywords" in result
        
        relevant_context = result["relevant_context"]
        assert "entities" in relevant_context
        assert "relationships" in relevant_context
        assert "temporal_context" in relevant_context
        assert "semantic_context" in relevant_context
        assert "conceptual_context" in relevant_context
    
    @pytest.mark.asyncio
    async def test_map_relationships(self, context_service, sample_context):
        """Test relationship mapping functionality."""
        entities = sample_context["entities"]
        
        result = await context_service.map_relationships(entities)
        
        assert result["success"] is True
        assert "relationships" in result
        assert "relationship_graph" in result
        assert "total_relationships" in result
        
        # Check relationship graph structure
        graph = result["relationship_graph"]
        assert "nodes" in graph
        assert "edges" in graph
        assert "metadata" in graph
        
        # Check metadata
        metadata = graph["metadata"]
        assert "total_nodes" in metadata
        assert "total_edges" in metadata
        assert "density" in metadata
    
    @pytest.mark.asyncio
    async def test_analyze_semantic_context(self, context_service, sample_context):
        """Test semantic context analysis."""
        query = "What are the semantic relationships in AI?"
        
        result = await context_service.analyze_semantic_context(query, sample_context)
        
        assert result["success"] is True
        assert "semantic_features" in result
        assert "semantic_relationships" in result
        assert "concept_mapping" in result
        assert "semantic_similarity" in result
    
    @pytest.mark.asyncio
    async def test_entity_extraction(self, context_service, sample_context):
        """Test entity extraction functionality."""
        query = "Machine Learning and Neural Networks are AI technologies"
        
        entities = await context_service._extract_entities(query, sample_context)
        
        assert isinstance(entities, list)
        assert len(entities) > 0
        
        # Check entity structure
        for entity in entities:
            assert "entity_id" in entity
            assert "entity_type" in entity
            assert "name" in entity
            assert "properties" in entity
            assert "relationships" in entity
            assert "confidence" in entity
            assert "timestamp" in entity
    
    @pytest.mark.asyncio
    async def test_relationship_analysis(self, context_service, sample_context):
        """Test relationship analysis functionality."""
        entities = sample_context["entities"]
        
        relationships = await context_service._analyze_relationships(entities)
        
        assert isinstance(relationships, list)
        
        if len(relationships) > 0:
            # Check relationship structure
            for relationship in relationships:
                assert "relationship_id" in relationship
                assert "source_entity" in relationship
                assert "target_entity" in relationship
                assert "relationship_type" in relationship
                assert "properties" in relationship
                assert "confidence" in relationship
                assert "timestamp" in relationship
    
    @pytest.mark.asyncio
    async def test_temporal_context_analysis(self, context_service, sample_context):
        """Test temporal context analysis."""
        query = "When did machine learning become popular?"
        
        temporal_context = await context_service._analyze_temporal_context(query, sample_context["entities"])
        
        assert isinstance(temporal_context, dict)
        assert "temporal_indicators" in temporal_context
        assert "time_references" in temporal_context
        assert "temporal_relationships" in temporal_context
    
    @pytest.mark.asyncio
    async def test_semantic_context_analysis(self, context_service, sample_context):
        """Test semantic context analysis."""
        query = "What is the meaning of machine learning?"
        
        semantic_context = await context_service._analyze_semantic_context(query, sample_context["entities"])
        
        assert isinstance(semantic_context, dict)
        assert "semantic_features" in semantic_context
        assert "concept_hierarchy" in semantic_context
        assert "semantic_similarity" in semantic_context
    
    @pytest.mark.asyncio
    async def test_conceptual_context_analysis(self, context_service, sample_context):
        """Test conceptual context analysis."""
        query = "What concepts are related to AI?"
        
        conceptual_context = await context_service._analyze_conceptual_context(query, sample_context["entities"])
        
        assert isinstance(conceptual_context, dict)
        assert "concepts" in conceptual_context
        assert "concept_relationships" in conceptual_context
        assert "conceptual_framework" in conceptual_context
    
    @pytest.mark.asyncio
    async def test_comprehensive_context_building(self, context_service, sample_context):
        """Test comprehensive context building."""
        entities = sample_context["entities"]
        relationships = sample_context["relationships"]
        temporal_context = {"temporal_indicators": ["when"]}
        semantic_context = {"semantic_features": []}
        conceptual_context = {"concepts": []}
        
        comprehensive_context = await context_service._build_comprehensive_context(
            entities, relationships, temporal_context, semantic_context, conceptual_context
        )
        
        assert comprehensive_context["success"] is True
        assert "entities" in comprehensive_context
        assert "relationships" in comprehensive_context
        assert "context_types" in comprehensive_context
        assert "metadata" in comprehensive_context
        
        metadata = comprehensive_context["metadata"]
        assert "total_entities" in metadata
        assert "total_relationships" in metadata
        assert "context_depth" in metadata
    
    @pytest.mark.asyncio
    async def test_keyword_extraction(self, context_service):
        """Test keyword extraction functionality."""
        query = "What is machine learning and how does it work?"
        
        keywords = await context_service._extract_keywords(query)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert all(isinstance(keyword, str) for keyword in keywords)
        
        # Check that stop words are filtered out
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        assert not any(keyword in stop_words for keyword in keywords)
    
    @pytest.mark.asyncio
    async def test_entity_relevance_calculation(self, context_service, sample_context):
        """Test entity relevance calculation."""
        entity = sample_context["entities"][0]
        query_entities = [{"name": "Machine Learning"}]
        query_keywords = ["machine", "learning"]
        
        relevance_score = await context_service._calculate_entity_relevance(
            entity, query_entities, query_keywords
        )
        
        assert isinstance(relevance_score, float)
        assert 0.0 <= relevance_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_relationship_relevance_calculation(self, context_service, sample_context):
        """Test relationship relevance calculation."""
        relationship = sample_context["relationships"][0]
        query_entities = [{"name": "Machine Learning"}]
        query_keywords = ["relationship", "includes"]
        
        relevance_score = await context_service._calculate_relationship_relevance(
            relationship, query_entities, query_keywords
        )
        
        assert isinstance(relevance_score, float)
        assert 0.0 <= relevance_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_entity_relationship_analysis(self, context_service, sample_context):
        """Test entity relationship analysis."""
        entity1 = sample_context["entities"][0]
        entity2 = sample_context["entities"][1]
        
        relationship = await context_service._analyze_entity_relationship(entity1, entity2)
        
        if relationship:
            assert "relationship_id" in relationship
            assert "source_entity" in relationship
            assert "target_entity" in relationship
            assert "relationship_type" in relationship
            assert "properties" in relationship
            assert "confidence" in relationship
            assert "timestamp" in relationship
    
    @pytest.mark.asyncio
    async def test_relationship_graph_building(self, context_service, sample_context):
        """Test relationship graph building."""
        entities = sample_context["entities"]
        relationships = sample_context["relationships"]
        
        graph = await context_service._build_relationship_graph(entities, relationships)
        
        assert "nodes" in graph
        assert "edges" in graph
        assert "metadata" in graph
        
        # Check nodes
        nodes = graph["nodes"]
        assert len(nodes) == len(entities)
        for node in nodes:
            assert "id" in node
            assert "label" in node
            assert "type" in node
            assert "properties" in node
        
        # Check edges
        edges = graph["edges"]
        assert len(edges) == len(relationships)
        for edge in edges:
            assert "id" in edge
            assert "source" in edge
            assert "target" in edge
            assert "type" in edge
            assert "properties" in edge
    
    @pytest.mark.asyncio
    async def test_semantic_feature_extraction(self, context_service):
        """Test semantic feature extraction."""
        query = "Machine learning algorithms process data"
        
        features = await context_service._extract_semantic_features(query)
        
        assert isinstance(features, list)
        assert len(features) > 0
        
        for feature in features:
            assert "word" in feature
            assert "type" in feature
            assert "semantic_role" in feature
            assert "confidence" in feature
    
    @pytest.mark.asyncio
    async def test_semantic_relationship_analysis(self, context_service, sample_context):
        """Test semantic relationship analysis."""
        semantic_features = [
            {"word": "machine", "type": "noun", "semantic_role": "subject", "confidence": 0.8},
            {"word": "learning", "type": "noun", "semantic_role": "object", "confidence": 0.7}
        ]
        
        relationships = await context_service._analyze_semantic_relationships(semantic_features, sample_context)
        
        assert isinstance(relationships, list)
        
        if len(relationships) > 0:
            for relationship in relationships:
                assert "source_feature" in relationship
                assert "target_feature" in relationship
                assert "relationship_type" in relationship
                assert "confidence" in relationship
    
    @pytest.mark.asyncio
    async def test_concept_mapping(self, context_service, sample_context):
        """Test concept mapping functionality."""
        query = "What concepts are related to AI?"
        
        concept_mapping = await context_service._perform_concept_mapping(query, sample_context)
        
        assert isinstance(concept_mapping, dict)
        assert "concepts" in concept_mapping
        assert "mappings" in concept_mapping
        assert "hierarchy" in concept_mapping
    
    @pytest.mark.asyncio
    async def test_semantic_similarity_analysis(self, context_service, sample_context):
        """Test semantic similarity analysis."""
        query = "machine learning algorithms"
        entities = sample_context["entities"]
        
        similarities = await context_service._analyze_semantic_similarity(query, entities)
        
        assert isinstance(similarities, dict)
        
        for entity_id, similarity in similarities.items():
            assert isinstance(similarity, float)
            assert 0.0 <= similarity <= 1.0
    
    @pytest.mark.asyncio
    async def test_concept_extraction(self, context_service, sample_context):
        """Test concept extraction functionality."""
        query = "Machine learning and neural networks"
        entities = sample_context["entities"]
        
        concepts = await context_service._extract_concepts(query, entities)
        
        assert isinstance(concepts, list)
        assert len(concepts) > 0
        
        for concept in concepts:
            assert "concept_id" in concept
            assert "name" in concept
            assert "type" in concept
            assert "source" in concept
            assert "confidence" in concept
    
    @pytest.mark.asyncio
    async def test_concept_relationship_analysis(self, context_service):
        """Test concept relationship analysis."""
        concepts = [
            {"concept_id": "concept_1", "name": "Machine Learning"},
            {"concept_id": "concept_2", "name": "Neural Networks"}
        ]
        
        relationships = await context_service._analyze_concept_relationships(concepts)
        
        assert isinstance(relationships, list)
        
        if len(relationships) > 0:
            for relationship in relationships:
                assert "source_concept" in relationship
                assert "target_concept" in relationship
                assert "relationship_type" in relationship
                assert "confidence" in relationship
    
    @pytest.mark.asyncio
    async def test_concept_hierarchy_building(self, context_service, sample_context):
        """Test concept hierarchy building."""
        entities = sample_context["entities"]
        
        hierarchy = await context_service._build_concept_hierarchy(entities)
        
        assert isinstance(hierarchy, dict)
        assert "root_concepts" in hierarchy
        assert "sub_concepts" in hierarchy
        assert "relationships" in hierarchy
    
    @pytest.mark.asyncio
    async def test_context_history(self, context_service, sample_context):
        """Test context history functionality."""
        # Perform some context analysis
        await context_service.analyze_context("Test query 1", "user1", sample_context)
        await context_service.analyze_context("Test query 2", "user2", sample_context)
        
        # Get history
        history = context_service.get_context_history()
        
        assert isinstance(history, list)
        assert len(history) >= 2
        
        # Test history clearing
        context_service.clear_history()
        history_after_clear = context_service.get_context_history()
        assert len(history_after_clear) == 0
    
    @pytest.mark.asyncio
    async def test_context_caching(self, context_service, sample_context):
        """Test context caching functionality."""
        query = "Test query for caching"
        user_id = "test_user"
        
        # First analysis
        result1 = await context_service.analyze_context(query, user_id, sample_context)
        
        # Second analysis (should use cache)
        result2 = await context_service.analyze_context(query, user_id, sample_context)
        
        assert result1["success"] is True
        assert result2["success"] is True
        
        # Test cache retrieval
        context_key = f"{user_id}_{hash(query)}"
        cached_context = context_service.get_cached_context(context_key)
        
        assert cached_context is not None
        
        # Test cache clearing
        context_service.clear_cache()
        cached_context_after_clear = context_service.get_cached_context(context_key)
        assert cached_context_after_clear is None
    
    @pytest.mark.asyncio
    async def test_error_handling(self, context_service):
        """Test error handling in context analysis."""
        # Test with invalid input
        result = await context_service.analyze_context("", "user1", None)
        
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_configuration_options(self):
        """Test different configuration options."""
        # Test with disabled temporal analysis
        config = ContextConfig(enable_temporal_analysis=False)
        service = EnhancedContextService(config)
        
        query = "When did this happen?"
        entities = []
        
        temporal_context = await service._analyze_temporal_context(query, entities)
        assert temporal_context == {}
        
        # Test with disabled semantic analysis
        config = ContextConfig(enable_semantic_analysis=False)
        service = EnhancedContextService(config)
        
        semantic_context = await service._analyze_semantic_context(query, {})
        assert semantic_context == {}


class TestContextEntity:
    """Test cases for ContextEntity class."""
    
    def test_context_entity_creation(self):
        """Test ContextEntity creation and properties."""
        entity = ContextEntity(
            entity_id="test_entity",
            entity_type="concept",
            name="Test Entity",
            properties={"domain": "test", "confidence": 0.8},
            relationships=["rel1", "rel2"],
            confidence=0.8,
            timestamp=datetime.now()
        )
        
        assert entity.entity_id == "test_entity"
        assert entity.entity_type == "concept"
        assert entity.name == "Test Entity"
        assert entity.properties["domain"] == "test"
        assert entity.relationships == ["rel1", "rel2"]
        assert entity.confidence == 0.8
        assert isinstance(entity.timestamp, datetime)


class TestContextRelationship:
    """Test cases for ContextRelationship class."""
    
    def test_context_relationship_creation(self):
        """Test ContextRelationship creation and properties."""
        relationship = ContextRelationship(
            relationship_id="test_rel",
            source_entity="entity1",
            target_entity="entity2",
            relationship_type="related",
            properties={"confidence": 0.7},
            confidence=0.7,
            timestamp=datetime.now()
        )
        
        assert relationship.relationship_id == "test_rel"
        assert relationship.source_entity == "entity1"
        assert relationship.target_entity == "entity2"
        assert relationship.relationship_type == "related"
        assert relationship.properties["confidence"] == 0.7
        assert relationship.confidence == 0.7
        assert isinstance(relationship.timestamp, datetime)


class TestContextConfig:
    """Test cases for ContextConfig."""
    
    def test_context_config_defaults(self):
        """Test ContextConfig default values."""
        config = ContextConfig()
        
        assert config.max_context_depth == 5
        assert config.confidence_threshold == 0.6
        assert config.enable_temporal_analysis is True
        assert config.enable_semantic_analysis is True
        assert config.enable_relationship_mapping is True
        assert config.context_timeout == 30
    
    def test_context_config_custom_values(self):
        """Test ContextConfig with custom values."""
        config = ContextConfig(
            max_context_depth=3,
            confidence_threshold=0.8,
            enable_temporal_analysis=False,
            enable_semantic_analysis=False,
            enable_relationship_mapping=False,
            context_timeout=15
        )
        
        assert config.max_context_depth == 3
        assert config.confidence_threshold == 0.8
        assert config.enable_temporal_analysis is False
        assert config.enable_semantic_analysis is False
        assert config.enable_relationship_mapping is False
        assert config.context_timeout == 15 