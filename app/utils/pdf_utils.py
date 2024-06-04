import os
import fitz
import shutil
import tempfile
from langchain.schema import Document
from dotenv import load_dotenv
load_dotenv()

PDF_DIRECTORY = "/Users/tnoce/env/work/miyazakishi/google-vais/app-gemini-eval/app/pdf"

def check_existing_pdf(pdf_path):
    """ローカルにすでにPDFがあるかを確認する"""
    file_name = os.path.basename(pdf_path)
    actual_pdf_path = os.path.join(PDF_DIRECTORY, file_name)
    print(f"check_existing_pdf関数: actual_pdf_path={actual_pdf_path}\n")

    if os.path.exists(actual_pdf_path):
        print(f"{actual_pdf_path}が存在してます。")
        return True
    else:
        print(f"{actual_pdf_path}がPDFファイルが存在しないっす。")
        return False

def extract_chunks_from_pdf(pdf_path, chunk_size=1000):
    """PDFからページごとにチャンクを抽出する"""
    print(repr(f"PDFのパスは...{pdf_path}"))
    chunks = []
    doc = fitz.open(pdf_path)
    print(doc)
    text = ""
    for page_num in range(len(doc)):
        page = doc[page_num]
        text += page.get_text()
        print(text)
        while len(text) >= chunk_size:
            chunks.append(Document(page_content=text[:chunk_size], metadata={"chunk_id": len(chunks), "page_num": page_num}))
            text = text[chunk_size:]
    if text:
        chunks.append(Document(page_content=text, metadata={"chunk_id": len(chunks), "page_num": page_num}))
        print(chunks)
    return chunks

def save_temp_pdf(pdf_file):
    """一時ファイルとしてPDFを保存する"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(pdf_file.read())
        return temp_file.name

def move_pdf_to_directory(pdf_path, directory):
    """PDFを指定されたディレクトリに移動する"""
    new_pdf_path = os.path.join(directory, os.path.basename(pdf_path))
    shutil.move(pdf_path, new_pdf_path)
    return new_pdf_path