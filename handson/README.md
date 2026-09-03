# Developing Generative AI Applications on AWS - ハンズオンガイド

## コース概要

このハンズオンガイドは「Developing Generative AI Applications on AWS（日本語）」研修コースの
各モジュール（モジュール 1 〜 モジュール 10）に対応した、実践的なシナリオと手順を提供します。
スライドで学んだ概念を、実際に手を動かして確認することで理解を深めることを目的としています。

各モジュールのフォルダには次の 3 種類のファイルがあります。

- `scenario.md` … 業務シナリオ・学習目標・アーキテクチャ・所要時間
- `steps.md` … コンソール操作とスクリプト実行を含むハンズオン手順
- `*.py` … デモ用の Python スクリプト（Amazon Bedrock を呼び出します）

## モジュール一覧

| モジュール | テーマ | フォルダ | 目安時間 |
|-----------|--------|---------|---------|
| M01 | AWS 上の生成 AI アプリケーションのコンポーネント | `M01-components` | 40分 |
| M02 | Amazon Bedrock でのプログラミング（推論パラメータ・InvokeModel・Converse） | `M02-bedrock-programming` | 45分 |
| M03 | デベロッパー向けプロンプトエンジニアリングの応用 | `M03-prompt-engineering` | 40分 |
| M04 | 一般的なアーキテクチャでの Amazon Bedrock API の使用（会話メモリ） | `M04-architecture-patterns` | 45分 |
| M05 | RAG による生成 AI レスポンスのカスタマイズ（Knowledge Bases） | `M05-rag-knowledge-bases` | 60分 |
| M06 | オープンソースフレームワーク（LangChain）と Amazon Bedrock の統合 | `M06-langchain` | 40分 |
| M07 | 生成 AI アプリケーションコンポーネントの評価（Ragas・コスト最適化） | `M07-evaluation` | 45分 |
| M08 | 責任ある AI の実装（Amazon Bedrock Guardrails） | `M08-responsible-ai` | 45分 |
| M09 | 生成 AI アプリケーションにおけるツールとエージェント（Strands・MCP・A2A） | `M09-tools-agents` | 45分 |
| M10 | Amazon Bedrock エージェントの開発（Flows・Agents・AgentCore） | `M10-bedrock-agents` | 60分 |

## 前提条件

### 環境要件

- AWS アカウント（管理者アクセス）
- AWS CLI v2 設定済み
- Python 3.12+（EC2 環境では venv が自動で有効化されます）
- Amazon Bedrock モデルアクセス有効化済み
  - Amazon Nova Lite / Pro / Micro
  - Amazon Titan Text Embeddings V2（M05 で使用）
  - Anthropic Claude Sonnet 4.5

### 使用するモデル ID（クロスリージョン推論プロファイル）

本ハンズオンでは、可用性とスループットの高い**クロスリージョン推論プロファイル**（`us.` プレフィックス）を使用します。

