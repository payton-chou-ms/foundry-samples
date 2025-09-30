# Azure Databricks 與 Genie 整合 - AI Foundry Agent

## 📑 目錄 (Table of Contents)

- [專案概述](#-專案概述)
- [主要功能](#-主要功能)
- [檔案結構](#-檔案結構)
- [參考文件](#-參考文件)
- [詳細步驟說明](#-詳細步驟說明)
  - [CLI 版本](#1-cli-版本---命令行互動)
  - [UI 版本](#2-ui-版本---chainlit-互動式介面-推薦)
- [使用指南](#-使用指南)
- [範例問題類型](#-範例問題類型)
- [Agent 設定](#-agent-設定)
- [常見問題](#-常見問題)

## 📋 專案概述

此專案展示如何使用 Azure AI Foundry Agent 整合 Azure Databricks Genie API，提供強大的 NYC 計程車數據分析功能。透過自然語言提問，Agent 會自動與 Databricks Genie 溝通，執行 SQL 查詢並返回分析結果。

專案提供兩種版本：
- **CLI 版本**：適合命令行環境和自動化腳本
- **UI 版本**：基於 Chainlit 的互動式網頁介面（推薦）

## 🎯 主要功能

- **互動式 UI**：基於聊天的介面，附有範例問題按鈕
- **代理程式生命週期管理**：顯示代理程式 ID 並在會話結束時自動清理
- **範例問題**：為常見分析任務預先設定的按鈕
- **即時分析**：連接到 Databricks Genie 進行即時數據分析
- **會話管理**：在多個問題間維持對話上下文

## 📁 檔案結構

```
mylab/s04_azure_databricks/
├── .chainlit/                          # Chainlit 設定目錄
├── .env.example                        # 環境變數範本檔案
├── README.md                           # 本說明文件
├── cli_agent_adb_genie.py             # CLI 版本：命令行互動
├── ui_agent_adb_genie.py              # UI 版本：Chainlit 網頁介面
└── requirements.txt                    # Python 相依套件清單
```

## � 參考文件

### 官方文件
- [Azure Databricks Native Connector in Azure AI Foundry](https://caiomsouza.medium.com/announcing-the-azure-databricks-native-connector-in-azure-ai-foundry-78c15250d643)
- [Azure AI Foundry 角色型存取控制](https://learn.microsoft.com/azure/ai-foundry/concepts/rbac-ai-foundry)

### 參考程式碼
- [AI Foundry Connections - Databricks Genie Agent Sample](https://github.com/Azure-Samples/AI-Foundry-Connections/blob/main/src/samples/python/sample_agent_adb_genie.py)

## 📋 詳細步驟說明

### 1. CLI 版本 - 命令行互動

**檔案**: `cli_agent_adb_genie.py`

**功能說明**:
- 展示如何在命令行環境中使用 Azure Databricks Genie API
- 透過 `ask_genie` 函數與 Databricks Genie 進行自然語言查詢
- 維持對話上下文 (conversation_id) 進行多輪對話
- 自動處理結構化數據結果（表格格式）和純文字回應
- 適合自動化腳本和批次處理場景

**執行方式**:
```bash
python cli_agent_adb_genie.py
```

**預期輸出**:
- ✅ AI Project client 初始化成功
- ✅ Databricks 連接驗證通過 (connection type: 'genie')
- ✅ Genie Space ID 取得成功
- ✅ Databricks workspace client 建立完成
- ✅ Agent 創建成功（顯示 Agent ID）
- ✅ Thread 創建成功（顯示 Thread ID）
- 📊 執行 2 個測試查詢並顯示結果
- 📜 顯示所有訊息和執行步驟詳情

**環境變數需求**:
```bash
FOUNDRY_PROJECT_ENDPOINT=<your-ai-project-endpoint>
FOUNDRY_DATABRICKS_CONNECTION_NAME=<your-databricks-connection-name>
GENIE_QUESTION_1=<first-test-question>
GENIE_QUESTION_2=<second-test-question>
```

**關鍵特性**:
- **對話管理**: 使用 conversation_id 維持多輪對話上下文
- **結果解析**: 自動解析 SQL 查詢結果為 JSON 格式（包含表格或純文字）
- **錯誤處理**: 完整的異常捕獲和錯誤訊息返回
- **函數工具**: 使用 FunctionTool 和 ToolSet 整合 ask_genie 函數

### 2. UI 版本 - Chainlit 互動式介面 (推薦)

**檔案**: `ui_agent_adb_genie.py`

**功能說明**:
- 🚕 **互動式聊天介面**：專為 NYC 計程車數據分析設計的網頁 UI
- 📊 **預設範例問題按鈕**：5 個常見分析類型的快速提問按鈕
- 🆔 **Agent 生命週期管理**：顯示 Agent ID，會話結束時自動清理資源
- ⚡ **即時分析**：透過 Databricks Genie API 進行即時數據查詢
- 🔄 **會話管理**：在多個問題間維持對話上下文
- 💬 **視覺化回應**：清晰的訊息顯示，包含處理狀態和結果

**執行方式**:
```bash
chainlit run ui_agent_adb_genie.py
```

**預期輸出**:
1. 啟動 Chainlit 伺服器（預設 http://localhost:8000）
2. 瀏覽器自動開啟或手動前往 URL
3. 顯示歡迎訊息和 Agent 初始化狀態
4. 顯示 Agent ID 用於追蹤
5. 提供 5 個範例問題按鈕供快速測試
6. 即時顯示查詢處理狀態和結果

**環境變數需求**:
```bash
FOUNDRY_PROJECT_ENDPOINT=<your-ai-project-endpoint>
FOUNDRY_DATABRICKS_CONNECTION_NAME=<your-databricks-connection-name>
MODEL_DEPLOYMENT_NAME=gpt-4o  # 可選，預設為 gpt-4o
```

**關鍵特性**:
- **範例問題按鈕**: 5 個預設問題涵蓋不同分析類型
- **處理狀態顯示**: 即時顯示 "🤔 Analyzing..." 和 "✅ Analysis completed"
- **自動清理**: 使用 @cl.on_stop 在會話結束時刪除 Agent
- **錯誤處理**: 友善的錯誤訊息顯示和重試提示
- **UI/UX 優化**: 使用 emoji 和格式化文字提升使用體驗

## 🎮 使用指南

### 完整流程執行 - UI 版本

1. **安裝相依套件**:
   ```bash
   pip install -r requirements.txt
   ```

2. **設定環境變數**:
   ```bash
   # 複製範本檔案
   cp .env.example .env
   
   # 編輯 .env 並填入實際值
   # - FOUNDRY_PROJECT_ENDPOINT: 您的 AI Foundry 專案端點
   # - FOUNDRY_DATABRICKS_CONNECTION_NAME: Databricks Genie 連接名稱
   # - MODEL_DEPLOYMENT_NAME: 模型部署名稱（可選，預設 gpt-4o）
   ```

3. **執行互動式 UI**:
   ```bash
   chainlit run ui_agent_adb_genie.py
   ```

4. **開啟瀏覽器**:
   - 前往終端機顯示的 URL（通常是 http://localhost:8000）
   - 查看 Agent ID 和初始化狀態

5. **開始分析**:
   - 點擊範例問題按鈕進行快速測試
   - 或輸入自訂的 NYC 計程車數據問題

### 完整流程執行 - CLI 版本

1. **安裝相依套件**:
   ```bash
   pip install -r requirements.txt
   ```

2. **設定環境變數**:
   ```bash
   # 編輯 .env 檔案，CLI 版本需要額外設定測試問題
   FOUNDRY_PROJECT_ENDPOINT=<your-endpoint>
   FOUNDRY_DATABRICKS_CONNECTION_NAME=<your-connection>
   GENIE_QUESTION_1=What is the average fare amount per trip?
   GENIE_QUESTION_2=How does the number of trips vary by hour of the day?
   ```

3. **執行 CLI 版本**:
   ```bash
   python cli_agent_adb_genie.py
   ```

4. **查看輸出**:
   - 觀察 Agent 創建和初始化過程
   - 查看兩個測試問題的執行結果
   - 檢視所有訊息和執行步驟的 JSON 詳情

### 進階使用

#### 自定義 Agent 指令
在 `ui_agent_adb_genie.py` 或 `cli_agent_adb_genie.py` 中修改 Agent 指令：
```python
AGENT_INSTRUCTIONS = """
您是一個連接到 Databricks "samples.nyctaxi.trips" 資料集的數據分析代理。
# 可在此自定義 Agent 的行為和回應風格
"""
```

#### 修改範例問題
在 `ui_agent_adb_genie.py` 中更新範例問題列表：
```python
SAMPLE_QUESTIONS = [
    "您的自訂問題 1",
    "您的自訂問題 2",
    # 最多 5 個問題
]
```

#### CLI 版本測試問題
在 `.env` 檔案中修改 CLI 版本的測試問題：
```bash
GENIE_QUESTION_1=What is the total revenue from all trips?
GENIE_QUESTION_2=Which day of the week has the most trips?
```

## 📊 範例問題類型

UI 版本提供以下 5 種分析類型的預設按鈕：

### 1. **車資統計** (平均車資)
- "每趟行程的平均車資金額是多少？"
- 分析整體車資分布和平均值

### 2. **時間趨勢** (依時間的趨勢)
- "行程數量如何依一天中的小時或一週中的日期變化？"
- 分析時間模式和高峰時段

### 3. **距離與車資分析** (距離 vs 車資關係)
- "行程距離與車資金額之間的相關性是什麼？"
- 探索距離與費用的關係

### 4. **地理比較** (地區比較)
- "哪些接載郵遞區號具有最高的平均車資？"
- 分析不同地區的車資差異

### 5. **異常值檢測** (異常值分析)
- "是否有相較於距離具有異常高車資金額的異常行程？"
- 識別異常數據和潛在問題

## 🤖 Agent 設定

Agent 專門針對 **NYC 計程車行程數據分析** 進行設定：

### 資料來源
- **資料集**: Databricks "samples.nyctaxi.trips" 資料集
- **連接類型**: Genie (使用 Genie Space ID)
- **數據欄位**: pickup_datetime, fare_amount, trip_distance, passenger_count, pickup_location 等

### Agent 能力
- **SQL 查詢生成**: 根據自然語言自動產生 SQL 查詢
- **結果摘要**: 將查詢結果轉換為易懂的自然語言說明
- **上下文維持**: 透過 conversation_id 維持多輪對話
- **結構化輸出**: 支援表格格式和純文字回應

### 支援的分析類型
1. **車資統計**: 平均、最高、最低車資金額計算
2. **時間趨勢**: 依小時、日期、週別的行程數量分析
3. **距離與車資分析**: 距離與車資的相關性和分布
4. **地理比較**: 不同郵遞區號的車資比較
5. **異常值偵測**: 識別異常高車資或異常行程模式

### Agent 指令 (CLI 版本)
```python
instructions = "你是一個有幫助的助理，使用 Databricks Genie 來回答問題。" \
               "使用第一次呼叫 ask_genie 函數回傳的 conversation_id 來在 Genie 中繼續對話。"
```

### Agent 指令 (UI 版本)
詳細的多語言指令，包含：
- 角色定義和資料來源說明
- 5 種支援的分析類型
- 回應風格要求（清晰解釋、顯示查詢和自然語言摘要）

## ❓ 常見問題

### Q1: 如何取得 Databricks 連接名稱？
**A**: 在 Azure AI Foundry Portal 中：
1. 前往您的 AI Project
2. 點擊「管理中心」(Management center)
3. 選擇「連接的資源」(Connected resources)
4. 找到 Databricks 連接並複製其名稱

### Q2: 什麼是 Genie Space ID？
**A**: Genie Space ID 是 Databricks Genie 的工作空間識別碼：
- 在建立 Databricks 連接時自動產生
- 儲存在連接的 metadata 中
- 用於識別特定的 Genie 對話空間和資料集存取權限

### Q3: 為什麼需要 conversation_id？
**A**: conversation_id 用於維持對話上下文：
- 第一次查詢時由 Genie 自動生成
- 後續查詢使用相同的 conversation_id 可以參考之前的對話
- 這樣 Agent 可以理解「上一個結果」、「再分析」等上下文相關的問題

### Q4: CLI 和 UI 版本有什麼區別？
**A**: 主要差異：

| 特性 | CLI 版本 | UI 版本 |
|------|----------|---------|
| 介面 | 命令行 | 網頁 (Chainlit) |
| 互動方式 | 預設問題 | 範例按鈕 + 自由輸入 |
| 適用場景 | 自動化、批次處理 | 互動式探索、演示 |
| Agent 清理 | 手動（註解掉的程式碼） | 自動（會話結束時） |
| 視覺化 | JSON 輸出 | 格式化訊息 |

### Q5: 如何修改測試問題？
**A**: 
- **CLI 版本**: 在 `.env` 檔案中修改 `GENIE_QUESTION_1` 和 `GENIE_QUESTION_2`
- **UI 版本**: 在 `ui_agent_adb_genie.py` 中修改 `SAMPLE_QUESTIONS` 列表（最多 5 個）

### Q6: 如何處理連接錯誤？
**A**: 常見解決方法：
1. 確認 Databricks 連接類型為 'genie'（不是其他類型）
2. 檢查 Azure AI Foundry 專案端點正確性
3. 驗證 Azure CLI 已登入且有適當權限
4. 確認 Databricks workspace 可正常存取
5. 檢查 samples.nyctaxi.trips 資料集是否存在

### Q7: ask_genie 函數如何工作？
**A**: ask_genie 函數的工作流程：
1. 接收問題和可選的 conversation_id
2. 如果沒有 conversation_id，開始新對話
3. 如果有 conversation_id，繼續現有對話
4. 執行查詢並等待結果
5. 解析結果（表格或純文字）
6. 返回 JSON 格式的回應，包含 conversation_id 用於後續查詢

### Q8: 可以使用其他資料集嗎？
**A**: 可以！您需要：
1. 在 Databricks 中準備您的資料集
2. 建立指向該資料集的 Genie Space
3. 在 Azure AI Foundry 中建立對應的連接
4. 修改 Agent 指令以適應新的資料領域和分析需求

### Q9: 如何查看 Agent 的執行步驟？
**A**: 
- **CLI 版本**: 程式會自動列印所有 run_steps 的詳細 JSON 輸出
- **UI 版本**: 在處理訊息中顯示狀態，完整步驟儲存在會話中
- 兩者都可以透過 `project_client.agents.run_steps.list()` 取得詳細資訊

### Q10: Agent 會自動清理嗎？
**A**: 
- **CLI 版本**: 預設不會自動刪除（程式碼中有註解掉的刪除指令），方便除錯和檢視
- **UI 版本**: 使用 `@cl.on_stop` 在會話結束時自動刪除 Agent，避免資源浪費

### Q11: 這個範例的成本如何？
**A**: 主要成本來源：
- **Azure OpenAI/AI Models**: 根據 token 使用量計費（模型調用）
- **Azure AI Foundry**: Agent 運行時間和調用次數
- **Azure Databricks**: Genie API 查詢次數和計算資源
- 建議使用開發層級或免費額度進行測試

### Q12: 為什麼回應有時是表格，有時是純文字？
**A**: 取決於 Genie 的查詢結果：
- **表格格式**: 當查詢返回結構化數據（SELECT 查詢結果）
- **純文字**: 當 Genie 返回說明性回應或無法產生 SQL 查詢時
- ask_genie 函數會自動處理兩種格式並以 JSON 返回

## 📝 技術細節

### 認證機制
- 使用 `DefaultAzureCredential` 進行 Azure 身份驗證
- 支援多種認證方式：Azure CLI、環境變數、Managed Identity 等
- Databricks 使用 Entra ID token 進行認證

### 對話管理
- 第一次查詢：`genie_api.start_conversation_and_wait()`
- 後續查詢：`genie_api.create_message_and_wait()` with conversation_id
- 對話 ID 在 JSON 回應中返回，供後續查詢使用

### 結果解析
- 檢查 `query_result.statement_response` 是否存在
- 使用 `statement_execution.get_statement()` 取得執行結果
- 解析 schema columns 和 data_array 為表格格式
- 處理不同數據類型（字串、數字、日期等）

### 工具整合
- CLI 版本：使用 `FunctionTool` 和 `ToolSet` 整合 ask_genie
- UI 版本：相同的工具整合 + Chainlit 事件處理
- 啟用 `enable_auto_function_calls()` 讓 Agent 自動調用工具
