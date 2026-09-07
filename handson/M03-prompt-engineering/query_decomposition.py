"""
モジュール 3: クエリの分解
------------------------------------------------------------
複雑な 1 つの要求を、論理的なサブタスクに分割して順番に処理し、
最後に結果を統合します。明瞭性・精度・複雑性管理の面で有利です。

例: 「メール検証と適切なエラー処理でユーザー登録を処理する REST API を作成」
    -> データモデル -> エンドポイント -> 検証 -> エラー処理 -> 統合

実行:
    python query_decomposition.py
"""

import boto3
from botocore.config import Config

REGION = "us-east-1"
MODEL_ID = "us.amazon.nova-lite-v1:0"


def ask(bedrock_runtime, prompt: str, prior: str = "") -> str:
    full = (prior + "\n\n" + prompt) if prior else prompt
    resp = bedrock_runtime.converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": full}]}],
        inferenceConfig={"maxTokens": 500, "temperature": 0.2},
    )
    return resp["output"]["message"]["content"][0]["text"].strip()


def main():
    bedrock_runtime = boto3.client(
        "bedrock-runtime",
        region_name=REGION,
        config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
    )

    print("=" * 60)
    print(" クエリの分解: ユーザー登録 REST API")
    print("=" * 60)

    steps = [
        ("ステップ1: データモデル設計",
         "username, email, password, verification_status を含むユーザー登録モデルの "
         "JSON スキーマを設計してください。JSON のみ出力してください。"),
        ("ステップ2: エンドポイント構造",
         "上のモデルを受け取る Flask の '/register' POST エンドポイントの雛形を書いてください。"),
        ("ステップ3: メール検証ロジック",
         "登録関数に、検証トークンの生成と検証メール送信の処理を追加する方針を簡潔に示してください。"),
    ]

    prior = ""
    for title, prompt in steps:
        print(f"\n--- {title} ---")
        answer = ask(bedrock_runtime, prompt, prior)
        print(answer[:500])
        # 前ステップの出力を次のコンテキストに引き継ぐ
        prior = f"これまでの成果物:\n{answer}"

    print("\nポイント:")
    print("  - 複雑な要求を分割すると、各ステップの精度と可読性が上がります。")
    print("  - 前段の出力を次段のコンテキストに渡すことで一貫性を保てます。")


if __name__ == "__main__":
    main()
