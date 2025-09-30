# Copyright (c) Microsoft. All rights reserved.

from azure.identity.aio import DefaultAzureCredential
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.dashboards import GenieAPI
from config.settings import settings


class ConnectionManager:
    """管理所有外部服務連接的類別"""
    
    def __init__(self):
        self.genie_api = None
        self.genie_space_id = None
        self.databricks_workspace_client = None
        self.fabric_connection = None
    
    async def initialize_databricks(self, client):
        """初始化 Databricks 連接"""
        try:
            if settings.FOUNDRY_DATABRICKS_CONNECTION_NAME:
                connection = await client.connections.get(name=settings.FOUNDRY_DATABRICKS_CONNECTION_NAME)
                print(f"✅ 取得 Databricks 連接 '{settings.FOUNDRY_DATABRICKS_CONNECTION_NAME}'")
                
                if connection.metadata.get('azure_databricks_connection_type') == 'genie':
                    self.genie_space_id = connection.metadata.get('genie_space_id')
                    print(f"✅ 取得 Genie Space ID: {self.genie_space_id}")
                else:
                    print("⚠️ Databricks 連接不是 Genie 類型")

                # 初始化 Databricks 工作區客戶端
                creds = DefaultAzureCredential()
                token_result = await creds.get_token(settings.DATABRICKS_ENTRA_ID_AUDIENCE_SCOPE)
                self.databricks_workspace_client = WorkspaceClient(
                    host=connection.target,
                    token=token_result.token,
                )
                self.genie_api = GenieAPI(self.databricks_workspace_client.api_client)
                print("✅ Databricks Genie API 初始化成功")
                return True
        except Exception as e:
            print(f"⚠️ Databricks 連接失敗: {e}")
            return False
    
    async def initialize_fabric(self, client):
        """初始化 Microsoft Fabric 連接"""
        try:
            if settings.FOUNDRY_FABRIC_CONNECTION_NAME:
                connection = await client.connections.get(name=settings.FOUNDRY_FABRIC_CONNECTION_NAME)
                print(f"✅ 取得 Fabric 連接 '{settings.FOUNDRY_FABRIC_CONNECTION_NAME}'")
                
                self.fabric_connection = {
                    "name": connection.name,
                    "target": connection.target if hasattr(connection, 'target') else 'mock-fabric-endpoint',
                    "connection_type": "fabric_lakehouse"
                }
                print("✅ Microsoft Fabric 連接初始化成功")
                return True
        except Exception as e:
            print(f"⚠️ Fabric 連接失敗，使用模擬模式: {e}")
            self.fabric_connection = {
                "name": "mock-fabric-connection",
                "target": "mock-fabric-endpoint", 
                "connection_type": "fabric_lakehouse"
            }
            return True
    
    def get_databricks_connections(self):
        """取得 Databricks 連接資訊"""
        return self.genie_api, self.genie_space_id, self.databricks_workspace_client
    
    def get_fabric_connection(self):
        """取得 Fabric 連接資訊"""
        return self.fabric_connection