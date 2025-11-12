"""
Agent state management
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from enum import Enum
import json


class AgentMode(Enum):
    """Different operational modes of the agent"""
    IDLE = "idle"
    PROCESSING = "processing"
    LEARNING = "learning"
    REASONING = "reasoning"
    CONVERSING = "conversing"


class EmotionalState(Enum):
    """Emotional states for emotional intelligence"""
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    HAPPY = "happy"
    CURIOUS = "curious"
    CONFUSED = "confused"
    FRUSTRATED = "frustrated"
    ENGAGED = "engaged"
    NEGATIVE = "negative"


class AgentState:
    """Manages the current state of the agent"""
    
    def __init__(self):
        self.mode = AgentMode.IDLE
        self.emotional_state = EmotionalState.NEUTRAL
        self.context: Dict[str, Any] = {}
        self.current_task: Optional[str] = None
        self.interaction_history: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, float] = {}
        self.last_updated = datetime.now(timezone.utc)
        
    def update_mode(self, new_mode: AgentMode) -> None:
        """Update the agent's operational mode"""
        self.mode = new_mode
        self.last_updated = datetime.now(timezone.utc)
        
    def update_emotional_state(self, new_state: EmotionalState) -> None:
        """Update the agent's emotional state"""
        self.emotional_state = new_state
        self.last_updated = datetime.now(timezone.utc)
        
    def add_context(self, key: str, value: Any) -> None:
        """Add context information"""
        self.context[key] = value
        self.last_updated = datetime.now(timezone.utc)
        
    def set_current_task(self, task: str) -> None:
        """Set the current task the agent is working on"""
        self.current_task = task
        self.last_updated = datetime.now(timezone.utc)
        
    def add_interaction(self, interaction: Dict[str, Any]) -> None:
        """Add an interaction to the history"""
        interaction['timestamp'] = datetime.now(timezone.utc).isoformat()
        self.interaction_history.append(interaction)
        
        # Keep only last 100 interactions in active memory
        if len(self.interaction_history) > 100:
            self.interaction_history = self.interaction_history[-100:]
            
        self.last_updated = datetime.now(timezone.utc)
        
    def update_performance_metric(self, metric: str, value: float) -> None:
        """Update a performance metric"""
        self.performance_metrics[metric] = value
        self.last_updated = datetime.now(timezone.utc)
        
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get all performance metrics"""
        return self.performance_metrics.copy()
        
    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of current context"""
        return {
            "mode": self.mode.value,
            "emotional_state": self.emotional_state.value,
            "current_task": self.current_task,
            "context_keys": list(self.context.keys()),
            "interaction_count": len(self.interaction_history),
            "performance_metrics": self.performance_metrics,
            "last_updated": self.last_updated.isoformat()
        }
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization"""
        return {
            "mode": self.mode.value,
            "emotional_state": self.emotional_state.value,
            "context": self.context,
            "current_task": self.current_task,
            "interaction_history": self.interaction_history,
            "performance_metrics": self.performance_metrics,
            "last_updated": self.last_updated.isoformat()
        }
        
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load state from dictionary"""
        self.mode = AgentMode(data.get("mode", "idle"))
        self.emotional_state = EmotionalState(data.get("emotional_state", "neutral"))
        self.context = data.get("context", {})
        self.current_task = data.get("current_task")
        self.interaction_history = data.get("interaction_history", [])
        self.performance_metrics = data.get("performance_metrics", {})
        
        if "last_updated" in data:
            self.last_updated = datetime.fromisoformat(data["last_updated"])
        else:
            self.last_updated = datetime.now(timezone.utc)
