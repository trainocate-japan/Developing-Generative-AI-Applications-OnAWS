"""
モジュール 4: 4 つのアーキテクチャパターン
------------------------------------------------------------
生成 / 要約 / 質問応答 / 会話 の 4 パターンを、同じ Converse API で実装します。
プロンプトの組み立て方だけで、さまざまなユースケースに対応できることを確認します。

実行:
    python architecture_patterns.py
"""

import boto3
from botocore.config import Config

REGION = "us-east-1"
MODEL_ID = "us.amazon.nova-lite-v1:0"


def converse(bedrock_runtime, messages, system=None, max_tokens=400):
    kwargs = {
        "modelId": MODEL_ID,
        "messages": messages,
        "inferenceConfig": {"maxTokens": max_tokens, "temperature": 0.5},
    }
    if system:
        kwargs["system"] = [{"text": system}]
    resp = bedrock_runtime.converse(**kwargs)
    return resp["output"]["message"]["content"][0]["text"].strip()


def main():
    br = boto3.client(
        "bedrock-runtime",
        region_name=REGION,
        config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
    )

    # 1. 生成
    print("=" * 60)
    print(" 1. 生成 (Generation)")
    print("=" * 60)
    print(converse(
        br,
        [{"role": "user", "content": [{"text": "オンラインストアの配送サービスに関する満足度の高い短いレビューを 2 文で書いてください。"}]}],
    ))

    # 2. 要約
    print("\n" + "=" * 60)
    print(" 2. 要約 (Summarization)")
    print("=" * 60)
    article = (
        "Amazon Bedrock は、複数プロバイダーの基盤モデルに単一 API でアクセスできる"
        "フルマネージドサービスです。Converse API による統一インターフェイス、"
        "Knowledge Bases による RAG、Guardrails による安全対策、Agents による自律実行など、"
        "生成 AI アプリに必要な機能を提供します。"
    )
    print(converse(
        br,
        [{"role": "user", "content": [{"text": f"次の文章を 1 文で要約してください。\n{article}"}]}],
    ))

    # 3. 質問応答
    print("\n" + "=" * 60)
    print(" 3. 質問応答 (Q&A)")
    print("=" * 60)
    print(converse(
        br,
        [{"role": "user", "content": [{"text": "Amazon Bedrock の Converse API を使う利点を 1 つ挙げてください。"}]}],
        system="簡潔に 1 文で答えてください。",
    ))

    # 4. 会話（次のスクリプトで詳しく扱う）
    print("\n" + "=" * 60)
    print(" 4. 会話 (Conversation) の入り口")
    print("=" * 60)
    print("会話パターンは履歴を messages に積み重ねます。")
    print("詳細は conversation_memory.py を実行してください。")


if __name__ == "__main__":
    main()
