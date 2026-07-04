import json
import requests
from search import hybrid_search

def generate_cited_answer(question, n_results=5):
    search_results = hybrid_search(question, n_results=n_results)
    documents = search_results.get("documents", [[]])[0]
    metadatas = search_results.get("metadatas", [[]])[0]
    
    context_text = ""
    for i in range(len(documents)):
        context_text += f"Page {metadatas[i]['page_number']}:\n{documents[i]}\n\n"
        
    prompt = f"""You are a professional assistant. Answer the user's question using ONLY the provided documents.
    You must include exact inline citations using the provided page numbers (e.g., "This is the answer (Page X).").
    If the answer is not contained in the documents, state clearly that you cannot find it. Do not hallucinate.
    
    Documents:
    {context_text}
    
    Question: {question}
    """
    
    payload = {
        "model": "llama3.1",
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.RequestException:
        return "Error: Could not connect to Ollama. Ensure it is running locally."

if __name__ == "__main__":
    query = "What is the primary objective of Auto Mininet?"
    print("Searching database and generating answer...\n")
    answer = generate_cited_answer(query)
    print("Final Answer:\n", answer)