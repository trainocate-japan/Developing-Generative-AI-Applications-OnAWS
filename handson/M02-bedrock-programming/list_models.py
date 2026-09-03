"""
モジュール 2: 基盤モデルの一覧表示（コントロールプレーン）
------------------------------------------------------------
bedrock（コントロールプレーン）クライアントの ListFoundationModels で
利用可能なモデルを一覧表示します。データプレーン（推論）とは別 API である
ことを確認します。

実行:
    python list_models.py
"""

import boto3
from botocore.config import Config

REGION = "us-east-1"


def main():
    # コントロールプレーン: モデルの一覧・管理に使う（推論はしない）
    bedrock = boto3.client(
        "bedrock",
        region_name=REGION,
        config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
    )

    response = bedrock.list_foundation_models()
    models = response.get("modelSummaries", [])

    print("=" * 60)
    print(f" 利用可能な基盤モデル: {len(models)} 件（リージョン: {REGION}）")
    print("=" * 60)

    # テキスト出力に対応するモデルだけ表示
    for m in models:
        if "TEXT" in m.get("outputModalities", []):
            print(f"  {m['modelId']:55s} [{m.get('providerName')}]")

    print("\nヒント: 実際の推論には推論プロファイル ID（us. プレフィックス）を推奨:")
    print("  aws bedrock list-inference-profiles --region", REGION)


if __name__ == "__main__":
    main()
