from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseAgent(ABC):
    """Abstract base class for all agents in the MitraVerse system."""
    
    def __init__(self, name: str):
        self.name = name
        self.memory = []  # Simple memory to store past interactions
    
    def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a query using the React pattern: Observe, Think, Act, Reflect.
        
        Args:
            query: The user's query or request
            context: Additional context information
            
        Returns:
            A dictionary containing the response and any additional information
        """
        # 1. Observe - Gather information about the current state
        observation = self.observe(query, context)
        
        # 2. Think - Reason about what to do
        thoughts = self.think(observation)
        
        # 3. Act - Take action based on reasoning
        action_result = self.act(thoughts)
        
        # 4. Reflect - Learn from the action
        reflection = self.reflect(action_result)
        
        # Store in memory
        self.memory.append({
            "query": query,
            "observation": observation,
            "thoughts": thoughts,
            "action_result": action_result,
            "reflection": reflection
        })
        
        return action_result
    
    @abstractmethod
    def observe(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Observe the current state and gather relevant information."""
        pass
    
    @abstractmethod
    def think(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Think about the observation and decide what to do."""
        pass
    
    @abstractmethod
    def act(self, thoughts: Dict[str, Any]) -> Dict[str, Any]:
        """Act based on the thoughts."""
        pass
    
    def reflect(self, action_result: Dict[str, Any]) -> Dict[str, Any]:
        """Reflect on the action and its results."""
        # Default implementation - can be overridden by subclasses
        return {
            "success": action_result.get("success", True),
            "lessons": "Completed action successfully" if action_result.get("success", True) else "Action failed",
            "improvement": "Consider more context next time"
        }
