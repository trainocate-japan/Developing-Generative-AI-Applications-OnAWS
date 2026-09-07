# モジュール 6: LangChain と Amazon Bedrock の統合 - ハンズオン手順

## パート 1: 準備（5分）

### ステップ 1.1: プロジェクトの準備

```bash
cd ~/handson/M06-langchain
```

### ステップ 1.2: パッケージの確認

EC2 環境にはインストール済みです。ローカルの場合は以下を実行します。

```bash
pip install langchain langchain-aws langchain-community boto3
```

---

## パート 2: LangChain から Bedrock を呼び出す（10分）

### ステップ 2.1: 基本の呼び出し

```bash
python langchain_basics.py
```

- `ChatBedrockConverse`（`langchain-aws`）で Bedrock を呼び出す
- `SystemMessage` / `HumanMessage` という LangChain のメッセージ抽象を使う
- 内部では Bedrock の Converse API が呼ばれている

**議論**: LangChain を使う利点は「速くなる」ことではなく、**追加の抽象化とコンポーネント**が
使えること。直接 API と比べて何が便利になるか話し合う。

---

## パート 3: チェーンを構築する（10分）

### ステップ 3.1: プロンプト | モデル | パーサー

```bash
python langchain_chain.py
```

- `ChatPromptTemplate` でテンプレート化
- LCEL（`|`）で `prompt | model | StrOutputParser()` を連結
- `language` を差し替えるだけで多言語翻訳パイプラインを再利用

### ステップ 3.2: チェーンの構成要素

| 要素 | 役割 |
|------|------|
| `ChatPromptTemplate` | プレースホルダー付きプロンプト |
| `ChatBedrockConverse` | Bedrock モデル |
| `StrOutputParser` | モデル出力を文字列に変換 |

---

## パート 4: 会話メモリ（DynamoDB）（15分）

### ステップ 4.1: DynamoDB 永続メモリ付きチャット

```bash
python langchain_memory.py
```

- 初回に `genai-handson-sessions` テーブル（パーティションキー `SessionId`）を自動作成
- 1 つ目で名前を伝え、2 つ目で「名前を覚えていますか？」に答えられることを確認
- `RunnableWithMessageHistory` が `session_id` ごとに履歴を DynamoDB から出し入れ

> **補足（DeprecationWarning について）**: 実行時に `langchain-community` のサンセットや
> `RunnableWithMessageHistory` の非推奨に関する警告が表示される場合があります。
> 動作には影響しません。より新しい構成では、履歴管理に **LangGraph の永続化（checkpointer）** を
> 使う方法が推奨されています。本ハンズオンでは概念理解のため従来の構成を使用しています。

### ステップ 4.2: 永続化を確認する

```bash
# もう一度実行しても履歴が残っている
python langchain_memory.py

# DynamoDB の中身を確認
aws dynamodb get-item --table-name genai-handson-sessions --region us-east-1 \
  --key '{"SessionId": {"S": "user-alice"}}' --query "Item.History" --output text | head -c 500
```

### ステップ 4.3: スライドとの対応

スライドでは会話履歴の保存に「**セッションテーブル (SessionTable)**」を使っていました。
本ハンズオンでも同様に、`session_id` をキーにした DynamoDB テーブルで履歴を管理しています。

---

## パート 5: まとめとナレッジチェック（5分）

### ナレッジチェック（スライド対応）

1. LangChain + DynamoDB で会話履歴の保存に使うテーブルは？ → **セッションテーブル**
2. Bedrock で LangChain を使う利点は？ → **さらに抽象化とコンポーネントが利用できる**
   （「速くなる」「AWS 公式サポート」「特定モデル限定」は誤り）

### クリーンアップ

```bash
cd ~/handson
bash cleanup_all.sh   # genai-handson-sessions テーブルを削除
```

---

## 参考ドキュメント

- [langchain-aws: ChatBedrockConverse](https://python.langchain.com/docs/integrations/chat/bedrock/)
- [RunnableWithMessageHistory](https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html)
- [DynamoDBChatMessageHistory](https://python.langchain.com/docs/integrations/memory/aws_dynamodb/)
- [Amazon Bedrock, DynamoDB, LangChain でスケーラブルなチャットボットを構築](https://aws.amazon.com/blogs/database/build-a-scalable-context-aware-chatbot-with-amazon-dynamodb-amazon-bedrock-and-langchain/)
