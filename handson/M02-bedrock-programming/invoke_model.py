"""
モジュール 2: InvokeModel（プロバイダー固有のリクエストボディ）
------------------------------------------------------------
InvokeModel は、モデルプロバイダーごとに異なるリクエストボディ形式を
要求します。ここでは Amazon Nova 形式のボディを組み立てて呼び出します。

  - Nova 形式: {"schemaVersion": "messages-v1", "messages": [...], "inferenceConfig": {...}}

Converse API（converse_api.py）と比べると、プロバイダー固有の知識が
必要なことがわかります。基本的には Converse API の使用を推奨します。

実行:
    python invoke_model.py
"""

import json
import boto3
from botocore.config import Config

REGION = "us-east-1"
MODEL_ID = "us.amazon.nova-lite-v1:0"


def main():
    bedrock_runtime = boto3.client(
        "bedrock-runtime",
        region_name=REGION,
        config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
    )

    prompt = "画像サイズを変更する Python スクリプトを書いてください。"

    # Amazon Nova 固有のボディ形式
    body = {
        "schemaVersion": "messages-v1",
        "messages": [{"role": "user", "content": [{"text": prompt}]}],
        "inferenceConfig": {"maxTokens": 512, "temperature": 0.3},
    }

    print("=" * 60)
    print(" InvokeModel（Amazon Nova 形式のボディ）")
    print("=" * 60)
    print(f"\nプロンプト: {prompt}\n")

    response = bedrock_runtime.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(body),
        accept="application/json",
        contentType="application/json",
    )

    response_body = json.loads(response["body"].read())
    # Nova のレスポンス構造から本文を取り出す
    text = response_body["output"]["message"]["content"][0]["text"]

    print("モデルの応答:")
    print(text)

    print("\n" + "-" * 60)
    print("注意: このボディ形式は Amazon Nova 固有です。")
    print("Claude や Llama では別の形式が必要になります。")
    print("モデルを切り替えやすくするには Converse API を使いましょう。")


if __name__ == "__main__":
    main()
