import uuid

def chunk_document(pages, source_file, chunk_size=800, overlap=100):
    chunks = []
    
    for page_data in pages:
        page_num = page_data.get("page_number", "unknown")
        text = page_data.get("text", "")
        
        clean_text = " ".join(text.split())
        
        if len(clean_text) < 20:
            continue
            
        start = 0
        text_length = len(clean_text)
        
        while start < text_length:
            end = start + chunk_size
            chunk_text = clean_text[start:end]
            
            chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "text": chunk_text,
                "page_number": page_num,
                "source_doc": source_file
            })
            
            start += (chunk_size - overlap)
            
    return chunks

if __name__ == "__main__":
    from ingest import extract_text_from_pdf
    
    pdf_path = "../data/sample.pdf"
    
    print(f"Ingesting {pdf_path}...")
    pages = extract_text_from_pdf(pdf_path)
    
    print("Chunking by sliding window...")
    document_chunks = chunk_document(pages, source_file="sample.pdf")
    
    print(f"\nSuccess! Created {len(document_chunks)} structural chunks.")
    
    if document_chunks:
        print("\n--- Schema Check on First Chunk ---")
        for key, value in document_chunks[0].items():
            print(f"{key}: {value}")