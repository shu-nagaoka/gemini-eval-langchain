from openai import OpenAI
from langchain_community.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
import google.generativeai as genai
from .eval_task import evaluate_rag
import os

from dotenv import load_dotenv
load_dotenv()

client = OpenAI()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PERSIST_DIRECTORY = os.path.join(os.path.dirname(__file__), '..', 'db')

embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
vectorstore = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embeddings)

def format_eval_summary(eval_summary):
    return "\n".join([f"{key}: {value}" for key, value in eval_summary.items()])

async def get_answer_from_db(query):
    """既存のベクトルDBから回答を取得する"""
    print(f"get_answer_from_db関数: query={repr(query)}")
    results = vectorstore.similarity_search(query, k=5)
    print(f"get_answer_from_db関数: results={repr(results)}")

    if results:
        context = results[0].page_content
        model = genai.GenerativeModel('gemini-1.5-flash-001')
        response = model.generate_content(
            f"あなたは有能なアシスタントです。\n\n"
            f"以下のコンテキストに基づいて質問に答えてください。\n\n"
            f"コンテキスト: {context}\n\n"
            f"質問: {query}"
        )

        eval_summary, formatted_response = await evaluate_rag(query, context, response.text.strip(), instruction="事実に基づく回答のみを提供してください。")
        print("評価結果サマリー:", eval_summary)
        print("評価結果テーブル(構造化済み):", formatted_response)
        return response.text.strip(), eval_summary, format_eval_summary(eval_summary), formatted_response.strip()
    else:
        return "データベースに一致するドキュメントがありませんでした。", None, None