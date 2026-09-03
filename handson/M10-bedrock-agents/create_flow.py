"""
モジュール 10: Amazon Bedrock Flows をプログラムで作成・実行
------------------------------------------------------------
入力(Input) -> プロンプト(Prompt) -> 出力(Output) の最小フローを作成します。
Flows は制御可能な生成 AI ワークフローをノード接続で構築する機能です。
（コンソールのビジュアルビルダーでも同じことができます）

作成される Flow 名: genai-handson-flow
後片付けは handson/cleanup_all.sh を実行してください。

前提: Flows 実行用の IAM ロールが必要です（steps.md を参照）。
    export FLOWS_ROLE_ARN=arn:aws:iam::<ACCOUNT_ID>:role/<FlowsRole>

実行:
    python create_flow.py
"""

import os
import sys
import time
import boto3
from botocore.config import Config

REGION = "us-east-1"
FLOW_NAME = "genai-handson-flow"
# プロンプトノードで使うモデル（推論プロファイル）
MODEL_ID = "us.amazon.nova-lite-v1:0"


def build_definition():
    """input -> prompt -> output のノードと接続を定義する"""
    input_node = {
        "type": "Input",
        "name": "FlowInput",
        "outputs": [{"name": "document", "type": "String"}],
    }
    prompt_node = {
        "type": "Prompt",
        "name": "GenApp",
        "configuration": {
            "prompt": {
                "sourceConfiguration": {
                    "inline": {
                        "modelId": MODEL_ID,
                        "templateType": "TEXT",
                        "inferenceConfiguration": {"text": {"maxTokens": 300, "temperature": 0.5}},
                        "templateConfiguration": {
                            "text": {
                                "text": "次のトピックについて、初心者向けに 3 文で説明してください:\n{{topic}}",
                                "inputVariables": [{"name": "topic"}],
                            }
                        },
                    }
                }
            }
        },
        "inputs": [{"name": "topic", "type": "String", "expression": "$.data"}],
        "outputs": [{"name": "modelCompletion", "type": "String"}],
    }
    output_node = {
        "type": "Output",
        "name": "FlowOutput",
        "inputs": [{"name": "document", "type": "String", "expression": "$.data"}],
    }
    connections = [
        {
            "name": "InputToPrompt",
            "source": "FlowInput",
            "target": "GenApp",
            "type": "Data",
            "configuration": {"data": {"sourceOutput": "document", "targetInput": "topic"}},
        },
        {
            "name": "PromptToOutput",
            "source": "GenApp",
            "target": "FlowOutput",
            "type": "Data",
            "configuration": {"data": {"sourceOutput": "modelCompletion", "targetInput": "document"}},
        },
    ]
    return {"nodes": [input_node, prompt_node, output_node], "connections": connections}


def main():
    role_arn = os.environ.get("FLOWS_ROLE_ARN")
    if not role_arn:
        print("環境変数 FLOWS_ROLE_ARN を設定してください（steps.md のロール作成を参照）。")
        sys.exit(1)

    cfg = Config(retries={"max_attempts": 5, "mode": "adaptive"})
    agent = boto3.client("bedrock-agent", region_name=REGION, config=cfg)
    runtime = boto3.client("bedrock-agent-runtime", region_name=REGION, config=cfg)

    print("=" * 60)
    print(" Amazon Bedrock Flows の作成と実行")
    print("=" * 60)

    # 1. フロー作成
    resp = agent.create_flow(
        name=FLOW_NAME,
        description="ハンズオン用の最小フロー（input -> prompt -> output）",
        executionRoleArn=role_arn,
        definition=build_definition(),
    )
    flow_id = resp["id"]
    print(f"\nFlow 作成: {flow_id}")

    # 2. 準備（Prepare）してバージョン/エイリアスを作成
    agent.prepare_flow(flowIdentifier=flow_id)
    # Prepare 完了を待つ
    for _ in range(30):
        status = agent.get_flow(flowIdentifier=flow_id)["status"]
        if status == "Prepared":
            break
        time.sleep(2)
    print(f"Flow ステータス: {status}")

    ver = agent.create_flow_version(flowIdentifier=flow_id)["version"]
    alias = agent.create_flow_alias(
        flowIdentifier=flow_id, name="live",
        routingConfiguration=[{"flowVersion": ver}],
    )["id"]
    print(f"Version: {ver} / Alias: {alias}")

    # 3. フロー実行
    print("\nフローを実行: topic='検索拡張生成 (RAG)'")
    exec_resp = runtime.invoke_flow(
        flowIdentifier=flow_id,
        flowAliasIdentifier=alias,
        inputs=[{
            "content": {"document": "検索拡張生成 (RAG)"},
            "nodeName": "FlowInput",
            "nodeOutputName": "document",
        }],
    )
    for event in exec_resp["responseStream"]:
        if "flowOutputEvent" in event:
            print("\n出力:")
            print(f"  {event['flowOutputEvent']['content']['document']}")

    print(f"\n作成したリソース: Flow={flow_id}（後片付け: handson/cleanup_all.sh）")


if __name__ == "__main__":
    main()
