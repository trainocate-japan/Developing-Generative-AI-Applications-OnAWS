# モジュール 8: 責任ある AI の実装 - ハンズオン手順

## パート 1: 責任ある AI のリスクを整理する（5分）

生成 AI の新たなリスクと、Guardrail による対処を対応づけます。

| リスク | 説明 | Guardrail での対処 |
|--------|------|------------------|
| 信憑性（ハルシネーション） | 事実と異なる生成 | 状況に応じたグラウンディングチェック |
| 有害性・安全性 | 有害・攻撃的な内容 | コンテンツフィルター |
| 知的財産 | 不適切な引用・生成 | 単語フィルター・拒否トピック |
| データプライバシー | PII 漏洩 | 機密情報フィルター |

---

## パート 2: Guardrail を作成する（15分）

### ステップ 2.1: プロジェクトの準備

```bash
cd ~/handson/M08-responsible-ai
```

### ステップ 2.2: プログラムから Guardrail を作成

```bash
python create_guardrail.py
```

作成される Guardrail（`genai-handson-guardrail`）には以下が設定されます。

- **拒否トピック**: 投資助言（InvestmentAdvice）
- **コンテンツフィルター**: 憎悪・侮辱・性的・暴力・プロンプト攻撃
- **単語フィルター**: 冒涜語（マネージドリスト）
- **機密情報フィルター**: メール・電話番号を匿名化（マスク）

> **Standard Tier と日本語対応（重要）**: このハンズオンは日本語コンテンツを扱うため、
> ガードレールを **Standard Tier** で作成します。Standard Tier は日本語を
> 「Optimized and supported（最適化＆サポート）」で扱えます（Classic Tier では
> 日本語の拒否トピック・コンテンツ検出の精度が限定的）。
> Standard Tier はクロスリージョン設定が必須のため、コード内で
> `crossRegionConfig`（ガードレールプロファイル `us.guardrail.v1:0`）と
> 各ポリシーの `tierConfig={"tierName": "STANDARD"}` を指定しています。
> `us.` プロファイルは推論を us-east-1 / us-east-2 / us-west-2 へ自動ルーティングします。

出力された Guardrail ID を控えます。

```bash
export GUARDRAIL_ID=<create_guardrail.py が出力した ID>
```

### ステップ 2.3: コンソールでの作成（参考）

コンソールでも作成できます: Bedrock → **Guardrails** → **Create guardrail**。
コンテンツフィルターの強度、拒否トピック、PII の扱い（ブロック/マスク）を GUI で設定できます。

---

## パート 3: Guardrail をテストする（15分）

### ステップ 3.1: ApplyGuardrail でテキストを評価

```bash
python test_guardrail.py
```

3 つのケースで動作を確認します。

| ケース | 期待される結果 |
|--------|--------------|
| 通常の質問 | 通過（action = NONE） |
| 投資助言の質問 | ブロック（拒否トピック検出、GUARDRAIL_INTERVENED） |
| PII を含む出力 | メール・電話がマスクされる |

- `ApplyGuardrail` はモデルを呼ばずにテキストだけを評価できる（コスト効率が良い）
- 入力（INPUT）と出力（OUTPUT）の両方に同じ Guardrail を適用できる

---

## パート 4: プロンプトインジェクション対策（10分）

### ステップ 4.1: モデル呼び出し時に Guardrail を適用

```bash
python prompt_injection_demo.py
```

- 「コードレビュー依頼」を装って指示を乗っ取ろうとする入力を送信
- `converse` に `guardrailConfig` を渡すと、プロンプト攻撃検出が働き `stopReason=guardrail_intervened` でブロック

### ステップ 4.2: 多層防御を議論する

Guardrail だけに頼らず、以下を組み合わせます。

- 入力の検証とサニタイズ
- 安全なプロンプト設計（役割の固定、区切りの明確化）
- アクセスコントロール（決定論的制御）
- モニタリングと検出

---

## パート 5: まとめとナレッジチェック（5分）

### 決定論的制御 vs 確率的制御

| | 決定論的制御 | 確率的制御 |
|--|------------|-----------|
| 例 | ユーザー権限チェック、単語フィルター | 有害コンテンツ・バイアス検出 |
| 特徴 | ルールで確実に判定 | モデルで文脈判断 |

### ナレッジチェック（スライド対応）

1. AI の意思決定の根拠を示すことで対処できる責任ある AI の側面は？ → **説明可能性**
2. バイアス軽減の効果的な手法は？ → **より代表的なサンプルでデータセットを強化する**
3. 決定論的制御で最適に処理できるシナリオは？ → **モデル送信前にユーザーの権限を確認する**

### クリーンアップ

```bash
cd ~/handson
bash cleanup_all.sh   # genai-handson-guardrail を削除
```

---

## 参考ドキュメント

- [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)
- [ApplyGuardrail API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_ApplyGuardrail.html)
- [Guardrails がサポートする言語（Standard Tier）](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-supported-languages.html)
- [クロスリージョンガードレール推論](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-cross-region.html)
- [AWS の責任ある AI](https://aws.amazon.com/machine-learning/responsible-ai/)
