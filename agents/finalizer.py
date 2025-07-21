from typing import Dict, Any, List
from .base_agent import BaseAgent
import re

class CodeFinalizerAgent(BaseAgent):
    """Agent specialized in finalizing code by adding documentation, tests, and optimizations."""
    
    def __init__(self):
        super().__init__(name="CodeFinalizer")
    
    def observe(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Observe the code that needs to be finalized."""
        code_snippets = self._extract_code_snippets(query, context)
        requirements = self._extract_requirements(query)
        
        return {
            "query": query,
            "code_snippets": code_snippets,
            "requirements": requirements,
            "context": context
        }
    
    def think(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the code and plan improvements."""
        code_snippets = observation["code_snippets"]
        requirements = observation["requirements"]
        
        if not code_snippets:
            return {
                "action": "request_code",
                "message": "I need the code to finalize. Could you provide it?"
            }
        
        code_snippet = code_snippets[0]
        code = code_snippet["code"]
        language = code_snippet["language"]
        
        # Analyze the code
        analysis = self._analyze_code(code, language)
        
        # Determine what improvements are needed
        improvements_needed = self._determine_improvements_needed(analysis, requirements)
        
        return {
            "action": "finalize_code",
            "code": code,
            "language": language,
            "analysis": analysis,
            "improvements_needed": improvements_needed
        }
    
    def act(self, thoughts: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize the code with improvements."""
        action = thoughts.get("action")
        
        if action == "request_code":
            return {
                "success": False,
                "response": thoughts["message"],
                "needs_more_info": True
            }
        
        if action == "finalize_code":
            code = thoughts["code"]
            language = thoughts["language"]
            improvements_needed = thoughts["improvements_needed"]
            
            # Apply improvements
            improved_code = self._apply_improvements(code, language, improvements_needed)
            
            # Generate explanation of improvements
            explanation = self._generate_improvement_explanation(improvements_needed)
            
            return {
                "success": True,
                "response": f"I've finalized the {language} code with the following improvements:\n\n{explanation}\n\n```{language}\n{improved_code}\n```",
                "code": improved_code,
                "language": language,
                "improvements": improvements_needed
            }
        
        return {
            "success": False,
            "response": "I'm not sure how to finalize this code."
        }
    
    def _extract_code_snippets(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract code snippets from the query and context."""
        snippets = []
        
        # Extract code blocks from markdown-style code blocks
        code_block_pattern = r'```(\w*)\n(.*?)\n```'
        for match in re.finditer(code_block_pattern, query, re.DOTALL):
            language = match.group(1) or "unknown"
            code = match.group(2)
            snippets.append({"language": language, "code": code})
        
        # Check if there's code in the context
        if context and "code_snippets" in context:
            snippets.extend(context["code_snippets"])
        elif context and "code" in context:
            snippets.append({
                "language": context.get("language", "unknown"),
                "code": context["code"]
            })
        
        return snippets
    
    def _extract_requirements(self, query: str) -> List[str]:
        """Extract requirements from the query."""
        requirements = []
        
        # Look for specific improvement requests
        improvement_patterns = [
            r'add\s+(.*?)(?:\.|$)',
            r'improve\s+(.*?)(?:\.|$)',
            r'optimize\s+(.*?)(?:\.|$)',
            r'include\s+(.*?)(?:\.|$)'
        ]
        
        for pattern in improvement_patterns:
            for match in re.finditer(pattern, query, re.I):
                requirement = match.group(1).strip()
                if requirement:
                    requirements.append(requirement)
        
        return requirements
    
    def _analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze the code to identify areas for improvement."""
        analysis = {
            "has_documentation": self._has_documentation(code, language),
            "has_tests": self._has_tests(code, language),
            "has_error_handling": self._has_error_handling(code, language),
            "complexity": self._estimate_complexity(code, language),
            "code_quality": self._estimate_code_quality(code, language)
        }
        
        return analysis
    
    def _has_documentation(self, code: str, language: str) -> bool:
        """Check if the code has documentation."""
        if language == "python":
            # Check for docstrings
            return '"""' in code or "'''" in code
        elif language in ["javascript", "typescript"]:
            # Check for JSDoc comments
            return '/**' in code
        elif language in ["java", "c#", "c++", "c"]:
            # Check for JavaDoc-style comments
            return '/**' in code
        else:
            # Generic check for comments
            return '#' in code or '//' in code or '/*' in code
    
    def _has_tests(self, code: str, language: str) -> bool:
        """Check if the code has tests."""
        test_indicators = [
            "test", "assert", "expect", "should", "mock", "stub", "spy",
            "unittest", "pytest", "jest", "mocha", "jasmine"
        ]
        
        return any(indicator in code.lower() for indicator in test_indicators)
    
    def _has_error_handling(self, code: str, language: str) -> bool:
        """Check if the code has error handling."""
        if language == "python":
            return "try:" in code and "except" in code
        elif language in ["javascript", "typescript", "java", "c#"]:
            return "try {" in code and "catch" in code
        else:
            # Generic check
            return "try" in code and "catch" in code
    
    def _estimate_complexity(self, code: str, language: str) -> str:
        """Estimate the complexity of the code."""
        # Count control structures as a simple complexity metric
        control_structures = 0
        
        if language == "python":
            patterns = [r'\bif\b', r'\bfor\b', r'\bwhile\b', r'\btry\b', r'\bwith\b']
        else:
            patterns = [r'\bif\b', r'\bfor\b', r'\bwhile\b', r'\btry\b', r'\bswitch\b']
        
        for pattern in patterns:
            control_structures += len(re.findall(pattern, code))
        
        if control_structures <= 3:
            return "Simple"
        elif control_structures <= 10:
            return "Moderate"
        else:
            return "Complex"
    
    def _estimate_code_quality(self, code: str, language: str) -> str:
        """Estimate the quality of the code."""
        # This is a simplified metric
        quality_score = 0
        
        # Check for documentation
        if self._has_documentation(code, language):
            quality_score += 2
        
        # Check for tests
        if self._has_tests(code, language):
            quality_score += 2
        
        # Check for error handling
        if self._has_error_handling(code, language):
            quality_score += 1
        
        # Check for consistent indentation
        if self._has_consistent_indentation(code, language):
            quality_score += 1
        
        # Evaluate based on score
        if quality_score >= 5:
            return "High"
        elif quality_score >= 3:
            return "Medium"
        else:
            return "Low"
    
    def _has_consistent_indentation(self, code: str, language: str) -> bool:
        """Check if the code has consistent indentation."""
        lines = code.split('\n')
        indentation_sizes = set()
        
        for line in lines:
            if line.strip():  # Skip empty lines
                # Count leading spaces
                leading_spaces = len(line) - len(line.lstrip())
                if leading_spaces > 0:
                    indentation_sizes.add(leading_spaces)
        
        # If we have more than 2 different indentation sizes, it's inconsistent
        return len(indentation_sizes) <= 2
    
    def _determine_improvements_needed(self, analysis: Dict[str, Any], requirements: List[str]) -> List[str]:
        """Determine what improvements are needed based on analysis and requirements."""
        improvements = []
        
        # Check for missing documentation
        if not analysis["has_documentation"]:
            improvements.append("documentation")
        
        # Check for missing tests
        if not analysis["has_tests"]:
            improvements.append("tests")
        
        # Check for missing error handling
        if not analysis["has_error_handling"] and analysis["complexity"] != "Simple":
            improvements.append("error_handling")
        
        # Check for code quality
        if analysis["code_quality"] == "Low":
            improvements.append("code_quality")
        
        # Add specific requirements
        for req in requirements:
            if "document" in req.lower() and "documentation" not in improvements:
                improvements.append("documentation")
            elif "test" in req.lower() and "tests" not in improvements:
                improvements.append("tests")
            elif "error" in req.lower() and "error_handling" not in improvements:
                improvements.append("error_handling")
            elif "optim" in req.lower():
                improvements.append("optimization")
            elif "comment" in req.lower() and "documentation" not in improvements:
                improvements.append("documentation")
        
        return improvements
    
    def _apply_improvements(self, code: str, language: str, improvements_needed: List[str]) -> str:
        """Apply the needed improvements to the code."""
        improved_code = code
        
        for improvement in improvements_needed:
            if improvement == "documentation":
                improved_code = self._add_documentation(improved_code, language)
            elif improvement == "tests":
                improved_code = self._add_tests(improved_code, language)
            elif improvement == "error_handling":
                improved_code = self._add_error_handling(improved_code, language)
            elif improvement == "code_quality":
                improved_code = self._improve_code_quality(improved_code, language)
            elif improvement == "optimization":
                improved_code = self._optimize_code(improved_code, language)
        
        return improved_code
    
    def _add_documentation(self, code: str, language: str) -> str:
        """Add documentation to the code."""
        if language == "python":
            # Add module docstring if not present
            if not ('"""' in code[:500] or "'''" in code[:500]):
                code = '"""Module documentation.\n\nThis module provides functionality for...\n"""\n\n' + code
            
            # Add function/class docstrings
            def_pattern = r'(def\s+\w+\s*\(.*?\):)'
            class_pattern = r'(class\s+\w+(?:\(.*?\))?:)'
            
            for pattern in [def_pattern, class_pattern]:
                code = re.sub(
                    pattern,
                    r'\1\n    """Description of this function/class.\n    \n    Args:\n        param1: Description of param1\n    \n    Returns:\n        Description of return value\n    """',
                    code
                )
        
        elif language in ["javascript", "typescript"]:
            # Add JSDoc comments
            function_pattern = r'(function\s+\w+\s*\(.*?\))'
            method_pattern = r'(\w+\s*\(.*?\)\s*{)'
            
            for pattern in [function_pattern, method_pattern]:
                code = re.sub(
                    pattern,
                    r'/**\n * Description of this function/method.\n * @param {type} param1 - Description of param1\n * @returns {type} Description of return value\n */\n\1',
                    code
                )
        
        return code
    
    def _add_tests(self, code: str, language: str) -> str:
        """Add tests to the code."""
        if language == "python":
            # Add unittest framework
            test_code = "\n\n# Tests\nimport unittest\n\n"
            test_code += "class TestFunctionality(unittest.TestCase):\n"
            test_code += "    def test_example(self):\n"
            test_code += "        # TODO: Replace with actual test\n"
            test_code += "        self.assertEqual(1, 1)\n\n"
            test_code += "if __name__ == '__main__':\n"
            test_code += "    unittest.main()\n"
            
            return code + test_code
        
        elif language in ["javascript", "typescript"]:
            # Add simple test framework (e.g., Jest-like)
            test_code = "\n\n// Tests\n"
            test_code += "function test() {\n"
            test_code += "  // TODO: Replace with actual tests\n"
            test_code += "  console.assert(1 === 1, 'Assertion failed');\n"
            test_code += "}\n\n"
            test_code += "test();\n"
            
            return code + test_code
        
        return code
    
    def _add_error_handling(self, code: str, language: str) -> str:
        """Add error handling to the code."""
        if language == "python":
            # Find function definitions without try-except
            def_pattern = r'(def\s+\w+\s*\(.*?\):(?:\s*""".*?""")?)((?!\s*try:).)*?(\s+\w+)'
            
            # Add try-except blocks
            code = re.sub(
                def_pattern,
                r'\1\n    try:\2\3\n    except Exception as e:\n        print(f"Error: {e}")\n        raise',
                code,
                flags=re.DOTALL
            )
        
        elif language in ["javascript", "typescript"]:
            # Find function bodies without try-catch
            func_pattern = r'(function\s+\w+\s*\(.*?\)\s*{(?:\s*\/\*\*.*?\*\/)?)((?!\s*try\s*{).)*?(\s+\w+)'
            
            # Add try-catch blocks
            code = re.sub(
                func_pattern,
                r'\1\n  try {\2\3\n  } catch (error) {\n    console.error("Error:", error);\n    throw error;\n  }',
                code,
                flags=re.DOTALL
            )
        
        return code
    
    def _improve_code_quality(self, code: str, language: str) -> str:
        """Improve the quality of the code."""
        # Add comments for clarity
        improve
