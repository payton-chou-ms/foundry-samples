# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_fabric.py

DESCRIPTION:
    This sample demonstrates how to use Agent operations with the Microsoft Fabric grounding tool from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_fabric.py

    Before running the sample:

    pip install azure-identity
    pip install --pre azure-ai-projects

    Set this environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) FABRIC_CONNECTION_NAME  - The name of a connection to the Microsoft Fabric resource as it is
       listed in Azure AI Foundry connected resources.
"""

import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import FabricTool, ListSortOrder

# Load environment variables from .env file
load_dotenv()

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# [START create_agent_with_fabric_tool]
conn_id = project_client.connections.get(os.environ["FABRIC_CONNECTION_NAME"]).id

print(conn_id)

# Initialize an Agent Fabric tool and add the connection id
fabric = FabricTool(connection_id=conn_id)

# Create an Agent with the Fabric tool and process an Agent run
with project_client:
    agents_client = project_client.agents

    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="""你是一位資料分析協作代理（Analysis Orchestrator Agent）。你的唯一資料來源是「Data Agent 工具」。你的任務是：
1) 讀取使用者的商業問題，
2) 將問題轉換為清晰、可執行的資料查詢請求，
3) 透過 Data Agent 工具發送查詢（不得自行杜撰數據），
4) 將 Data Agent 的回覆整理為易讀的結論、表格與重點洞察，必要時提出後續分析建議。

【行為原則】
- 僅以 Data Agent 的回覆為準；嚴禁臆測或補造資料。
- 在提出洞察前，先標示主要指標（如總量、平均、最大/最小、趨勢方向）。
- 若使用者需求不完整（缺少時間範圍、地域或指標），請主動用 1~2 個精準問題澄清，或先用合理預設（例如「最近 30 天」、「按月彙整」、「Top 10 區域」）並在回覆中註明假設。
- 遇到過大結果集時，預設回傳前 20 筆，並提供「展開更多」選項。
- 對於異常/極端值：標記可能原因（如節慶、促銷、天氣、停電），並提出下一步分析建議（例如切片、比對前後 7 天）。
- 嚴格避免暴露內部推理內容；只輸出結論、方法與可驗證的依據。

【輸出格式】
- 先給「結論摘要（3~5 點）」，再給「主要指標表格」，最後給「後續建議」。
- 需要圖表時，回傳結構化規格（如 Vega-Lite）或清楚的圖表需求（X/Y 軸、度量、分組）。
- 如資料不足，明確說明缺口與所需補充的欄位/維度。

【工具使用策略】
- 所有數據、趨勢、比較、異常偵測，均需透過 Data Agent 工具完成。
- 每次查詢前先縮小範圍（時間/地域/車種/駕駛等），必要時分步查詢再彙整。
- 對於「最大/最小/Top-N」類問題，務必指定排序欄位與時間窗，並回傳對應樣本（行程編號/時間/地點）供稽核。
- 回傳金額或比率時，標明單位與小數位（預設兩位）。

【語言】
- 使用繁體中文回覆使用者；欄位名保留原始命名（必要時在括號附中文註解）。
""",
        tools=fabric.definitions,
    )
    # [END create_agent_with_fabric_tool]
    print(f"Created Agent, ID: {agent.id}")

    # Create thread for communication
    thread = agents_client.threads.create()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = agents_client.messages.create(
        thread_id=thread.id,
        role="user",
        content="平日與假日的每小時叫車分布，找出尖峰時段",
    )
    print(f"Created message, ID: {message.id}")

    # Create and process an Agent run in thread with tools
    run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Delete the Agent when done
    agents_client.delete_agent(agent.id)
    print("Deleted agent")

    # Fetch and log all messages
    messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    for msg in messages:
        if msg.text_messages:
            last_text = msg.text_messages[-1]
            print(f"{msg.role}: {last_text.text.value}")
