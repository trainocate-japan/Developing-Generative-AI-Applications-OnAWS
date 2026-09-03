# モジュール 9: ツールとエージェントの使用 - ハンズオン手順

## パート 1: ツール使用（関数呼び出し）の基礎（15分）

### ステップ 1.1: プロジェクトの準備

```bash
cd ~/handson/M09-tools-agents
```

### ステップ 1.2: Converse API のツール使用ループ

```bash
python tool_use_converse.py
```

出力を追いながら、ツール実行ループを確認します。

1. モデルが `toolUse`（どのツールをどの引数で呼ぶか）を返す
2. アプリが実際の関数（`get_weather` など）を実行
3. 結果を `toolResult` としてモデルに返す
4. モデルが結果を踏まえた最終回答を生成

**重要**: モデルは「ツールを呼ぶ判断」をするだけで、**実行はアプリ側の責務**です。
2 つ目の質問（株価＋天気）では、複数ツールが順に呼ばれることを確認します。

---

## パート 2: エージェントフレームワーク（Strands）（15分）

### ステップ 2.1: Strands Agents で同じことを実現

```bash
python strands_agent.py
```

- `@tool` デコレーターで関数をツール化（docstring と型ヒントがそのままツール仕様に）
- ツール実行ループはフレームワークが自動で処理
- `tool_use_converse.py` と同じ動作を、はるかに少ないコードで実現

### ステップ 2.2: フレームワークの比較（座学）

| フレームワーク | 特徴 |
|--------------|------|
| Strands Agents | モデル駆動型。エージェント構築を簡素化・高速化 |
| CrewAI | ロール・タスク・Crew でエージェントを編成 |
| LangGraph | ノード・エッジ・状態でグラフ型オーケストレーション |

---

## パート 3: MCP（Model Context Protocol）（10分）

### ステップ 3.1: MCP クライアントでツールを検出・呼び出し

```bash
pip install "mcp[cli]"   # EC2 環境では未導入の場合のみ
python mcp_client_demo.py
```

- `mcp_client_demo.py` が `mcp_server_demo.py` を stdio 経由で起動
- サーバーが公開するツール一覧を取得し、`get_weather` を呼び出す
- MCP は「ツールへの統一アクセス」を提供する標準プロトコル

### ステップ 3.2: MCP と A2A の違い（座学）

| 観点 | MCP | A2A |
|------|-----|-----|
| やり取り | 単一エージェント/ツール接続 | 複数エージェント間 |
| 通信 | MCP サーバー/ホストで一元化 | ピアツーピア |
| 適合 | ツールオーケストレーション | 分散タスク委任・専門化 |

---

## パート 4: まとめとナレッジチェック（5分）

### ナレッジチェック（スライド対応）

1. LLM の推論に基づく行動を可能にするコンポーネントは？ → **ツール**
2. モデル駆動型開発でエージェント構築を簡素化するフレームワークは？ → **Strands**
3. カスタム API を作らずにツールへの統合アクセスを設定するには？ → **モデルコンテキストプロトコル (MCP)**

---

## 参考ドキュメント

- [Converse API のツール使用](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html)
- [Strands Agents SDK](https://strandsagents.com/latest/documentation/docs/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [AgentCore Gateway（API/Lambda を MCP ツールに変換）](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)
