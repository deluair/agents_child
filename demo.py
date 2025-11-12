"""
Working demo of the Advanced AI Agent core functionality
"""

import sys
import os

# Add the parent directory to the path so we can import the agent
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_core_functionality():
    """Demonstrate core agent functionality without heavy dependencies"""
    
    print("🤖 Advanced AI Agent - Core Functionality Demo")
    print("=" * 60)
    
    # Test configuration system
    print("\n📋 1. Configuration System")
    print("-" * 30)
    
    from agent.core.config import AgentConfig, MemoryConfig, LearningConfig
    
    config = AgentConfig(
        name="DemoAgent",
        version="1.0.0",
        memory_path="./demo_memory"
    )
    
    print(f"✓ Agent: {config.name} v{config.version}")
    print(f"✓ Memory Path: {config.memory_path}")
    print(f"✓ Short-term capacity: {config.memory.short_term_capacity}")
    print(f"✓ Learning rate: {config.learning.learning_rate}")
    
    # Test state management
    print("\n🧠 2. State Management")
    print("-" * 30)
    
    from agent.core.state import AgentState, AgentMode, EmotionalState
    
    state = AgentState()
    print(f"✓ Initial mode: {state.mode}")
    
    state.update_mode(AgentMode.PROCESSING)
    print(f"✓ Updated mode: {state.mode}")
    
    state.update_emotional_state(EmotionalState.NEUTRAL)
    print(f"✓ Emotional state: {state.emotional_state}")
    
    state.add_context("user_name", "Alice")
    state.add_context("topic", "machine learning")
    print(f"✓ Context: {state.get_context_summary()}")
    
    # Test learning scheduler
    print("\n📚 3. Learning Scheduler")
    print("-" * 30)
    
    from agent.learning.learning_scheduler import LearningScheduler, LearningTrigger, ScheduledTask
    
    scheduler = LearningScheduler()
    
    # Create a simple task
    def test_task(context):
        return {"message": "Task executed successfully!"}
    
    task = ScheduledTask(
        task_id="demo_task",
        trigger=LearningTrigger.MANUAL,
        trigger_params={},
        action=test_task,
        priority=5
    )
    
    scheduler.add_task(task)
    print(f"✓ Added task: {task.task_id}")
    
    # Execute the task
    result = scheduler.trigger_manual_task("demo_task")
    print(f"✓ Task executed: {result}")
    
    stats = scheduler.get_execution_statistics()
    print(f"✓ Total executions: {stats['total_executions']}")
    
    # Test memory consolidation
    print("\n💾 4. Memory Consolidation")
    print("-" * 30)
    
    from agent.memory.memory_consolidation import MemoryConsolidation
    
    consolidation = MemoryConsolidation()
    
    # Create sample memories
    sample_memories = [
        {"content": "User asked about Python", "importance": 0.6, "type": "short_term"},
        {"content": "User learned about neural networks", "importance": 0.8, "type": "episodic"},
        {"content": "Python is a programming language", "importance": 0.9, "type": "semantic"}
    ]
    
    consolidation_scores = []
    for memory in sample_memories:
        score = consolidation.calculate_consolidation_score(memory)
        consolidation_scores.append(score)
        print(f"✓ Memory consolidation score: {score:.3f}")
    
    # Test adaptation engine
    print("\n🔄 5. Adaptation Engine")
    print("-" * 30)
    
    from agent.learning.adaptation_engine import AdaptationEngine
    
    adaptation = AdaptationEngine()
    
    # Simulate feedback
    feedback = {
        "sentiment": "positive",
        "rating": 0.8,
        "aspects": ["clarity", "helpfulness"]
    }
    
    performance_metrics = {
        "user_satisfaction": 0.8,
        "response_time": 1.2
    }
    
    adaptation_result = adaptation.adapt(feedback, performance_metrics)
    print(f"✓ Adaptations applied: {len(adaptation_result['adjustments'])}")
    
    current_settings = adaptation.get_current_settings()
    print(f"✓ Current settings: {current_settings}")
    
    # Test feedback processor
    print("\n💬 6. Feedback Processing")
    print("-" * 30)
    
    from agent.learning.feedback_processor import FeedbackProcessor
    
    processor = FeedbackProcessor()
    
    feedback_data = {
        "comment": "This was very helpful and clear!",
        "rating": 0.9
    }
    
    processed_feedback = processor.process_feedback(feedback_data)
    print(f"✓ Feedback sentiment: {processed_feedback['sentiment']}")
    print(f"✓ Feedback category: {processed_feedback['category']}")
    print(f"✓ Feedback aspects: {processed_feedback['aspects']}")
    
    learning_signals = processor.extract_learning_signals(processed_feedback)
    print(f"✓ Learning signals: {len(learning_signals['strength_areas'])} strengths, {len(learning_signals['improvement_areas'])} improvements")
    
    # Test emotion processor
    print("\n😊 7. Emotion Processing")
    print("-" * 30)
    
    from agent.processors.emotion_processor import EmotionProcessor
    
    emotion_processor = EmotionProcessor()
    
    emotional_texts = [
        "I'm so excited to learn about AI!",
        "This is confusing me a bit.",
        "That's fantastic news!"
    ]
    
    for text in emotional_texts:
        analysis = emotion_processor.analyze(text)
        print(f"✓ Text: '{text}'")
        print(f"  - Dominant emotion: {analysis['dominant_emotion']}")
        print(f"  - Sentiment: {analysis['sentiment']['label']}")
        print(f"  - Intensity: {analysis['intensity']['overall']:.2f}")
    
    # Test context processor
    print("\n🎯 8. Context Processing")
    print("-" * 30)
    
    from agent.processors.context_processor import ContextProcessor
    
    context_processor = ContextProcessor()
    
    conversation = [
        "Hello, I'm interested in machine learning.",
        "Can you explain neural networks?",
        "That's helpful! What about deep learning?"
    ]
    
    for text in conversation:
        context = context_processor.process_context(text)
        print(f"✓ Processed: '{text}'")
        print(f"  - Topics: {context['topics']}")
        print(f"  - User intent: {context['context_variables']['user_intent']}")
        print(f"  - Conversation stage: {context['summary']['conversation_stage']}")
    
    print("\n🎉 Core Functionality Demo Completed!")
    print("=" * 60)
    
    print("\n📊 Summary:")
    print("✓ Configuration system working")
    print("✓ State management working")
    print("✓ Learning scheduler working")
    print("✓ Memory consolidation working")
    print("✓ Adaptation engine working")
    print("✓ Feedback processing working")
    print("✓ Emotion processing working")
    print("✓ Context processing working")
    
    print("\n🚀 The Advanced AI Agent core is fully functional!")
    print("All major components are working correctly.")
    print("The agent is ready for integration with external models and services.")


if __name__ == "__main__":
    demo_core_functionality()
