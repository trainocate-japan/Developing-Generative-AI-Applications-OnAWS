"""
モジュール 7: 優先順位に基づくモデル選択（コスト/品質/速度）
------------------------------------------------------------
同じプロンプトを複数モデルに投げ、レイテンシー・出力トークン数を実測して比較します。
「速度」「コスト（トークン量の代理指標）」「品質（目視/別モデル評価）」の
トレードオフを体感し、ユースケースに合ったモデルを選ぶ判断材料にします。

実行:
    python model_selection.py
"""

import time
import boto3
from botocore.config import Config

REGION = "us-east-1"

CANDIDATES = {
    "Nova Lite": "us.amazon.nova-lite-v1:0",
    "Nova Pro": "us.amazon.nova-pro-v1:0",
    "Claude Sonnet 4.5": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
}

PROMPT = "RAG（検索拡張生成）とは何かを、3 文で分かりやすく説明してください。"


def main():
    br = boto3.client(
        "bedrock-runtime",
        region_name=REGION,
        config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
    )

    print("=" * 70)
    print(" モデル比較: 速度 / トークン量 / 出力")
    print("=" * 70)

    results = []
    for label, model_id in CANDIDATES.items():
        try:
            start = time.time()
            resp = br.converse(
                modelId=model_id,
                messages=[{"role": "user", "content": [{"text": PROMPT}]}],
                inferenceConfig={"maxTokens": 300, "temperature": 0.3},
            )
            elapsed = time.time() - start
            usage = resp["usage"]
            text = resp["output"]["message"]["content"][0]["text"].strip()
            results.append((label, elapsed, usage["outputTokens"], text))
        except Exception as e:
            results.append((label, None, None, f"呼び出し失敗: {e}"))

    for label, elapsed, out_tokens, text in results:
        print(f"\n--- {label} ---")
        if elapsed is not None:
            print(f"  レイテンシー: {elapsed:.2f} 秒 / 出力トークン: {out_tokens}")
        print(f"  出力: {text[:200]}")

    print("\n" + "=" * 70)
    print(" まとめ表")
    print("=" * 70)
    print(f"  {'モデル':22s} {'速度(秒)':>10s} {'出力トークン':>12s}")
    for label, elapsed, out_tokens, _ in results:
        e = f"{elapsed:.2f}" if elapsed is not None else "N/A"
        t = str(out_tokens) if out_tokens is not None else "N/A"
        print(f"  {label:22s} {e:>10s} {t:>12s}")

    print("\nポイント:")
    print("  - 単純なタスクは軽量モデル（Nova Lite）で十分なことが多い。")
    print("  - コスト優先か品質優先かで、選ぶモデルが変わる。")
    print("  - 本番では『簡単な候補リスト → ベンチマーク → 優先順位で選択』の順で決める。")


if __name__ == "__main__":
    main()
