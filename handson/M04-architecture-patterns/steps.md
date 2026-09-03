# モジュール 4: 一般的なアーキテクチャでの Amazon Bedrock API の使用 - ハンズオン手順

## パート 1: 4 つのアーキテクチャパターン（15分）

### ステップ 1.1: プロジェクトの準備

```bash
cd ~/handson/M04-architecture-patterns
```

### ステップ 1.2: パターンを実行して比較

```bash
python architecture_patterns.py
```

同じ Converse API で、**生成 / 要約 / 質問応答**の 3 パターンが実装されていることを確認します。
違いは「プロンプトの組み立て方」だけです。

| パターン | プロンプトの特徴 |
|---------|----------------|
| 生成 | 「〜を書いてください」 |
| 要約 | 「次の文章を要約してください」＋入力データ |
| 質問応答 | 質問文＋system で出力形式を指定 |

---

## パート 2: 推論モードの比較（10分）

### ステップ 2.1: オンデマンド推論を計測

```bash
python batch_vs_ondemand.py
```

- 実際のレイテンシーとトークン使用量を確認
- オンデマンド料金の考え方（入力トークン × 単価 + 出力トークン × 単価）を理解

### ステップ 2.2: モードの使い分け

| モード | 選ぶ基準 |
|-------|---------|
| オンデマンド | すぐ応答が欲しい・トラフィックが読めない（チャット・RAG） |
| バッチ | 大量データを安く処理したい（レポート・分析）。S3 入出力を使う |
| プロビジョンドスループット | 一定の大規模負荷でスループットを保証したい |

---

## パート 3: 会話メモリの追加（20分）

### ステップ 3.1: インメモリの会話メモリ

```bash
python conversation_memory.py
```

- 2 つ目の質問「そこは子ども連れでも...」の「そこ」が、1 つ目の観光スポットを指せていることを確認
- これは過去のやり取りを `messages` に積み重ねているため（＝会話メモリ）

### ステップ 3.2: DynamoDB で永続化する

```bash
python conversation_memory.py --dynamodb
```

- 初回は `genai-handson-conversation` テーブルを自動作成し、会話を保存
- **もう一度**同じコマンドを実行すると、DynamoDB から履歴を復元してから会話を続けることを確認

```bash
# 保存された履歴を CLI で確認
aws dynamodb scan --table-name genai-handson-conversation --region us-east-1 \
  --query "Items[].{turn:turn.N, role:role.S, text:text.S}" --output table
```

### ステップ 3.3: 後片付け

DynamoDB テーブルは課金対象（PAY_PER_REQUEST）です。研修終了後に削除します。

```bash
cd ~/handson
bash cleanup_all.sh
```

---

## パート 4: まとめとナレッジチェック（5分）

### ナレッジチェック（スライド対応）

1. 会話型アプリで「this / that / it」などの代名詞を適切に処理するには？ → **メモリ**（会話コンテキスト）
2. チャットボットに適した推論モードは？ → **オンデマンド**（低レイテンシー）
3. 大量のAIレポート生成に適した推論モードは？ → **バッチ**（低コスト）

---

## 参考ドキュメント

- [Converse API を使用した推論](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html)
- [バッチ推論](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference.html)
- [プロビジョンドスループット](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html)
- [Amazon DynamoDB とは](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html)
