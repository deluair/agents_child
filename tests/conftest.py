"""
Pytest configuration and fixtures
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from agent.core.config import AgentConfig, MemoryConfig, LearningConfig, KnowledgeConfig
from agent.core.agent import AdvancedAgent


@pytest.fixture
def temp_memory_path():
    """Create a temporary directory for memory storage"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def test_config(temp_memory_path):
    """Create a test configuration"""
    return AgentConfig(
        name="TestAgent",
        memory_path=temp_memory_path,
        memory=MemoryConfig(
            short_term_capacity=50,
            episodic_capacity=100,
            semantic_capacity=200
        ),
        learning=LearningConfig(
            enabled=True,
            update_frequency=10
        ),
        knowledge=KnowledgeConfig(
            max_entities=1000,
            max_relations=2000
        )
    )


@pytest.fixture
def test_agent(test_config):
    """Create a test agent instance"""
    agent = AdvancedAgent(config=test_config)
    yield agent
    # Cleanup
    try:
        agent.shutdown()
    except:
        pass


@pytest.fixture
def sample_interaction():
    """Sample interaction data for testing"""
    return {
        "input": "Hello, how are you?",
        "response": "I'm doing well, thank you!",
        "sentiment": "positive",
        "importance": 0.6
    }


@pytest.fixture
def sample_feedback():
    """Sample feedback data for testing"""
    return {
        "type": "rating",
        "rating": 0.8,
        "comment": "Great response!",
        "aspects": {"helpfulness": 0.9, "clarity": 0.8}
    }
