"""
モジュール 6: LangChain のチェーン（プロンプト | モデル | パーサー）
------------------------------------------------------------
ChatPromptTemplate とモデル、出力パーサーを LCEL（|）で連結します。
プロンプトのプレースホルダーに値を差し込むだけで、再利用可能なパイプラインになります。

実行:
    python langchain_chain.py
"""

from langchain_aws import ChatBedrockConverse
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

REGION = "us-east-1"
MODEL_ID = "us.amazon.nova-lite-v1:0"


def main():
    model = ChatBedrockConverse(
        model=MODEL_ID,
        region_name=REGION,
        max_tokens=200,
        temperature=0.3,
    )

    # プロンプトテンプレート（{language} と {text} を差し込む）
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", "次の英語を {language} に翻訳してください。翻訳結果のみ出力してください。"),
            ("user", "{text}"),
        ]
    )

    # LCEL: プロンプト | モデル | 文字列パーサー を連結してチェーンを作る
    chain = prompt_template | model | StrOutputParser()

    print("=" * 60)
    print(" LangChain チェーン（prompt | model | parser）")
    print("=" * 60)

    for language in ["日本語", "イタリア語", "フランス語"]:
        result = chain.invoke({"language": language, "text": "Hello, how are you today?"})
        print(f"\n[{language}] {result}")

    print("\nポイント: 同じチェーンに language を差し替えるだけで、")
    print("複数言語の翻訳パイプラインを再利用できます。")


if __name__ == "__main__":
    main()
