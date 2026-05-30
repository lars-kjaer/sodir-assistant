import os
import sqlite3
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

DB_PATH = "data/sodir.db"
MODEL_NAME = "gemini-2.5-flash"

SCHEMA = """
Table: gold_wellbore
- wellbore_name: text, official wellbore name
- well_name: text, parent well name
- wellbore_type: text, EXPLORATION, DEVELOPMENT or OTHER
- wellbore_purpose: text, e.g. WILDCAT, APPRAISAL, PRODUCTION, INJECTION
- wellbore_status: text, e.g. DRILLING, PRODUCING, P&A, PLUGGED, INJECTING
- wellbore_content: text, e.g. OIL, GAS, DRY
- drilling_operator: text, company name
- wellbore_production_licence: text
- field_name: text
- wellbore_main_area: text, NORTH SEA, NORWEGIAN SEA or BARENTS SEA
- wellbore_entry_year: integer
- wellbore_completion_year: integer
- wellbore_spud_date: text
- wellbore_completed_date: text
- wellbore_drilling_days: integer
- wellbore_water_depth_meters: real
- wellbore_tvd_meters: real
- wellbore_md_meters: real
- wellbore_subsea_flag: text, YES or NO
- wellbore_multilateral_flag: text, YES or NO
- wellbore_plugged_date: text
- wellbore_plug_and_abandon_date: text
- wellbore_oldest_penetrated_formation: text
- wellbore_oldest_penetrated_age: text
- wellbore_1st_level_with_hc_formation: text
- wellbore_1st_level_with_hc_age: text
- npdid_wellbore: integer, unique wellbore ID
- npdid_field: integer, foreign key to field
- npdid_discovery: integer, foreign key to discovery
"""

SYSTEM_PROMPT = f"""
You are a data analyst for Norwegian Continental Shelf petroleum data.
Given a user question, generate a valid SQLite SQL query to answer it.

You have access to a SQLite database with the following table:

{SCHEMA}

Rules:
- Return ONLY the SQL query, no explanation, no markdown, no backticks
- Use exact column and table names as listed above
- If the question cannot be answered from the available data, return: SELECT 'Data not available' as answer
"""

def generate_sql(question: str) -> str:
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=f"{SYSTEM_PROMPT}\n\nUser question: {question}"
    )
    return response.text.strip()

def run_query(sql: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(sql)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return columns, rows

def ask(question: str):
    sql = generate_sql(question)
    print(f"\nGenerated SQL:\n{sql}\n")
    try:
        columns, rows = run_query(sql)
        if not rows:
            return "No results found."
        result = []
        for row in rows:
            result.append(dict(zip(columns, row)))
        return result
    except Exception as e:
        return f"Query failed: {e}\nSQL: {sql}"

if __name__ == "__main__":
    print("SODIR Wellbore Assistant")
    print("------------------------")
    while True:
        question = input("\nAsk a question (or 'quit'): ")
        if question.lower() == "quit":
            break
        answer = ask(question)
        print(f"\nAnswer: {answer}")