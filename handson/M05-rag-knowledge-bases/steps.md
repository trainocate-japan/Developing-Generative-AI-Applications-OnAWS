# モジュール 5: RAG による生成 AI レスポンスのカスタマイズ - ハンズオン手順

## パート 1: RAG なしの限界を確認する（5分）

### ステップ 1.1: 基盤モデルに社内情報を聞いてみる

Amazon Bedrock コンソール → Test playgrounds → Chat/Text（モデル: Nova Lite）で質問します。

```
AnyCompany Cloud の Enterprise プランのバックアップ保持期間は何日ですか？
```

**観察ポイント**: モデルは架空の社内製品を知らないため、答えられない・推測で答えることを確認します。
→ これが RAG（社内データの検索と根拠付き生成）が必要な理由です。

---

## パート 2: サンプルドキュメントを S3 にアップロード（10分）

### ステップ 2.1: バケットを作成して資材をアップロード

```bash
cd ~/handson/M05-rag-knowledge-bases

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
KB_BUCKET="genai-handson-kb-docs-${ACCOUNT_ID}"

# バケット作成（us-east-1 の場合）
aws s3 mb s3://$KB_BUCKET --region us-east-1

# サンプルドキュメントをアップロード
aws s3 cp sample-docs/ s3://$KB_BUCKET/docs/ --recursive

# 確認
aws s3 ls s3://$KB_BUCKET/docs/
```

---

## パート 3: Knowledge Base を作成する（コンソール）（20分）

### ステップ 3.1: Knowledge Base の作成を開始

1. Amazon Bedrock コンソール → 左ナビ **Knowledge Bases** → **Create** → **Knowledge Base with vector store**
2. **Knowledge Base name**: `genai-handson-kb`
3. **IAM permissions**: **Create and use a new service role**（新しいロールを自動作成）
4. **Next**

### ステップ 3.2: データソースの設定

1. **Data source name**: `anycompany-docs`
2. **S3 URI**: 上でアップロードした `s3://genai-handson-kb-docs-<ACCOUNT_ID>/docs/` を指定
3. **Chunking strategy**: **Default chunking**（まずは既定でOK。表を含む PDF では後述の高度なパースを検討）
4. **Next**

### ステップ 3.3: 埋め込みモデルとベクトルストア

1. **Embeddings model**: **Titan Text Embeddings V2** を選択
2. **Vector store**: **Quick create a new vector store**（Amazon OpenSearch Serverless を自動作成）
3. **Next** → 設定を確認して **Create Knowledge Base**

> 作成には数分かかります。ベクトルストアの準備が完了するまで待ちます。

### ステップ 3.4: データを同期（Sync）

1. Knowledge Base の詳細画面 → **Data source** で `anycompany-docs` を選択 → **Sync**
2. Sync が **Completed** になるまで待つ（ドキュメントがチャンク化・埋め込み・格納されます）

> 同期前にクエリすると結果が空になります。必ず Sync 完了を待ちましょう。

### ステップ 3.5: Knowledge Base ID を控える

詳細画面の **Knowledge Base ID**（例: `ABCD1234EF`）をメモします。

```bash
# CLI でも取得できます
aws bedrock-agent list-knowledge-bases --region us-east-1 \
  --query "knowledgeBaseSummaries[?name=='genai-handson-kb'].knowledgeBaseId" --output text
```

---

## パート 4: RetrieveAndGenerate で RAG を実行（10分）

### ステップ 4.1: 環境変数に KB ID を設定

```bash
export KB_ID=<ステップ 3.5 の Knowledge Base ID>
```

### ステップ 4.2: エンドツーエンドの RAG を実行

```bash
python retrieve_and_generate.py
python retrieve_and_generate.py "Business プランのサポート体制を教えてください。"
```

- パート 1 で答えられなかった質問に、**社内ドキュメントに基づいて**回答することを確認
- **引用（根拠）**が S3 の該当ファイルを指していることを確認

---

## パート 5: Retrieve で生チャンクを取得（10分）

### ステップ 5.1: 生チャンク取得 + 自前生成

```bash
python retrieve_only.py
python retrieve_only.py "デプロイが DEPLOY_007 で失敗します。原因は？"
```

- `Retrieve` は関連チャンクを**スコア付き**で返す
- 取得したチャンクを自前のプロンプトに埋め込み、`Converse` で回答を生成
- カスタムプロンプト・生成モデルの差し替え・複数 KB の統合などが自由にできる

### ステップ 5.2: カスタマイズを試す

- `retrieve_only.py` の `TOP_K` を変えて、取得件数が回答に与える影響を見る
- プロンプトの指示（「情報がない場合は『情報がありません』」）を変えて挙動を確認

---

## パート 6: まとめとナレッジチェック（5分）

### RetrieveAndGenerate と Retrieve の違い

| | RetrieveAndGenerate | Retrieve |
|--|---------------------|----------|
| 役割 | 検索＋生成をエンドツーエンド | 関連チャンクの取得のみ |
| 引用 | 自動で付与 | 自前で組み込む |
| 柔軟性 | 低（簡単） | 高（カスタムプロンプト・後処理） |

### ナレッジチェック（スライド対応）

1. RAG 用に KB をハイドレートするフローは？ → **データをチャンク化 → 埋め込みに変換 → KB に保存**
2. `Retrieve` の説明として正しいのは？ → クエリに関連するチャンクを配列で返す
3. `RetrieveAndGenerate` の説明として正しいのは？ → RAG パイプライン全体をエンドツーエンドで管理する

---

## クリーンアップ

OpenSearch Serverless は起動中課金されます。研修後に削除してください。

```bash
cd ~/handson
bash cleanup_all.sh   # KB とデータソースを削除

# ドキュメント用 S3 バケットの削除
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws s3 rb s3://genai-handson-kb-docs-$ACCOUNT_ID --force
```

> OpenSearch Serverless コレクションと自動作成された IAM ロールは、
> コンソール（OpenSearch Serverless / IAM）から手動で削除してください。

---

## 参考ドキュメント

- [Amazon Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [RetrieveAndGenerate API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_RetrieveAndGenerate.html)
- [Retrieve API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_Retrieve.html)
- [Amazon Titan Text Embeddings](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html)
