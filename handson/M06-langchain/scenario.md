# モジュール 6: オープンソースフレームワーク（LangChain）と Amazon Bedrock の統合 - ハンズオンシナリオ

## シナリオ概要

あなたは、複数の生成 AI 機能（翻訳・要約・チャット）を持つアプリを開発しています。
Bedrock API を直接呼ぶ代わりに、**LangChain** を使うことで、プロンプトテンプレート・チェーン・
メモリなどの再利用可能なコンポーネントを活用し、開発を効率化します。

## 学習目標

このハンズオンを完了すると、以下ができるようになります。

1. **LangChain から Bedrock を呼ぶ**: `ChatBedrockConverse`（langchain-aws）でモデルを呼び出す
2. **抽象化の利点を理解する**: 直接 API 呼び出しとの違い（追加コンポーネント・可搬性）
3. **チェーンを構築する**: プロンプトテンプレート `|` モデル `|` 出力パーサーを連結する
4. **会話メモリを実装する**: `RunnableWithMessageHistory` + DynamoDB でセッション履歴を保持する

## LangChain と直接 API の比較

| 観点 | Amazon Bedrock API 直接 | LangChain（オープンソース） |
|------|------------------------|---------------------------|
| 速度・効率 | 迅速・軽量 | 抽象化レイヤーが加わる |
| 提供元 | AWS の SDK | サードパーティのプロジェクト |
| 追加機能 | 最小限 | プロンプト・チェーン・メモリ・エージェント等 |

> LangChain は「速くなる」わけではありません。**追加の抽象化とコンポーネント**が使えるのが利点です。

## LangChain の主なコンポーネント

```
モデル (ChatBedrockConverse)
プロンプトテンプレート (ChatPromptTemplate)
チェーン (prompt | model | parser)
メモリ (RunnableWithMessageHistory + DynamoDBChatMessageHistory)
```

## 使用する AWS サービス

- Amazon Bedrock（`langchain-aws` の `ChatBedrockConverse` 経由）
- Amazon DynamoDB（会話履歴の保存）

## 所要時間

約 40 分

## 前提条件

- AWS CLI 設定済み / Python 3.12+
- パッケージ: `langchain`, `langchain-aws`, `langchain-community`, `boto3`
- モデルアクセス有効化済み: Anthropic Claude Sonnet 4.5 / Amazon Nova Lite
