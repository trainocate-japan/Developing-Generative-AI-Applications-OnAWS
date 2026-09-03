"""
モジュール 6: LangChain の会話メモリ（DynamoDB 永続化）
------------------------------------------------------------
RunnableWithMessageHistory と DynamoDBChatMessageHistory を使い、
チャット履歴を DynamoDB に保存します。session_id ごとに履歴が管理され、
セッションを跨いで会話を継続できます。

DynamoDB テーブル genai-handson-sessions を自動作成します。
後片付けは handson/cleanup_all.sh を実行してください。

実行:
    python langchain_memory.py
"""

import boto3
from langchain_aws import ChatBedrockConverse
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import DynamoDBChatMessageHistory

REGION = "us-east-1"
MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
TABLE_NAME = "genai-handson-sessions"
SESSION_ID = "user-alice"


def ensure_table():
    """DynamoDBChatMessageHistory 用のテーブル（パーティションキー: SessionId）を作成する"""
    ddb = boto3.resource("dynamodb", region_name=REGION)
    existing = ddb.meta.client.list_tables()["TableNames"]
    if TABLE_NAME in existing:
        return
    print(f"  DynamoDB テーブル作成中: {TABLE_NAME} ...")
    table = ddb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[{"AttributeName": "SessionId", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "SessionId", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    table.wait_until_exists()
    print("  作成完了")


def get_history(session_id: str) -> DynamoDBChatMessageHistory:
    """session_id に対応する DynamoDB バックエンドの履歴を返す"""
    return DynamoDBChatMessageHistory(
        table_name=TABLE_NAME,
        session_id=session_id,
        region_name=REGION,
    )


def main():
    ensure_table()

    model = ChatBedrockConverse(
        model=MODEL_ID, region_name=REGION, max_tokens=300, temperature=0.5
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "あなたは親切なアシスタントです。日本語で簡潔に答えてください。"),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),
        ]
    )

    chain = prompt | model

    # チェーンに会話履歴機能を付与（session_id で履歴を出し入れ）
    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_history,
        input_messages_key="question",
        history_messages_key="history",
    )

    config = {"configurable": {"session_id": SESSION_ID}}

    print("=" * 60)
    print(" LangChain 会話メモリ（DynamoDB 永続化）")
    print("=" * 60)

    q1 = "こんにちは。私の名前はアリスです。"
    print(f"\n[user] {q1}")
    r1 = chain_with_history.invoke({"question": q1}, config=config)
    print(f"[assistant] {r1.content}")

    q2 = "私の名前を覚えていますか？"
    print(f"\n[user] {q2}")
    r2 = chain_with_history.invoke({"question": q2}, config=config)
    print(f"[assistant] {r2.content}")

    print("\nポイント:")
    print("  - 2 つ目の質問で名前を答えられるのは、DynamoDB に保存した履歴を")
    print("    RunnableWithMessageHistory が自動で読み込んでいるためです。")
    print("  - 再実行しても履歴が残ります。後片付けは handson/cleanup_all.sh。")


if __name__ == "__main__":
    main()
