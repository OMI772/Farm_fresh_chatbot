from langchain_ollama import ChatOllama
from langgraph.prebuilt import ToolNode

from graph.state import ChatState
from graph.tools import TOOL_LIST

model = ChatOllama(model="llama3.2")
model_with_tools = model.bind_tools(TOOL_LIST)
tool_node = ToolNode(TOOL_LIST)


def generate_response(state: ChatState) -> dict:
    """Invoke the LLM with tool bindings and append the response to state."""
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}
