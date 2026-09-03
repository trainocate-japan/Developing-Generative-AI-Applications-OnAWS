# モジュール 1: 生成 AI アプリケーションのコンポーネント - ハンズオン手順

## パート 1: Bedrock プレイグラウンドで「推論」と「コンテキスト」を体感する（10分）

### ステップ 1.1: Bedrock チャットプレイグラウンドを開く

1. AWS コンソールで **Amazon Bedrock** を開く: https://console.aws.amazon.com/bedrock/
2. 左ナビゲーションペインの **Test playgrounds** → **Chat / Text** を選択
3. **Select model** をクリックし、**Amazon** → **Nova Pro** を選択して **Apply**

### ステップ 1.2: コンテキストが応答に与える影響を観察する

以下を **1 つ目のプロンプト**として送信します。

```
シアトルで一番訪問するべき場所はどこですか？
```

続けて **2 つ目のプロンプト**を送信します（前の会話を踏まえて答えるか観察）。

```
それは子どもたちにも楽しめますか？
```

**観察ポイント**:
- 2 つ目の質問の「それ」が、1 つ目の回答を指していることをモデルが理解しているか
- この「会話のつながり」を成立させているのが**コンテキスト**（会話履歴）です
- コンテキストには**トークン数の上限**があり、**持続しない**（API を分けると失われる）ことを意識する

→ 会話を跨いで記憶させたい場合は、後のモジュールで学ぶ**メモリ**が必要になります。

---

## パート 2: AWS 生成 AI スタックを確認する（10分）

### ステップ 2.1: プロジェクトの準備

```bash
cd ~/handson/M01-components
```

### ステップ 2.2: 利用可能な基盤モデルを一覧表示する

```bash
python genai_stack_explorer.py
```

出力を見ながら、以下を確認します。

- Amazon Bedrock が「モデルとツール層」として、複数プロバイダーの FM に**単一 API**でアクセスできること
- 各モデルの**入力/出力モダリティ**（テキスト・画像・動画）と**ストリーミング対応**
- 本ハンズオンで使う Nova Lite / Nova Pro / Titan Embeddings / Claude Sonnet の存在

### ステップ 2.3: スタックの 3 層を整理する

| 層 | 代表サービス | 役割 |
|----|-------------|------|
| アプリケーション層 | Amazon Quick Suite, Amazon Q Developer, Kiro | 業務アプリ・生産性向上 |
| モデルとツール層 | **Amazon Bedrock**, Amazon Bedrock AgentCore | FM 呼び出し・エージェント運用 |
| インフラストラクチャ層 | Amazon SageMaker AI, AWS Trainium / Inferentia | モデルの構築・学習・推論基盤 |

---

## パート 3: 最小構成の生成 AI アプリを動かす（15分）

### ステップ 3.1: 4 つの主要コンポーネントを持つアプリを実行

```bash
python basic_app_architecture.py
```

### ステップ 3.2: コードとアーキテクチャの対応を確認

`basic_app_architecture.py` のコードは、主要コンポーネントに対応しています。

| コンポーネント | コード上の対応 |
|--------------|--------------|
| アプリケーションフロントエンド | `question`（固定の質問） |
| アプリケーションロジック | `build_prompt()` |
| FM インターフェイス | `bedrock-runtime` の `converse()` |
| 基盤モデル (FM) | `us.amazon.nova-lite-v1:0` |

### ステップ 3.3: 実験してみる

- `question` を別の質問に書き換えて再実行し、応答の違いを見る
- `system` プロンプト（アシスタントの役割）を変更して、口調や専門性がどう変わるか確認する
- `temperature` を `0.0` にすると応答がより決定的に、`1.0` に近づけると多様になることを確認する

---

## パート 4: オプションコンポーネントの必要性を議論する（5分）

このモジュールで作ったのは「1 往復で完結する」最小アプリです。
以下のような要件が出てきたとき、どのオプションコンポーネントが必要になるか整理します。

| 要件 | 必要なコンポーネント | 対応モジュール |
|------|-------------------|--------------|
| 会話の流れを覚えていてほしい | メモリ（会話コンテキスト） | M04 / M06 |
| 社内ドキュメントに基づいて答えてほしい | ベクトルストア（RAG） | M05 |
| 外部システムを操作してほしい | ツール / エージェント | M09 / M10 |
| 不適切な入出力をブロックしたい | ガードレール | M08 |

### ディスカッションポイント

1. 「まず最小構成で作り、必要に応じてコンポーネントを足す」アプローチの利点は何か
2. コンテキストの上限が、アプリ設計にどのような制約を与えるか

---

## 参考ドキュメント

- [Amazon Bedrock とは](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)
- [Converse API を使用した推論](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html)
- [Amazon Bedrock プレイグラウンド](https://docs.aws.amazon.com/bedrock/latest/userguide/playgrounds.html)
- [Amazon Nova とは](https://docs.aws.amazon.com/nova/latest/userguide/what-is-nova.html)
- [Amazon Bedrock で対応している基盤モデル](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html)
