import vertexai
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
PROJECT_ID = os.getenv('PROJECT_ID')
GCS_BUCKET_NAME = os.getenv('GCS_BUCKET_NAME')
SIMILARITY_SEARCH_L = os.getenv('SIMILARITY_SEARCH_L')
CHUNK_SIZE = os.getenv('CHUNK_SIZE')

def load_config():
    vertexai.init(project=PROJECT_ID)
    genai.configure(api_key=GEMINI_API_KEY)