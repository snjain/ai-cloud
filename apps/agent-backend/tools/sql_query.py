"""SQL query tool for read-only queries on Supabase."""
from supabase import Client
import json
import re


async def execute_sql_query_tool(supabase: Client, sql_query: str) -> str:
    """Execute a read-only SQL query via Supabase RPC.

    Args:
        supabase: The Supabase client.
        sql_query: The SQL query to execute.

    Returns:
        JSON-formatted query results or error message.
    """
    sql_query = sql_query.strip()
    write_operations = ["INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER", "TRUNCATE", "GRANT", "REVOKE"]
    upper_query = sql_query.upper()

    for op in write_operations:
        if re.search(rf"\b{op}\b", upper_query):
            return f"Error: Write operation '{op}' detected. Only read-only queries are allowed."

    try:
        result = supabase.rpc(
            "execute_custom_sql",
            {"sql_query": sql_query},
        ).execute()

        if result.data and isinstance(result.data, dict) and "error" in result.data:
            return f"SQL Error: {result.data['error']}"

        return json.dumps(result.data, indent=2)
    except Exception as e:
        return f"Error executing SQL query: {e}"
