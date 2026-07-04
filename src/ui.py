import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="DocLens", layout="wide")
st.title("📄 DocLens — Source-Cited Document Q&A")

with st.sidebar:
    st.header("Upload a Document")
    uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"])
    if uploaded_file is not None:
        if st.button("Process Document"):
            with st.spinner("Ingesting and indexing document..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                response = requests.post(f"{API_URL}/upload", files=files)
            if response.status_code == 200:
                st.success(f"'{uploaded_file.name}' indexed successfully.")
            else:
                st.error(f"Upload failed: {response.text}")

    st.divider()
    st.header("Indexed Documents")
    try:
        docs_response = requests.get(f"{API_URL}/documents")
        if docs_response.status_code == 200:
            # FIXED: Extract the actual list of files from the JSON dictionary
            docs = docs_response.json().get("documents", [])
            if docs:
                for doc in docs:
                    st.write(f"📄 {doc}")
            else:
                st.write("No documents indexed yet.")
    except requests.exceptions.ConnectionError:
        st.error("Backend not reachable. Is FastAPI running?")

st.header("Ask a Question")
question = st.text_input("Type your question about the uploaded documents:")

if st.button("Ask") and question:
    with st.spinner("Thinking..."):
        response = requests.post(f"{API_URL}/query", json={"question": question})
    if response.status_code == 200:
        answer = response.json().get("answer", "No answer returned.")
        st.markdown("### Answer")
        st.write(answer)
    else:
        st.error(f"Query failed: {response.text}")