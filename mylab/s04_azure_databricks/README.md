# Azure Databricks 與 Genie 整合 - AI Foundry 連接

此專案展示如何使用 AI Foundry 連接與代理程式，特別是針對 Azure Databricks 與 Genie API 的整合，提供 NYC 計程車數據分析功能。

## 📋 專案概述

AI Foundry 連接提供各種資源與 AI Foundry 代理程式之間的整合能力。此專案包含範例實作、最佳實務和入門模板，協助您使用 AI Foundry 建構智慧應用程式。

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
├── .env.template                       # 環境變數範本檔案
├── README.md                           # 本說明文件（整合版）
├── cli_agent_adb_genie.py             # 命令行版本範例
├── ui_agent_adb_genie.py              # Chainlit 互動式 UI 版本
└── requirements.txt                    # Python 相依套件清單
```

## 🚀 可用應用程式

### 1. **Chainlit 互動式 UI** 🆕 (推薦)
**檔案**: `ui_agent_adb_genie.py`

**主要功能**:
- 🚕 **互動式聊天介面**：專為 NYC 計程車數據分析設計
- 📊 **預設範例問題按鈕**：車資統計、時間趨勢、地理比較等
- 🆔 **代理程式生命週期管理**：顯示代理程式 ID，會話結束時自動清理
- ⚡ **透過 Databricks Genie API 進行即時分析**
- 🔄 **具有對話上下文的會話管理**

### 2. **命令行範例**
**檔案**: `cli_agent_adb_genie.py`

**功能說明**:
- 展示如何在命令行環境中使用 Databricks Genie
- 維持對話上下文的代理程式對話
- 適合自動化腳本和批次處理

## 🛠️ 環境準備

### 系統需求
- Python 3.12 或更新版本
- [Azure 訂閱帳戶]
- [Azure AI Foundry 專案](https://learn.microsoft.com/azure/ai-studio/how-to/create-projects)
- Azure CLI 已安裝並登入
  - az login --tenant <YOUR_TENANT_ID> --use-device-code

### 權限需求
- 適當的角色指派，請參閱 [Azure AI Foundry 入口網站中的角色型存取控制](https://learn.microsoft.com/azure/ai-foundry/concepts/rbac-ai-foundry)
- 可透過 Azure 入口網站中 Azure AI 專案資源的「存取控制 (IAM)」頁籤完成角色指派

## 🎮 快速開始 - Chainlit UI

### 1. 安裝相依套件
```bash
pip install -r requirements.txt
```

### 2. 設定環境變數
```bash
cp .env.template .env
# 編輯 .env 檔案，填入您的設定值
```

必要的環境變數：
```env
FOUNDRY_PROJECT_ENDPOINT=your_project_endpoint
FOUNDRY_DATABRICKS_CONNECTION_NAME=your_databricks_connection
MODEL_DEPLOYMENT_NAME=gpt-4o
```

### 3. 執行互動式 UI
```bash
chainlit run ui_agent_adb_genie.py
```

### 4. 開啟瀏覽器
前往終端機顯示的 URL（通常是 http://localhost:8000）

### 5. 開始分析
點擊範例問題按鈕或輸入您自己的 NYC 計程車數據問題！

## 📊 範例問題類型

應用程式提供以下類型分析的預設按鈕：

### 1. **車資統計** (平均車資)
- "每趟行程的平均車資金額是多少？"

### 2. **時間趨勢** (依時間的趨勢)
- "行程數量如何依一天中的小時或一週中的日期變化？"

### 3. **距離與車資分析** (距離 vs 車資關係)
- "行程距離與車資金額之間的相關性是什麼？"

### 4. **地理比較** (地區比較)
- "哪些接載郵遞區號具有最高的平均車資？"

### 5. **異常值檢測** (異常值分析)
- "是否有相較於距離具有異常高車資金額的異常行程？"

## 🤖 代理程式設定

代理程式專門針對 **NYC 計程車行程數據分析** 進行設定：

- **資料集**：連接至 Databricks "samples.nyctaxi.trips" 資料集
- **角色**：計程車行程數據的數據分析專家
- **能力**：SQL 查詢產生和結果摘要
- **回應風格**：清楚的解釋，包含查詢和自然語言摘要
- **支援功能**：車資統計、時間趨勢、距離與車資分析、地理比較、異常值檢測
