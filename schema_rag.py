from database import get_schema
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


def create_schema_documents():
    schema = get_schema()

    documents = []

    for table, columns in schema.items():
        documents.append(
            f"Table: {table}\n"
            f"Columns: {', '.join(columns)}\n"
        )

    return documents


documents = create_schema_documents()

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

vector_db = Chroma.from_texts(
    texts=documents,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

print("Schema RAG database created successfully!")
print(f"Documents stored: {len(documents)}")