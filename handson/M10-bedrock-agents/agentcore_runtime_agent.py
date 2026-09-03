"""
モジュール 10: AgentCore Runtime 用エージェント
------------------------------------------------------------
Strands で作ったエージェントを Amazon Bedrock AgentCore Runtime に
デプロイするためのエントリポイントです。BedrockAgentCoreApp の
@app.entrypoint がリクエストを受け取り、エージェントを呼び出します。

ローカルテスト:
    python agentcore_runtime_agent.py            # ローカルで HTTP サーバー起動（app.run）
デプロイ（AgentCore CLI 使用。steps.md 参照）:
    agentcore configure --entrypoint agentcore_runtime_agent.py
    agentcore launch
    agentcore invoke '{"prompt": "AMZN の株価は？"}'
"""

MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel

app = BedrockAgentCoreApp()


@tool
def get_stock_price(symbol: str) -> str:
    """指定したティッカーシンボルの株価を返す。

    Args:
        symbol: 銘柄シンボル（例: AMZN）
    """
    dummy = {"AMZN": "185.4 USD", "AAPL": "227.1 USD"}
    return dummy.get(symbol.upper(), f"{symbol} の株価は取得できませんでした")


model = BedrockModel(model_id=MODEL_ID)
agent = Agent(
    model=model,
    tools=[get_stock_price],
    system_prompt="あなたは株式リサーチアシスタントです。必要に応じてツールを使い、日本語で簡潔に答えてください。",
)


@app.entrypoint
def invoke(payload):
    """AgentCore Runtime のエントリポイント。payload からプロンプトを取り出して応答する。"""
    user_input = payload.get("prompt", "こんにちは")
    result = agent(user_input)
    return result.message["content"][0]["text"]


if __name__ == "__main__":
    # ローカル実行時は HTTP サーバーを起動（デプロイ時は AgentCore が管理）
    app.run()
