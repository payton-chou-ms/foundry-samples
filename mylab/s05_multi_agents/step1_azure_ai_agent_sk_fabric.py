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
以下範例示範如何在 Semantic Kernel 中使用 Azure AI Agent 與 Microsoft Fabric 整合。
本範例建立一個具有資料倉儲和分析平台功能的 agent。
"""

# 新增 agent_id 變數 (需要先透過程式、Portal 或 CLI 建立 agent)
# agent_id = "<your-fabric-agent-id>"
agent_id = "asst_fabric_example_id"  # 請替換為實際的 agent ID

# 模擬與 Fabric agent 的對話
USER_INPUTS = [
    "建立一個新的資料湖並匯入客戶資料",
    "執行 Power BI 報表產生作業",
    "同步 OneLake 中的資料到資料倉儲",
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
        # 1. 根據 agent_id 取得 Fabric agent 定義
        # 將 "agent_id" 換成您要使用的實際 Fabric agent ID
        agent_definition = await client.agents.get_agent(
            agent_id=agent_id,
        )

        # 2. 建立 Semantic Kernel 對應的 Azure AI Agent (Fabric 專用)
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
                # 4. 以指定執行緒呼叫 Fabric agent 並串流回應
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
        # User: '建立一個新的資料湖並匯入客戶資料'
        # Agent: 正在連接 Microsoft Fabric 工作區...
        正在建立新的資料湖...
        客戶資料匯入至 OneLake 完成。
        
        # User: '執行 Power BI 報表產生作業'
        # Agent: 正在啟動 Power BI 服務...
        報表產生作業已完成，可於 Power BI Service 中查看。
        
        # User: '同步 OneLake 中的資料到資料倉儲'
        # Agent: 正在執行資料同步作業...
        OneLake 資料已成功同步至 Fabric 資料倉儲。
        """


if __name__ == "__main__":
    asyncio.run(main())