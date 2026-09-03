# モジュール 10: Amazon Bedrock エージェントの開発 - ハンズオンシナリオ

## シナリオ概要

コースの総まとめとして、これまで学んだ要素（モデル呼び出し・プロンプト・RAG・ツール・
ガードレール）を組み合わせ、**エージェント**として動くアプリを構築します。
Amazon Bedrock には、目的に応じて 3 つの構築手段があります。

- **Amazon Bedrock Flows**: ビジュアルビルダーで制御可能なワークフローを構築
- **Amazon Bedrock Agents**: マネージドなエージェント（アクショングループ・KB・メモリ・ガードレール）
- **Amazon Bedrock AgentCore**: 本番規模でエージェントをデプロイ・運用する基盤

## 学習目標

このハンズオンを完了すると、以下ができるようになります。

1. **Flows を理解する**: ノードを接続して制御可能な生成 AI ワークフローを構築する
2. **AgentCore Runtime を理解する**: 任意フレームワークのエージェントをサーバーレスでホストする
3. **AgentCore の各機能を把握する**: Runtime / Identity / Gateway / Memory / Observability / Policy
4. **3 つの構築手段を使い分ける**: Flows / Agents / AgentCore の関係を理解する

## 3 つの構築手段の関係

```
Amazon Bedrock Flows     … ビジュアルなワークフロー（ノード接続）
Amazon Bedrock Agents    … マネージドエージェント（アクショングループ等）
Amazon Bedrock AgentCore … 本番運用基盤（Runtime/Gateway/Identity/Memory/Observability/Policy）

これらは排他ではなく、アプリの各コンポーネントで自由に組み合わせて使えます。
```

> **重要（最新情報）**: クラシックな Amazon Bedrock Agents（`bedrock-agent`）は
> **メンテナンスモード**で、新規顧客にはクローズされています。
> 新規のエージェントワークロードでは **AgentCore**（Runtime / Harness）が推奨です。
> 本モジュールでは概念理解のため両方に触れつつ、実装デモは AgentCore Runtime を中心に扱います。

## AgentCore の主な機能

| 機能 | 役割 |
|------|------|
| Runtime | サーバーレスでエージェント/ツールをホスト（任意モデル・任意フレームワーク） |
| Identity | エージェントの認証・認可（外部 IdP 統合） |
| Gateway | API/Lambda を MCP 互換ツールに変換 |
| Memory | 短期・長期メモリ（セッション跨ぎ） |
| Observability | トレース・デバッグ・モニタリング |
| Policy | 自然言語/Cedar でエージェントの境界を強制 |

## 使用する AWS サービス

- Amazon Bedrock Flows（`bedrock-agent` / `bedrock-agent-runtime`）
- Amazon Bedrock AgentCore（`bedrock-agentcore` / スターターツールキット）
- Strands Agents（AgentCore にデプロイするエージェント本体）

## 所要時間

約 60 分

## 前提条件

- AWS CLI 設定済み / Python 3.12+
- パッケージ: `boto3`, `strands-agents`, `bedrock-agentcore`, `bedrock-agentcore-starter-toolkit`
- モデルアクセス有効化済み: Anthropic Claude Sonnet 4.5 / Amazon Nova
- Docker（AgentCore Runtime のコンテナデプロイを行う場合）
