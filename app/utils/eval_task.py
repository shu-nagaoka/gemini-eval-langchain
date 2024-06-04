from vertexai.preview.evaluation import EvalTask
import pandas as pd
import anyio
import asyncio
import google.generativeai as genai

async def evaluate_rag(query, context, answer, instruction=""):  # instruction を追加
    """RAGの評価を行い、評価結果のサマリーと詳細を返す"""
    eval_dataset = pd.DataFrame(
        {
            "content": [query],
            "context": [context],  # context を追加
            "response": [answer],
            "instruction": [instruction],  # instruction を追加
        }
    )
    eval_task = EvalTask(
        dataset=eval_dataset,
        metrics=[
            # "question_answering_quality",
            # "question_answering_relevance",
            # "question_answering_helpfulness",
            "groundedness",
            # "fulfillment",
        ],
        experiment="rag-eval-shimashi-01",
    )
    print("EvalTask object created:", eval_task)


    # anyio.to_thread.run_sync 内でイベントループを作成・設定
    def run_eval_task():  # async def を削除
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # return eval_task.evaluate(model=GenerativeModel("gemini-pro", generation_config={"temperature": 0.5, "top_k": 1}))
            # eval_task.evaluate を直接実行
            return eval_task.evaluate()

        finally:
            loop.close()

    # run_sync に同期関数 run_eval_task を渡す
    eval_result = await anyio.to_thread.run_sync(run_eval_task)
    print(eval_result)

    model = genai.GenerativeModel('gemini-1.5-flash-001')
    formatted_metrics_table = model.generate_content(
        f"以下の評価結果の詳細を原文に忠実に日本語で説明できるように構造化してください:\n{eval_result}"
    )
    # return eval_result.summary_metrics, eval_result.metrics_table
    return eval_result.summary_metrics, formatted_metrics_table.text.strip()