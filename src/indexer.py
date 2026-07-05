import os
import chromadb
from src.chunker import chunk_document
from src.ingest import extract_text_from_pdf

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.exists("/app/chroma_db"):
    CHROMA_PATH = "/app/chroma_db"
else:
    CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")

def index_documents(chunks, collection_name="doclens_mvp"):
    client = chromadb.PersistentClient(path=CHROMA_PATH)
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

def delete_document_from_index(filename: str, collection_name="doclens_mvp"):
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(name=collection_name)
    collection.delete(where={"source_doc": filename})
    print(f"Deleted all vector chunks for {filename}.")

if __name__ == "__main__":
    data_dir = os.path.join(BASE_DIR, "data")
    
    if not os.path.exists(data_dir):
        print(f"Data directory not found at {data_dir}")
        exit(1)
        
    all_chunks = []
    
    for file_name in os.listdir(data_dir):
        if file_name.lower().endswith(".pdf"):
            pdf_path = os.path.join(data_dir, file_name)
            print(f"\n--- Processing: {file_name} ---")
            
            try:
                pages = extract_text_from_pdf(pdf_path)
                chunks = chunk_document(pages, source_file=file_name)
                all_chunks.extend(chunks)
            except Exception as e:
                print(f"Error processing {file_name}: {str(e)}")
                
    if all_chunks:
        print("\n3. Indexing all gathered chunks into ChromaDB...")
        index_documents(all_chunks)
    else:
        print("No PDF files found to index.")