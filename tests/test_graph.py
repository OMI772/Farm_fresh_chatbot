"""Tests for the FarmFresh chatbot graph."""

from langchain_core.messages import HumanMessage

from graph.workflow import workflow


def test_workflow_invoke() -> None:
    """Smoke test: workflow returns a response for a simple question."""
    config = {"configurable": {"thread_id": "test-thread"}}
    response = workflow.invoke(
        {"messages": [HumanMessage(content="What is the capital of India?")]},
        config,
    )
    assert response["messages"]
    assert response["messages"][-1].content
