"""
モジュール 3: プロンプトテンプレート（再利用可能なプロンプト）
------------------------------------------------------------
プレースホルダーを持つテンプレートを定義し、変数を差し込んで再利用します。
一貫性・再利用性・テスト容易性・スケーラビリティが得られます。

実行:
    python prompt_template.py
"""

import boto3
from botocore.config import Config

REGION = "us-east-1"
MODEL_ID = "us.amazon.nova-lite-v1:0"

# 要約用テンプレート（{category} と {text} と {length} を差し込む）
SUMMARY_TEMPLATE = (
    "以下は {category} のテキストです:\n"
    "---\n{text}\n---\n"
    "この {category} を {length}で要約してください。"
)


def ask(bedrock_runtime, prompt: str) -> str:
    resp = bedrock_runtime.converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 300, "temperature": 0.3, "topP": 0.9},
    )
    return resp["output"]["message"]["content"][0]["text"].strip()


def main():
    bedrock_runtime = boto3.client(
        "bedrock-runtime",
        region_name=REGION,
        config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
    )

    review = (
        "Amazon Prime Student は、お金を節約したい学生のためのお得な選択肢です。"
        "送料無料が最大の節約になり、無料 2 日間配送は時間の節約にもなります。"
        "通常のプライム会員の半額でストリーミングや書籍も楽しめます。"
        "大学生活をより快適にする多くのサービスを提供しています。"
    )

    print("=" * 60)
    print(" プロンプトテンプレートの再利用")
    print("=" * 60)

    # 同じテンプレートを、異なる長さ指定で再利用する
    for length in ["1 文", "3 つの箇条書き"]:
        prompt = SUMMARY_TEMPLATE.format(
            category="サービスレビュー", text=review, length=length
        )
        print(f"\n--- length = '{length}' ---")
        print(ask(bedrock_runtime, prompt))

    print("\nポイント:")
    print("  - テンプレート化により、length や category を差し替えるだけで")
    print("    同じ品質の要約を量産できます（一貫性・再利用性）。")
    print("  - 本番では Amazon Bedrock プロンプト管理でバージョン管理できます。")


if __name__ == "__main__":
    main()
