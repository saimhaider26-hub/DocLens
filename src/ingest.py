import fitz
import os
from typing import List, Dict

def extract_text_from_pdf(pdf_path: str) -> List[Dict[str, any]]:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Could not find document at {pdf_path}")

    print(f" Processing: {os.path.basename(pdf_path)}...")
    
    document_chunks = []
    doc = fitz.open(pdf_path)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text").strip()
        
        if text:
            document_chunks.append({
                "page_number": page_num + 1,
                "text": text,
                "source_file": os.path.basename(pdf_path)
            })

    print(f"Extracted {len(document_chunks)} pages with readable text.")
    return document_chunks

if __name__ == "__main__":
    test_file = "../data/sample.pdf" 
    
    try:
        extracted_data = extract_text_from_pdf(test_file)
        print(f"\nPreview of Page 1:\n{extracted_data[0]['text'][:200]}...")
    except FileNotFoundError as e:
        print(e)
        print("💡 Action: Please put a PDF named 'sample.pdf' in the 'data' folder to test.")