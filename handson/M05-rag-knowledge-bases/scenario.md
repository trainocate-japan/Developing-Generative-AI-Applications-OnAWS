# モジュール 5: RAG による生成 AI レスポンスのカスタマイズ - ハンズオンシナリオ

## シナリオ概要

あなたは社内ヘルプデスク向けのチャットボットを開発しています。
基盤モデルは一般知識には強いものの、**自社製品「AnyCompany Cloud」独自の仕様**は知りません。
そこで、社内ドキュメントを **Amazon Bedrock Knowledge Bases** に取り込み、
検索拡張生成 (RAG) で「根拠付きの回答」を返すチャットボットを構築します。

## 学習目標

このハンズオンを完了すると、以下ができるようになります。

1. **RAG の仕組みを理解する**: 埋め込み → チャンク化 → ベクトル検索 → プロンプト拡張 → 生成
2. **Knowledge Base を作成する**: S3 データソース + Titan Embeddings V2 + ベクトルストア
3. **RetrieveAndGenerate を使う**: 検索から回答生成までを 1 API で実行し、引用を得る
4. **Retrieve を使う**: 生のチャンクを取得し、独自の後処理・プロンプトに組み込む
5. **クエリをカスタマイズする**: 取得件数・カスタムプロンプト・出力言語を制御する

## RAG のデータフロー

```
【取り込み(ハイドレート)】
  エンタープライズデータ → チャンク化 → 埋め込みに変換 → ベクトルストアに保存

【検索と生成】
  ユーザー質問 → 埋め込み → ベクトル検索 → 関連チャンク取得
             → プロンプト拡張（質問＋チャンク）→ FM が回答生成（引用付き）
```

## 検索用の主な API

| API | 役割 |
|-----|------|
| `RetrieveAndGenerate` | 検索＋回答生成をエンドツーエンドで実行（引用付き） |
| `Retrieve` | クエリに関連するチャンクを配列で返す（生成は自前） |

## 使用する AWS サービス

- Amazon Bedrock Knowledge Bases（`bedrock-agent` / `bedrock-agent-runtime`）
- Amazon Titan Text Embeddings V2（埋め込み）
- ベクトルストア（Amazon OpenSearch Serverless など。KB 作成時にクイック作成可）
- Amazon S3（データソース）
- Anthropic Claude Sonnet 4.5 / Amazon Nova（回答生成）

## 所要時間

約 60 分（うち KB 作成・同期の待ち時間を含む）

## 前提条件

- AWS CLI 設定済み / Python 3.12+
- モデルアクセス有効化済み: Amazon Titan Text Embeddings V2、Anthropic Claude Sonnet 4.5、Amazon Nova Lite
- Knowledge Base 作成に必要な IAM 権限（コンソールのクイック作成が簡単）
