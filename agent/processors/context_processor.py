"""
Context processing component for understanding and managing conversation context
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from collections import deque
import re
from loguru import logger


class ContextProcessor:
    """Context processor for managing conversation context and situational awareness"""
    
    def __init__(self, max_context_length: int = 10):
        self.max_context_length = max_context_length
        self.conversation_history: deque = deque(maxlen=max_context_length)
        self.context_variables: Dict[str, Any] = {}
        self.topic_history: List[str] = []
        self.entity_mentions: Dict[str, List[datetime]] = {}
        
    def process_context(self, current_input: str, previous_interactions: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process and update conversation context"""
        
        # Add current input to history
        self.conversation_history.append({
            "text": current_input,
            "timestamp": datetime.now(timezone.utc),
            "type": "user_input"
        })
        
        # Extract topics
        topics = self._extract_topics(current_input)
        self.topic_history.extend(topics)
        
        # Keep topic history manageable
        if len(self.topic_history) > 50:
            self.topic_history = self.topic_history[-50:]
            
        # Extract entities
        entities = self._extract_entities(current_input)
        self._update_entity_mentions(entities)
        
        # Analyze conversation flow
        flow_analysis = self._analyze_conversation_flow()
        
        # Detect context shifts
        context_shift = self._detect_context_shift(current_input)
        
        # Update context variables
        self._update_context_variables(current_input, topics, entities)
        
        # Build context summary
        context_summary = self._build_context_summary()
        
        return {
            "topics": topics,
            "entities": entities,
            "flow_analysis": flow_analysis,
            "context_shift": context_shift,
            "context_variables": self.context_variables.copy(),
            "summary": context_summary,
            "conversation_length": len(self.conversation_history)
        }
        
    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text"""
        
        # Simple topic extraction based on keywords and patterns
        topics = []
        
        # Common topic indicators
        topic_patterns = {
            "technology": ["computer", "software", "programming", "code", "algorithm", "data", "ai", "machine learning", "python", "javascript"],
            "science": ["research", "study", "experiment", "theory", "hypothesis", "analysis", "discovery", "scientific"],
            "business": ["company", "business", "market", "sales", "revenue", "profit", "customer", "product", "service"],
            "education": ["learning", "teaching", "school", "university", "student", "course", "lesson", "education"],
            "health": ["health", "medicine", "doctor", "patient", "treatment", "disease", "symptom", "medical"],
            "entertainment": ["movie", "music", "game", "book", "show", "entertainment", "fun", "play"],
            "sports": ["sport", "game", "team", "player", "match", "competition", "score", "win"],
            "travel": ["travel", "trip", "vacation", "hotel", "flight", "destination", "tourism"]
        }
        
        text_lower = text.lower()
        
        for topic, keywords in topic_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
                
        # Extract noun phrases as potential topics (simplified)
        noun_phrases = self._extract_noun_phrases(text)
        topics.extend(noun_phrases[:3])  # Add top 3 noun phrases
        
        return list(set(topics))  # Remove duplicates
        
    def _extract_noun_phrases(self, text: str) -> List[str]:
        """Extract noun phrases (simplified implementation)"""
        
        # Simple pattern: adjective + noun or noun + noun
        patterns = [
            r'\b[A-Za-z]+ [A-Za-z]+\b',  # Two-word phrases
            r'\b[A-Za-z]+ [A-Za-z]+ [A-Za-z]+\b'  # Three-word phrases
        ]
        
        phrases = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            phrases.extend(matches)
            
        # Filter out common non-topics
        stop_phrases = {"I want", "I need", "I think", "I feel", "this is", "that is", "there is", "here is"}
        phrases = [p for p in phrases if p.lower() not in stop_phrases]
        
        return phrases
        
    def _extract_entities(self, text: str) -> List[Dict[str, str]]:
        """Extract named entities (simplified)"""
        
        entities = []
        
        # Person names (capitalized words)
        person_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        for match in re.findall(person_pattern, text):
            entities.append({"type": "person", "text": match})
            
        # Organizations
        org_pattern = r'\b[A-Z][a-z]+ (?:Inc|Ltd|Corp|Company|University|College)\b'
        for match in re.findall(org_pattern, text):
            entities.append({"type": "organization", "text": match})
            
        # Locations
        location_pattern = r'\b[A-Z][a-z]+, [A-Z]{2}\b'  # City, State
        for match in re.findall(location_pattern, text):
            entities.append({"type": "location", "text": match})
            
        # Dates
        date_pattern = r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}\b'
        for match in re.findall(date_pattern, text):
            entities.append({"type": "date", "text": match})
            
        return entities
        
    def _update_entity_mentions(self, entities: List[Dict[str, str]]) -> None:
        """Update entity mention tracking"""

        current_time = datetime.now(timezone.utc)

        for entity in entities:
            entity_text = entity["text"]
            if entity_text not in self.entity_mentions:
                self.entity_mentions[entity_text] = []
            self.entity_mentions[entity_text].append(current_time)

        # Clean old mentions (older than 1 hour)
        cutoff_time = current_time - timedelta(hours=1)
        for entity_text in self.entity_mentions:
            self.entity_mentions[entity_text] = [
                mention for mention in self.entity_mentions[entity_text]
                if mention > cutoff_time
            ]
            
    def _analyze_conversation_flow(self) -> Dict[str, Any]:
        """Analyze conversation flow patterns"""
        
        if len(self.conversation_history) < 2:
            return {
                "flow_type": "starting",
                "topic_continuity": 0.0,
                "engagement_level": 0.0,
                "conversation_depth": len(self.conversation_history)
            }
            
        # Analyze topic continuity
        recent_topics = self.topic_history[-5:] if self.topic_history else []
        topic_continuity = len(set(recent_topics)) / len(recent_topics) if recent_topics else 0.0
        
        # Analyze response patterns
        flow_type = "continuous"
        if topic_continuity > 0.8:
            flow_type = "focused"
        elif topic_continuity < 0.3:
            flow_type = "fragmented"
            
        # Calculate engagement level
        engagement = self._calculate_engagement()
        
        return {
            "flow_type": flow_type,
            "topic_continuity": topic_continuity,
            "engagement_level": engagement,
            "conversation_depth": len(self.conversation_history)
        }
        
    def _calculate_engagement(self) -> float:
        """Calculate conversation engagement level"""
        
        if len(self.conversation_history) == 0:
            return 0.0
            
        # Factors for engagement
        factors = {
            "length": 0.0,
            "questions": 0.0,
            "entities": 0.0,
            "variety": 0.0
        }
        
        # Average message length
        total_length = sum(len(item["text"]) for item in self.conversation_history)
        avg_length = total_length / len(self.conversation_history)
        factors["length"] = min(1.0, avg_length / 100)  # Normalize to 0-1
        
        # Question frequency
        question_count = sum(item["text"].count("?") for item in self.conversation_history)
        factors["questions"] = min(1.0, question_count / len(self.conversation_history))
        
        # Entity variety
        unique_entities = len(self.entity_mentions)
        factors["entities"] = min(1.0, unique_entities / 10)
        
        # Topic variety
        unique_topics = len(set(self.topic_history))
        factors["variety"] = min(1.0, unique_topics / 5)
        
        # Calculate overall engagement
        engagement = sum(factors.values()) / len(factors)
        return engagement
        
    def _detect_context_shift(self, current_text: str) -> Dict[str, Any]:
        """Detect if there's a context shift in the conversation"""
        
        if len(self.conversation_history) < 2:
            return {"shift_detected": False, "shift_type": "none"}
            
        previous_text = self.conversation_history[-2]["text"]
        
        # Calculate similarity between current and previous text
        similarity = self._calculate_text_similarity(previous_text, current_text)
        
        shift_detected = similarity < 0.3
        shift_type = "topic_change" if shift_detected else "continuation"
        
        # Check for specific shift indicators
        if any(indicator in current_text.lower() for indicator in 
               ["by the way", "changing subject", "speaking of", "that reminds me"]):
            shift_detected = True
            shift_type = "explicit_shift"
            
        return {
            "shift_detected": shift_detected,
            "shift_type": shift_type,
            "similarity_score": similarity
        }
        
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
        
    def _update_context_variables(self, text: str, topics: List[str], 
                                 entities: List[Dict[str, str]]) -> None:
        """Update context variables based on current input"""
        
        # Update current topics
        self.context_variables["current_topics"] = topics
        
        # Update active entities
        self.context_variables["active_entities"] = [e["text"] for e in entities]
        
        # Update conversation state
        self.context_variables["last_interaction"] = datetime.now(timezone.utc).isoformat()
        self.context_variables["interaction_count"] = len(self.conversation_history)
        
        # Detect user intent
        intent = self._detect_intent(text)
        self.context_variables["user_intent"] = intent
        
    def _detect_intent(self, text: str) -> str:
        """Detect user intent from text"""
        
        text_lower = text.lower()
        
        # Question patterns
        if any(text_lower.startswith(q) for q in ["what", "where", "when", "why", "how", "who", "which"]):
            return "question"
            
        # Command patterns
        if any(word in text_lower for word in ["tell me", "show me", "give me", "find", "search", "look up"]):
            return "command"
            
        # Request patterns
        if any(word in text_lower for word in ["please", "could you", "would you", "can you"]):
            return "request"
            
        # Statement patterns
        if any(text_lower.endswith(p) for p in [".", "!"]):
            return "statement"
            
        return "unknown"
        
    def _build_context_summary(self) -> Dict[str, Any]:
        """Build a summary of current context"""

        # Get recent topics
        recent_topics = list(set(self.topic_history[-5:])) if self.topic_history else []

        # Get active entities (mentioned in last 10 minutes)
        current_time = datetime.now(timezone.utc)
        cutoff_time = current_time - timedelta(minutes=10)
        active_entities = [
            entity for entity, mentions in self.entity_mentions.items()
            if any(mention > cutoff_time for mention in mentions)
        ]
        
        # Get conversation stage
        stage = self._determine_conversation_stage()
        
        return {
            "recent_topics": recent_topics,
            "active_entities": active_entities,
            "conversation_stage": stage,
            "context_duration": (current_time - self.conversation_history[0]["timestamp"]).total_seconds() if self.conversation_history else 0,
            "total_entities_mentioned": len(self.entity_mentions),
            "topic_diversity": len(set(self.topic_history))
        }
        
    def _determine_conversation_stage(self) -> str:
        """Determine current conversation stage"""
        
        if len(self.conversation_history) == 0:
            return "not_started"
        elif len(self.conversation_history) <= 3:
            return "opening"
        elif len(self.conversation_history) <= 10:
            return "middle"
        else:
            return "extended"
            
    def get_context_for_response(self) -> Dict[str, Any]:
        """Get relevant context for generating responses"""
        
        return {
            "recent_history": list(self.conversation_history)[-3:],  # Last 3 interactions
            "current_topics": self.context_variables.get("current_topics", []),
            "active_entities": self.context_variables.get("active_entities", []),
            "user_intent": self.context_variables.get("user_intent", "unknown"),
            "conversation_stage": self._determine_conversation_stage(),
            "engagement_level": self._calculate_engagement()
        }
        
    def reset_context(self) -> None:
        """Reset conversation context"""
        
        self.conversation_history.clear()
        self.context_variables.clear()
        self.topic_history.clear()
        self.entity_mentions.clear()
        
        logger.info("Conversation context reset")
        
    def get_context_statistics(self) -> Dict[str, Any]:
        """Get statistics about conversation context"""
        
        return {
            "conversation_length": len(self.conversation_history),
            "unique_topics": len(set(self.topic_history)),
            "total_entities": len(self.entity_mentions),
            "active_entities": len([
                e for e, mentions in self.entity_mentions.items()
                if mentions  # Has recent mentions
            ]),
            "context_variables_count": len(self.context_variables),
            "average_engagement": self._calculate_engagement()
        }
