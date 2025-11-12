"""
Reasoning engine for logical inference and knowledge deduction
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime
import networkx as nx
from loguru import logger


class ReasoningEngine:
    """Reasoning engine for logical inference and knowledge deduction"""
    
    def __init__(self, knowledge_graph):
        self.knowledge_graph = knowledge_graph
        self.reasoning_rules = []
        self.inference_cache = {}
        
    def add_rule(self, rule: Dict[str, Any]) -> None:
        """Add a reasoning rule"""
        
        rule_data = {
            "id": rule.get("id", f"rule_{datetime.now().timestamp()}"),
            "name": rule.get("name", ""),
            "premises": rule.get("premises", []),
            "conclusion": rule.get("conclusion", ""),
            "confidence": rule.get("confidence", 1.0),
            "type": rule.get("type", "forward")
        }
        
        self.reasoning_rules.append(rule_data)
        logger.info(f"Added reasoning rule: {rule_data['name']}")
        
    def infer(self, query: str, max_depth: int = 3) -> List[Dict[str, Any]]:
        """Perform inference to answer queries"""
        
        # Check cache first
        cache_key = f"{query}_{max_depth}"
        if cache_key in self.inference_cache:
            return self.inference_cache[cache_key]
            
        results = []
        
        # Direct knowledge lookup
        direct_results = self.knowledge_graph.query(query)
        results.extend(direct_results)
        
        # Rule-based inference
        rule_results = self._apply_rules(query)
        results.extend(rule_results)
        
        # Graph-based reasoning
        graph_results = self._graph_reasoning(query, max_depth)
        results.extend(graph_results)
        
        # Remove duplicates and sort by relevance
        unique_results = []
        seen_ids = set()
        
        for result in results:
            result_id = result.get("id", str(result))
            if result_id not in seen_ids:
                unique_results.append(result)
                seen_ids.add(result_id)
                
        unique_results.sort(key=lambda x: x.get("relevance", 0), reverse=True)
        
        # Cache results
        self.inference_cache[cache_key] = unique_results[:10]
        
        return unique_results[:10]
        
    def _apply_rules(self, query: str) -> List[Dict[str, Any]]:
        """Apply reasoning rules to generate inferences"""
        
        results = []
        query_lower = query.lower()
        
        for rule in self.reasoning_rules:
            # Check if rule premises match query
            premises_match = any(
                premise.lower() in query_lower 
                for premise in rule["premises"]
            )
            
            if premises_match:
                inference = {
                    "id": f"inference_{rule['id']}",
                    "type": "inference",
                    "content": rule["conclusion"],
                    "rule_applied": rule["name"],
                    "confidence": rule["confidence"],
                    "relevance": 0.7,
                    "reasoning_type": "rule_based"
                }
                results.append(inference)
                
        return results
        
    def _graph_reasoning(self, query: str, max_depth: int) -> List[Dict[str, Any]]:
        """Perform reasoning using the knowledge graph structure"""
        
        results = []
        query_lower = query.lower()
        
        # Find entities related to query
        query_results = self.knowledge_graph.query(query_lower)
        
        for entity_result in query_results:
            if entity_result.get("type") == "entity":
                entity_id = entity_result.get("id")
                
                # Find related entities through graph traversal
                related_entities = self.knowledge_graph.find_related_entities(
                    entity_id, max_depth=max_depth
                )
                
                for related in related_entities:
                    # Generate inference about relationship
                    inference = {
                        "id": f"graph_inference_{entity_id}_{related['id']}",
                        "type": "graph_inference",
                        "content": f"{entity_result.get('name', 'Entity')} is related to {related.get('name', 'Related entity')}",
                        "source_entity": entity_result.get("name"),
                        "target_entity": related.get("name"),
                        "relationship_strength": related.get("relationship_strength", 0),
                        "relationship_distance": related.get("relationship_distance", 0),
                        "confidence": related.get("relationship_strength", 0),
                        "relevance": related.get("relationship_strength", 0) * 0.8,
                        "reasoning_type": "graph_based"
                    }
                    results.append(inference)
                    
        return results
        
    def explain_reasoning(self, inference_id: str) -> Dict[str, Any]:
        """Explain the reasoning process for an inference"""
        
        # Find the inference in recent results
        for cached_results in self.inference_cache.values():
            for result in cached_results:
                if result.get("id") == inference_id:
                    explanation = {
                        "inference": result,
                        "explanation": self._generate_explanation(result),
                        "confidence_factors": self._analyze_confidence_factors(result)
                    }
                    return explanation
                    
        return {"error": "Inference not found"}
        
    def _generate_explanation(self, inference: Dict[str, Any]) -> str:
        """Generate explanation for an inference"""
        
        reasoning_type = inference.get("reasoning_type", "unknown")
        
        if reasoning_type == "rule_based":
            rule_name = inference.get("rule_applied", "unknown rule")
            return f"This conclusion was derived using the reasoning rule: {rule_name}"
            
        elif reasoning_type == "graph_based":
            source = inference.get("source_entity", "unknown entity")
            target = inference.get("target_entity", "unknown entity")
            strength = inference.get("relationship_strength", 0)
            return f"This inference is based on the relationship between {source} and {target} (strength: {strength:.2f})"
            
        else:
            return "This inference was generated through logical reasoning."
            
    def _analyze_confidence_factors(self, inference: Dict[str, Any]) -> List[str]:
        """Analyze factors contributing to inference confidence"""
        
        factors = []
        confidence = inference.get("confidence", 0)
        
        if confidence > 0.8:
            factors.append("High confidence based on strong evidence")
        elif confidence > 0.6:
            factors.append("Moderate confidence based on available evidence")
        else:
            factors.append("Lower confidence due to limited evidence")
            
        reasoning_type = inference.get("reasoning_type", "")
        if reasoning_type == "rule_based":
            factors.append("Based on established reasoning rules")
        elif reasoning_type == "graph_based":
            factors.append("Based on knowledge graph relationships")
            
        return factors
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get reasoning engine statistics"""
        
        return {
            "total_rules": len(self.reasoning_rules),
            "cached_inferences": len(self.inference_cache),
            "rule_types": {
                rule_type: len([r for r in self.reasoning_rules if r.get("type") == rule_type])
                for rule_type in set(r.get("type", "unknown") for r in self.reasoning_rules)
            }
        }
