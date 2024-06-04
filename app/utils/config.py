import vertexai
import google.generativeai as genai
import os

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
PROJECT_ID = os.getenv('PROJECT_ID')

def load_config():
    vertexai.init(project=PROJECT_ID)
    genai.configure(api_key=GEMINI_API_KEY)