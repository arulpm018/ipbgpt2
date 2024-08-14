import streamlit as st
import requests
import os
from dotenv import load_dotenv
from document_processing import check_server_status

load_dotenv()

URL_BASE = os.getenv("URL_BASE")

def process_pdf_chat(prompt, previous_response=""):
    if not check_server_status():
        return "Server not ready. Please try again later."
    
    url = f"{URL_BASE}/query-pdf/"
    if previous_response:
        prompt = f"Previous response: {previous_response}\n\nContinue the answer for: {prompt}"
    data = {"question": prompt}
    try:
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        return result['answer']
    except requests.RequestException:
        return "Failed to process chat. Server might be busy or unavailable."

def process_selected_documents_chat(prompt, previous_response=""):
    if not st.session_state['selected_document']:
        return "Error: No documents selected."
    
    if not check_server_status():
        return "Server not ready. Please try again later."
    
    context = "\n\n".join(f"{doc['judul']} {doc['abstrak']} {doc['url']}" for doc in st.session_state['selected_document'])
    
    if previous_response:
        prompt = f"Previous response: {previous_response}\n\nContinue the answer for: {prompt}"
    
    url = f"{URL_BASE}/chat/"
    data = {"query": prompt, "context": context}
    try:
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        return result['response']
    except requests.RequestException:
        return "Failed to process chat. Server might be busy or unavailable."

def process_continue_generate(query, previous_response, context):
    if not check_server_status():
        return "Server not ready. Please try again later."
    
    url = f"{URL_BASE}/continue-generate/"
    data = {
        "query": query,
        "previous_response": previous_response,
        "context": context
    }
    try:
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        return result['response']
    except requests.RequestException:
        return "Failed to continue generation. Server might be busy or unavailable."