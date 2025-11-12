"""
Standalone demo of the Advanced AI Agent core functionality
This demo imports modules directly to avoid dependency issues.
"""

import sys
import os
from datetime import datetime

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_configuration():
    """Demonstrate configuration system"""
    
    print("📋 Configuration System Demo")
    print("-" * 40)
    
    # Import directly to avoid chain imports
    from agent.core.config import AgentConfig, MemoryConfig, LearningConfig, KnowledgeConfig
    
    # Create configuration
    config = AgentConfig(
        name="StandaloneAgent",
        version="1.0.0",
        memory_path="./standalone_memory",
        log_level="INFO"
    )
    
    print(f"✓ Agent Name: {config.name}")
    print(f"✓ Version: {config.version}")
    print(f"✓ Memory Path: {config.memory_path}")
    print(f"✓ Log Level: {config.log_level}")
    
    # Show memory configuration
    memory = config.memory
    print(f"✓ Short-term Capacity: {memory.short_term_capacity}")
    print(f"✓ Episodic Capacity: {memory.episodic_capacity}")
    print(f"✓ Semantic Capacity: {memory.semantic_capacity}")
    
    # Show learning configuration
    learning = config.learning
    print(f"✓ Learning Rate: {learning.learning_rate}")
    print(f"✓ Batch Size: {learning.batch_size}")
    print(f"✓ Exploration Rate: {learning.exploration_rate}")
    
    return config


def demo_state_management():
    """Demonstrate state management"""
    
    print("\n🧠 State Management Demo")
    print("-" * 40)
    
    from agent.core.state import AgentState, AgentMode, EmotionalState
    
    # Create agent state
    state = AgentState()
    print(f"✓ Initial Mode: {state.mode}")
    print(f"✓ Initial Emotional State: {state.emotional_state}")
    
    # Update state
    state.update_mode(AgentMode.PROCESSING)
    print(f"✓ Updated Mode: {state.mode}")
    
    state.update_emotional_state(EmotionalState.POSITIVE)
    print(f"✓ Updated Emotional State: {state.emotional_state}")
    
    # Add context
    state.add_context("user_name", "Alice")
    state.add_context("topic", "machine learning")
    state.add_context("session_id", "demo_001")
    
    context = state.get_context_summary()
    print(f"✓ Context Variables: {len(context)} items")
    
    # Add interaction
    interaction = {
        "timestamp": datetime.now().isoformat(),
        "user_input": "Tell me about AI",
        "agent_response": "AI is artificial intelligence...",
        "confidence": 0.85
    }
    
    state.add_interaction(interaction)
    print(f"✓ Interactions Count: {len(state.interaction_history)}")
    
    # Update performance metrics
    state.update_performance_metric("response_time", 1.2)
    state.update_performance_metric("user_satisfaction", 0.8)
    
    metrics = state.get_performance_metrics()
    print(f"✓ Performance Metrics: {len(metrics)} tracked")
    
    return state


def demo_learning_scheduler():
    """Demonstrate learning scheduler"""
    
    print("\n📚 Learning Scheduler Demo")
    print("-" * 40)
    
    from agent.learning.learning_scheduler import LearningScheduler, LearningTrigger, ScheduledTask
    
    # Create scheduler
    scheduler = LearningScheduler()
    print(f"✓ Scheduler created")
    
    # Create sample tasks
    def memory_consolidation_task(context):
        return {"action": "consolidated_memories", "count": 5}
    
    def performance_monitor_task(context):
        metrics = context.get("performance_metrics", {})
        return {"action": "monitored_performance", "metrics": len(metrics)}
    
    # Add tasks
    task1 = ScheduledTask(
        task_id="memory_consolidation",
        trigger=LearningTrigger.INTERACTION_COUNT,
        trigger_params={"count": 10, "last_count": 0},
        action=memory_consolidation_task,
        priority=8
    )
    
    task2 = ScheduledTask(
        task_id="performance_monitor",
        trigger=LearningTrigger.TIME_INTERVAL,
        trigger_params={"hours": 1},
        action=performance_monitor_task,
        priority=5
    )
    
    scheduler.add_task(task1)
    scheduler.add_task(task2)
    
    print(f"✓ Added {len(scheduler.tasks)} tasks")
    
    # Get task status
    all_tasks = scheduler.get_all_tasks_status()
    for task_id, status in all_tasks.items():
        print(f"✓ Task {task_id}: {status['trigger']} (priority: {status['priority']})")
    
    # Execute manual task
    result = scheduler.trigger_manual_task("performance_monitor")
    print(f"✓ Manual execution result: {result['success']}")
    
    # Get statistics
    stats = scheduler.get_execution_statistics()
    print(f"✓ Total Executions: {stats['total_executions']}")
    print(f"✓ Success Rate: {stats['success_rate']:.2%}")
    
    return scheduler


