"""
Basic usage example for the Advanced AI Agent
"""

import sys
import os

# Add the parent directory to the path so we can import the agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import AdvancedAgent
from agent.core.config import AgentConfig
import time


def main():
    """Demonstrate basic agent usage"""
    
    print("🤖 Advanced AI Agent - Basic Usage Example")
    print("=" * 50)
    
    # Create custom configuration
    config = AgentConfig(
        name="DemoAgent",
        version="1.0.0",
        memory_path="./demo_memory"
    )
    
    # Initialize the agent
    print("\n📦 Initializing agent...")
    agent = AdvancedAgent(config)
    
    try:
        # Example 1: Basic conversation
        print("\n💬 Example 1: Basic Conversation")
        print("-" * 30)
        
        inputs = [
            "Hello, my name is Alice. I'm interested in machine learning.",
            "Can you explain what neural networks are?",
            "That's interesting! How do they learn?",
            "Thank you for the explanation."
        ]
        
        for user_input in inputs:
            print(f"\n👤 User: {user_input}")
            
            # Process the input
            response = agent.process(user_input)
            
            print(f"🤖 {config.name}: {response['response']}")
            print(f"   Confidence: {response['confidence']:.2f}")
            
        # Example 2: Adding knowledge
        print("\n🧠 Example 2: Adding Knowledge")
        print("-" * 30)
        
        knowledge_items = [
            {
                "type": "concept",
                "name": "Machine Learning",
                "definition": "A subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.",
                "category": "technology",
                "importance": 0.9
            },
            {
                "type": "fact",
                "statement": "Python is one of the most popular programming languages for machine learning.",
                "confidence": 0.95,
                "importance": 0.8
            }
        ]
        
        for knowledge in knowledge_items:
            entity_id = agent.add_knowledge(knowledge)
            print(f"✓ Added knowledge: {knowledge['name'] if 'name' in knowledge else knowledge['statement'][:50]}...")
            
        # Example 3: Querying memory
        print("\n🔍 Example 3: Querying Memory")
        print("-" * 30)
        
        queries = ["machine learning", "neural networks", "Alice"]
        
        for query in queries:
            print(f"\n🔎 Query: '{query}'")
            memories = agent.query_memory(query, limit=3)
            
            if memories:
                for i, memory in enumerate(memories, 1):
                    content = str(memory.get("content", ""))[:100]
                    print(f"   {i}. [{memory.get('type', 'unknown')}] {content}...")
                    print(f"      Relevance: {memory.get('relevance', 0):.2f}")
            else:
                print("   No memories found.")
                
        # Example 4: Learning from feedback
        print("\n📚 Example 4: Learning from Feedback")
        print("-" * 30)
        
        feedback = {
            "type": "rating",
            "rating": 0.8,
            "comment": "The explanation was very clear and helpful!",
            "aspects": ["clarity", "helpfulness"]
        }
        
        agent.learn(feedback)
        print("✓ Feedback processed and learned from.")
        
        # Example 5: Getting statistics
        print("\n📊 Example 5: Agent Statistics")
        print("-" * 30)
        
        stats = agent.get_statistics()
        
        print(f"Agent Name: {stats['agent_info']['name']}")
        print(f"Total Interactions: {stats['agent_info']['total_interactions']}")
        print(f"Current Mode: {stats['state']['mode']}")
        print(f"Memory Usage:")
        
        for memory_type, memory_stats in stats['memory'].items():
            if memory_type != 'total_consolidations':
                utilization = memory_stats['utilization'] * 100
                print(f"  - {memory_type}: {memory_stats['count']}/{memory_stats['capacity']} ({utilization:.1f}%)")
                
        print(f"Learning Episodes: {stats['learning']['learning_episodes']}")
        print(f"Knowledge Entities: {stats['knowledge']['total_entities']}")
        
        # Example 6: Emotional intelligence
        print("\n💭 Example 6: Emotional Intelligence")
        print("-" * 30)
        
        emotional_inputs = [
            "I'm so excited about learning AI!",
            "This is confusing me a bit.",
            "That's fantastic news!"
        ]
        
        for user_input in emotional_inputs:
            print(f"\n👤 User: {user_input}")
            response = agent.process(user_input)
            print(f"🤖 {config.name}: {response['response']}")
            print(f"   Emotional State: {response['emotional_state']}")
            
        print("\n✅ Basic usage example completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
    finally:
        # Properly shutdown the agent
        print("\n🔄 Shutting down agent...")
        agent.shutdown()
        print("✓ Agent shutdown complete.")


if __name__ == "__main__":
    main()
