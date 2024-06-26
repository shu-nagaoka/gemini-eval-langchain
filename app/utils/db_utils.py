from openai import OpenAI
from langchain_community.vectorstores import Chroma
from .embeddings import GeminiEmbeddings
import google.generativeai as genai
from .eval_task import evaluate_rag
import os
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
PERSIST_DIRECTORY = os.path.join(os.path.dirname(__file__), '..', 'db')
SIMILARITY_SEARCH_K = os.getenv('SIMILARITY_SEARCH_K')
GEMINI_MODEL = os.getenv('GEMINI_MODEL')


import logging
from datetime import datetime
current_date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

log_directory = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_directory, exist_ok=True)
log_filename = os.path.join(log_directory, f"logs-{current_date}.log")

logging.basicConfig(filename=log_filename, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

"""
GeminiでEmbeddingを行う
"""
embeddings = GeminiEmbeddings()
vectorstore = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embeddings)

"""
OpenAIでEmbeddingを行う場合以下のコメントアウトを外していただき、GeminiでEmbeddingの2行をコメントアウトしてください。
"""
# EMBED_MODEL = os.getenv('EMBED_MODEL')
# from langchain.embeddings import OpenAIEmbeddings
# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# embeddings = OpenAIEmbeddings(model=EMBED_MODEL)
# vectorstore = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embeddings)

def format_eval_summary(eval_summary):
    return "\n".join([f"{key}: {value}" for key, value in eval_summary.items()])

async def get_answer_from_db(query):
    """既存のベクトルDBから回答を取得する"""
    logging.info(f"get_answer_from_db関数: {query}")
    results = vectorstore.similarity_search(query, k=int(SIMILARITY_SEARCH_K))
    logging.info(f"get_answer_from_db関数:{results}")

    if results:
        # context = results[0].page_content
        contexts = [result.page_content for result in results]
        combined_context = "\n\n".join(contexts)
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(
            f"あなたは有能なアシスタントです。\n\n"
            f"以下のコンテキストに基づいて質問に答えてください。\n\n"
            f"コンテキスト: {combined_context}\n\n"
            f"質問: {query}"
        )

        eval_summary, formatted_response = await evaluate_rag(query, combined_context, response.text.strip(), instruction="事実に基づく回答のみを提供してください。")
        # logging.info(f"combined_contexts: {combined_context}")
        logging.info(f"評価結果サマリー: {eval_summary}")
        logging.info(f"評価結果テーブル(構造化済み): {formatted_response}")
        return response.text.strip(), eval_summary, format_eval_summary(eval_summary), formatted_response.strip()
    else:
        return "データベースに一致するドキュメントがありませんでした。", None, None, None