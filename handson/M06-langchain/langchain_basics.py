"""
モジュール 6: LangChain から Amazon Bedrock を呼び出す（基本）
------------------------------------------------------------
langchain-aws の ChatBedrockConverse を使って基盤モデルを呼び出します。
内部では Bedrock の Converse API が使われます。

実行:
    python langchain_basics.py
"""

from langchain_aws import ChatBedrockConverse
from langchain_core.messages import HumanMessage, SystemMessage

REGION = "us-east-1"
MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"


def main():
    # ChatBedrockConverse: LangChain のチャットモデル抽象（内部で Converse API を使用）
    model = ChatBedrockConverse(
        model=MODEL_ID,
        region_name=REGION,
        max_tokens=300,      # maxTokens は必ず指定
        temperature=0.7,
    )

    print("=" * 60)
    print(" LangChain + Bedrock（ChatBedrockConverse）")
    print("=" * 60)

    messages = [
        SystemMessage("次の日本語を英語に翻訳してください。翻訳結果のみ出力してください。"),
        HumanMessage("私はプログラミングが大好きです。"),
    ]

    response = model.invoke(messages)

    print("\n入力: 私はプログラミングが大好きです。")
    print(f"出力: {response.content}")

    # usage_metadata でトークン数を確認できる
    if response.usage_metadata:
        print(f"\n[usage] {response.usage_metadata}")

    print("\nポイント: LangChain のメッセージ抽象（SystemMessage / HumanMessage）を")
    print("使いつつ、内部では Bedrock Converse API が呼ばれています。")


if __name__ == "__main__":
    main()
