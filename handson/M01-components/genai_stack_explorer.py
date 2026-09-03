"""
モジュール 1: AWS 生成 AI スタックの確認
------------------------------------------------------------
このスクリプトは Amazon Bedrock で利用可能な基盤モデル (FM) を一覧表示し、
「モデルとツール層」に、どのプロバイダーの、どんなモダリティのモデルがあるかを
確認します。生成 AI アプリの中核となる FM の全体像をつかむのが目的です。

実行:
    python genai_stack_explorer.py
"""

import boto3
from botocore.config import Config
from collections import defaultdict

REGION = "us-east-1"


def main():
    # bedrock（コントロールプレーン）クライアント: モデルの一覧・管理に使用
    bedrock = boto3.client(
        "bedrock",
        region_name=REGION,
        config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
    )

    print("=" * 60)
    print(" AWS 生成 AI スタック - モデルとツール層 (Amazon Bedrock)")
    print("=" * 60)

    resp = bedrock.list_foundation_models()
    models = resp.get("modelSummaries", [])
    print(f"\n利用可能な基盤モデル数: {len(models)}\n")

    # プロバイダーごとに集計
    by_provider = defaultdict(list)
    for m in models:
        by_provider[m.get("providerName", "Unknown")].append(m)

    print("--- プロバイダー別のモデル数 ---")
    for provider in sorted(by_provider):
        print(f"  {provider:20s}: {len(by_provider[provider]):3d} モデル")

    # 本ハンズオンで使用する主要モデルの詳細を表示
    print("\n--- 本ハンズオンで使用する主要モデル ---")
    targets = [
        "amazon.nova-lite-v1:0",
        "amazon.nova-pro-v1:0",
        "amazon.titan-embed-text-v2:0",
        "anthropic.claude-sonnet-4-5-20250929-v1:0",
    ]
    for m in models:
        if m["modelId"] in targets:
            in_mod = ",".join(m.get("inputModalities", []))
            out_mod = ",".join(m.get("outputModalities", []))
            stream = "Yes" if m.get("responseStreamingSupported") else "No"
            print(f"\n  ModelId : {m['modelId']}")
            print(f"    Provider   : {m.get('providerName')}")
            print(f"    Input      : {in_mod}")
            print(f"    Output     : {out_mod}")
            print(f"    Streaming  : {stream}")

    print("\n" + "=" * 60)
    print(" ポイント:")
    print("  - Amazon Bedrock は単一の API で複数プロバイダーの FM に")
    print("    アクセスできる『モデルとツール層』のサービスです。")
    print("  - 実際の呼び出しには推論プロファイル ID（us. プレフィックス）を")
    print("    使うと、可用性とスループットが向上します。")
    print("=" * 60)


if __name__ == "__main__":
    main()
