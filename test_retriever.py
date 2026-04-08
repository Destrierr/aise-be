# test_retriever.py
from vector import retriever

query = "bagaimana cara registrasi internet banking bank sumsel babel?"  # ganti dengan pertanyaan yang kamu test
results = retriever.invoke(query)

print(f"Jumlah dokumen ditemukan: {len(results)}")
for i, doc in enumerate(results):
    print(f"\n--- Review {i+1} ---")
    print(f"Content: {doc.page_content}")
    print(f"Metadata: {doc.metadata}")