| 用途 | モデル ID |
|------|-----------|
| 軽量・低コスト | `us.amazon.nova-lite-v1:0` |
| バランス型 | `us.amazon.nova-pro-v1:0` |
| 高品質（Claude） | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` |
| 埋め込み（RAG） | `amazon.titan-embed-text-v2:0` |

> 実行前に `aws bedrock list-foundation-models --region <region>` で利用可能なモデルを確認できます。
> リージョンは `us-east-1`（バージニア北部）または `us-west-2`（オレゴン）を推奨します。

### Python パッケージ

EC2 デモ環境には以下がプリインストールされています（`infra/demo-ec2.yaml` 参照）。

- `boto3`, `requests`, `numpy`
- `langchain`, `langchain-aws`, `langchain-community`（M06 / M07）
- `ragas`, `datasets`（M07）
- `strands-agents`, `strands-agents-tools`（M09）
- `bedrock-agentcore`, `bedrock-agentcore-starter-toolkit`（M10）

ローカルで実行する場合は以下でインストールできます。

```bash
pip install boto3 requests numpy langchain langchain-aws langchain-community "ragas>=0.2" datasets strands-agents strands-agents-tools
```

## フォルダ構造

```
handson/
├── README.md                       # このファイル
├── cleanup_all.sh                  # 全リソース一括削除スクリプト
├── M01-components/
│   ├── scenario.md
│   ├── steps.md
│   ├── genai_stack_explorer.py     # AWS 生成 AI スタックの確認
│   └── basic_app_architecture.py   # 基本的な生成 AI アプリの最小実装
├── M02-bedrock-programming/
│   ├── scenario.md
│   ├── steps.md
│   ├── list_models.py              # 基盤モデルの一覧表示
│   ├── invoke_model.py             # InvokeModel（プロバイダー固有ボディ）
│   ├── converse_api.py             # Converse API（統一インターフェイス）
│   ├── converse_stream.py          # ConverseStream（ストリーミング）
│   └── inference_parameters.py     # 推論パラメータの比較
├── M03-prompt-engineering/
│   ├── scenario.md
│   ├── steps.md
│   ├── prompting_techniques.py     # Zero-shot / Few-shot / CoT
│   ├── prompt_template.py          # プロンプトテンプレート
│   └── query_decomposition.py      # クエリの分解
├── M04-architecture-patterns/
│   ├── scenario.md
│   ├── steps.md
│   ├── architecture_patterns.py    # 生成/要約/QA/会話パターン
│   ├── batch_vs_ondemand.py        # 推論モードの比較
│   └── conversation_memory.py      # 会話メモリの追加
├── M05-rag-knowledge-bases/
│   ├── scenario.md
│   ├── steps.md
│   ├── retrieve_and_generate.py    # RetrieveAndGenerate API
│   ├── retrieve_only.py            # Retrieve API + 手動生成
│   └── sample-docs/                # KB 用サンプルドキュメント
├── M06-langchain/
│   ├── scenario.md
│   ├── steps.md
│   ├── langchain_basics.py         # ChatBedrockConverse の基本
│   ├── langchain_chain.py          # プロンプト | モデル チェーン
│   └── langchain_memory.py         # DynamoDB 会話履歴
├── M07-evaluation/
│   ├── scenario.md
│   ├── steps.md
│   ├── model_selection.py          # コスト/品質/速度でのモデル選択
│   ├── rag_evaluation.py           # Ragas による RAG 評価
│   ├── latency_cost_optimization.py# プロンプトキャッシュ/レイテンシー最適化
│   └── evaluation-dataset.jsonl    # 評価データセット
├── M08-responsible-ai/
│   ├── scenario.md
│   ├── steps.md
│   ├── create_guardrail.py         # Guardrail の作成
│   ├── test_guardrail.py           # Guardrail のテスト（ApplyGuardrail）
│   └── prompt_injection_demo.py    # プロンプトインジェクション対策
├── M09-tools-agents/
│   ├── scenario.md
│   ├── steps.md
│   ├── tool_use_converse.py        # Converse API のツール使用（関数呼び出し）
│   ├── strands_agent.py            # Strands Agents の基本
│   ├── mcp_server_demo.py          # MCP サーバー（デモ用）
│   └── mcp_client_demo.py          # MCP クライアントデモ
└── M10-bedrock-agents/
    ├── scenario.md
    ├── steps.md
    ├── create_flow.py              # Amazon Bedrock Flows
    ├── agentcore_runtime_agent.py  # AgentCore Runtime 用エージェント
    └── requirements.txt            # AgentCore デプロイ用
```

## 使い方

1. 各モジュールフォルダ内の `scenario.md` でシナリオと学習目標を確認します。
2. `steps.md` の手順に従ってハンズオンを実施します。
3. Python スクリプトがある場合は実行してデモ動作を確認します。
4. 終了後は下記クリーンアップ手順に従ってリソースを削除します。

## クリーンアップ

一部のモジュール（M05 の Knowledge Base、M08 の Guardrail、M04/M06 の DynamoDB、M10 の Agent など）は
AWS リソースを作成します。研修終了後は以下で一括削除できます。

```bash
cd ~/handson
bash cleanup_all.sh
```

### 対象リソース一覧

| モジュール | 削除対象 |
|-----------|---------|
| M04 / M06 | DynamoDB テーブル（会話履歴） |
| M05 | Bedrock Knowledge Base、データソース、（任意で）OpenSearch Serverless |
| M07 | ローカル実行のみ（削除対象なし） |
| M08 | Bedrock Guardrail |
| M10 | Bedrock Flow、AgentCore Runtime |

> スクリプトは冪等です（リソースが存在しなければスキップします）。
> 実行前に `aws sts get-caller-identity` で正しいアカウントか確認してください。

## コスト管理

- 各ハンズオンの推定コスト: $1〜$5
- Bedrock のモデル呼び出しコストが主な費用です（Nova Lite は特に安価）
- M05 の OpenSearch Serverless は起動中は課金されるため、使用後は必ず削除してください

## トラブルシューティング

### モデルアクセスエラー

```
AccessDeniedException: You don't have access to the model ...
```

→ AWS コンソール → Bedrock → Model access で該当モデルを有効化してください。

### ThrottlingException

→ `maxTokens` を明示的に指定しているか確認してください（未指定だとモデル最大値が予約され、
スロットリングの原因になります）。本ハンズオンのスクリプトはすべて `maxTokens` を明示しています。
また `us.` プレフィックスのクロスリージョン推論プロファイルを使用すると分散され改善します。

### On-demand throughput isn't supported

```
Invocation of model ID ... with on-demand throughput isn't supported.
Retry your request with the ID or ARN of an inference profile ...
```

→ ベースモデル ID ではなく推論プロファイル ID（例: `us.amazon.nova-lite-v1:0`）を使用してください。

### リージョン未対応

→ `us-east-1` または `us-west-2` に変更してください。
