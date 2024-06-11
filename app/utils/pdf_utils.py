import io
import os
import fitz
import shutil
import tempfile
from langchain.schema import Document
from .eval_task import evaluate_rag
import google.generativeai as genai
from .db_utils import format_eval_summary
from google.cloud import storage


from dotenv import load_dotenv
load_dotenv()

PDF_DIRECTORY = os.path.join(os.path.dirname(__file__), '..', 'pdf')


import logging
from datetime import datetime
current_date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
log_filename = f"logs-{current_date}.log"
logging.basicConfig(filename=log_filename,
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def upload_to_gcs(temp_file_path, bucket_name, destination_blob_name):
    """GCSバケットにファイルをアップロードする"""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    try:
        blob.upload_from_filename(temp_file_path)
        logging.info(f"GCSにアップロード完了: gs://{bucket_name}/{destination_blob_name}")
    except Exception as e:
        logging.error(f"ファイルのアップロードに失敗しました。{e}")
        return None

def extract_chunks_from_pdf(pdf_path, chunk_size=1000):
    """PDFからページごとにチャンクを抽出する"""
    chunks = []
    doc = fitz.open(pdf_path)
    logging.info(doc)
    text = ""
    for page_num in range(len(doc)):
        page = doc[page_num]
        text += page.get_text()
        logging.info(text)
        while len(text) >= chunk_size:
            chunks.append(Document(page_content=text[:chunk_size], metadata={"chunk_id": len(chunks), "page_num": page_num}))
            text = text[chunk_size:]
    if text:
        chunks.append(Document(page_content=text, metadata={"chunk_id": len(chunks), "page_num": page_num}))
        logging.info(chunks)
    return chunks

def save_temp_pdf(pdf_file):
    """一時ファイルとしてPDFを保存する"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(pdf_file.read())
        return temp_file.name

async def get_answer_from_pdf(pdf_path, query):
    """PDFから抽出したテキストを使用して質問に回答する"""
    chunks = extract_chunks_from_pdf(pdf_path)
    if not chunks:
        return "PDFからテキストを抽出できませんでした。", None, None

    context = " ".join(chunk.page_content for chunk in chunks)
    model = genai.GenerativeModel('gemini-1.5-flash-001')
    response = model.generate_content(
        f"あなたは有能なアシスタントです。\n\n"
        f"以下のコンテキストに基づいて質問に答えてください。\n\n"
        f"コンテキスト: {context}\n\n"
        f"質問: {query}"
    )
    eval_summary, formatted_response = await evaluate_rag(query, context, response.text.strip(), instruction="事実に基づく回答のみを提供してください。")
    logging.info("評価結果サマリー:", eval_summary)
    logging.info("評価結果テーブル(構造化済み):", formatted_response)
    return response.text.strip(), eval_summary, format_eval_summary(eval_summary), formatted_response.strip()