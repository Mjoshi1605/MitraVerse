from typing import Dict, Any, Optional, List
from agents.base_agent import BaseAgent
import re
from autogen_integration import AutoGenManager

class AutoGenAdapter(BaseAgent):
    """
    Adapter to integrate AutoGen with the MitraVerse agent system.
    """
    
    def __init__(self):
        super().__init__(name="AutoGenAdapter")
        self.autogen_manager = AutoGenManager()
    
    def observe(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Observe the query and context to understand what's being asked.
        """
        # Determine the task type
        task_type = self._determine_task_type(query)
        
        # Extract relevant information from the query
        code_snippets = context.get("code_snippets", [])
        language = self._detect_language(query, code_snippets)
        
        return {
            "query": query,
            "task_type": task_type,
            "language": language,
            "code_snippets": code_snippets,
            "context": context
        }
    
    def think(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Think about how to handle the query using AutoGen.
        """
        task_type = observation["task_type"]
        query = observation["query"]
        language = observation["language"]
        code_snippets = observation["code_snippets"]
        
        if task_type == "code_generation":
            return {
                "action": "generate_code",
                "requirements": query,
                "language": language
            }
        
        elif task_type == "code_explanation":
            if code_snippets:
                return {
                    "action": "explain_code",
                    "code": code_snippets[0]["code"],
                    "language": code_snippets[0]["language"] or language
                }
            else:
                return {
                    "action": "request_code",
                    "message": "Please provide the code you'd like me to explain."
                }
        
        elif task_type == "code_debugging":
            if code_snippets:
                error_message = self._extract_error_message(query)
                return {
                    "action": "debug_code",
                    "code": code_snippets[0]["code"],
                    "error_message": error_message,
                    "language": code_snippets[0]["language"] or language
                }
            else:
                return {
                    "action": "request_code",
                    "message": "Please provide the code you'd like me to debug."
                }
        
        else:  # collaborative or complex task
            return {
                "action": "collaborative_task",
                "task": query
            }
    
    def act(self, thoughts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the task using AutoGen.
        """
        action = thoughts["action"]
        
        if action == "generate_code":
            requirements = thoughts["requirements"]
            language = thoughts["language"]
            
            code = self.autogen_manager.generate_code(requirements, language)
            
            return {
                "success": True,
                "response": f"Here's the {language} code based on your requirements:\n\n```{language}\n{code}\n```",
                "code": code,
                "language": language
            }
        
        elif action == "explain_code":
            code = thoughts["code"]
            language = thoughts["language"]
            
            explanation = self.autogen_manager.explain_code(code, language)
            
            return {
                "success": True,
                "response": explanation,
                "code": code,
                "language": language
            }
        
        elif action == "debug_code":
            code = thoughts["code"]
            error_message = thoughts.get("error_message")
            language = thoughts["language"]
            
            debug_result = self.autogen_manager.debug_code(code, error_message, language)
            
            return {
                "success": True,
                "response": f"Here's the debugged code:\n\n```{language}\n{debug_result['debugged_code']}\n```\n\n{debug_result['explanation']}",
                "code": debug_result["debugged_code"],
                "explanation": debug_result["explanation"],
                "language": language
            }
        
        elif action == "collaborative_task":
            task = thoughts["task"]
            
            result = self.autogen_manager.collaborative_task(task)
            
            return {
                "success": True,
                "response": result
            }
        
        elif action == "request_code":
            return {
                "success": False,
                "response": thoughts["message"],
                "needs_more_info": True
            }
        
        return {
            "success": False,
            "response": "I'm not sure how to handle this request using AutoGen."
        }
    
    def _determine_task_type(self, query: str) -> str:
        """
        Determine the type of task based on the query.
        """
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ["create", "generate", "write", "implement"]):
            return "code_generation"
        
        elif any(keyword in query_lower for keyword in ["explain", "understand", "what does", "how does"]):
            return "code_explanation"
        
        elif any(keyword in query_lower for keyword in ["debug", "fix", "error", "issue", "problem"]):
            return "code_debugging"
        
        else:
            return "collaborative_task"
    
    def _detect_language(self, query: str, code_snippets: List[Dict[str, Any]]) -> str:
        """
        Detect the programming language from the query and code snippets.
        """
        # Check if language is explicitly mentioned in the query
        language_patterns = {
            "python": r'\b(python|py)\b',
            "javascript": r'\b(javascript|js)\b',
            "java": r'\bjava\b',
            "c++": r'\b(c\+\+|cpp)\b',
            "c#": r'\b(c#|csharp)\b',
            "ruby": r'\bruby\b',
            "go": r'\bgo\b',
            "rust": r'\brust\b',
            "php": r'\bphp\b',
            "typescript": r'\b(typescript|ts)\b'
        }
        
        for lang, pattern in language_patterns.items():
            if re.search(pattern, query, re.I):
                return lang
        
        # Check if we have code snippets with language info
        if code_snippets:
            for snippet in code_snippets:
                if snippet.get("language") and snippet["language"] != "unknown":
                    return snippet["language"]
        
        # Default to Python
        return "python"
    
    def _extract_error_message(self, query: str) -> Optional[str]:
        """
        Extract error message from the query.
        """
        # Look for text that appears to be an error message
        error_patterns = [
            r'error[:\s]+(.*?)(?:\n|$)',
            r'exception[:\s]+(.*?)(?:\n|$)',
            r'traceback[:\s]+(.*?)(?:\n|$)'
        ]
        
        for pattern in error_patterns:
            match = re.search(pattern, query, re.I)
            if match:
                return match.group(1).strip()
        
        # If no specific error pattern is found, look for text between "error" and the end of the line
        error_index
