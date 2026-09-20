from graph.workflow import checkpointer


class ThreadService:
    """Retrieve conversation thread IDs persisted by the LangGraph checkpointer."""

    def __init__(self) -> None:
        self.checkpointer = checkpointer

    def get_thread_ids(self) -> list[str]:
        thread_ids: set[str] = set()

        for checkpoint in self.checkpointer.list(None):
            thread_id = checkpoint.config["configurable"]["thread_id"]
            thread_ids.add(thread_id)

        return list(thread_ids)
