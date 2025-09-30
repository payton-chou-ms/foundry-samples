# Azure Logic Apps 與 Azure AI Foundry Agent 整合範例

## 📑 目錄 (Table of Contents)

- [專案概述](#-專案概述)
- [學習目標](#-學習目標)
- [檔案結構](#-檔案結構)
- [參考文件](#-參考文件)
- [詳細步驟說明](#-詳細步驟說明)
  - [CLI 版本: 命令行 Logic App 整合](#cli-版本-命令行-logic-app-整合)
  - [UI 版本: Chainlit 互動式介面](#ui-版本-chainlit-互動式介面)
- [使用指南](#-使用指南)
- [常見問題](#-常見問題)

## 📋 專案概述

此專案展示如何將 Azure AI Foundry Agent 與 Azure Logic Apps 進行整合，實現自動化工作流程執行，特別是電子郵件發送等任務。專案提供兩種執行方式：命令行版本和 Chainlit Web UI 版本。

## 🎯 學習目標

- 學習如何建立和配置 Azure Logic Apps 工作流程
- 了解如何透過 HTTP 觸發器調用 Logic Apps
- 掌握 AI Agent 與 Logic Apps 的整合方法
- 學習如何使用自定義函數工具擴展 Agent 功能
- 了解如何建立互動式 Chainlit UI 應用程式
- 掌握 Agent 生命週期管理和資源清理

## 📁 檔案結構

```
mylab/s02_azure_logic_app/
├── cli_logic_apps.py      # 命令行版本的 Logic App 整合
├── ui_logic_apps.py       # Chainlit Web UI 版本
├── user_logic_apps.py     # Logic Apps 工具類別實作
├── user_functions.py      # 工具函數（日期/時間、天氣、計算等）
├── .env.example          # 環境變數範本檔案
└── README.md             # 本說明文件
```

## 📚 參考文件

### 官方文件
- [Azure App Service - 使用 Logic Apps 發送電子郵件教學](https://learn.microsoft.com/en-us/azure/app-service/tutorial-send-email?tabs=dotnetcore)
- [Office 365 Outlook 連接器 - 新增動作](https://learn.microsoft.com/en-us/azure/connectors/connectors-create-api-office365-outlook?tabs=consumption#add-an-office-365-outlook-action)
- [Azure Logic Apps - 新增觸發器和動作到工作流程](https://learn.microsoft.com/en-us/azure/logic-apps/add-trigger-action-workflow?tabs=consumption#add-action)

### 參考程式碼
- [Azure AI Foundry - Logic Apps Agent 範例](https://github.com/azure-ai-foundry/foundry-samples/blob/main/samples/microsoft/python/getting-started-agents/logic_apps/)

## 📋 詳細步驟說明

### CLI 版本: 命令行 Logic App 整合

**檔案**: `cli_logic_apps.py`

**功能說明**:
- 初始化 Azure AI Project 客戶端和認證
- 建立 `AzureLogicAppTool` 工具實例
  - 使用 Azure 訂閱 ID 和資源群組初始化
  - 透過 `LogicManagementClient` 管理 Logic App
- 註冊 Logic App 工作流程
  - 擷取 Logic App 的回呼 URL
  - 儲存回呼 URL 供後續調用使用
- 建立自定義函數工具
  - `fetch_current_datetime`: 取得目前日期時間
  - `send_email_via_logic_app`: 透過 Logic App 發送電子郵件
- 建立 AI Agent 並整合工具
- 執行測試任務：發送包含目前時間的電子郵件
- 自動清理 Agent 資源

**執行方式**:
```bash
python cli_logic_apps.py
```

**預期輸出**:
- ✅ Logic App 工具初始化成功
- ✅ Logic App 註冊成功
- ✅ AI Agent 創建成功 (顯示 Agent ID)
- ✅ Thread 創建成功 (顯示 Thread ID)
- 📧 執行測試任務並顯示結果
- 🧹 自動清理 Agent 資源

**關鍵組件**:
- **AzureLogicAppTool**: 管理 Logic Apps 的服務類別
  - `register_logic_app()`: 註冊並擷取回呼 URL
  - `invoke_logic_app()`: 以 JSON payload 調用 Logic App
- **create_send_email_function()**: 工廠函數，建立電子郵件發送函數
- **ToolSet & FunctionTool**: 將 Python 函數轉換為 Agent 可用的工具

**環境變數需求**:
```bash
PROJECT_ENDPOINT=<your-ai-project-endpoint>
MODEL_DEPLOYMENT_NAME=<model-name>
AZURE_SUBSCRIPTION_ID=<subscription-id>
AZURE_RESOURCE_GROUP=<resource-group-name>
LOGIC_APP_NAME=<logic-app-name>
TRIGGER_NAME=When_a_HTTP_request_is_received
RECIPIENT_EMAIL=<recipient-email>
```

### UI 版本: Chainlit 互動式介面

**檔案**: `ui_logic_apps.py`

**功能說明**:
- 包含 CLI 版本的所有功能
- **額外功能**: Chainlit 互動式網頁 UI 整合
- **額外功能**: 5 個預設自動化任務的快速執行按鈕
- **額外功能**: Agent 生命週期管理（顯示 ID、自動清理）
- **額外功能**: 即時狀態更新和錯誤處理
- **額外功能**: 繁體中文使用者介面

**執行方式**:

**Chainlit 互動式 UI 模式** (推薦):
```bash
chainlit run ui_logic_apps.py
```

**UI 功能特色**:
- 🤖 **Logic Apps Agent**: 專門用於自動化工作流程的 AI 助理
- 🎯 **5 個預設任務按鈕**: 快速執行常見自動化任務
- 🆔 **Agent ID 顯示**: 在 UI 中顯示當前 Agent 和 Thread ID
- 📧 **電子郵件自動化**: 透過 Logic Apps 發送電子郵件
- 🔄 **即時狀態更新**: 顯示任務執行進度
- 🧹 **自動清理**: 會話結束時自動刪除 Agent
- 💬 **互動式對話**: 支援自然語言指令

**預設任務按鈕**:
1. **發送目前日期時間** - 取得系統時間並透過電子郵件發送
2. **發送天氣更新** - 取得紐約天氣資訊並發送郵件
3. **發送會議提醒** - 發送團隊會議提醒郵件
4. **計算並發送結果** - 執行數學計算並透過郵件發送結果
5. **發送歡迎郵件** - 發送友善的歡迎訊息

**自訂指令範例**:
- "發送電子郵件到 user@example.com，主旨是 'Test'，內容是 'Hello world'"
- "取得東京的目前天氣並發送給收件人"
- "計算 100 和 200 的總和，然後用電子郵件發送結果"

**預期輸出**:
- ✅ Chainlit UI 啟動成功
- ✅ Logic App 工具初始化完成
- ✅ AI Agent 創建成功 (UI 中顯示 Agent ID)
- 🎯 5 個預設任務按鈕可用
- 💬 互動式聊天介面就緒
- 🧹 會話結束時自動清理

### 支援檔案說明

#### user_logic_apps.py
**AzureLogicAppTool 類別**:
- 使用 `LogicManagementClient` 管理 Logic Apps
- `register_logic_app()`: 擷取並儲存 Logic App 的回呼 URL
- `invoke_logic_app()`: 使用 HTTP POST 調用已註冊的 Logic App

**create_send_email_function() 函數**:
- 工廠函數，建立專用的電子郵件發送函數
- 使用閉包封裝 `AzureLogicAppTool` 實例
- 返回符合 Agent 工具規範的函數

#### user_functions.py
**可用的工具函數**:
- `fetch_current_datetime()`: 取得當前時間（可選格式）
- `fetch_weather()`: 取得指定地點的天氣資訊（模擬）
- `send_email()`: 發送電子郵件（模擬，非 Logic App）
- `calculate_sum()`: 計算兩個數字的總和
- `convert_temperature()`: 攝氏轉華氏
- `toggle_flag()`: 布林值切換
- `merge_dicts()`: 合併兩個字典
- `get_user_info()`: 取得用戶資訊（模擬）
- `longest_word_in_sentences()`: 找出句子中最長的單詞
- `process_records()`: 處理記錄列表

這些函數可以與 Logic App 整合，創建複雜的自動化工作流程。

## 🎮 使用指南

### 前置準備：建立 Logic App

在執行範例前，需要先在 Azure Portal 中建立 Logic App：

1. **建立 Logic App**:
   - 在 Azure Portal 中，與您的 Azure AI Project 相同的資源群組內建立 Logic App
   - 選擇 Consumption 或 Standard 方案

2. **設定 HTTP 觸發器**:
   - 新增「When a HTTP request is received」觸發器
   - 設定 JSON Schema 接受以下參數：
     ```json
     {
       "type": "object",
       "properties": {
         "to": {"type": "string"},
         "subject": {"type": "string"},
         "body": {"type": "string"}
       }
     }
     ```

3. **設定 Office 365 Outlook 動作**:
   - 新增「Send an email (V2)」動作
   - 連接您的 Office 365 帳戶
   - 設定動態內容：
     - To: `@{triggerBody()?['to']}`
     - Subject: `@{triggerBody()?['subject']}`
     - Body: `@{triggerBody()?['body']}`

4. **儲存並取得觸發器名稱**:
   - 儲存 Logic App
   - 記下觸發器名稱（預設為 "When_a_HTTP_request_is_received"）

### 完整流程執行

#### 使用 CLI 版本

1. **執行命令行版本**:
   ```bash
   python cli_logic_apps.py
   ```
   - 初始化 Logic App 工具
   - 註冊 Logic App 並取得回呼 URL
   - 建立 AI Agent
   - 執行測試任務：發送包含當前時間的電子郵件
   - 自動清理資源

#### 使用 UI 版本（推薦）

1. **啟動 Chainlit UI**:
   ```bash
   chainlit run ui_logic_apps.py
   ```
   - 瀏覽器自動開啟 `http://localhost:8000`
   - 顯示歡迎訊息和 Agent ID

2. **使用預設任務按鈕**:
   - 點擊任一預設任務按鈕快速執行
   - 查看即時狀態更新
   - 檢查收件箱確認電子郵件

3. **使用自訂指令**:
   - 在聊天框中輸入自然語言指令
   - Agent 會自動調用適當的工具
   - 透過 Logic App 執行工作流程

4. **結束會話**:
   - 關閉瀏覽器或停止 Chainlit
   - Agent 資源會自動清理

### 進階使用

#### 自定義工具函數

在 `user_functions.py` 中新增自定義函數：

```python
def your_custom_function(param: str) -> str:
    """
    您的自定義函數說明。
    
    :param param: 參數說明
    :return: 返回值說明
    """
    # 實作您的邏輯
    result = {"result": "your result"}
    return json.dumps(result)
```

然後在 `cli_logic_apps.py` 或 `ui_logic_apps.py` 中註冊：

```python
from user_functions import your_custom_function

functions_to_use: Set = {
    fetch_current_datetime,
    send_email_func,
    your_custom_function,  # 新增您的函數
}
```

#### 調整 Agent 行為

在建立 Agent 時修改 `instructions` 參數：

```python
agent = project_client.agents.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="logic-app-agent",
    instructions="您的自定義指令...",  # 修改這裡
    tools=function_tools.definitions,
)
```

#### 整合多個 Logic Apps

在 `AzureLogicAppTool` 中註冊多個 Logic Apps：

```python
logic_app_tool = AzureLogicAppTool(subscription_id, resource_group)
logic_app_tool.register_logic_app("email-logic-app", "trigger-name-1")
logic_app_tool.register_logic_app("sms-logic-app", "trigger-name-2")
logic_app_tool.register_logic_app("teams-logic-app", "trigger-name-3")
```

然後為每個 Logic App 建立對應的函數。

## ❓ 常見問題

### Q1: 如何建立 Logic App？
**A**: 
1. 前往 Azure Portal
2. 建立新的 Logic App 資源
3. 選擇與 AI Project 相同的資源群組
4. 設定 HTTP 觸發器和 Office 365 Outlook 動作
5. 參考[官方教學](https://learn.microsoft.com/en-us/azure/logic-apps/add-trigger-action-workflow?tabs=consumption#add-action)

### Q2: 觸發器名稱在哪裡找？
**A**: 
- 在 Logic App Designer 中，展開 HTTP 觸發器
- 觸發器名稱顯示在標題列
- 預設為 "When_a_HTTP_request_is_received"
- 注意：名稱區分大小寫

### Q3: 為什麼 Logic App 註冊失敗？
**A**: 常見原因：
- Logic App 不存在或名稱錯誤
- 觸發器名稱不正確（區分大小寫）
- 沒有足夠的 Azure 權限
- 訂閱 ID 或資源群組錯誤
- Logic App 狀態為停用

### Q4: 如何確認電子郵件已發送？
**A**: 
1. 檢查收件人的收件箱（包括垃圾郵件資料夾）
2. 在 Azure Portal 中查看 Logic App 的執行歷史記錄
3. 查看 Agent 的回應訊息確認狀態
4. 檢查 Logic App 的診斷日誌

### Q5: 可以發送給多個收件人嗎？
**A**: 可以！修改函數以接受多個收件人：
```python
def send_email_via_logic_app(recipients: str, subject: str, body: str) -> str:
    """
    :param recipients: 以分號分隔的多個收件人，例如 "user1@example.com;user2@example.com"
    """
    payload = {
        "to": recipients,
        "subject": subject,
        "body": body,
    }
    result = service.invoke_logic_app(logic_app_name, payload)
    return json.dumps(result)
```

### Q6: 如何測試 Logic App 是否正常運作？
**A**: 
1. 在 Azure Portal 中使用「Run Trigger」手動測試
2. 使用 Postman 或 curl 直接調用回呼 URL
3. 執行 `cli_logic_apps.py` 進行快速測試

### Q7: Agent 可以執行哪些自動化任務？
**A**: Agent 可以執行任何 Logic App 支援的任務：
- 發送電子郵件 (Office 365, Gmail, Outlook)
- 發送 Teams 訊息
- 更新 SharePoint 文件
- 建立 Planner 任務
- 發送 SMS (Twilio)
- 調用 REST API
- 寫入資料庫

### Q8: 如何除錯 Agent 行為？
**A**: 
1. 檢查 Agent 和 Thread ID（在歡迎訊息中）
2. 查看控制台輸出的詳細訊息
3. 在 Azure Portal 中查看 Logic App 執行歷史
4. 使用 `print()` 語句追蹤函數調用
5. 啟用 Azure AI Project 的診斷日誌

### Q9: 費用如何計算？
**A**: 主要費用來源：
- **Logic Apps**: 根據執行次數和動作數量計費
- **Azure OpenAI/AI Models**: 根據 token 使用量計費
- **Azure AI Foundry**: 根據 Agent 運行時間計費
- 建議使用 Consumption 方案測試以降低成本

### Q10: UI 版本和 CLI 版本有什麼差別？
**A**: 

| 功能 | CLI 版本 | UI 版本 |
|------|---------|---------|
| 介面 | 命令行 | 網頁 UI (Chainlit) |
| 互動性 | 單次執行 | 多輪對話 |
| 預設任務 | 無 | 5 個快速按鈕 |
| 狀態顯示 | 控制台文字 | 即時 UI 更新 |
| 錯誤處理 | 基本 | 豐富的 UI 訊息 |
| 資源清理 | 需手動 | 自動清理 |
| 適用場景 | 腳本自動化 | 互動式演示 |

建議：學習和測試使用 CLI 版本，演示和生產使用 UI 版本。