import requests
import os
from dotenv import load_dotenv

load_dotenv()

URL_BASE = os.getenv("URL_BASE")

def check_server_status():
    try:
        response = requests.get(f"{URL_BASE}/status", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def upload_pdf(file):
    if not check_server_status():
        return {"error": "Server not ready. Please try again later."}
    
    url = f"{URL_BASE}/upload-pdf/"
    files = {'file': file}
    try:
        response = requests.post(url, files=files, timeout=10)
        return response.json()
    except requests.RequestException:
        return {"error": "Failed to upload PDF. Server might be busy or unavailable."}

def get_related_documents(title):
    if not check_server_status():
        return {"error": "Server not ready. Please try again later."}
    
    url = f"{URL_BASE}/related_documents/"
    data = {"title": title}
    try:
        response = requests.post(url, json=data, timeout=10)
        return response.json()
    except requests.RequestException:
        return {"error": "Failed to get related documents. Server might be busy or unavailable."}