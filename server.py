import os
import psycopg2
import psycopg2.extras
from fastmcp import FastMCP

mcp = FastMCP(
    "Neon PostgreSQL Explorer",
    instructions=(
        "Use this server to explore and query your Neon PostgreSQL database. "
        "You can list tables, view their structure, and run read-only SELECT queries."
    ),
)


def get_connection():
    """Create a new database connection."""
    url = os.environ.get("DATABASE_URL") or os.environ.get("NEONDATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL environment variable is not set.")
    return psycopg2.connect(url)


@mcp.tool
def list_tables() -> list[str]:
    """List all tables in the database."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
                """
            )
            return [row[0] for row in cur.fetchall()]


@mcp.tool
def describe_table(table_name: str) -> list[dict]:
    """
    Show the columns and data types for a given table.

    Args:
        table_name: The name of the table to describe.
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = %s
                ORDER BY ordinal_position
                """,
                (table_name,),
            )
            return [dict(row) for row in cur.fetchall()]


@mcp.tool
def sample_table(table_name: str, limit: int = 5) -> list[dict]:
    """
    Return a sample of rows from a table.

    Args:
        table_name: The name of the table to sample.
        limit: Number of rows to return (max 50).
    """
    limit = min(limit, 50)
    # Table name is validated against existing tables before use
    allowed_tables = _get_table_names()
    if table_name not in allowed_tables:
        raise ValueError(f"Table '{table_name}' does not exist.")

    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f'SELECT * FROM "{table_name}" LIMIT %s', (limit,))
            return [dict(row) for row in cur.fetchall()]


@mcp.tool
def query_database(sql: str) -> list[dict]:
    """
    Run a read-only SELECT query on the database and return the results.
    Only SELECT statements are allowed.

    Args:
        sql: A valid SQL SELECT statement.
    """
    # Security: only allow read-only queries
    normalized = sql.strip().upper()
    if not normalized.startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed.")

    forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER", "TRUNCATE", "GRANT", "REVOKE"]
    for keyword in forbidden:
        if keyword in normalized:
            raise ValueError(f"Forbidden keyword '{keyword}' found in query.")

    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql)
            rows = cur.fetchmany(200)  # Cap at 200 rows for safety
            return [dict(row) for row in rows]


def _get_table_names() -> set[str]:
    """Internal helper: fetch all public table names."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            )
            return {row[0] for row in cur.fetchall()}


if __name__ == "__main__":
    mcp.run()
