import os
import re

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from sqlalchemy import create_engine, inspect, text

from database import engine as mysql_engine

load_dotenv()


# --------------------------------------------------
# GEMINI
# --------------------------------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0
)


# --------------------------------------------------
# GET ACTIVE DATABASE
# --------------------------------------------------

def get_active_engine():

    # If uploaded dataset exists, use SQLite
    if os.path.exists("uploaded_data.db"):

        return create_engine(
            "sqlite:///uploaded_data.db"
        )

    # Otherwise use MySQL
    return mysql_engine


# --------------------------------------------------
# GET SCHEMA
# --------------------------------------------------

def get_active_schema():

    engine = get_active_engine()

    inspector = inspect(engine)

    schema = {}

    for table in inspector.get_table_names():

        columns = inspector.get_columns(table)

        schema[table] = [
            column["name"]
            for column in columns
        ]

    return schema


# --------------------------------------------------
# RETRIEVE RELEVANT SCHEMA
# --------------------------------------------------

def retrieve_schema(question):

    schema = get_active_schema()

    schema_text = ""

    for table, columns in schema.items():

        schema_text += (
            f"Table: {table}\n"
            f"Columns: {', '.join(columns)}\n\n"
        )

    return schema_text


# --------------------------------------------------
# GENERATE SQL
# --------------------------------------------------

def generate_sql(question):

    relevant_schema = retrieve_schema(question)

    engine = get_active_engine()

    dialect = engine.dialect.name

    prompt = f"""
You are an expert {dialect} SQL assistant.

Database schema:

{relevant_schema}

User question:

{question}

Generate ONLY the SQL query needed to answer the question.

Rules:
- Use only tables and columns from the schema.
- Never invent columns.
- Never modify the database.
- Never use INSERT, UPDATE, DELETE, DROP, ALTER,
  TRUNCATE, CREATE, REPLACE.
- Return only SQL.
- Do not use markdown.
"""

    response = llm.invoke(prompt)

    content = response.content

    # Gemini sometimes returns structured content
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

    # Remove markdown if Gemini adds it
    sql = re.sub(
        r"```sql|```",
        "",
        sql,
        flags=re.IGNORECASE
    ).strip()

    return sql


# --------------------------------------------------
# SQL SAFETY
# --------------------------------------------------

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

    sql_lower = sql.lower()

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


# --------------------------------------------------
# EXECUTE SQL
# --------------------------------------------------

def execute_query(sql):

    if not validate_sql(sql):

        raise ValueError(
            "Unsafe SQL query blocked."
        )

    engine = get_active_engine()

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


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    question = (
        "Find the highest sputtering yield value"
    )

    print("\nDatabase schema:")

    print(
        retrieve_schema(question)
    )

    sql = generate_sql(question)

    print("\nGenerated SQL:")

    print(sql)

    columns, rows = execute_query(sql)

    print("\nResult:")

    print(columns)

    print(rows)