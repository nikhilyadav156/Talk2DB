from dotenv import load_dotenv
load_dotenv()

import pandas as pd
from sqlalchemy import text
from backend.db_config import get_engine


def execute_query(sql: str) -> dict:
    """
    Executes a SQL query on MySQL and returns results
    as a pandas DataFrame.
    """
    engine = get_engine()

    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            rows = result.fetchall()
            columns = list(result.keys())

            if not rows:
                return {
                    "status": "success",
                    "message": "Query executed but returned no results.",
                    "dataframe": pd.DataFrame(),
                    "row_count": 0,
                    "columns": columns
                }

            df = pd.DataFrame(rows, columns=columns)

            return {
                "status": "success",
                "message": f"Query returned {len(df)} row(s).",
                "dataframe": df,
                "row_count": len(df),
                "columns": columns
            }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "dataframe": pd.DataFrame(),
            "row_count": 0,
            "columns": []
        }


def run_pipeline(question: str) -> dict:
    """
    Full pipeline — question → SQL → execute → return results.
    Imports nl2sql here to avoid circular imports.
    """
    from backend.nl2sql import generate_sql

    # Step 1: Generate SQL
    nl2sql_result = generate_sql(question)

    if nl2sql_result["status"] == "error":
        return {
            "status": "error",
            "question": question,
            "sql": None,
            "message": nl2sql_result["message"],
            "dataframe": pd.DataFrame(),
            "row_count": 0
        }

    sql = nl2sql_result["sql"]

    # Step 2: Execute SQL
    exec_result = execute_query(sql)

    return {
        "status": exec_result["status"],
        "question": question,
        "sql": sql,
        "message": exec_result["message"],
        "dataframe": exec_result["dataframe"],
        "row_count": exec_result["row_count"],
        "columns": exec_result["columns"]
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
        print(f"Question: {question}")
        result = run_pipeline(question)
        print(f"SQL: {result['sql']}")
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        if not result["dataframe"].empty:
            print(result["dataframe"].to_string(index=False))