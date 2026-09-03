"""
モジュール 7: レイテンシーとコストの最適化（プロンプトキャッシュ）
------------------------------------------------------------
Converse API の cachePoint を使い、繰り返し使う大きなコンテキスト（システムプロンプト）を
キャッシュします。2 回目以降の呼び出しでキャッシュがヒットすると、レイテンシーと
コストが削減されます（cacheReadInputTokens が増える）。

注意:
  - プロンプトキャッシュ対応モデルと最小トークン閾値があります（モデルにより異なる）。
  - キャッシュ TTL は既定 5 分。同一内容・同一 cachePoint 位置で再送する必要があります。

実行:
    python latency_cost_optimization.py
"""

import time
import boto3
from botocore.config import Config

REGION = "us-east-1"
# プロンプトキャッシュ対応モデル（Claude 系）を使用
MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

# キャッシュ対象にする大きめのシステムプロンプト（閾値を満たすよう十分な長さにする）
LARGE_CONTEXT = (
    "あなたは AnyCompany Cloud のサポートアシスタントです。以下の製品仕様に基づいて回答します。\n"
    + ("AnyCompany Cloud はマネージドアプリケーションプラットフォームです。"
       "Web アプリのホスティング、データベース、オブジェクトストレージ、認証機能を提供します。"
       "プランは Starter（月額2000円）、Business（月額8000円）、Enterprise（月額30000円から）。"
       "バックアップ保持は Starter 7日、Business 30日、Enterprise 90日。"
       "セキュリティは全プランで TLS1.3 と AES-256。Business 以上で MFA と IP 制限。"
       "Enterprise で SSO と監査ログ。リージョンは東京・大阪・シンガポール・バージニア。\n") * 40
)


def ask(br, question: str):
    resp = br.converse(
        modelId=MODEL_ID,
        system=[
            {"text": LARGE_CONTEXT},
            {"cachePoint": {"type": "default"}},   # ここまでをキャッシュ対象にする
        ],
        messages=[{"role": "user", "content": [{"text": question}]}],
        inferenceConfig={"maxTokens": 200, "temperature": 0.2},
    )
    usage = resp["usage"]
    text = resp["output"]["message"]["content"][0]["text"].strip()
    return text, usage


def main():
    br = boto3.client(
        "bedrock-runtime",
        region_name=REGION,
        config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
    )

    print("=" * 60)
    print(" プロンプトキャッシュのデモ")
    print("=" * 60)

    questions = [
        "Enterprise プランのバックアップ保持期間は？",
        "MFA はどのプランから使えますか？",
    ]

    for i, q in enumerate(questions, 1):
        print(f"\n--- 呼び出し {i}: {q} ---")
        start = time.time()
        text, usage = ask(br, q)
        elapsed = time.time() - start
        print(f"  回答: {text[:120]}")
        print(f"  レイテンシー: {elapsed:.2f} 秒")
        # キャッシュ関連トークン（キーが無いモデル/未ヒット時は 0 や欠落）
        print(
            f"  input={usage.get('inputTokens')} "
            f"cacheWrite={usage.get('cacheWriteInputTokens', 0)} "
            f"cacheRead={usage.get('cacheReadInputTokens', 0)}"
        )

    print("\nポイント:")
    print("  - 1 回目で cacheWrite が発生し、2 回目で cacheRead が増えるのが理想。")
    print("  - 大きな共通コンテキスト（製品仕様・長い手順）を持つ用途で効果的。")
    print("  - cacheRead が 0 のままなら: 対応モデルか / トークン閾値を満たすか /")
    print("    cachePoint 位置と内容が一致しているか / TTL(5分)内かを確認。")
    print("\n他の最適化手法:")
    print("  - Intelligent Prompt Routing: 応答品質を予測して安価なモデルへ動的ルーティング")
    print("  - レイテンシー最適化推論: performanceConfig={'latency':'optimized'} で TTFT を短縮")


if __name__ == "__main__":
    main()
