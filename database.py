import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import URL

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "dataquery")


# Connect to MySQL server WITHOUT selecting a database
server_url = URL.create(
    drivername="mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

server_engine = create_engine(server_url)

# Create our database automatically
with server_engine.connect() as connection:
    connection.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`"))
    connection.commit()

print(f"Database '{DB_NAME}' is ready.")


# Now connect to our database
database_url = URL.create(
    drivername="mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME
)

engine = create_engine(database_url)


def get_tables():
    inspector = inspect(engine)
    return inspector.get_table_names()


def get_schema():
    inspector = inspect(engine)
    schema = {}

    for table in inspector.get_table_names():
        columns = inspector.get_columns(table)
        schema[table] = [column["name"] for column in columns]

    return schema


if __name__ == "__main__":
    print("Tables:", get_tables())
    print("Schema:", get_schema())