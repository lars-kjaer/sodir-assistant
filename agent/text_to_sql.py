"""
text_to_sql.py
--------------
The Text-to-SQL agent. Turns a natural-language question into SQL,
runs it against the SODIR database, and phrases the result as an answer.

Database access (schema introspection + query execution) lives in
database.py; this module handles the LLM interaction and orchestration.
"""

import os
from groq import Groq
from dotenv import load_dotenv
from agent.database import get_schema_description, run_query

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = "llama-3.3-70b-versatile"

# Schema is read live from the database, so it always reflects the
# actual gold tables and never drifts out of sync.
SCHEMA = get_schema_description()

SYSTEM_PROMPT = f"""
You are a data analyst for Norwegian Continental Shelf petroleum data.
Given a user question, generate a valid SQLite SQL query to answer it.

You have access to a SQLite database with the following tables:

{SCHEMA}

Table relationships:
- gold_wellbore and gold_field_sales_production_month join on npdid_field
- gold_field_sales_production_month has one row per field per month; SUM across months for annual totals

Important guidance:
- Volumes are stored in Sm3 and pre-converted to bbl (liquids) and scf (gas). Use whichever unit the user asks for.
- All depths are in metres. Convert feet to metres (1 ft = 0.3048 m) if asked in feet.
- Filter company and field names with LIKE and wildcards because exact names vary.
- drilling_operator is who drilled the wellbore, which may differ from the current field operator.

Rules:
- Return ONLY the SQL query, no explanation, no markdown, no backticks
- Use exact column and table names as listed above
- If the question cannot be answered, return: SELECT 'Data not available' as answer
"""


def generate_sql(question: str) -> str:
    """Ask the LLM to translate a natural-language question into SQL."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        temperature=0,  # deterministic: same question -> same SQL
    )
    sql = response.choices[0].message.content.strip()

    # Safety net: strip markdown code fences if the model adds them
    # despite being told not to.
    if sql.startswith("```"):
        sql = sql.split("```")[1].replace("sql", "", 1).strip()
    return sql


def format_answer(question: str, columns, rows) -> str:
    """Ask the LLM to phrase the raw query result as a natural answer."""
    result_text = str([dict(zip(columns, row)) for row in rows])
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": f"""The user asked: "{question}"

The query returned this result:
{result_text}

Write a clear, concise natural language answer to the user's question based on this result.
Do not mention SQL, queries, or databases. Just answer the question directly."""},
        ],
        temperature=0,
    )
    return response.choices[0].message.content.strip()


def ask(question: str):
    """Full pipeline: question -> SQL -> execute -> natural-language answer."""
    sql = generate_sql(question)
    print(f"\nGenerated SQL:\n{sql}\n")
    try:
        columns, rows = run_query(sql)
        if not rows:
            return "No results found."
        return format_answer(question, columns, rows)
    except Exception as e:
        # The caller sees the error and the offending SQL, rather than a crash.
        return f"Query failed: {e}\nSQL: {sql}"


if __name__ == "__main__":
    print("SODIR Assistant")
    print("---------------")
    while True:
        question = input("\nAsk a question (or 'quit'): ")
        if question.lower() == "quit":
            break
        answer = ask(question)
        print(f"\nAnswer: {answer}")