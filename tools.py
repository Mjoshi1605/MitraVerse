from langchain_core.tools import tool
from langchain_together import ChatTogether
import os

# --- Execute Code ---
@tool
def execute_code(code: str) -> str:
    """ Execute a code snippet and return the resulting local variable or ant error."""
    exec_locals = {}
    try:
        exec(code, {}, exec_locals)
        return str(exec_locals)
    except Exception as e:
        return str(e)

# --- Explain Code ---
@tool
def explain_code(code: str) -> str:
    """Explain what a given code snippet does using an llm"""
    llm = ChatTogether(
        model="meta-llama/Meta-Llama-3-8B-Instruct",
        together_api_key=os.environ["together_api_key"]
    )
    system_prompt = "You are a  code explainer. Explain clearly and concisely what the code does."
    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Explain this  code:\n{code}"}
    ])
    return response.content

# --- Web Search ---
@tool
def web_search(query: str) -> str:
    """Perform a web search using the Tavily API and return the top results's content."""
    from tavily import TavilyClient
    tavily = TavilyClient(api_key=os.environ["tavily_api_key"])
    try:
        return tavily.search(query=query)['results'][0]['content']
    except Exception as e:
        return f"Error from Tavily: {e}"

# --- Deep Think ---
@tool
def deep_think(prompt: str) -> str:
    """Use an LLM to generate a deeply reasoned response to a prompt."""
    llm = ChatTogether(
        model="meta-llama/Meta-Llama-3-8B-Instruct",
        together_api_key=os.environ["together_api_key"]
    )
    system_prompt = "You are a thoughtful reasoning assistant. Think deeply and provide insightful reasoning for the input given by the user. And also what are the steps you need to do as per the user input."
    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ])
    return response.content

# --- Analyze Code ---
@tool
def analyze_code(code: str) -> str:
    """Analyze the structure and type of code"""
    llm = ChatTogether(
        model="meta-llama/Meta-Llama-3-8B-Instruct",
        together_api_key=os.environ["together_api_key"]
    )
    system_prompt = "You are a code structure analyzer. Determine what kind of code this is and its structure."
    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Analyze this code:\n{code}"}
    ])
    return response.content

# --- Code Generator ---
@tool
def code_generator(prompt: str) -> str:
    """ Generate code based on the natural language description using an LLM"""
    llm = ChatTogether(
        model="meta-llama/Meta-Llama-3-8B-Instruct",
        together_api_key=os.environ["together_api_key"]
    )
    system_prompt = "You are a Python code generator. Generate efficient and clean Python code."
    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Write Python code based on this requirement:\n{prompt}"}
    ])
    return response.content

# --- Return All Tools ---
def get_all_tools():
    return [
        execute_code,
        explain_code,
        web_search,
        deep_think,
        analyze_code,
        code_generator,
    ]
