"""
モジュール 9: MCP クライアントデモ
------------------------------------------------------------
Model Context Protocol (MCP) クライアントとして、mcp_server_demo.py を
stdio 経由で起動し、公開ツールの一覧取得とツール呼び出しを行います。

MCP は「ツールへの統一アクセス」を提供する標準プロトコルで、
エージェントごとにカスタム API を作らずにツールを接続できます。

必要: pip install "mcp[cli]"

実行:
    python mcp_client_demo.py
"""

import asyncio
import os
import sys


async def run():
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError:
        print('mcp が見つかりません。pip install "mcp[cli]" を実行してください。')
        return

    server_path = os.path.join(os.path.dirname(__file__), "mcp_server_demo.py")
    # 同じ Python インタプリタで MCP サーバーを子プロセスとして起動
    server_params = StdioServerParameters(command=sys.executable, args=[server_path])

    print("=" * 60)
    print(" MCP クライアントデモ")
    print("=" * 60)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1. 公開されているツールを一覧取得
            tools = await session.list_tools()
            print("\n公開ツール:")
            for t in tools.tools:
                print(f"  - {t.name}: {t.description}")

            # 2. ツールを呼び出す
            print("\nツール呼び出し: get_weather(city='東京')")
            result = await session.call_tool("get_weather", {"city": "東京"})
            for c in result.content:
                if getattr(c, "type", None) == "text":
                    print(f"  結果: {c.text}")

    print("\nポイント:")
    print("  - MCP はサーバー/クライアントの標準アーキテクチャでツールを抽象化する。")
    print("  - エージェントは MCP 経由でツールを検出・利用でき、カスタム API 実装が不要。")
    print("  - 本番では AgentCore Gateway が API/Lambda を MCP ツールに変換できる（M10）。")


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
