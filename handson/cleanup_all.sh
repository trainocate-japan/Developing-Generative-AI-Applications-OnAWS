#!/bin/bash
# =============================================================================
# Developing Generative AI Applications on AWS - 全リソース一括削除スクリプト
# 各モジュールのハンズオンで作成した AWS リソースを削除します。
# スクリプトは冪等です（存在しないリソースはスキップします）。
# =============================================================================

REGION="${AWS_REGION:-us-east-1}"

echo "=============================================="
echo " ハンズオンリソース クリーンアップ"
echo " リージョン: $REGION"
echo "=============================================="
echo ""
echo "  対象アカウント:"
aws sts get-caller-identity --query "Account" --output text
echo ""
read -r -p "  上記アカウントのリソースを削除します。続行しますか？ (y/N): " ANSWER
if [ "$ANSWER" != "y" ] && [ "$ANSWER" != "Y" ]; then
    echo "  中止しました。"
    exit 0
fi
echo ""

# =============================================================================
# M04 / M06: DynamoDB 会話履歴テーブル
# =============================================================================
echo "----------------------------------------------"
echo " [M04/M06] DynamoDB 会話履歴テーブルの削除"
echo "----------------------------------------------"
for TABLE in genai-handson-sessions genai-handson-conversation; do
    if aws dynamodb describe-table --table-name "$TABLE" --region "$REGION" >/dev/null 2>&1; then
        aws dynamodb delete-table --table-name "$TABLE" --region "$REGION" >/dev/null 2>&1 && \
            echo "  OK テーブル削除: $TABLE" || echo "  WARN テーブル削除失敗: $TABLE"
    else
        echo "  -- テーブルなし: $TABLE（スキップ）"
    fi
done
echo ""

# =============================================================================
# M05: Bedrock Knowledge Base
# =============================================================================
echo "----------------------------------------------"
echo " [M05] Bedrock Knowledge Base の削除"
echo "----------------------------------------------"
KB_ID=$(aws bedrock-agent list-knowledge-bases --region "$REGION" \
    --query "knowledgeBaseSummaries[?name=='genai-handson-kb'].knowledgeBaseId" \
    --output text 2>/dev/null || echo "")
if [ -n "$KB_ID" ] && [ "$KB_ID" != "None" ]; then
    # データソースを削除
    DS_IDS=$(aws bedrock-agent list-data-sources --knowledge-base-id "$KB_ID" --region "$REGION" \
        --query "dataSourceSummaries[].dataSourceId" --output text 2>/dev/null || echo "")
    for DS in $DS_IDS; do
        aws bedrock-agent delete-data-source --knowledge-base-id "$KB_ID" --data-source-id "$DS" --region "$REGION" >/dev/null 2>&1 && \
            echo "  OK データソース削除: $DS" || echo "  WARN データソース削除失敗: $DS"
    done
    aws bedrock-agent delete-knowledge-base --knowledge-base-id "$KB_ID" --region "$REGION" >/dev/null 2>&1 && \
        echo "  OK Knowledge Base 削除: $KB_ID" || echo "  WARN Knowledge Base 削除失敗: $KB_ID"
else
    echo "  -- Knowledge Base なし: genai-handson-kb（スキップ）"
fi
echo "   i OpenSearch Serverless コレクションを手動作成した場合は、コンソールから削除してください。"
echo ""

# =============================================================================
# M08: Bedrock Guardrail
# =============================================================================
echo "----------------------------------------------"
echo " [M08] Bedrock Guardrail の削除"
echo "----------------------------------------------"
GUARDRAIL_ID=$(aws bedrock list-guardrails --region "$REGION" \
    --query "guardrails[?name=='genai-handson-guardrail'].id" \
    --output text 2>/dev/null || echo "")
if [ -n "$GUARDRAIL_ID" ] && [ "$GUARDRAIL_ID" != "None" ]; then
    aws bedrock delete-guardrail --guardrail-identifier "$GUARDRAIL_ID" --region "$REGION" >/dev/null 2>&1 && \
        echo "  OK Guardrail 削除: $GUARDRAIL_ID" || echo "  WARN Guardrail 削除失敗: $GUARDRAIL_ID"
else
    echo "  -- Guardrail なし: genai-handson-guardrail（スキップ）"
fi
echo ""

# =============================================================================
# M10: Bedrock Flow
# =============================================================================
echo "----------------------------------------------"
echo " [M10] Bedrock Flow / AgentCore の削除"
echo "----------------------------------------------"
FLOW_ID=$(aws bedrock-agent list-flows --region "$REGION" \
    --query "flowSummaries[?name=='genai-handson-flow'].id" \
    --output text 2>/dev/null || echo "")
if [ -n "$FLOW_ID" ] && [ "$FLOW_ID" != "None" ]; then
    # エイリアスが残っていると Flow 削除が ConflictException で失敗するため、
    # 先にユーザー作成のエイリアスを削除する（テストエイリアス TSTALIASID は削除不可なので除外）
    ALIAS_IDS=$(aws bedrock-agent list-flow-aliases --flow-identifier "$FLOW_ID" --region "$REGION" \
        --query "flowAliasSummaries[?id!='TSTALIASID'].id" --output text 2>/dev/null || echo "")
    for AID in $ALIAS_IDS; do
        aws bedrock-agent delete-flow-alias --flow-identifier "$FLOW_ID" --alias-identifier "$AID" --region "$REGION" >/dev/null 2>&1 && \
            echo "  OK Flow エイリアス削除: $AID" || echo "  WARN Flow エイリアス削除失敗: $AID"
    done
    aws bedrock-agent delete-flow --flow-identifier "$FLOW_ID" --region "$REGION" >/dev/null 2>&1 && \
        echo "  OK Flow 削除: $FLOW_ID" || echo "  WARN Flow 削除失敗: $FLOW_ID"
else
    echo "  -- Flow なし: genai-handson-flow（スキップ）"
fi
# Flows 実行ロールの削除
if aws iam get-role --role-name GenAIHandsonFlowsRole >/dev/null 2>&1; then
    aws iam detach-role-policy --role-name GenAIHandsonFlowsRole \
        --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess >/dev/null 2>&1 || true
    aws iam delete-role --role-name GenAIHandsonFlowsRole >/dev/null 2>&1 && \
        echo "  OK IAM ロール削除: GenAIHandsonFlowsRole" || echo "  WARN IAM ロール削除失敗: GenAIHandsonFlowsRole"
else
    echo "  -- IAM ロールなし: GenAIHandsonFlowsRole（スキップ）"
fi
echo "  i AgentCore Runtime を 'agentcore' CLI でデプロイした場合は、以下で削除してください:"
echo "     agentcore destroy   （または AWS コンソール → Bedrock AgentCore → Runtime）"
echo ""

echo "=============================================="
echo " クリーンアップ完了!"
echo "=============================================="
echo ""
echo "  以下は手動確認を推奨します:"
echo "  - M05: OpenSearch Serverless コレクション / IAM ロール"
echo "  - M10: AgentCore Runtime / ECR リポジトリ"
