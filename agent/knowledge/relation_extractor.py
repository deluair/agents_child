"""
Relation extraction component for identifying relationships between entities
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger


class RelationExtractor:
    """Relation extractor for identifying relationships between entities"""
    
    def __init__(self):
        # Relation patterns
        self.relation_patterns = {
            # Employment/Organization relations
            "works_for": [
                r'(\w+(?:\s+\w+)*)\s+(?:works for|is employed by|is a\s+\w+\s+at)\s+(\w+(?:\s+\w+)*)',
                r'(\w+(?:\s+\w+)*)\'?s?\s+(?:job|position|role)\s+(?:is|at)?\s+(\w+(?:\s+\w+)*)'
            ],
            "manages": [
                r'(\w+(?:\s+\w+)*)\s+(?:manages|is the manager of|supervises)\s+(\w+(?:\s+\w+)*)',
                r'(\w+(?:\s+\w+)*)\'?s?\s+manager\s+(?:is)?\s+(\w+(?:\s+\w+)*)'
            ],
            
            # Location relations
            "located_in": [
                r'(\w+(?:\s+\w+)*)\s+(?:is located in|is in|can be found in)\s+(\w+(?:\s+\w+)*)',
                r'(\w+(?:\s+\w+)*)\s+(?:headquartered|based)\s+in\s+(\w+(?:\s+\w+)*)'
            ],
            "headquarters_in": [
                r'(\w+(?:\s+\w+)*)\'?s?\s+headquarters\s+(?:is|are)?\s+in\s+(\w+(?:\s+\w+)*)'
            ],
            
            # Ownership relations
            "owns": [
                r'(\w+(?:\s+\w+)*)\s+(?:owns|possesses|has)\s+(\w+(?:\s+\w+)*)',
                r'(\w+(?:\s+\w+)*)\s+(?:is owned by|belongs to)\s+(\w+(?:\s+\w+)*)'
            ],
            "subsidiary_of": [
                r'(\w+(?:\s+\w+)*)\s+(?:is a subsidiary of|is owned by)\s+(\w+(?:\s+\w+)*)'
            ],
            
            # Family/Personal relations
            "parent_of": [
                r'(\w+(?:\s+\w+)*)\s+(?:is the parent of|has a child named|parent of)\s+(\w+(?:\s+\w+)*)'
            ],
            "child_of": [
                r'(\w+(?:\s+\w+)*)\s+(?:is the child of|son of|daughter of)\s+(\w+(?:\s+\w+)*)'
            ],
            "spouse_of": [
                r'(\w+(?:\s+\w+)*)\s+(?:is married to|spouse of|husband of|wife of)\s+(\w+(?:\s+\w+)*)'
            ],
            
            # Creation/Product relations
            "created_by": [
                r'(\w+(?:\s+\w+)*)\s+(?:was created by|was developed by|was made by|was built by)\s+(\w+(?:\s+\w+)*)',
                r'(\w+(?:\s+\w+)*)\s+(?:created|developed|made|built)\s+(\w+(?:\s+\w+)*)'
            ],
            "produces": [
                r'(\w+(?:\s+\w+)*)\s+(?:produces|manufactures|makes)\s+(\w+(?:\s+\w+)*)'
            ],
            
            # Educational relations
            "graduated_from": [
                r'(\w+(?:\s+\w+)*)\s+(?:graduated from|has a degree from)\s+(\w+(?:\s+\w+)*)'
            ],
            "works_at": [
                r'(\w+(?:\s+\w+)*)\s+(?:works at|is a\s+\w+\s+at)\s+(\w+(?:\s+\w+)*)'
            ],
            
            # General relations
            "part_of": [
                r'(\w+(?:\s+\w+)*)\s+(?:is part of|belongs to)\s+(\w+(?:\s+\w+)*)'
            ],
            "example_of": [
                r'(\w+(?:\s+\w+)*)\s+(?:is an example of|is a type of)\s+(\w+(?:\s+\w+)*)'
            ],
            "member_of": [
                r'(\w+(?:\s+\w+)*)\s+(?:is a member of|belongs to)\s+(\w+(?:\s+\w+)*)'
            ]
        }
        
        # Confidence weights for different patterns
        self.pattern_confidence = {
            "works_for": 0.8,
            "manages": 0.7,
            "located_in": 0.8,
            "owns": 0.7,
            "created_by": 0.8,
            "graduated_from": 0.9,
            "part_of": 0.6
        }
        
    def extract_relations(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract relations between entities in text"""
        
        relations = []
        
        # Extract relations using patterns
        for relation_type, patterns in self.relation_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    try:
                        source_text = match.group(1).strip()
                        target_text = match.group(2).strip()
                        
                        # Find corresponding entities
                        source_entity = self._find_best_entity_match(source_text, entities)
                        target_entity = self._find_best_entity_match(target_text, entities)
                        
                        if source_entity and target_entity:
                            # Calculate confidence
                            base_confidence = self.pattern_confidence.get(relation_type, 0.5)
                            confidence = self._calculate_relation_confidence(
                                source_text, target_text, source_entity, target_entity, base_confidence
                            )
                            
                            relation = {
                                "type": relation_type,
                                "source": source_entity,
                                "target": target_entity,
                                "source_text": source_text,
                                "target_text": target_text,
                                "confidence": confidence,
                                "pattern": pattern,
                                "extraction_method": "pattern_based"
                            }
                            relations.append(relation)
                            
                    except IndexError:
                        # Pattern didn't capture expected groups
                        continue
                        
        # Extract relations using co-occurrence and heuristics
        cooccurrence_relations = self._extract_cooccurrence_relations(text, entities)
        relations.extend(cooccurrence_relations)
        
        # Remove duplicates and sort by confidence
        unique_relations = self._remove_duplicate_relations(relations)
        unique_relations.sort(key=lambda x: x["confidence"], reverse=True)
        
        return unique_relations
        
    def _find_best_entity_match(self, text: str, entities: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find the best matching entity for given text"""
        
        text_lower = text.lower()
        best_match = None
        best_score = 0
        
        for entity in entities:
            entity_text = entity["text"].lower()
            
            # Exact match
            if entity_text == text_lower:
                return entity
                
            # Partial match scoring
            if text_lower in entity_text:
                score = len(text_lower) / len(entity_text)
                if score > best_score:
                    best_score = score
                    best_match = entity
                    
            elif entity_text in text_lower:
                score = len(entity_text) / len(text_lower)
                if score > best_score:
                    best_score = score
                    best_match = entity
                    
        # Return best match if score is reasonable
        if best_match and best_score > 0.5:
            return best_match
            
        return None
        
    def _calculate_relation_confidence(self, source_text: str, target_text: str,
                                     source_entity: Dict[str, Any], target_entity: Dict[str, Any],
                                     base_confidence: float) -> float:
        """Calculate confidence score for a relation"""
        
        confidence = base_confidence
        
        # Boost confidence based on text match quality
        source_match_ratio = len(source_text.lower()) / len(source_entity["text"])
        target_match_ratio = len(target_text.lower()) / len(target_entity["text"])
        
        match_quality = (source_match_ratio + target_match_ratio) / 2
        confidence *= match_quality
        
        # Boost confidence based on entity types
        source_type = source_entity.get("type", "")
        target_type = target_entity.get("type", "")
        
        # Certain type combinations are more reliable
        reliable_combinations = [
            ("person", "organization"),
            ("organization", "location"),
            ("person", "location"),
            ("organization", "organization")
        ]
        
        if (source_type, target_type) in reliable_combinations:
            confidence *= 1.2
            
        # Ensure confidence stays within bounds
        return min(1.0, max(0.0, confidence))
        
    def _extract_cooccurrence_relations(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract relations based on entity co-occurrence"""
        
        relations = []
        
        # Find entities that appear close to each other
        window_size = 50  # characters
        
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                distance = abs(entity1["start"] - entity2["start"])
                
                if distance <= window_size:
                    # Determine relation type based on entity types
                    relation_type = self._infer_relation_type(entity1, entity2, text)
                    
                    if relation_type:
                        relation = {
                            "type": relation_type,
                            "source": entity1,
                            "target": entity2,
                            "confidence": 0.4,  # Lower confidence for co-occurrence
                            "distance": distance,
                            "extraction_method": "cooccurrence"
                        }
                        relations.append(relation)
                        
        return relations
        
    def _infer_relation_type(self, entity1: Dict[str, Any], entity2: Dict[str, Any], text: str) -> Optional[str]:
        """Infer relation type based on entity types and context"""
        
        type1 = entity1.get("type", "")
        type2 = entity2.get("type", "")
        text_lower = text.lower()
        
        # Person-Organization relations
        if (type1 == "person" and type2 == "organization") or (type1 == "organization" and type2 == "person"):
            if any(word in text_lower for word in ["work", "job", "employee", "staff"]):
                return "works_for" if type1 == "person" else "employs"
                
        # Organization-Location relations
        if (type1 == "organization" and type2 == "location") or (type1 == "location" and type2 == "organization"):
            if any(word in text_lower for word in ["located", "based", "headquarters"]):
                return "located_in" if type1 == "organization" else "contains"
                
        # Person-Person relations
        if type1 == "person" and type2 == "person":
            if any(word in text_lower for word in ["family", "married", "parent", "child"]):
                return "related_to"
                
        return "associated_with"  # Generic relation
        
    def _remove_duplicate_relations(self, relations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate relations"""
        
        unique_relations = []
        seen_relations = set()
        
        for relation in relations:
            # Create a key based on source, target, and type
            source_id = relation["source"]["text"]
            target_id = relation["target"]["text"]
            relation_type = relation["type"]
            
            relation_key = (source_id, target_id, relation_type)
            
            if relation_key not in seen_relations:
                unique_relations.append(relation)
                seen_relations.add(relation_key)
                
        return unique_relations
        
    def get_relation_statistics(self, relations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about extracted relations"""
        
        if not relations:
            return {"total_relations": 0}
            
        # Count by type
        type_counts = {}
        for relation in relations:
            relation_type = relation["type"]
            type_counts[relation_type] = type_counts.get(relation_type, 0) + 1
            
        # Average confidence
        confidences = [r["confidence"] for r in relations]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Extraction methods
        methods = {}
        for relation in relations:
            method = relation["extraction_method"]
            methods[method] = methods.get(method, 0) + 1
            
        return {
            "total_relations": len(relations),
            "type_distribution": type_counts,
            "average_confidence": avg_confidence,
            "extraction_methods": methods,
            "high_confidence_relations": len([r for r in relations if r["confidence"] > 0.7])
        }
