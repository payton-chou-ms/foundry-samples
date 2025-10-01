# Multi-Agent 系統 - Semantic Kernel 整合範例

## 📑 目錄 (Table of Contents)

- [專案概述](#-專案概述)
- [主要功能](#-主要功能)
- [檔案結構](#-檔案結構)
- [參考文件](#-參考文件)
- [詳細步驟說明](#-詳細步驟說明)
  - [步驟 1: 單一 Agent 範例 (sk01_single_agent)](#步驟-1-單一-agent-範例-sk01_single_agent)
  - [步驟 2: Multi-Agent 範例 (sk02_multi_agent)](#步驟-2-multi-agent-範例-sk02_multi_agent)
  - [步驟 3: Magentic 編排最終版本 (sk03_magentic_app_final)](#步驟-3-magentic-編排最終版本-sk03_magentic_app_final)
- [使用指南](#-使用指南)
- [常見問題](#-常見問題)

## 📋 專案概述

此專案展示如何使用 **Microsoft Semantic Kernel** 建構單一和多代理程式 (Multi-Agent) 系統，整合 Azure AI Foundry 的各種連接服務，包括：
- Azure AI Search（向量搜索和語意檢索）
- Azure Databricks Genie（數據分析）
- Microsoft Fabric（商業智慧和數據湖）
- Azure Logic Apps（工作流程自動化和郵件發送）

專案分為三個階段，逐步從單一 Agent 發展到複雜的 Multi-Agent 編排系統：
1. **sk01_single_agent**: 單一 Agent 整合各項服務
2. **sk02_multi_agent**: 基礎 Multi-Agent 協作
3. **sk03_magentic_app_final**: 使用 Magentic 框架的企業級多代理程式系統

## 🎯 主要功能

- **Semantic Kernel 整合**: 使用 Microsoft Semantic Kernel 作為 Agent 框架
- **Azure AI Agent 支援**: 整合 Azure AI Foundry Agent Service
- **多服務連接**: 
  - Azure AI Search 進行飯店資訊檢索
  - Databricks Genie 進行數據分析
  - Microsoft Fabric 進行計程車數據分析
  - Logic Apps 進行郵件發送和工作流程
- **Function Calling**: 使用 Kernel Function 和 Plugin 機制
- **Multi-Agent 編排**: 多個專業 Agent 協同工作
- **Magentic 框架**: 使用 Magentic 進行高級 Agent 編排
- **模組化架構**: 清晰的分層設計，易於維護和擴展

## 📁 檔案結構

```
mylab/s05_multi_agents/
├── .env.example                                      # 環境變數範本檔案
├── README.md                                         # 本說明文件
├── sk01_single_agent/                               # 步驟 1: 單一 Agent 範例
│   ├── .env                                         # 環境變數設定
│   ├── step1_azure_ai_agent_retrieval_ai_search.py # AI Search Agent
│   ├── step1_azure_ai_agent_sk_databricks.py       # Databricks Agent
│   ├── step1_azure_ai_agent_sk_fabric.py           # Fabric Agent
│   └── step1_azure_ai_agent_sk_logic_app.py        # Logic App Agent
├── sk02_multi_agent/                                # 步驟 2: Multi-Agent 範例
│   ├── .env                                         # 環境變數設定
│   ├── step2_sk_multi_agent_magentic.py            # 真實多代理系統
│   └── step2_fake_sk_multi_agent_magentic.py       # 模擬多代理系統（測試用）
└── sk03_magentic_app_final/                         # 步驟 3: 企業級 Magentic 系統
    ├── .env                                         # 環境變數設定
    ├── README_refactored.md                         # 重構版本說明
    ├── main.py                                      # 主入口點
    ├── __init__.py
    ├── config/                                      # 配置管理
    │   ├── __init__.py
    │   └── settings.py                              # 環境變數和設定
    ├── plugins/                                     # 功能插件
    │   ├── __init__.py
    │   ├── ai_search_plugin.py                      # AI Search 功能
    │   ├── databricks_plugin.py                     # Databricks 功能
    │   ├── fabric_plugin.py                         # Fabric 功能
    │   └── logic_app_plugin.py                      # Logic App 功能
    ├── agents/                                      # Agent 管理
    │   ├── __init__.py
    │   └── agent_factory.py                         # Agent 工廠模式
    ├── orchestration/                               # 編排邏輯
    │   ├── __init__.py
    │   └── magentic_orchestrator.py                 # Magentic 編排器
    └── utils/                                       # 工具模組
        ├── __init__.py
        ├── connection_manager.py                    # 連接管理
        ├── logic_app_manager.py                     # Logic App 管理
        └── menu_helper.py                           # 選單輔助
```

## 📚 參考文件

### 官方文件
- [Microsoft Semantic Kernel 概述](https://learn.microsoft.com/en-us/semantic-kernel/overview/)
- [Semantic Kernel - Magentic Agent 編排](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-orchestration/magentic?pivots=programming-language-python)

### 參考程式碼
- [Microsoft Semantic Kernel GitHub](https://github.com/microsoft/semantic-kernel)
- [Azure AI Agent Workshop](https://github.com/payton-chou-ms/azure-ai-agent-workshop)

## 📋 詳細步驟說明

### 步驟 1: 單一 Agent 範例 (sk01_single_agent)

此階段展示如何使用 Semantic Kernel 建立單一 Azure AI Agent，並整合不同的 Azure 服務。

#### 1.1 AI Search Agent

**檔案**: `sk01_single_agent/step1_azure_ai_agent_retrieval_ai_search.py`

**功能說明**:
- 使用已存在的 Azure AI Agent（需先透過 Portal 或 CLI 建立）
- 整合 Azure AI Search 進行飯店資訊檢索
- 展示 Semantic Kernel 的 `AzureAIAgent` 和 `AzureAIAgentThread` 使用
- 支援串流回應 (streaming response)
- 處理中間步驟 (intermediate steps) 包含 Function Call 和 Function Result

**執行方式**:
```bash
cd sk01_single_agent
python step1_azure_ai_agent_retrieval_ai_search.py
```

**預期輸出**:
- ✅ 連接到已存在的 Azure AI Agent
- ✅ 建立對話線程 (Thread)
- 📊 串流顯示 Agent 回應
- 🔍 展示 Function Call 和 Function Result

**關鍵特性**:
- 使用 `DefaultAzureCredential` 進行 Azure 身份驗證
- 透過 `agent_id` 取得已存在的 Agent 定義
- 使用 `invoke_stream` 進行串流對話
- `handle_streaming_intermediate_steps` 處理中間步驟

**環境變數需求**:
- Agent ID 在程式碼中設定：`agent_id = "asst_vnVvS09TGw3zOC6Z0vxiviN0"`
- 需要 Azure 認證（透過 Azure CLI 或環境變數）

#### 1.2 Databricks Genie Agent

**檔案**: `sk01_single_agent/step1_azure_ai_agent_sk_databricks.py`

**功能說明**:
- 建立新的 Azure AI Agent 並整合 Databricks Genie API
- 使用 Kernel Function 機制定義 `ask_genie` 函數
- 維持對話上下文 (conversation_id) 進行多輪對話
- 支援結構化數據查詢結果（表格格式）
- 動態註冊 Plugin 到 Agent Kernel

**執行方式**:
```bash
cd sk01_single_agent
python step1_azure_ai_agent_sk_databricks.py
```

**預期輸出**:
- ✅ 初始化 Databricks 連接和 Genie API
- ✅ 建立 Agent 定義並註冊 ask_genie 函數
- ✅ 執行數據查詢並顯示結果
- 🗑️ 清理資源：刪除 Thread 和 Agent

**關鍵特性**:
- **Function Tool 定義**: 在 Azure AI 服務層面定義函數工具
- **Plugin 註冊**: 使用 `DatabricksPlugin` 類別註冊實際函數實現
- **對話管理**: 使用 conversation_id 維持 Genie 對話上下文
- **結果解析**: 自動解析 SQL 查詢結果為 JSON 格式

**環境變數需求**:
```bash
FOUNDRY_PROJECT_ENDPOINT=<your-project-endpoint>
FOUNDRY_DATABRICKS_CONNECTION_NAME=<your-databricks-connection-name>
MODEL_DEPLOYMENT_NAME=gpt-4o-mini  # 可選，預設值
```

#### 1.3 Microsoft Fabric Agent

**檔案**: `sk01_single_agent/step1_azure_ai_agent_sk_fabric.py`

**功能說明**:
- 建立整合 Microsoft Fabric lakehouse 的 Agent
- 使用 `query_fabric` Kernel Function 查詢計程車數據
- 模擬 Fabric 查詢功能（可替換為真實 Fabric 連接）
- 支援多種查詢類型：統計、趨勢、異常、地理分析

**執行方式**:
```bash
cd sk01_single_agent
python step1_azure_ai_agent_sk_fabric.py
```

**預期輸出**:
- ✅ 初始化 Fabric 連接（或使用模擬連接）
- ✅ 建立 FabricLakehouseAgent
- 📊 執行計程車數據查詢
- 📈 顯示分析結果（行程統計、車資分析等）

**關鍵特性**:
- **模擬模式**: 範例使用模擬數據，便於測試
- **查詢類型**: 支援 general, stats, trends, anomaly, geography
- **Plugin 架構**: 使用 FabricPlugin 封裝查詢邏輯
- **錯誤處理**: 完整的異常捕獲和回退機制

**環境變數需求**:
```bash
FOUNDRY_PROJECT_ENDPOINT=<your-project-endpoint>
FABRIC_CONNECTION_NAME=<your-fabric-connection-name>
MODEL_DEPLOYMENT_NAME=gpt-4o-mini  # 可選，預設值
```

#### 1.4 Logic App Agent

**檔案**: `sk01_single_agent/step1_azure_ai_agent_sk_logic_app.py`

**功能說明**:
- 建立整合 Azure Logic Apps 的 Agent
- 提供兩個 Kernel Functions:
  - `fetch_current_datetime`: 取得當前時間
  - `send_email_via_logic_app`: 透過 Logic App 發送郵件
- 支援兩種 Logic App 連接模式：
  - 直接 URL 模式
  - Azure Management API 模式
- 使用 `LogicAppManager` 類別管理連接

**執行方式**:
```bash
cd sk01_single_agent
python step1_azure_ai_agent_sk_logic_app.py
```

**預期輸出**:
- ✅ 驗證 Logic App 設定
- ✅ 建立 LogicAppEmailAgent
- 📧 發送測試郵件
- ✅ 顯示郵件發送結果

**關鍵特性**:
- **雙模式支援**: 直接 URL 或 Azure Management API
- **模擬模式**: 無 Logic App 設定時使用模擬模式
- **環境變數驗證**: 自動檢查並提示必要的環境變數
- **錯誤處理**: 友善的錯誤訊息和回退機制

**環境變數需求**:

選項 1 - 直接 URL 模式:
```bash
PROJECT_ENDPOINT=<your-project-endpoint>
LOGIC_APP_EMAIL_TRIGGER_URL=<your-logic-app-trigger-url>
RECIPIENT_EMAIL=<default-recipient-email>  # 可選
```

選項 2 - Azure Management API 模式:
```bash
PROJECT_ENDPOINT=<your-project-endpoint>
AZURE_SUBSCRIPTION_ID=<your-subscription-id>
AZURE_RESOURCE_GROUP=<your-resource-group>
LOGIC_APP_NAME=<your-logic-app-name>
TRIGGER_NAME=<your-trigger-name>
RECIPIENT_EMAIL=<default-recipient-email>  # 可選
```

### 步驟 2: Multi-Agent 範例 (sk02_multi_agent)

此階段展示如何建立多個專業 Agent 並使用 Magentic 框架進行編排。

#### 2.1 真實 Multi-Agent 系統

**檔案**: `sk02_multi_agent/step2_sk_multi_agent_magentic.py`

**功能說明**:
- 建立 4 個專業 Agent：
  1. **SearchAgent**: 處理飯店搜索（AI Search）
  2. **DataAnalyst**: 處理數據分析（Databricks Genie）
  3. **BusinessIntelligence**: 處理商業智慧（Microsoft Fabric）
  4. **EmailAssistant**: 處理郵件發送（Logic Apps）
- 使用 Magentic 的 `@prompt_chain` 進行 Agent 編排
- 實現協調者 (Coordinator) 決策邏輯
- 支援複雜的多步驟任務流程

**執行方式**:
```bash
cd sk02_multi_agent
python step2_sk_multi_agent_magentic.py
```

**預期輸出**:
- 🤖 初始化 4 個專業 Agent
- 🎯 Coordinator 分析任務並選擇合適的 Agent
- 🔄 多個 Agent 協作完成複雜任務
- 📊 顯示每個 Agent 的執行結果
- 🗑️ 清理所有 Agent 和 Thread

**關鍵特性**:
- **Agent 專業化**: 每個 Agent 有明確的職責和專業領域
- **Magentic 編排**: 使用 `@prompt_chain` 實現智能編排
- **決策邏輯**: Coordinator 根據任務類型選擇合適的 Agent
- **串流處理**: 支援 Agent 回應的串流顯示

**環境變數需求**:
```bash
# 需要所有服務的環境變數（參考 .env.example）
FOUNDRY_PROJECT_ENDPOINT=<your-project-endpoint>
MODEL_DEPLOYMENT_NAME=<your-model-name>
FOUNDRY_DATABRICKS_CONNECTION_NAME=<databricks-connection>
FABRIC_CONNECTION_NAME=<fabric-connection>
# ... 其他 Logic App 相關變數
```

#### 2.2 模擬 Multi-Agent 系統

**檔案**: `sk02_multi_agent/step2_fake_sk_multi_agent_magentic.py`

**功能說明**:
- 與真實系統相同的架構，但使用模擬數據
- 用於測試和開發，無需實際的 Azure 服務連接
- 展示 Multi-Agent 編排邏輯和決策流程
- 適合學習和理解 Magentic 框架

**執行方式**:
```bash
cd sk02_multi_agent
python step2_fake_sk_multi_agent_magentic.py
```

**預期輸出**:
- 🤖 建立模擬 Agent（無需實際服務）
- 🎯 展示 Coordinator 決策流程
- 📊 返回模擬的查詢結果
- ✅ 驗證 Multi-Agent 編排邏輯

### 步驟 3: Magentic 編排最終版本 (sk03_magentic_app_final)

此階段提供企業級的多代理程式系統，採用良好的軟體架構設計原則。

**主要檔案**: `sk03_magentic_app_final/main.py`

**功能說明**:
- 完整的模組化架構設計
- 分層結構：Config、Plugins、Agents、Orchestration、Utils
- 支援互動式選單和命令行介面
- 生產環境就緒的錯誤處理和日誌記錄
- 遵循 SOLID 設計原則

**執行方式**:
```bash
cd sk03_magentic_app_final
python main.py
```

**預期輸出**:
- 📋 顯示互動式選單
- 🤖 根據選擇初始化對應的 Agent
- 🔄 執行用戶任務
- 📊 顯示結構化結果
- 🗑️ 自動清理資源

**架構特色**:

1. **Config 層** (`config/settings.py`):
   - 統一的環境變數管理
   - 配置驗證和預設值處理
   - 支援多種環境（開發、測試、生產）

2. **Plugin 層** (`plugins/`):
   - `ai_search_plugin.py`: AI Search 功能封裝
   - `databricks_plugin.py`: Databricks Genie 整合
   - `fabric_plugin.py`: Microsoft Fabric 查詢
   - `logic_app_plugin.py`: Logic App 郵件發送

3. **Agent 層** (`agents/agent_factory.py`):
   - Agent 工廠模式
   - 統一的 Agent 創建介面
   - 支援 Agent 生命週期管理

4. **Orchestration 層** (`orchestration/magentic_orchestrator.py`):
   - Magentic 框架整合
   - Agent 協調和編排邏輯
   - 任務分發和結果聚合

5. **Utils 層** (`utils/`):
   - `connection_manager.py`: Azure 連接管理
   - `logic_app_manager.py`: Logic App 管理
   - `menu_helper.py`: UI 和選單輔助

**設計原則**:
- ✅ 單一職責原則 (SRP)
- ✅ 開放封閉原則 (OCP)
- ✅ 依賴反轉原則 (DIP)
- ✅ 介面隔離原則 (ISP)
- ✅ 模組化設計

**環境變數需求**:
```bash
# 參考 .env.example，需要所有服務的完整配置
```

詳細說明請參考: `sk03_magentic_app_final/README_refactored.md`

## 🎮 使用指南

### 完整流程執行

#### 1. 準備環境

```bash
# 安裝相依套件
pip install -r requirements.txt

# 複製環境變數範本
cp .env.example .env

# 編輯 .env 填入實際值
# - Azure AI Foundry 專案端點
# - 各項服務的連接名稱
# - Logic App 設定（如需使用）
```

#### 2. 執行單一 Agent 範例

```bash
cd sk01_single_agent

# AI Search Agent
python step1_azure_ai_agent_retrieval_ai_search.py

# Databricks Agent
python step1_azure_ai_agent_sk_databricks.py

# Fabric Agent
python step1_azure_ai_agent_sk_fabric.py

# Logic App Agent
python step1_azure_ai_agent_sk_logic_app.py
```

#### 3. 執行 Multi-Agent 範例

```bash
cd sk02_multi_agent

# 真實系統（需要完整的環境變數）
python step2_sk_multi_agent_magentic.py

# 模擬系統（用於測試）
python step2_fake_sk_multi_agent_magentic.py
```

#### 4. 執行企業級系統

```bash
cd sk03_magentic_app_final

# 啟動互動式選單
python main.py
```

### 進階使用

#### 自定義 Agent ID

在 sk01_single_agent 的檔案中修改：
```python
# 替換為您的 Agent ID
agent_id = "asst_xxxxxxxxxxxxx"
```

#### 修改測試問題

在各檔案中修改 `USER_INPUTS` 變數：
```python
USER_INPUTS = [
    "您的自訂問題 1",
    "您的自訂問題 2",
]
```

#### 自定義 Agent 指令

在建立 Agent 時修改 `instructions` 參數：
```python
agent_definition = await client.agents.create_agent(
    model="gpt-4o-mini",
    name="CustomAgent",
    instructions="您的自訂指令...",
    tools=[...],
)
```

#### 開發新的 Plugin

在 `sk03_magentic_app_final/plugins/` 中新增：
```python
# my_plugin.py
from semantic_kernel.functions.kernel_function_decorator import kernel_function

class MyPlugin:
    @kernel_function(description="您的功能描述", name="my_function")
    def my_function(self, param: str) -> str:
        # 實現您的邏輯
        return result
```

## ❓ 常見問題

### Q1: 什麼是 Semantic Kernel？
**A**: Semantic Kernel 是 Microsoft 開發的開源 AI 編排框架：
- 提供統一的介面整合不同的 AI 服務
- 支援 Plugin 和 Function Calling 機制
- 支援複雜的 Multi-Agent 編排
- 跨平台支援（Python, C#, Java）

### Q2: 什麼是 Magentic 框架？
**A**: Magentic 是 Semantic Kernel 中的 Agent 編排框架：
- 使用 `@prompt_chain` 裝飾器定義編排邏輯
- 支援 Agent 之間的協調和通信
- 提供決策流程和任務分發機制
- 適合建構複雜的 Multi-Agent 系統

### Q3: AzureAIAgent 與一般 Agent 有什麼不同？
**A**: 
- **AzureAIAgent**: 連接到 Azure AI Foundry Agent Service，使用雲端 Agent
- **一般 Agent**: 在本地運行，不依賴 Azure 服務
- **優點**: AzureAIAgent 提供雲端擴展性、管理介面、更好的監控

### Q4: 如何取得 Agent ID？
**A**: 
1. 在 Azure AI Foundry Portal 建立 Agent
2. 從 Portal 複製 Agent ID
3. 或透過程式碼建立 Agent 後取得 ID：
```python
agent_definition = await client.agents.create_agent(...)
agent_id = agent_definition.id
```

### Q5: 為什麼需要定義兩次函數？
**A**: 
- **Azure AI 層面**: 定義函數工具的 schema (在 `tools` 參數中)
- **Kernel 層面**: 提供函數的實際實現 (在 Plugin 類別中)
- 這樣 Azure AI Agent 知道如何調用函數，Kernel 知道如何執行函數

### Q6: sk01、sk02、sk03 的主要差異？
**A**:

| 特性 | sk01 | sk02 | sk03 |
|------|------|------|------|
| Agent 數量 | 1 個 | 4 個 | 4 個 |
| 編排方式 | 無編排 | 基礎 Magentic | 企業級 Magentic |
| 架構設計 | 簡單腳本 | 中等複雜度 | 模組化分層 |
| 適用場景 | 學習、測試 | 功能驗證 | 生產環境 |
| 程式碼組織 | 單一檔案 | 兩個檔案 | 多層目錄結構 |

### Q7: 如何處理 Azure 認證錯誤？
**A**: 常見解決方法：
1. 確認已安裝 Azure CLI 並登入：`az login`
2. 確認有專案的存取權限（Azure AI Foundry Portal）
3. 檢查環境變數設定是否正確
4. 使用 `DefaultAzureCredential` 自動處理多種認證方式

### Q8: 如何除錯 Agent 的 Function Call？
**A**: 
- 使用 `handle_streaming_intermediate_steps` 函數
- 會顯示 `FunctionCallContent` 和 `FunctionResultContent`
- 檢查函數名稱、參數和返回值
- 確認函數在 Kernel 中正確註冊

### Q9: Multi-Agent 系統如何決定使用哪個 Agent？
**A**: 
- 使用 Coordinator (協調者) 進行決策
- 分析用戶問題的關鍵字和意圖
- 根據每個 Agent 的專業領域進行匹配
- 可以串聯多個 Agent 完成複雜任務

### Q10: 模擬模式和真實模式有什麼不同？
**A**: 
- **模擬模式**: 返回假數據，無需實際服務連接，用於測試
- **真實模式**: 連接實際 Azure 服務，返回真實數據
- **轉換**: 只需設定正確的環境變數即可從模擬切換到真實

### Q11: 如何清理創建的 Agent？
**A**: 
```python
# 清理 Thread
if thread:
    await thread.delete()

# 清理 Agent
try:
    await client.agents.delete_agent(agent_definition.id)
    print(f"Deleted agent: {agent_definition.id}")
except Exception as e:
    print(f"Error deleting agent: {e}")
```

### Q12: 企業級系統 (sk03) 的主要優勢？
**A**: 
- ✅ **可維護性**: 清晰的模組劃分，易於維護
- ✅ **可擴展性**: 遵循開放封閉原則，易於擴展新功能
- ✅ **可測試性**: 每個模組可獨立測試
- ✅ **可讀性**: 結構清晰，易於理解
- ✅ **生產就緒**: 完整的錯誤處理和日誌記錄

### Q13: 如何整合新的 Azure 服務？
**A**: 
1. 在 `plugins/` 建立新的 plugin 檔案
2. 定義 Kernel Function
3. 在 `agents/agent_factory.py` 註冊新 Agent
4. 在 `orchestration/` 更新編排邏輯
5. 更新 `.env.example` 添加新的環境變數

### Q14: 為什麼有些檔案使用 async/await？
**A**: 
- Semantic Kernel 的 Agent API 主要是非同步的
- 非同步可以提高並發性能
- 適合 I/O 密集型操作（如 API 調用）
- 所有主函數需要使用 `asyncio.run(main())`

### Q15: 這個專案的成本如何？
**A**: 主要成本來源：
- **Azure OpenAI/AI Models**: 根據 token 使用量計費
- **Azure AI Foundry**: Agent 運行時間和調用次數
- **Azure AI Search**: 查詢次數和索引大小
- **Azure Databricks**: Genie API 調用和計算資源
- **Azure Logic Apps**: 執行次數
- 建議使用開發層級或免費額度進行測試

## 📝 技術細節

### Semantic Kernel 核心概念

1. **Kernel**: 管理 Plugins 和 Functions 的核心容器
2. **Plugin**: 一組相關的 Kernel Functions
3. **Kernel Function**: 使用 `@kernel_function` 裝飾的函數
4. **Agent**: 整合 Kernel、Plugin 和 AI 模型的智能代理
5. **Thread**: Agent 對話的線程，維持上下文

### Azure AI Agent 整合

```python
# 建立 Agent 定義（Azure AI 層面）
agent_definition = await client.agents.create_agent(
    model="gpt-4o-mini",
    name="MyAgent",
    instructions="...",
    tools=[{
        "type": "function",
        "function": {
            "name": "PluginName-function_name",
            "description": "...",
            "parameters": {...}
        }
    }]
)

# 建立 Semantic Kernel Agent（本地層面）
agent = AzureAIAgent(
    client=client,
    definition=agent_definition,
    plugins=[MyPlugin()]  # 提供實際實現
)
```

### Function Tool 命名規則

- 格式: `PluginName-function_name`
- 範例: `DatabricksPlugin-ask_genie`
- Plugin 名稱要與類別名稱一致
- Function 名稱要與 `@kernel_function` 的 `name` 參數一致

### Magentic 編排模式

```python
from magentic import prompt_chain

@prompt_chain(
    "Based on the user query: {query}\n"
    "Decide which agent should handle this task."
)
async def coordinate_agents(
    query: str,
    search_agent: AzureAIAgent,
    data_analyst: AzureAIAgent,
    bi_agent: AzureAIAgent,
    email_agent: AzureAIAgent
) -> str:
    # Magentic 會自動處理 Agent 選擇和調用
    ...
```

### 錯誤處理最佳實踐

```python
try:
    # Agent 操作
    result = await agent.invoke_stream(...)
except Exception as e:
    print(f"Error: {e}")
    # 記錄錯誤
    # 回退到預設行為
finally:
    # 清理資源
    if thread:
        await thread.delete()
    if agent_definition:
        await client.agents.delete_agent(agent_definition.id)
```

## 📚 相關資源

### 延伸學習

- [Semantic Kernel 文件](https://learn.microsoft.com/semantic-kernel/)
- [Azure AI Foundry 文件](https://learn.microsoft.com/azure/ai-foundry/)
- [Magentic 文件](https://magentic.dev/)
- [Azure AI Agents SDK](https://learn.microsoft.com/python/api/overview/azure/ai-agents)

### 相關專案

- **s01_azure_ai_search**: Azure AI Search 整合範例
- **s02_azure_logic_app**: Azure Logic Apps 整合範例
- **s03_microsoft_fabric**: Microsoft Fabric 整合範例
- **s04_azure_databricks**: Azure Databricks 整合範例

### 套件需求

主要套件：
- `semantic-kernel`: Microsoft Semantic Kernel 框架
- `azure-ai-projects`: Azure AI Foundry 專案 SDK
- `azure-ai-agents`: Azure AI Agents SDK
- `azure-identity`: Azure 身份驗證
- `databricks-sdk`: Databricks SDK
- `azure-mgmt-logic`: Azure Logic Apps 管理（可選）
- `magentic-ai`: Magentic 編排框架
- `python-dotenv`: 環境變數管理

### 貢獻和支援

如有問題或建議，請參考：
- [GitHub Issues](https://github.com/payton-chou-ms/azure-ai-agent-workshop/issues)
- [Semantic Kernel Community](https://github.com/microsoft/semantic-kernel/discussions)
