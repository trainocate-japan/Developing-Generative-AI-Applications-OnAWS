"""
モジュール 2: Converse API（モデル非依存の統一インターフェイス）
------------------------------------------------------------
Converse API は、すべてのモデルで共通のリクエスト/レスポンス構造を提供します。
modelId を変えるだけでモデルを切り替えられるのが最大の利点です。

  - system: システムプロンプト（役割・行動ガイドライン）
  - messages: 会話のやり取り
  - inferenceConfig: maxTokens / temperature / topP / stopSequences（共通）
    ※ Claude 4.5 など一部モデルは temperature と topP の同時指定不可。片方に絞る。

実行:
    python converse_api.py
"""

import boto3
from botocore.config import Config

REGION = "us-east-1"

# modelId を変えるだけでモデルを切り替えられる（ボディ形式の変更は不要）
MODELS = {
    "Nova Lite": "us.amazon.nova-lite-v1:0",
    "Claude Sonnet 4.5": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
}


def converse(bedrock_runtime, model_id: str, prompt: str) -> dict:
    return bedrock_runtime.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        system=[
            {
                "text": (
                    "あなたは Python に精通したアプリケーションデベロッパーです。"
                    "コーディングに関するトピックのみに会話を限定してください。"
                )
            }
        ],
        # 注: 一部のモデル（Claude 4.5 など）は temperature と topP の
        # 同時指定を許容しません。ここでは温度のみを指定して両モデルで動作させます。
        inferenceConfig={"maxTokens": 400, "temperature": 0.7},
    )


def main():
    bedrock_runtime = boto3.client(
        "bedrock-runtime",
        region_name=REGION,
        config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
    )

    prompt = "画像サイズを変更するスクリプトを作成してください。"

    print("=" * 60)
    print(" Converse API - 同じコードで複数モデルを呼び出す")
    print("=" * 60)

    for label, model_id in MODELS.items():
        print(f"\n{'-' * 60}\nモデル: {label} ({model_id})\n{'-' * 60}")
        try:
            resp = converse(bedrock_runtime, model_id, prompt)
            text = resp["output"]["message"]["content"][0]["text"]
            usage = resp["usage"]
            print(text[:600])
            print(
                f"\n[usage] input={usage['inputTokens']} "
                f"output={usage['outputTokens']} total={usage['totalTokens']}"
            )
        except Exception as e:
            print(f"呼び出し失敗: {e}")

    print("\nポイント: modelId を変えるだけで、同じコードが動きます。")


if __name__ == "__main__":
    main()
