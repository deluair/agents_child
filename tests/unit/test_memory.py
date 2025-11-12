"""
Unit tests for memory module
"""

import pytest
from datetime import datetime, timezone

from agent.core.config import MemoryConfig
from agent.memory.short_term_memory import ShortTermMemory, Memory
from agent.memory.episodic_memory import EpisodicMemory
from agent.memory.semantic_memory import SemanticMemory
from agent.memory.memory_consolidation import MemoryConsolidation


class TestMemory:
    """Test individual Memory class"""

    def test_memory_creation(self):
        """Test creating a memory"""
        mem = Memory("Test content", importance=0.7)
        assert mem.content == "Test content"
        assert mem.importance == 0.7
        assert mem.access_count == 0

    def test_memory_validation(self):
        """Test memory validation"""
        with pytest.raises(ValueError):
            Memory("Test", importance=1.5)  # Invalid importance

        with pytest.raises(ValueError):
            Memory("Test", importance=-0.1)  # Invalid importance

    def test_memory_access(self):
        """Test memory access tracking"""
        mem = Memory("Test")
        initial_time = mem.last_accessed
        mem.access()
        assert mem.access_count == 1
        assert mem.last_accessed >= initial_time

    def test_memory_decay(self):
        """Test memory importance decay"""
        mem = Memory("Test", importance=1.0)
        mem.decay_importance(0.9)
        assert mem.importance == 0.9

    def test_memory_serialization(self):
        """Test memory to/from dict"""
        mem = Memory("Test content", importance=0.8, metadata={"key": "value"})
        mem_dict = mem.to_dict()

        assert mem_dict["content"] == "Test content"
        assert mem_dict["importance"] == 0.8
        assert mem_dict["metadata"] == {"key": "value"}

        restored = Memory.from_dict(mem_dict)
        assert restored.content == mem.content
        assert restored.importance == mem.importance


class TestShortTermMemory:
    """Test short-term memory"""

    def test_stm_creation(self):
        """Test creating short-term memory"""
        config = MemoryConfig(short_term_capacity=10)
        stm = ShortTermMemory(config)
        assert stm.capacity == 10
        assert len(stm.memories) == 0

    def test_add_memory(self):
        """Test adding memories"""
        config = MemoryConfig(short_term_capacity=5)
        stm = ShortTermMemory(config)

        mem_id = stm.add_memory("Test 1", importance=0.8)
        assert mem_id is not None
        assert len(stm.memories) == 1

    def test_capacity_limit(self):
        """Test capacity limit enforcement"""
        config = MemoryConfig(short_term_capacity=3)
        stm = ShortTermMemory(config)

        for i in range(5):
            stm.add_memory(f"Memory {i}", importance=0.5)

        assert len(stm.memories) == 3  # Should not exceed capacity

    def test_retrieve_memory(self):
        """Test memory retrieval"""
        config = MemoryConfig()
        stm = ShortTermMemory(config)

        stm.add_memory("Python programming", importance=0.9)
        stm.add_memory("Java development", importance=0.7)
        stm.add_memory("Machine learning", importance=0.8)

        results = stm.retrieve_memory("programming", limit=5)
        assert len(results) > 0
        assert results[0]["content"] == "Python programming"

    def test_decay_and_forget(self):
        """Test decay and forgetting"""
        config = MemoryConfig()
        stm = ShortTermMemory(config)

        stm.add_memory("Test 1", importance=0.9)
        stm.add_memory("Test 2", importance=0.1)

        stm.decay_memories()
        stm.forget_low_importance(threshold=0.2)

        assert len(stm.memories) == 1  # Low importance forgotten

    def test_validation(self):
        """Test input validation"""
        config = MemoryConfig()
        stm = ShortTermMemory(config)

        with pytest.raises(ValueError):
            stm.add_memory(None)  # None content

        with pytest.raises(ValueError):
            stm.retrieve_memory("test", limit=-1)  # Invalid limit


