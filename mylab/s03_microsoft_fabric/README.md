# Microsoft Fabric 計程車數據分析代理程式

此範例展示如何使用 Azure AI Foundry 代理程式分析 Microsoft Fabric lakehouse 中的計程車行程數據，提供 CLI 和 Web UI 兩種介面。

## 功能特色

### 更新的代理程式配置
- 基於特定問題定義代理程式個性和能力
- 專注於特定分析能力：
  - 國定假日與平日分析
  - 高費用行程分析（>$70）
  - 日間與夜間模式分析
  - 地理上車點分析
  - 乘客數量分佈分析

### 兩種介面選項

#### 1. 命令列介面（CLI）
- 執行：`python cli_agents_fabric.py`
- 包含範例問題的互動選單
- 顯示代理程式 ID 供追蹤
- 退出時自動清理資源

#### 2. Chainlit Web UI
- 執行：`chainlit run ui_agents_fabric.py`
- 互動式網頁介面
- 範例問題提示按鈕
- 代理程式生命週期管理（顯示代理程式 ID，UI 關閉時自動清理）
- 即時聊天介面

## 設定

1. **安裝依賴項**
   ```bash
   pip install -r requirements.txt
   ```

2. **環境配置**
   複製 `.env.template` 為 `.env` 並設定：
   ```
   PROJECT_ENDPOINT=your_azure_ai_foundry_project_endpoint
   MODEL_DEPLOYMENT_NAME=your_model_deployment_name
   ```

3. **必要條件**
   - 已部署模型的 Azure AI Foundry 專案
   - 包含計程車行程數據的 Microsoft Fabric lakehouse
   - 適當的 Azure 認證

## 使用方法

### CLI 版本
```bash
python cli_agents_fabric.py
```

可選擇：
- 1-5：預設範例問題
- 9：自定義查詢
- 0：退出

### Chainlit Web UI 版本  
```bash
chainlit run ui_agents_fabric.py
```

功能：
- 點擊提示按鈕發送範例問題
- 在聊天中輸入自定義查詢
- 在歡迎訊息中查看代理程式 ID
- 關閉瀏覽器時自動清理代理程式

## 範例問題

1. 比較國定假日與一般平日的計程車總行程數。此外，分析假日與平日之間的平均行程距離和平均車資是否有顯著差異。
2. 計算車資金額大於 70 的行程數量。同時，計算這些高車資行程相對於所有行程的百分比。
3. 比較日間（7:00–19:00）與夜間（19:00–7:00）的行程數量和平均車資金額。
4. 識別擁有最高行程數的上車郵遞區號。提供按行程量排名的前 5 個上車郵遞區號。
5. 確定資料集中最常見的乘客數量值（眾數）。提供所有行程中乘客數量的分佈。

## 代理程式能力

代理程式可以分析計程車行程數據的各個層面：
- 行程數量和營收統計
- 地理模式和熱點
- 時間分析（每小時、每日、季節性）
- 費用和付款模式分析
- 異常檢測
- 趨勢分析和洞察

## 檔案結構

```
mylab/s03_microsoft_fabric/
├── cli_agents_fabric.py      # CLI 版本，包含更新的代理程式配置
├── ui_agents_fabric.py       # Chainlit Web UI 實作
├── taxi_query_functions.py   # 計程車數據查詢函數（模擬 Fabric lakehouse 查詢）
├── requirements.txt          # Python 依賴項
├── .env.template             # 環境變數範本
├── .env                      # 環境變數設定（不納入版本控制）
└── README.md                 # 本說明文件
```

## 技術架構

### 計程車數據查詢函數
`taxi_query_functions.py` 包含多個分析函數：
- **基本統計**：日間/月份行程統計
- **趨勢分析**：營收趨勢和成長分析  
- **異常檢測**：高費用短程行程偵測
- **地理分析**：熱門上車地點分析
- **時間模式**：小時/日夜間比較
- **乘客行為**：乘客數量分佈和小費分析

### 代理程式配置
- 使用 Azure AI Projects SDK
- 自動函數呼叫功能
- 專業化指令集，針對計程車數據分析
- 支援繁體中文回應

## 開發須知

1. **數據來源**：目前使用模擬數據，實際部署時需要連接到 Microsoft Fabric lakehouse
2. **認證**：使用 Azure DefaultAzureCredential 進行身份驗證
3. **資源管理**：代理程式會在程式結束時自動清理，避免資源累積