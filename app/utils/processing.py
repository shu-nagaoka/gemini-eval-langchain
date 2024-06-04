import io
import os
import anyio
from utils.pdf_utils import check_existing_pdf, extract_chunks_from_pdf, save_temp_pdf, move_pdf_to_directory
from utils.db_utils import get_answer_from_db, vectorstore
from utils.answer_utils import get_answer_from_documents
import google.generativeai as genai
from utils.eval_task import evaluate_rag
import pandas as pd
from io import StringIO

PDF_DIRECTORY = "/Users/tnoce/env/work/miyazakishi/google-vais/app-gemini-eval/app/pdf"

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
        existing_db_answer = await get_answer_from_db(query)
        return "このPDFはすでに処理済みです。", existing_db_answer, None, None
    else:
        pdf_path = move_pdf_to_directory(temp_pdf_path, PDF_DIRECTORY)
        chunks = extract_chunks_from_pdf(pdf_path)
        add_chunks_to_vectorstore(chunks)
        new_pdf_answer = await get_answer_from_new_pdf(chunks, query)
        existing_db_answer = await get_answer_from_db(query)

    return new_pdf_answer, existing_db_answer

async def get_answer_from_new_pdf(chunks, query):
    """新しいPDFから回答を取得する"""
    safety_settings = {
        "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
        "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
        "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
        "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
    }
    results = vectorstore.similarity_search(query, k=10)
    relevant_chunks = results
    context = get_answer_from_documents(relevant_chunks, query)

    model = genai.GenerativeModel('gemini-1.5-flash-001', safety_settings=safety_settings)
    response = model.generate_content(
        f"あなたは有能なアシスタントです。\n\n"
        f"以下のコンテキストに基づいて質問に答えてください。\n\n"
        f"コンテキスト: {context}\n\n"
        f"質問: {query}"
    )

    # 安全性評価の確認とエラーハンドリング
    # if not response.candidates or not hasattr(response.candidates[0], 'text'):
    #     safety_ratings = response.candidates[0].safety_ratings if response.candidates else "No candidates"
    #     raise ValueError(f"生成されたテキストがブロックされました。安全性評価: {safety_ratings}")
    # eval_summary, eval_table = await evaluate_rag(query, context, response.text.strip(), instruction="あなたの仕事は事前の知識データベースを元に質問に答えることです。")
    # print("評価結果サマリー:", eval_summary)
    # print("評価結果テーブル:", eval_table.to_string(max_colwidth=400))
    return response.text.strip()

def process_pdf(pdf_file, query):
    """PDFを処理し、クエリに対する回答を生成する (同期版)"""
    return anyio.run(async_process_pdf, pdf_file, query)