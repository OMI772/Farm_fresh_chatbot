from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class ChatState(TypedDict):
    """State schema for the FarmFresh chatbot LangGraph workflow."""

    messages: Annotated[list[BaseMessage], add_messages]
