"""
モジュール 1: 基本的な生成 AI アプリケーションのアーキテクチャ
------------------------------------------------------------
生成 AI アプリの 4 つの主要コンポーネントを、最小構成のコードで表現します。

  1. アプリケーションフロントエンド  -> この例では標準入力 / 固定の質問
  2. アプリケーションロジック        -> build_prompt() でプロンプトを組み立てる
  3. FM インターフェイス             -> Amazon Bedrock Converse API
  4. 基盤モデル (FM)                 -> Amazon Nova Lite

「コンテキスト」がどのように渡り、応答が返るのかを体感します。

実行:
    python basic_app_architecture.py
"""

import boto3
from botocore.config import Config

REGION = "us-east-1"
# 推論プロファイル ID（クロスリージョン推論）を使用
MODEL_ID = "us.amazon.nova-lite-v1:0"


def build_prompt(user_question: str) -> list:
    """アプリケーションロジック: ユーザー入力を Converse API の messages 形式に変換する"""
    return [{"role": "user", "content": [{"text": user_question}]}]


def call_fm(bedrock_runtime, messages: list) -> str:
    """FM インターフェイス: Converse API で基盤モデルを呼び出す"""
    response = bedrock_runtime.converse(
        modelId=MODEL_ID,
        messages=messages,
        system=[{"text": "あなたは親切な旅行アシスタントです。簡潔に日本語で答えてください。"}],
        # maxTokens は必ず明示する（未指定はスロットリングの原因）
        inferenceConfig={"maxTokens": 512, "temperature": 0.7, "topP": 0.9},
    )
    return response["output"]["message"]["content"][0]["text"]


def main():
    # FM インターフェイス: bedrock-runtime（データプレーン）クライアント
    bedrock_runtime = boto3.client(
        "bedrock-runtime",
        region_name=REGION,
        config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
    )

    print("=" * 60)
    print(" 最小構成の生成 AI アプリケーション")
    print("=" * 60)

    # 1. フロントエンド（ここでは固定の質問）
    question = "シアトルで一番訪問するべき場所はどこですか？1 つだけ教えてください。"
    print(f"\n[フロントエンド] ユーザーの質問:\n  {question}")

    # 2. アプリケーションロジック
    messages = build_prompt(question)
    print("\n[アプリケーションロジック] Converse messages を組み立てました。")

    # 3-4. FM インターフェイス -> 基盤モデル
    print("\n[FM インターフェイス] Amazon Bedrock Converse API を呼び出し中...")
    answer = call_fm(bedrock_runtime, messages)

    print("\n[基盤モデルの応答]")
    print(f"  {answer}")

    print("\n" + "=" * 60)
    print(" ポイント:")
    print("  - この 4 コンポーネントが最小の生成 AI アプリを構成します。")
    print("  - 会話を続けたい場合は『メモリ』、社内データを参照したい場合は")
    print("    『ベクトルストア(RAG)』、外部操作をしたい場合は『エージェント』")
    print("    といったオプションコンポーネントを追加していきます。")
    print("  - これらは後続のモジュール (M04, M05, M09, M10) で扱います。")
    print("=" * 60)


if __name__ == "__main__":
    main()
