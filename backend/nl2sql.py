from dotenv import load_dotenv
load_dotenv()

import os
import re
from groq import Groq
from backend.rag_pipeline import retrieve_context, save_to_history

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

GROQ_MODEL = "llama-3.3-70b-versatile"


def build_prompt(question: str, context: str) -> str:
    """
    Builds the final prompt sent to Llama-3.
    Schema context + past examples + user question.
    """
    return f"""You are an expert SQL query generator. Your job is to convert natural language questions into accurate MySQL queries.

You will be given:
1. The database schema (table names, columns, data types)
2. The user's question in plain English

STRICT RULES:
- Return ONLY the SQL query, nothing else
- No explanations, no markdown, no backticks
- Always use correct table and column names from the schema
- Use JOINs when data spans multiple tables
- Never use DROP, DELETE, UPDATE, INSERT or any destructive statement
- End every query with a semicolon

DATABASE SCHEMA:
{context}

USER QUESTION:
{question}

SQL QUERY:"""


def extract_sql(raw_output: str) -> str:
    """
    Cleans the LLM output to extract pure SQL.
    Handles cases where LLM adds extra text despite instructions.
    """
    # Remove markdown code blocks if present
    raw_output = re.sub(r"```sql", "", raw_output, flags=re.IGNORECASE)
    raw_output = re.sub(r"```", "", raw_output)

    # Take only the first SQL statement
    lines = raw_output.strip().split("\n")
    sql_lines = []
    for line in lines:
        sql_lines.append(line)
        if line.strip().endswith(";"):
            break

    return " ".join(sql_lines).strip()


def is_safe_sql(sql: str) -> bool:
    """
    Basic safety check — blocks destructive SQL statements.
    """
    dangerous = ["DROP", "DELETE", "UPDATE", "INSERT",
                 "ALTER", "TRUNCATE", "CREATE", "REPLACE"]
    sql_upper = sql.upper()
    for keyword in dangerous:
        if keyword in sql_upper:
            return False
    return True


def generate_sql(question: str) -> dict:
    """
    Main function — takes a natural language question,
    retrieves schema context via RAG, generates SQL via Groq.
    Returns dict with question, context, sql, and status.
    """
    print(f"\nQuestion: {question}")

    # Step 1: Retrieve relevant schema context via RAG
    print("Retrieving context...")
    context = retrieve_context(question, k=3)

    # Step 2: Build prompt
    prompt = build_prompt(question, context)

    # Step 3: Call Groq Llama-3
    print("Generating SQL...")
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0,        # 0 = deterministic, more accurate SQL
        max_tokens=300
    )

    raw_output = response.choices[0].message.content
    print(f"Raw output: {raw_output}")

    # Step 4: Extract clean SQL
    sql = extract_sql(raw_output)
    print(f"Extracted SQL: {sql}")

    # Step 5: Safety check
    if not is_safe_sql(sql):
        return {
            "question": question,
            "context": context,
            "sql": None,
            "status": "error",
            "message": "Unsafe SQL detected and blocked."
        }

    # Step 6: Save to history for future RAG improvement
    save_to_history(question, sql)

    return {
        "question": question,
        "context": context,
        "sql": sql,
        "status": "success",
        "message": "SQL generated successfully."
    }


if __name__ == "__main__":
    test_questions = [
        "show me all employees in IT department",
        "what is the total salary of all employees",
        "show me top 3 employees with highest salary",
        "how many employees are active",
        "show me all sales from the North region"
    ]

    for question in test_questions:
        print("\n" + "="*50)
        result = generate_sql(question)
        print(f"Final SQL: {result['sql']}")
        print(f"Status: {result['status']}")