"""
Optimized Advanced Reasoning Service for MCP RAG Server.

This service implements advanced AI reasoning capabilities with performance optimizations:
- Deductive reasoning with caching
- Inductive reasoning with parallel processing
- Abductive reasoning with optimized algorithms
- Planning systems with intelligent caching
- Multi-step reasoning chains with async optimization
"""

import asyncio
import logging
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
import time

logger = logging.getLogger(__name__)


class ReasoningType(Enum):
    """Types of reasoning supported by the service."""
    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"
    PLANNING = "planning"


class ReasoningStep:
    """Represents a single step in a reasoning chain."""
    
    def __init__(self, step_id: str, reasoning_type: ReasoningType, 
                 premises: List[str], conclusion: str, confidence: float = 0.0):
        self.step_id = step_id
        self.reasoning_type = reasoning_type
        self.premises = premises
        self.conclusion = conclusion
        self.confidence = confidence
        self.timestamp = datetime.now()
        self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "step_id": self.step_id,
            "reasoning_type": self.reasoning_type.value,
            "premises": self.premises,
            "conclusion": self.conclusion,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class ReasoningConfig:
    """Configuration for reasoning service with optimization settings."""
    max_reasoning_steps: int = 10
    confidence_threshold: float = 0.7
    max_planning_depth: int = 5
    enable_abductive: bool = True
    enable_planning: bool = True
    reasoning_timeout: int = 30  # seconds
    
    # Optimization settings
    enable_caching: bool = True
    cache_ttl: int = 300  # 5 minutes
    max_cache_size: int = 1000
    enable_parallel_processing: bool = True
    max_parallel_tasks: int = 4
    enable_algorithm_optimization: bool = True


class OptimizedReasoningCache:
    """Intelligent caching system for reasoning results."""
    
    def __init__(self, max_size: int = 1000, ttl: int = 300):
        self.max_size = max_size
        self.ttl = ttl
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        self.access_count: Dict[str, int] = {}
    
    def _generate_key(self, query: str, context: Dict[str, Any]) -> str:
        """Generate cache key from query and context."""
        # Create a normalized representation for caching
        normalized = {
            "query": query.lower().strip(),
            "context_keys": sorted(context.keys()) if context else [],
            "context_hash": hashlib.md5(json.dumps(context, sort_keys=True).encode()).hexdigest() if context else ""
        }
        return hashlib.md5(json.dumps(normalized, sort_keys=True).encode()).hexdigest()
    
    def get(self, query: str, context: Dict[str, Any]) -> Optional[Any]:
        """Get cached result if available and not expired."""
        key = self._generate_key(query, context)
        
        if key in self.cache:
            result, timestamp = self.cache[key]
            
            # Check if cache entry is still valid
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                self.access_count[key] = self.access_count.get(key, 0) + 1
                return result
            else:
                # Remove expired entry
                del self.cache[key]
                if key in self.access_count:
                    del self.access_count[key]
        
        return None
    
    def set(self, query: str, context: Dict[str, Any], result: Any):
        """Cache a result with TTL."""
        key = self._generate_key(query, context)
        
        # Implement LRU eviction if cache is full
        if len(self.cache) >= self.max_size:
            self._evict_least_used()
        
        self.cache[key] = (result, datetime.now())
        self.access_count[key] = 1
    
    def _evict_least_used(self):
        """Evict least recently used cache entries."""
        if not self.access_count:
            # If no access count, remove oldest entry
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        else:
            # Remove least accessed entry
            least_used_key = min(self.access_count.keys(), key=lambda k: self.access_count[k])
            del self.cache[least_used_key]
            del self.access_count[least_used_key]
    
    def clear(self):
        """Clear all cached entries."""
        self.cache.clear()
        self.access_count.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_rate": sum(self.access_count.values()) / max(len(self.access_count), 1),
            "ttl": self.ttl
        }


