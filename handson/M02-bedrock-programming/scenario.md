# モジュール 2: Amazon Bedrock でのプログラミング - ハンズオンシナリオ

## シナリオ概要

あなたは開発チームで「大規模言語モデル (LLM) を利用したコーディングアシスタント」を実装する担当になりました。
Amazon Bedrock を**プログラムから**呼び出し、推論パラメータで応答をコントロールしながら、
用途に応じて適切な API（InvokeModel / Converse / ストリーミング）を選べるようになることが目標です。

## 学習目標

このハンズオンを完了すると、以下ができるようになります。

1. **推論パラメータで応答を誘導する**: `temperature` / `topP` / `maxTokens` / `stopSequences` の効果を体感する
2. **基盤モデルを一覧表示する**: `bedrock`（コントロールプレーン）クライアントでモデルを確認する
3. **InvokeModel を使う**: プロバイダー固有のリクエストボディを理解する
4. **Converse API を使う**: モデルに依存しない統一インターフェイスの利点を理解する
5. **ストリーミングを実装する**: `ConverseStream` で最初のトークンまでのレイテンシーを短縮する
6. **API を使い分ける**: どのユースケースでどの API を選ぶべきか判断できる

## API の全体像

| クライアント | エンドポイント | 主な API | 用途 |
|-------------|--------------|---------|------|
| `bedrock` | コントロールプレーン | `ListFoundationModels` | モデル一覧・管理 |
| `bedrock-runtime` | データプレーン | `InvokeModel`, `Converse`, `ConverseStream` | モデルの呼び出し（推論） |

### API の選択指針

| API | 特徴 | 向いているケース |
|-----|------|----------------|
| InvokeModel | プロバイダー固有のボディ形式 | 特定モデル固有機能が必要な場合（まれ） |
| Converse | モデル非依存の統一形式（推奨） | 複数モデルを切り替える、標準的な呼び出し |
| ConverseStream | トークンを逐次受信 | チャット UI など低レイテンシーが必要な場合 |

> **重要**: どの API でも `maxTokens`（最大出力トークン）は必ず明示的に指定します。
> 未指定だとモデルの最大値が予約され、`ThrottlingException` の原因になります。

## 使用する AWS サービス

- Amazon Bedrock（`bedrock` / `bedrock-runtime`）
- Amazon Nova Lite / Nova Pro、Anthropic Claude Sonnet 4.5

## 所要時間

約 45 分

## 前提条件

- AWS CLI 設定済み / Python 3.12+ / boto3（v1.34 以降）
- モデルアクセス有効化済み: Amazon Nova Lite / Pro、Anthropic Claude Sonnet 4.5
