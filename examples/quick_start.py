"""
Quick start example for the Advanced AI Agent
"""

import sys
import os

# Add the parent directory to the path so we can import the agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import AdvancedAgent


def main():
    """Quick start demonstration"""
    
    print("🚀 Advanced AI Agent - Quick Start")
    print("=" * 40)
    
    # Initialize agent with default settings
    print("📦 Initializing agent...")
    agent = AdvancedAgent()
    
    try:
        # Simple conversation
        print("\n💬 Starting conversation...")
        
        conversation = [
            "Hello! I'm new to artificial intelligence.",
            "Can you tell me what machine learning is?",
            "That's interesting! What are some applications?",
            "Thank you for the information!"
        ]
        
        for user_input in conversation:
            print(f"\n👤 You: {user_input}")
            
            # Get response from agent
            response = agent.process(user_input)
            
            print(f"🤖 Agent: {response['response']}")
            
        # Show agent learned something
        print("\n📊 Agent Statistics:")
        stats = agent.get_statistics()
        print(f"Total Interactions: {stats['agent_info']['total_interactions']}")
        print(f"Memories Stored: {stats['memory']['episodic']['count']}")
        print(f"Learning Episodes: {stats['learning']['learning_episodes']}")
        
        print("\n✅ Quick start completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
    finally:
        # Clean shutdown
        agent.shutdown()
        print("🔄 Agent shutdown complete.")


if __name__ == "__main__":
    main()
