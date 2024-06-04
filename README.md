# アプリケーションの説明
- このドキュメントは、Eval＿Gemini＿PDF質問応答システムのセットアップと起動方法について説明します。

## 前提条件
- `venv` で `Python 3.10` を使用してください。
- `pip` (Pythonパッケージマネージャ)を使用してください。

## セットアップ
1. 当該リポジトリをクローンします。

```bash
git clone <リポジトリURL>
cd app-gemini-eval
```

2. 仮想環境を作成し、アクティベートします。
```bash
python -m venv venv
source venv/bin/activate # Windowsの場合は venv\Scripts\activate
```

2. 必要なパッケージをインストールします。

```bash
pip install -r requirements.txt
```

3. 環境変数を設定します。プロジェクトルートに、`.env`ファイルを作成し、必要なAPI_KEYなどを設定します。

```.env
OPENAI_API_KEY=your_openai_api_key # 精度の都合上PDFのベクトル化のみに使用
GOOGLE_API_KEY=your_google_api_key # Gemini APIによる質問応答に使用
```


## 起動方法
- 以下のコマンドでアプリケーションを起動します。

```bash
python app/main.py
```

## ファイル構成
- `app/main.py`: アプリケーションのエントリーポイント
- `app/utils/db_utils.py`: データベース関連のユーティリティ
- `app/utils/interface.py`: Gradioインターフェースの設定
- `app/utils/eval_task.py`: 評価タスクの実行

## 使用方法
1. ブラウザで`http://localhost:7860`を開きます
2. PDFファイルをアップロードし、質問を入力します
3. 「新規PDFからの回答」および「既存DBからの回答」が表示されます。
4. 評価結果サマリーとディティールも表示されます。

## 注意事項
- 環境変数の設定が正しいことを確認してください。
- 必要なAPIキーを取得し、`.env` ファイルに設定してください。

以上でセットアップと起動方法の説明は終了です。問題が発生した場合は、リポジトリのIssueに報告してください。