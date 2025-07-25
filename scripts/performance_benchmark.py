#!/usr/bin/env python3
"""
Performance Benchmarking Script for MCP RAG Server AI Features

This script measures the performance of the newly implemented AI features
including reasoning engine, context service, and memory operations.
"""

import asyncio
import time
import statistics
import psutil
import os
import sys
from datetime import datetime
from typing import Dict, List, Any
import json

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp_rag_server.services.reasoning_service import AdvancedReasoningEngine, ReasoningConfig
from mcp_rag_server.services.context_service import EnhancedContextService, ContextConfig
from mcp_rag_server.tools.ai_tools import AdvancedAITools


class PerformanceBenchmark:
    """Performance benchmarking for AI features."""
    
    def __init__(self):
        """Initialize the benchmark with AI services."""
        self.reasoning_config = ReasoningConfig(
            max_reasoning_steps=5,
            confidence_threshold=0.7,
            max_planning_depth=5,
            enable_abductive=True,
            enable_planning=True,
            reasoning_timeout=30
        )
        
        self.context_config = ContextConfig(
            max_context_depth=5,
            confidence_threshold=0.6,
            enable_temporal_analysis=True,
            enable_semantic_analysis=True,
            enable_relationship_mapping=True,
            context_timeout=30
        )
        
        self.reasoning_engine = AdvancedReasoningEngine(self.reasoning_config)
        self.context_service = EnhancedContextService(self.context_config)
        self.ai_tools = AdvancedAITools(self.reasoning_engine, self.context_service)
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "system_info": self._get_system_info(),
            "benchmarks": {}
        }
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information for benchmarking context."""
        return {
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "python_version": sys.version,
            "platform": sys.platform
        }
    
    async def benchmark_reasoning_engine(self) -> Dict[str, Any]:
        """Benchmark the reasoning engine performance."""
        print("🔍 Benchmarking Reasoning Engine...")
        
        test_queries = [
            {
                "query": "If all mammals have lungs and dogs are mammals, what can we conclude?",
                "context": {"facts": ["All mammals have lungs", "Dogs are mammals"]},
                "type": "deductive"
            },
            {
                "query": "Based on the patterns, what can we generalize about mammals?",
                "context": {"observations": ["Dogs breathe with lungs", "Cats breathe with lungs", "Horses breathe with lungs"]},
                "type": "inductive"
            },
            {
                "query": "The patient has a fever and cough. What could be the cause?",
                "context": {"symptoms": ["fever", "cough"], "medical_history": "healthy adult"},
                "type": "abductive"
            },
            {
                "query": "How to plan a study of mammal breathing patterns?",
                "context": {"goal": "study mammal breathing", "resources": ["lab equipment", "animals"]},
                "type": "planning"
            }
        ]
        
        results = {
            "total_queries": len(test_queries),
            "response_times": [],
            "success_rate": 0,
            "error_count": 0,
            "memory_usage": [],
            "cpu_usage": []
        }
        
        for i, test_case in enumerate(test_queries):
            print(f"  Testing {test_case['type']} reasoning ({i+1}/{len(test_queries)})...")
            
            # Measure memory and CPU before
            process = psutil.Process()
            memory_before = process.memory_info().rss
            cpu_before = process.cpu_percent()
            
            start_time = time.time()
            
            try:
                result = await self.reasoning_engine.reason(
                    test_case["query"],
                    test_case["context"]
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                
                # Measure memory and CPU after
                memory_after = process.memory_info().rss
                cpu_after = process.cpu_percent()
                
                results["response_times"].append(response_time)
                results["memory_usage"].append(memory_after - memory_before)
                results["cpu_usage"].append(cpu_after - cpu_before)
                
                if result.get("success", False):
                    results["success_rate"] += 1
                else:
                    results["error_count"] += 1
                    
            except Exception as e:
                end_time = time.time()
                response_time = end_time - start_time
                results["response_times"].append(response_time)
                results["error_count"] += 1
                print(f"    Error: {e}")
        
        # Calculate statistics
        if results["response_times"]:
            results["avg_response_time"] = statistics.mean(results["response_times"])
            results["min_response_time"] = min(results["response_times"])
            results["max_response_time"] = max(results["response_times"])
            results["median_response_time"] = statistics.median(results["response_times"])
        
        if results["memory_usage"]:
            results["avg_memory_usage"] = statistics.mean(results["memory_usage"])
            results["total_memory_usage"] = sum(results["memory_usage"])
        
        if results["cpu_usage"]:
            results["avg_cpu_usage"] = statistics.mean(results["cpu_usage"])
        
        results["success_rate"] = (results["success_rate"] / len(test_queries)) * 100
        
        print(f"  ✅ Reasoning Engine Benchmark Complete")
        print(f"    Average Response Time: {results.get('avg_response_time', 0):.3f}s")
        print(f"    Success Rate: {results['success_rate']:.1f}%")
        
        return results
    
    async def benchmark_context_service(self) -> Dict[str, Any]:
        """Benchmark the context service performance."""
        print("🔍 Benchmarking Context Service...")
        
        test_cases = [
            {
                "query": "What are the key entities in machine learning research?",
                "context": {
                    "domain": "machine learning",
                    "entities": ["neural networks", "deep learning", "algorithms"],
                    "relationships": [{"from": "neural networks", "to": "deep learning", "type": "subclass"}]
                }
            },
            {
                "query": "Analyze the temporal context of AI development",
                "context": {
                    "timeline": ["1950s: AI beginnings", "2010s: Deep learning", "2020s: Large language models"],
                    "current_year": 2025
                }
            },
            {
                "query": "What are the semantic relationships between programming languages?",
                "context": {
                    "languages": ["Python", "JavaScript", "Java", "C++"],
                    "paradigms": ["object-oriented", "functional", "procedural"]
                }
            }
        ]
        
        results = {
            "total_queries": len(test_cases),
            "response_times": [],
            "success_rate": 0,
            "error_count": 0,
            "memory_usage": [],
            "cpu_usage": []
        }
        
        for i, test_case in enumerate(test_cases):
            print(f"  Testing context analysis ({i+1}/{len(test_cases)})...")
            
            process = psutil.Process()
            memory_before = process.memory_info().rss
            cpu_before = process.cpu_percent()
            
            start_time = time.time()
            
            try:
                result = await self.context_service.analyze_context(
                    test_case["query"],
                    "test_user",
                    test_case["context"]
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                
                memory_after = process.memory_info().rss
                cpu_after = process.cpu_percent()
                
                results["response_times"].append(response_time)
                results["memory_usage"].append(memory_after - memory_before)
                results["cpu_usage"].append(cpu_after - cpu_before)
                
                if result.get("success", False):
                    results["success_rate"] += 1
                else:
                    results["error_count"] += 1
                    
            except Exception as e:
                end_time = time.time()
                response_time = end_time - start_time
                results["response_times"].append(response_time)
                results["error_count"] += 1
                print(f"    Error: {e}")
        
        # Calculate statistics
        if results["response_times"]:
            results["avg_response_time"] = statistics.mean(results["response_times"])
            results["min_response_time"] = min(results["response_times"])
            results["max_response_time"] = max(results["response_times"])
            results["median_response_time"] = statistics.median(results["response_times"])
        
        if results["memory_usage"]:
            results["avg_memory_usage"] = statistics.mean(results["memory_usage"])
            results["total_memory_usage"] = sum(results["memory_usage"])
        
        if results["cpu_usage"]:
            results["avg_cpu_usage"] = statistics.mean(results["cpu_usage"])
        
        results["success_rate"] = (results["success_rate"] / len(test_cases)) * 100
        
        print(f"  ✅ Context Service Benchmark Complete")
        print(f"    Average Response Time: {results.get('avg_response_time', 0):.3f}s")
        print(f"    Success Rate: {results['success_rate']:.1f}%")
        
        return results
    
    async def benchmark_ai_tools(self) -> Dict[str, Any]:
        """Benchmark the AI tools integration performance."""
        print("🔍 Benchmarking AI Tools Integration...")
        
        test_cases = [
            {
                "method": "advanced_reasoning",
                "args": {
                    "query": "If all mammals have lungs and dogs are mammals, what can we conclude?",
                    "context": {"facts": ["All mammals have lungs", "Dogs are mammals"]}
                }
            },
            {
                "method": "analyze_context",
                "args": {
                    "query": "What are the key entities in machine learning?",
                    "additional_context": {"domain": "machine learning", "entities": ["neural networks", "algorithms"]}
                }
            },
            {
                "method": "contextual_question_answering",
                "args": {
                    "question": "What is the relationship between AI and machine learning?",
                    "context": {"domain": "artificial intelligence"}
                }
            }
        ]
        
        results = {
            "total_queries": len(test_cases),
            "response_times": [],
            "success_rate": 0,
            "error_count": 0,
            "memory_usage": [],
            "cpu_usage": []
        }
        
        for i, test_case in enumerate(test_cases):
            print(f"  Testing {test_case['method']} ({i+1}/{len(test_cases)})...")
            
            process = psutil.Process()
            memory_before = process.memory_info().rss
            cpu_before = process.cpu_percent()
            
            start_time = time.time()
            
            try:
                method = getattr(self.ai_tools, test_case["method"])
                result = await method(**test_case["args"])
                
                end_time = time.time()
                response_time = end_time - start_time
                
                memory_after = process.memory_info().rss
                cpu_after = process.cpu_percent()
                
                results["response_times"].append(response_time)
                results["memory_usage"].append(memory_after - memory_before)
                results["cpu_usage"].append(cpu_after - cpu_before)
                
                if result.get("success", False):
                    results["success_rate"] += 1
                else:
                    results["error_count"] += 1
                    
            except Exception as e:
                end_time = time.time()
                response_time = end_time - start_time
                results["response_times"].append(response_time)
                results["error_count"] += 1
                print(f"    Error: {e}")
        
        # Calculate statistics
        if results["response_times"]:
            results["avg_response_time"] = statistics.mean(results["response_times"])
            results["min_response_time"] = min(results["response_times"])
            results["max_response_time"] = max(results["response_times"])
            results["median_response_time"] = statistics.median(results["response_times"])
        
        if results["memory_usage"]:
            results["avg_memory_usage"] = statistics.mean(results["memory_usage"])
            results["total_memory_usage"] = sum(results["memory_usage"])
        
        if results["cpu_usage"]:
            results["avg_cpu_usage"] = statistics.mean(results["cpu_usage"])
        
        results["success_rate"] = (results["success_rate"] / len(test_cases)) * 100
        
        print(f"  ✅ AI Tools Integration Benchmark Complete")
        print(f"    Average Response Time: {results.get('avg_response_time', 0):.3f}s")
        print(f"    Success Rate: {results['success_rate']:.1f}%")
        
        return results
    
    async def run_concurrent_benchmark(self) -> Dict[str, Any]:
        """Run concurrent operations benchmark."""
        print("🔍 Benchmarking Concurrent Operations...")
        
        async def single_operation():
            """Single concurrent operation."""
            try:
                result = await self.reasoning_engine.reason(
                    "If A implies B and B implies C, what can we conclude?",
                    {"premises": ["A implies B", "B implies C"]}
                )
                return result.get("success", False)
            except:
                return False
        
        # Test different concurrency levels
        concurrency_levels = [1, 2, 5, 10]
        results = {
            "concurrency_levels": concurrency_levels,
            "response_times": {},
            "success_rates": {},
            "throughput": {}
        }
        
        for level in concurrency_levels:
            print(f"  Testing {level} concurrent operations...")
            
            start_time = time.time()
            tasks = [single_operation() for _ in range(level)]
            results_list = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            total_time = end_time - start_time
            success_count = sum(1 for r in results_list if r is True)
            
            results["response_times"][level] = total_time / level
            results["success_rates"][level] = (success_count / level) * 100
            results["throughput"][level] = level / total_time
        
        print(f"  ✅ Concurrent Operations Benchmark Complete")
        return results
    
    async def run_full_benchmark(self) -> Dict[str, Any]:
        """Run the complete performance benchmark."""
        print("🚀 Starting Performance Benchmark...")
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"System: {self.results['system_info']['cpu_count']} CPUs, {self.results['system_info']['memory_total'] / (1024**3):.1f}GB RAM")
        print()
        
        # Run individual benchmarks
        self.results["benchmarks"]["reasoning_engine"] = await self.benchmark_reasoning_engine()
        print()
        
        self.results["benchmarks"]["context_service"] = await self.benchmark_context_service()
        print()
        
        self.results["benchmarks"]["ai_tools"] = await self.benchmark_ai_tools()
        print()
        
        self.results["benchmarks"]["concurrent_operations"] = await self.run_concurrent_benchmark()
        print()
        
        # Calculate overall statistics
        self._calculate_overall_statistics()
        
        # Save results
        self._save_results()
        
        # Print summary
        self._print_summary()
        
        return self.results
    
    def _calculate_overall_statistics(self):
        """Calculate overall performance statistics."""
        benchmarks = self.results["benchmarks"]
        
        # Overall response times
        all_response_times = []
        for benchmark_name, benchmark_data in benchmarks.items():
            if benchmark_name != "concurrent_operations":
                all_response_times.extend(benchmark_data.get("response_times", []))
        
        if all_response_times:
            self.results["overall"] = {
                "avg_response_time": statistics.mean(all_response_times),
                "min_response_time": min(all_response_times),
                "max_response_time": max(all_response_times),
                "median_response_time": statistics.median(all_response_times),
                "total_operations": len(all_response_times)
            }
    
    def _save_results(self):
        """Save benchmark results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"benchmark_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"📊 Results saved to: {filename}")
    
    def _print_summary(self):
        """Print benchmark summary."""
        print("📊 PERFORMANCE BENCHMARK SUMMARY")
        print("=" * 50)
        
        if "overall" in self.results:
            overall = self.results["overall"]
            print(f"Overall Average Response Time: {overall['avg_response_time']:.3f}s")
            print(f"Overall Median Response Time: {overall['median_response_time']:.3f}s")
            print(f"Overall Min/Max Response Time: {overall['min_response_time']:.3f}s / {overall['max_response_time']:.3f}s")
            print(f"Total Operations Tested: {overall['total_operations']}")
        
        print()
        print("Component Performance:")
        for name, data in self.results["benchmarks"].items():
            if name != "concurrent_operations":
                avg_time = data.get("avg_response_time", 0)
                success_rate = data.get("success_rate", 0)
                print(f"  {name.replace('_', ' ').title()}: {avg_time:.3f}s ({success_rate:.1f}% success)")
        
        print()
        print("Concurrent Performance:")
        concurrent = self.results["benchmarks"]["concurrent_operations"]
        for level in concurrent["concurrency_levels"]:
            avg_time = concurrent["response_times"][level]
            throughput = concurrent["throughput"][level]
            print(f"  {level} concurrent: {avg_time:.3f}s per op ({throughput:.1f} ops/sec)")


async def main():
    """Main benchmark execution."""
    benchmark = PerformanceBenchmark()
    await benchmark.run_full_benchmark()


if __name__ == "__main__":
    asyncio.run(main()) 