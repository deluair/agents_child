"""
Learning scheduler for managing when and how learning occurs
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import threading
import time
from loguru import logger


class LearningTrigger(Enum):
    """Different triggers for learning events"""
    INTERACTION_COUNT = "interaction_count"
    TIME_INTERVAL = "time_interval"
    PERFORMANCE_THRESHOLD = "performance_threshold"
    FEEDBACK_RECEIVED = "feedback_received"
    MEMORY_PRESSURE = "memory_pressure"
    MANUAL = "manual"


class ScheduledTask:
    """Represents a scheduled learning task"""
    
    def __init__(self, task_id: str, trigger: LearningTrigger, 
                 trigger_params: Dict[str, Any], action: Callable,
                 priority: int = 5):
        self.task_id = task_id
        self.trigger = trigger
        self.trigger_params = trigger_params
        self.action = action
        self.priority = priority
        self.last_executed = None
        self.execution_count = 0
        self.enabled = True
        
    def should_execute(self, context: Dict[str, Any]) -> bool:
        """Check if task should be executed based on trigger and context"""
        
        if not self.enabled:
            return False
            
        if self.trigger == LearningTrigger.INTERACTION_COUNT:
            threshold = self.trigger_params.get("count", 100)
            current_count = context.get("interaction_count", 0)
            
            # Check if we've reached the threshold since last execution
            if self.last_executed is None:
                return current_count >= threshold
            else:
                count_since_last = current_count - self.trigger_params.get("last_count", 0)
                return count_since_last >= threshold
                
        elif self.trigger == LearningTrigger.TIME_INTERVAL:
            interval_hours = self.trigger_params.get("hours", 1)
            
            if self.last_executed is None:
                return True
            else:
                time_since_last = datetime.now() - self.last_executed
                return time_since_last >= timedelta(hours=interval_hours)
                
        elif self.trigger == LearningTrigger.PERFORMANCE_THRESHOLD:
            metric = self.trigger_params.get("metric", "user_satisfaction")
            threshold = self.trigger_params.get("threshold", 0.5)
            below_threshold = self.trigger_params.get("below_threshold", True)
            
            current_value = context.get("performance_metrics", {}).get(metric, 0.5)
            
            if below_threshold:
                return current_value < threshold
            else:
                return current_value > threshold
                
        elif self.trigger == LearningTrigger.FEEDBACK_RECEIVED:
            return context.get("new_feedback", False)
            
        elif self.trigger == LearningTrigger.MEMORY_PRESSURE:
            memory_usage = context.get("memory_usage", 0.0)
            threshold = self.trigger_params.get("threshold", 0.8)
            return memory_usage >= threshold
            
        elif self.trigger == LearningTrigger.MANUAL:
            return context.get("manual_trigger", {}).get(self.task_id, False)
            
        return False
        
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the scheduled task"""
        
        try:
            logger.info(f"Executing learning task: {self.task_id}")
            
            result = self.action(context)
            
            self.last_executed = datetime.now()
            self.execution_count += 1
            
            # Update trigger params if needed
            if self.trigger == LearningTrigger.INTERACTION_COUNT:
                self.trigger_params["last_count"] = context.get("interaction_count", 0)
                
            return {
                "task_id": self.task_id,
                "success": True,
                "result": result,
                "execution_time": self.last_executed.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error executing task {self.task_id}: {e}")
            return {
                "task_id": self.task_id,
                "success": False,
                "error": str(e),
                "execution_time": datetime.now().isoformat()
            }


class LearningScheduler:
    """Scheduler for managing learning tasks and triggers"""
    
    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.running = False
        self.scheduler_thread = None
        self.check_interval = 60  # Check every 60 seconds
        
    def add_task(self, task: ScheduledTask) -> None:
        """Add a scheduled learning task"""
        
        self.tasks[task.task_id] = task
        logger.info(f"Added learning task: {task.task_id}")
        
    def remove_task(self, task_id: str) -> bool:
        """Remove a scheduled learning task"""
        
        if task_id in self.tasks:
            del self.tasks[task_id]
            logger.info(f"Removed learning task: {task_id}")
            return True
        return False
        
    def enable_task(self, task_id: str) -> bool:
        """Enable a scheduled task"""
        
        if task_id in self.tasks:
            self.tasks[task_id].enabled = True
            logger.info(f"Enabled learning task: {task_id}")
            return True
        return False
        
    def disable_task(self, task_id: str) -> bool:
        """Disable a scheduled task"""
        
        if task_id in self.tasks:
            self.tasks[task_id].enabled = False
            logger.info(f"Disabled learning task: {task_id}")
            return True
        return False
        
    def start(self, context_provider: Callable[[], Dict[str, Any]]) -> None:
        """Start the learning scheduler"""
        
        if self.running:
            logger.warning("Scheduler is already running")
            return
            
        self.running = True
        self.scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            args=(context_provider,),
            daemon=True
        )
        self.scheduler_thread.start()
        
        logger.info("Learning scheduler started")
        
    def stop(self) -> None:
        """Stop the learning scheduler"""
        
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
            
        logger.info("Learning scheduler stopped")
        
    def _scheduler_loop(self, context_provider: Callable[[], Dict[str, Any]]) -> None:
        """Main scheduler loop"""
        
        while self.running:
            try:
                context = context_provider()
                
                # Check each task
                ready_tasks = []
                for task in self.tasks.values():
                    if task.should_execute(context):
                        ready_tasks.append(task)
                        
                # Sort by priority (higher priority first)
                ready_tasks.sort(key=lambda t: t.priority, reverse=True)
                
                # Execute ready tasks
                for task in ready_tasks:
                    result = task.execute(context)
                    self.execution_history.append(result)
                    
                    # Keep only recent execution history
                    if len(self.execution_history) > 1000:
                        self.execution_history = self.execution_history[-1000:]
                        
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(self.check_interval)
                
    def trigger_manual_task(self, task_id: str) -> Dict[str, Any]:
        """Manually trigger a task execution"""
        
        if task_id not in self.tasks:
            return {"success": False, "error": "Task not found"}
            
        # Create temporary context with manual trigger
        context = {"manual_trigger": {task_id: True}}
        
        task = self.tasks[task_id]
        result = task.execute(context)
        self.execution_history.append(result)
        
        return result
        
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        
        if task_id not in self.tasks:
            return None
            
        task = self.tasks[task_id]
        
        return {
            "task_id": task.task_id,
            "trigger": task.trigger.value,
            "trigger_params": task.trigger_params,
            "priority": task.priority,
            "enabled": task.enabled,
            "last_executed": task.last_executed.isoformat() if task.last_executed else None,
            "execution_count": task.execution_count
        }
        
    def get_all_tasks_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all tasks"""
        
        return {
            task_id: self.get_task_status(task_id)
            for task_id in self.tasks.keys()
        }
        
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get execution statistics"""
        
        if not self.execution_history:
            return {
                "total_executions": 0,
                "success_rate": 0.0,
                "average_executions_per_day": 0.0
            }
            
        total_executions = len(self.execution_history)
        successful_executions = len([
            e for e in self.execution_history 
            if e.get("success", False)
        ])
        
        success_rate = successful_executions / total_executions if total_executions > 0 else 0.0
        
        # Calculate executions per day
        if total_executions > 1:
            first_execution = datetime.fromisoformat(self.execution_history[0]["execution_time"])
            days_since_first = (datetime.now() - first_execution).days
            executions_per_day = total_executions / max(1, days_since_first)
        else:
            executions_per_day = 0.0
            
        # Task-specific statistics
        task_stats = {}
        for execution in self.execution_history:
            task_id = execution.get("task_id", "unknown")
            if task_id not in task_stats:
                task_stats[task_id] = {"total": 0, "successful": 0}
                
            task_stats[task_id]["total"] += 1
            if execution.get("success", False):
                task_stats[task_id]["successful"] += 1
                
        return {
            "total_executions": total_executions,
            "success_rate": success_rate,
            "average_executions_per_day": executions_per_day,
            "task_statistics": task_stats,
            "recent_executions": len([
                e for e in self.execution_history
                if datetime.fromisoformat(e["execution_time"]) > datetime.now() - timedelta(days=1)
            ])
        }
        
    def create_default_tasks(self, agent_instance) -> None:
        """Create default learning tasks for an agent"""
        
        # Memory consolidation task
        consolidation_task = ScheduledTask(
            task_id="memory_consolidation",
            trigger=LearningTrigger.INTERACTION_COUNT,
            trigger_params={"count": 10, "last_count": 0},
            action=lambda ctx: agent_instance.memory.consolidate_memories(),
            priority=8
        )
        
        # Learning optimization task
        optimization_task = ScheduledTask(
            task_id="learning_optimization",
            trigger=LearningTrigger.INTERACTION_COUNT,
            trigger_params={"count": 50, "last_count": 0},
            action=lambda ctx: agent_instance.learner.optimize_model(),
            priority=7
        )
        
        # Performance monitoring task
        performance_task = ScheduledTask(
            task_id="performance_monitoring",
            trigger=LearningTrigger.TIME_INTERVAL,
            trigger_params={"hours": 1},
            action=lambda ctx: self._monitor_performance(ctx, agent_instance),
            priority=5
        )
        
        # Memory cleanup task
        cleanup_task = ScheduledTask(
            task_id="memory_cleanup",
            trigger=LearningTrigger.MEMORY_PRESSURE,
            trigger_params={"threshold": 0.9},
            action=lambda ctx: self._cleanup_memory(ctx, agent_instance),
            priority=9
        )
        
        # Add all tasks
        for task in [consolidation_task, optimization_task, performance_task, cleanup_task]:
            self.add_task(task)
            
        logger.info("Created default learning tasks")
        
    def _monitor_performance(self, context: Dict[str, Any], agent_instance) -> Dict[str, Any]:
        """Monitor agent performance and trigger adaptations if needed"""
        
        performance_metrics = context.get("performance_metrics", {})
        
        # Check if performance is below threshold
        satisfaction = performance_metrics.get("user_satisfaction", 0.5)
        
        if satisfaction < 0.4:
            # Trigger adaptation
            feedback = {
                "sentiment": "negative",
                "rating": satisfaction,
                "aspects": ["performance"]
            }
            
            adaptation = agent_instance.learner.adaptation_engine.adapt(feedback, performance_metrics)
            
            return {
                "action": "performance_adaptation",
                "satisfaction": satisfaction,
                "adaptations": len(adaptation.get("adjustments", {}))
            }
            
        return {"action": "performance_monitoring", "status": "satisfactory"}
        
    def _cleanup_memory(self, context: Dict[str, Any], agent_instance) -> Dict[str, Any]:
        """Perform memory cleanup when memory pressure is high"""
        
        # Force memory consolidation
        agent_instance.memory.consolidate_memories()
        
        # Apply forgetting
        agent_instance.memory.forget_memories()
        
        # Clean up knowledge graph
        agent_instance.knowledge.cleanup()
        
        return {"action": "memory_cleanup", "memory_pressure": context.get("memory_usage", 0.0)}
