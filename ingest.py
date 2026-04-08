import os
import re
from sqlalchemy import create_engine, text

# Langchain
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import PGVector

# Multi Loader
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    CSVLoader,
    Docx2txtLoader,
    UnstructuredExcelLoader
)

# ========================================
# KONFIGURASI
# ========================================
CONNECTION_STRING = "postgresql+psycopg2://dezze:password123@localhost:5433/db_helpdesk"

COLLECTION_NAME = "sop_kantor"

embeddings = OllamaEmbeddings(model="nomic-embed-text")

# ========================================
# LOAD MULTI FILE
# ========================================
def load_documents(data_dir):
    documents = []

    for filename in os.listdir(data_dir):
        file_path = os.path.join(data_dir, filename)

        try:
            if filename.endswith(".txt"):
                loader = TextLoader(file_path, encoding="utf-8")

            elif filename.endswith(".pdf"):
                loader = PyPDFLoader(file_path)

            elif filename.endswith(".csv"):
                loader = CSVLoader(file_path)

            elif filename.endswith(".docx"):
                loader = Docx2txtLoader(file_path)

            elif filename.endswith(".xlsx"):
                loader = UnstructuredExcelLoader(file_path)

            else:
                continue

            docs = loader.load()

            for doc in docs:
                doc.metadata["source"] = filename

            documents.extend(docs)

            print(f"[OK] Loaded: {filename}")

        except Exception as e:
            print(f"[ERROR] {filename}: {e}")

    return documents


# ========================================
# LOAD DATABASE FAQ (OPTIONAL)
# ========================================
def load_from_database():
    docs = []

    try:
        engine = create_engine(CONNECTION_STRING)

        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT pertanyaan, jawaban FROM faq")
            )

            for row in result:
                content = f"Pertanyaan: {row[0]}\nJawaban: {row[1]}"
                docs.append(
                    Document(
                        page_content=content,
                        metadata={"source": "database"}
                    )
                )

        print("[OK] Loaded data dari database")

    except Exception as e:
        print(f"[INFO] Database skip: {e}")

    return docs


# ========================================
# CHUNKING
# ========================================
def split_documents(documents):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    docs = text_splitter.split_documents(documents)

    return docs


# ========================================
# DELETE OLD DATA
# ========================================
def delete_old_data():

    try:
        engine = create_engine(CONNECTION_STRING)

        with engine.connect() as conn:
            conn.execute(text(f"""
                DELETE FROM langchain_pg_embedding 
                WHERE collection_id = (
                    SELECT uuid FROM langchain_pg_collection 
                    WHERE name = '{COLLECTION_NAME}'
                )
            """))
            conn.commit()

        print("[OK] Data lama dihapus")

    except Exception as e:
        print(f"[INFO] {e}")


# ========================================
# MAIN INGEST
# ========================================
def main():

    print("=" * 60)
    print("INGEST AI HELPDESK")
    print("=" * 60)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data")

    # 1. Load File
    print("\n[1/5] Load Documents...")
    folder_docs = load_documents(data_dir)

    # 2. Load Database
    print("\n[2/5] Load Database...")
    db_docs = load_from_database()

    documents = folder_docs + db_docs

    print(f"[OK] Total Document: {len(documents)}")

    # 3. Chunking
    print("\n[3/5] Chunking...")
    docs = split_documents(documents)

    print(f"[OK] Total Chunk: {len(docs)}")

    # 4. Delete old data
    print("\n[4/5] Delete old data...")
    delete_old_data()

    # 5. Embedding
    print("\n[5/5] Embedding & Save...")
    vector_store = PGVector.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        connection_string=CONNECTION_STRING
    )

    print("\n" + "=" * 60)
    print("[OK] INGEST SELESAI")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Total docs: {len(docs)}")
    print("=" * 60)


if __name__ == "__main__":
    main()