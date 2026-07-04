import chromadb

def query_vector_db(question, n_results=3, collection_name="doclens_mvp"):
    client = chromadb.PersistentClient(path="../.chroma_db")
    collection = client.get_collection(name=collection_name)
    
    results = collection.query(
        query_texts=[question],
        n_results=n_results
    )
    
    return results

if __name__ == "__main__":
    query = "What is the primary objective of Auto Mininet?"
    search_results = query_vector_db(query)
    
    documents = search_results.get("documents", [[]])[0]
    metadatas = search_results.get("metadatas", [[]])[0]
    
    print(f"Query: {query}\n")
    for i in range(len(documents)):
        print(f"Result {i+1}:")
        print(f"Text: {documents[i]}")
        print(f"Page: {metadatas[i]['page_number']}")
        print(f"Source: {metadatas[i]['source_doc']}")
        print("-" * 40)