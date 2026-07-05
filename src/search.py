import os
import chromadb
from rank_bm25 import BM25Okapi

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.exists("/app/chroma_db"):
    CHROMA_PATH = "/app/chroma_db"
else:
    CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")

def hybrid_search(question, n_results=3, collection_name="doclens_mvp"):
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(name=collection_name)
    
    all_data = collection.get(include=['documents', 'metadatas'])
    ids = all_data['ids']
    docs = all_data['documents']
    metadatas = all_data['metadatas']
    
    if not docs:
        return {"documents": [[]], "metadatas": [[]]}
    
    tokenized_corpus = [doc.lower().split() for doc in docs]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = question.lower().split()
    bm25_scores = bm25.get_scores(tokenized_query)
    
    vector_results = collection.query(
        query_texts=[question],
        n_results=len(docs)
    )
    vector_ids = vector_results['ids'][0]
    
    combined_scores = {}
    
    for i, doc_id in enumerate(ids):
        bm25_rank = sorted(bm25_scores, reverse=True).index(bm25_scores[i]) + 1
        combined_scores[doc_id] = 1 / (60 + bm25_rank)
        
    for i, doc_id in enumerate(vector_ids):
        vector_rank = i + 1
        if doc_id in combined_scores:
            combined_scores[doc_id] += 1 / (60 + vector_rank)
        else:
            combined_scores[doc_id] = 1 / (60 + vector_rank)
            
    sorted_ids = sorted(combined_scores.keys(), key=lambda x: combined_scores[x], reverse=True)[:n_results]
    
    final_docs = []
    final_metadatas = []
    
    for doc_id in sorted_ids:
        idx = ids.index(doc_id)
        final_docs.append(docs[idx])
        final_metadatas.append(metadatas[idx])
        
    return {"documents": [final_docs], "metadatas": [final_metadatas]}

if __name__ == "__main__":
    query = "What is the primary objective of Auto Mininet?"
    search_results = hybrid_search(query)
    
    documents = search_results.get("documents", [[]])[0]
    metadatas = search_results.get("metadatas", [[]])[0]
    
    print(f"Query: {query}\n")
    for i in range(len(documents)):
        print(f"Result {i+1}:")
        print(f"Text: {documents[i]}")
        print(f"Page: {metadatas[i]['page_number']}")
        print(f"Source: {metadatas[i]['source_doc']}")
        print("-" * 40)