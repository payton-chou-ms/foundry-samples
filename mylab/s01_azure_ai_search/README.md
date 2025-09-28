# Azure AI Search 與 AI Foundry Agent 整合範例

## 📋 專案概述

此專案展示如何將 Azure AI Search 與 Azure AI Foundry Agent 進行整合，提供完整的向量搜索和智能對話功能。專案分為三個主要步驟，每個步驟都有對應的 Python 腳本。

## 🎯 學習目標

- 學習如何建立和配置 Azure AI Search 向量索引
- 了解如何創建和部署 AI Foundry Agent
- 掌握 AI Agent 與搜索服務的整合方法
- 學習如何正確清理和管理雲端資源

## 📁 檔案結構

```
mylab/s01_azure_ai_search/
├── step1_create_search_index.py       # 步驟 1: 建立搜索索引
├── step2_cli_create_ai_agent.py       # 步驟 2A: 建立 AI Agent (命令行版本)
├── step2_ui_create_ai_agent.py        # 步驟 2B: 建立 AI Agent (Chainlit UI 版本)
├── step3_cleanup_resources.py         # 步驟 3: 清理資源
├── requirements.txt                   # Python 依賴套件清單
├── .env.example                       # 環境變數範本檔案
├── README.md                          # 本說明文件
├── vector-search-quickstart.ipynb     # 完整功能展示的 Jupyter Notebook
└── Ref/
    └── ref-azure-search-quickstart.ipynb  # 原始參考的 Jupyter Notebook
```

## 🔧 環境準備

### 系統需求

- Python 3.8 或更高版本
- Azure 訂閱帳戶
- Azure AI Foundry 專案
- Azure AI Search 服務

### 安裝依賴套件

```bash
# 使用 requirements.txt（推薦）
pip install -r requirements.txt

# 或手動安裝個別套件
pip install azure-search-documents
pip install azure-ai-projects
pip install azure-identity
pip install python-dotenv
pip install chainlit
```

### 環境變數設定

1. 複製環境變數範本：
```bash
cp .env.example .env
```

2. 編輯 `.env` 檔案並填入您的設定：
```bash
# Azure AI Search 設定
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_API_KEY=your-search-api-key
AZURE_SEARCH_INDEX=vector-search-quickstart

# Azure AI Project 設定
PROJECT_ENDPOINT=https://your-ai-project.cognitiveservices.azure.com
MODEL_DEPLOYMENT_NAME=gpt-4o
```

## 📋 詳細步驟說明

### 步驟 1: 建立 AI Search 索引和相關功能

**檔案**: `step1_create_search_index.py`

**功能說明**:
- 初始化 Azure Search 客戶端和認證
- 建立具有向量搜索功能的索引
- 準備酒店文檔數據（包含預先計算的嵌入向量）
- 上傳文檔到索引
- 測試基本搜索功能（文字搜索、向量搜索、篩選搜索）

**執行方式**:
```bash
python step1_create_search_index.py
```

**預期輸出**:
- ✅ 索引建立成功
- ✅ 文檔上傳完成
- ✅ 搜索功能測試通過

### 步驟 2: 建立 AI Foundry Agent（兩種執行方式）

本步驟提供兩種不同的執行方式，您可以根據需要選擇合適的版本：

#### 步驟 2A: 命令行版本

**檔案**: `step2_cli_create_ai_agent.py`

**功能說明**:
- 初始化 Azure AI Project 客戶端
- 驗證搜索索引可用性
- 建立具有酒店搜索專業能力的 AI Agent
- 建立對話線程和測試功能
- 提供基本的命令行互動

**執行方式**:
```bash
python step2_cli_create_ai_agent.py
```

**適用場景**: 腳本測試、自動化流程、或偏好命令行介面的開發者

#### 步驟 2B: Chainlit 互動式 UI 版本 (推薦)

**檔案**: `step2_ui_create_ai_agent.py`

**功能說明**:
- 包含步驟 2A 的所有功能
- **額外功能**: Chainlit 互動式網頁 UI 整合
- **額外功能**: 樣本問題建議按鈕
- **額外功能**: Agent 生命週期管理（顯示 ID、自動清理）
- **額外功能**: 現代化的聊天介面

**執行方式**:

**Chainlit 互動式 UI 模式** (推薦):
```bash
chainlit run step2_ui_create_ai_agent.py -w
```

**命令行測試模式**:
```bash
python step2_ui_create_ai_agent.py
```

**UI 功能特色**:
- 🏨 **專業酒店助理**: 基於酒店搜索領域的專門化 AI 助理
- 🎯 **樣本問題按鈕**: 5 個預設酒店相關問題的快速按鈕
- 🆔 **Agent ID 顯示**: 在 UI 中顯示當前 Agent 和 Thread ID
- 🧹 **自動清理**: UI 關閉時自動刪除 Agent，避免資源浪費
- 💬 **即時對話**: 流暢的對話體驗和即時回應

**樣本問題包括**:
1. "What hotels do you know about? Can you tell me about them?"
2. "Can you recommend a boutique hotel in New York?"
3. "Tell me about hotels with high ratings."
4. "What amenities are available at the Old Century Hotel?"
5. "Are there any hotels with parking included?"

**預期輸出**:
- ✅ AI Agent 建立成功
- ✅ Chainlit UI 啟動成功
- ✅ 樣本問題按鈕可用
- ✅ Agent 生命週期管理就緒

### 步驟 3: 清理 AI Search 索引和 AI Foundry Agent

**檔案**: `step3_cleanup_resources.py`

**功能說明**:
- 列出和識別需要清理的資源
- 安全刪除 AI Agent 和相關資源
- 清理搜索索引和文檔
- 驗證清理完成狀態
- 提供清理摘要報告

**執行方式**:

基本模式：
```bash
python step3_cleanup_resources.py
```

互動模式：
```bash
python step3_cleanup_resources.py --interactive
```

指定 Agent ID：
```bash
python step3_cleanup_resources.py --agent-id "your-agent-id"
```

強制清理：
```bash
python step3_cleanup_resources.py --force
```

**預期輸出**:
- ✅ Agent 清理完成
- ✅ 索引清理完成
- 📊 清理摘要報告

## 🎮 使用指南

### 完整流程執行

1. **準備環境**:
   ```bash
   # 安裝套件
   pip install -r requirements.txt
   
   # 設定環境變數
   cp .env.example .env
   # 編輯 .env 檔案填入您的設定
   ```

2. **執行步驟 1**:
   ```bash
   python step1_create_search_index.py
   ```
   等待索引建立完成

3. **執行步驟 2 - 選擇其中一種方式**:
   
   **選項 A: 命令行版本（基本測試）**:
   ```bash
   python step2_cli_create_ai_agent.py
   ```
   
   **選項 B: Chainlit UI 版本（推薦使用）**:
   ```bash
   chainlit run step2_ui_create_ai_agent.py -w
   ```
   - 在瀏覽器中會自動開啟 Chainlit UI
   - 可以點擊樣本問題按鈕快速測試
   - Agent ID 會顯示在介面中
   - 關閉瀏覽器時會自動清理 Agent
   
   **選項 B 的命令行測試模式**:
   ```bash
   python step2_ui_create_ai_agent.py
   ```

4. **執行步驟 3**:
   ```bash
   python step3_cleanup_resources.py --interactive
   ```
   根據提示清理資源

### 進階使用

#### 僅清理特定資源
```bash
# 僅清理 Agent
python step3_cleanup_resources.py --agents-only

# 僅清理索引
python step3_cleanup_resources.py --index-only
```
