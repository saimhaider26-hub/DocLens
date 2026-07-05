import sqlite3
import requests
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "company_data.db")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

def get_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    schema_info = ""
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [row[1] for row in cursor.fetchall()]
        schema_info += f"Table: {table_name}, Columns: {', '.join(columns)}\n"
    conn.close()
    return schema_info

def generate_sql(question):
    schema = get_schema()
    prompt = f"""You are a SQLite expert. Given the following database schema, write a SQL query to answer the user's question.
    Use the exact table and column names provided in the schema.
    Return ONLY the raw SQL query, nothing else. No markdown formatting, no explanations.

    Schema:
    {schema}

    Question: {question}
    """
    
    payload = {"model": "llama3.1", "prompt": prompt, "stream": False}
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        sql_query = response.json()["response"].strip()
        return sql_query.replace("```sql", "").replace("```", "").strip()
    except Exception as e:
        return f"Error: {str(e)}"

def execute_sql(sql_query):
    if not sql_query.upper().startswith("SELECT"):
        return "Guardrail Blocked: Only SELECT queries are allowed."
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        return f"Database error: {str(e)}"

def run_sql_agent(question):
    sql_query = generate_sql(question)
    if "Error" in sql_query:
        return {"query": "Failed", "results": sql_query}
    results = execute_sql(sql_query)
    return {"query": sql_query, "results": results}

if __name__ == "__main__":
    test_question = "How many invoices are PAID?"
    print("Testing SQL Agent...")
    result = run_sql_agent(test_question)
    print(f"Generated SQL: {result.get('query')}")
    print(f"Results: {result.get('results')}")