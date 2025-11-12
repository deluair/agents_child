"""
Feedback processing system for learning from user interactions
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import re
from loguru import logger


class FeedbackProcessor:
    """Processes and analyzes user feedback for learning"""
    
    def __init__(self):
        self.feedback_categories = {
            "positive": ["good", "great", "excellent", "helpful", "perfect", "amazing", "thanks", "thank you"],
            "negative": ["bad", "terrible", "unhelpful", "wrong", "incorrect", "poor", "awful"],
            "neutral": ["okay", "fine", "alright", "decent", "acceptable"]
        }
        
        self.aspect_keywords = {
            "accuracy": ["correct", "accurate", "right", "wrong", "inaccurate", "mistake"],
            "helpfulness": ["helpful", "useful", "unhelpful", "useless", "relevant", "irrelevant"],
            "clarity": ["clear", "unclear", "confusing", "easy", "difficult", "understandable"],
            "completeness": ["complete", "incomplete", "missing", "thorough", "detailed", "brief"],
            "tone": ["friendly", "rude", "polite", "professional", "casual", "formal"]
        }
        
    def process_feedback(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw feedback and extract structured information"""
        
        processed = {
            "timestamp": datetime.now().isoformat(),
            "raw_feedback": feedback,
            "sentiment": self._analyze_sentiment(feedback),
            "aspects": self._analyze_aspects(feedback),
            "category": self._categorize_feedback(feedback),
            "severity": self._assess_severity(feedback),
            "actionable": self._is_actionable(feedback)
        }
        
        logger.debug(f"Processed feedback: {processed['category']} - {processed['sentiment']}")
        return processed
        
    def _analyze_sentiment(self, feedback: Dict[str, Any]) -> str:
        """Analyze sentiment of feedback"""
        
        text = feedback.get("comment", "").lower()
        rating = feedback.get("rating", 0.5)
        
        # Check explicit rating first
        if rating >= 0.7:
            return "positive"
        elif rating <= 0.3:
            return "negative"
        else:
            return "neutral"
            
    def _analyze_aspects(self, feedback: Dict[str, Any]) -> List[str]:
        """Extract aspects mentioned in feedback"""
        
        text = feedback.get("comment", "").lower()
        mentioned_aspects = []
        
        for aspect, keywords in self.aspect_keywords.items():
            if any(keyword in text for keyword in keywords):
                mentioned_aspects.append(aspect)
                
        return mentioned_aspects
        
    def _categorize_feedback(self, feedback: Dict[str, Any]) -> str:
        """Categorize feedback into predefined categories"""
        
        text = feedback.get("comment", "").lower()
        rating = feedback.get("rating", 0.5)
        
        # Rating-based categorization
        if rating >= 0.8:
            return "highly_positive"
        elif rating >= 0.6:
            return "positive"
        elif rating >= 0.4:
            return "neutral"
        elif rating >= 0.2:
            return "negative"
        else:
            return "highly_negative"
            
    def _assess_severity(self, feedback: Dict[str, Any]) -> str:
        """Assess severity level of feedback"""
        
        text = feedback.get("comment", "").lower()
        rating = feedback.get("rating", 0.5)
        
        # Check for strong negative indicators
        strong_negative = ["terrible", "awful", "horrible", "useless", "completely wrong"]
        if any(word in text for word in strong_negative) or rating <= 0.2:
            return "high"
            
        # Check for moderate negative indicators
        moderate_negative = ["bad", "poor", "unhelpful", "not good"]
        if any(word in text for word in moderate_negative) or rating <= 0.4:
            return "medium"
            
        return "low"
        
    def _is_actionable(self, feedback: Dict[str, Any]) -> bool:
        """Determine if feedback is actionable for learning"""
        
        text = feedback.get("comment", "").lower()
        
        # Check for specific suggestions or corrections
        actionable_patterns = [
            r"should have",
            r"could have",
            r"instead of",
            r"try to",
            r"consider",
            r"maybe you should",
            r"it would be better if"
        ]
        
        for pattern in actionable_patterns:
            if re.search(pattern, text):
                return True
                
        # Check if specific aspects are mentioned
        aspects = self._analyze_aspects(feedback)
        return len(aspects) > 0
        
    def extract_learning_signals(self, processed_feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Extract specific learning signals from processed feedback"""
        
        signals = {
            "improvement_areas": [],
            "strength_areas": [],
            "specific_corrections": [],
            "behavior_adjustments": []
        }
        
        sentiment = processed_feedback["sentiment"]
        aspects = processed_feedback["aspects"]
        category = processed_feedback["category"]
        
        # Identify improvement areas
        if sentiment in ["negative", "highly_negative"]:
            signals["improvement_areas"] = aspects
            
        # Identify strength areas
        if sentiment in ["positive", "highly_positive"]:
            signals["strength_areas"] = aspects
            
        # Extract specific corrections
        text = processed_feedback["raw_feedback"].get("comment", "")
        corrections = self._extract_corrections(text)
        signals["specific_corrections"] = corrections
        
        # Suggest behavior adjustments
        adjustments = self._suggest_adjustments(category, aspects)
        signals["behavior_adjustments"] = adjustments
        
        return signals
        
    def _extract_corrections(self, text: str) -> List[str]:
        """Extract specific corrections from feedback text"""
        
        corrections = []
        
        # Look for correction patterns
        correction_patterns = [
            r"instead of (.*?), you should have (.*?)",
            r"(.*?) would have been better",
            r"you should have said (.*?)",
            r"the correct answer is (.*?)"
        ]
        
        for pattern in correction_patterns:
            matches = re.findall(pattern, text.lower())
            corrections.extend(matches)
            
        return corrections
        
    def _suggest_adjustments(self, category: str, aspects: List[str]) -> List[str]:
        """Suggest behavioral adjustments based on feedback"""
        
        adjustments = []
        
        if category in ["negative", "highly_negative"]:
            adjustments.append("increase_caution")
            adjustments.append("seek_clarification")
            
        if "accuracy" in aspects:
            adjustments.append("verify_facts")
            adjustments.append("reduce_confidence")
            
        if "clarity" in aspects:
            adjustments.append("simplify_language")
            adjustments.append("provide_examples")
            
        if "helpfulness" in aspects:
            adjustments.append("provide_more_detail")
            adjustments.append("offer_alternatives")
            
        if "tone" in aspects:
            adjustments.append("adjust_tone")
            adjustments.append("increase_politeness")
            
        return list(set(adjustments))  # Remove duplicates
