"""
モジュール 4: 推論モードの比較（オンデマンドの実測 + モード解説）
------------------------------------------------------------
オンデマンド推論を実際に呼び出してレイテンシーとトークン使用量を計測し、
バッチ / プロビジョンドスループットとの違いを整理します。

（バッチ推論は S3 入出力と時間を要するため、ここでは概念のみ扱います）

実行:
    python batch_vs_ondemand.py
"""

import time
import boto3
from botocore.config import Config

REGION = "us-east-1"
MODEL_ID = "us.amazon.nova-lite-v1:0"


def main():
    br = boto3.client(
        "bedrock-runtime",
        region_name=REGION,
        config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
    )

    print("=" * 60)
    print(" オンデマンド推論の計測")
    print("=" * 60)

    prompt = "AWS の生成 AI サービスを 3 つ挙げてください。"
    start = time.time()
    resp = br.converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 200, "temperature": 0.3},
    )
    elapsed = time.time() - start

    text = resp["output"]["message"]["content"][0]["text"].strip()
    usage = resp["usage"]

    print(f"\n応答:\n{text}")
    print(f"\nレイテンシー: {elapsed:.2f} 秒")
    print(
        f"トークン: input={usage['inputTokens']} "
        f"output={usage['outputTokens']} total={usage['totalTokens']}"
    )

    # オンデマンド料金の概算式（実際の単価はモデル・リージョンで異なる）
    print("\nオンデマンド料金の考え方:")
    print("  料金 = (入力トークン数 × 入力単価) + (出力トークン数 × 出力単価)")

    print("\n" + "=" * 60)
    print(" 推論モードの比較")
    print("=" * 60)
    print(
        "  オンデマンド        : 低レイテンシー / リクエスト課金 / チャット・RAG 向き\n"
        "  バッチ              : 高レイテンシー / 低コスト / レポート・分析向き\n"
        "                        （S3 に入力を置き CreateModelInvocationJob で実行）\n"
        "  プロビジョンド       : 低レイテンシー / モデルユニット購入 / 大規模・一貫負荷向き"
    )


if __name__ == "__main__":
    main()
