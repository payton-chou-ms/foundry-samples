# Copyright (c) Microsoft. All rights reserved.

import asyncio
import time
from semantic_kernel.agents import MagenticOrchestration, StandardMagenticManager
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatMessageContent
from config.settings import settings
from utils import display_task_info
from utils.timeout_manager import TimeoutManager


class MagenticOrchestrator:
    """Magentic 編排器 - 負責管理多代理程式的協作"""
    
    def __init__(self, agents_list, response_timeout=60, max_iterations=10):
        self.agents_list = agents_list
        self.orchestration = None
        self.runtime = None
        self.response_timeout = response_timeout  # 響應超時時間（秒）
        self.max_iterations = max_iterations      # 最大迭代次數
        self.current_responses = 0                # 當前響應計數
        self.start_time = None                    # 開始時間
        
        # 創建編排
        self._create_orchestration()
    
    def _create_orchestration(self):
        """創建 Magentic 編排"""
        self.orchestration = MagenticOrchestration(
            members=self.agents_list,
            manager=StandardMagenticManager(
                chat_completion_service=AzureChatCompletion(
                    endpoint=settings.AZURE_OPENAI_ENDPOINT,
                )
            ),
            agent_response_callback=self._agent_response_callback,
        )
    
    def _agent_response_callback(self, message: ChatMessageContent) -> None:
        """觀察函數，用於列印來自代理程式的訊息"""
        self.current_responses += 1
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        
        # 只顯示重要的響應，避免過多輸出
        if self.current_responses <= self.max_iterations:
            print(f"\n**{message.name}** (回應 #{self.current_responses}, 耗時: {elapsed_time:.1f}s)")
            # 限制內容長度，避免過長輸出
            content = message.content or ""
            if len(content) > 200:
                content = content[:200] + "..."
            print(f"{content}")
            print("-" * 60)
        elif self.current_responses == self.max_iterations + 1:
            print(f"\n⚠️ 已達到最大響應次數 ({self.max_iterations})，將等待最終結果...")
            print("-" * 60)
    
    async def start_runtime(self):
        """啟動運行時"""
        self.runtime = InProcessRuntime()
        self.runtime.start()
        print("✅ 多代理程式運行時已啟動")
    
    async def stop_runtime(self):
        """停止運行時"""
        if self.runtime:
            await self.runtime.stop_when_idle()
            print("✅ 運行時已停止")
    
    async def process_query(self, query: str, query_type: str = "multi_agent") -> bool:
        """處理使用者查詢"""
        try:
            # 根據查詢類型調整超時時間
            adaptive_timeout = min(self.response_timeout, TimeoutManager.get_recommended_timeout(query_type))
            
            # 重置計數器
            self.current_responses = 0
            self.start_time = time.time()
            
            display_task_info(query, query_type, adaptive_timeout)
            print(f"⏱️ 設定響應超時: {adaptive_timeout} 秒")
            print(f"🔄 最大響應次數: {self.max_iterations}")
            print("=" * 60)
            
            # 呼叫編排，使用自適應超時
            orchestration_result = await TimeoutManager.with_progress(
                self.orchestration.invoke(
                    task=query,
                    runtime=self.runtime,
                ),
                f"正在處理 {query_type} 查詢",
                adaptive_timeout
            )

            # 等待並展示結果，也設定超時
            print("\n🔍 正在等待最終結果...")
            final_result = await asyncio.wait_for(
                orchestration_result.get(),
                timeout=min(30, adaptive_timeout // 2)  # 最終結果的超時時間較短
            )

            elapsed_time = time.time() - self.start_time
            print("\n" + "=" * 60)
            print("🎯 **最終結果**")
            print("=" * 60)
            print(f"⏱️ 總耗時: {elapsed_time:.1f} 秒")
            print(f"📊 總響應次數: {self.current_responses}")
            print(f"🏷️ 查詢類型: {query_type}")
            print("-" * 60)
            print(f"{final_result}")
            print("=" * 60)
            
            return True
            
        except asyncio.TimeoutError:
            elapsed_time = time.time() - self.start_time if self.start_time else 0
            print(f"\n⏰ **查詢超時** (耗時: {elapsed_time:.1f} 秒)")
            print("=" * 60)
            print("可能的原因:")
            print("• 代理程式處理時間過長")
            print("• 網路連接問題") 
            print("• Azure 服務響應慢")
            print(f"• {query_type} 類型查詢較為複雜")
            print("\n建議:")
            print("• 嘗試更簡單的查詢")
            print("• 檢查網路連接")
            print("• 稍後再試")
            if query_type == "complex":
                print("• 將複雜查詢拆分為多個簡單查詢")
            print("=" * 60)
            return False
            
        except KeyboardInterrupt:
            print(f"\n⚠️ **用戶中斷操作**")
            print("=" * 60)
            return False
            
        except Exception as e:
            elapsed_time = time.time() - self.start_time if self.start_time else 0
            print(f"\n❌ **處理查詢時發生錯誤** (耗時: {elapsed_time:.1f} 秒)")
            print("=" * 60)
            print(f"錯誤詳情: {str(e)}")
            print("=" * 60)
            return False