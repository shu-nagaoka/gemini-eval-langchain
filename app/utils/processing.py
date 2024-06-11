import io
import os
import anyio
from utils.pdf_utils import extract_chunks_from_pdf, save_temp_pdf, upload_to_gcs
from utils.db_utils import get_answer_from_db, vectorstore
from utils.answer_utils import get_answer_from_documents
import google.generativeai as genai
import tempfile
from google.cloud import storage
from dotenv import load_dotenv
load_dotenv()

PDF_DIRECTORY = os.path.join(os.path.dirname(__file__), '..', 'pdf')
GCS_BUCKET_NAME = os.getenv('GCS_BUCKET_NAME')

import logging
from datetime import datetime
current_date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
log_filename = f"logs-{current_date}.log"
logging.basicConfig(filename=log_filename,
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_pdf_path(pdf_file):
    """PDFファイルのパスを取得する"""
    if isinstance(pdf_file, str):
        return os.path.join(PDF_DIRECTORY, pdf_file)
    else:
        return pdf_file

def add_chunks_to_vectorstore(chunks):
    """チャンクをベクトルストアに追加する"""
    chunk_size = 10
    for i in range(0, len(chunks), chunk_size):
        vectorstore.add_documents(chunks[i:i+chunk_size])

def check_existing_pdf_in_gcs(bucket_name, blob_name):
    """GCSにすでにPDFがあるかを確認する"""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return blob.exists()

async def async_process_pdf(pdf_file, query):
    """PDFを処理し、クエリに対する回答を生成する (非同期版)"""
    if pdf_file is None:
        db_answer, eval_summary, eval_summary_formatted, eval_table = await get_answer_from_db(query)
        return "PDFファイルが選択されていません。", db_answer, eval_summary_formatted, eval_table

    pdf_path = get_pdf_path(pdf_file)
    if isinstance(pdf_path, io.BytesIO):
        temp_pdf_path = save_temp_pdf(pdf_path)
    else:
        temp_pdf_path = pdf_path

    destination_blob_name = os.path.basename(temp_pdf_path)
    logging.info(f"添付されたファイル名: {destination_blob_name}")

    # GCSバケット内にPDFファイルが存在するかを確認
    if check_existing_pdf_in_gcs(GCS_BUCKET_NAME, destination_blob_name):
        db_answer, eval_summary, eval_summary_formatted, eval_table = await get_answer_from_db(query)
        return "このPDFはGCSバケットに保存されており、すでに処理済みです。", db_answer, eval_summary_formatted, eval_table
    else:
        # GCSへのuploadの開始
        logging.info(f"{GCS_BUCKET_NAME}へアップロードを開始します。")
        upload_to_gcs(temp_pdf_path, GCS_BUCKET_NAME, destination_blob_name)
        logging.info(f"{GCS_BUCKET_NAME}へアップロードが完了しました。")

        # GCSからPDFをダウンロードしてチャンクを抽出
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(destination_blob_name)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            blob.download_to_filename(temp_file.name)
            chunks = extract_chunks_from_pdf(temp_file.name)
        add_chunks_to_vectorstore(chunks)
        return "新規PDFとしてベクトル化が完了しました。", None, None, None

def process_pdf(pdf_file, query):
    """PDFを処理し、クエリに対する回答を生成する (同期版)"""
    return anyio.run(async_process_pdf, pdf_file, query)