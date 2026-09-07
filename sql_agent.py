import os
import re

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from sqlalchemy import create_engine, inspect, text

from schema_rag import create_schema_rag, retrieve_schema

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0
)


def get_active_engine():
    if os.path.exists("uploaded_data.db"):
        return create_engine("sqlite:///uploaded_data.db")
    return None


def get_active_schema():
    engine = get_active_engine()

    if engine is None:
        return {}

    inspector = inspect(engine)

    schema = {}

    for table in inspector.get_table_names():
        columns = inspector.get_columns(table)

        schema[table] = [
            column["name"]
            for column in columns
        ]

    return schema


def retrieve_relevant_schema(question):
    schema = get_active_schema()

    if not schema:
        return "No dataset has been uploaded."

    vector_db = create_schema_rag(schema)

    return retrieve_schema(
        vector_db,
        question
    )


def generate_sql(question):
    engine = get_active_engine()

    if engine is None:
        raise ValueError(
            "Please upload a CSV or Excel file first."
        )

    relevant_schema = retrieve_relevant_schema(
        question
    )

    prompt = f"""
You are an expert SQLite SQL assistant.

Relevant database schema:

{relevant_schema}

User question:

{question}

Generate ONLY the SQL query required to answer the question.

Rules:
- Use only tables and columns from the provided schema.
- Never invent columns.
- The uploaded data table is called uploaded_data.
- Never modify the database.
- Never use INSERT.
- Never use UPDATE.
- Never use DELETE.
- Never use DROP.
- Never use ALTER.
- Never use TRUNCATE.
- Never use CREATE.
- Never use REPLACE.
- Return only SQL.
- Do not use markdown.
"""

    response = llm.invoke(prompt)

    content = response.content

    if isinstance(content, list):
        sql = ""

        for item in content:
            if isinstance(item, dict) and "text" in item:
                sql += item["text"]
            elif isinstance(item, str):
                sql += item
    else:
        sql = str(content)

    sql = sql.strip()

    sql = re.sub(
        r"```sql|```",
        "",
        sql,
        flags=re.IGNORECASE
    ).strip()

    return sql


def validate_sql(sql):
    forbidden = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "truncate",
        "create",
        "replace"
    ]

    sql_lower = sql.lower().strip()

    for word in forbidden:
        if re.search(
            rf"\b{word}\b",
            sql_lower
        ):
            return False

    return (
        sql_lower.startswith("select")
        or sql_lower.startswith("with")
    )


def execute_query(sql):
    if not validate_sql(sql):
        raise ValueError(
            "Unsafe SQL query blocked."
        )

    engine = get_active_engine()

    if engine is None:
        raise ValueError(
            "Please upload a CSV or Excel file first."
        )

    with engine.connect() as connection:
        result = connection.execute(
            text(sql)
        )

        columns = list(result.keys())

        rows = [
            list(row)
            for row in result.fetchall()
        ]

    return columns, rows