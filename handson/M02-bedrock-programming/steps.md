# モジュール 2: Amazon Bedrock でのプログラミング - ハンズオン手順

## パート 1: 推論パラメータで応答を誘導する（10分）

### ステップ 1.1: プロジェクトの準備

```bash
cd ~/handson/M02-bedrock-programming
```

### ステップ 1.2: temperature の効果を体感する

```bash
python inference_parameters.py
```

出力を見ながら、以下を確認します。

- `temperature = 0.0` は 2 回とも**ほぼ同じ**出力（決定的）
- `temperature = 1.0` は 2 回で**異なる**出力（多様）
- `stopSequences` に `"3."` を指定すると、3 番目の項目の直前で生成が止まる

**議論**: コーディングアシスタントを作るなら `temperature` は高い方がよいか、低い方がよいか。
（→ 正確性・再現性が重要なので低め。`temperature=0.3`, `top_p=0.2` などが目安）

---

## パート 2: モデルの一覧表示（コントロールプレーン）（5分）

### ステップ 2.1: 利用可能なモデルを確認

```bash
python list_models.py
```

- `bedrock` クライアント（コントロールプレーン）は**モデルの一覧・管理**に使う
- 推論（モデルの呼び出し）は `bedrock-runtime`（データプレーン）を使う、という違いを押さえる

---

## パート 3: InvokeModel（プロバイダー固有ボディ）（10分）

### ステップ 3.1: Amazon Nova 形式のボディで呼び出す

```bash
python invoke_model.py
```

- リクエストボディが `{"schemaVersion": "messages-v1", "messages": [...]}` という **Nova 固有**の形式
- Claude や Llama では別の形式が必要になる点を確認する
- 誤った形式を送ると `Malformed input request` エラーになる

---

## パート 4: Converse API（統一インターフェイス）（10分）

### ステップ 4.1: 同じコードで複数モデルを呼び出す

```bash
python converse_api.py
```

- `modelId` を変えるだけで、**Nova と Claude を同じコード**で呼び出せる
- レスポンス構造も統一（`output.message.content[0].text`、`usage`）
- これが Converse API を推奨する理由

### ステップ 4.2: リクエストの構成要素を確認

| 要素 | 役割 |
|------|------|
| `system` | システムプロンプト（役割・行動ガイドライン） |
| `messages` | ユーザー / アシスタントのやり取り |
| `inferenceConfig` | `maxTokens` / `temperature` / `topP` / `stopSequences` |

> `maxTokens` は必ず指定します。未指定だとモデル最大値が予約され `ThrottlingException` の原因になります。

---

## パート 5: ConverseStream（ストリーミング）（5分）

### ステップ 5.1: トークンを逐次表示する

```bash
python converse_stream.py
```

- 応答が**少しずつ**表示されることを確認（`contentBlockDelta` を逐次処理）
- チャット UI のように体感レイテンシーを下げたいときに有効
- AWS CLI はストリーミング非対応。SDK（`converse_stream`）が必要

---

## パート 6: API の使い分けとまとめ（5分）

### API 選択のまとめ

| API | 使うべきケース |
|-----|--------------|
| InvokeModel | プロバイダー固有機能が必要な場合（まれ） |
| Converse | 標準的な呼び出し、複数モデルの切り替え（**基本はこれ**） |
| ConverseStream | チャット UI・低レイテンシーが必要な対話アプリ |

### ナレッジチェック（スライド対応）

1. コーディングアシスタント（収益化）に適した推論パラメータは？ → `top_p = 0.2`, `temperature = 0.3`（正確性重視）
2. コンソールと Boto3 は Bedrock 操作で異なる API を使う？ → **誤**（同じ API を使用）
3. 低レイテンシーでモデルを柔軟に切り替えたいときに使う API は？ → **ConverseStream**

---

## 参考ドキュメント

- [Converse API を使用した推論](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html)
- [推論パラメータ (InferenceConfiguration)](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InferenceConfiguration.html)
- [Amazon Bedrock でサポートされている API](https://docs.aws.amazon.com/bedrock/latest/userguide/apis.html)
- [AWS SDK for Python (Boto3) - Bedrock Runtime](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime.html)
