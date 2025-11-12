"""
Adaptation engine for dynamic behavior adjustment
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
import numpy as np
from loguru import logger


class AdaptationEngine:
    """Engine for adapting agent behavior based on learning and feedback"""
    
    def __init__(self):
        self.adaptation_strategies = {
            "response_length": {"short": 0.3, "medium": 0.5, "long": 0.7},
            "formality": {"casual": 0.3, "neutral": 0.5, "formal": 0.7},
            "confidence": {"low": 0.3, "medium": 0.5, "high": 0.7},
            "detail_level": {"brief": 0.3, "moderate": 0.5, "detailed": 0.7}
        }
        
        self.current_settings = {
            "response_length": 0.5,
            "formality": 0.5,
            "confidence": 0.5,
            "detail_level": 0.5
        }
        
        self.adaptation_history = []
        self.performance_window = 20  # Number of recent interactions to consider
        
    def adapt(self, feedback: Dict[str, Any], performance_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Adapt agent behavior based on feedback and performance"""
        
        adaptation = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trigger_feedback": feedback,
            "trigger_metrics": performance_metrics,
            "adjustments": {},
            "rationale": []
        }
        
        # Analyze what needs adaptation
        needed_adjustments = self._analyze_adaptation_needs(feedback, performance_metrics)
        
        # Apply adjustments
        for adjustment_type, adjustment_value in needed_adjustments.items():
            old_value = self.current_settings.get(adjustment_type, 0.5)
            new_value = self._apply_adjustment(old_value, adjustment_value, adjustment_type)
            
            self.current_settings[adjustment_type] = new_value
            adaptation["adjustments"][adjustment_type] = {
                "old_value": old_value,
                "new_value": new_value,
                "change": new_value - old_value
            }
            
        # Record rationale
        adaptation["rationale"] = self._generate_adaptation_rationale(needed_adjustments)
        
        # Store adaptation
        self.adaptation_history.append(adaptation)
        
        # Keep only recent adaptations
        if len(self.adaptation_history) > 100:
            self.adaptation_history = self.adaptation_history[-100:]
            
        logger.info(f"Applied {len(adaptation['adjustments'])} adaptations")
        return adaptation
        
    def _analyze_adaptation_needs(self, feedback: Dict[str, Any], 
                                 performance_metrics: Dict[str, float]) -> Dict[str, float]:
        """Analyze what adaptations are needed"""
        
        needs = {}
        
        # Analyze feedback sentiment
        sentiment = feedback.get("sentiment", "neutral")
        rating = feedback.get("rating", 0.5)
        
        # Analyze performance metrics
        satisfaction = performance_metrics.get("user_satisfaction", 0.5)
        response_time = performance_metrics.get("response_time", 1.0)
        
        # Adapt based on satisfaction
        if satisfaction < 0.4:
            needs["confidence"] = -0.2  # Reduce confidence
            needs["detail_level"] = 0.1  # Increase detail
        elif satisfaction > 0.8:
            needs["confidence"] = 0.1   # Increase confidence slightly
            
        # Adapt based on response time
        if response_time > 2.0:  # Slow responses
            needs["response_length"] = -0.1  # Make responses shorter
            needs["detail_level"] = -0.1     # Reduce detail
            
        # Adapt based on feedback aspects
        aspects = feedback.get("aspects", [])
        
        if "clarity" in aspects:
            if sentiment == "negative":
                needs["response_length"] = -0.2  # Shorter, clearer responses
                needs["detail_level"] = -0.1
            else:
                needs["detail_level"] = 0.1     # More detail for clarity
                
        if "helpfulness" in aspects:
            if sentiment == "negative":
                needs["detail_level"] = 0.2     # Increase detail
                needs["response_length"] = 0.1  # Longer responses
                
        if "tone" in aspects:
            if sentiment == "negative":
                needs["formality"] = 0.1        # Increase formality
                
        # Adapt based on rating
        if rating < 0.3:
            needs["confidence"] = -0.3
            needs["formality"] = 0.1
        elif rating > 0.8:
            needs["confidence"] = 0.1
            
        return needs
        
    def _apply_adjustment(self, current_value: float, adjustment: float, 
                         adjustment_type: str) -> float:
        """Apply an adjustment to a current setting"""
        
        # Calculate new value with bounds checking
        new_value = current_value + adjustment
        
        # Apply bounds (0.0 to 1.0)
        new_value = max(0.0, min(1.0, new_value))
        
        # Apply gradual change constraint (max 0.2 change per adaptation)
        max_change = 0.2
        if abs(new_value - current_value) > max_change:
            new_value = current_value + (max_change if adjustment > 0 else -max_change)
            
        return new_value
        
    def _generate_adaptation_rationale(self, adjustments: Dict[str, float]) -> List[str]:
        """Generate rationale for applied adaptations"""
        
        rationale = []
        
        for adjustment_type, value in adjustments.items():
            if adjustment_type == "confidence":
                if value < 0:
                    rationale.append("Reducing confidence due to negative feedback")
                else:
                    rationale.append("Increasing confidence based on positive performance")
                    
            elif adjustment_type == "detail_level":
                if value > 0:
                    rationale.append("Increasing detail level to improve helpfulness")
                else:
                    rationale.append("Reducing detail level to improve clarity")
                    
            elif adjustment_type == "response_length":
                if value > 0:
                    rationale.append("Increasing response length for more comprehensive answers")
                else:
                    rationale.append("Decreasing response length for faster, clearer responses")
                    
            elif adjustment_type == "formality":
                if value > 0:
                    rationale.append("Increasing formality to improve tone")
                else:
                    rationale.append("Decreasing formality for more natural conversation")
                    
        return rationale
        
    def get_current_settings(self) -> Dict[str, float]:
        """Get current adaptation settings"""
        return self.current_settings.copy()
        
    def apply_settings_to_response(self, base_response: str) -> str:
        """Apply current settings to modify a response"""
        
        response = base_response
        
        # Apply response length adjustment
        length_setting = self.current_settings["response_length"]
        if length_setting < 0.4:  # Short
            response = self._shorten_response(response)
        elif length_setting > 0.6:  # Long
            response = self._lengthen_response(response)
            
        # Apply detail level adjustment
        detail_setting = self.current_settings["detail_level"]
        if detail_setting < 0.4:  # Brief
            response = self._reduce_detail(response)
        elif detail_setting > 0.6:  # Detailed
            response = self._add_detail(response)
            
        # Apply formality adjustment
        formality_setting = self.current_settings["formality"]
        if formality_setting < 0.4:  # Casual
            response = self._make_casual(response)
        elif formality_setting > 0.6:  # Formal
            response = self._make_formal(response)
            
        return response
        
    def _shorten_response(self, response: str) -> str:
        """Shorten a response"""
        sentences = response.split('.')
        if len(sentences) > 2:
            return '. '.join(sentences[:2]) + '.'
        return response
        
    def _lengthen_response(self, response: str) -> str:
        """Lengthen a response"""
        if not response.endswith('.'):
            response += '.'
        response += " Is there anything specific about this you'd like me to elaborate on?"
        return response
        
    def _reduce_detail(self, response: str) -> str:
        """Reduce detail in response"""
        # Simple implementation - remove parenthetical details
        import re
        response = re.sub(r'\([^)]*\)', '', response)
        return response.strip()
        
    def _add_detail(self, response: str) -> str:
        """Add detail to response"""
        if not response.endswith('.'):
            response += '.'
        response += " This involves several important factors that are worth considering."
        return response
        
    def _make_casual(self, response: str) -> str:
        """Make response more casual"""
        casual_replacements = {
            "I understand": "Got it",
            "Therefore": "So",
            "However": "But",
            "Furthermore": "Also",
            "consequently": "so"
        }
        
        for formal, casual in casual_replacements.items():
            response = response.replace(formal, casual)
            
        return response
        
    def _make_formal(self, response: str) -> str:
        """Make response more formal"""
        formal_replacements = {
            "Got it": "I understand",
            "So": "Therefore",
            "But": "However",
            "Also": "Furthermore",
            "yeah": "yes",
            "gonna": "going to"
        }
        
        for casual, formal in formal_replacements.items():
            response = response.replace(casual, formal)
            
        return response
        
    def get_adaptation_statistics(self) -> Dict[str, Any]:
        """Get statistics about adaptations"""
        
        if not self.adaptation_history:
            return {
                "total_adaptations": 0,
                "adaptation_frequency": 0.0
            }
            
        total_adaptations = len(self.adaptation_history)
        
        # Calculate adaptation frequency (adaptations per day)
        if total_adaptations > 1:
            first_adaptation = datetime.fromisoformat(self.adaptation_history[0]["timestamp"])
            days_since_first = (datetime.now(timezone.utc) - first_adaptation).days
            frequency = total_adaptations / max(1, days_since_first)
        else:
            frequency = 0.0
            
        # Analyze common adjustments
        adjustment_counts = {}
        for adaptation in self.adaptation_history:
            for adj_type in adaptation["adjustments"].keys():
                adjustment_counts[adj_type] = adjustment_counts.get(adj_type, 0) + 1
                
        return {
            "total_adaptations": total_adaptations,
            "adaptation_frequency": frequency,
            "common_adjustments": adjustment_counts,
            "current_settings": self.current_settings,
            "recent_adaptations": len([
                a for a in self.adaptation_history
                if datetime.fromisoformat(a["timestamp"]) > datetime.now(timezone.utc) - timedelta(days=1)
            ])
        }
        
    def reset_adaptations(self) -> None:
        """Reset all adaptations to default values"""
        
        logger.warning("Resetting all adaptations")
        
        self.current_settings = {
            "response_length": 0.5,
            "formality": 0.5,
            "confidence": 0.5,
            "detail_level": 0.5
        }
        
        self.adaptation_history.clear()
        
        logger.info("Adaptations reset completed")