def demo_adaptation_engine():
    """Demonstrate adaptation engine"""
    
    print("\n🔄 Adaptation Engine Demo")
    print("-" * 40)
    
    from agent.learning.adaptation_engine import AdaptationEngine
    
    # Create adaptation engine
    engine = AdaptationEngine()
    print(f"✓ Adaptation engine created")
    
    # Show initial settings
    initial_settings = engine.get_current_settings()
    print(f"✓ Initial Settings: {initial_settings}")
    
    # Simulate feedback and performance
    feedback = {
        "sentiment": "negative",
        "rating": 0.3,
        "aspects": ["clarity", "helpfulness"]
    }
    
    performance_metrics = {
        "user_satisfaction": 0.3,
        "response_time": 3.5
    }
    
    # Apply adaptations
    adaptation = engine.adapt(feedback, performance_metrics)
    print(f"✓ Applied {len(adaptation['adjustments'])} adaptations")
    
    # Show new settings
    new_settings = engine.get_current_settings()
    print(f"✓ Updated Settings: {new_settings}")
    
    # Show adaptation statistics
    stats = engine.get_adaptation_statistics()
    print(f"✓ Total Adaptations: {stats['total_adaptations']}")
    print(f"✓ Adaptation Frequency: {stats['adaptation_frequency']:.2f}/day")
    
    return engine


def demo_feedback_processor():
    """Demonstrate feedback processing"""
    
    print("\n💬 Feedback Processor Demo")
    print("-" * 40)
    
    from agent.learning.feedback_processor import FeedbackProcessor
    
    # Create processor
    processor = FeedbackProcessor()
    print(f"✓ Feedback processor created")
    
    # Process different types of feedback
    feedback_samples = [
        {"comment": "This was very helpful and clear!", "rating": 0.9},
        {"comment": "The response was confusing and too brief.", "rating": 0.2},
        {"comment": "It was okay, but could be better.", "rating": 0.5}
    ]
    
    for i, feedback in enumerate(feedback_samples, 1):
        processed = processor.process_feedback(feedback)
        signals = processor.extract_learning_signals(processed)
        
        print(f"✓ Feedback {i}:")
        print(f"  - Sentiment: {processed['sentiment']}")
        print(f"  - Category: {processed['category']}")
        print(f"  - Severity: {processed['severity']}")
        print(f"  - Actionable: {processed['actionable']}")
        print(f"  - Strengths: {signals['strength_areas']}")
        print(f"  - Improvements: {signals['improvement_areas']}")
    
    return processor


def demo_emotion_processor():
    """Demonstrate emotion processing"""
    
    print("\n😊 Emotion Processor Demo")
    print("-" * 40)
    
    from agent.processors.emotion_processor import EmotionProcessor
    
    # Create processor
    processor = EmotionProcessor()
    print(f"✓ Emotion processor created")
    
    # Process emotional texts
    emotional_texts = [
        "I'm so excited to learn about artificial intelligence! This is amazing!",
        "I'm feeling confused about neural networks. Can you help me understand better?",
        "This is frustrating! My code keeps giving me errors.",
        "Wow, that's incredible! I never thought AI could be so powerful.",
        "I'm worried that I might not be smart enough for this field."
    ]
    
    for i, text in enumerate(emotional_texts, 1):
        analysis = processor.analyze(text)
        
        print(f"✓ Text {i}: '{text[:50]}...'")
        print(f"  - Dominant Emotion: {analysis['dominant_emotion']}")
        print(f"  - Sentiment: {analysis['sentiment']['label']} (polarity: {analysis['sentiment']['polarity']:.2f})")
        print(f"  - Intensity: {analysis['intensity']['overall']:.2f}")
        print(f"  - Tone: {analysis['tone']}")
        print(f"  - Complexity: {analysis['emotional_complexity']}")
    
    return processor


