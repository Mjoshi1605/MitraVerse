from langchain.agents import initialize_agent, AgentType
from tools import get_all_tools
from langchain_together import ChatTogether
import os

tools = get_all_tools()
llm = ChatTogether(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    together_api_key=os.environ["together_api_key"]
)
agent = initialize_agent(tools=tools, llm=llm, agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

def router_node(state: dict) -> dict:
    user_input = state["input"]
    result = agent.run(user_input)
    route = decide_route_from_output(result)
    return {**state, "output": result, "route": route}

def decide_route_from_output(output: str) -> str:
    output = output.lower()
    if "explain" in output:
        return "CodeExplainer"
    elif "generate" in output or "code:" in output:
        return "CodeGenerator"
    elif "execution result" in output or "run this code" in output:
        return "ExecuteCode"
    elif "thought" in output or "reason" in output:
        return "DeepThink"
    else:
        return "END"
