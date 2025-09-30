# Azure AI Search 與 AI Foundry Agent 整合範例

## � 目錄 (Table of Contents)

- [專案概述](#-專案概述)
- [學習目標](#-學習目標)
- [檔案結構](#-檔案結構)
- [參考文件](#-參考文件)
- [詳細步驟說明](#-詳細步驟說明)
  - [步驟 1: 建立 AI Search 索引](#步驟-1-建立-ai-search-索引)
  - [步驟 2: 建立 AI Foundry Agent](#步驟-2-建立-ai-foundry-agent)
  - [步驟 3: 清理資源](#步驟-3-清理-ai-search-索引和-ai-foundry-agent)
- [使用指南](#-使用指南)
- [常見問題](#-常見問題)

## �📋 專案概述

此專案展示如何將 Azure AI Search 與 Azure AI Foundry Agent 進行整合，提供完整的向量搜索和智能對話功能。專案分為三個主要步驟，每個步驟都有對應的 Python 腳本。

## 🎯 學習目標

- 學習如何建立和配置 Azure AI Search 向量索引
- 了解如何使用 HNSW 演算法進行向量搜索
- 掌握語意搜索 (Semantic Search) 的配置與使用
- 了解如何創建和部署 AI Foundry Agent
- 掌握 AI Agent 與搜索服務的整合方法
- 學習如何正確清理和管理雲端資源

## 📁 檔案結構

```
mylab/s01_azure_ai_search/
├── step1_create_search_index.py       # 步驟 1: 建立向量搜索索引
├── step2_simple_search_agent.py       # 步驟 2: 建立 AI Agent 與搜索整合
├── step3_cleanup_resources.py         # 步驟 3: 清理資源
├── vector-search-quickstart.ipynb     # 完整功能展示的 Jupyter Notebook
├── .env.example                       # 環境變數範本檔案
├── README.md                          # 本說明文件
└── Ref/
    ├── ref-azure-search-quickstart.ipynb  # 原始參考的 Jupyter Notebook
    ├── step2_cli_create_ai_agent.py       # 參考: CLI 版本 AI Agent
    └── step2_ui_create_ai_agent.py        # 參考: Chainlit UI 版本 AI Agent
```

## � 參考文件

### 官方文件
- [Azure AI Search - 向量搜索快速入門 (Python)](https://learn.microsoft.com/zh-tw/azure/search/search-get-started-vector?tabs=keyless&pivots=python)

### 參考程式碼
- [Azure AI Foundry - Azure AI Search Agent 範例](https://github.com/azure-ai-foundry/foundry-samples/blob/main/samples/microsoft/python/getting-started-agents/azure_ai_search.py)
- [Azure Search Python Samples - Vector Search Quickstart](https://github.com/Azure-Samples/azure-search-python-samples/tree/main/Quickstart-Vector-Search)

## 📋 詳細步驟說明

### 步驟 1: 建立 AI Search 索引

**檔案**: `step1_create_search_index.py`

**功能說明**:
- 初始化 Azure Search 客戶端和認證
- 建立具有向量搜索功能的索引
  - 使用 HNSW (Hierarchical Navigable Small World) 演算法進行向量搜索
  - 配置語意搜索 (Semantic Search) 功能
  - 設定索引欄位與搜索配置
- 準備酒店文檔數據（包含預先計算的嵌入向量）
- 上傳文檔到索引
- 測試多種搜索功能：
  - 純向量搜索 (Pure Vector Search)
  - 混合搜索 (Hybrid Search - 結合向量與全文搜索)
  - 語意混合搜索 (Semantic Hybrid Search)

**執行方式**:
```bash
python step1_create_search_index.py
```

**預期輸出**:
- ✅ 索引建立成功 (包含向量搜索設定)
- ✅ 文檔上傳完成 (包含嵌入向量)
- ✅ 搜索功能測試通過 (向量、混合、語意搜索)

**關鍵特性**:
- **向量維度**: 1536 (OpenAI text-embedding-ada-002)
- **相似度度量**: Cosine similarity
- **語意配置**: 支援標題、內容、關鍵字的語意理解
- **索引欄位**: 包含 HotelName, Description, Category, Tags 等可搜索欄位

### 步驟 2: 建立 AI Foundry Agent

**檔案**: `step2_simple_search_agent.py`

**功能說明**:
- 初始化 Azure AI Project 客戶端與認證
- 配置 Azure AI Search 工具整合
  - 使用 **SEMANTIC** 查詢類型進行智能搜索
  - 設定 `top_k=3` 返回最相關的 3 筆結果
  - 支援篩選條件 (filter) 設定
- 建立專業的飯店推薦 AI Agent
  - Agent 名稱: `hotel-search-agent`
  - 具備飯店搜索與推薦的專業指令
  - 整合 Azure AI Search 工具資源
- 建立對話線程 (Thread) 進行多輪對話
- 執行測試查詢並展示 Agent 回應

**執行方式**:
```bash
python step2_simple_search_agent.py
```

**預期輸出**:
- ✅ AIProjectClient 初始化成功
- ✅ Azure AI Search 工具設置完成
- ✅ AI Agent 創建成功 (顯示 Agent ID)
- ✅ Thread 創建成功 (顯示 Thread ID)
- � 執行 4 個測試查詢並顯示 Agent 回應

**測試查詢範例**:
1. "What are the best hotels for budget-conscious travelers?"
2. "Can you recommend luxury hotels with spa facilities?"
3. "What hotels are near the city center?"
4. "Tell me about hotels with good ratings and reviews."

**Agent 特性**:
- **模型**: 使用環境變數中指定的模型部署 (如 gpt-4o)
- **搜索類型**: Semantic Search (語意搜索)
- **工具整合**: Azure AI Search 工具自動調用
- **對話管理**: 支援多輪對話與上下文理解

**環境變數需求**:
```bash
PROJECT_ENDPOINT=<your-ai-project-endpoint>
AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME=<model-name>  # 或 MODEL_DEPLOYMENT_NAME
AZURE_SEARCH_INDEX=vector-search-quickstart  # 可選，預設值
```

### 步驟 3: 清理 AI Search 索引和 AI Foundry Agent

**檔案**: `step3_cleanup_resources.py`

**功能說明**:
- 初始化環境和認證
- 列出並識別需要清理的資源
  - 列出所有 AI Agents
  - 列出所有 Search Indexes
- 安全刪除 AI Agent 和相關資源
  - 支援指定 Agent ID 進行刪除
  - 支援批次刪除所有 Agents
- 清理搜索索引和文檔
  - 刪除指定名稱的索引
  - 驗證索引刪除狀態
- 驗證清理完成狀態
- 提供清理摘要報告

**執行方式**:

基本模式（使用預設設定）：
```bash
python step3_cleanup_resources.py
```

互動模式（提供確認提示）：
```bash
python step3_cleanup_resources.py --interactive
```

指定 Agent ID 進行清理：
```bash
python step3_cleanup_resources.py --agent-id "your-agent-id"
```

強制清理（跳過確認）：
```bash
python step3_cleanup_resources.py --force
```

僅清理 Agents：
```bash
python step3_cleanup_resources.py --agents-only
```

僅清理索引：
```bash
python step3_cleanup_resources.py --index-only
```

**預期輸出**:
- 🔧 初始化環境變數和認證
- 📋 列出現有資源 (Agents, Indexes)
- 🗑️ 清理 AI Agents
- 🗑️ 清理搜索索引
- ✅ 驗證資源已被刪除
- 📊 清理摘要報告

**注意事項**:
- 刪除操作不可逆，請謹慎使用
- 建議先使用互動模式 (`--interactive`) 確認要刪除的資源
- 確保 `.env` 檔案中的環境變數正確設定

## 🎮 使用指南

### 完整流程執行

1. **執行步驟 1 - 建立搜索索引**:
   ```bash
   python step1_create_search_index.py
   ```
   - 建立具有向量搜索功能的索引
   - 上傳包含嵌入向量的酒店文檔
   - 測試向量搜索、混合搜索、語意搜索
   - 等待索引建立完成

2. **執行步驟 2 - 建立 AI Agent**:
   ```bash
   python step2_simple_search_agent.py
   ```
   - 初始化 AI Project Client
   - 建立具有 Azure AI Search 工具的 AI Agent
   - 建立對話線程
   - 執行 4 個測試查詢驗證功能
   - Agent 會自動調用 Azure AI Search 進行酒店資訊檢索

3. **執行步驟 3 - 清理資源**:
   ```bash
   python step3_cleanup_resources.py --interactive
   ```
   - 列出所有需要清理的資源
   - 根據提示確認刪除
   - 清理 AI Agents 和搜索索引
   - 驗證資源已被正確刪除

### 進階使用

#### 使用 Jupyter Notebook
```bash
# 啟動 Jupyter Notebook
jupyter notebook vector-search-quickstart.ipynb
```
- 包含完整的向量搜索示範
- 逐步執行每個步驟
- 可視化搜索結果

#### 自定義搜索查詢
在 `step2_simple_search_agent.py` 中修改測試查詢：
```python
test_queries = [
    "Your custom query here",
    "Another custom query",
]
run_queries(test_queries)
```

#### 調整搜索參數
在 `step2_simple_search_agent.py` 中修改搜索工具設定：
```python
ai_search_tool = AzureAISearchTool(
    index_connection_id="your-connection-id",
    index_name=index_name,
    query_type=AzureAISearchQueryType.SEMANTIC,  # 或 SIMPLE, FULL
    top_k=5,  # 調整返回結果數量
    filter="Category eq 'Boutique'",  # 添加篩選條件
)
```

#### 僅清理特定資源
```bash
# 僅清理 Agents
python step3_cleanup_resources.py --agents-only

# 僅清理索引
python step3_cleanup_resources.py --index-only

# 指定 Agent ID
python step3_cleanup_resources.py --agent-id "asst_xxxxx"

# 強制清理（跳過確認）
python step3_cleanup_resources.py --force
```

## ❓ 常見問題

### Q1: 如何取得 Azure AI Search 的端點和 API 金鑰？
**A**: 在 Azure Portal 中：
1. 前往您的 Azure AI Search 服務
2. 在左側選單中選擇「金鑰」(Keys)
3. 複製「URL」作為 `AZURE_SEARCH_ENDPOINT`
4. 複製「主要管理金鑰」作為 `AZURE_SEARCH_API_KEY`

### Q2: 如何取得 Azure AI Project 的端點？
**A**: 在 Azure AI Foundry Portal 中：
1. 前往您的 AI Project
2. 在「Overview」或「Settings」中找到 Project Endpoint
3. 複製完整的端點 URL 作為 `PROJECT_ENDPOINT`

### Q3: 向量嵌入 (Embeddings) 是如何生成的？
**A**: 在本範例中，文檔的嵌入向量已經預先計算並包含在程式碼中。實際應用中，您需要：
- 使用 OpenAI 的 `text-embedding-ada-002` 模型
- 或使用 Azure OpenAI 的嵌入服務
- 為每個文檔生成 1536 維的向量

### Q4: 什麼是 HNSW 演算法？
**A**: HNSW (Hierarchical Navigable Small World) 是一種高效的近似最近鄰搜索演算法：
- 專為大規模向量搜索設計
- 提供快速的查詢速度
- 在準確性和效能之間取得良好平衡
- Azure AI Search 使用此演算法進行向量搜索

### Q5: Semantic Search 與一般搜索有什麼不同？
**A**: 
- **一般搜索**: 基於關鍵字匹配
- **向量搜索**: 基於語意相似度
- **Semantic Search**: 結合 AI 模型理解查詢意圖，提供更智能的結果排序

### Q6: Agent 為什麼能夠搜索酒店資訊？
**A**: Agent 整合了 `AzureAISearchTool`，這個工具：
- 自動連接到 Azure AI Search 索引
- 根據用戶查詢生成搜索請求
- 將搜索結果整合到 Agent 的回應中
- 支援語意搜索 (SEMANTIC) 提供更相關的結果

### Q7: 如何修改 Agent 的行為？
**A**: 在 `step2_simple_search_agent.py` 中修改 `instructions` 參數：
```python
agent = project_client.agents.create_agent(
    model=model_deployment_name,
    name="hotel-search-agent",
    instructions="您的自定義指令...",  # 修改這裡
    tools=ai_search_tool.definitions,
    tool_resources=ai_search_tool.resources,
)
```

### Q8: 清理資源時出現錯誤怎麼辦？
**A**: 常見解決方法：
1. 確認環境變數設定正確
2. 檢查 Azure 服務是否正常運作
3. 確認您有足夠的權限刪除資源
4. 使用 `--force` 參數跳過確認
5. 手動在 Azure Portal 中刪除資源

### Q9: 可以使用其他資料集嗎？
**A**: 可以！您需要：
1. 準備您的資料集（JSON 格式）
2. 為每筆資料生成嵌入向量
3. 修改 `step1_create_search_index.py` 中的欄位定義
4. 更新 Agent 的指令以適應新的資料領域

### Q10: 這個範例的成本如何？
**A**: 主要成本來源：
- **Azure AI Search**: 根據服務層級和查詢量計費
- **Azure OpenAI/AI Models**: 根據 token 使用量計費
- **Azure AI Foundry**: 根據 Agent 運行時間和調用次數計費
- 建議使用免費層或開發層進行測試

## 📝 相關資源

### Ref 資料夾說明
`Ref/` 資料夾包含其他版本的實作範例：
- **ref-azure-search-quickstart.ipynb**: 原始參考的 Jupyter Notebook，包含詳細的中文註解
- **step2_cli_create_ai_agent.py**: 命令行版本的 AI Agent 實作，包含更多驗證和測試功能
- **step2_ui_create_ai_agent.py**: Chainlit UI 版本，提供網頁互動介面

這些檔案可作為參考或替代實作方式使用。
