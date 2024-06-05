import io
import os
import anyio
from utils.pdf_utils import check_existing_pdf, extract_chunks_from_pdf, save_temp_pdf, move_pdf_to_directory
from utils.db_utils import get_answer_from_db, vectorstore
from utils.answer_utils import get_answer_from_documents
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

PDF_DIRECTORY = os.path.join(os.path.dirname(__file__), '..', 'pdf')

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

    if check_existing_pdf(temp_pdf_path):
        db_answer, eval_summary, eval_summary_formatted, eval_table = await get_answer_from_db(query)
        return "このPDFはすでに処理済みです。", db_answer, eval_summary_formatted, eval_table
    else:
        pdf_path = move_pdf_to_directory(temp_pdf_path, PDF_DIRECTORY)
        chunks = extract_chunks_from_pdf(pdf_path)
        add_chunks_to_vectorstore(chunks)
        return "新規PDFとしてベクトル化が完了しました。", None, None, None

def process_pdf(pdf_file, query):
    """PDFを処理し、クエリに対する回答を生成する (同期版)"""
    return anyio.run(async_process_pdf, pdf_file, query)