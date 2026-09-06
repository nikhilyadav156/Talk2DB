from dotenv import load_dotenv
load_dotenv()

import json
import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.executor import run_pipeline

HISTORY_FILE = "vector_store/query_history.json"

app = FastAPI(
    title="Talk2DB API",
    description="Natural Language to SQL powered by RAG + Groq Llama-3",
    version="1.0.0"
)

# Allow Streamlit frontend to talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    status: str
    question: str
    sql: str | None
    message: str
    data: list
    columns: list
    row_count: int


@app.get("/")
def root():
    return {
        "app": "Talk2DB",
        "status": "running",
        "version": "1.0.0"
    }


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    """
    Takes a natural language question.
    Returns generated SQL + query results.
    """
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    result = run_pipeline(request.question)

    # Convert DataFrame to list of dicts for JSON response
    if not result["dataframe"].empty:
        data = result["dataframe"].to_dict(orient="records")
    else:
        data = []

    # Convert any non-serializable types to string
    cleaned_data = []
    for row in data:
        cleaned_row = {}
        for k, v in row.items():
            if pd.isna(v) if not isinstance(v, (list, dict)) else False:
                cleaned_row[k] = None
            else:
                cleaned_row[k] = str(v) if not isinstance(
                    v, (int, float, str, bool, type(None))
                ) else v
        cleaned_data.append(cleaned_row)

    return QueryResponse(
        status=result["status"],
        question=result["question"],
        sql=result.get("sql"),
        message=result["message"],
        data=cleaned_data,
        columns=result.get("columns", []),
        row_count=result.get("row_count", 0)
    )


@app.get("/history")
def get_history():
    """
    Returns all past question-SQL pairs.
    """
    if not os.path.exists(HISTORY_FILE):
        return {"history": [], "count": 0}

    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)

    return {
        "history": history,
        "count": len(history)
    }


@app.delete("/history")
def clear_history():
    """
    Clears all query history.
    """
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w") as f:
            json.dump([], f)
    return {"message": "History cleared successfully."}