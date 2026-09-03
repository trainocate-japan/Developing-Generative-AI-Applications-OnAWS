"""
モジュール 9: Converse API のツール使用（関数呼び出し）
------------------------------------------------------------
Converse API の toolConfig にツール定義を渡し、モデルが「どのツールを、どの引数で
呼ぶべきか」を判断します。アプリ側で実際に関数を実行し、結果 (toolResult) を
モデルに返して最終回答を得る、という「ツール実行ループ」を実装します。

このパターンはフレームワーク非依存で、エージェントの基礎になります。

実行:
    python tool_use_converse.py
"""

import boto3
from botocore.config import Config

REGION = "us-east-1"
MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"


# ------- 実際のツール（ここではダミー実装）-------
def get_weather(city: str) -> str:
    dummy = {"東京": "晴れ、最高 28 度", "大阪": "曇り、最高 26 度", "札幌": "雨、最高 19 度"}
    return dummy.get(city, f"{city} の天気情報は取得できませんでした")


def get_stock_price(symbol: str) -> str:
    dummy = {"AMZN": "185.4 USD", "AAPL": "227.1 USD"}
    return dummy.get(symbol.upper(), f"{symbol} の株価は取得できませんでした")


TOOL_FUNCS = {"get_weather": get_weather, "get_stock_price": get_stock_price}

# ------- モデルに渡すツール定義 -------
TOOL_CONFIG = {
    "tools": [
        {
            "toolSpec": {
                "name": "get_weather",
                "description": "指定した都市の現在の天気を返す",
                "inputSchema": {"json": {
                    "type": "object",
                    "properties": {"city": {"type": "string", "description": "都市名（例: 東京）"}},
                    "required": ["city"],
                }},
            }
        },
        {
            "toolSpec": {
                "name": "get_stock_price",
                "description": "指定したティッカーシンボルの株価を返す",
                "inputSchema": {"json": {
                    "type": "object",
                    "properties": {"symbol": {"type": "string", "description": "銘柄シンボル（例: AMZN）"}},
                    "required": ["symbol"],
                }},
            }
        },
    ]
}


def run(br, user_text: str):
    print(f"\n[user] {user_text}")
    messages = [{"role": "user", "content": [{"text": user_text}]}]

    # ツール実行ループ（モデルがツールを要求しなくなるまで繰り返す）
    while True:
        resp = br.converse(
            modelId=MODEL_ID,
            messages=messages,
            toolConfig=TOOL_CONFIG,
            inferenceConfig={"maxTokens": 500, "temperature": 0.2},
        )
        output_msg = resp["output"]["message"]
        messages.append(output_msg)

        if resp.get("stopReason") == "tool_use":
            # モデルがツール呼び出しを要求 -> 実行して結果を返す
            tool_results = []
            for block in output_msg["content"]:
                if "toolUse" in block:
                    tu = block["toolUse"]
                    name = tu["name"]
                    args = tu["input"]
                    print(f"  [toolUse] {name}({args})")
                    result_text = TOOL_FUNCS[name](**args)
                    print(f"  [result] {result_text}")
                    tool_results.append({
                        "toolResult": {
                            "toolUseId": tu["toolUseId"],
                            "content": [{"text": result_text}],
                        }
                    })
            messages.append({"role": "user", "content": tool_results})
        else:
            # ツール不要 -> 最終回答
            final = "".join(b.get("text", "") for b in output_msg["content"])
            print(f"[assistant] {final}")
            break


def main():
    br = boto3.client(
        "bedrock-runtime",
        region_name=REGION,
        config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
    )

    print("=" * 60)
    print(" Converse API のツール使用（関数呼び出し）")
    print("=" * 60)

    run(br, "東京の天気を教えてください。")
    run(br, "AMZN の株価と、札幌の天気を教えてください。")

    print("\nポイント:")
    print("  - モデルは『どのツールを呼ぶか』を判断するだけ。実行はアプリ側の責務。")
    print("  - toolUse -> 実行 -> toolResult -> 最終回答、というループが基本。")
    print("  - この仕組みを抽象化したのが Strands などのエージェントフレームワーク。")


if __name__ == "__main__":
    main()
