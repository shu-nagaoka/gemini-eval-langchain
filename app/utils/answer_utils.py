from typing import Any, List, Mapping, Optional
from langchain.llms.base import LLM
from langchain.chains.question_answering import load_qa_chain
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

# Gemini APIの設定
genai.configure(api_key='AIzaSyCiA-H5fUVo1mx-Am_yHpgNYFCsHCizIRg')
MODEL_NAME="gemini-1.5-pro-001"

# Gemini API用のカスタムLLMクラス
class GeminiLLM(LLM):
    @property
    def _llm_type(self) -> str:
        return "custom"
    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs: Any) -> str:
        """Gemini APIを呼び出してテキストを生成する"""
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text.strip()

def get_answer_from_documents(documents, query):
    """アップロードされたPDFから回答を取得する"""
    llm = GeminiLLM()
    chain = load_qa_chain(llm, chain_type="stuff")
    return chain.run(input_documents=documents, question=query)
