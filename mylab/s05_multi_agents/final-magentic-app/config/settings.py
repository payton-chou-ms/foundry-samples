# Copyright (c) Microsoft. All rights reserved.

import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

class Settings:
    """應用程式設定管理"""
    
    # Azure OpenAI 設定
    AZURE_OPENAI_ENDPOINT = os.getenv("MY_AZURE_OPENAI_ENDPOINT")
    MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")
    
    # Foundry 專案設定
    FOUNDRY_PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    
    # Databricks 設定
    FOUNDRY_DATABRICKS_CONNECTION_NAME = os.getenv("FOUNDRY_DATABRICKS_CONNECTION_NAME")
    DATABRICKS_ENTRA_ID_AUDIENCE_SCOPE = "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default"
    
    # Microsoft Fabric 設定
    FOUNDRY_FABRIC_CONNECTION_NAME = os.getenv("FABRIC_CONNECTION_NAME")
    
    # Logic App 設定
    AZURE_SUBSCRIPTION_ID = os.environ.get("AZURE_SUBSCRIPTION_ID")
    AZURE_RESOURCE_GROUP = os.environ.get("AZURE_RESOURCE_GROUP")
    LOGIC_APP_NAME = os.environ.get("LOGIC_APP_NAME")
    TRIGGER_NAME = os.environ.get("TRIGGER_NAME")
    RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL")
    LOGIC_APP_EMAIL_TRIGGER_URL = os.getenv("LOGIC_APP_EMAIL_TRIGGER_URL")
    
    # 響應時間設定
    RESPONSE_TIMEOUT = int(os.getenv("RESPONSE_TIMEOUT", "90"))  # 預設90秒
    MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "15"))     # 預設最大15次響應
    
    # Databricks SDK 設定
    @staticmethod
    def configure_databricks_sdk():
        """配置 Databricks SDK 環境變數"""
        os.environ["DATABRICKS_SDK_UPSTREAM"] = "AzureAIFoundry"
        os.environ["DATABRICKS_SDK_UPSTREAM_VERSION"] = "1.0.0"
    
    def validate(self):
        """驗證必要的配置是否存在"""
        required_settings = [
            ("FOUNDRY_PROJECT_ENDPOINT", self.FOUNDRY_PROJECT_ENDPOINT),
        ]
        
        missing_settings = []
        for name, value in required_settings:
            if not value:
                missing_settings.append(name)
        
        if missing_settings:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_settings)}")
        
        return True


# 全域設定實例
settings = Settings()