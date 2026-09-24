from langchain_ollama import ChatOllama
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from graph.state import ChatState
from graph.tools import TOOL_LIST

load_dotenv()
groq_base_url = os.getenv("GROQ_BASE_URL")
groq_api_key = os.getenv("GROQ_API_KEY")
# model = ChatOllama(model="llama3.2")
model = ChatOpenAI(api_key = groq_api_key, base_url = groq_base_url, model = "openai/gpt-oss-120b")
model_with_tools = model.bind_tools(TOOL_LIST)
tool_node = ToolNode(TOOL_LIST)


def generate_response(state: ChatState) -> dict:
    """Invoke the LLM with tool bindings and append the response to state."""
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}
