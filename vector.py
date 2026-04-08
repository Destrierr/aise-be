from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import PGVector

# ========================================
# CONFIG
# ========================================
CONNECTION_STRING = "postgresql+psycopg2://dezze:password123@localhost:5433/db_helpdesk"

COLLECTION_NAME = "sop_kantor"

# ========================================
# EMBEDDING
# ========================================
def get_embeddings():
    return OllamaEmbeddings(
        model="nomic-embed-text"
    )

# ========================================
# VECTOR DB
# ========================================
def get_vector_db():

    embeddings = get_embeddings()

    vector_db = PGVector(
        connection_string=CONNECTION_STRING,
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings
    )

    return vector_db


# ========================================
# RETRIEVER
# ========================================
def get_retriever():

    vector_db = get_vector_db()

    retriever = vector_db.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 5
        }
    )

    return retriever