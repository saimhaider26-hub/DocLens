import uuid

def chunk_document(pages, source_file):
    """
    Chunks document pages by structural boundaries (paragraphs).
    Returns a list of dictionaries with the strict metadata schema needed for ChromaDB and exact citations.
    """
    chunks = []
    
    for page_data in pages:
        
        page_num = page_data.get("page_number", "unknown")
        text = page_data.get("text", "")
        
       
        raw_paragraphs = text.split('\n\n')
        
        for para in raw_paragraphs:
            clean_para = para.strip()
            
           
            if len(clean_para) > 30: 
                chunks.append({
                    "chunk_id": str(uuid.uuid4()),
                    "text": clean_para,
                    "page_number": page_num,
                    "source_doc": source_file
                })
                
    return chunks

if __name__ == "__main__":
    
    from ingest import extract_text_from_pdf
    
    pdf_path = "../data/sample.pdf"
    
    print(f"Ingesting {pdf_path}...")
    pages = extract_text_from_pdf(pdf_path)
    
    print("Chunking by structural boundaries...")
    document_chunks = chunk_document(pages, source_file="sample.pdf")
    
    print(f"\nSuccess! Created {len(document_chunks)} structural chunks.")
    
    if document_chunks:
        print("\n--- Schema Check on First Chunk ---")
        for key, value in document_chunks[0].items():
            print(f"{key}: {value}")