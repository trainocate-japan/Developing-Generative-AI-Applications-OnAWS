"""
モジュール 4: 会話メモリの追加（インメモリ + DynamoDB 永続化）
------------------------------------------------------------
会話パターンでは、過去のやり取りを messages に積み重ねてコンテキストを維持します。
さらに DynamoDB に履歴を保存すれば、別セッションからも会話を復元できます。

使い方:
    python conversation_memory.py            # インメモリのみ（DynamoDB 不要）
    python conversation_memory.py --dynamodb # DynamoDB に履歴を永続化

DynamoDB モードは genai-handson-conversation テーブルを自動作成します。
後片付けは handson/cleanup_all.sh を実行してください。
"""

import sys
import time
import boto3
from boto3.dynamodb.conditions import Key
from botocore.config import Config

REGION = "us-east-1"
MODEL_ID = "us.amazon.nova-lite-v1:0"
TABLE_NAME = "genai-handson-conversation"
SESSION_ID = "demo-session-001"

SYSTEM = "あなたは親切なカスタマーサポート担当です。簡潔に日本語で答えてください。"


def chat_once(br, messages):
    """会話履歴 messages 全体を渡して 1 ターン応答する"""
    resp = br.converse(
        modelId=MODEL_ID,
        messages=messages,
        system=[{"text": SYSTEM}],
        inferenceConfig={"maxTokens": 300, "temperature": 0.5},
    )
    return resp["output"]["message"]["content"][0]["text"].strip()


# ---------- DynamoDB 永続化ヘルパー ----------
def ensure_table(ddb):
    existing = ddb.meta.client.list_tables()["TableNames"]
    if TABLE_NAME in existing:
        return ddb.Table(TABLE_NAME)
    print(f"  DynamoDB テーブル作成中: {TABLE_NAME} ...")
    table = ddb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[
            {"AttributeName": "session_id", "KeyType": "HASH"},
            {"AttributeName": "turn", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "session_id", "AttributeType": "S"},
            {"AttributeName": "turn", "AttributeType": "N"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    table.wait_until_exists()
    print("  作成完了")
    return table


def save_turn(table, turn, role, text):
    table.put_item(Item={
        "session_id": SESSION_ID, "turn": turn, "role": role,
        "text": text, "ts": int(time.time()),
    })


def load_history(table):
    resp = table.query(
        KeyConditionExpression=Key("session_id").eq(SESSION_ID),
    )
    items = sorted(resp.get("Items", []), key=lambda x: int(x["turn"]))
    return [{"role": i["role"], "content": [{"text": i["text"]}]} for i in items]


def main():
    use_ddb = "--dynamodb" in sys.argv

    br = boto3.client(
        "bedrock-runtime",
        region_name=REGION,
        config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
    )

    print("=" * 60)
    print(f" 会話メモリのデモ（{'DynamoDB 永続化' if use_ddb else 'インメモリ'}）")
    print("=" * 60)

    table = None
    messages = []
    turn = 0

    if use_ddb:
        ddb = boto3.resource("dynamodb", region_name=REGION)
        table = ensure_table(ddb)
        messages = load_history(table)
        turn = len(messages)
        if messages:
            print(f"  既存の履歴 {turn} 件を DynamoDB から復元しました。")

    # 会話を 2 往復する。2 つ目の質問は代名詞（それ）で 1 つ目を参照する
    user_turns = [
        "シアトルで一番おすすめの観光スポットを 1 つ教えてください。",
        "そこは子ども連れでも楽しめますか？",
    ]

    for user_text in user_turns:
        print(f"\n[user] {user_text}")
        messages.append({"role": "user", "content": [{"text": user_text}]})
        if table is not None:
            save_turn(table, turn, "user", user_text); turn += 1

        answer = chat_once(br, messages)
        print(f"[assistant] {answer}")
        messages.append({"role": "assistant", "content": [{"text": answer}]})
        if table is not None:
            save_turn(table, turn, "assistant", answer); turn += 1

    print("\nポイント:")
    print("  - 2 つ目の質問『そこは...』が、1 つ目の観光スポットを指せているのは")
    print("    過去のやり取りを messages に積み重ねているためです（会話メモリ）。")
    if use_ddb:
        print("  - DynamoDB に保存したので、再実行すると履歴が復元されます。")
        print("  - 後片付け: handson/cleanup_all.sh")
    else:
        print("  - --dynamodb を付けると履歴を DynamoDB に永続化できます。")


if __name__ == "__main__":
    main()
