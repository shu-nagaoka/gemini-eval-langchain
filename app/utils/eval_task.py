from vertexai.preview.evaluation import EvalTask
import pandas as pd
import anyio
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()


import logging
from datetime import datetime
current_date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
log_filename = f"logs-{current_date}.log"
logging.basicConfig(filename=log_filename,
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

async def evaluate_rag(query, context, answer, instruction=""):
    """RAGの評価を行い、評価結果のサマリーと詳細を返す"""
    eval_dataset = pd.DataFrame(
        {
            "content": [query],
            "context": [context],
            "response": [answer],
            "instruction": [instruction],
        }
    )
    eval_task = EvalTask(
        dataset=eval_dataset,
        metrics=[
            "question_answering_quality",
            "question_answering_relevance",
            "question_answering_helpfulness",
            "groundedness",
            "fulfillment",
        ],
        experiment="rag-eval-01",
    )
    logging.info(f"EvalTask object created:{eval_task}")

    # score_sample = """
    #                 | Result名                                   | スコア値                                                                                                                                          | 説明                                                            | 確信度     |
    #                 |--------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------|------------|
    #                 | ExactMatchResults                          | 0: 完全一致しない<br>1: 完全一致                                                                                                                  | -                                                              | -          |
    #                 | BleuResults                                | [0, 1] 高いほど予測が参照に近い                                                                                                                   | -                                                              | -          |  
    #                 | RougeResults                               | [0, 1] 高いほど予測が参照に近い                                                                                                                   | -                                                              | -          |
    #                 | FluencyResult                              | 1: 不明瞭<br>2: やや不明瞭<br>3: 普通<br>4: ややわかりやすい<br>5: わかりやすい                                                                   | スコアの根拠を説明                                             | [0, 1]     |
    #                 | CoherenceResult                            | 1: 一貫性なし<br>2: やや一貫性なし<br>3: 普通<br>4: やや一貫性あり<br>5: 一貫性あり                                                               | スコアの根拠を説明                                             | [0, 1]     | 
    #                 | SafetyResult                               | 0: 安全でない<br>1: 安全                                                                                                                          | スコアの根拠を説明                                             | [0, 1]     |
    #                 | GroundednessResult                         | 0: 根拠なし<br>1: 根拠あり                                                                                                                        | スコアの根拠を説明                                             | [0, 1]     |
    #                 | FulfillmentResult                          | 1: 指示に沿っていない<br>2: 指示に沿っていない<br>3: ある程度指示に沿っている<br>4: 指示にほぼ沿っている<br>5: 指示に完全に沿っている           | スコアの根拠を説明                                             | [0, 1]     |
    #                 | SummarizationQualityResult                 | 1: 非常に悪い<br>2: 悪い<br>3: 普通<br>4: 良い<br>5: 非常に良い                                                                                   | スコアの根拠を説明                                             | [0, 1]     |
    #                 | PairwiseSummarizationQualityResult         | BASELINE: ベースラインの予測が良い<br>CANDIDATE: 候補の予測が良い<br>TIE: 両者同点                                                                 | ペアワイズ選択の根拠を説明                                     | [0, 1]     |
    #                 | SummarizationHelpfulnessResult             | 1: 役に立たない<br>2: あまり役に立たない<br>3: 普通<br>4: ある程度役に立つ<br>5: 役に立つ                                                         | スコアの根拠を説明                                             | [0, 1]     |
    #                 | SummarizationVerbosityResult               | -2: 簡潔すぎる<br>-1: やや簡潔すぎる<br>0: 最適<br>1: やや冗長<br>2: 冗長                                                                         | スコアの根拠を説明                                             | [0, 1]     |
    #                 | QuestionAnsweringQualityResult             | 1: 非常に悪い<br>2: 悪い<br>3: 普通<br>4: 良い<br>5: 非常に良い                                                                                   | スコアの根拠を説明                                             | [0, 1]     |
    #                 | PairwiseQuestionAnsweringQualityResult     | BASELINE: ベースラインの予測が良い<br>CANDIDATE: 候補の予測が良い<br>TIE: 両者同点                                                                 | ペアワイズ選択の根拠を説明                                     | [0, 1]     |
    #                 | QuestionAnsweringRelevancyResult           | 1: 無関係<br>2: やや無関係<br>3: 普通<br>4: ある程度関連性あり<br>5: 関連性が高い                                                                 | スコアの根拠を説明                                             | [0, 1]     | 
    #                 | QuestionAnsweringHelpfulnessResult         | 1: 役に立たない<br>2: あまり役に立たない<br>3: 普通<br>4: ある程度役に立つ<br>5: 役に立つ                                                         | スコアの根拠を説明                                             | [0, 1]     |
    #                 | QuestionAnsweringCorrectnessResult         | 0: 不正解<br>1: 正解                                                                                                                              | スコアの根拠を説明                                             | [0, 1]     | 
    #                 | ToolCallValidResults                       | 0: 無効なツール呼び出し<br>1: 有効なツール呼び出し                                                                                                | -                                                              | -          |
    #                 | ToolNameMatchResults                       | 0: ツール名が参照と一致しない<br>1: ツール名が参照と一致する                                                                                      | -                                                              | -          |
    #                 | ToolParameterKeyMatchResults               | [0, 1] 高いほどパラメータ名が参照と一致                                                                                                           | -                                                              | -          |
    #                 | ToolParameterKVMatchResults                | [0, 1] 高いほどパラメータ名と値が参照と一致                                                                                                       | -                                                              | -          |
    #                 """
    score_sample_new = """
                    | Result名                                   | スコア値                                                                                                                                          | 説明                                                            | 確信度     |
                    |--------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------|------------|
                    | groundedness                               | 0: 根拠なし<br>1: 根拠あり                                                                                                                        | スコアの根拠を説明                                             | [0, 1]     |
                    | fulfillment                                | 1: 指示に沿っていない<br>2: 指示に沿っていない<br>3: ある程度指示に沿っている<br>4: 指示にほぼ沿っている<br>5: 指示に完全に沿っている           | スコアの根拠を説明                                             | [0, 1]     |
                    | question_answering_quality                 | 1: 非常に悪い<br>2: 悪い<br>3: 普通<br>4: 良い<br>5: 非常に良い                                                                                   | スコアの根拠を説明                                             | [0, 1]     |
                    | question_answering_relevance               | 1: 無関係<br>2: やや無関係<br>3: 普通<br>4: ある程度関連性あり<br>5: 関連性が高い                                                                 | スコアの根拠を説明                                             | [0, 1]     | 
                    | question_answering_helpfulness             | 1: 役に立たない<br>2: あまり役に立たない<br>3: 普通<br>4: ある程度役に立つ<br>5: 役に立つ                                                         | スコアの根拠を説明                                             | [0, 1]     |
                    """

    # anyio.to_thread.run_sync 内でイベントループを作成・設定
    def run_eval_task():  # async def を削除
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return eval_task.evaluate()
        finally:
            loop.close()

    # run_sync に同期関数 run_eval_task を渡す
    eval_result = await anyio.to_thread.run_sync(run_eval_task)
    logging.info(eval_result)

    model = genai.GenerativeModel('gemini-1.5-flash-001')
    formatted_metrics_table = model.generate_content(
        f"{eval_result}の評価結果の詳細を、{score_sample_new}の指標を参考にしながら、簡潔に箇条書きで構造化して評価してください。\n"
        f"{score_sample_new}は文中に表記させないでください。\n"
        f"特にgroundnessに注意して原文に忠実に日本語で説明できるように構造化してください:\n"
    )
    # return eval_result.summary_metrics, eval_result.metrics_table
    return eval_result.summary_metrics, formatted_metrics_table.text.strip()