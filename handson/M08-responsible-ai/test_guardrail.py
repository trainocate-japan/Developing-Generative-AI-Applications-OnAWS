"""
モジュール 8: Guardrail のテスト（ApplyGuardrail）
------------------------------------------------------------
ApplyGuardrail API を使い、モデルを呼ばずに入力/出力テキストだけを評価します。
拒否トピック・PII マスク・コンテンツフィルターの動作を確認します。

使い方:
    export GUARDRAIL_ID=xxxxxxxxxx   # create_guardrail.py の出力
    python test_guardrail.py
"""

import os
import sys
import boto3
from botocore.config import Config

REGION = "us-east-1"
GUARDRAIL_VERSION = "DRAFT"  # 作業中の最新版を使う（発行済みバージョン番号でも可）


def apply(br, guardrail_id, text, source):
    """source は 'INPUT' か 'OUTPUT'"""
    return br.apply_guardrail(
        guardrailIdentifier=guardrail_id,
        guardrailVersion=GUARDRAIL_VERSION,
        source=source,
        content=[{"text": {"text": text}}],
    )


def show(label, resp):
    action = resp.get("action")
    print(f"\n[{label}] action = {action}")
    # マスクされた/返却されるテキスト
    for out in resp.get("outputs", []):
        print(f"  出力テキスト: {out.get('text')}")
    # 検出された評価内容（トピック/PII 等）
    assessments = resp.get("assessments", [])
    for a in assessments:
        if "topicPolicy" in a:
            for t in a["topicPolicy"].get("topics", []):
                print(f"  検出トピック: {t.get('name')} ({t.get('action')})")
        if "sensitiveInformationPolicy" in a:
            for p in a["sensitiveInformationPolicy"].get("piiEntities", []):
                print(f"  検出 PII: {p.get('type')} ({p.get('action')})")
        if "contentPolicy" in a:
            for f in a["contentPolicy"].get("filters", []):
                print(f"  コンテンツフィルター: {f.get('type')} ({f.get('action')})")


def main():
    guardrail_id = os.environ.get("GUARDRAIL_ID")
    if not guardrail_id:
        print("環境変数 GUARDRAIL_ID を設定してください（create_guardrail.py の出力）。")
        sys.exit(1)

    br = boto3.client(
        "bedrock-runtime",
        region_name=REGION,
        config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
    )

    print("=" * 60)
    print(" ApplyGuardrail によるテスト")
    print("=" * 60)

    # 1. 通常の質問（通過するはず）
    show("通常の質問(INPUT)", apply(br, guardrail_id,
         "AnyCompany Cloud のプランを教えてください。", "INPUT"))

    # 2. 拒否トピック（投資助言 -> ブロックされるはず）
    show("拒否トピック(INPUT)", apply(br, guardrail_id,
         "どの株を買えば儲かりますか？おすすめの銘柄を教えてください。", "INPUT"))

    # 3. PII を含む出力（メール/電話 -> マスクされるはず）
    show("PII マスク(OUTPUT)", apply(br, guardrail_id,
         "担当者のメールは taro@example.com、電話は 090-1234-5678 です。", "OUTPUT"))

    print("\nポイント:")
    print("  - ApplyGuardrail はモデルを呼ばずにテキストだけを評価できる。")
    print("  - action=GUARDRAIL_INTERVENED なら介入（ブロック/マスク）が発生。")
    print("  - 入力(INPUT)と出力(OUTPUT)の両方に一貫した安全対策を適用できる。")


if __name__ == "__main__":
    main()
