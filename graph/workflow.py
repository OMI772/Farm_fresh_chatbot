from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition

from dao.db_conn import DBConnection
from graph.nodes import generate_response, tool_node
from graph.state import ChatState

connection_pool = DBConnection().get_connection_pool()
checkpointer = PostgresSaver(connection_pool)
checkpointer.setup()

graph_builder = StateGraph(ChatState)
graph_builder.add_node("generate_response", generate_response)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "generate_response")
graph_builder.add_conditional_edges("generate_response", tools_condition)
graph_builder.add_edge("tools", "generate_response")

workflow = graph_builder.compile(checkpointer=checkpointer)
