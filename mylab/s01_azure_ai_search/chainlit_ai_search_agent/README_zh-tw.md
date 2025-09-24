# Azure AI Search Agent with Chainlit 互動式聊天介面

## 概述 / Overview

這個專案展示如何使用 Python 建立一個整合 Azure AI Search 的智能代理，並透過 Chainlit 提供友善的互動式聊天介面。

This project demonstrates how to create an AI agent integrated with Azure AI Search using Python, with a user-friendly interactive chat interface powered by Chainlit.

## 功能特色 / Features

- 🤖 **智能代理 (AI Agent)**: 基於 Azure AI Foundry 的智能對話代理
- 🔍 **搜索整合 (Search Integration)**: 深度整合 Azure AI Search 功能
- 💬 **互動式 UI (Interactive UI)**: 使用 Chainlit 提供現代化的聊天介面
- 🌐 **雙語支援 (Bilingual Support)**: 支援中文和英文查詢
- 📚 **文檔搜索 (Document Search)**: 能搜索並檢索相關文檔內容
- ⚡ **即時回應 (Real-time Response)**: 提供快速且準確的回應

## 技術架構 / Technical Architecture

```
用戶介面 (User Interface)
    ↓
Chainlit 前端 (Chainlit Frontend)
    ↓
Azure AI Agent (智能代理)
    ↓
Azure AI Search (搜索服務)
    ↓
搜索索引 (Search Index)
```

## 系統需求 / Prerequisites

### 必要軟體 / Required Software
- Python 3.8+ 
- pip (Python 套件管理器)

### Azure 服務 / Azure Services
- Azure AI Foundry Project (Azure AI 專案)
- Azure AI Search Service (Azure AI 搜索服務)
- 已建立的搜索索引 (Created search index)

## 安裝步驟 / Installation

### 1. 安裝 Python 相依套件 / Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. 設定環境變數 / Environment Setup

複製 `.env.example` 到 `.env` 並填入您的 Azure 服務資訊：

Copy `.env.example` to `.env` and fill in your Azure service information:

```bash
cp .env.example .env
```

編輯 `.env` 檔案：

Edit `.env` file:

```env
# Azure AI Search 設定
AZURE_AI_CONNECTION_ID=your-search-connection-id
AZURE_SEARCH_INDEX=your-index-name

# Azure AI Project 設定  
PROJECT_ENDPOINT=https://your-project.cognitiveservices.azure.com
MODEL_DEPLOYMENT_NAME=gpt-4o
```

### 3. 確保搜索索引已建立 / Ensure Search Index is Created

在執行此應用程式之前，請先執行：

Before running this application, please execute:

```bash
cd ..
python step1_create_search_index.py
```

## 使用方法 / Usage

### 啟動應用程式 / Start the Application

```bash
chainlit run app.py -w
```

啟動後，瀏覽器會自動開啟 `http://localhost:8000`，您可以開始與 AI 代理進行對話。

After startup, your browser will automatically open `http://localhost:8000`, and you can start conversing with the AI agent.

### 範例查詢 / Example Queries

**中文查詢範例 / Chinese Query Examples:**
- "請幫我搜尋高評分的酒店"
- "有哪些酒店提供停車服務？"
- "推薦一些精品酒店給我"
- "告訴我關於 Old Century Hotel 的資訊"

**English Query Examples:**
- "Show me hotels with high ratings"
- "Which hotels offer parking facilities?"
- "Recommend some boutique hotels"
- "Tell me about hotels in New York"

## 專案結構 / Project Structure

```
chainlit_ai_search_agent/
├── app.py                 # 主要應用程式檔案 / Main application file
├── requirements.txt       # Python 相依套件 / Python dependencies  
├── .env.example          # 環境變數範例 / Environment variables template
├── .chainlit/            # Chainlit 設定檔案夾 / Chainlit config folder
│   └── config.toml       # Chainlit 配置檔案 / Chainlit configuration
└── README_zh-tw.md       # 本說明文件 / This documentation
```

## 功能詳細說明 / Detailed Features

### 智能代理能力 / AI Agent Capabilities

1. **自然語言理解**: 理解中文和英文查詢
2. **上下文維持**: 保持對話上下文，支援多輪對話
3. **搜索整合**: 自動調用 Azure AI Search 獲取相關資訊
4. **智能回應**: 基於搜索結果生成有用的回答

### Chainlit UI 特色 / Chainlit UI Features

1. **現代化介面**: 乾淨、直觀的聊天介面
2. **即時互動**: 支援即時訊息和回應
3. **多媒體支援**: 可顯示文字、連結等多種內容
4. **會話歷史**: 保持會話歷史記錄

## 故障排除 / Troubleshooting

### 常見問題 / Common Issues

**問題**: 代理無法找到搜索結果  
**解決方案**: 確保已正確執行 `step1_create_search_index.py` 並且索引包含資料

**Problem**: Agent cannot find search results  
**Solution**: Ensure `step1_create_search_index.py` was executed correctly and the index contains data

**問題**: 環境變數錯誤  
**解決方案**: 檢查 `.env` 檔案是否正確設定所有必要的變數

**Problem**: Environment variable errors  
**Solution**: Check that `.env` file correctly sets all required variables

**問題**: Chainlit 無法啟動  
**解決方案**: 確保已安裝所有相依套件，並檢查 Python 版本是否符合需求

**Problem**: Chainlit fails to start  
**Solution**: Ensure all dependencies are installed and Python version meets requirements

### 日誌和除錯 / Logging and Debugging

應用程式會輸出詳細的日誌資訊，包括：
- Azure AI 代理的建立和執行狀態
- 搜索查詢和結果
- 錯誤訊息和例外處理

The application outputs detailed logging information including:
- Azure AI agent creation and execution status  
- Search queries and results
- Error messages and exception handling

## 開發和客製化 / Development and Customization

### 修改代理行為 / Modify Agent Behavior

編輯 `app.py` 中的 `instructions` 參數來客製化代理的行為和回應風格。

Edit the `instructions` parameter in `app.py` to customize the agent's behavior and response style.

### 自定義 UI / Customize UI

修改 `.chainlit/config.toml` 來調整 Chainlit 介面的外觀和行為。

Modify `.chainlit/config.toml` to adjust the Chainlit interface appearance and behavior.

### 擴展功能 / Extend Functionality

您可以：
- 添加更多搜索參數和篩選條件
- 整合其他 Azure 服務
- 實作自定義的回應格式
- 加入使用者認證功能

You can:
- Add more search parameters and filters
- Integrate other Azure services  
- Implement custom response formatting
- Add user authentication features

## 授權 / License

此專案遵循 MIT 授權條款。

This project is licensed under the MIT License.

## 支援和回饋 / Support and Feedback

如有問題或建議，請在 GitHub 上提交 Issue。

For questions or suggestions, please submit an Issue on GitHub.

---

**注意**: 此專案僅供學習和開發用途。在生產環境中使用前，請確保遵循 Azure 的安全最佳實踐。

**Note**: This project is for learning and development purposes. Before using in production, ensure you follow Azure security best practices.