from typing import Dict, Any, List, Tuple
from .base_agent import BaseAgent
import re

class CodeCompilerAgent(BaseAgent):
    """Agent specialized in validating, debugging, and optimizing code."""
    
    def __init__(self):
        super().__init__(name="CodeCompiler")
        self.language_checkers = {
            "python": self._check_python,
            "javascript": self._check_javascript,
            # Add more language checkers as needed
        }
    
    def observe(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Observe the code that needs validation or debugging."""
        code_snippets = context.get("code_snippets", [])
        validation_type = self._determine_validation_type(query)
        
        return {
            "query": query,
            "code_snippets": code_snippets,
            "validation_type": validation_type,
            "context": context
        }
    
    def think(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the code and plan the validation approach."""
        code_snippets = observation["code_snippets"]
        validation_type = observation["validation_type"]
        
        if not code_snippets:
            return {
                "action": "request_code",
                "message": "I need code to validate or debug. Could you provide some code?"
            }
        
        snippet = code_snippets[0]
        language = snippet["language"]
        code = snippet["code"]
        
        if language not in self.language_checkers:
            return {
                "action": "unsupported_language",
                "message": f"I don't currently support validation for {language}. Supported languages are: {', '.join(self.language_checkers.keys())}."
            }
        
        return {
            "action": "validate_code",
            "code": code,
            "language": language,
        }