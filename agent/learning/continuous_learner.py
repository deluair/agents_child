"""
Continuous learning system for adaptive behavior improvement
"""

import os
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta, timezone
from loguru import logger
import json
from collections import deque, defaultdict

from ..core.config import LearningConfig


class ContinuousLearner:
    """Continuous learning system that adapts based on interactions and feedback"""
    
    def __init__(self, config: LearningConfig, memory_path: str = "./memory"):
        self.config = config
        self.memory_path = memory_path
        self._ensure_memory_directory()
        
        # Learning data storage
        self.interaction_history: deque = deque(maxlen=1000)
        self.feedback_history: deque = deque(maxlen=500)
        self.performance_metrics: Dict[str, List[float]] = defaultdict(list)
        
        # Model parameters (simplified for demonstration)
        self.response_patterns: Dict[str, List[str]] = defaultdict(list)
        self.context_weights: Dict[str, float] = defaultdict(float)
        self.success_patterns: Dict[str, float] = defaultdict(float)
        
        # Learning statistics
        self.learning_episodes = 0
        self.last_optimization = datetime.now(timezone.utc)
        self.adaptation_count = 0
        
        # Load existing learning data
        self._load_learning_data()
        
        logger.info("Continuous learner initialized")
        
    def _ensure_memory_directory(self):
        """Ensure learning memory directory exists"""
        os.makedirs(self.memory_path, exist_ok=True)
        
    def _load_learning_data(self):
        """Load existing learning data from disk (secure JSON format)"""
        learning_file = os.path.join(self.memory_path, "learning_data.json")
        legacy_file = os.path.join(self.memory_path, "learning_data.pkl")

        if os.path.exists(learning_file):
            try:
                with open(learning_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.interaction_history = deque(data.get("interaction_history", []), maxlen=1000)
                self.feedback_history = deque(data.get("feedback_history", []), maxlen=500)
                self.performance_metrics = defaultdict(list, data.get("performance_metrics", {}))
                self.response_patterns = defaultdict(list, data.get("response_patterns", {}))
                self.context_weights = defaultdict(float, data.get("context_weights", {}))
                self.success_patterns = defaultdict(float, data.get("success_patterns", {}))
                self.learning_episodes = data.get("learning_episodes", 0)
                self.adaptation_count = data.get("adaptation_count", 0)

                # Parse timestamp
                last_opt_str = data.get("last_optimization")
                if last_opt_str:
                    try:
                        self.last_optimization = datetime.fromisoformat(last_opt_str)
                    except (ValueError, TypeError):
                        self.last_optimization = datetime.now(timezone.utc)
                else:
                    self.last_optimization = datetime.now(timezone.utc)

                logger.info("Learning data loaded from disk (JSON)")

            except Exception as e:
                logger.warning(f"Failed to load learning data: {e}")

        elif os.path.exists(legacy_file):
            logger.warning("Legacy pickle format detected. Please migrate to JSON format.")
            logger.warning("For security, pickle format is no longer supported.")
                
    def _save_learning_data(self):
        """Save learning data to disk (secure JSON format)"""
        learning_file = os.path.join(self.memory_path, "learning_data.json")
        temp_file = learning_file + ".tmp"

        try:
            data = {
                "interaction_history": list(self.interaction_history),
                "feedback_history": list(self.feedback_history),
                "performance_metrics": dict(self.performance_metrics),
                "response_patterns": dict(self.response_patterns),
                "context_weights": dict(self.context_weights),
                "success_patterns": dict(self.success_patterns),
                "learning_episodes": self.learning_episodes,
                "last_optimization": self.last_optimization.isoformat() if isinstance(self.last_optimization, datetime) else str(self.last_optimization),
                "adaptation_count": self.adaptation_count
            }

            # Atomic write
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)

            os.replace(temp_file, learning_file)

            logger.debug("Learning data saved to disk (JSON)")

        except Exception as e:
            logger.warning(f"Failed to save learning data: {e}")
            # Clean up temp file
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            
    def learn_from_interaction(self, interaction: Dict[str, Any]) -> None:
        """Learn from a new interaction"""
        
        # Add to interaction history
        interaction["timestamp"] = datetime.now(timezone.utc).isoformat()
        self.interaction_history.append(interaction)
        
        # Extract learning signals
        self._extract_patterns(interaction)
        self._update_context_weights(interaction)
        self._track_performance(interaction)
        
        self.learning_episodes += 1
        
        # Trigger optimization if needed
        if self.learning_episodes % self.config.update_frequency == 0:
            self._optimize_learning()
            
        self._save_learning_data()
        
    def _extract_patterns(self, interaction: Dict[str, Any]) -> None:
        """Extract patterns from interactions"""
        
        input_text = interaction.get("input", "").lower()
        response = interaction.get("response", "").lower()
        
        # Extract input patterns
        input_words = input_text.split()
        if len(input_words) > 0:
            # Use first few words as pattern key
            pattern_key = " ".join(input_words[:3])
            
            if pattern_key not in self.response_patterns:
                self.response_patterns[pattern_key] = []
                
            self.response_patterns[pattern_key].append(response)
            
            # Keep only recent responses for each pattern
            if len(self.response_patterns[pattern_key]) > 10:
                self.response_patterns[pattern_key] = self.response_patterns[pattern_key][-10:]
                
    def _update_context_weights(self, interaction: Dict[str, Any]) -> None:
        """Update weights for different context factors"""
        
        # Memory usage influence
        memories_used = interaction.get("memories_used", 0)
        self.context_weights["memory_importance"] = (
            self.context_weights.get("memory_importance", 0.5) * 0.9 +
            min(1.0, memories_used / 5.0) * 0.1
        )
        
        # Knowledge usage influence
        knowledge_used = interaction.get("knowledge_used", 0)
        self.context_weights["knowledge_importance"] = (
            self.context_weights.get("knowledge_importance", 0.5) * 0.9 +
            min(1.0, knowledge_used / 3.0) * 0.1
        )
        
        # Emotional state influence
        emotional_state = interaction.get("emotional_analysis", {}).get("dominant_emotion", "neutral")
        self.context_weights[f"emotion_{emotional_state}"] = (
            self.context_weights.get(f"emotion_{emotional_state}", 0.5) * 0.9 +
            0.1
        )
        
    def _track_performance(self, interaction: Dict[str, Any]) -> None:
        """Track performance metrics"""
        
        # Response time
        response_time = interaction.get("response_time", 0)
        self.performance_metrics["response_time"].append(response_time)
        
        # Keep only recent metrics
        if len(self.performance_metrics["response_time"]) > 100:
            self.performance_metrics["response_time"] = self.performance_metrics["response_time"][-100:]
            
        # Confidence scores
        confidence = interaction.get("confidence", 0.5)
        self.performance_metrics["confidence"].append(confidence)
        
        if len(self.performance_metrics["confidence"]) > 100:
            self.performance_metrics["confidence"] = self.performance_metrics["confidence"][-100:]
            
    def _optimize_learning(self) -> None:
        """Optimize learning parameters based on collected data"""
        
        if len(self.interaction_history) < 10:
            return
            
        logger.info("Optimizing learning parameters")
        
        # Analyze successful patterns
        self._analyze_success_patterns()
        
        # Prune ineffective patterns
        self._prune_ineffective_patterns()
        
        # Update adaptation strategies
        self._update_adaptation_strategies()
        
        self.last_optimization = datetime.now(timezone.utc)
        self.adaptation_count += 1
        
    def _analyze_success_patterns(self) -> None:
        """Analyze which patterns lead to successful outcomes"""
        
        # Simple heuristic: patterns that appear frequently are successful
        pattern_counts = defaultdict(int)
        
        for interaction in self.interaction_history:
            input_text = interaction.get("input", "").lower()
            input_words = input_text.split()
            
            if len(input_words) > 0:
                pattern_key = " ".join(input_words[:3])
                pattern_counts[pattern_key] += 1
                
        # Update success patterns
        total_interactions = len(self.interaction_history)
        for pattern, count in pattern_counts.items():
            success_rate = count / total_interactions
            self.success_patterns[pattern] = success_rate
            
    def _prune_ineffective_patterns(self) -> None:
        """Remove patterns that don't lead to good outcomes"""
        
        patterns_to_remove = []
        
        for pattern, success_rate in self.success_patterns.items():
            if success_rate < 0.1:  # Low success threshold
                patterns_to_remove.append(pattern)
                
        for pattern in patterns_to_remove:
            if pattern in self.response_patterns:
                del self.response_patterns[pattern]
            if pattern in self.success_patterns:
                del self.success_patterns[pattern]
                
        logger.info(f"Pruned {len(patterns_to_remove)} ineffective patterns")
        
    def _update_adaptation_strategies(self) -> None:
        """Update adaptation strategies based on performance"""
        
        # Adjust exploration vs exploitation
        if self.performance_metrics["confidence"]:
            avg_confidence = np.mean(self.performance_metrics["confidence"][-20:])
            
            if avg_confidence < 0.6:
                # Increase exploration if confidence is low
                self.config.exploration_rate = min(0.3, self.config.exploration_rate * 1.1)
            elif avg_confidence > 0.8:
                # Decrease exploration if confidence is high
                self.config.exploration_rate = max(0.05, self.config.exploration_rate * 0.9)
                
    def generate_response(self, context: Dict[str, Any]) -> str:
        """Generate response based on learned patterns"""
        
        input_text = context.get("processed_input", {}).get("text", "").lower()
        
        # Try to match existing patterns
        input_words = input_text.split()
        
        if len(input_words) > 0:
            pattern_key = " ".join(input_words[:3])
            
            if pattern_key in self.response_patterns:
                responses = self.response_patterns[pattern_key]
                
                if responses:
                    # Choose response based on exploration rate
                    if np.random.random() < self.config.exploration_rate:
                        # Explore: random response
                        return np.random.choice(responses)
                    else:
                        # Exploit: most recent successful response
                        return responses[-1]
                        
        # Generate contextual response if no pattern matches
        return self._generate_contextual_response(context)
        
    def _generate_contextual_response(self, context: Dict[str, Any]) -> str:
        """Generate response based on context when no pattern matches"""
        
        emotional_state = context.get("emotional_state", "neutral")
        memories = context.get("memories", [])
        knowledge = context.get("knowledge", [])
        
        # Base response templates
        responses = {
            "neutral": [
                "I understand. Let me help you with that.",
                "That's interesting. Based on what I know...",
                "I can assist you with this."
            ],
            "happy": [
                "That's wonderful! I'm happy to help.",
                "Great! Let me share what I know about this.",
                "I'm excited to assist you with this!"
            ],
            "curious": [
                "That's fascinating! Let me explore this topic.",
                "Interesting question! Let me think about this.",
                "I'm curious about this too. Let me help you explore."
            ],
            "confused": [
                "I'm not sure I understand completely. Could you clarify?",
                "Let me think about this differently.",
                "I need more information to help you properly."
            ]
        }
        
        # Choose base response
        base_responses = responses.get(emotional_state, responses["neutral"])
        base_response = np.random.choice(base_responses)
        
        # Add memory/knowledge context
        if memories:
            base_response += " I recall some relevant experiences that might help."
        elif knowledge:
            base_response += " Based on my knowledge..."
            
        return base_response
        
    def process_feedback(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Process feedback for learning"""

        processed_feedback = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "feedback_type": feedback.get("type", "rating"),
            "rating": feedback.get("rating", 0.5),
            "comment": feedback.get("comment", ""),
            "interaction_id": feedback.get("interaction_id", ""),
            "aspects": feedback.get("aspects", {})
        }
        
        # Add to feedback history
        self.feedback_history.append(processed_feedback)
        
        # Extract learning signals
        self._extract_feedback_signals(processed_feedback)
        
        return processed_feedback
        
    def _extract_feedback_signals(self, feedback: Dict[str, Any]) -> None:
        """Extract learning signals from feedback"""
        
        rating = feedback.get("rating", 0.5)
        
        # Update performance metrics
        self.performance_metrics["user_satisfaction"].append(rating)
        
        if len(self.performance_metrics["user_satisfaction"]) > 100:
            self.performance_metrics["user_satisfaction"] = self.performance_metrics["user_satisfaction"][-100:]
            
        # Adjust learning parameters based on feedback
        if rating < 0.3:
            # Poor feedback - increase exploration
            self.config.exploration_rate = min(0.4, self.config.exploration_rate * 1.2)
        elif rating > 0.8:
            # Good feedback - decrease exploration
            self.config.exploration_rate = max(0.05, self.config.exploration_rate * 0.8)
            
    def update_from_feedback(self, processed_feedback: Dict[str, Any]) -> None:
        """Update learning model based on processed feedback"""
        
        # Find related interaction if available
        interaction_id = processed_feedback.get("interaction_id")
        
        if interaction_id:
            # Find the interaction and update its success metrics
            for interaction in self.interaction_history:
                if interaction.get("id") == interaction_id:
                    interaction["feedback_rating"] = processed_feedback.get("rating")
                    interaction["feedback_processed"] = True
                    break
                    
        # Update success patterns based on feedback
        self._update_patterns_from_feedback(processed_feedback)
        
        self._save_learning_data()
        
    def _update_patterns_from_feedback(self, feedback: Dict[str, Any]) -> None:
        """Update pattern success rates based on feedback"""
        
        rating = feedback.get("rating", 0.5)
        interaction_id = feedback.get("interaction_id")
        
        if not interaction_id:
            return
            
        # Find the interaction and extract its pattern
        for interaction in self.interaction_history:
            if interaction.get("id") == interaction_id:
                input_text = interaction.get("input", "").lower()
                input_words = input_text.split()
                
                if len(input_words) > 0:
                    pattern_key = " ".join(input_words[:3])
                    
                    # Update success pattern with feedback
                    current_success = self.success_patterns.get(pattern_key, 0.5)
                    self.success_patterns[pattern_key] = (
                        current_success * 0.8 + rating * 0.2
                    )
                    
                break
                
    def optimize_model(self) -> None:
        """Optimize the learning model"""
        
        if len(self.interaction_history) < 50:
            return
            
        logger.info("Optimizing learning model")
        
        # Calculate current performance
        recent_performance = self._calculate_recent_performance()
        
        # Adjust learning rate based on performance
        if recent_performance < 0.6:
            self.config.learning_rate = min(0.01, self.config.learning_rate * 1.1)
        elif recent_performance > 0.8:
            self.config.learning_rate = max(0.0001, self.config.learning_rate * 0.9)
            
        # Perform pattern optimization
        self._optimize_response_patterns()
        
        self._save_learning_data()
        
    def _calculate_recent_performance(self) -> float:
        """Calculate recent performance metrics"""
        
        if not self.performance_metrics["user_satisfaction"]:
            return 0.5
            
        # Get last 20 satisfaction ratings
        recent_ratings = self.performance_metrics["user_satisfaction"][-20:]
        
        return np.mean(recent_ratings) if recent_ratings else 0.5
        
    def _optimize_response_patterns(self) -> None:
        """Optimize response patterns for better performance"""
        
        # Remove patterns with consistently low performance
        patterns_to_remove = []
        
        for pattern, success_rate in self.success_patterns.items():
            if success_rate < 0.2 and pattern in self.response_patterns:
                patterns_to_remove.append(pattern)
                
        for pattern in patterns_to_remove:
            del self.response_patterns[pattern]
            del self.success_patterns[pattern]
            
        logger.info(f"Optimized response patterns, removed {len(patterns_to_remove)} low-performing patterns")
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get learning statistics"""

        current_time = datetime.now(timezone.utc)
        uptime = current_time - self.last_optimization
        
        return {
            "learning_episodes": self.learning_episodes,
            "adaptation_count": self.adaptation_count,
            "interaction_history_size": len(self.interaction_history),
            "feedback_history_size": len(self.feedback_history),
            "response_patterns_count": len(self.response_patterns),
            "success_patterns_count": len(self.success_patterns),
            "hours_since_optimization": uptime.total_seconds() / 3600,
            "current_learning_rate": self.config.learning_rate,
            "current_exploration_rate": self.config.exploration_rate,
            "recent_performance": self._calculate_recent_performance(),
            "performance_metrics": {
                metric: {
                    "count": len(values),
                    "average": np.mean(values) if values else 0.0,
                    "recent_average": np.mean(values[-10:]) if len(values) >= 10 else np.mean(values) if values else 0.0
                }
                for metric, values in self.performance_metrics.items()
            }
        }
        
    def export_learning_data(self, filepath: str) -> None:
        """Export learning data to file"""

        export_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "config": self.config.dict(),
            "interaction_history": list(self.interaction_history),
            "feedback_history": list(self.feedback_history),
            "performance_metrics": dict(self.performance_metrics),
            "response_patterns": dict(self.response_patterns),
            "context_weights": dict(self.context_weights),
            "success_patterns": dict(self.success_patterns),
            "statistics": self.get_statistics()
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
            
        logger.info(f"Learning data exported to {filepath}")
        
    def reset_learning(self) -> None:
        """Reset learning data"""
        
        logger.warning("Resetting learning data")
        
        self.interaction_history.clear()
        self.feedback_history.clear()
        self.performance_metrics.clear()
        self.response_patterns.clear()
        self.context_weights.clear()
        self.success_patterns.clear()
        
        self.learning_episodes = 0
        self.last_optimization = datetime.now(timezone.utc)
        self.adaptation_count = 0
        
        self._save_learning_data()
        
        logger.info("Learning data reset completed")
