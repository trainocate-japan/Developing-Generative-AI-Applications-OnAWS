# モジュール 10: Amazon Bedrock エージェントの開発 - ハンズオン手順

## パート 1: Amazon Bedrock Flows（20分）

### ステップ 1.1: プロジェクトの準備

```bash
cd ~/handson/M10-bedrock-agents
```

### ステップ 1.2: Flows 実行ロールを作成

Flows はプロンプトノードで Bedrock を呼ぶため、実行ロールが必要です。

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

cat > /tmp/flows-trust.json <<'EOF'
{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"bedrock.amazonaws.com"},"Action":"sts:AssumeRole"}]}
EOF

aws iam create-role --role-name GenAIHandsonFlowsRole \
  --assume-role-policy-document file:///tmp/flows-trust.json

aws iam attach-role-policy --role-name GenAIHandsonFlowsRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

export FLOWS_ROLE_ARN=arn:aws:iam::$ACCOUNT_ID:role/GenAIHandsonFlowsRole
echo $FLOWS_ROLE_ARN
```

### ステップ 1.3: フローを作成・実行

```bash
python create_flow.py
```

- `input -> prompt -> output` の最小フローを作成
- Prepare → バージョン発行 → エイリアス作成 → 実行、の流れを確認
- トピックを渡すと、プロンプトノードが説明文を生成して返す

### ステップ 1.4: コンソールのビジュアルビルダー（参考）

Bedrock コンソール → **Flows** → **Create flow** で、ノードをドラッグ＆ドロップして
同じフローを視覚的に構築・テスト・デプロイできます。ノード種別（ロジック / データ /
AI サービス / オーケストレーション / コード）を確認しましょう。

---

## パート 2: Amazon Bedrock Agents（座学）（10分）

> **最新情報**: クラシックな Amazon Bedrock Agents（`bedrock-agent`）は
> **メンテナンスモード**で、新規顧客にはクローズされています。
> 新規ワークロードでは AgentCore（Runtime / Harness）が推奨です。

マネージドエージェントの構成要素を整理します（スライド対応）。

| 構成要素 | 役割 |
|---------|------|
| アクショングループ | Lambda 等で外部アクションを実行 |
| ナレッジベース | RAG による社内情報参照（M05） |
| メモリ | セッション状態・長期保持（最大 365 日） |
| ガードレール | 安全対策（M08） |
| トレース | デバッグ・オブザーバビリティ |

---

## パート 3: Amazon Bedrock AgentCore Runtime（25分）

### ステップ 3.1: エージェントコードを確認

```bash
cat agentcore_runtime_agent.py
```

- `BedrockAgentCoreApp` の `@app.entrypoint` がリクエストを受ける
- 中身は M09 で学んだ Strands エージェント（ツール付き）

### ステップ 3.2: ローカルで動作確認

```bash
# 別ターミナルでローカルサーバーを起動
python agentcore_runtime_agent.py
```

ローカル HTTP サーバーが起動します（`app.run()`）。動作を確認したら Ctrl+C で停止します。

### ステップ 3.3: AgentCore Runtime へデプロイ（スターターツールキット）

```bash
# 設定（entrypoint と requirements を指定）
agentcore configure --entrypoint agentcore_runtime_agent.py

# デプロイ（コンテナビルド + Runtime 作成。Docker が必要）
agentcore launch

# 呼び出し
agentcore invoke '{"prompt": "AMZN の株価を教えてください。"}'
```

> `agentcore` CLI は `bedrock-agentcore-starter-toolkit` に含まれます。
> ARM64 コンテナのビルドが行われるため、Docker が必要です。

### ステップ 3.4: AgentCore の機能マップ（座学）

| 機能 | 役割 | 関連モジュール |
|------|------|--------------|
| Runtime | サーバーレスでエージェントをホスト | 本パート |
| Gateway | API/Lambda を MCP ツールに変換 | M09（MCP） |
| Identity | 外部 IdP と統合した認証・認可 | M08（責任ある AI） |
| Memory | 短期・長期メモリ | M04 / M06（会話メモリ） |
| Observability | トレース・モニタリング | M07（評価） |
| Policy | 自然言語/Cedar で境界を強制 | M08 |

---

## パート 4: まとめとナレッジチェック（5分）

### ナレッジチェック（スライド対応）

1. ビジュアルビルダーでワークフローを作成・テスト・デプロイする機能は？ → **Amazon Bedrock Flows**
2. API/Lambda をエージェントが使えるツールに変換する AgentCore コンポーネントは？ → **AgentCore Gateway**
3. Flows / Agents / AgentCore の関係は？ → **各コンポーネントで自由に組み合わせて使える**

### コース全体のまとめ

| モジュール | 学んだこと | 本モジュールとの関係 |
|-----------|-----------|-------------------|
| M02 | モデル呼び出し | エージェントの推論エンジン |
| M03 | プロンプト | system_prompt / ツール説明 |
| M05 | RAG | ナレッジベース連携 |
| M08 | ガードレール | エージェントの安全対策 |
| M09 | ツール・エージェント | AgentCore にデプロイする本体 |

### クリーンアップ

```bash
cd ~/handson
bash cleanup_all.sh   # Flow を削除

# AgentCore Runtime をデプロイした場合
agentcore destroy     # または コンソールから Runtime / ECR を削除

# Flows 実行ロールの削除
aws iam detach-role-policy --role-name GenAIHandsonFlowsRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
aws iam delete-role --role-name GenAIHandsonFlowsRole
```

---

## 参考ドキュメント

- [Amazon Bedrock Flows](https://docs.aws.amazon.com/bedrock/latest/userguide/flows.html)
- [Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html)
- [AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime.html)
- [Bedrock Agents クラシック メンテナンスモードのお知らせ](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-classic-maintenance-mode.html)
- [Strands Agents SDK](https://strandsagents.com/latest/documentation/docs/)
