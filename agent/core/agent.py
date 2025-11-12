"""
Main Advanced Agent class with continuous learning and memory
"""

import os
import json
import time
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from loguru import logger

from .config import AgentConfig, load_config
from .state import AgentState, AgentMode, EmotionalState
from ..memory.memory_manager import MemoryManager
from ..learning.continuous_learner import ContinuousLearner
from ..knowledge.knowledge_graph import KnowledgeGraph

# Lazy imports for processors to avoid TensorFlow dependency issues
TextProcessor = None
EmotionProcessor = None


class AdvancedAgent:
    """Advanced AI agent with memory, learning, and reasoning capabilities"""
    
    def __init__(self, config: Optional[AgentConfig] = None, memory_path: Optional[str] = None):
        # Load configuration
        self.config = config or load_config()
        if memory_path:
            self.config.memory_path = memory_path
            
        # Initialize core components
        self.state = AgentState()
        self.memory = MemoryManager(self.config.memory, self.config.memory_path)
        self.learner = ContinuousLearner(self.config.learning)
        self.knowledge = KnowledgeGraph(self.config.knowledge, self.config.memory_path)
        
        # Initialize processors (lazy loading to avoid dependency issues)
        self.text_processor = None
        self.emotion_processor = None
        self._init_processors()
        
        # Performance tracking
        self.interaction_count = 0
        self.start_time = datetime.now()
        
    def _init_processors(self):
        """Initialize processors with graceful fallback if dependencies missing"""
        try:
            from ..processors.text_processor import TextProcessor
            self.text_processor = TextProcessor(self.config)
            logger.info("Text processor initialized")
        except Exception as e:
            logger.warning(f"Text processor not available: {e}")
            self.text_processor = None
            
        try:
            from ..processors.emotion_processor import EmotionProcessor
            self.emotion_processor = EmotionProcessor()
            logger.info("Emotion processor initialized")
        except Exception as e:
            logger.warning(f"Emotion processor not available: {e}")
            self.emotion_processor = None
        
        # Load existing state if available
        self._load_state()
        
        logger.info(f"Advanced agent '{self.config.name}' initialized")
        
    def _load_state(self):
        """Load agent state from disk"""
        state_file = os.path.join(self.config.memory_path, "agent_state.json")
        
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r') as f:
                    state_data = json.load(f)
                self.state.from_dict(state_data)
                logger.info("Agent state loaded from disk")
            except Exception as e:
                logger.warning(f"Failed to load agent state: {e}")
                
    def _save_state(self):
        """Save agent state to disk"""
        state_file = os.path.join(self.config.memory_path, "agent_state.json")
        
        try:
            with open(state_file, 'w') as f:
                json.dump(self.state.to_dict(), f, indent=2)
            logger.debug("Agent state saved to disk")
        except Exception as e:
            logger.warning(f"Failed to save agent state: {e}")
            
    def process(self, input_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process input and generate response"""
        
        self.state.update_mode(AgentMode.PROCESSING)
        self.interaction_count += 1
        
        try:
            # Add context if provided
            if context:
                for key, value in context.items():
                    self.state.add_context(key, value)
                    
            # Process input text
            if self.text_processor:
                processed_input = self.text_processor.process(input_text)
            else:
                # Fallback text processing
                processed_input = {
                    "text": input_text,
                    "tokens": input_text.split(),
                    "sentences": [input_text],
                    "features": {}
                }
            
            # Analyze emotional content
            if self.emotion_processor:
                emotional_analysis = self.emotion_processor.analyze(input_text)
                self.state.update_emotional_state(
                    EmotionalState(emotional_analysis.get("dominant_emotion", "neutral"))
                )
            else:
                # Fallback emotional analysis
                emotional_analysis = {
                    "dominant_emotion": "neutral",
                    "sentiment": {"label": "neutral", "polarity": 0.0},
                    "intensity": {"overall": 0.5}
                }
            
            # Retrieve relevant memories
            relevant_memories = self.memory.retrieve_memory(input_text, limit=5)
            
            # Query knowledge graph
            knowledge_insights = self.knowledge.query(input_text)
            
            # Generate response using learning model
            response_data = self._generate_response(
                processed_input, 
                relevant_memories, 
                knowledge_insights,
                emotional_analysis
            )
            
            # Store interaction in memory
            interaction = {
                "input": input_text,
                "response": response_data["response"],
                "emotional_analysis": emotional_analysis,
                "memories_used": len(relevant_memories),
                "knowledge_used": len(knowledge_insights),
                "context": context or {}
            }
            
            memory_id = self.memory.add_memory(
                interaction, 
                "episodic", 
                importance=response_data.get("confidence", 0.5)
            )
            
            # Update agent state
            self.state.add_interaction(interaction)
            self.state.update_performance_metric("response_time", response_data.get("processing_time", 0))
            
            # Learn from this interaction
            self.learner.learn_from_interaction(interaction)
            
            # Periodic maintenance
            if self.interaction_count % 10 == 0:
                self._perform_maintenance()
                
            response_data["memory_id"] = memory_id
            response_data["agent_state"] = self.state.get_context_summary()
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            self.state.update_emotional_state(EmotionalState.CONFUSED)
            
            return {
                "response": "I'm having trouble processing that. Could you please rephrase?",
                "confidence": 0.1,
                "error": str(e),
                "agent_state": self.state.get_context_summary()
            }
        finally:
            self.state.update_mode(AgentMode.IDLE)
            self._save_state()
            
    def _generate_response(self, processed_input: Dict[str, Any], 
                          memories: List[Dict[str, Any]], 
                          knowledge: List[Dict[str, Any]],
                          emotional_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response based on input, memories, and knowledge"""
        
        start_time = time.time()
        
        # Combine context information
        context = {
            "processed_input": processed_input,
            "memories": memories,
            "knowledge": knowledge,
            "emotional_state": self.state.emotional_state.value,
            "emotional_analysis": emotional_analysis,
            "conversation_history": self.state.interaction_history[-5:]  # Last 5 interactions
        }
        
        # Generate response using the learning model
        response = self.learner.generate_response(context)
        
        # Calculate confidence
        confidence = self._calculate_response_confidence(context, response)
        
        processing_time = time.time() - start_time
        
        return {
            "response": response,
            "confidence": confidence,
            "processing_time": processing_time,
            "memories_used": len(memories),
            "knowledge_used": len(knowledge),
            "emotional_state": self.state.emotional_state.value
        }
        
    def _calculate_response_confidence(self, context: Dict[str, Any], response: str) -> float:
        """Calculate confidence score for the response"""
        
        confidence = 0.5  # Base confidence
        
        # Boost confidence if we have relevant memories
        if context["memories"]:
            confidence += 0.2
            
        # Boost confidence if we have relevant knowledge
        if context["knowledge"]:
            confidence += 0.2
            
        # Adjust based on emotional state
        if self.state.emotional_state in [EmotionalState.HAPPY, EmotionalState.ENGAGED]:
            confidence += 0.1
        elif self.state.emotional_state == EmotionalState.CONFUSED:
            confidence -= 0.2
            
        return min(1.0, max(0.0, confidence))
        
    def _perform_maintenance(self):
        """Perform periodic maintenance tasks"""
        
        logger.info("Performing agent maintenance")
        
        # Memory consolidation
        self.memory.consolidate_memories()
        
        # Memory forgetting
        self.memory.forget_memories()
        
        # Learning model optimization
        self.learner.optimize_model()
        
        # Knowledge graph cleanup
        self.knowledge.cleanup()
        
        # Save all states
        self.memory.save_state()
        self.knowledge.save_state()
        
    def learn(self, feedback: Dict[str, Any]) -> None:
        """Learn from explicit feedback"""
        
        self.state.update_mode(AgentMode.LEARNING)
        
        try:
            # Process feedback
            processed_feedback = self.learner.process_feedback(feedback)
            
            # Update learning model
            self.learner.update_from_feedback(processed_feedback)
            
            # Store feedback in memory
            self.memory.add_memory(
                {
                    "type": "feedback",
                    "feedback": feedback,
                    "processed_feedback": processed_feedback,
                    "timestamp": datetime.now().isoformat()
                },
                "semantic",
                importance=0.8
            )
            
            logger.info("Agent learned from feedback")
            
        except Exception as e:
            logger.error(f"Error learning from feedback: {e}")
        finally:
            self.state.update_mode(AgentMode.IDLE)
            self._save_state()
            
    def add_knowledge(self, knowledge_item: Dict[str, Any]) -> str:
        """Add new knowledge to the agent"""
        
        try:
            # Add to knowledge graph
            entity_id = self.knowledge.add_entity(knowledge_item)
            
            # Also store in semantic memory
            self.memory.add_memory(
                knowledge_item,
                "semantic",
                importance=knowledge_item.get("importance", 0.7)
            )
            
            logger.info(f"Added knowledge entity: {entity_id}")
            return entity_id
            
        except Exception as e:
            logger.error(f"Error adding knowledge: {e}")
            raise
            
    def query_memory(self, query: str, memory_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Query agent's memory"""
        
        return self.memory.retrieve_memory(query, memory_type, limit)
        
    def query_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """Query agent's knowledge graph"""
        
        return self.knowledge.query(query)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the agent"""
        
        uptime = datetime.now() - self.start_time
        
        return {
            "agent_info": {
                "name": self.config.name,
                "version": self.config.version,
                "uptime_hours": uptime.total_seconds() / 3600,
                "total_interactions": self.interaction_count
            },
            "state": self.state.get_context_summary(),
            "memory": self.memory.get_memory_stats(),
            "learning": self.learner.get_statistics(),
            "knowledge": self.knowledge.get_statistics()
        }
        
    def export_memory(self, filepath: str) -> None:
        """Export agent's memory to file"""
        
        try:
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "agent_info": {
                    "name": self.config.name,
                    "version": self.config.version,
                    "interactions": self.interaction_count
                },
                "state": self.state.to_dict(),
                "memory": {
                    "short_term": self.memory.short_term.to_dict(),
                    "episodic": self.memory.episodic.to_dict(),
                    "semantic": self.memory.semantic.to_dict()
                },
                "knowledge": self.knowledge.to_dict()
            }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
                
            logger.info(f"Memory exported to {filepath}")
            
        except Exception as e:
            logger.error(f"Error exporting memory: {e}")
            raise
            
    def import_memory(self, filepath: str) -> None:
        """Import memory from file"""
        
        try:
            with open(filepath, 'r') as f:
                import_data = json.load(f)
                
            # Import state
            if "state" in import_data:
                self.state.from_dict(import_data["state"])
                
            # Import memory
            if "memory" in import_data:
                memory_data = import_data["memory"]
                
                if "short_term" in memory_data:
                    self.memory.short_term.from_dict(memory_data["short_term"])
                    
                if "episodic" in memory_data:
                    self.memory.episodic.from_dict(memory_data["episodic"])
                    
                if "semantic" in memory_data:
                    self.memory.semantic.from_dict(memory_data["semantic"])
                    
            # Import knowledge
            if "knowledge" in import_data:
                self.knowledge.from_dict(import_data["knowledge"])
                
            logger.info(f"Memory imported from {filepath}")
            
        except Exception as e:
            logger.error(f"Error importing memory: {e}")
            raise
            
    def reset(self) -> None:
        """Reset agent to initial state"""
        
        logger.warning("Resetting agent to initial state")
        
        # Clear memory
        self.memory.short_term.clear()
        self.memory.episodic.episodes.clear()
        self.memory.semantic.concepts.clear()
        self.memory.semantic.facts.clear()
        
        # Reset state
        self.state = AgentState()
        
        # Reset counters
        self.interaction_count = 0
        self.start_time = datetime.now()
        
        # Save reset state
        self._save_state()
        
        logger.info("Agent reset completed")
        
    def shutdown(self) -> None:
        """Properly shutdown the agent"""
        
        logger.info("Shutting down agent")
        
        # Perform final maintenance
        self._perform_maintenance()
        
        # Save all states
        self._save_state()
        self.memory.save_state()
        self.knowledge.save_state()
        
        logger.info("Agent shutdown completed")
