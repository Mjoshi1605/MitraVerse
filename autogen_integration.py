import autogen
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
import os
import together
import re
from typing import Dict, Any, List, Optional

# Set up TogetherAI API key
os.environ["TOGETHER_API_KEY"] = "your_together_api_key_here"  # Replace with your actual key

# Configure the TogetherAI model
together_config = {
    "model": "togethercomputer/llama-2-70b-chat",  # You can change this to any model available on TogetherAI
    "temperature": 0.7,
    "max_tokens": 2000
}

# Create a configuration list for AutoGen
config_list = [
    {
        "model": together_config["model"],
        "api_key": os.environ["TOGETHER_API_KEY"],
        "api_base": "https://api.together.xyz/v1",
        "api_type": "openai"
    }
]

class AutoGenManager:
    """
    Manager class for AutoGen agents to simplify tasks in MitraVerse.
    """
    
    def __init__(self):
        self.config_list = config_list
        
        # Initialize agents
        self.assistant = AssistantAgent(
            name="coding_assistant",
            llm_config={"config_list": self.config_list},
            system_message="You are a helpful coding assistant. You can write code, explain code, and help debug issues."
        )
        
        self.user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config={"work_dir": "workspace"}
        )
        
        # Specialized agents
        self.coder = AssistantAgent(
            name="coder",
            llm_config={"config_list": self.config_list},
            system_message="You are a code generation specialist. Your task is to write clean, efficient, and well-documented code based on requirements."
        )
        
        self.explainer = AssistantAgent(
            name="explainer",
            llm_config={"config_list": self.config_list},
            system_message="You are a code explanation specialist. Your task is to explain code in a clear and understandable way."
        )
        
        self.debugger = AssistantAgent(
            name="debugger",
            llm_config={"config_list": self.config_list},
            system_message="You are a debugging specialist. Your task is to identify and fix issues in code."
        )
    
    def generate_code(self, requirements: str, language: str = "python") -> str:
        """
        Generate code based on requirements using AutoGen.
        
        Args:
            requirements: The requirements for the code
            language: The programming language to use
            
        Returns:
            The generated code
        """
        task = f"Generate {language} code for the following requirements:\n{requirements}\n\nProvide only the code without explanations."
        
        # Create a chat between user proxy and coder
        self.user_proxy.initiate_chat(
            self.coder,
            message=task
        )
        
        # Extract code from the chat history
        chat_history = self.user_proxy.chat_messages[self.coder.name]
        code = self._extract_code_from_messages(chat_history, language)
        
        return code
    
    def explain_code(self, code: str, language: str = "python") -> str:
        """
        Explain code using AutoGen.
        
        Args:
            code: The code to explain
            language: The programming language of the code
            
        Returns:
            The explanation
        """
        task = f"Explain the following {language} code in detail:\n\n```{language}\n{code}\n```"
        
        # Create a chat between user proxy and explainer
        self.user_proxy.initiate_chat(
            self.explainer,
            message=task
        )
        
        # Extract explanation from the chat history
        chat_history = self.user_proxy.chat_messages[self.explainer.name]
        explanation = chat_history[-1]["content"]
        
        return explanation
    
    def debug_code(self, code: str, error_message: Optional[str] = None, language: str = "python") -> Dict[str, str]:
        """
        Debug code using AutoGen.
        
        Args:
            code: The code to debug
            error_message: Optional error message
            language: The programming language of the code
            
        Returns:
            Dictionary containing debugged code and explanation
        """
        task = f"Debug the following {language} code:\n\n```{language}\n{code}\n```"
        
        if error_message:
            task += f"\n\nError message:\n{error_message}"
        
        # Create a chat between user proxy and debugger
        self.user_proxy.initiate_chat(
            self.debugger,
            message=task
        )
        
        # Extract debugged code from the chat history
        chat_history = self.user_proxy.chat_messages[self.debugger.name]
        result = self._extract_code_from_messages(chat_history, language)
        explanation = chat_history[-1]["content"]
        
        return {
            "debugged_code": result,
            "explanation": explanation
        }
    
    def collaborative_task(self, task: str) -> str:
        """
        Perform a collaborative task using multiple agents.
        
        Args:
            task: The task description
            
        Returns:
            The result of the collaborative task
        """
        # Create a group chat
        groupchat = autogen.GroupChat(
            agents=[self.user_proxy, self.coder, self.explainer, self.debugger],
            messages=[],
            max_round=12
        )
        
        manager = autogen.GroupChatManager(groupchat=groupchat)
        
        # Start the group chat
        self.user_proxy.initiate_chat(
            manager,
            message=task
        )
        
        # Get the final result
        result = groupchat.messages[-1]["content"]
        
        return result
    
    def _extract_code_from_messages(self, messages: List[Dict[str, Any]], language: str) -> str:
        """
        Extract code from chat messages.
        
        Args:
            messages: The chat messages
            language: The programming language
            
        Returns:
            The extracted code
        """
        code = ""
        
        # Look for the most recent code block in the messages
        for message in reversed(messages):
            content = message.get("content", "")
            
            # Extract code blocks
            code_blocks = re.findall(r'```(?:' + language + r')?\n(.*?)\n```', content, re.DOTALL)
            
            if code_blocks:
                code = code_blocks[0]
                break
        
        return code

# Example usage
if __name__ == "__main__":
    autogen_manager = AutoGenManager()
    
    # Generate code
    code = autogen_manager.generate_code(
        "Create a function that calculates the Fibonacci sequence up to n terms",
        "python"
    )
    print("Generated code:")
    print(code)
    
    # Explain code
    explanation = autogen_manager.explain_code(code)
    print("\nExplanation:")
    print(explanation)
    
    # Collaborative task
    result = autogen_manager.collaborative_task(
        "Design a simple web scraper that extracts headlines from a news website"
    )
    print("\nCollaborative task result:")
    print(result)
