"""
モジュール 5: RetrieveAndGenerate（RAG をエンドツーエンドで実行）
------------------------------------------------------------
Knowledge Base に対して RetrieveAndGenerate API を呼び出し、
検索 → プロンプト拡張 → 回答生成 → 引用取得を一度に行います。

事前に Knowledge Base を作成し、その ID を環境変数 KB_ID に設定してください（steps.md 参照）。

使い方:
    export KB_ID=XXXXXXXXXX
    python retrieve_and_generate.py
    python retrieve_and_generate.py "Business プランのバックアップ保持期間は？"
"""

import os
import sys
import boto3
from botocore.config import Config

REGION = "us-east-1"
# 回答生成に使うモデル（推論プロファイル ARN 形式で指定）
MODEL_ARN = (
    f"arn:aws:bedrock:{REGION}:"
    "{account}:inference-profile/us.anthropic.claude-sonnet-4-5-20250929-v1:0"
)


def main():
    kb_id = os.environ.get("KB_ID")
    if not kb_id:
        print("環境変数 KB_ID を設定してください（例: export KB_ID=XXXXXXXXXX）")
        sys.exit(1)

    query = sys.argv[1] if len(sys.argv) > 1 else "Enterprise プランのバックアップ保持期間は何日ですか？"

    # アカウント ID を取得して推論プロファイル ARN を組み立てる
    account_id = boto3.client("sts", region_name=REGION).get_caller_identity()["Account"]
    model_arn = MODEL_ARN.format(account=account_id)

    agent_rt = boto3.client(
        "bedrock-agent-runtime",
        region_name=REGION,
        config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
    )

    print("=" * 60)
    print(" RetrieveAndGenerate（RAG）")
    print("=" * 60)
    print(f"\n質問: {query}\n")

    resp = agent_rt.retrieve_and_generate(
        input={"text": query},
        retrieveAndGenerateConfiguration={
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": kb_id,
                "modelArn": model_arn,
            },
        },
    )

    print("回答:")
    print(f"  {resp['output']['text']}")

    # 引用（根拠）を表示
    print("\n引用（根拠となったソース）:")
    for i, citation in enumerate(resp.get("citations", []), 1):
        for ref in citation.get("retrievedReferences", []):
            loc = ref.get("location", {})
            snippet = ref.get("content", {}).get("text", "")[:120]
            print(f"  [{i}] {loc}")
            print(f"      \"{snippet}...\"")

    print("\nポイント: 回答が社内ドキュメントに基づき、引用付きで返ることを確認しましょう。")


if __name__ == "__main__":
    main()
