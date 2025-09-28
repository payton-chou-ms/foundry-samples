# Microsoft Fabric 計程車數據分析代理程式

此範例展示如何使用 Azure AI Foundry 代理程式分析 Microsoft Fabric lakehouse 中的計程車行程數據，提供 CLI 和 Web UI 兩種介面。

## 功能特色

### 更新的代理程式配置
- 基於 `sample.txt` 中問題定義代理程式個性
- 專注於特定分析能力：
  - 國定假日與平日分析
  - 高費用行程分析（>$70）
  - 日間與夜間模式分析
  - 地理上車點分析
  - 乘客數量分佈分析

### 兩種介面選項

#### 1. 命令列介面（CLI）
- 執行：`python sample_agents_fabric.py`
- 包含範例問題的互動選單
- 顯示代理程式 ID 供追蹤
- 退出時自動清理資源

#### 2. Chainlit Web UI
- 執行：`chainlit run chainlit_app.py`
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
   
   或者您也可以參考 `.env.example` 檔案來了解完整的配置選項。

3. **必要條件**
   - 已部署模型的 Azure AI Foundry 專案
   - 包含計程車行程數據的 Microsoft Fabric lakehouse
   - 適當的 Azure 認證

## 快速展示

如果您想在不需要 Azure 認證的情況下查看功能：

```bash
python demo.py
```

此展示腳本會顯示：
- 範例問題載入
- CLI 選單格式預覽
- 函數配置確認
- 實作功能概覽

## 使用方法

### CLI 版本
```bash
python sample_agents_fabric.py
```

可選擇：
- 1-5：來自 sample.txt 的範例問題
- 9：自定義查詢
- 0：退出

### Chainlit Web UI 版本  
```bash
chainlit run chainlit_app.py
```

功能：
- 點擊提示按鈕發送範例問題
- 在聊天中輸入自定義查詢
- 在歡迎訊息中查看代理程式 ID
- 關閉瀏覽器時自動清理代理程式

## 範例問題（來自 sample.txt）

1. 比較國定假日與一般平日的計程車行程數量
2. 分析費用金額大於 $70 的行程
3. 比較日間（7:00-19:00）與夜間（19:00-7:00）模式
4. 識別按行程量排名前 5 的上車郵遞區號
5. 確定乘客數量分佈和眾數

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
├── sample_agents_fabric.py    # CLI 版本，包含更新的代理程式配置
├── chainlit_app.py           # 新的 Chainlit Web UI 實作
├── taxi_query_functions.py   # 模擬數據函數（替換為真實的 Fabric 查詢）
├── sample.txt               # 用於代理程式個性定義的範例問題
├── demo.py                  # 展示功能的示範腳本
├── requirements.txt         # Python 依賴項
├── .env.template           # 環境變數範本
├── .env.example            # 環境變數設定範例
├── chainlit.md             # Chainlit 歡迎訊息
└── README.md               # 本說明文件
```