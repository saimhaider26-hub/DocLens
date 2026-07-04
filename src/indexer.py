import chromadb
from chunker import chunk_document
from ingest import extract_text_from_pdf

def index_documents(chunks, collection_name="doclens_mvp"):
    """
    Initializes a local ChromaDB and stores document chunks with their metadata.
    """

    client = chromadb.PersistentClient(path="../.chroma_db")
    
    
    collection = client.get_or_create_collection(name=collection_name)
    

    ids = []
    documents = []
    metadatas = []
    
    for chunk in chunks:
        ids.append(chunk["chunk_id"])
        documents.append(chunk["text"])
        metadatas.append({
            "page_number": chunk["page_number"],
            "source_doc": chunk["source_doc"]
        })
        
    if documents:
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        print(f"Successfully indexed {len(documents)} chunks into '{collection_name}'.")
    else:
        print("No chunks provided to index.")
        
    return collection

if __name__ == "__main__":
    pdf_path = "../data/sample.pdf"
    
    print("1. Extracting text...")
    pages = extract_text_from_pdf(pdf_path)
    
    print("2. Chunking document...")
    chunks = chunk_document(pages, source_file="sample.pdf")
    
    print("3. Indexing into ChromaDB...")
    index_documents(chunks)