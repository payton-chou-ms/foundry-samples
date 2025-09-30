# Copyright (c) Microsoft. All rights reserved.

import requests
from azure.identity import DefaultAzureCredential as SyncDefaultAzureCredential
from config.settings import settings

# Logic App imports
try:
    from azure.mgmt.logic import LogicManagementClient
    LOGIC_MGMT_AVAILABLE = True
except ImportError:
    LOGIC_MGMT_AVAILABLE = False


class LogicAppManager:
    """管理 Logic App 調用的類別，支援兩種模式：直接 URL 或 Azure Management API"""
    
    def __init__(self):
        self.callback_url = None
        self.logic_client = None
        self.subscription_id = settings.AZURE_SUBSCRIPTION_ID
        self.resource_group = settings.AZURE_RESOURCE_GROUP
        self.logic_app_name = settings.LOGIC_APP_NAME
        self.trigger_name = settings.TRIGGER_NAME
        
        # 初始化 Logic App 連接
        self._initialize_logic_app()
    
    def _initialize_logic_app(self):
        """初始化 Logic App 連接"""
        if settings.LOGIC_APP_EMAIL_TRIGGER_URL:
            # 使用直接 URL 模式
            self.callback_url = settings.LOGIC_APP_EMAIL_TRIGGER_URL
            print("✅ 使用直接 Logic App URL 模式")
            return
        
        if (LOGIC_MGMT_AVAILABLE and self.subscription_id and 
            self.resource_group and self.logic_app_name and self.trigger_name):
            # 使用 Azure Management API 模式
            try:
                credential = SyncDefaultAzureCredential()
                self.logic_client = LogicManagementClient(credential, self.subscription_id)
                
                callback = self.logic_client.workflow_triggers.list_callback_url(
                    resource_group_name=self.resource_group,
                    workflow_name=self.logic_app_name,
                    trigger_name=self.trigger_name,
                )
                
                if callback.value:
                    self.callback_url = callback.value
                    print(f"✅ 成功註冊 Logic App '{self.logic_app_name}' 觸發器 '{self.trigger_name}'")
                else:
                    print(f"❌ Logic App '{self.logic_app_name}' 未回傳回呼 URL")
                    
            except Exception as e:
                print(f"❌ 註冊 Logic App 失敗: {str(e)}")
                print("將使用模擬模式")
    
    def send_email(self, recipient: str, subject: str, body: str) -> dict:
        """發送郵件的統一介面"""
        if not self.callback_url:
            return {
                "status": "warning",
                "message": "Logic App URL 未設定，使用模擬模式",
                "result": "模擬寄送: OK",
                "recipient": recipient,
                "subject": subject
            }
        
        payload = {"to": recipient, "subject": subject, "body": body}
        try:
            resp = requests.post(self.callback_url, json=payload, timeout=30)
            resp.raise_for_status()
            return {
                "status": "success",
                "message": "寄送成功",
                "recipient": recipient,
                "subject": subject
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"寄送失敗: {e}",
                "recipient": recipient,
                "subject": subject
            }