"""
Advanced features example for the Advanced AI Agent
"""

import sys
import os
import json
from datetime import datetime

# Add the parent directory to the path so we can import the agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import AdvancedAgent
from agent.core.config import AgentConfig
from agent.memory.memory_manager import MemoryManager
from agent.knowledge.knowledge_graph import KnowledgeGraph
from agent.learning.continuous_learner import ContinuousLearner


def demonstrate_memory_systems():
    """Demonstrate the multi-layered memory system"""
    
    print("🧠 Advanced Memory Systems Demonstration")
    print("=" * 50)
    
    config = AgentConfig(
        name="MemoryDemo",
        memory_path="./memory_demo"
    )
    
    agent = AdvancedAgent(config)
    
    try:
        # Short-term memory
        print("\n📝 Short-term Memory:")
        print("-" * 25)
        
        short_term_memories = [
            "User asked about Python programming",
            "User mentioned they are a student",
            "User wants to learn about data structures",
            "User expressed interest in algorithms"
        ]
        
        for memory in short_term_memories:
            memory_id = agent.memory.add_memory(
                memory, 
                "short_term", 
                importance=0.6,
                metadata={"source": "conversation"}
            )
            print(f"✓ Added to short-term: {memory[:40]}...")
            
        # Episodic memory
        print("\n📚 Episodic Memory:")
        print("-" * 25)
        
        episodic_memories = [
            {
                "content": "User had their first successful machine learning training run",
                "importance": 0.8,
                "metadata": {
                    "entities": ["User", "machine learning"],
                    "emotions": ["happy", "excited"],
                    "location": "online_session",
                    "participants": ["User", "AI Assistant"]
                }
            },
            {
                "content": "User struggled with gradient descent concepts",
                "importance": 0.7,
                "metadata": {
                    "entities": ["User", "gradient descent"],
                    "emotions": ["confused", "frustrated"],
                    "location": "online_session",
                    "participants": ["User", "AI Assistant"]
                }
            }
        ]
        
        for memory in episodic_memories:
            memory_id = agent.memory.add_memory(
                memory["content"],
                "episodic",
                importance=memory["importance"],
                metadata=memory["metadata"]
            )
            print(f"✓ Added episodic memory: {memory['content'][:40]}...")
            
        # Semantic memory
        print("\n🎯 Semantic Memory:")
        print("-" * 25)
        
        semantic_memories = [
            {
                "content": {
                    "name": "Gradient Descent",
                    "definition": "An optimization algorithm used to minimize the loss function in machine learning models",
                    "category": "algorithm",
                    "importance": 0.9,
                    "keywords": ["optimization", "machine learning", "loss function"]
                },
                "importance": 0.9
            },
            {
                "content": {
                    "name": "Neural Network",
                    "definition": "A computing system inspired by biological neural networks that constitute animal brains",
                    "category": "architecture",
                    "importance": 0.9,
                    "keywords": ["deep learning", "neurons", "layers"]
                },
                "importance": 0.9
            }
        ]
        
        for memory in semantic_memories:
            memory_id = agent.memory.add_memory(
                memory["content"],
                "semantic",
                importance=memory["importance"]
            )
            print(f"✓ Added semantic concept: {memory['content']['name']}")
            
        # Memory consolidation
        print("\n🔄 Memory Consolidation:")
        print("-" * 25)
        
        print("Performing memory consolidation...")
        agent.memory.consolidate_memories()
        print("✓ Memory consolidation completed")
        
        # Memory statistics
        print("\n📊 Memory Statistics:")
        print("-" * 25)
        
        memory_stats = agent.memory.get_memory_stats()
        for memory_type, stats in memory_stats.items():
            if memory_type != "total_consolidations":
                utilization = stats["utilization"] * 100
                print(f"{memory_type.replace('_', ' ').title()}: {stats['count']}/{stats['capacity']} ({utilization:.1f}%)")
                
        print(f"Total Consolidations: {memory_stats['total_consolidations']}")
        
    finally:
        agent.shutdown()


