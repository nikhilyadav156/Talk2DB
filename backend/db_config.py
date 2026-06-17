from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text, inspect
from urllib.parse import quote_plus

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = quote_plus(os.getenv('DB_PASSWORD', 'nikhilroot7'))
DB_NAME = os.getenv('DB_NAME', 'talk2db')

DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine
engine = create_engine(DB_URL)

def get_engine():
    return engine

def get_schema_docs():
    """
    Automatically reads all tables and columns from the database
    and returns them as a list of text documents for RAG.
    """
    inspector = inspect(engine)
    schema_docs = []

    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        foreign_keys = inspector.get_foreign_keys(table_name)

        # Build column descriptions
        col_descriptions = []
        for col in columns:
            col_type = str(col['type'])
            nullable = "nullable" if col.get('nullable', True) else "not null"
            col_descriptions.append(f"  - {col['name']} ({col_type}, {nullable})")

        # Build foreign key descriptions
        fk_descriptions = []
        for fk in foreign_keys:
            fk_descriptions.append(
                f"  - {fk['constrained_columns']} references "
                f"{fk['referred_table']}({fk['referred_columns']})"
            )

        # Build the full table document
        doc = f"Table: {table_name}\n"
        doc += f"Columns:\n" + "\n".join(col_descriptions)
        if fk_descriptions:
            doc += f"\nForeign Keys:\n" + "\n".join(fk_descriptions)

        schema_docs.append(doc)

    return schema_docs


def get_schema_string():
    """
    Returns the full schema as a single string.
    Useful for injecting directly into LLM prompts.
    """
    docs = get_schema_docs()
    return "\n\n".join(docs)


if __name__ == "__main__":
    print("=== Schema Docs ===\n")
    for doc in get_schema_docs():
        print(doc)
        print("-" * 40)