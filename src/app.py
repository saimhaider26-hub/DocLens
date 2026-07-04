import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.ingest import extract_text_from_pdf
from src.chunker import chunk_document
from src.indexer import index_documents
from src.qa import generate_cited_answer

app = FastAPI(title="DocLens API", version="1.0")

UPLOAD_DIR = "data"


os.makedirs(UPLOAD_DIR, exist_ok=True)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        pages = extract_text_from_pdf(file_path)
        chunks = chunk_document(pages, source_file=file.filename)
        index_documents(chunks)
        return {"status": "success", "filename": file.filename, "chunks_indexed": len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_pipeline(request: QueryRequest):
    try:
        answer = generate_cited_answer(request.question)
        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def list_documents():
    if not os.path.exists(UPLOAD_DIR):
        return {"documents": []}
    files = [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]
    return {"documents": files}

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run("src.app:app", host="127.0.0.1", port=8000, reload=True)