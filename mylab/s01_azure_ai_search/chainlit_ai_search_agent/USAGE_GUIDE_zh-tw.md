# Azure AI Search Agent with Chainlit UI - 使用指南 / Usage Guide

## 快速開始 / Quick Start

### 1. 環境準備 / Environment Setup

```bash
# 進入專案目錄 / Navigate to project directory
cd chainlit_ai_search_agent

# 安裝相依套件 / Install dependencies
pip install -r requirements.txt

# 設定環境變數 / Setup environment variables
cp .env.example .env
# 編輯 .env 填入您的 Azure 服務資訊 / Edit .env with your Azure service info
```

### 2. 執行應用程式 / Run the Application

#### 方法一：使用啟動腳本 / Method 1: Using Startup Script
```bash
python start.py
```

#### 方法二：直接啟動 Chainlit / Method 2: Direct Chainlit Launch
```bash
# 完整版本 (需要 Azure 憑證) / Full version (requires Azure credentials)
chainlit run app.py -w

# 演示版本 (無需 Azure 憑證) / Demo version (no Azure credentials needed)
chainlit run demo_app.py -w
```

### 3. 測試元件 / Test Components

```bash
# 測試 Azure 連線和元件 / Test Azure connectivity and components
python test_components.py
```

## 功能展示 / Feature Demonstration

### 歡迎介面 / Welcome Interface
應用程式啟動後會顯示：
- 雙語歡迎訊息 (中文/英文)
- 範例查詢建議
- 系統說明

After startup, the application displays:
- Bilingual welcome message (Chinese/English)
- Example query suggestions
- System description

### 互動式對話 / Interactive Chat

**中文範例查詢 / Chinese Example Queries:**
```
請推薦一些高評分的酒店
有哪些酒店提供停車服務？
告訴我關於精品酒店的資訊
搜尋台北的酒店
```

**English Example Queries:**
```
Please recommend some high-rated hotels
Which hotels offer parking facilities?
Tell me about boutique hotels
Search for hotels in New York
```

### AI Agent 回應流程 / AI Agent Response Flow

1. **接收訊息** / Message Reception
   - 用戶輸入查詢 / User inputs query
   - 系統顯示「處理中」指示器 / System shows processing indicator

2. **搜索處理** / Search Processing
   - AI Agent 調用 Azure AI Search / AI Agent calls Azure AI Search
   - 顯示搜索狀態 / Shows search status

3. **生成回應** / Generate Response
   - 基於搜索結果生成回答 / Generate answer based on search results
   - 提供結構化的酒店資訊 / Provide structured hotel information

## 技術特色 / Technical Features

### Azure 整合 / Azure Integration
- **Azure AI Search Tool**: 使用 `AzureAISearchTool` 進行搜索
- **Azure AI Agents**: 基於 `azure-ai-agents` 套件
- **DefaultAzureCredential**: 安全的認證機制

### Chainlit UI 特色 / Chainlit UI Features
- **即時聊天**: 支援即時訊息交換
- **多語言介面**: 中英文雙語支援
- **步驟顯示**: 顯示 AI 處理步驟
- **響應式設計**: 支援不同螢幕尺寸

### 錯誤處理 / Error Handling
- 連線錯誤自動重試 / Automatic retry for connection errors
- 友善的錯誤訊息 / User-friendly error messages
- 詳細的除錯日誌 / Detailed debugging logs

## 自訂和擴展 / Customization and Extension

### 修改 Agent 行為 / Modify Agent Behavior
編輯 `app.py` 中的 `instructions` 參數：

Edit the `instructions` parameter in `app.py`:

```python
instructions="""你是一個專業的搜索助手...
You are a professional search assistant..."""
```

### 調整搜索參數 / Adjust Search Parameters
修改 `AzureAISearchTool` 設定：

Modify `AzureAISearchTool` configuration:

```python
ai_search = AzureAISearchTool(
    index_connection_id=azure_ai_connection_id,
    index_name=search_index,
    query_type=AzureAISearchQueryType.SIMPLE,  # or FULL
    top_k=5,  # 調整返回結果數量 / Adjust result count
    filter="category eq 'hotel'",  # 添加篩選條件 / Add filters
)
```

### 自訂 UI 主題 / Custom UI Theme
編輯 `.chainlit/config.toml`：

Edit `.chainlit/config.toml`:

```toml
[UI.theme]
primary_color = "#1976d2"
background_color = "#fafafa"
paper_color = "#ffffff"
```

## 疑難排解 / Troubleshooting

### 常見問題 / Common Issues

**Q: Chainlit 無法啟動**
A: 確認已安裝所有相依套件，檢查 Python 版本是否 3.8+

**Q: Azure 認證失敗**
A: 檢查 `.env` 檔案設定，確認 Azure 服務端點和金鑰正確

**Q: 搜索無結果**
A: 確認搜索索引已建立且包含資料，檢查連線 ID 是否正確

**Q: Chainlit won't start**
A: Ensure all dependencies are installed, check Python version is 3.8+

**Q: Azure authentication fails**
A: Check `.env` file settings, ensure Azure service endpoints and keys are correct

**Q: Search returns no results**
A: Ensure search index is created and contains data, verify connection ID is correct

### 除錯模式 / Debug Mode
啟用詳細日誌：

Enable verbose logging:

```bash
# 設定環境變數 / Set environment variable
export CHAINLIT_DEBUG=true
chainlit run app.py -w
```

## 效能優化 / Performance Optimization

### 搜索優化 / Search Optimization
- 調整 `top_k` 參數平衡結果品質和速度
- 使用適當的篩選條件減少搜索範圍
- 考慮使用快取機制

### UI 優化 / UI Optimization
- 啟用資源快取
- 優化圖片和靜態資源載入
- 調整會話逾時設定

## 部署建議 / Deployment Recommendations

### 生產環境 / Production Environment
- 使用 HTTPS
- 設定適當的會話逾時
- 啟用日誌輪轉
- 配置負載均衡

### 安全性 / Security
- 不要在程式碼中硬編碼憑證
- 使用 Azure Key Vault 管理秘密
- 限制網路訪問
- 啟用審計日誌

---

**注意**: 此應用程式展示了 Azure AI Search 與 Chainlit 的整合功能。在生產環境中使用前，請確保遵循所有安全和效能最佳實踐。

**Note**: This application demonstrates the integration of Azure AI Search with Chainlit. Before using in production, ensure all security and performance best practices are followed.