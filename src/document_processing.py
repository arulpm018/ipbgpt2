import requests
import os
from dotenv import load_dotenv

load_dotenv()

URL_BASE = os.getenv("URL_BASE")


def upload_pdf(file):
    
    url = f"{URL_BASE}/upload-pdf/"
    files = {'file': file}
    try:
        response = requests.post(url, files=files)
        return response.json()
    except requests.RequestException:
        return {"error": "Failed to upload PDF. Server might be busy or unavailable."}

def get_related_documents(title):
 
    
    url = f"{URL_BASE}/related_documents/"
    data = {"title": title}
    try:
        response = requests.post(url, json=data)
        return response.json()
    except requests.RequestException:
        return {"error": "Failed to get related documents. Server might be busy or unavailable."}