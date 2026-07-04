import json
import requests
from src.search import hybrid_search

def generate_cited_answer(question, n_results=15):
    search_results = hybrid_search(question, n_results=n_results)
    documents = search_results.get("documents", [[]])[0]
    metadatas = search_results.get("metadatas", [[]])[0]
    
    context_text = ""
    for i in range(len(documents)):
        context_text += f"Source: {metadatas[i]['source_doc']} (Page {metadatas[i]['page_number']}):\n{documents[i]}\n\n"
        
    prompt = f"""You are a professional assistant. Answer the user's question using ONLY the provided documents.
    You must include exact inline citations specifying the source file and page number.
    Documents: {context_text}
    Question: {question}"""
    
    payload = {"model": "llama3.1", "prompt": prompt, "stream": False}
    
    try:
        # Changed localhost to host.docker.internal
        response = requests.post("http://host.docker.internal:11434/api/generate", json=payload)
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.RequestException as e:
        return f"Error: Could not connect to Ollama. {str(e)}"

if __name__ == "__main__":
    answer = generate_cited_answer("What is the capital of france?")
    print(answer)