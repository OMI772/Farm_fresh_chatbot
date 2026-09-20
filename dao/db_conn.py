from config.settings import DATABASE_URL
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool


class DBConnection:
    """Manages a PostgreSQL connection pool for LangGraph checkpoint storage."""

    def __init__(self) -> None:
        self.pool = ConnectionPool(
            conninfo=DATABASE_URL,
            min_size=1,
            max_size=5,
            kwargs={
                "autocommit": True,
                "prepare_threshold": 0,
                "row_factory": dict_row,
            },
        )

    def get_connection_pool(self) -> ConnectionPool:
        return self.pool
