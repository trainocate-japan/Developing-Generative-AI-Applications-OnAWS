"""
モジュール 5: Retrieve（生チャンク取得）+ 自前で回答生成
------------------------------------------------------------
Retrieve API で関連チャンクだけを取得し、独自プロンプトに埋め込んで
Converse API で回答を生成します。カスタムプロンプトや再ランク付け、
複数 KB の統合など、柔軟な後処理をしたい場合に使います。

使い方:
    export KB_ID=XXXXXXXXXX
    python retrieve_only.py
    python retrieve_only.py "ログインできないときの原因は？"
"""

import os
import sys
import boto3
from botocore.config import Config

REGION = "us-east-1"
GEN_MODEL_ID = "us.amazon.nova-lite-v1:0"
TOP_K = 3


def main():
    kb_id = os.environ.get("KB_ID")
    if not kb_id:
        print("環境変数 KB_ID を設定してください（例: export KB_ID=XXXXXXXXXX）")
        sys.exit(1)

    query = sys.argv[1] if len(sys.argv) > 1 else "ログインできないときの主な原因を教えてください。"

    cfg = Config(retries={"max_attempts": 5, "mode": "adaptive"})
    agent_rt = boto3.client("bedrock-agent-runtime", region_name=REGION, config=cfg)
    br = boto3.client("bedrock-runtime", region_name=REGION, config=cfg)

    print("=" * 60)
    print(" Retrieve（生チャンク取得）+ 手動生成")
    print("=" * 60)
    print(f"\n質問: {query}\n")

    # 1. 関連チャンクを取得
    retrieval = agent_rt.retrieve(
        knowledgeBaseId=kb_id,
        retrievalQuery={"text": query},
        retrievalConfiguration={
            "vectorSearchConfiguration": {"numberOfResults": TOP_K}
        },
    )
    chunks = retrieval.get("retrievalResults", [])

    print(f"取得したチャンク: {len(chunks)} 件")
    context_parts = []
    for i, c in enumerate(chunks, 1):
        text = c.get("content", {}).get("text", "")
        score = c.get("score")
        context_parts.append(f"[{i}] {text}")
        print(f"  [{i}] score={score:.3f} {text[:80]}...")

    # 2. 取得チャンクを使って自前のプロンプトで回答生成
    context = "\n\n".join(context_parts)
    prompt = (
        "あなたは社内ヘルプデスクのアシスタントです。以下のコンテキストのみに基づいて、"
        "日本語で簡潔に回答してください。コンテキストにない場合は「情報がありません」と答えてください。\n\n"
        f"# コンテキスト\n{context}\n\n# 質問\n{query}"
    )

    resp = br.converse(
        modelId=GEN_MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 400, "temperature": 0.2, "topP": 0.9},
    )
    answer = resp["output"]["message"]["content"][0]["text"].strip()

    print("\n生成した回答:")
    print(f"  {answer}")

    print("\nポイント: Retrieve は生チャンクを返すため、プロンプトや生成モデルを")
    print("自由に制御できます（RetrieveAndGenerate はこれを一括で行う簡易版）。")


if __name__ == "__main__":
    main()
