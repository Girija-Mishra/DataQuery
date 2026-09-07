
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


def create_schema_rag(schema):
    documents = []

    for table, columns in schema.items():
        documents.append(
            f"Table: {table}\n"
            f"Columns: {', '.join(columns)}"
        )

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    vector_db = Chroma.from_texts(
        texts=documents,
        embedding=embeddings
    )

    return vector_db


def retrieve_schema(vector_db, question):
    results = vector_db.similarity_search(
        question,
        k=3
    )

    schema_text = "\n\n".join(
        document.page_content
        for document in results
    )

    return schema_text