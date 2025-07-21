from typing import Dict, Any, List
from .base_agent import BaseAgent
import re

class CodeBuilderAgent(BaseAgent):
    """Agent specialized in generating code based on requirements."""
    
    def __init__(self):
        super().__init__(name="CodeBuilder")
        self.supported_languages = [
            "python", "javascript", "typescript", "java", "c", "cpp", "csharp", 
            "go", "rust", "ruby", "php", "swift", "kotlin"
        ]
    
    def observe(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Observe the requirements for code generation."""
        language = self._detect_language(query)
        requirements = self._extract_requirements(query)
        existing_code = self._extract_existing_code(context)
        
        return {
            "query": query,
            "language": language,
            "requirements": requirements,
            "existing_code": existing_code,
            "context": context
        }
    
    def think(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Plan the code generation approach."""
        language = observation["language"]
        requirements = observation["requirements"]
        existing_code = observation["existing_code"]
        
        if not language:
            return {
                "action": "request_language",
                "message": "What programming language would you like me to use?"
            }
        
        if not requirements:
            return {
                "action": "clarify_requirements",
                "message": "Could you provide more specific requirements for the code you need?"
            }
        
        approach = self._determine_approach(language, requirements, existing_code)
        structure = self._plan_code_structure(language, requirements, existing_code)
        
        return {
            "action": "generate_code",
            "language": language,
            "requirements": requirements,
            "existing_code": existing_code,
            "approach": approach,
            "structure": structure
        }
    
    def act(self, thoughts: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the code based on the plan."""
        action = thoughts.get("action")
        
        if action in ["request_language", "clarify_requirements"]:
            return {
                "success": False,
                "response": thoughts["message"],
                "needs_more_info": True
            }
        
        if action == "generate_code":
            language = thoughts["language"]
            requirements = thoughts["requirements"]
            approach = thoughts["approach"]
            structure = thoughts["structure"]
            
            code = self._generate_code(language, requirements, structure, approach)
            explanation = self._generate_explanation(code, language, structure)
            
            return {
                "success": True,
                "response": f"Here's the {language} code based on your requirements:\n\n```{language}\n{code}\n```\n\n{explanation}",
                "code": code,
                "language": language,
                "explanation": explanation
            }
        
        return {
            "success": False,
            "response": "I'm not sure how to generate code for this request."
        }
    
    def _detect_language(self, query: str) -> str:
        """Detect the programming language from the query."""
        for language in self.supported_languages:
            if language in query.lower():
                return language
        
        # Default to Python if no language is specified
        return "python"
    
    def _extract_requirements(self, query: str) -> List[str]:
        """Extract requirements from the query."""
        # Simple implementation - in reality, this would be more sophisticated
        requirements = []
        
        # Remove code blocks to avoid confusion
        clean_query = re.sub(r'```.*?```', '', query, flags=re.DOTALL)
        
        # Split by common requirement indicators
        for line in clean_query.split('\n'):
            line = line.strip()
            if line and any(line.startswith(prefix) for prefix in ['- ', '* ', '1. ', '2. ']):
                requirements.append(line.lstrip('- *123456789. '))
        
        # If no structured requirements found, use the whole query
        if not requirements:
            requirements = [clean_query]
        
        return requirements
    
    def _extract_existing_code(self, context: Dict[str, Any]) -> str:
        """Extract existing code from context if available."""
        code_snippets = context.get("code_snippets", [])
        if code_snippets:
            return code_snippets[0]["code"]
        return ""
    
    def _determine_approach(self, language: str, requirements: List[str], existing_code: str) -> str:
        """Determine the approach to code generation."""
        if existing_code:
            return "extend_existing"
        elif len(requirements) > 3:
            return "modular"
        else:
            return "single_unit"
    
    def _plan_code_structure(self, language: str, requirements: List[str], existing_code: str) -> Dict[str, Any]:
        """Plan the structure of the code to be generated."""
        # This would be more sophisticated in a real implementation
        return {
            "components": [f"Component for {req[:30]}..." for req in requirements],
            "interfaces": [],
            "dependencies": []
        }
    
    def _generate_code(self, language: str, requirements: List[str], structure: Dict[str, Any], approach: str) -> str:
        """Generate code based on requirements and structure."""
        # This is a placeholder - in a real implementation, this would use a more sophisticated approach
        if language == "python":
            return self._generate_python_code(requirements, structure, approach)
        elif language == "javascript":
            return self._generate_javascript_code(requirements, structure, approach)
        else:
            return f"# Code for {language}\n# Implementing: {', '.join(requirements)}"
    
    def _generate_python_code(self, requirements: List[str], structure: Dict[str, Any], approach: str) -> str:
        """Generate Python code."""
        # Simplified implementation
        code = "# Generated Python code\n\n"
        
        if approach == "modular":
            code += "class Solution:\n"
            for i, req in enumerate(requirements):
                code += f"    def function_{i+1}(self):\n"
                code += f"        # Implements: {req}\n"
                code += "        pass\n\n"
            
            code += "# Usage example\n"
            code += "solution = Solution()\n"
        else:
            code += "def main():\n"
            for req in requirements:
                code += f"    # Implements: {req}\n"
                code += "    pass\n\n"
            
            code += "if __name__ == '__main__':\n"
            code += "    main()\n"
        
        return code
    
    def _generate_javascript_code(self, requirements: List[str], structure: Dict[str, Any], approach: str) -> str:
        """Generate JavaScript code."""
        # Simplified implementation
        code = "// Generated JavaScript code\n\n"
        
        if approach == "modular":
            code += "class Solution {\n"
            for i, req in enumerate(requirements):
                code += f"  function{i+1}() {{\n"
                code += f"    // Implements: {req}\n"
                code += "    // Implementation here\n"
                code += "  }\n\n"
            code += "}\n\n"
            
            code += "// Usage example\n"
            code += "const solution = new Solution();\n"
        else:
            code += "function main() {\n"
            for req in requirements:
                code += f"  // Implements: {req}\n"
                code += "  // Implementation here\n"
            code += "}\n\n"
            
            code += "main();\n"
        
        return code
    
    def _generate_explanation(self, code: str, language: str, structure: Dict[str, Any]) -> str:
        """Generate an explanation for the code."""
        return "This code implements the requested functionality with the following components:\n" + \
               "\n".join([f"- {component}" for component in structure["components"]])
