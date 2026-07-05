import fitz
import os
from typing import List, Dict
import pytesseract
from pdf2image import convert_from_path

def extract_text_from_pdf(pdf_path: str) -> List[Dict[str, any]]:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Could not find document at {pdf_path}")

    print(f" Processing: {os.path.basename(pdf_path)}...")
    
    document_chunks = []
    doc = fitz.open(pdf_path)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text").strip()
        
        if len(text) < 50:
            print(f"   Page {page_num + 1} appears to be an image/scan. Running OCR...")
            try:
                images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1)
                if images:
                    ocr_text = pytesseract.image_to_string(images[0]).strip()
                    text = ocr_text
            except Exception as e:
                print(f"   OCR failed on page {page_num + 1}: {str(e)}")

        if text:
            document_chunks.append({
                "page_number": page_num + 1,
                "text": text,
                "source_file": os.path.basename(pdf_path)
            })

    print(f"Extracted {len(document_chunks)} pages with readable text.")
    return document_chunks

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_file = os.path.join(BASE_DIR, "data", "sample.pdf")
    
    try:
        extracted_data = extract_text_from_pdf(test_file)
        if extracted_data:
            print(f"\nPreview of Page 1:\n{extracted_data[0]['text'][:200]}...")
    except FileNotFoundError as e:
        print(e)
        print("💡 Action: Please put a PDF named 'sample.pdf' in the 'data' folder to test.")