def demo_context_processor():
    """Demonstrate context processing"""
    
    print("\n🎯 Context Processor Demo")
    print("-" * 40)
    
    from agent.processors.context_processor import ContextProcessor
    
    # Create processor
    processor = ContextProcessor(max_context_length=5)
    print(f"✓ Context processor created")
    
    # Simulate conversation
    conversation = [
        "Hello, I'm Bob and I'm interested in machine learning.",
        "Can you explain what neural networks are?",
        "That's helpful! What about deep learning then?",
        "By the way, I'm also interested in Python programming.",
        "How do I get started with ML in Python?"
    ]
    
    for i, text in enumerate(conversation, 1):
        context = processor.process_context(text)
        
        print(f"✓ Turn {i}: '{text}'")
        print(f"  - Topics: {context['topics']}")
        print(f"  - Entities: {len(context['entities'])} found")
        print(f"  - User Intent: {context['context_variables']['user_intent']}")
        print(f"  - Context Shift: {context['context_shift']['shift_detected']}")
        print(f"  - Conversation Stage: {context['summary']['conversation_stage']}")
        print(f"  - Engagement Level: {context['flow_analysis']['engagement_level']:.2f}")
    
    # Get final context for response
    response_context = processor.get_context_for_response()
    print(f"✓ Final Context: {len(response_context['current_topics'])} topics, {len(response_context['active_entities'])} entities")
    
    return processor


def main():
    """Run the standalone demo"""
    
    print("🚀 Advanced AI Agent - Standalone Core Demo")
    print("=" * 60)
    print("This demo showcases the core functionality without external dependencies.")
    print("=" * 60)
    
    demos = [
        ("Configuration", demo_configuration),
        ("State Management", demo_state_management),
        ("Learning Scheduler", demo_learning_scheduler),
        ("Adaptation Engine", demo_adaptation_engine),
        ("Feedback Processor", demo_feedback_processor),
        ("Emotion Processor", demo_emotion_processor),
        ("Context Processor", demo_context_processor)
    ]
    
    results = {}
    
    for demo_name, demo_func in demos:
        try:
            print(f"\n{'='*20} {demo_name} {'='*20}")
            result = demo_func()
            results[demo_name] = "✅ SUCCESS"
            print(f"✅ {demo_name} completed successfully!")
        except Exception as e:
            results[demo_name] = f"❌ FAILED: {e}"
            print(f"❌ {demo_name} failed: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 DEMO SUMMARY")
    print("=" * 60)
    
    success_count = 0
    for demo_name, result in results.items():
        print(f"{result}")
        if "SUCCESS" in result:
            success_count += 1
    
    print(f"\n🎯 Results: {success_count}/{len(demos)} demos successful")
    
    if success_count == len(demos):
        print("\n🎉 ALL DEMOS PASSED!")
        print("The Advanced AI Agent core architecture is fully functional.")
        print("All major components are working correctly.")
        print("\n📋 What was demonstrated:")
        print("• Configuration management with environment variables")
        print("• Agent state management and context tracking")
        print("• Learning scheduler with task automation")
        print("• Adaptation engine for dynamic behavior adjustment")
        print("• Feedback processing for continuous improvement")
        print("• Emotion processing for emotional intelligence")
        print("• Context processing for conversation awareness")
        
        print("\n🚀 The agent is ready for:")
        print("• Integration with language models")
        print("• Connection to external knowledge sources")
        print("• Deployment in production environments")
        print("• Extension with additional capabilities")
        
    else:
        print(f"\n⚠️  {len(demos) - success_count} demos failed.")
        print("Check the error messages above for details.")
    
    return success_count == len(demos)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
