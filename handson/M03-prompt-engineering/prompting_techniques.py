"""
モジュール 3: 3 つの基本プロンプトテクニック
------------------------------------------------------------
同じタスク（感情分類 / 計算）に対して、ゼロショット・フューショット・
思考の連鎖 (CoT) を適用し、出力の違いを比較します。

実行:
    python prompting_techniques.py
"""

import boto3
from botocore.config import Config

REGION = "us-east-1"
MODEL_ID = "us.amazon.nova-lite-v1:0"


def ask(bedrock_runtime, prompt: str, max_tokens: int = 400) -> str:
    resp = bedrock_runtime.converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": max_tokens, "temperature": 0.2, "topP": 0.9},
    )
    return resp["output"]["message"]["content"][0]["text"].strip()


def main():
    bedrock_runtime = boto3.client(
        "bedrock-runtime",
        region_name=REGION,
        config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
    )

    # 1. ゼロショット
    print("=" * 60)
    print(" 1. ゼロショット（例を挙げずに指示）")
    print("=" * 60)
    zero_shot = (
        "次のソーシャルメディア投稿の印象を、ポジティブ・ネガティブ・ニュートラルの"
        "いずれかで分類してください。\n\n"
        "投稿: 電気自動車の革命をお見逃しなく。AnyCompany は EV に移行中で、投資家に"
        "とって大きなチャンスです。"
    )
    print(ask(bedrock_runtime, zero_shot, 60))

    # 2. フューショット
    print("\n" + "=" * 60)
    print(" 2. フューショット（入出力例を提示して形式を揃える）")
    print("=" * 60)
    few_shot = (
        "次の見出しの印象を、ポジティブ・ネガティブ・ニュートラルで分類してください。\n\n"
        "見出し: 研究会社は新技術をめぐる不正疑惑を退けている。\n回答: ネガティブ\n\n"
        "見出し: 洋上風力発電所は反対の声が減り、発展しています。\n回答: ポジティブ\n\n"
        "見出し: 製造工場が州当局の調査対象になっている。\n回答:"
    )
    print(ask(bedrock_runtime, few_shot, 60))

    # 3. 思考の連鎖 (CoT)
    print("\n" + "=" * 60)
    print(" 3. 思考の連鎖 (CoT)（中間推論ステップを促す）")
    print("=" * 60)
    cot = (
        "以下の情報から、頭金がより多く必要なのはどちらの車でしょうか。"
        "計算過程を示してから結論を述べてください。\n"
        "車 A: 総額 40,000 USD、頭金 30%\n"
        "車 B: 総額 50,000 USD、頭金 20%"
    )
    print(ask(bedrock_runtime, cot, 300))

    print("\nポイント:")
    print("  - フューショットは出力形式を安定させる（1 単語で返る）。")
    print("  - CoT は計算・多段推論の正確性を高める。")


if __name__ == "__main__":
    main()
