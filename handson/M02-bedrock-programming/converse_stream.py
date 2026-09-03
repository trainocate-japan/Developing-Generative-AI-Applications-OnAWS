"""
モジュール 2: ConverseStream（ストリーミング応答）
------------------------------------------------------------
ConverseStream は、生成されたトークンを逐次受信できます。
チャット UI のように「入力しながら表示」したい場合や、最初のトークンまでの
レイテンシー (TTFT) を短くしたい場合に有効です。

注意: AWS CLI はストリーミングに非対応です。SDK（boto3 の converse_stream）を
使う必要があります。

実行:
    python converse_stream.py
"""

import sys
import boto3
from botocore.config import Config

REGION = "us-east-1"
MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"


def main():
    bedrock_runtime = boto3.client(
        "bedrock-runtime",
        region_name=REGION,
        config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
    )

    prompt = "リストを昇順にソートする Python 関数を、説明付きで書いてください。"

    print("=" * 60)
    print(" ConverseStream - トークンを逐次表示")
    print("=" * 60)
    print(f"\nプロンプト: {prompt}\n")
    print("-" * 60)

    response = bedrock_runtime.converse_stream(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 500, "temperature": 0.7},
    )

    # ストリームからチャンクを読み取り、テキスト部分だけ逐次出力する
    for event in response["stream"]:
        if "contentBlockDelta" in event:
            delta = event["contentBlockDelta"]["delta"]
            if "text" in delta:
                sys.stdout.write(delta["text"])
                sys.stdout.flush()
        elif "metadata" in event:
            usage = event["metadata"].get("usage", {})
            print("\n" + "-" * 60)
            print(
                f"[usage] input={usage.get('inputTokens')} "
                f"output={usage.get('outputTokens')} total={usage.get('totalTokens')}"
            )

    print("\nポイント: 逐次表示によりユーザーの体感レイテンシーが向上します。")


if __name__ == "__main__":
    main()
