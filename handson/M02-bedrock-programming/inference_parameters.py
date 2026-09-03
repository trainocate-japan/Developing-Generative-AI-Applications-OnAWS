"""
モジュール 2: 推論パラメータの比較
------------------------------------------------------------
同じプロンプトに対して temperature を変えて複数回呼び出し、
出力の「決定性」と「多様性」がどう変わるかを比較します。

  - temperature 低（0.0〜0.3）: 事実に基づく・再現性の高い応答
  - temperature 高（0.8〜1.0）: 創造的・多様な応答
  - stopSequences: 指定文字列で生成を停止

実行:
    python inference_parameters.py
"""

import boto3
from botocore.config import Config

REGION = "us-east-1"
MODEL_ID = "us.amazon.nova-lite-v1:0"


def run(bedrock_runtime, prompt: str, temperature: float, stop=None) -> str:
    inference_config = {"maxTokens": 120, "temperature": temperature, "topP": 0.9}
    if stop:
        inference_config["stopSequences"] = stop
    resp = bedrock_runtime.converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig=inference_config,
    )
    return resp["output"]["message"]["content"][0]["text"].strip()


def main():
    bedrock_runtime = boto3.client(
        "bedrock-runtime",
        region_name=REGION,
        config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
    )

    print("=" * 60)
    print(" 推論パラメータの比較: temperature")
    print("=" * 60)

    prompt = "新しいコーヒーショップのキャッチコピーを 1 つ考えてください。"

    for temp in [0.0, 0.5, 1.0]:
        print(f"\n--- temperature = {temp} を 2 回実行 ---")
        for i in range(2):
            out = run(bedrock_runtime, prompt, temp)
            print(f"  [{i + 1}] {out}")

    # stopSequences のデモ
    print("\n" + "=" * 60)
    print(" stopSequences のデモ（'3.' で生成を停止）")
    print("=" * 60)
    list_prompt = "Python を学ぶメリットを箇条書きで 5 つ挙げてください。"
    out = run(bedrock_runtime, list_prompt, 0.3, stop=["3."])
    print(out)

    print("\nポイント:")
    print("  - temperature=0 は毎回ほぼ同じ（決定的）、1.0 は毎回異なる（多様）。")
    print("  - コーディングアシスタントのような正確性重視の用途では低め、")
    print("    創作用途では高めが適しています。")
    print("  - stopSequences で出力の途中終了を制御できます。")


if __name__ == "__main__":
    main()
