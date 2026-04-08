from vector import get_retriever, get_vector_db

retriever = get_retriever()
vector_db = get_vector_db()

# ========================================
# KEYWORD SEARCH
# ========================================
def keyword_search(question, documents, top_k=3):
    question_words = question.lower().split()
    scored_docs = []

    for doc in documents:
        content = doc.page_content.lower()
        score = sum(1 for word in question_words if word in content)
        if score > 0:
            scored_docs.append((score, doc))

    scored_docs.sort(reverse=True, key=lambda x: x[0])
    return [doc for _, doc in scored_docs[:top_k]]


# ========================================
# HYBRID SEARCH
# ========================================
def hybrid_search(question):

    # 1. Semantic Search
    semantic_docs = retriever.invoke(question)
    print(f"[DEBUG] Semantic docs: {len(semantic_docs)}")

    # 2. Ambil semua dokumen dengan query yang bermakna ✅
    all_docs = vector_db.similarity_search(question, k=20)
    print(f"[DEBUG] All docs: {len(all_docs)}")

    # 3. Keyword Search
    keyword_docs = keyword_search(question, all_docs)
    print(f"[DEBUG] Keyword docs: {len(keyword_docs)}")

    # 4. Combine & deduplicate
    combined = semantic_docs + keyword_docs
    seen = set()
    results = []

    for doc in combined:
        if doc.page_content not in seen:
            results.append(doc)
            seen.add(doc.page_content)

    print(f"[DEBUG] Final results: {len(results)}")
    return results