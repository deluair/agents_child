"""
Basic test for the Advanced AI Agent without heavy dependencies
"""

import sys
import os

# Add the parent directory to the path so we can import the agent
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """Test basic imports without heavy dependencies"""
    
    print("🧪 Testing Basic Imports")
    print("=" * 40)
    
    try:
        # Test core config
        from agent.core.config import AgentConfig, MemoryConfig, LearningConfig
        print("✓ Configuration modules imported successfully")
        
        # Test core state
        from agent.core.state import AgentState, AgentMode, EmotionalState
        print("✓ State management modules imported successfully")
        
        # Test memory modules (without dependencies)
        from agent.memory.memory_manager import MemoryManager
        print("✓ Memory management modules imported successfully")
        
        # Test learning scheduler
        from agent.learning.learning_scheduler import LearningScheduler
        print("✓ Learning scheduler imported successfully")
        
        # Test knowledge graph (without networkx for now)
        try:
            from agent.knowledge.knowledge_graph import KnowledgeGraph
            print("✓ Knowledge graph imported successfully")
        except ImportError as e:
            print(f"⚠ Knowledge graph import failed: {e}")
            
        print("\n🎉 Basic imports test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import test failed: {e}")
        return False


def test_basic_functionality():
    """Test basic functionality without heavy dependencies"""
    
    print("\n🧪 Testing Basic Functionality")
    print("=" * 40)
    
    try:
        from agent.core.config import AgentConfig
        from agent.core.state import AgentState, AgentMode
        from agent.learning.learning_scheduler import LearningScheduler
        
        # Test configuration
        config = AgentConfig(name="TestAgent")
        print(f"✓ Created agent config: {config.name}")
        
        # Test state management
        state = AgentState()
        state.update_mode(AgentMode.PROCESSING)
        print(f"✓ State management working: {state.mode}")
        
        # Test learning scheduler
        scheduler = LearningScheduler()
        print(f"✓ Learning scheduler created with {len(scheduler.tasks)} tasks")
        
        print("\n🎉 Basic functionality test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Functionality test failed: {e}")
        return False


def test_memory_system():
    """Test memory system without external dependencies"""
    
    print("\n🧪 Testing Memory System")
    print("=" * 40)
    
    try:
        from agent.core.config import MemoryConfig
        from agent.memory.short_term_memory import ShortTermMemory
        from agent.memory.episodic_memory import EpisodicMemory
        from agent.memory.semantic_memory import SemanticMemory
        
        # Create memory configs
        memory_config = MemoryConfig()
        
        # Test short-term memory
        stm = ShortTermMemory(memory_config)
        stm.add_memory("Test memory 1", importance=0.8)
        stm.add_memory("Test memory 2", importance=0.6)
        retrieved = stm.retrieve_memory("test", limit=2)
        print(f"✓ Short-term memory: {len(retrieved)} memories retrieved")
        
        # Test episodic memory
        em = EpisodicMemory(memory_config)
        em.add_memory("Test episode", importance=0.7, metadata={"type": "test"})
        retrieved = em.retrieve_memory("episode", limit=1)
        print(f"✓ Episodic memory: {len(retrieved)} memories retrieved")
        
        # Test semantic memory
        sm = SemanticMemory(memory_config)
        sm.add_memory({"name": "Test Concept", "definition": "A test concept"}, importance=0.9)
        retrieved = sm.retrieve_memory("test", limit=1)
        print(f"✓ Semantic memory: {len(retrieved)} memories retrieved")
        
        print("\n🎉 Memory system test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Memory system test failed: {e}")
        return False


def main():
    """Run all basic tests"""
    
    print("🚀 Advanced AI Agent - Basic Tests")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Basic Functionality", test_basic_functionality),
        ("Memory System", test_memory_system)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            
    print(f"\n{'='*50}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed!")
        print("The core agent architecture is working correctly.")
        print("Some advanced features may require additional dependencies.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
        
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
