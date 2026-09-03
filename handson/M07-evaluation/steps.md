# モジュール 7: 生成 AI アプリケーションコンポーネントの評価 - ハンズオン手順

## パート 1: 優先順位に基づくモデル選択（15分）

### ステップ 1.1: プロジェクトの準備

```bash
cd ~/handson/M07-evaluation
```

### ステップ 1.2: モデルを実測比較する

```bash
python model_selection.py
```

- 同じ質問を Nova Lite / Nova Pro / Claude Sonnet に投げ、**レイテンシー**と**出力トークン数**を比較
- 出力の質（目視）とあわせて、コスト・品質・速度のトレードオフを確認

### ステップ 1.3: 選定プロセスを整理する

1. **簡単な候補リスト**: 少数のテストプロンプトでざっくり絞る
2. **ケースに基づくベンチマーク**: プロンプトカタログで定量評価
3. **優先順位に基づく選択**: コスト・品質・速度・レイテンシーで最終決定

**議論**: 大量の FAQ 応答には？（コスト優先で軽量モデル）。法務文書の要約には？（品質優先）。

---

## パート 2: RAG の評価（Ragas）（20分）

### ステップ 2.1: 評価データセットを確認

```bash
cat evaluation-dataset.jsonl
```

各行は 1 サンプルで、以下を含みます。

| フィールド | 意味 |
|-----------|------|
| `user_input` | ユーザーの質問 |
| `retrieved_contexts` | 検索で取得したコンテキスト |
| `response` | RAG が生成した応答 |
| `reference` | 期待される正解（リファレンス） |

### ステップ 2.2: Ragas で評価を実行

```bash
python rag_evaluation.py
```

- 評価者 LLM（Claude Sonnet）と埋め込み（Titan V2）に Bedrock を使用
- 3 つのメトリクスを算出（Bedrock を複数回呼ぶため数十秒かかります）

| メトリクス | 意味 | 低いときの対処 |
|-----------|------|--------------|
| Faithfulness（忠実度） | 応答がコンテキストに忠実か | ハルシネーション。生成プロンプトを見直す |
| ResponseRelevancy（応答の関連性） | 質問に的確に答えているか | 生成プロンプト・モデルを見直す |
| ContextPrecision（コンテキスト適合率） | 検索が適切か | チャンク戦略・検索設定を見直す |

### ステップ 2.3: 検索と生成の切り分け

- 検索系メトリクスが低い → **Retrieve（検索）**の問題（チャンク・埋め込み・件数）
- 生成系メトリクスが低い → **生成プロンプト・モデル**の問題

---

## パート 3: レイテンシーとコストの最適化（10分）

### ステップ 3.1: プロンプトキャッシュ

```bash
python latency_cost_optimization.py
```

- 大きな共通コンテキスト（製品仕様）を `cachePoint` でキャッシュ
- 1 回目は `cacheWrite`、2 回目は `cacheRead` が増える（＝ヒット）ことを確認
- `cacheRead` が 0 のままの場合の確認項目（対応モデル・トークン閾値・内容の一致・TTL）

### ステップ 3.2: その他の最適化手法

| 手法 | 効果 |
|------|------|
| プロンプトキャッシュ | 繰り返しコンテキストを再利用。コスト最大 90% / レイテンシー最大 85% 削減 |
| Intelligent Prompt Routing | 品質を予測して安価なモデルへ動的ルーティング |
| レイテンシー最適化推論 | `performanceConfig={"latency":"optimized"}` で TTFT 短縮 |

---

## パート 4: まとめとナレッジチェック（5分）

### ナレッジチェック（スライド対応）

1. 生成段階の評価に使う RAG メトリクスは？ → **忠実度 (Faithfulness)**
2. 応答から人工質問を作り、元の質問との類似度を測るメトリクスは？ → **応答の関連性 (ResponseRelevancy)**
3. 応答品質を動的に予測してレイテンシーを短縮する仕組みは？ → **Intelligent Prompt Routing**

---

## 参考ドキュメント

- [Amazon Bedrock によるモデル評価](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation.html)
- [プロンプトキャッシュ](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html)
- [レイテンシー最適化推論](https://docs.aws.amazon.com/bedrock/latest/userguide/latency-optimized-inference.html)
- [Ragas ドキュメント](https://docs.ragas.io/)
