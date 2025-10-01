# MyLab 專案參考資料整理

本文件整理了 mylab 資料夾下所有專案的參考資料連結，包含官方文件、範例程式碼、教學文章等。

## 📑 目錄

- [S01 - Azure AI Search](#s01---azure-ai-search)
- [S02 - Azure Logic App](#s02---azure-logic-app)
- [S03 - Microsoft Fabric](#s03---microsoft-fabric)
- [S04 - Azure Databricks](#s04---azure-databricks)
- [S05 - Multi Agents](#s05---multi-agents)

---

## S01 - Azure AI Search

### 官方文件
- [Azure AI Search - 向量搜索快速入門 (Python)](https://learn.microsoft.com/zh-tw/azure/search/search-get-started-vector?tabs=keyless&pivots=python)
  - 說明如何在 Azure AI Search 中建立和使用向量搜索功能
  - 包含 Python SDK 的完整範例

### 範例程式碼
- [Azure AI Foundry - Azure AI Search Agent 範例](https://github.com/azure-ai-foundry/foundry-samples/blob/main/samples/microsoft/python/getting-started-agents/azure_ai_search.py)
  - 展示如何建立整合 Azure AI Search 的 AI Agent
  
- [Azure Search Python Samples - Vector Search Quickstart](https://github.com/Azure-Samples/azure-search-python-samples/tree/main/Quickstart-Vector-Search)
  - Azure 官方的向量搜索快速入門範例
  - 包含索引建立、數據上傳、搜索功能測試

### 本地檔案
- `mylab/s01_azure_ai_search/README.md` - 詳細的專案說明文件
- `mylab/s01_azure_ai_search/step1_create_search_index.py` - 建立搜索索引
- `mylab/s01_azure_ai_search/step2_simple_search_agent.py` - 建立 AI Agent
- `mylab/s01_azure_ai_search/step3_cleanup_resources.py` - 清理資源

---

## S02 - Azure Logic App

### 官方文件
- [Azure App Service - 使用 Logic Apps 發送電子郵件教學](https://learn.microsoft.com/en-us/azure/app-service/tutorial-send-email?tabs=dotnetcore)
  - 完整的 Logic Apps 電子郵件發送教學
  
- [Office 365 Outlook 連接器 - 新增動作](https://learn.microsoft.com/en-us/azure/connectors/connectors-create-api-office365-outlook?tabs=consumption#add-an-office-365-outlook-action)
  - Office 365 Outlook 動作的設定方法
  
- [Azure Logic Apps - 新增觸發器和動作到工作流程](https://learn.microsoft.com/en-us/azure/logic-apps/add-trigger-action-workflow?tabs=consumption#add-action)
  - 工作流程設計的基礎教學

### 範例程式碼
- [Azure AI Foundry - Logic Apps Agent 範例](https://github.com/azure-ai-foundry/foundry-samples/blob/main/samples/microsoft/python/getting-started-agents/logic_apps/)
  - AI Agent 與 Logic Apps 整合範例

### 本地檔案
- `mylab/s02_azure_logic_app/README.md` - 專案說明文件
- `mylab/s02_azure_logic_app/cli_logic_apps.py` - CLI 版本
- `mylab/s02_azure_logic_app/ui_logic_apps.py` - Chainlit UI 版本
- `mylab/s02_azure_logic_app/user_logic_apps.py` - Logic Apps 工具類別
- `mylab/s02_azure_logic_app/user_functions.py` - 工具函數集合

---

## S03 - Microsoft Fabric

### 官方文件
- [Microsoft Fabric Data Agent 與 AI Foundry 整合入門指南 (Medium)](https://medium.com/@meetalpa/getting-started-with-microsoft-fabric-data-agent-ai-foundry-integration-de1ee9514a50)
  - 第三方詳細教學文章
  
- [Microsoft Fabric - Data Agent Foundry 整合](https://learn.microsoft.com/zh-tw/fabric/data-science/data-agent-foundry)
  - 官方 Fabric Data Agent 整合文件
  
- [Microsoft Fabric - Data Agent 租戶設定](https://learn.microsoft.com/zh-tw/fabric/data-science/data-agent-tenant-settings)
  - 租戶層級的設定說明
  
- [Azure AI Foundry - Fabric 工具使用指南](https://learn.microsoft.com/zh-tw/azure/ai-foundry/agents/how-to/tools/fabric?pivots=portal)
  - 在 AI Foundry 中使用 Fabric 工具的指南
  
- [Microsoft Fabric - Data Agent 共用設定](https://learn.microsoft.com/zh-tw/fabric/data-science/data-agent-sharing)
  - 數據共用和權限管理

### 範例程式碼
- [Azure SDK for Python - Fabric Agent 範例](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-agents/samples/agents_tools/sample_agents_fabric.py)
  - 官方 Python SDK 範例

### 本地檔案
- `mylab/s03_microsoft_fabric/README.md` - 專案說明文件
- `mylab/s03_microsoft_fabric/cli_agents_fabric.py` - CLI 版本
- `mylab/s03_microsoft_fabric/ui_agents_fabric.py` - Chainlit UI 版本
- `mylab/s03_microsoft_fabric/taxi_query_functions.py` - 查詢函數範例

---

## S04 - Azure Databricks

### 官方文件
- [Azure Databricks Native Connector in Azure AI Foundry (Medium)](https://caiomsouza.medium.com/announcing-the-azure-databricks-native-connector-in-azure-ai-foundry-78c15250d643)
  - Databricks 與 AI Foundry 整合介紹
  
- [Azure AI Foundry 角色型存取控制](https://learn.microsoft.com/azure/ai-foundry/concepts/rbac-ai-foundry)
  - AI Foundry 的 RBAC 設定說明

### 範例程式碼
- [AI Foundry Connections - Databricks Genie Agent Sample](https://github.com/Azure-Samples/AI-Foundry-Connections/blob/main/src/samples/python/sample_agent_adb_genie.py)
  - 官方 Databricks Genie Agent 範例

### 本地檔案
- `mylab/s04_azure_databricks/README.md` - 專案說明文件
- `mylab/s04_azure_databricks/cli_agent_adb_genie.py` - CLI 版本
- `mylab/s04_azure_databricks/ui_agent_adb_genie.py` - Chainlit UI 版本

---

## S05 - Multi Agents

### 官方文件
- [Microsoft Semantic Kernel 概述](https://learn.microsoft.com/en-us/semantic-kernel/overview/)
  - Semantic Kernel 框架的完整介紹
  
- [Semantic Kernel - Magentic Agent 編排](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-orchestration/magentic?pivots=programming-language-python)
  - 使用 Magentic 進行多代理程式編排的指南

### 範例程式碼
- [Microsoft Semantic Kernel GitHub](https://github.com/microsoft/semantic-kernel)
  - Semantic Kernel 官方 GitHub 儲存庫
  
- [Azure AI Agent Workshop](https://github.com/payton-chou-ms/azure-ai-agent-workshop)
  - Azure AI Agent 工作坊範例程式碼

### 本地檔案
- `mylab/s05_multi_agents/README.md` - 主要專案說明文件
- `mylab/s05_multi_agents/sk01_single_agent/` - 單一 Agent 範例
  - `step1_azure_ai_agent_retrieval_ai_search.py` - AI Search Agent
  - `step1_azure_ai_agent_sk_databricks.py` - Databricks Agent
  - `step1_azure_ai_agent_sk_fabric.py` - Fabric Agent
  - `step1_azure_ai_agent_sk_logic_app.py` - Logic App Agent
- `mylab/s05_multi_agents/sk02_multi_agent/` - Multi-Agent 範例
  - `step2_sk_multi_agent_magentic.py` - 真實多代理系統
  - `step2_fake_sk_multi_agent_magentic.py` - 模擬多代理系統
- `mylab/s05_multi_agents/sk03_magentic_app_final/` - 企業級系統
  - `README_magentic_app.md` - 重構版本說明

---

## 🔗 快速導航

### 按主題分類

#### 向量搜索與檢索
- S01 - Azure AI Search
- S05/sk01 - AI Search Agent

#### 工作流程自動化
- S02 - Azure Logic App
- S05/sk01 - Logic App Agent

#### 數據分析
- S03 - Microsoft Fabric
- S04 - Azure Databricks
- S05/sk01 - Databricks & Fabric Agents

#### Multi-Agent 系統
- S05/sk02 - Multi-Agent 協作
- S05/sk03 - 企業級 Magentic 系統

### 按實作方式分類

#### CLI 版本
- `s01_azure_ai_search/step2_simple_search_agent.py`
- `s02_azure_logic_app/cli_logic_apps.py`
- `s03_microsoft_fabric/cli_agents_fabric.py`
- `s04_azure_databricks/cli_agent_adb_genie.py`

#### Chainlit UI 版本
- `s02_azure_logic_app/ui_logic_apps.py`
- `s03_microsoft_fabric/ui_agents_fabric.py`
- `s04_azure_databricks/ui_agent_adb_genie.py`

#### Semantic Kernel 版本
- `s05_multi_agents/sk01_single_agent/` - 所有檔案
- `s05_multi_agents/sk02_multi_agent/` - 所有檔案
- `s05_multi_agents/sk03_magentic_app_final/` - 完整系統

---

## 📝 使用建議

### 學習路徑

1. **基礎入門** (1-2 週)
   - 從 S01 (Azure AI Search) 開始，了解基本的 Agent 建立
   - 學習 S02 (Logic App) 了解工作流程整合
   - 閱讀各專案的 README.md 了解架構

2. **服務整合** (2-3 週)
   - 學習 S03 (Fabric) 和 S04 (Databricks) 的數據分析整合
   - 比較 CLI 和 UI 版本的差異
   - 實作自己的查詢函數

3. **Multi-Agent 系統** (3-4 週)
   - 學習 S05/sk01 的單一 Agent 整合各服務
   - 理解 S05/sk02 的 Multi-Agent 協作模式
   - 研究 S05/sk03 的企業級架構設計

4. **進階應用** (持續)
   - 自定義 Agent 行為和指令
   - 整合新的 Azure 服務
   - 優化效能和錯誤處理
   - 實作自己的 Multi-Agent 系統

---

## ⚠️ 注意事項

### 環境變數設定
- 所有專案都需要正確設定 `.env` 檔案
- 參考各專案的 `.env.example` 檔案
- 確保 Azure 服務的連接和權限設定正確

### 費用考量
- 使用 Azure 服務會產生費用
- 建議在測試時使用免費層或開發層
- 注意 API 呼叫次數和資源使用量

---
