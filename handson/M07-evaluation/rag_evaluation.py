"""
モジュール 7: Ragas による RAG 評価
------------------------------------------------------------
evaluation-dataset.jsonl（質問・検索コンテキスト・応答・リファレンス）を読み込み、
Ragas のメトリクスで RAG の品質を評価します。評価者 LLM / 埋め込みには Bedrock を使います。

  - Faithfulness（忠実度）        : 応答がコンテキストに忠実か（ハルシネーション検出）
  - ResponseRelevancy（応答の関連性）: 応答が質問に関連しているか
  - LLMContextPrecisionWithReference（コンテキスト適合率）: 検索が適切か

実行:
    python rag_evaluation.py
"""

import json
import os

DATASET_PATH = os.path.join(os.path.dirname(__file__), "evaluation-dataset.jsonl")
REGION = "us-east-1"
EVAL_MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
EMBED_MODEL_ID = "amazon.titan-embed-text-v2:0"


def load_dataset(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main():
    print("=" * 60)
    print(" Ragas による RAG 評価")
    print("=" * 60)

    samples = load_dataset(DATASET_PATH)
    print(f"\n評価サンプル数: {len(samples)}")

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
    except ImportError as e:
        print(f"\n必要なパッケージが見つかりません: {e}")
        print("pip install 'ragas>=0.2' datasets langchain-aws を実行してください。")
        return

    # 評価者 LLM と 埋め込み（Bedrock を Ragas でラップ）
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

    print("\n評価を実行中...（Bedrock を複数回呼び出すため数十秒かかります）\n")
    result = evaluate(dataset=dataset, metrics=metrics)

    print("=" * 60)
    print(" 評価結果（スコアは 0.0〜1.0、高いほど良い）")
    print("=" * 60)
    print(result)

    print("\nポイント:")
    print("  - 忠実度が低い → 応答がコンテキストにない情報を含む（ハルシネーション）")
    print("  - 応答の関連性が低い → 質問に的確に答えていない")
    print("  - コンテキスト適合率が低い → 検索（Retrieve）の改善が必要")


if __name__ == "__main__":
    main()