def demonstrate_knowledge_graph():
    """Demonstrate the knowledge graph capabilities"""
    
    print("\n🕸️  Knowledge Graph Demonstration")
    print("=" * 50)
    
    config = AgentConfig(
        name="KnowledgeDemo",
        memory_path="./knowledge_demo"
    )
    
    agent = AdvancedAgent(config)
    
    try:
        # Create entities
        print("\n🏷️  Creating Entities:")
        print("-" * 25)
        
        entities = [
            {
                "name": "Machine Learning",
                "type": "field",
                "description": "A subset of artificial intelligence focused on learning from data",
                "attributes": {"domain": "computer_science", "applications": ["vision", "nlp", "robotics"]},
                "importance": 0.9
            },
            {
                "name": "Python",
                "type": "programming_language",
                "description": "A high-level programming language popular in data science",
                "attributes": {"paradigm": "multi_paradigm", "creator": "Guido van Rossum"},
                "importance": 0.8
            },
            {
                "name": "TensorFlow",
                "type": "library",
                "description": "An open-source machine learning framework",
                "attributes": {"developer": "Google", "language": "Python"},
                "importance": 0.7
            },
            {
                "name": "Deep Learning",
                "type": "subfield",
                "description": "A subset of machine learning using neural networks",
                "attributes": {"parent_field": "Machine Learning", "key_concepts": ["neural_networks", "backpropagation"]},
                "importance": 0.8
            }
        ]
        
        entity_ids = []
        for entity_data in entities:
            entity_id = agent.knowledge.add_entity(entity_data)
            entity_ids.append(entity_id)
            print(f"✓ Created entity: {entity_data['name']}")
            
        # Create relations
        print("\n🔗 Creating Relations:")
        print("-" * 25)
        
        relations = [
            {
                "source": entity_ids[0],  # Machine Learning
                "target": entity_ids[3],  # Deep Learning
                "type": "has_subfield",
                "importance": 0.9,
                "bidirectional": False
            },
            {
                "source": entity_ids[1],  # Python
                "target": entity_ids[0],  # Machine Learning
                "type": "used_in",
                "importance": 0.8,
                "bidirectional": False
            },
            {
                "source": entity_ids[1],  # Python
                "target": entity_ids[2],  # TensorFlow
                "type": "implements",
                "importance": 0.7,
                "bidirectional": False
            },
            {
                "source": entity_ids[2],  # TensorFlow
                "target": entity_ids[3],  # Deep Learning
                "type": "supports",
                "importance": 0.8,
                "bidirectional": False
            }
        ]
        
        relation_ids = []
        for relation_data in relations:
            relation_id = agent.knowledge.add_relation(relation_data)
            relation_ids.append(relation_id)
            source_name = agent.knowledge.get_entity(relation_data["source"])["name"]
            target_name = agent.knowledge.get_entity(relation_data["target"])["name"]
            print(f"✓ Created relation: {source_name} --{relation_data['type']}--> {target_name}")
            
        # Query knowledge graph
        print("\n🔍 Querying Knowledge Graph:")
        print("-" * 30)
        
        queries = ["machine learning", "Python", "deep learning"]
        
        for query in queries:
            print(f"\nQuery: '{query}'")
            results = agent.knowledge.query(query, limit=3)
            
            for result in results:
                if result["type"] == "entity":
                    print(f"  📍 Entity: {result['name']} ({result['type']})")
                    print(f"     Relevance: {result['relevance']:.2f}")
                elif result["type"] == "relation":
                    print(f"  🔗 Relation: {result['source_name']} --{result['type']}--> {result['target_name']}")
                    print(f"     Relevance: {result['relevance']:.2f}")
                    
        # Find related entities
        print("\n🌐 Finding Related Entities:")
        print("-" * 35)
        
        ml_entity_id = entity_ids[0]  # Machine Learning
        related_entities = agent.knowledge.find_related_entities(ml_entity_id, max_depth=2)
        
        print(f"Entities related to 'Machine Learning':")
        for entity in related_entities:
            print(f"  • {entity['name']} (distance: {entity['relationship_distance']}, strength: {entity['relationship_strength']:.2f})")
            
        # Knowledge graph statistics
        print("\n📊 Knowledge Graph Statistics:")
        print("-" * 35)
        
        kg_stats = agent.knowledge.get_statistics()
        print(f"Total Entities: {kg_stats['total_entities']}")
        print(f"Total Relations: {kg_stats['total_relations']}")
        print(f"Graph Nodes: {kg_stats['graph_nodes']}")
        print(f"Graph Edges: {kg_stats['graph_edges']}")
        print(f"Entity Types: {kg_stats['entity_types']}")
        
    finally:
        agent.shutdown()


