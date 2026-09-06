from dotenv import load_dotenv
load_dotenv()

import os
import json
import pickle
import math
import numpy as np
import faiss
from groq import Groq
from backend.db_config import get_schema_docs

VECTOR_STORE_PATH = "vector_store/faiss_index.bin"
DOCS_PATH = "vector_store/docs.pkl"
VOCAB_PATH = "vector_store/vocab.pkl"
HISTORY_FILE = "vector_store/query_history.json"

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ── Pure Python TF-IDF (no sklearn/scipy) ──────────────────────────────────

def tokenize(text: str) -> list:
    return text.lower().split()


def build_vocab(documents: list) -> dict:
    vocab = {}
    idx = 0
    for doc in documents:
        for word in tokenize(doc["content"]):
            if word not in vocab:
                vocab[word] = idx
                idx += 1
    return vocab


def tfidf_vector(text: str, vocab: dict, documents: list) -> np.ndarray:
    tokens = tokenize(text)
    n_docs = len(documents)
    vec = np.zeros(len(vocab), dtype=np.float32)

    # TF
    tf = {}
    for t in tokens:
        tf[t] = tf.get(t, 0) + 1
    for t in tf:
        tf[t] /= len(tokens)

    # IDF
    for t in set(tokens):
        if t in vocab:
            doc_count = sum(
                1 for doc in documents
                if t in tokenize(doc["content"])
            )
            idf = math.log((n_docs + 1) / (doc_count + 1)) + 1
            vec[vocab[t]] = tf[t] * idf

    # Normalize
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm

    return vec


# ── Core pipeline ───────────────────────────────────────────────────────────

def get_all_documents() -> list:
    schema_docs = get_schema_docs()
    documents = []

    for doc in schema_docs:
        documents.append({"content": doc, "type": "schema"})

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
        for item in history:
            documents.append({
                "content": f"Question: {item['question']}\nSQL: {item['sql']}",
                "type": "history"
            })

    return documents


def build_vector_store():
    print("Building vector store...")

    documents = get_all_documents()
    vocab = build_vocab(documents)

    vectors = np.array([
        tfidf_vector(doc["content"], vocab, documents)
        for doc in documents
    ], dtype=np.float32)

    dimension = vectors.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(vectors)

    os.makedirs("vector_store", exist_ok=True)
    faiss.write_index(index, VECTOR_STORE_PATH)

    with open(DOCS_PATH, "wb") as f:
        pickle.dump(documents, f)

    with open(VOCAB_PATH, "wb") as f:
        pickle.dump(vocab, f)

    print(f"Vector store saved. {len(documents)} docs indexed.")
    return index, documents, vocab


def load_vector_store():
    if not os.path.exists(VECTOR_STORE_PATH):
        print("Vector store not found, building...")
        return build_vector_store()

    index = faiss.read_index(VECTOR_STORE_PATH)

    with open(DOCS_PATH, "rb") as f:
        documents = pickle.load(f)

    with open(VOCAB_PATH, "rb") as f:
        vocab = pickle.load(f)

    print("Vector store loaded.")
    return index, documents, vocab


def retrieve_context(question: str, k: int = 4) -> str:
    index, documents, vocab = load_vector_store()

    query_vec = tfidf_vector(
        question, vocab, documents
    ).reshape(1, -1)

    distances, indices = index.search(query_vec, k)

    context_parts = []
    for idx in indices[0]:
        if idx < len(documents):
            context_parts.append(documents[idx]["content"])

    return "\n\n".join(context_parts)


def save_to_history(question: str, sql: str):
    history = []

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)

    history.append({"question": question, "sql": sql})

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

    build_vector_store()
    print(f"Saved to history: {question}")


if __name__ == "__main__":
    print("=== Building Vector Store ===")
    build_vector_store()

    print("\n=== Testing Retrieval ===")
    question = "show me all employees in IT department"
    context = retrieve_context(question)
    print(f"Question: {question}")
    print(f"\nRetrieved Context:\n{context}")

    print("\n=== Saving Sample History ===")
    save_to_history(
        "show me all employees in IT department",
        "SELECT * FROM employees WHERE department = 'IT';"
    )
    print("Done.")