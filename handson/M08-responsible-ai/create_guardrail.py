"""
モジュール 8: Bedrock Guardrail の作成
------------------------------------------------------------
CreateGuardrail API で、コンテンツフィルター・拒否トピック・単語フィルター・
PII フィルターを備えたガードレールを作成します。作成後、テスト用のバージョンを発行します。

作成される Guardrail 名: genai-handson-guardrail
後片付けは handson/cleanup_all.sh を実行してください。

実行:
    python create_guardrail.py
"""

import boto3
from botocore.config import Config

REGION = "us-east-1"
GUARDRAIL_NAME = "genai-handson-guardrail"


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
        description="責任ある AI ハンズオン用ガードレール",
        # 拒否トピック: 投資助言を扱わない
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
            ]
        },
        # コンテンツフィルター: 憎悪・侮辱・性的・暴力・プロンプト攻撃
        contentPolicyConfig={
            "filtersConfig": [
                {"type": "HATE", "inputStrength": "HIGH", "outputStrength": "HIGH"},
                {"type": "INSULTS", "inputStrength": "HIGH", "outputStrength": "HIGH"},
                {"type": "SEXUAL", "inputStrength": "HIGH", "outputStrength": "HIGH"},
                {"type": "VIOLENCE", "inputStrength": "HIGH", "outputStrength": "HIGH"},
                {"type": "PROMPT_ATTACK", "inputStrength": "HIGH", "outputStrength": "NONE"},
            ]
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