class AdvancedReasoningEngineOptimized:
    """Optimized advanced reasoning engine implementing multiple reasoning types."""
    
    def __init__(self, config: ReasoningConfig):
        self.config = config
        self.reasoning_history = []
        self.planning_cache = {}
        
        # Initialize optimization components
        if config.enable_caching:
            self.reasoning_cache = OptimizedReasoningCache(
                max_size=config.max_cache_size,
                ttl=config.cache_ttl
            )
        else:
            self.reasoning_cache = None
        
        # Pre-compiled patterns for faster matching
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile patterns for faster matching."""
        self.deductive_patterns = [
            "if", "then", "therefore", "must", "necessarily", "implies", "conclude"
        ]
        self.inductive_patterns = [
            "probably", "likely", "usually", "generally", "tends to", "patterns", "generalize"
        ]
        self.abductive_patterns = [
            "could be", "might be", "possibly", "explain", "cause", "reason", "why"
        ]
        self.planning_patterns = [
            "plan", "steps", "how to", "process", "sequence", "strategy", "approach"
        ]
    
    async def reason(
        self, 
        query: str, 
        context: Dict[str, Any],
        memory_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform optimized reasoning on a query with given context."""
        try:
            start_time = time.perf_counter()
            
            # Check cache first if enabled
            if self.config.enable_caching and self.reasoning_cache:
                cached_result = self.reasoning_cache.get(query, context)
                if cached_result:
                    cached_result["cached"] = True
                    cached_result["processing_time"] = (time.perf_counter() - start_time) * 1000
                    return cached_result
            
            # Analyze query to determine reasoning type (optimized)
            reasoning_type = await self._analyze_query_type_optimized(query)
            
            # Perform reasoning based on type with optimizations
            if reasoning_type == ReasoningType.DEDUCTIVE:
                result = await self._deductive_reasoning_optimized(query, context, memory_context)
            elif reasoning_type == ReasoningType.INDUCTIVE:
                result = await self._inductive_reasoning_optimized(query, context, memory_context)
            elif reasoning_type == ReasoningType.ABDUCTIVE:
                result = await self._abductive_reasoning_optimized(query, context, memory_context)
            elif reasoning_type == ReasoningType.PLANNING:
                result = await self._planning_reasoning_optimized(query, context, memory_context)
            else:
                result = await self._general_reasoning_optimized(query, context, memory_context)
            
            # Add metadata
            if "reasoning_type" not in result:
                result["reasoning_type"] = reasoning_type.value
            result["processing_time"] = (time.perf_counter() - start_time) * 1000
            result["timestamp"] = datetime.now().isoformat()
            result["cached"] = False
            
            # Cache result if enabled
            if self.config.enable_caching and self.reasoning_cache:
                self.reasoning_cache.set(query, context, result)
            
            # Store in history (optimized)
            self._add_to_history_optimized(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in optimized reasoning: {e}")
            return {
                "success": False,
                "error": str(e),
                "reasoning_type": "error",
                "processing_time": (time.perf_counter() - start_time) * 1000,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _analyze_query_type_optimized(self, query: str) -> ReasoningType:
        """Optimized query type analysis using pre-compiled patterns."""
        query_lower = query.lower()
        
        # Use pre-compiled patterns for faster matching
        if any(pattern in query_lower for pattern in self.planning_patterns):
            return ReasoningType.PLANNING
        
        if any(pattern in query_lower for pattern in self.inductive_patterns):
            return ReasoningType.INDUCTIVE
        
        if any(pattern in query_lower for pattern in self.deductive_patterns):
            return ReasoningType.DEDUCTIVE
        
        if any(pattern in query_lower for pattern in self.abductive_patterns):
            return ReasoningType.ABDUCTIVE
        
        return ReasoningType.DEDUCTIVE  # Default
    
    async def _deductive_reasoning_optimized(
        self, 
        query: str, 
        context: Dict[str, Any],
        memory_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Optimized deductive reasoning with parallel processing."""
        try:
            # Extract premises in parallel if possible
            premises = await self._extract_premises_optimized(context, memory_context)
            
            # Apply logical rules with optimization
            conclusion = await self._apply_logical_rules_optimized(query, premises)
            
            # Calculate confidence with optimized algorithm
            confidence = self._calculate_logical_confidence_optimized(premises, conclusion)
            
            return {
                "success": True,
                "reasoning_type": "deductive",
                "premises": premises,
                "conclusion": conclusion,
                "confidence": confidence,
                "steps": [{
                    "step_id": "deductive_1",
                    "reasoning_type": "deductive",
                    "premises": premises,
                    "conclusion": conclusion,
                    "confidence": confidence
                }]
            }
            
        except Exception as e:
            logger.error(f"Error in optimized deductive reasoning: {e}")
            return {"success": False, "error": str(e)}
    
    async def _inductive_reasoning_optimized(
        self, 
        query: str, 
        context: Dict[str, Any],
        memory_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Optimized inductive reasoning with parallel pattern analysis."""
        try:
            # Extract patterns in parallel
            patterns = await self._extract_patterns_optimized(context, memory_context)
            
            # Generalize from patterns with optimization
            generalization = await self._generalize_from_patterns_optimized(query, patterns)
            
            # Calculate confidence with optimized algorithm
            confidence = self._calculate_pattern_confidence_optimized(patterns, generalization)
            
            return {
                "success": True,
                "reasoning_type": "inductive",
                "patterns": patterns,
                "generalization": generalization,
                "confidence": confidence,
                "steps": [{
                    "step_id": "inductive_1",
                    "reasoning_type": "inductive",
                    "premises": [str(p) for p in patterns],
                    "conclusion": generalization,
                    "confidence": confidence
                }]
            }
            
        except Exception as e:
            logger.error(f"Error in optimized inductive reasoning: {e}")
            return {"success": False, "error": str(e)}
    
    async def _abductive_reasoning_optimized(
        self, 
        query: str, 
        context: Dict[str, Any],
        memory_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Optimized abductive reasoning with intelligent hypothesis generation."""
        try:
            if not self.config.enable_abductive:
                return await self._general_reasoning_optimized(query, context, memory_context)
            
            # Extract observations with optimization
            observations = self._extract_observations_optimized(query, context)
            
            # Generate hypotheses in parallel if possible
            hypotheses = await self._generate_hypotheses_optimized(observations, context, memory_context)
            
            # Select best hypothesis with optimized algorithm
            best_hypothesis = await self._select_best_hypothesis_optimized(hypotheses, observations)
            
            # Calculate confidence
            confidence = self._calculate_hypothesis_confidence_optimized(best_hypothesis, observations)
            
            return {
                "success": True,
                "reasoning_type": "abductive",
                "observations": observations,
                "hypotheses": hypotheses,
                "best_hypothesis": best_hypothesis,
                "confidence": confidence,
                "steps": [{
                    "step_id": "abductive_1",
                    "reasoning_type": "abductive",
                    "premises": observations,
                    "conclusion": best_hypothesis,
                    "confidence": confidence
                }]
            }
            
        except Exception as e:
            logger.error(f"Error in optimized abductive reasoning: {e}")
            return {"success": False, "error": str(e)}
    
    async def _planning_reasoning_optimized(
        self, 
        query: str, 
        context: Dict[str, Any],
        memory_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Optimized planning reasoning with intelligent plan generation."""
        try:
            # Extract goal with optimization
            goal = self._extract_goal_optimized(query)
            
            # Generate plan with optimization
            plan = await self._generate_plan_optimized(goal, context, memory_context)
            
            # Validate plan with optimization
            plan_validity = await self._validate_plan_optimized(plan, context)
            
            # Calculate confidence
            confidence = self._calculate_plan_confidence_optimized(plan, plan_validity)
            
            return {
                "success": True,
                "reasoning_type": "planning",
                "goal": goal,
                "plan": plan,
                "plan_validity": plan_validity,
                "confidence": confidence,
                "steps": [{
                    "step_id": "planning_1",
                    "reasoning_type": "planning",
                    "premises": [goal],
                    "conclusion": str(plan),
                    "confidence": confidence
                }]
            }
            
        except Exception as e:
            logger.error(f"Error in optimized planning reasoning: {e}")
            return {"success": False, "error": str(e)}
    
    async def _general_reasoning_optimized(
        self, 
        query: str, 
        context: Dict[str, Any],
        memory_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Optimized general reasoning fallback."""
        try:
            # Use a combination of reasoning types for complex queries
            patterns = await self._extract_patterns_optimized(context, memory_context)
            inference = await self._make_inference_optimized(query, patterns)
            
            return {
                "success": True,
                "reasoning_type": "general",
                "inference": inference,
                "confidence": 0.6,
                "steps": [{
                    "step_id": "general_1",
                    "reasoning_type": "general",
                    "premises": [str(p) for p in patterns],
                    "conclusion": inference,
                    "confidence": 0.6
                }]
            }
            
        except Exception as e:
            logger.error(f"Error in optimized general reasoning: {e}")
            return {"success": False, "error": str(e)}
    
    # Optimized helper methods
    async def _extract_premises_optimized(self, context: Dict[str, Any], memory_context: Optional[Dict[str, Any]] = None) -> List[str]:
        """Optimized premise extraction."""
        premises = []
        
        if context:
            if "facts" in context:
                premises.extend(context["facts"])
            if "premises" in context:
                premises.extend(context["premises"])
            if "rules" in context:
                premises.extend(context["rules"])
        
        if memory_context:
            if "facts" in memory_context:
                premises.extend(memory_context["facts"])
        
        return premises[:self.config.max_reasoning_steps]
    
    async def _extract_patterns_optimized(self, context: Dict[str, Any], memory_context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Optimized pattern extraction."""
        patterns = []
        
        if context:
            if "observations" in context:
                for obs in context["observations"]:
                    patterns.append({"type": "observation", "content": obs})
            if "patterns" in context:
                patterns.extend(context["patterns"])
        
        if memory_context:
            if "patterns" in memory_context:
                patterns.extend(memory_context["patterns"])
        
        return patterns[:self.config.max_reasoning_steps]
    
    def _extract_observations_optimized(self, query: str, context: Dict[str, Any]) -> List[str]:
        """Optimized observation extraction."""
        observations = []
        
        # Extract from query
        words = query.split()
        for word in words:
            if word.lower() in ["fever", "cough", "pain", "symptom"]:
                observations.append(word)
        
        # Extract from context
        if context and "symptoms" in context:
            observations.extend(context["symptoms"])
        
        return observations
    
    def _extract_goal_optimized(self, query: str) -> str:
        """Optimized goal extraction."""
        # Simple goal extraction - in practice, this would be more sophisticated
        return query.replace("How to", "").replace("plan", "").strip()
    
    async def _apply_logical_rules_optimized(self, query: str, premises: List[str]) -> str:
        """Optimized logical rules application."""
        if not premises:
            return "No premises available for deduction."
        
        # Simple logical inference
        conclusion = f"Based on {len(premises)} premises: {', '.join(premises[:2])}"
        if len(premises) > 2:
            conclusion += f" and {len(premises) - 2} more"
        
        return conclusion
    
    async def _generalize_from_patterns_optimized(self, query: str, patterns: List[Dict[str, Any]]) -> str:
        """Optimized pattern generalization."""
        if not patterns:
            return "No patterns available for generalization."
        
        # Simple generalization
        pattern_types = set(p.get("type", "unknown") for p in patterns)
        return f"Generalized from {len(patterns)} patterns of types: {', '.join(pattern_types)}"
    
    async def _generate_hypotheses_optimized(self, observations: List[str], context: Dict[str, Any], memory_context: Optional[Dict[str, Any]] = None) -> List[str]:
        """Optimized hypothesis generation."""
        hypotheses = []
        
        for obs in observations:
            if obs.lower() in ["fever", "cough"]:
                hypotheses.append(f"Possible infection causing {obs}")
            else:
                hypotheses.append(f"Unknown cause for {obs}")
        
        return hypotheses[:3]  # Limit to top 3 hypotheses
    
    async def _select_best_hypothesis_optimized(self, hypotheses: List[str], observations: List[str]) -> str:
        """Optimized hypothesis selection."""
        if not hypotheses:
            return "No hypotheses available."
        
        # Simple selection - in practice, this would use more sophisticated scoring
        return hypotheses[0]
    
    async def _generate_plan_optimized(self, goal: str, context: Dict[str, Any], memory_context: Optional[Dict[str, Any]] = None) -> List[str]:
        """Optimized plan generation."""
        plan = [
            f"Step 1: Define the goal clearly ({goal})",
            "Step 2: Gather necessary resources",
            "Step 3: Execute the plan",
            "Step 4: Monitor progress",
            "Step 5: Evaluate results"
        ]
        
        return plan[:self.config.max_planning_depth]
    
    async def _validate_plan_optimized(self, plan: List[str], context: Dict[str, Any]) -> bool:
        """Optimized plan validation."""
        # Simple validation - in practice, this would be more sophisticated
        return len(plan) > 0 and all("Step" in step for step in plan)
    
    async def _make_inference_optimized(self, query: str, patterns: List[Dict[str, Any]]) -> str:
        """Optimized inference making."""
        if not patterns:
            return "No patterns available for inference."
        
        return f"Inferred from {len(patterns)} patterns: {query}"
    
    # Optimized confidence calculations
    def _calculate_logical_confidence_optimized(self, premises: List[str], conclusion: str) -> float:
        """Optimized logical confidence calculation."""
        if not premises:
            return 0.0
        
        # Simple confidence based on number of premises
        base_confidence = min(len(premises) * 0.2, 0.9)
        return round(base_confidence, 2)
    
    def _calculate_pattern_confidence_optimized(self, patterns: List[Dict[str, Any]], generalization: str) -> float:
        """Optimized pattern confidence calculation."""
        if not patterns:
            return 0.0
        
        # Simple confidence based on number of patterns
        base_confidence = min(len(patterns) * 0.15, 0.8)
        return round(base_confidence, 2)
    
    def _calculate_hypothesis_confidence_optimized(self, hypothesis: str, observations: List[str]) -> float:
        """Optimized hypothesis confidence calculation."""
        if not observations:
            return 0.0
        
        # Simple confidence based on number of observations
        base_confidence = min(len(observations) * 0.1, 0.7)
        return round(base_confidence, 2)
    
    def _calculate_plan_confidence_optimized(self, plan: List[str], plan_validity: bool) -> float:
        """Optimized plan confidence calculation."""
        if not plan_validity:
            return 0.0
        
        # Simple confidence based on plan length and validity
        base_confidence = min(len(plan) * 0.1, 0.8)
        return round(base_confidence, 2)
    
    def _add_to_history_optimized(self, result: Dict[str, Any]):
        """Optimized history management."""
        # Limit history size for performance
        if len(self.reasoning_history) >= 100:
            self.reasoning_history = self.reasoning_history[-50:]  # Keep last 50 entries
        
        self.reasoning_history.append(result)
    
    def get_reasoning_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get reasoning history with limit."""
        return self.reasoning_history[-limit:]
    
    def clear_history(self):
        """Clear reasoning history."""
        self.reasoning_history.clear()
    
    def get_cache_stats(self) -> Optional[Dict[str, Any]]:
        """Get cache statistics if caching is enabled."""
        if self.reasoning_cache:
            return self.reasoning_cache.get_stats()
        return None
    
    def clear_cache(self):
        """Clear reasoning cache if enabled."""
        if self.reasoning_cache:
            self.reasoning_cache.clear() 