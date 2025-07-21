from typing import Dict, Any, List, Optional, Tuple
import re
from agents.base_agent import BaseAgent
from agents.explainer import CodeExplainerAgent
from agents.builder import CodeBuilderAgent
from agents.compiler import CodeCompilerAgent
from agents.finalizer import CodeFinalizerAgent
from tools.tool_manager import ToolManager
from models.conversation import Conversation

class MasterAgent(BaseAgent):
    """
    Master agent that coordinates all interactions, delegates to sub-agents,
    and manages tool usage.
    """
    
    def __init__(self):
        super().__init__(name="MasterAgent")
        
        # Initialize sub-agents
        self.sub_agents = {
            "explainer": CodeExplainerAgent(),
            "builder": CodeBuilderAgent(),
            "compiler": CodeCompilerAgent(),
            "finalizer": CodeFinalizerAgent()
        }
        
        # Initialize tool manager
        self.tool_manager = ToolManager()
        
        # Initialize conversation state
        self.conversation = Conversation()
    
    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a user query and return a response.
        
        Args:
            query: The user's query
            context: Optional additional context
            
        Returns:
            A string response to the user
        """
        # Update conversation with user query
        self.conversation.add_user_message(query)
        
        # Get full context
        full_context = self.conversation.get_context()
        if context:
            full_context.update(context)
        
        # Process using the React pattern
        result = self.process(query, full_context)
        
        # Extract response
        response = result.get("response", "I'm not sure how to help with that.")
        
        # Update conversation with response
        self.conversation.add_assistant_message(response)
        
        return response
    
    def observe(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Observe the query and context to understand what's being asked.
        """
        # Analyze the query to determine intent
        intent_analysis = self._analyze_intent(query)
        
        # Check if code is present in the query or context
        code_snippets = self._extract_code_snippets(query, context)
        
        # Determine if we need specific tools or agents
        tools_needed = self._determine_tools_needed(intent_analysis, code_snippets)
        agents_needed = self._determine_agents_needed(intent_analysis, code_snippets)
        
        return {
            "query": query,
            "intent": intent_analysis,
            "code_snippets": code_snippets,
            "tools_needed": tools_needed,
            "agents_needed": agents_needed,
            "context": context
        }
    
    def think(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Think about how to handle the query based on observations.
        """
        intent = observation["intent"]
        tools_needed = observation["tools_needed"]
        agents_needed = observation["agents_needed"]
        
        # Determine execution strategy
        strategy = []
        
        # First, decide if we need to use tools
        for tool_name in tools_needed:
            tool_params = self._get_tool_params(tool_name, observation)
            strategy.append({"type": "tool", "name": tool_name, "params": tool_params})
        
        # Then, decide if we need to use agents
        for agent_name in agents_needed:
            agent_params = self._get_agent_params(agent_name, observation)
            strategy.append({"type": "agent", "name": agent_name, "params": agent_params})
        
        # If no specific strategy, use a default approach
        if not strategy:
            if "code_generation" in intent:
                strategy.append({"type": "agent", "name": "builder", "params": {"query": observation["query"]}})
            elif "code_explanation" in intent:
                strategy.append({"type": "agent", "name": "explainer", "params": {"query": observation["query"]}})
            else:
                strategy.append({"type": "default", "name": "direct_response", "params": {"query": observation["query"]}})
        
        return {
            "observation": observation,
            "strategy": strategy,
            "reasoning": f"Based on the query '{observation['query']}', I've determined we need {', '.join([s['name'] for s in strategy])}."
        }
    
    def act(self, thoughts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the strategy determined during thinking.
        """
        strategy = thoughts["strategy"]
        results = []
        
        for step in strategy:
            step_type = step["type"]
            step_name = step["name"]
            step_params = step["params"]
            
            if step_type == "tool":
                # Execute tool
                try:
                    tool_result = self.tool_manager.execute_tool(step_name, **step_params)
                    results.append({"type": "tool_result", "name": step_name, "result": tool_result})
                except Exception as e:
                    results.append({"type": "tool_error", "name": step_name, "error": str(e)})
            
            elif step_type == "agent":
                # Execute sub-agent
                try:
                    if step_name in self.sub_agents:
                        agent_result = self.sub_agents[step_name].process(
                            step_params.get("query", ""),
                            step_params.get("context", {})
                        )
                        results.append({"type": "agent_result", "name": step_name, "result": agent_result})
                    else:
                        results.append({"type": "agent_error", "name": step_name, "error": "Agent not found"})
                except Exception as e:
                    results.append({"type": "agent_error", "name": step_name, "error": str(e)})
            
            elif step_type == "default":
                # Direct response
                results.append({"type": "default", "result": self._generate_direct_response(step_params["query"])})
        
        # Synthesize final response from all results
        response = self._synthesize_response(results, thoughts["observation"]["query"])
        
        return {
            "success": True,
            "results": results,
            "response": response
        }
    
    def reflect(self, action_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reflect on the actions taken and results obtained.
        """
        success = action_result.get("success", False)
        results = action_result.get("results", [])
        
        # Analyze what went well and what didn't
        successes = [r for r in results if "error" not in r]
        failures = [r for r in results if "error" in r]
        
        lessons = []
        if failures:
            for failure in failures:
                lessons.append(f"Failed to use {failure['name']}: {failure.get('error', 'Unknown error')}")
        
        improvements = []
        if not success:
            improvements.append("Consider using different tools or agents next time")
        
        return {
            "success": success,
            "lessons": lessons,
            "improvements": improvements
        }
    
    def _analyze_intent(self, query: str) -> Dict[str, float]:
        """
        Analyze the intent of the query.
        
        Returns:
            A dictionary mapping intent types to confidence scores
        """
        intents = {
            "code_generation": 0.0,
            "code_explanation": 0.0,
            "code_debugging": 0.0,
            "information_retrieval": 0.0,
            "general_question": 0.0
        }
        
        # Simple keyword-based intent detection
        if re.search(r'(create|generate|write|implement|build)\s+code', query, re.I):
            intents["code_generation"] = 0.8
        
        if re.search(r'(explain|understand|clarify|what does|how does)\s+code', query, re.I):
            intents["code_explanation"] = 0.8
        
        if re.search(r'(debug|fix|error|issue|problem|not working)', query, re.I):
            intents["code_debugging"] = 0.8
        
        if re.search(r'(search|find|look up|information about|tell me about)', query, re.I):
            intents["information_retrieval"] = 0.8
        
        # If no specific intent is detected, assume it's a general question
        if all(score == 0.0 for score in intents.values()):
            intents["general_question"] = 0.6
        
        return intents
    
    def _extract_code_snippets(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract code snippets from the query and context.
        
        Returns:
            A list of dictionaries containing code snippets and their languages
        """
        snippets = []
        
        # Extract code blocks from markdown-style code blocks
        code_block_pattern = r'```(\w*)\n(.*?)\n```'
        for match in re.finditer(code_block_pattern, query, re.DOTALL):
            language = match.group(1) or "unknown"
            code = match.group(2)
            snippets.append({"language": language, "code": code})
        
        # Check if there's code in the context
        if context and "code" in context:
            snippets.append({
                "language": context.get("language", "unknown"),
                "code": context["code"]
            })
        
        return snippets
    
    def _determine_tools_needed(self, intent_analysis: Dict[str, float], code_snippets: List[Dict[str, Any]]) -> List[str]:
        """
        Determine which tools are needed based on intent and code snippets.
        """
        tools_needed = []
        
        # Check if we need web search
        if intent_analysis["information_retrieval"] > 0.5:
            tools_needed.append("web_search")
        
        # Check if we need code generation
        if intent_analysis["code_generation"] > 0.5:
            tools_needed.append("code_generation")
        
        # Check if we need code analysis
        if intent_analysis["code_explanation"] > 0.5 and code_snippets:
            tools_needed.append("code_analysis")
        
        # Check if we need deep reasoning
        if intent_analysis["code_debugging"] > 0.5 or (
            intent_analysis["general_question"] > 0.5 and 
            any(intent > 0.3 for intent in intent_analysis.values())
        ):
            tools_needed.append("reasoning")
        
        return tools_needed
    
    def _determine_agents_needed(self, intent_analysis: Dict[str, float], code_snippets: List[Dict[str, Any]]) -> List[str]:
        """
        Determine which agents are needed based on intent and code snippets.
        """
        agents_needed = []
        
        # Check if we need the code explainer
        if intent_analysis["code_explanation"] > 0.5:
            agents_needed.append("explainer")
        
        # Check if we need the code builder
        if intent_analysis["code_generation"] > 0.5:
            agents_needed.append("builder")
        
        # Check if we need the code compiler
        if intent_analysis["code_debugging"] > 0.5 or (code_snippets and intent_analysis["code_generation"] > 0.3):
            agents_needed.append("compiler")
        
        # Check if we need the code finalizer
        if "builder" in agents_needed or "compiler" in agents_needed:
            agents_needed.append("finalizer")
        
        return agents_needed
    
    def _get_tool_params(self, tool_name: str, observation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get parameters for a specific tool based on the observation.
        """
        query = observation["query"]
        
        if tool_name == "web_search":
            return {"query": query}
        
        elif tool_name == "code_generation":
            return {
                "specification": query,
                "language": self._detect_language(query, observation["code_snippets"])
            }
        
        elif tool_name == "code_analysis":
            if observation["code_snippets"]:
                snippet = observation["code_snippets"][0]
                return {
                    "code": snippet["code"],
                    "language": snippet["language"],
                    "level_of_detail": "medium"
                }
            return {"query": query}
        
        elif tool_name == "reasoning":
            return {
                "problem": query,
                "context": observation["context"]
            }
        
        # Default case
        return {"query": query}
    
    def _get_agent_params(self, agent_name: str, observation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get parameters for a specific agent based on the observation.
        """
        query = observation["query"]
        context = observation["context"]
        code_snippets = observation["code_snippets"]
        
        if agent_name == "explainer":
            agent_context = dict(context)
            agent_context["code_snippets"] = code_snippets
            return {
                "query": query,
                "context": agent_context
            }
        
        elif agent_name == "builder":
            return {
                "query": query,
                "context": context
            }
        
        elif agent_name == "compiler":
            agent_context = dict(context)
            agent_context["code_snippets"] = code_snippets
            return {
                "query": query,
                "context": agent_context
            }
        
        elif agent_name == "finalizer":
            return {
                "query": query,
                "context": context,
                "results": observation.get("previous_results", [])
            }
        
        # Default case
        return {
            "query": query,
            "context": context
        }
    
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
                if snippet["language"] and snippet["language"] != "unknown":
                    return snippet["language"]
