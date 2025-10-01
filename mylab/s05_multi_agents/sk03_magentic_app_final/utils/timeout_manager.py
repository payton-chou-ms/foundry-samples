# Copyright (c) Microsoft. All rights reserved.

import asyncio
import time
from typing import Optional


class ProgressIndicator:
    """進度指示器 - 顯示處理進度避免用戶等待焦慮"""
    
    def __init__(self, message: str = "處理中", timeout: int = 60):
        self.message = message
        self.timeout = timeout
        self.is_running = False
        self.start_time = None
        self.task: Optional[asyncio.Task] = None
    
    async def _show_progress(self):
        """顯示進度動畫"""
        indicators = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        i = 0
        
        while self.is_running:
            elapsed = time.time() - self.start_time if self.start_time else 0
            remaining = max(0, self.timeout - elapsed)
            
            print(f"\r{indicators[i % len(indicators)]} {self.message}... (已耗時: {elapsed:.1f}s, 剩餘: {remaining:.1f}s)", end="", flush=True)
            i += 1
            await asyncio.sleep(0.5)
    
    async def start(self):
        """開始顯示進度"""
        if not self.is_running:
            self.is_running = True
            self.start_time = time.time()
            self.task = asyncio.create_task(self._show_progress())
    
    async def stop(self):
        """停止顯示進度"""
        if self.is_running:
            self.is_running = False
            if self.task:
                self.task.cancel()
                try:
                    await self.task
                except asyncio.CancelledError:
                    pass
            print("\r" + " " * 100 + "\r", end="", flush=True)  # 清除進度行


class TimeoutManager:
    """超時管理器 - 統一管理各種超時設定"""
    
    @staticmethod
    def with_progress(coro, message: str, timeout: int):
        """
        為協程添加進度指示器和超時控制
        
        Args:
            coro: 要執行的協程
            message: 進度顯示訊息
            timeout: 超時時間（秒）
        
        Returns:
            協程結果或拋出 TimeoutError
        """
        async def _wrapped():
            progress = ProgressIndicator(message, timeout)
            try:
                await progress.start()
                result = await asyncio.wait_for(coro, timeout=timeout)
                await progress.stop()
                return result
            except asyncio.TimeoutError:
                await progress.stop()
                raise
            except Exception as e:
                await progress.stop()
                raise
        
        return _wrapped()
    
    @staticmethod
    def get_recommended_timeout(query_type: str) -> int:
        """
        根據查詢類型推薦合適的超時時間
        
        Args:
            query_type: 查詢類型
            
        Returns:
            推薦的超時時間（秒）
        """
        timeouts = {
            "simple": 120,      # 簡單查詢（如時間、單一代理程式）- 2分鐘
            "search": 180,      # 搜尋類查詢 - 3分鐘
            "analysis": 240,    # 數據分析類查詢 - 4分鐘
            "multi_agent": 300, # 多代理程式協作查詢 - 5分鐘
            "complex": 360,     # 複雜的整合查詢 - 6分鐘
        }
        
        return timeouts.get(query_type, 60)  # 預設60秒