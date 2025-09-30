# Copyright (c) Microsoft. All rights reserved.

import datetime
import json
from typing import Optional
from semantic_kernel.functions import kernel_function


class LogicAppPlugin:
    """Logic App 插件 - 處理工作流程自動化和郵件發送"""
    
    def __init__(self):
        self.logic_app_manager = None
    
    def set_manager(self, logic_app_manager):
        """設定 Logic App 管理器"""
        self.logic_app_manager = logic_app_manager
    
    @kernel_function
    def fetch_current_datetime(self, time_format: Optional[str] = None) -> str:
        """以 JSON 字串形式取得目前時間，可選擇性地格式化。
        
        Args:
            time_format: 返回目前時間的格式。預設為 None，將使用標準格式。
        
        Returns:
            目前的 UTC 日期時間
        """
        current_time = datetime.datetime.now(datetime.timezone.utc)
        if time_format:
            try:
                return current_time.strftime(time_format)
            except ValueError:
                # 如果格式無效，回傳 ISO 格式
                pass
        return current_time.isoformat()

    @kernel_function
    def send_email_via_logic_app(self, recipient: str, subject: str, body: str) -> str:
        """透過以給定的收件人、主旨和內容調用指定的 Logic App 來傳送電子郵件。
        
        Args:
            recipient: 收件人的電子郵件地址。
            subject: 電子郵件的主旨。
            body: 電子郵件的內容。
        
        Returns:
            寄送結果訊息的 JSON 字串
        """
        if not self.logic_app_manager:
            return json.dumps({
                "status": "warning",
                "message": "Logic App 未正確設定，使用模擬模式",
                "result": "模擬寄送: OK",
                "recipient": recipient,
                "subject": subject
            })
        
        result = self.logic_app_manager.send_email(recipient, subject, body)
        return json.dumps(result)