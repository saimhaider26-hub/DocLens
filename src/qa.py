import json
import requests
import os
from src.search import hybrid_search

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

def generate_cited_answer(question, n_results=15):
    search_results = hybrid_search(question, n_results=n_results)
    documents = search_results.get("documents", [[]])[0]
    metadatas = search_results.get("metadatas", [[]])[0]
    
    context_text = ""
    for i in range(len(documents)):
        context_text += f"Source: {metadatas[i]['source_doc']} (Page {metadatas[i]['page_number']}):\n{documents[i]}\n\n"
        
    prompt = f"""You are an advanced reading assistant. Your task is to answer the user's question using ONLY the text snippets provided below. 
    Do not use outside general knowledge or make assumptions about private companies. 
    If the information is in the documents, extract it and provide the exact inline citation specifying the source file and page number.

    Documents:
    {context_text}

    Question: {question}
    """
    
    payload = {"model": "llama3.1", "prompt": prompt, "stream": False}
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.RequestException as e:
        return f"Error: Could not connect to Ollama. {str(e)}"

if __name__ == "__main__":
    answer = generate_cited_answer("What is the capital of france?")
    print(answer)