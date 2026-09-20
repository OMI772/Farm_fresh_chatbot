"""FarmFresh AI — Streamlit chat interface."""

from pathlib import Path
import uuid

import streamlit as st
from langchain_core.messages import AIMessage, AIMessageChunk

from graph.workflow import workflow
from services.thread_service import ThreadService

ASSETS_DIR = Path(__file__).parent / "assets"
CSS_PATH = ASSETS_DIR / "styles.css"


def load_custom_css() -> None:
    """Inject custom theme styles into the Streamlit app."""
    css = CSS_PATH.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def init_session_state() -> None:
    """Initialize Streamlit session state for chat threads and messages."""
    if "threads" not in st.session_state:
        st.session_state.threads = []

    if "current_thread_id" not in st.session_state:
        thread_id = str(uuid.uuid4())
        st.session_state.current_thread_id = thread_id
        st.session_state.threads.append(thread_id)

    if "messages" not in st.session_state:
        st.session_state.messages = []


def create_new_chat() -> None:
    """Start a fresh conversation thread."""
    thread_id = str(uuid.uuid4())
    st.session_state.current_thread_id = thread_id
    st.session_state.messages = []
    st.session_state.threads.append(thread_id)


def load_thread(thread_id: str) -> None:
    """Load an existing conversation from the LangGraph checkpointer."""
    config = {"configurable": {"thread_id": thread_id}}
    state = workflow.get_state(config)
    st.session_state.current_thread_id = thread_id
    st.session_state.messages = state.values.get("messages", [])


def render_sidebar() -> None:
    """Render chat history and new-chat controls in the sidebar."""
    with st.sidebar:
        st.title("FarmFresh")

        if st.button("+ New Chat", use_container_width=True):
            create_new_chat()
            st.rerun()

        st.divider()

        thread_service = ThreadService()
        for thread in thread_service.get_thread_ids():
            if st.button(thread, key=f"thread_{thread}", use_container_width=True):
                load_thread(thread)
                st.rerun()


def render_chat_history() -> None:
    """Display messages for the current thread."""
    for message in st.session_state.messages:
        if message.type == "human":
            role = "user"
        elif message.type == "ai" and message.content:
            role = "assistant"
        else:
            continue

        with st.chat_message(role):
            st.markdown(message.content)


def handle_user_input(prompt: str) -> None:
    """Process user input and stream the assistant response."""
    thread_id = st.session_state.current_thread_id
    config = {"configurable": {"thread_id": thread_id}}

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        for message_chunk, _metadata in workflow.stream(
            {"messages": [("user", prompt)]},
            config,
            stream_mode="messages",
        ):
            if not isinstance(message_chunk, (AIMessage, AIMessageChunk)):
                continue
            if not message_chunk.content:
                continue

            full_response += message_chunk.content
            response_placeholder.markdown(full_response)

    state = workflow.get_state(config)
    st.session_state.messages = state.values.get("messages", [])

    if not full_response:
        for message in reversed(st.session_state.messages):
            if isinstance(message, AIMessage) and message.content:
                response_placeholder.markdown(message.content)
                break


def main() -> None:
    st.set_page_config(
        page_title="FarmFresh AI",
        page_icon="🍊",
        layout="wide",
    )
    load_custom_css()
    init_session_state()

    st.title("🍊 FarmFresh AI")
    st.caption("Your intelligent farming & food assistant")

    render_sidebar()
    render_chat_history()

    if prompt := st.chat_input("Ask FarmFresh anything..."):
        handle_user_input(prompt)


if __name__ == "__main__":
    main()
