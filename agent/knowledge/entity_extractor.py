"""
Entity extraction component for identifying and extracting entities from text
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger


class EntityExtractor:
    """Entity extractor for identifying named entities in text"""
    
    def __init__(self):
        # Entity patterns
        self.patterns = {
            "person": [
                r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # First Last
                r'\b(?:Mr|Mrs|Ms|Dr|Prof)\.?\s+[A-Z][a-z]+ [A-Z][a-z]+\b'  # Title + Name
            ],
            "organization": [
                r'\b[A-Z][a-z]+ (?:Inc|Ltd|Corp|Company|Corporation|LLC|LTD)\b',
                r'\b[A-Z][a-z]+ (?:University|College|Institute)\b',
                r'\b[A-Z][a-z]+ [A-Z][a-z]+ (?:Technologies|Systems|Solutions)\b'
            ],
            "location": [
                r'\b[A-Z][a-z]+, [A-Z]{2}\b',  # City, State
                r'\b[A-Z][a-z]+, [A-Z][a-z]+\b',  # City, Country
                r'\b(?:North|South|East|West) [A-Z][a-z]+\b'  # Direction + Place
            ],
            "date": [
                r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
                r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
                r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}\b'
            ],
            "email": [
                r'\b[\w\.-]+@[\w\.-]+\.\w+\b'
            ],
            "phone": [
                r'\b\d{3}-\d{3}-\d{4}\b',
                r'\b\(\d{3}\) \d{3}-\d{4}\b',
                r'\b\d{3}\.\d{3}\.\d{4}\b'
            ],
            "url": [
                r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?'
            ],
            "money": [
                r'\$\d+(?:,\d{3})*(?:\.\d{2})?',
                r'\b\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:dollars?|USD|bucks?)\b'
            ],
            "product": [
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Pro|Max|Plus|Ultra|Lite|Mini)\b',
                r'\b[A-Z][a-z]+\d+(?:\s+[A-Z][a-z]+)?\b'  # Brand + Model number
            ]
        }
        
        # Common entity dictionaries
        self.common_entities = {
            "technology": [
                "Python", "JavaScript", "Java", "C++", "Ruby", "Go", "Rust",
                "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas",
                "Machine Learning", "Deep Learning", "Neural Networks", "AI",
                "Docker", "Kubernetes", "AWS", "Azure", "Google Cloud"
            ],
            "science": [
                "Physics", "Chemistry", "Biology", "Mathematics", "Statistics",
                "Einstein", "Newton", "Darwin", "Curie", "Hawking"
            ],
            "business": [
                "CEO", "CTO", "CFO", "Manager", "Director", "President",
                "Revenue", "Profit", "Loss", "Investment", "Portfolio"
            ]
        }
        
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities from text"""
        
        entities = []
        
        # Pattern-based extraction
        for entity_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    entity = {
                        "type": entity_type,
                        "text": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                        "confidence": 0.8,
                        "extraction_method": "pattern"
                    }
                    entities.append(entity)
                    
        # Dictionary-based extraction
        for category, entity_list in self.common_entities.items():
            for entity_name in entity_list:
                if entity_name in text:
                    start = text.find(entity_name)
                    entity = {
                        "type": category,
                        "text": entity_name,
                        "start": start,
                        "end": start + len(entity_name),
                        "confidence": 0.9,
                        "extraction_method": "dictionary"
                    }
                    entities.append(entity)
                    
        # Remove duplicates and sort by position
        unique_entities = self._remove_duplicates(entities)
        unique_entities.sort(key=lambda x: x["start"])
        
        return unique_entities
        
    def _remove_duplicates(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate entities"""
        
        unique_entities = []
        seen_spans = set()
        
        for entity in entities:
            span = (entity["start"], entity["end"])
            if span not in seen_spans:
                unique_entities.append(entity)
                seen_spans.add(span)
                
        return unique_entities
        
    def extract_relations(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract relations between entities"""
        
        relations = []
        
        # Simple relation patterns
        relation_patterns = [
            (r'(\w+)\s+(?:is|was)\s+(?:a|an|the)?\s*(\w+)', "is_a"),
            (r'(\w+)\s+(?:works for|employed by)\s+(\w+)', "works_for"),
            (r'(\w+)\s+(?:located in|in)\s+(\w+)', "located_in"),
            (r'(\w+)\s+(?:founded|created|established)\s+(\w+)', "founded"),
            (r'(\w+)\s+(?:owns|owns the)\s+(\w+)', "owns")
        ]
        
        for pattern, relation_type in relation_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                source_text = match.group(1)
                target_text = match.group(2)
                
                # Find corresponding entities
                source_entity = self._find_entity_by_text(source_text, entities)
                target_entity = self._find_entity_by_text(target_text, entities)
                
                if source_entity and target_entity:
                    relation = {
                        "type": relation_type,
                        "source": source_entity,
                        "target": target_entity,
                        "confidence": 0.7,
                        "extraction_method": "pattern"
                    }
                    relations.append(relation)
                    
        return relations
        
    def _find_entity_by_text(self, text: str, entities: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find entity by text content"""
        
        for entity in entities:
            if entity["text"].lower() == text.lower():
                return entity
                
        # Partial match
        for entity in entities:
            if text.lower() in entity["text"].lower() or entity["text"].lower() in text.lower():
                return entity
                
        return None
        
    def get_entity_statistics(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about extracted entities"""
        
        if not entities:
            return {"total_entities": 0}
            
        # Count by type
        type_counts = {}
        for entity in entities:
            entity_type = entity["type"]
            type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
            
        # Average confidence
        confidences = [e["confidence"] for e in entities]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            "total_entities": len(entities),
            "type_distribution": type_counts,
            "average_confidence": avg_confidence,
            "extraction_methods": {
                method: len([e for e in entities if e["extraction_method"] == method])
                for method in set(e["extraction_method"] for e in entities)
            }
        }
