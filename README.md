# アプリケーションの説明
- このドキュメントは、Eval＿Gemini＿PDF質問応答システムのセットアップと起動方法について説明します。

## 前提条件
- `venv` で `Python 3.10` を使用してください。
- `pip` (Pythonパッケージマネージャ)を使用してください。

## セットアップ
1. 当該リポジトリをクローンします。

```bash
git clone <リポジトリURL>
cd gemini-eval-langchain
```

2. 仮想環境を作成し、アクティベートします。
```bash
python3.10 -m venv venv
source ./venv/bin/activate # Windowsの場合は .\venv\Scripts\activate
```

2. 必要なパッケージをインストールします。

```bash
pip install -r requirements.txt
```

3. 環境変数を設定します。`.env.example`をコピーしてプロジェクトルートに、`.env`ファイルを作成し、必要なAPI_KEYなどを設定します。

```.env
# Google Cloud プロジェクト内で取得したAPIKEY
GEMINI_API_KEY=-

# OpenAPIで取得したAPIKEY（ベクトル化に使用）
OPENAI_API_KEY=

# Google CloudのProjectID
PROJECT_ID=
```


## 起動方法
- 以下のコマンドでアプリケーションを起動します。

```bash
python ./app/main.py
```

## ファイル構成
- `app/main.py`: アプリケーションのエントリーポイント
- `app/utils/answer_utils.py`: 質問応答のためのユーティリティ
- `app/utils/db_utils.py`: データベース関連のユーティリティ
- `app/utils/interface.py`: Gradioインターフェースの設定
- `app/utils/pdf_utils.py`: PDF処理のためのユーティリティ
- `app/utils/processing.py`: PDFの処理とクエリに対する回答生成

## 使用方法
1. ブラウザで`http://localhost:7860`を開きます
2. PDFファイルをアップロードし、Submitをクリックします
3. DBにベクトル化されるので、以降は質問を送信することができます
4. 質問を送信すると、既存DBから回答をが返されます
5. 同時に評価結果サマリーとディティールも表示されます

## 注意事項
- 環境変数の設定が正しいことを確認してください。
- 必要なAPIキーを取得し、`.env` ファイルに設定してください。

以上でセットアップと起動方法の説明は終了です。問題が発生した場合は、リポジトリのIssueに報告してください。