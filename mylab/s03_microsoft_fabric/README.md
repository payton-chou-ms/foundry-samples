# Microsoft Fabric 與 AI Foundry Agent 整合範例

## 📑 目錄 (Table of Contents)

- [專案概述](#-專案概述)
- [學習目標](#-學習目標)
- [檔案結構](#-檔案結構)
- [參考文件](#-參考文件)
- [詳細步驟說明](#-詳細步驟說明)
  - [CLI 版本: 命令列互動介面](#cli-版本-命令列互動介面)
  - [UI 版本: Chainlit 互動式介面](#ui-版本-chainlit-互動式介面)
  - [支援檔案說明](#支援檔案說明)
- [使用指南](#-使用指南)
- [常見問題](#-常見問題)

## 📋 專案概述

此專案展示如何使用 Azure AI Foundry Agent 整合 Microsoft Fabric lakehouse，進行計程車行程數據的智能分析。專案提供 CLI 和 Chainlit Web UI 兩種介面，讓使用者能透過自然語言查詢 Fabric 中的數據，並獲得專業的數據分析結果。

## 🎯 學習目標

- 學習如何整合 Azure AI Foundry Agent 與 Microsoft Fabric lakehouse
- 了解如何使用 Function Calling 將自定義函數註冊到 Agent
- 掌握 Fabric Data Agent 的租戶設定與權限管理
- 學習如何建立專業的數據分析 Agent 與指令設計
- 了解如何使用 Chainlit 建立互動式 AI Agent UI
- 掌握 Agent 生命週期管理與資源清理

## 📁 檔案結構

```
mylab/s03_microsoft_fabric/
├── cli_agents_fabric.py        # CLI 版本：命令列互動介面
├── ui_agents_fabric.py         # UI 版本：Chainlit 網頁介面
├── taxi_query_functions.py     # 計程車數據查詢函數（模擬 Fabric lakehouse 查詢）
├── .env.template               # 環境變數範本檔案
└── README.md                   # 本說明文件
```

## 📚 參考文件

### 官方文件
- [Microsoft Fabric Data Agent 與 AI Foundry 整合入門指南 (Medium)](https://medium.com/@meetalpa/getting-started-with-microsoft-fabric-data-agent-ai-foundry-integration-de1ee9514a50)
- [Microsoft Fabric - Data Agent Foundry 整合](https://learn.microsoft.com/zh-tw/fabric/data-science/data-agent-foundry)
- [Microsoft Fabric - Data Agent 租戶設定](https://learn.microsoft.com/zh-tw/fabric/data-science/data-agent-tenant-settings)
- [Azure AI Foundry - Fabric 工具使用指南](https://learn.microsoft.com/zh-tw/azure/ai-foundry/agents/how-to/tools/fabric?pivots=portal)
- [Microsoft Fabric - Data Agent 共用設定](https://learn.microsoft.com/zh-tw/fabric/data-science/data-agent-sharing)

### 參考程式碼
- [Azure SDK for Python - Fabric Agent 範例](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-agents/samples/agents_tools/sample_agents_fabric.py)

## 📋 詳細步驟說明

### CLI 版本: 命令列互動介面

**檔案**: `cli_agents_fabric.py`

**功能說明**:
- 初始化 Azure AI Project Client 與認證
- **使用真實的 Fabric 連接**（透過 `FabricTool`）
- 從 Azure AI Foundry 取得 Fabric 連接 ID
- 建立專業的計程車數據分析 Agent
  - Agent 名稱: `TaxiDataAnalysisAgent`
  - 專注於特定分析能力：國定假日分析、高費用行程、日夜模式、地理分析、乘客分佈
  - 整合 Fabric 工具進行實際的 lakehouse 數據查詢
- 建立對話線程 (Thread) 進行持續對話
- 提供互動式選單：5 個範例問題 + 自定義查詢選項
- 顯示 Fabric 連接狀態、Agent ID 和 Thread ID
- 格式化顯示對話歷史
- 使用重試機制處理 Agent 執行
- 自動清理 Agent 資源

**執行方式**:
```bash
python cli_agents_fabric.py
```

**互動選單**:
- **選項 1-5**: 執行預設範例問題
- **選項 9**: 輸入自定義查詢
- **選項 0**: 退出程式

**預期輸出**:
- ✅ AIProjectClient 初始化成功
- 🔗 正在取得 Fabric 連接...
- ✅ 成功取得 Fabric 連接 ID
- ✅ Fabric 工具初始化完成
- ✅ TaxiDataAnalysisAgent 創建成功（顯示 Agent ID）
- ✅ Thread 創建成功（顯示 Thread ID）
- 🎯 互動式選單顯示
- 💬 格式化對話歷史顯示（包含真實的 Fabric 查詢結果）
- 🔄 自動重試機制處理失敗
- 🧹 程式結束時自動清理 Agent

**範例問題**:
1. **假日分析**: 比較國定假日與平日的行程數、平均距離和平均車資
2. **高費用分析**: 計算車資 > $70 的行程數量與百分比
3. **日夜模式**: 比較日間 (7:00-19:00) 與夜間 (19:00-7:00) 的行程與費用
4. **地理熱點**: 識別行程數最高的上車郵遞區號 (Top 5)
5. **乘客分佈**: 確定最常見的乘客數量值與分佈

**Agent 特性**:
- **專業指令**: 針對計程車數據分析的專業化 instructions
- **繁體中文**: 回應使用繁體中文，技術術語保留英文
- **自動工具調用**: Agent 自動選擇並調用適當的查詢函數
- **持續對話**: 支援多輪對話與上下文理解

**環境變數需求**:
```bash
PROJECT_ENDPOINT=<your-ai-project-endpoint>
MODEL_DEPLOYMENT_NAME=<model-name>
FABRIC_CONNECTION_NAME=<fabric-connection-name>
```

**重要**: 此版本使用真實的 Fabric 連接，而非模擬數據。需要在 Azure AI Foundry 中預先建立 Fabric 連接。

### UI 版本: Chainlit 互動式介面

**檔案**: `ui_agents_fabric.py`

**功能說明**:
- 包含 CLI 版本的所有功能（使用真實 Fabric 連接）
- **額外功能**: Chainlit 互動式網頁 UI 整合
- **額外功能**: 5 個範例問題的快速執行按鈕 (Actions)
- **額外功能**: Agent 生命週期管理（顯示 ID、自動清理）
- **額外功能**: 即時狀態更新和錯誤處理
- **額外功能**: 格式化的聊天介面
- **額外功能**: 顯示 Fabric 連接初始化狀態

**執行方式**:

**Chainlit 互動式 UI 模式** (推薦):
```bash
chainlit run ui_agents_fabric.py
```

**UI 功能特色**:
- 🤖 **Taxi Data Analysis Agent**: 專業計程車數據分析 AI 助理
- 🎯 **5 個範例問題按鈕**: 快速執行預設查詢
- 🆔 **Agent ID 顯示**: 在 UI 中顯示 Agent ID 和 Thread ID
- 📊 **數據分析**: 透過自然語言查詢 Fabric lakehouse 數據
- 🔄 **即時處理**: 顯示查詢處理進度
- 🧹 **自動清理**: 關閉瀏覽器時自動刪除 Agent
- 💬 **互動式對話**: 支援自然語言查詢與多輪對話

**範例問題按鈕**:
1. **Q1**: 假日與平日行程比較分析（距離與車資）
2. **Q2**: 高費用行程分析（>$70）與百分比
3. **Q3**: 日間與夜間行程模式比較
4. **Q4**: 熱門上車地點 Top 5 郵遞區號
5. **Q5**: 乘客數量分佈與眾數分析

**自訂查詢範例**:
- "分析過去 30 天的營收趨勢"
- "找出異常的短程高費用行程"
- "比較不同付款方式的使用情況"
- "分析每小時的行程模式"

**預期輸出**:
- ✅ Chainlit UI 啟動成功 (http://localhost:8000)
- 🔗 正在取得 Fabric 連接...（UI 訊息）
- ✅ 成功取得 Fabric 連接 ID（UI 訊息）
- ✅ Fabric 工具初始化完成（UI 訊息）
- ✅ Agent 初始化完成
- 🤖 歡迎訊息顯示 Agent ID 和 Thread ID
- 🎯 5 個範例問題按鈕可用
- 💬 互動式聊天介面就緒（查詢真實 Fabric 數據）
- 🧹 關閉時自動清理 Agent

**生命週期管理**:
- `@cl.on_chat_start`: 初始化 Agent 和 Thread
- `@cl.on_message`: 處理使用者訊息
- `@cl.action_callback`: 處理範例問題按鈕
- `@cl.on_chat_end`: 自動清理 Agent 資源

### 支援檔案說明

#### taxi_query_functions.py

**功能說明**:
此檔案包含 14 個計程車數據查詢函數的範例實作，展示可能的查詢類型。**注意：現在 `cli_agents_fabric.py` 和 `ui_agents_fabric.py` 使用 `FabricTool` 直接連接 Fabric lakehouse**，不再使用這些自定義函數。這些函數僅作為參考，說明 Agent 可以執行的數據分析類型。

**函數類別與功能**:

**1. 基本查詢和聚合函數**:
- `get_daily_trip_stats(date)`: 取得特定日期的總行程數、營收和平均車資
- `get_monthly_statistics(year)`: 取得年度每月行程數和費用統計
- `get_vehicle_and_driver_count()`: 取得唯一車輛數和活躍司機數

**2. 歷史趨勢函數**:
- `get_monthly_revenue_trends()`: 取得月度營收趨勢與環比、同比分析
- `get_top_growth_areas(months)`: 識別近期行程成長最高的前 10 個區域

**3. 異常和極值函數**:
- `get_highest_fares(start_date, limit)`: 取得最高車資行程及詳細資訊
- `get_anomalous_short_high_fare_trips(days)`: 找出異常短程高費用行程（<1km, >$50）

**4. 地理分佈函數**:
- `get_top_pickup_areas(days)`: 取得前 10 名上車地點與行程量百分比

**5. 時間分析函數**:
- `get_day_night_comparison(days)`: 比較日間與夜間的行程數、費用、距離
- `get_hourly_ride_patterns()`: 分析 24 小時每小時的行程模式

**6. 乘客/司機行為函數**:
- `get_passenger_count_distribution()`: 取得乘客數量分佈與眾數
- `get_highest_tip_rate_hours()`: 識別小費率最高的時段

**7. 欄位統計函數**:
- `get_fare_statistics_by_month(start_month, end_month)`: 取得指定月份範圍的費用統計
- `get_payment_type_analysis()`: 分析不同付款方式的使用情況與平均費用

**技術特點**:
- 所有函數返回 JSON 格式字串
- 包含完整的 docstring 說明參數與返回值
- 使用模擬數據生成，便於理解查詢邏輯
- **實際執行時不使用這些函數**：Agent 透過 `FabricTool` 直接查詢 lakehouse

**重要提醒**:
當前的 `cli_agents_fabric.py` 和 `ui_agents_fabric.py` 已改用 Azure AI Foundry 的 `FabricTool`，這是官方推薦的方式，可以直接與 Fabric lakehouse 互動，無需自定義查詢函數。`taxi_query_functions.py` 僅保留作為參考。

## 🎮 使用指南

### 前置準備：Microsoft Fabric 設定

在執行範例前，需要先設定 Microsoft Fabric 環境：

1. **建立 Fabric Workspace**:
   - 前往 [Microsoft Fabric Portal](https://app.fabric.microsoft.com/)
   - 建立新的 Workspace 或使用現有的

2. **設定 Lakehouse**:
   - 在 Workspace 中建立 Lakehouse
   - 上傳計程車行程數據（或使用範例數據）
   - 確認數據表結構符合查詢函數需求

3. **配置 Data Agent 租戶設定**:
   - 在 Fabric 管理入口網站中啟用 Data Agent 功能
   - 設定適當的權限與共用選項
   - 參考[租戶設定文件](https://learn.microsoft.com/zh-tw/fabric/data-science/data-agent-tenant-settings)

4. **連接 Azure AI Foundry**:
   - 在 AI Foundry 中建立或選擇專案
   - 設定 Fabric 工具連接
   - 參考[Fabric 工具使用指南](https://learn.microsoft.com/zh-tw/azure/ai-foundry/agents/how-to/tools/fabric?pivots=portal)

### 完整流程執行

#### 使用 CLI 版本

1. **執行命令列版本**:
   ```bash
   python cli_agents_fabric.py
   ```
   - 初始化 AIProjectClient 和認證
   - 建立 TaxiDataAnalysisAgent
   - 建立對話線程
   - 顯示互動式選單

2. **選擇查詢方式**:
   - **選項 1-5**: 執行預設範例問題，快速測試功能
   - **選項 9**: 輸入自定義查詢，測試 Agent 理解能力
   - **選項 0**: 退出程式

3. **查看結果**:
   - Agent 自動選擇並調用適當的查詢函數
   - 格式化顯示對話歷史
   - 查看 Agent 的專業分析與洞察

4. **持續對話**:
   - 可以進行多輪對話
   - Agent 保持上下文理解
   - 按 'n' 退出對話循環

#### 使用 UI 版本（推薦）

1. **啟動 Chainlit UI**:
   ```bash
   chainlit run ui_agents_fabric.py
   ```
   - 瀏覽器自動開啟 `http://localhost:8000`
   - 顯示歡迎訊息、Agent ID 和 Thread ID
   - 顯示系統狀態

2. **使用範例問題按鈕**:
   - 點擊任一 Q1-Q5 按鈕快速執行查詢
   - 查看即時處理進度
   - 閱讀格式化的分析結果

3. **使用自訂查詢**:
   - 在聊天框中輸入自然語言問題
   - Agent 自動理解並調用適當工具
   - 取得專業的數據分析回應

4. **結束會話**:
   - 關閉瀏覽器標籤
   - Agent 資源自動清理
   - 無需手動刪除

### 進階使用

#### 自定義 Fabric 連接

當前實作使用 `FabricTool`，這是 Azure AI Foundry 的官方工具。若需要更多控制：

1. **建立多個 Fabric 連接**:
   ```python
   # 在 Azure AI Foundry 中建立多個連接
   conn_id_1 = project_client.connections.get("FabricConnection1").id
   conn_id_2 = project_client.connections.get("FabricConnection2").id
   
   fabric_1 = FabricTool(connection_id=conn_id_1)
   fabric_2 = FabricTool(connection_id=conn_id_2)
   ```

2. **指定特定的 lakehouse 或 workspace**:
   - 在 Azure AI Foundry 建立連接時指定
   - 不同的連接可以指向不同的 lakehouse

3. **結合自定義函數**（進階）:
   如果需要預處理或後處理數據，可以結合 `FabricTool` 與自定義函數：
   ```python
   from azure.ai.agents.models import FabricTool, FunctionTool, ToolSet
   
   # Fabric 工具用於查詢
   fabric = FabricTool(connection_id=conn_id)
   
   # 自定義函數用於特殊處理
   functions = FunctionTool(functions=your_custom_functions)
   
   # 組合工具
   toolset = ToolSet()
   toolset.add(fabric.definitions)
   toolset.add(functions)
   ```

#### 調整 Agent 指令

在 `cli_agents_fabric.py` 或 `ui_agents_fabric.py` 中修改 Agent 的專業指令：

```python
agent = project_client.agents.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="TaxiDataAnalysisAgent",
    instructions="您的自定義指令...",  # 修改這裡
    toolset=toolset,
)
```

#### 驗證 Fabric 連接

確保您的 Fabric 連接正確設定：

```python
# 測試 Fabric 連接
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
import os

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# 列出所有連接
connections = project_client.connections.list()
for conn in connections:
    print(f"連接名稱: {conn.name}")
    print(f"連接類型: {conn.connection_type}")
    print(f"連接 ID: {conn.id}")
    print("---")

# 取得特定連接
fabric_conn = project_client.connections.get("your-connection-name")
print(f"Fabric 連接 ID: {fabric_conn.id}")
```

## ❓ 常見問題

### Q1: 如何設定 Microsoft Fabric Data Agent？
**A**: 
1. 前往 [Fabric Portal](https://app.fabric.microsoft.com/)
2. 在管理設定中啟用 Data Agent 功能
3. 設定租戶權限和共用選項
4. 參考[官方文件](https://learn.microsoft.com/zh-tw/fabric/data-science/data-agent-tenant-settings)

### Q2: 如何連接 Fabric lakehouse 到 AI Foundry？
**A**: 
- 在 AI Foundry Portal 中建立 Fabric 連接
- 提供 Fabric workspace 和 lakehouse 資訊
- 設定適當的認證方式
- 參考[Fabric 工具設定指南](https://learn.microsoft.com/zh-tw/azure/ai-foundry/agents/how-to/tools/fabric?pivots=portal)

### Q3: 如何準備 Fabric lakehouse 中的數據？
**A**: 
- 此範例使用真實的 Fabric 連接，需要預先準備數據
- 在 Fabric lakehouse 中建立計程車行程數據表
- 確保數據表包含必要的欄位（如 pickup_datetime, fare_amount 等）
- 可參考 `taxi_query_functions.py` 中的 SQL 查詢了解所需欄位
- Agent 會透過 Fabric 工具直接查詢 lakehouse 中的真實數據

### Q4: Agent 如何選擇要調用的函數？
**A**: 
- Agent 根據使用者查詢的語意自動選擇
- 使用 Function Calling 機制
- 函數的 docstring 幫助 Agent 理解功能
- 可能一次調用多個函數以完成複雜查詢

### Q5: 如何除錯 Agent 的函數調用？
**A**: 
1. 查看控制台輸出的函數調用訊息
2. 在函數中加入 `print()` 語句追蹤執行
3. 檢查 Agent 的 run status 和錯誤訊息
4. 使用 Chainlit UI 查看即時處理狀態
5. 確認函數返回格式為有效的 JSON 字串

### Q6: CLI 版本和 UI 版本有什麼差別？
**A**: 

| 功能 | CLI 版本 | UI 版本 |
|------|---------|---------|
| 介面 | 命令列 | 網頁 UI (Chainlit) |
| 互動性 | 選單式 | 聊天式 |
| 範例問題 | 編號選擇 (1-5) | 按鈕點擊 (Q1-Q5) |
| 對話歷史 | 文字格式化 | UI 格式化 |
| 狀態顯示 | 控制台輸出 | 即時 UI 更新 |
| 錯誤處理 | 基本訊息 | 豐富的 UI 回饋 |
| 資源清理 | 註解掉（需手動） | 自動清理 |
| 適用場景 | 測試與除錯 | 演示與生產 |

### Q7: 如何擴展支援更多數據分析場景？
**A**: 
1. 在 `taxi_query_functions.py` 中新增分析函數
2. 確保函數有清晰的 docstring
3. 返回格式為 JSON 字串
4. 將函數加入 `taxi_query_functions` 集合
5. Agent 會自動識別並使用新函數

### Q8: Agent 可以執行哪些類型的查詢？
**A**: Agent 可以分析：
- **基本統計**: 行程數量、營收、平均值
- **趨勢分析**: 時間序列、成長率、環比同比
- **異常檢測**: 異常值、極值、不合理數據
- **地理分析**: 熱點區域、分佈模式
- **時間模式**: 小時、日夜、季節性
- **行為分析**: 乘客模式、司機行為、付款習慣

### Q9: 費用如何計算？
**A**: 主要費用來源：
- **Azure OpenAI/AI Models**: 根據 token 使用量計費
- **Azure AI Foundry**: Agent 運行時間和調用次數
- **Microsoft Fabric**: Workspace 使用和數據儲存
- 建議在測試時使用較小的數據集和較少的查詢次數

### Q10: 如何處理大量數據查詢？
**A**: 
- 在查詢函數中使用分頁和限制
- 使用聚合查詢而非返回原始數據
- 實作查詢結果快取機制
- 優化 SQL 查詢效能
- 考慮使用 Fabric 的計算資源擴展

### Q11: Fabric Data Agent 的權限如何管理？
**A**: 
- 在 Fabric 管理入口網站設定租戶權限
- 配置工作區層級的訪問控制
- 設定數據共用選項
- 參考[共用設定文件](https://learn.microsoft.com/zh-tw/fabric/data-science/data-agent-sharing)

### Q12: 如何監控 Agent 的執行狀態？
**A**: 
1. **CLI 版本**: 查看控制台輸出和 run status
2. **UI 版本**: 查看 Chainlit UI 的即時更新
3. **Azure Portal**: 在 AI Foundry 中查看 Agent 執行歷史
4. **日誌**: 啟用診斷日誌追蹤詳細資訊
5. **Agent ID**: 使用顯示的 Agent ID 追蹤特定實例

## 📝 技術架構

### 核心組件

1. **Azure AI Foundry Agent**:
   - 使用 Azure AI Projects SDK
   - 支援 Function Calling 機制
   - 自動工具調用功能
   - 專業化指令設計

2. **Microsoft Fabric Integration**:
   - Lakehouse 數據源連接
   - SQL 查詢執行
   - 數據權限管理
   - 工作區共用設定

3. **Function Tools**:
   - 14 個數據分析函數
   - JSON 格式輸入輸出
   - 清晰的 docstring 說明
   - 可擴展的函數集合

4. **使用者介面**:
   - CLI: 互動式選單
   - Chainlit: 網頁聊天介面
   - 範例問題快速執行
   - Agent 生命週期管理

### 認證與安全

- **Azure 認證**: 使用 `DefaultAzureCredential`
- **支援方式**: 
  - Azure CLI (`az login`)
  - Managed Identity
  - 環境變數
  - Visual Studio Code
  - Azure PowerShell
- **權限需求**:
  - Cognitive Services User (AI Foundry)
  - Fabric Workspace Member/Admin
  - Lakehouse Read 權限

### 資源管理

- **Agent 生命週期**:
  - CLI: 程式結束時清理（註解掉，可選）
  - UI: 關閉瀏覽器時自動清理
- **Thread 管理**: 每個會話一個 Thread
- **成本控制**: 避免資源累積
