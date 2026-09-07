"""
モジュール 7: RAG 評価（忠実度・応答の関連性・コンテキスト適合率）
------------------------------------------------------------
evaluation-dataset.jsonl（質問・検索コンテキスト・応答・リファレンス）を読み込み、
RAG の品質を 3 つのメトリクスで評価します。

  - Faithfulness（忠実度）        : 応答がコンテキストに忠実か（ハルシネーション検出）
  - ResponseRelevancy（応答の関連性）: 応答が質問に関連しているか
  - ContextPrecision（コンテキスト適合率）: 検索コンテキストがリファレンスに適合するか

評価には Amazon Bedrock を「評価者 LLM（LLM-as-a-Judge）」および埋め込みモデルとして使います。

補足:
  Ragas（RAG 評価フレームワーク）が利用可能な環境では Ragas を使います。
  ただし ragas 0.4.x は langchain-community の一部バージョンと非互換で import に
  失敗することがあるため、その場合は Bedrock ベースの自前実装に自動フォールバックします。
  どちらも「各メトリクスが何を測るか」を学ぶという目的は同じです。

実行:
    python rag_evaluation.py
"""

import json
import os
import re

import boto3
from botocore.config import Config

DATASET_PATH = os.path.join(os.path.dirname(__file__), "evaluation-dataset.jsonl")
REGION = "us-east-1"
EVAL_MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
EMBED_MODEL_ID = "amazon.titan-embed-text-v2:0"


def load_dataset(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# =============================================================================
# 経路 A: Ragas が使える場合（import 成功時）
# =============================================================================
def try_ragas(samples):
    try:
        from ragas import EvaluationDataset, evaluate
        from ragas.metrics import (
            Faithfulness,
            ResponseRelevancy,
            LLMContextPrecisionWithReference,
        )
        from ragas.llms import LangchainLLMWrapper
        from ragas.embeddings import LangchainEmbeddingsWrapper
        from langchain_aws import ChatBedrockConverse, BedrockEmbeddings
    except Exception as e:  # ImportError や依存の破損を含む
        print(f"[info] Ragas を利用できないため自前実装にフォールバックします: {type(e).__name__}")
        return False

    evaluator_llm = LangchainLLMWrapper(
        ChatBedrockConverse(model=EVAL_MODEL_ID, region_name=REGION, max_tokens=1024, temperature=0)
    )
    evaluator_embeddings = LangchainEmbeddingsWrapper(
        BedrockEmbeddings(model_id=EMBED_MODEL_ID, region_name=REGION)
    )
    dataset = EvaluationDataset.from_list(samples)
    metrics = [
        Faithfulness(llm=evaluator_llm),
        ResponseRelevancy(llm=evaluator_llm, embeddings=evaluator_embeddings),
        LLMContextPrecisionWithReference(llm=evaluator_llm),
    ]
    print("\n[Ragas] 評価を実行中...（Bedrock を複数回呼び出すため数十秒かかります）\n")
    result = evaluate(dataset=dataset, metrics=metrics)
    print("=" * 60)
    print(" 評価結果（Ragas / スコアは 0.0〜1.0、高いほど良い）")
    print("=" * 60)
    print(result)
    return True


# =============================================================================
# 経路 B: Bedrock ベースの自前実装（LLM-as-a-Judge + 埋め込み類似度）
# =============================================================================
def judge_score(br, instruction: str) -> float:
    """評価者 LLM に 0.0〜1.0 のスコアだけを返させる"""
    resp = br.converse(
        modelId=EVAL_MODEL_ID,
        messages=[{"role": "user", "content": [{"text": instruction}]}],
        system=[{"text": "あなたは厳密な評価者です。指示に従い、0.0〜1.0 の数値のみを返してください。"}],
        inferenceConfig={"maxTokens": 10, "temperature": 0},
    )
    text = resp["output"]["message"]["content"][0]["text"].strip()
    m = re.search(r"[01](?:\.\d+)?", text)
    return float(m.group()) if m else 0.0


def faithfulness(br, contexts, response):
    ctx = "\n".join(contexts)
    return judge_score(
        br,
        f"次の応答が、与えられたコンテキストだけで裏付けられている度合いを 0.0〜1.0 で採点してください。"
        f"コンテキストにない情報が含まれるほど低くします。\n\n"
        f"# コンテキスト\n{ctx}\n\n# 応答\n{response}\n\nスコア:",
    )


def context_precision(br, contexts, reference):
    ctx = "\n".join(contexts)
    return judge_score(
        br,
        f"次の検索コンテキストが、リファレンス回答に関連・適合している度合いを 0.0〜1.0 で採点してください。\n\n"
        f"# 検索コンテキスト\n{ctx}\n\n# リファレンス\n{reference}\n\nスコア:",
    )


def embed(br, text: str):
    resp = br.invoke_model(
        modelId=EMBED_MODEL_ID,
        body=json.dumps({"inputText": text}),
    )
    return json.loads(resp["body"].read())["embedding"]


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    return dot / (na * nb) if na and nb else 0.0


def response_relevancy(br, user_input, response):
    """応答と質問の埋め込みコサイン類似度で関連性を近似する"""
    return max(0.0, cosine(embed(br, user_input), embed(br, response)))


def run_custom(samples):
    br = boto3.client(
        "bedrock-runtime",
        region_name=REGION,
        config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
    )
    print("\n[自前実装] Bedrock を評価者 LLM / 埋め込みとして評価中...\n")

    rows = []
    for i, s in enumerate(samples, 1):
        f = faithfulness(br, s["retrieved_contexts"], s["response"])
        r = response_relevancy(br, s["user_input"], s["response"])
        c = context_precision(br, s["retrieved_contexts"], s["reference"])
        rows.append((f, r, c))
        print(f"  [{i}] {s['user_input'][:30]}...")
        print(f"       忠実度={f:.2f}  応答の関連性={r:.2f}  コンテキスト適合率={c:.2f}")

    n = len(rows)
    print("\n" + "=" * 60)
    print(" 平均スコア（0.0〜1.0、高いほど良い）")
    print("=" * 60)
    print(f"  Faithfulness（忠実度）        : {sum(x[0] for x in rows)/n:.3f}")
    print(f"  ResponseRelevancy（応答の関連性）: {sum(x[1] for x in rows)/n:.3f}")
    print(f"  ContextPrecision（コンテキスト適合率）: {sum(x[2] for x in rows)/n:.3f}")


def main():
    print("=" * 60)
    print(" RAG 評価（忠実度・応答の関連性・コンテキスト適合率）")
    print("=" * 60)

    samples = load_dataset(DATASET_PATH)
    print(f"\n評価サンプル数: {len(samples)}")

    # まず Ragas を試し、使えなければ自前実装にフォールバック
    if not try_ragas(samples):
        run_custom(samples)

    print("\nポイント:")
    print("  - 忠実度が低い → 応答がコンテキストにない情報を含む（ハルシネーション）")
    print("  - 応答の関連性が低い → 質問に的確に答えていない")
    print("  - コンテキスト適合率が低い → 検索（Retrieve）の改善が必要")


if __name__ == "__main__":
    main()
