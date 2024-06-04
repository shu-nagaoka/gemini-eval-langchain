import vertexai
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
PROJECT_ID = os.getenv('PROJECT_ID')

def load_config():
    # vertexai.init(project="certain-frame-338210")
    # genai.configure(api_key="AIzaSyCiA-H5fUVo1mx-Am_yHpgNYFCsHCizIRg")
    vertexai.init(project=PROJECT_ID)
    genai.configure(api_key=GEMINI_API_KEY)