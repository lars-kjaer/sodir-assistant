"""
database.py
-----------
All database access for SODIR assistant lives here.

Module does two jobs:
  1. Describes database to LLM (schema introspection)
  2. Run SQL LLM generate

"""

import sqlite3

DB_PATH = "data/sodir.db"

def get_connection():
    """
    Open and return connection to SQLite database.
    """
    return sqlite3.connect(DB_PATH)


def get_schema_description(table_prefix: str = "gold_") -> str:
    """
    Build text description of database schema for LLM.

    Instead of hardcoding list of tables and columns, this reads
    structure directly from database (introspection).

    Only tables whose name starts with `table_prefix` included.
    Default is 'gold_' because agent should only ever query curated gold 
    tables, never raw bronze or silver layers.

    Returns a string like:
        Table: gold_wellbore
        - wellbore_name: text
        - wellbore_status: text
        ...
    """
    conn = get_connection()
    cursor = conn.cursor()

    # --- Step 1: find every table matching the prefix --------------------
    #
    # `sqlite_master` is a built-in table that SQLite maintains
    # automatically. It is a catalogue of everything in the database:
    # tables, views, indexes. We query it for the names of all tables
    # whose name begins with the prefix (e.g. 'gold_').

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name LIKE ?",
        (f"{table_prefix}%",),  # the % is a wildcard: "starts with gold_"
    )

    # fetchall() returns a list of rows, each row a tuple like ('gold_wellbore',).
    # We pull out the first element of each row to get a clean list of names.
    tables = [row[0] for row in cursor.fetchall()]

    # --- Step 2: describe each table's columns ---------------------------
    lines = []
    for table in tables:
        lines.append(f"\nTable: {table}")

        # `PRAGMA table_info(...)` is a special SQLite command that returns
        # one row per column. Each row is a tuple:
        #   (cid, name, type, notnull, default_value, primary_key)
        # We only need the name (index 1) and the type (index 2).
        cursor.execute(f"PRAGMA table_info({table})")
        for col in cursor.fetchall():
            col_name = col[1]
            col_type = col[2]
            lines.append(f"- {col_name}: {col_type.lower()}")

    conn.close()

    # Join all the lines into one string, ready to drop into the LLM prompt.
    return "\n".join(lines)


def run_query(sql: str):
    """Execute a SQL query and return its column names and rows.

    Returns a tuple of (columns, rows):
      - columns: list of column-name strings
      - rows:    list of row tuples

    No error handling here on purpose - the caller decides how to
    handle a failed query (e.g. show the user, or retry).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql)

    # After a SELECT, `cursor.description` holds metadata about the
    # result columns. The first element of each entry is the column name.
    columns = [desc[0] for desc in cursor.description]

    rows = cursor.fetchall()
    conn.close()
    return columns, rows