"""
Configuration management for the AI agent
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

load_dotenv()


class MemoryConfig(BaseModel):
    """Configuration for memory systems"""
    short_term_capacity: int = Field(default=100, description="Number of items in short-term memory")
    episodic_capacity: int = Field(default=10000, description="Number of episodic memories")
    semantic_capacity: int = Field(default=50000, description="Number of semantic memories")
    consolidation_threshold: float = Field(default=0.8, description="Threshold for memory consolidation")
    forgetting_rate: float = Field(default=0.001, description="Rate of memory decay")
    embedding_dim: int = Field(default=384, description="Dimension for embeddings")


class LearningConfig(BaseModel):
    """Configuration for learning systems"""
    learning_rate: float = Field(default=0.001, description="Learning rate for neural networks")
    batch_size: int = Field(default=32, description="Batch size for training")
    update_frequency: int = Field(default=10, description="Steps between model updates")
    exploration_rate: float = Field(default=0.1, description="Exploration vs exploitation")
    adaptation_threshold: float = Field(default=0.7, description="Threshold for behavior adaptation")


class KnowledgeConfig(BaseModel):
    """Configuration for knowledge graph"""
    max_entities: int = Field(default=100000, description="Maximum number of entities")
    max_relations: int = Field(default=500000, description="Maximum number of relations")
    similarity_threshold: float = Field(default=0.8, description="Threshold for entity similarity")
    reasoning_depth: int = Field(default=3, description="Maximum depth for reasoning")


class AgentConfig(BaseModel):
    """Main configuration for the AI agent"""
    name: str = Field(default="Cognita", description="Agent name")
    version: str = Field(default="0.1.0", description="Agent version")
    memory_path: str = Field(default="./memory", description="Path to store memory data")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Sub-configurations
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    learning: LearningConfig = Field(default_factory=LearningConfig)
    knowledge: KnowledgeConfig = Field(default_factory=KnowledgeConfig)
    
    # Model configurations
    embedding_model: str = Field(default="all-MiniLM-L6-v2", description="Sentence transformer model")
    language_model: str = Field(default="distilbert-base-uncased", description="Language model for processing")
    
    class Config:
        env_prefix = "AGENT_"
        case_sensitive = False


def load_config(config_path: Optional[str] = None) -> AgentConfig:
    """Load configuration from file or environment variables"""
    if config_path and os.path.exists(config_path):
        import json
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        return AgentConfig(**config_data)
    
    return AgentConfig()
