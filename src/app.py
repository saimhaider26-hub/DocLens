import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from src.ingest import extract_text_from_pdf
from src.chunker import chunk_document
from src.indexer import index_documents, delete_document_from_index
from src.router import run_router

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="DocLens API", version="1.0")

API_KEY = os.getenv("DOCLENS_API_KEY", "super-secret-key-123")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str

@app.post("/upload", dependencies=[Depends(verify_api_key)])
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

@app.post("/query", response_model=QueryResponse, dependencies=[Depends(verify_api_key)])
async def query_pipeline(request: QueryRequest):
    try:
        router_output = run_router(request.question)
        answer = router_output.get("answer", "No answer could be generated.")
        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents", dependencies=[Depends(verify_api_key)])
async def list_documents():
    if not os.path.exists(UPLOAD_DIR):
        return {"documents": []}
    files = [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]
    return {"documents": files}

@app.delete("/documents/{filename}", dependencies=[Depends(verify_api_key)])
async def delete_document(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    try:
        delete_document_from_index(filename)
    except Exception as e:
        print(f"Error deleting from index: {e}")
        
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"status": "success", "message": f"{filename} deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.app:app", host="127.0.0.1", port=8000, reload=True)