from dotenv import load_dotenv
import vertexai
import google.generativeai as genai

def load_config():
    load_dotenv()
    vertexai.init(project="certain-frame-338210")
    genai.configure(api_key='AIzaSyCiA-H5fUVo1mx-Am_yHpgNYFCsHCizIRg')