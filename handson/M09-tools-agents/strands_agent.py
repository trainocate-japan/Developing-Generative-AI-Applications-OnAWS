"""
モジュール 9: Strands Agents の基本
------------------------------------------------------------
Strands Agents SDK を使うと、@tool デコレーターで関数をツール化し、
ツール実行ループ（toolUse -> 実行 -> toolResult）をフレームワークが自動で回します。
tool_use_converse.py と同じことを、はるかに少ないコードで実現できます。

実行:
    python strands_agent.py
"""

REGION = "us-east-1"
MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"


def main():
    try:
        from strands import Agent, tool
        from strands.models import BedrockModel
    except ImportError:
        print("strands-agents が見つかりません。pip install strands-agents strands-agents-tools を実行してください。")
        return

    # @tool で関数をツール化（docstring と型ヒントがそのままツール仕様になる）
    @tool
    def get_weather(city: str) -> str:
        """指定した都市の現在の天気を返す。

        Args:
            city: 都市名（例: 東京）
        """
        dummy = {"東京": "晴れ、最高 28 度", "大阪": "曇り、最高 26 度", "札幌": "雨、最高 19 度"}
        return dummy.get(city, f"{city} の天気情報は取得できませんでした")

    @tool
    def get_stock_price(symbol: str) -> str:
        """指定したティッカーシンボルの株価を返す。

        Args:
            symbol: 銘柄シンボル（例: AMZN）
        """
        dummy = {"AMZN": "185.4 USD", "AAPL": "227.1 USD"}
        return dummy.get(symbol.upper(), f"{symbol} の株価は取得できませんでした")

    model = BedrockModel(model_id=MODEL_ID, region_name=REGION)
    agent = Agent(
        model=model,
        tools=[get_weather, get_stock_price],
        system_prompt="あなたは親切なアシスタントです。必要に応じてツールを使い、日本語で答えてください。",
    )

    print("=" * 60)
    print(" Strands Agents（ツール実行ループを自動化）")
    print("=" * 60)

    print("\n[user] AMZN の株価と、札幌の天気を教えてください。")
    response = agent("AMZN の株価と、札幌の天気を教えてください。")
    print(f"\n[assistant] {response}")

    print("\nポイント:")
    print("  - @tool で関数を宣言するだけ。toolConfig の手書きやループ処理は不要。")
    print("  - tool_use_converse.py と同じ動作を、少ないコードで実現できる。")
    print("  - Strands は『モデル駆動型』でエージェント構築を簡素化・高速化する。")


if __name__ == "__main__":
    main()
