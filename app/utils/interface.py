import gradio as gr
from .processing import process_pdf

iface = gr.Interface(
    fn=process_pdf,
    inputs=[
        gr.File(label="PDFファイルをアップロードしてください"),
        gr.Textbox(label="質問を入力してください")
    ],
    outputs=[
        gr.Textbox(label="新規PDFからの回答"),
        gr.Textbox(label="既存DBからの回答"),
        gr.Textbox(label="評価結果サマリー", max_lines=20),
        gr.Textbox(label="評価結果ディティール", max_lines=100),
    ],
    title="Eval_Gemini_PDF質問応答システム"
)

def launch_interface():
    iface.launch(debug=True)