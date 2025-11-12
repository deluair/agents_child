"""
Advanced AI Agent with Continuous Learning and Memory
"""

from .core.agent import AdvancedAgent
from .memory.memory_manager import MemoryManager
from .learning.continuous_learner import ContinuousLearner
from .knowledge.knowledge_graph import KnowledgeGraph

__version__ = "0.1.0"
__all__ = ["AdvancedAgent", "MemoryManager", "ContinuousLearner", "KnowledgeGraph"]
