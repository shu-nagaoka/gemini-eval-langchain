from langchain.embeddings.base import Embeddings
from typing import List
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()

EMBED_MODEL = os.getenv('EMBED_MODEL')

class GeminiEmbeddings(Embeddings):
    def __init__(self, model_name=EMBED_MODEL):
        super().__init__()
        self.model_name = model_name

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """複数のテキストを埋め込む"""
        if not texts or any(not text for text in texts):
            raise ValueError("'texts' 引数は空であってはならず、また空の文字列を含んではなりません。")

        embeddings = genai.embed_content(
            model=self.model_name,
            content=texts,
            task_type="RETRIEVAL_DOCUMENT"
        )
        return embeddings['embedding']

    def embed_query(self, text: str) -> List[float]:
        """単一のテキストを埋め込む"""
        if not text:
            raise ValueError("'text' 引数は空にできません。")

        embedding = genai.embed_content(
            model=self.model_name,
            content=text,
            task_type="RETRIEVAL_DOCUMENT"
        )
        return embedding['embedding']