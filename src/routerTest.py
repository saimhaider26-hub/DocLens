import requests
import json

def route_query(question: str) -> str:
    prompt = f"""You are an advanced query classification router. Classify the user's question into EXACTLY ONE of these four categories:

1. "document": Questions asking for factual information contained in uploaded documents (e.g., "Saim Haider projects", "Lecture 2 laws", "What is Auto Mininet").
2. "data": Questions asking for numerical aggregations, statistics, counts, or database metrics (e.g., "How many users", "average latency").
3. "ambiguous": Questions that lack specific context, use vague pronouns, or refer to entities present in multiple documents (e.g., "Who is the group leader for this project?" -> This is ambiguous because multiple documents describe different projects with different leaders; "this project" is unclear).
4. "out_of_scope": General knowledge questions completely unrelated to the documents or database (e.g., "What is the capital of Pakistan?", "Who is the President?").

Respond with ONLY one lowercase word: document, data, ambiguous, or out_of_scope. Do not include punctuation or explanation.

Question: {question}
Category:"""
    
    # Temperature 0 ensures the output is deterministic and not creative
    payload = {
        "model": "llama3.1",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0} 
    }
    
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        response.raise_for_status()
        return response.json()["response"].strip().lower()
    except Exception as e:
        return f"error: {e}"

if __name__ == "__main__":
    # Updated Test Set
    test_questions = [
        # Document Route Expected
        "Which specific IT-related laws are included in the Lecture 2 curriculum?",
        "What is the primary objective of Auto Mininet?",
        "What university did Saim graduate from?",
        "What are the projects for Saim Haider?",
        
        # Data Route Expected
        "How many total users are registered in the database?",
        "Show me a count of all the network topologies generated this month.",
        "What is the average latency of the API responses?",
        
        # Ambiguous Route Expected
        "Who is the group leader for this project?",
        "Does he have any experience with Python?",
        "Where is the supervisor's name listed?",
        
        # Out of Scope Expected
        "What is the capital of pakistan?",
        "Who is the president of the United States?"
    ]

    print("Running Router Classification Test (Temperature 0)...\n" + "-"*40)
    for q in test_questions:
        route = route_query(q)
        print(f"[{route.upper()}] - {q}")