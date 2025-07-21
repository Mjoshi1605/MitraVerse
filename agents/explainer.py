from typing import Dict, Any
from .base_agent import BaseAgent

class CodeExplainerAgent(BaseAgent):
    """Agent specialized in explaining code."""
    
    def __init__(self):
        super().__init__(name="CodeExplainer")
    
    def observe(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Observe the code that needs explanation."""
        code_snippets = context.get("code_snippets", [])
        return {
            "query": query,
            "code_snippets": code_snippets,
            "explanation_level": self._determine_explanation_level(query),
            "context": context
        }
    
    def think(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the code and plan the explanation."""
        code_snippets = observation["code_snippets"]
        explanation_level = observation["explanation_level"]
        
        if not code_snippets:
            return {
                "action": "request_code",
                "message": "I need code to explain. Could you provide some code?"
            }
        
        return {
            "action": "explain_code",
            "code": code_snippets[0]["code"],
            "language": code_snippets[0]["language"],
            "explanation_level": explanation_level,
            "approach": self._determine_explanation_approach(code_snippets[0], explanation_level)
        }
    
    def act(self, thoughts: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the code explanation."""
        action = thoughts.get("action")
        
        if action == "request_code":
            return {
                "success": False,
                "response": thoughts["message"],
                "needs_more_info": True
            }
        
        if action == "explain_code":
            code = thoughts["code"]
            language = thoughts["language"]
            explanation_level = thoughts["explanation_level"]
            approach = thoughts["approach"]
            
            explanation = self._generate_explanation(code, language, explanation_level, approach)
            
            return {
                "success": True,
                "response": explanation,
                "code": code,
                "language": language
            }
        
        return {
            "success": False,
            "response": "I'm not sure how to explain this code."
        }
    
    def _determine_explanation_level(self, query: str) -> str:
        """Determine the level of detail needed for the explanation."""
        if any(term in query.lower() for term in ["detailed", "in-depth", "comprehensive", "line by line"]):
            return "detailed"
        elif any(term in query.lower() for term in ["brief", "overview", "summary", "high level"]):
            return "high-level"
        else:
            return "medium"
    
    def _determine_explanation_approach(self, code_snippet: Dict[str, Any], level: str) -> str:
        """Determine the approach to explaining the code."""
        if level == "detailed":
            return "line-by-line"
        elif level == "high-level":
            return "functional-overview"
        else:
            return "key-components"
    
    def _generate_explanation(self, code: str, language: str, level: str, approach: str) -> str:
        """Generate an explanation of the code."""
        # This would use more sophisticated code analysis in a real implementation
        if approach == "line-by-line":
            lines = code.strip().split("\n")
            explanation = "Let me explain this code line by line:\n\n"
            
            for i, line in enumerate(lines, 1):
                if line.strip() and not line.strip().startswith(("#", "//", "/*", "*")):
                    explanation += f"Line {i}: `{line.strip()}` - "
                    explanation += self._explain_line(line, language) + "\n"
            
            return explanation
        
        elif approach == "functional-overview":
            return f"This {language} code appears to be {self._determine_code_purpose(code, language)}. " + \
                   f"The main components are {self._identify_main_components(code, language)}."
        
        else:  # key-components
            return f"Here are the key components of this {language} code:\n\n" + \
                   self._explain_key_components(code, language)
    
    def _explain_line(self, line: str, language: str) -> str:
        """Explain a single line of code."""
        # Simplified implementation - would be more sophisticated in reality
        return "This line performs an operation in the code."
    
    def _determine_code_purpose(self, code: str, language: str) -> str:
        """Determine the overall purpose of the code."""
        # Simplified implementation
        return "performing some operations"
    
    def _identify_main_components(self, code: str, language: str) -> str:
        """Identify the main components in the code."""
        # Simplified implementation
        return "functions, variables, and control structures"
    
    def _explain_key_components(self, code: str, language: str) -> str:
        """Explain the key components of the code."""
        # Simplified implementation
        return "1. Main functionality: The code performs operations\n2. Data handling: The code processes data"
