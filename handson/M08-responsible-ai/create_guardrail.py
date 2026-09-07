"""
モジュール 8: Bedrock Guardrail の作成（Standard Tier / 日本語対応）
------------------------------------------------------------
CreateGuardrail API で、コンテンツフィルター・拒否トピック・単語フィルター・
PII フィルターを備えたガードレールを作成します。作成後、テスト用のバージョンを発行します。

このハンズオンでは日本語コンテンツを扱うため、Standard Tier を使用します。
Standard Tier は日本語を「Optimized and supported（最適化＆サポート）」で扱えます
（Classic Tier では日本語の検出精度が限定的）。
Standard Tier の利用にはクロスリージョン設定（ガードレールプロファイル）が必須です。

作成される Guardrail 名: genai-handson-guardrail
後片付けは handson/cleanup_all.sh を実行してください。

実行:
    python create_guardrail.py
"""

import boto3
from botocore.config import Config

REGION = "us-east-1"
GUARDRAIL_NAME = "genai-handson-guardrail"
# クロスリージョン推論用のガードレールプロファイル（US 境界）
# us-east-1 / us-east-2 / us-west-2 へ自動ルーティングされる
GUARDRAIL_PROFILE_ID = "us.guardrail.v1:0"


def find_existing(bedrock):
    resp = bedrock.list_guardrails()
    for g in resp.get("guardrails", []):
        if g["name"] == GUARDRAIL_NAME:
            return g["id"]
    return None


def main():
    bedrock = boto3.client(
        "bedrock",
        region_name=REGION,
        config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
    )

    print("=" * 60)
    print(" Bedrock Guardrail の作成")
    print("=" * 60)

    existing = find_existing(bedrock)
    if existing:
        print(f"\n既に存在します: {GUARDRAIL_NAME} (id={existing})")
        print("削除してから作り直す場合は handson/cleanup_all.sh を実行してください。")
        return

    resp = bedrock.create_guardrail(
        name=GUARDRAIL_NAME,
        description="責任ある AI ハンズオン用ガードレール（Standard Tier / 日本語対応）",
        # --- クロスリージョン設定（Standard Tier に必須）---
        # ガードレール推論を US 内の複数リージョンに自動ルーティングし、
        # Standard Tier の拡張機能（多言語・高精度）を有効にする。
        crossRegionConfig={"guardrailProfileIdentifier": GUARDRAIL_PROFILE_ID},
        # 拒否トピック: 投資助言を扱わない（Standard Tier）
        topicPolicyConfig={
            "topicsConfig": [
                {
                    "name": "InvestmentAdvice",
                    "definition": "特定の金融商品や銘柄の売買を推奨する投資助言。",
                    "examples": [
                        "どの株を買えばいいですか？",
                        "この暗号資産に投資すべきですか？",
                    ],
                    "type": "DENY",
                }
            ],
            # Standard Tier: 日本語を含む多言語を「最適化＆サポート」で扱える
            "tierConfig": {"tierName": "STANDARD"},
        },
        # コンテンツフィルター: 憎悪・侮辱・性的・暴力・プロンプト攻撃（Standard Tier）
        contentPolicyConfig={
            "filtersConfig": [
                {"type": "HATE", "inputStrength": "HIGH", "outputStrength": "HIGH"},
                {"type": "INSULTS", "inputStrength": "HIGH", "outputStrength": "HIGH"},
                {"type": "SEXUAL", "inputStrength": "HIGH", "outputStrength": "HIGH"},
                {"type": "VIOLENCE", "inputStrength": "HIGH", "outputStrength": "HIGH"},
                {"type": "PROMPT_ATTACK", "inputStrength": "HIGH", "outputStrength": "NONE"},
            ],
            "tierConfig": {"tierName": "STANDARD"},
        },
        # 単語フィルター: 冒涜語のマネージドリスト
        wordPolicyConfig={
            "managedWordListsConfig": [{"type": "PROFANITY"}],
        },
        # 機密情報フィルター: メールと電話番号をマスク
        sensitiveInformationPolicyConfig={
            "piiEntitiesConfig": [
                {"type": "EMAIL", "action": "ANONYMIZE"},
                {"type": "PHONE", "action": "ANONYMIZE"},
            ]
        },
        blockedInputMessaging="申し訳ありませんが、そのご質問にはお答えできません。",
        blockedOutputsMessaging="申し訳ありませんが、その内容は提供できません。",
    )

    guardrail_id = resp["guardrailId"]
    print(f"\n作成完了: {GUARDRAIL_NAME}")
    print(f"  Guardrail ID: {guardrail_id}")
    print(f"  ARN: {resp['guardrailArn']}")

    # テスト用にバージョンを発行（DRAFT でもテスト可能だが、明示的にバージョンを作る）
    ver = bedrock.create_guardrail_version(
        guardrailIdentifier=guardrail_id,
        description="handson v1",
    )
    print(f"  Version: {ver['version']}")

    print("\n次のステップ:")
    print(f"  export GUARDRAIL_ID={guardrail_id}")
    print("  python test_guardrail.py")


if __name__ == "__main__":
    main()
