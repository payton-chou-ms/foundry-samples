# Copyright (c) Microsoft. All rights reserved.

import asyncio

from azure.identity.aio import DefaultAzureCredential

from semantic_kernel.agents import AzureAIAgent, AzureAIAgentThread
from semantic_kernel.contents import (
    ChatMessageContent,
    FunctionCallContent,
    FunctionResultContent,
)

"""
以下範例示範如何在 Semantic Kernel 中使用 Azure AI Agent 與 Databricks 整合。
本範例建立一個具有資料分析和處理能力的 agent。
"""

# 新增 agent_id 變數 (需要先透過程式、Portal 或 CLI 建立 agent)
# agent_id = "<your-databricks-agent-id>"
agent_id = "asst_databricks_example_id"  # 請替換為實際的 agent ID

# 模擬與 Databricks agent 的對話
USER_INPUTS = [
    "請幫我分析銷售數據並產生月度報告",
    "執行 ETL 流程處理客戶資料",
]


async def handle_streaming_intermediate_steps(message: ChatMessageContent) -> None:
    """處理串流中的中間步驟，包括函數呼叫和結果"""
    for item in message.items or []:
        if isinstance(item, FunctionResultContent):
            print(f"Function Result:> {item.result} for function: {item.name}")
        elif isinstance(item, FunctionCallContent):
            print(f"Function Call:> {item.name} with arguments: {item.arguments}")
        else:
            print(f"{item}")


async def main() -> None:
    async with (
        DefaultAzureCredential() as creds,
        AzureAIAgent.create_client(credential=creds) as client,
    ):
        # 1. 根據 agent_id 取得 Databricks agent 定義
        # 將 "agent_id" 換成您要使用的實際 Databricks agent ID
        agent_definition = await client.agents.get_agent(
            agent_id=agent_id,
        )

        # 2. 建立 Semantic Kernel 對應的 Azure AI Agent (Databricks 專用)
        agent = AzureAIAgent(
            client=client,
            definition=agent_definition,
        )

        # 3. 建立 agent 對話執行緒
        # 若未提供執行緒，系統將建立並回傳含初始回應的新執行緒
        thread: AzureAIAgentThread = None

        try:
            for user_input in USER_INPUTS:
                print(f"# User: '{user_input}'")
                # 4. 以指定執行緒呼叫 Databricks agent 並串流回應
                async for response in agent.invoke_stream(
                    messages=user_input,
                    thread=thread,
                    on_intermediate_message=handle_streaming_intermediate_steps,
                ):
                    # Print the agent's response
                    print(f"{response}", end="", flush=True)
                    # Update the thread for subsequent messages
                    thread = response.thread
                print("\n" + "=" * 50 + "\n")
        finally:
            # 5. 清理資源：刪除執行緒
            # 不刪除 agent，以便重複使用
            await thread.delete() if thread else None
            # Do not clean up the agent so it can be used again

        """
        範例輸出：
        # User: '請幫我分析銷售數據並產生月度報告'
        # Agent: 正在連接 Databricks 工作區...
        正在執行銷售數據分析查詢...
        已產生月度銷售報告，包含趨勢分析和預測。
        
        # User: '執行 ETL 流程處理客戶資料'
        # Agent: 正在啟動 Databricks ETL 管道...
        客戶資料清理和轉換已完成。
        """


if __name__ == "__main__":
    asyncio.run(main())