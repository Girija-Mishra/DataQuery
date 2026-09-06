import pandas as pd
from sqlalchemy import create_engine


def create_upload_database(df):
    """
    Create a temporary SQLite database
    from the uploaded DataFrame.
    """

    engine = create_engine(
        "sqlite:///uploaded_data.db"
    )

    df.to_sql(
        "uploaded_data",
        engine,
        if_exists="replace",
        index=False
    )

    return engine


def get_upload_schema(engine):
    """
    Get table and column information.
    """

    from sqlalchemy import inspect

    inspector = inspect(engine)

    columns = inspector.get_columns(
        "uploaded_data"
    )

    return {
        "uploaded_data": [
            column["name"]
            for column in columns
        ]
    }