def demonstrate_continuous_learning():
    """Demonstrate continuous learning capabilities"""
    
    print("\n🎓 Continuous Learning Demonstration")
    print("=" * 50)
    
    config = AgentConfig(
        name="LearningDemo",
        memory_path="./learning_demo"
    )
    
    agent = AdvancedAgent(config)
    
    try:
        # Simulate learning interactions
        print("\n💡 Learning from Interactions:")
        print("-" * 35)
        
        learning_scenarios = [
            {
                "input": "Can you explain what overfitting is?",
                "context": {"topic": "machine_learning", "difficulty": "intermediate"},
                "expected_feedback": {"rating": 0.7, "aspects": ["clarity", "completeness"]}
            },
            {
                "input": "How do I prevent overfitting in my neural network?",
                "context": {"topic": "deep_learning", "difficulty": "advanced"},
                "expected_feedback": {"rating": 0.8, "aspects": ["practicality", "helpfulness"]}
            },
            {
                "input": "What's the difference between L1 and L2 regularization?",
                "context": {"topic": "optimization", "difficulty": "advanced"},
                "expected_feedback": {"rating": 0.9, "aspects": ["accuracy", "detail"]}
            }
        ]
        
        for i, scenario in enumerate(learning_scenarios, 1):
            print(f"\nInteraction {i}:")
            print(f"User: {scenario['input']}")
            
            # Process the interaction
            response = agent.process(scenario['input'], scenario['context'])
            print(f"Agent: {response['response'][:100]}...")
            print(f"Confidence: {response['confidence']:.2f}")
            
            # Simulate feedback
            feedback = scenario['expected_feedback']
            feedback["interaction_id"] = response.get("memory_id", f"interaction_{i}")
            agent.learn(feedback)
            print(f"✓ Learned from feedback (rating: {feedback['rating']})")
            
        # Learning optimization
        print("\n⚙️  Learning Optimization:")
        print("-" * 30)
        
        print("Optimizing learning model...")
        agent.learner.optimize_model()
        print("✓ Learning model optimized")
        
        # Learning statistics
        print("\n📊 Learning Statistics:")
        print("-" * 25)
        
        learning_stats = agent.learner.get_statistics()
        print(f"Learning Episodes: {learning_stats['learning_episodes']}")
        print(f"Adaptation Count: {learning_stats['adaptation_count']}")
        print(f"Response Patterns: {learning_stats['response_patterns_count']}")
        print(f"Current Learning Rate: {learning_stats['current_learning_rate']}")
        print(f"Current Exploration Rate: {learning_stats['current_exploration_rate']}")
        print(f"Recent Performance: {learning_stats['recent_performance']:.2f}")
        
        # Performance metrics
        print("\n📈 Performance Metrics:")
        print("-" * 30)
        
        for metric, data in learning_stats['performance_metrics'].items():
            print(f"{metric}:")
            print(f"  Count: {data['count']}")
            print(f"  Average: {data['average']:.3f}")
            print(f"  Recent Average: {data['recent_average']:.3f}")
            
    finally:
        agent.shutdown()


def demonstrate_emotional_intelligence():
    """Demonstrate emotional intelligence capabilities"""
    
    print("\n💭 Emotional Intelligence Demonstration")
    print("=" * 50)
    
    config = AgentConfig(
        name="EmotionalDemo",
        memory_path="./emotional_demo"
    )
    
    agent = AdvancedAgent(config)
    
    try:
        # Test emotional processing
        print("\n😊 Emotional Processing Examples:")
        print("-" * 40)
        
        emotional_inputs = [
            "I'm so excited to learn about artificial intelligence! This is amazing!",
            "I'm feeling a bit confused about backpropagation. Can you help me understand it better?",
            "This is frustrating! My code keeps giving me errors and I don't know why.",
            "Wow, that's incredible! I never thought machine learning could be so powerful.",
            "I'm worried that I might not be smart enough for this field."
        ]
        
        for i, user_input in enumerate(emotional_inputs, 1):
            print(f"\n{i}. User: {user_input}")
            
            # Process the input
            response = agent.process(user_input)
            
            # Show emotional analysis
            emotional_analysis = response.get("emotional_analysis", {})
            if emotional_analysis:
                print(f"   Detected Emotion: {emotional_analysis.get('dominant_emotion', 'neutral')}")
                print(f"   Sentiment: {emotional_analysis.get('sentiment', {}).get('label', 'neutral')}")
                print(f"   Intensity: {emotional_analysis.get('intensity', {}).get('overall', 0):.2f}")
                
            print(f"   Agent Response: {response['response']}")
            print(f"   Agent State: {response['emotional_state']}")
            
    finally:
        agent.shutdown()


def main():
    """Run all advanced feature demonstrations"""
    
    print("🚀 Advanced AI Agent - Advanced Features Demo")
    print("=" * 60)
    
    demonstrations = [
        ("Memory Systems", demonstrate_memory_systems),
        ("Knowledge Graph", demonstrate_knowledge_graph),
        ("Continuous Learning", demonstrate_continuous_learning),
        ("Emotional Intelligence", demonstrate_emotional_intelligence)
    ]
    
    for demo_name, demo_func in demonstrations:
        print(f"\n{'='*20} {demo_name} {'='*20}")
        try:
            demo_func()
            print(f"\n✅ {demo_name} demonstration completed successfully!")
        except Exception as e:
            print(f"\n❌ Error in {demo_name} demonstration: {e}")
            
        print("\n" + "="*60)
        
    print("\n🎉 All advanced features demonstrations completed!")
    print("Check the generated demo directories for saved data.")


if __name__ == "__main__":
    main()
