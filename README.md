# Talk2DB

**Ask questions in plain English. Get answers from your database instantly.**

Talk2DB is an AI-powered web application that converts natural language questions into SQL queries and executes them on your database in real time. No SQL knowledge required.

---

## What is Talk2DB

Most people who work with data cannot write SQL. They depend on developers to pull reports and answer simple questions from databases. This creates a bottleneck that slows down decisions.

Talk2DB solves this by letting anyone type a question like **"show me the top 5 highest paid employees in the IT department"** and instantly getting back the SQL query and the results — without writing a single line of code.

---

## How It Works

When you type a question Talk2DB follows this pipeline:

**1. RAG Retrieval**
Before generating SQL the system retrieves the most relevant schema information from your database using a FAISS vector store. This tells the AI exactly which tables and columns exist so it generates accurate SQL instead of hallucinating.

**2. SQL Generation**
The retrieved schema context is injected into a prompt sent to Groq's Llama model. The model generates a precise SQL query tailored to your exact database structure.

**3. Safety Check**
Every generated query passes through a safety validator that blocks destructive statements like DROP TABLE or DELETE before they can run.

**4. Execution**
The validated SQL runs on your MySQL database via SQLAlchemy and the results are returned as a formatted table in the dashboard.

**5. History Learning**
Every successful query is saved to a history store. Future similar questions retrieve these past examples as few-shot prompts which improves accuracy over time.

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq · qwen/qwen3.8-27b |
| RAG Engine | FAISS · Pure Python TF-IDF |
| Backend | FastAPI · SQLAlchemy |
| Database | MySQL |
| Frontend | Streamlit |
| Deployment | Docker |

---

## Features

**Schema-aware RAG pipeline**
The system automatically reads your entire database schema on startup and indexes it into a FAISS vector store. When you ask a question it retrieves only the relevant tables and columns so the AI has exactly the context it needs.

**Query history retrieval**
Past successful question-SQL pairs are stored and retrieved as examples. The system gets smarter the more you use it.

**SQL safety layer**
Blocks all destructive operations including DROP TABLE, DELETE, UPDATE, INSERT, ALTER and TRUNCATE before execution.

**Three-tab dashboard**
The Query tab lets you type questions and see generated SQL with syntax highlighting. The Analytics tab shows usage metrics and connection info. The History tab shows all past queries.

**Production-ready architecture**
FastAPI backend and Streamlit frontend run as separate services and communicate via REST API. Docker compose packages both for easy deployment.

---

## Project Structure

```
Talk2DB/
├── backend/
│   ├── main.py            FastAPI app with /query and /history endpoints
│   ├── rag_pipeline.py    FAISS vector store and TF-IDF retrieval engine
│   ├── nl2sql.py          Groq LLM prompt builder and SQL generator
│   ├── executor.py        SQL runner and full pipeline orchestrator
│   └── db_config.py       Database connection and schema introspector
├── frontend/
│   └── app.py             Streamlit dashboard UI
├── vector_store/          FAISS index and query history files
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
└── requirements.txt
```

---

## Getting Started

**Prerequisites**

You will need Python 3.11 or above and MySQL installed locally. You will also need a free Groq API key from console.groq.com.

**Clone the repository**

```bash
git clone https://github.com/nikhilyadav156/Talk2DB.git
cd Talk2DB
```

**Create a virtual environment**

```bash
python -m venv venv
venv\Scripts\activate
```

**Install dependencies**

```bash
pip install -r requirements.txt
```

**Set up environment variables**

Create a `.env` file in the root directory with the following values:

```
GROQ_API_KEY=your_groq_api_key_here
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=talk2db
```

**Set up the database**

Open MySQL and run the setup queries to create the `talk2db` database with the `employees`, `departments` and `sales` tables and insert sample data.

**Run the application**

Open two terminal windows. In the first one start the backend:

```bash
uvicorn backend.main:app --reload --port 8000
```

In the second one start the frontend:

```bash
streamlit run frontend/app.py
```

Open your browser at `http://localhost:8501` to access the dashboard.

---

## API Endpoints

**POST /query**
Accepts a natural language question and returns the generated SQL query along with the results.

**GET /history**
Returns all past question and SQL pairs stored in query history.

**DELETE /history**
Clears the entire query history and rebuilds the vector store.

---

## Running with Docker

```bash
docker-compose up --build
```

This starts both the backend on port 8000 and the frontend on port 8501.

---

## Example Queries

Here are some questions you can try in the dashboard:

```
Show me all employees in the IT department
What is the total salary expense by department
Show me the top 3 highest paid employees
How many employees are currently active
Show all sales from the North region
Which department has the highest average salary
```

---

## About

Built by **Nikhil Yadav** as part of a portfolio project.

This project demonstrates end-to-end skills in LLM integration, RAG architecture, REST API development, database engineering and frontend design.