class TestEpisodicMemory:
    """Test episodic memory"""

    def test_episodic_creation(self):
        """Test creating episodic memory"""
        config = MemoryConfig(episodic_capacity=100)
        em = EpisodicMemory(config)
        assert em.capacity == 100

    def test_add_episode(self):
        """Test adding episodes"""
        config = MemoryConfig()
        em = EpisodicMemory(config)

        ep_id = em.add_memory(
            "Had a conversation about AI",
            importance=0.8,
            metadata={"context": "discussion"}
        )

        assert ep_id is not None
        assert len(em.episodes) == 1

    def test_retrieve_episodes(self):
        """Test episode retrieval"""
        config = MemoryConfig()
        em = EpisodicMemory(config)

        em.add_memory("Learned Python", importance=0.9)
        em.add_memory("Studied algorithms", importance=0.8)

        results = em.retrieve_memory("Python", limit=5)
        assert len(results) > 0

    def test_recent_episodes(self):
        """Test getting recent episodes"""
        config = MemoryConfig()
        em = EpisodicMemory(config)

        for i in range(5):
            em.add_memory(f"Episode {i}", importance=0.5)

        recent = em.get_recent_episodes(count=3)
        assert len(recent) == 3


class TestSemanticMemory:
    """Test semantic memory"""

    def test_semantic_creation(self):
        """Test creating semantic memory"""
        config = MemoryConfig(semantic_capacity=500)
        sm = SemanticMemory(config)
        assert sm.capacity == 500

    def test_add_concept(self):
        """Test adding concepts"""
        config = MemoryConfig()
        sm = SemanticMemory(config)

        concept_id = sm.add_memory(
            {"name": "Python", "definition": "A programming language"},
            importance=0.9,
            concept_type="language"
        )

        assert concept_id is not None
        assert len(sm.concepts) == 1

    def test_add_fact(self):
        """Test adding facts"""
        config = MemoryConfig()
        sm = SemanticMemory(config)

        fact_id = sm.add_memory(
            {"statement": "Python is dynamically typed"},
            importance=0.8,
            concept_type="fact"
        )

        assert fact_id is not None
        assert len(sm.facts) == 1

    def test_retrieve_concepts(self):
        """Test concept retrieval"""
        config = MemoryConfig()
        sm = SemanticMemory(config)

        sm.add_memory(
            {"name": "Python", "type": "language"},
            importance=0.9
        )

        results = sm.retrieve_memory("Python", limit=5)
        assert len(results) > 0

    def test_concept_relations(self):
        """Test concept relations"""
        config = MemoryConfig()
        sm = SemanticMemory(config)

        id1 = sm.add_memory({"name": "Python"}, importance=0.9)
        id2 = sm.add_memory({"name": "Programming"}, importance=0.9)

        sm.add_relation(id1, id2)

        related = sm.get_related_concepts(id1)
        assert len(related) > 0


class TestMemoryConsolidation:
    """Test memory consolidation"""

    def test_consolidation_creation(self):
        """Test creating consolidation system"""
        config = MemoryConfig()
        consolidation = MemoryConsolidation(config)
        assert consolidation.consolidation_count == 0

    def test_should_run(self):
        """Test consolidation schedule"""
        config = MemoryConfig(consolidation_interval=1)
        consolidation = MemoryConsolidation(config)

        # Should run initially
        assert consolidation.should_run_consolidation()

    def test_consolidate_memories(self):
        """Test memory consolidation process"""
        config = MemoryConfig()
        stm = ShortTermMemory(config)
        em = EpisodicMemory(config)
        sm = SemanticMemory(config)
        consolidation = MemoryConsolidation(config)

        # Add important memories
        stm.add_memory("Python is a language", importance=0.9)
        stm.add_memory("Had a good conversation", importance=0.8)

        stats = consolidation.consolidate(stm, em, sm)

        assert stats["episodic"] + stats["semantic"] > 0
