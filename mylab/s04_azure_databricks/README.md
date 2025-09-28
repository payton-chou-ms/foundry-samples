# AI Foundry Connections - Azure Databricks with Genie

This repository hosts samples and examples for using AI Foundry Connections with Agents, specifically for Azure Databricks integration with Genie API.

## Overview

AI Foundry Connections provides integration capabilities between various resources and AI Foundry Agent. This repository contains example implementations, best practices, and starter templates to help you build intelligent applications using AI Foundry.

## 📁 檔案結構

```
mylab/s04_azure_databricks/
├── .chainlit/                              # Chainlit 設定目錄
├── .env.template                           # 環境變數範本檔案
├── CHAINLIT_README.md                      # Chainlit 應用詳細說明文件
├── README.md                               # 本說明文件
├── chainlit.md                             # Chainlit 應用介面說明
├── chainlit_agent_adb_genie.py            # Chainlit 互動式 UI 版本
├── sample_agent_adb_genie_conversation.py # 命令行版本範例
├── sample.txt                              # Agent 指令和範例問題
└── requirements.txt                        # Python 相依套件清單
```

## Samples

The samples in this repository demonstrate:
- How to connect AI Foundry services with agents
- Integration patterns for different use cases  
- Best practices for implementation
- Interactive Chainlit UI for data analysis with sample question buttons

## Available Applications

### 1. **Chainlit 互動式 UI** 🆕 (推薦)
- `chainlit_agent_adb_genie.py` - **完整互動式網頁 UI，附有範例問題按鈕**
- Features:
  - 🚕 **互動式聊天介面**，用於 NYC 計程車數據分析
  - 📊 **預先設定的範例問題按鈕**（車資統計、時間趨勢等）
  - 🆔 **Agent 生命週期管理**（顯示 agent ID，自動清理）
  - ⚡ **透過 Databricks Genie API 進行即時分析**
  - 🔄 **具有對話上下文的會話管理**

### 2. Command Line Samples
- `sample_agent_adb_genie_conversation.py` - Agent with conversation context

## Quick Start - Chainlit UI

1. **安裝相依套件：**
   ```bash
   pip install -r requirements.txt
   ```

2. **設定環境變數：**
   ```bash
   cp .env.template .env
   # 編輯 .env 檔案，填入您的 Azure AI Foundry 專案詳細資訊
   ```

3. **執行互動式 UI：**
   ```bash
   chainlit run chainlit_agent_adb_genie.py
   ```

4. **開啟瀏覽器** 至顯示的 URL（通常是 http://localhost:8000）

5. **點擊範例問題按鈕** 或輸入您自己的 NYC 計程車數據問題！

詳細說明請參見 [CHAINLIT_README.md](CHAINLIT_README.md)。

## Agent Configuration

Agent 專門設定用於 **NYC 計程車行程數據分析**，指令基於 `sample.txt`：

- **數據集**：連接至 Databricks "samples.nyctaxi.trips" 數據集  
- **能力**：車資統計、基於時間的趨勢、距離與車資分析、地理比較、異常值檢測
- **範例問題**：5 個預先設定的常見分析任務按鈕
- **回應風格**：清晰的解釋，包含 SQL 查詢和自然語言摘要

## Prerequisites

- Python 3.12 或更新版本。
- An [Azure subscription][azure_sub].
- A [project in Azure AI Foundry](https://learn.microsoft.com/azure/ai-studio/how-to/create-projects).
- The Project endpoints. It can be found in your Azure AI Foundry project overview page.
- Entra ID is needed to authenticate the client. Your application needs an object that implements the [TokenCredential](https://learn.microsoft.com/python/api/azure-core/azure.core.credentials.tokencredential) interface. Code samples here use [DefaultAzureCredential](https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential). To get that working, you will need:
  * An appropriate role assignment. see [Role-based access control in Azure AI Foundry portal](https://learn.microsoft.com/azure/ai-foundry/concepts/rbac-ai-foundry). Role assigned can be done via the "Access Control (IAM)" tab of your Azure AI Project resource in the Azure portal.
  * [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed.
  * You are logged into your Azure account by running `az login`.
  * Note that if you have multiple Azure subscriptions, the subscription that contains your Azure AI Project resource must be your default subscription. Run `az account list --output table` to list all your subscription and see which one is the default. Run `az account set --subscription "Your Subscription ID or Name"` to change your default subscription.

