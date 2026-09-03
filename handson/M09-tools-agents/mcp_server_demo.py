"""
モジュール 9: MCP サーバー（デモ用）
------------------------------------------------------------
Model Context Protocol (MCP) のサーバー例です。天気ツールを 1 つ公開します。
このファイルは mcp_client_demo.py から stdio 経由で起動されます（直接実行しません）。

必要: pip install "mcp[cli]"
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather-demo")


@mcp.tool()
def get_weather(city: str) -> str:
    """指定した都市の現在の天気を返す。"""
    dummy = {"東京": "晴れ、最高 28 度", "大阪": "曇り、最高 26 度", "札幌": "雨、最高 19 度"}
    return dummy.get(city, f"{city} の天気情報は取得できませんでした")


if __name__ == "__main__":
    # stdio トランスポートで起動（クライアントがサブプロセスとして実行）
    mcp.run(transport="stdio")
