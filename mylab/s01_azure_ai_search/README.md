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
├── step1_create_search_index.py    # 步驟 1: 建立搜索索引
├── step2_create_ai_agent.py        # 步驟 2: 建立 AI Agent
├── step3_cleanup_resources.py      # 步驟 3: 清理資源
├── README.md                       # 本說明文件
└── vector-search-quickstart.ipynb  # 原始 Jupyter Notebook
```

## 🔧 環境準備

### 系統需求

- Python 3.8 或更高版本
- Azure 訂閱帳戶
- Azure AI Studio 專案
- Azure AI Search 服務

### 安裝依賴套件

```bash
pip install azure-search-documents
pip install azure-ai-projects
pip install azure-identity
pip install python-dotenv
```

### 環境變數設定

創建 `.env` 檔案並設定以下變數：

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

### 步驟 2: 建立 AI Foundry Agent 和相關功能

**檔案**: `step2_create_ai_agent.py`

**功能說明**:
- 初始化 Azure AI Project 客戶端
- 驗證搜索索引可用性
- 建立具有搜索整合功能的 AI Agent
- 建立對話線程
- 測試 Agent 對話能力
- 比較有/無搜索工具的回覆差異
- 驗證 Agent 搜索整合潛力

**執行方式**:
```bash
python step2_create_ai_agent.py
```

**預期輸出**:
- ✅ AI Agent 建立成功
- ✅ 對話功能測試通過
- ✅ 搜索整合驗證完成

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

3. **執行步驟 2**:
   ```bash
   python step2_create_ai_agent.py
   ```
   測試 Agent 功能

4. **執行步驟 3**:
   ```bash
   python step3_cleanup_resources.py --interactive
   ```
   根據提示清理資源

### 進階使用

#### 自訂索引名稱
```bash
export AZURE_SEARCH_INDEX=my-custom-index
python step1_create_search_index.py
```

#### 僅清理特定資源
```bash
# 僅清理 Agent
python step3_cleanup_resources.py --agents-only

# 僅清理索引
python step3_cleanup_resources.py --index-only
```

## 🔍 功能特色

### Azure AI Search 功能
- **向量搜索**: 支援高維向量相似度搜索
- **混合搜索**: 結合全文搜索和向量搜索
- **語意搜索**: 提供智能搜索排序
- **篩選功能**: 支援複雜的查詢篩選條件
- **地理搜索**: 支援地理位置查詢

### AI Foundry Agent 功能
- **智能對話**: 自然語言對話介面
- **搜索整合**: 與 Azure AI Search 無縫整合
- **上下文記憶**: 維持對話上下文
- **工具使用**: 支援外部工具調用
- **多輪對話**: 支援複雜的多輪對話

### 整合優勢
- **準確性提升**: 透過搜索獲得最新和準確的資訊
- **相關性增強**: 向量搜索提供語意相關的結果
- **可擴展性**: 支援大規模文檔和用戶查詢
- **可控性**: 提供清晰的資料來源和引用

## 🛠️ 故障排除

### 常見問題

#### 1. 認證錯誤
**問題**: 無法連接到 Azure 服務
**解決方案**:
- 檢查 `.env` 檔案中的端點和 API 金鑰
- 確認 Azure 訂閱狀態
- 驗證服務區域設定

#### 2. 索引建立失敗
**問題**: 搜索索引建立不成功
**解決方案**:
- 檢查 Azure Search 服務層級和配額
- 確認索引名稱符合命名規則
- 驗證向量維度設定正確

#### 3. Agent 建立失敗
**問題**: AI Agent 無法建立
**解決方案**:
- 確認 AI Studio 專案已正確設定
- 檢查模型部署狀態
- 驗證專案端點 URL

#### 4. 搜索整合問題
**問題**: Agent 無法使用搜索功能
**解決方案**:
- 確認索引已建立並包含文檔
- 檢查搜索服務權限設定
- 驗證向量維度匹配

### 除錯技巧

#### 啟用詳細日誌
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 測試連接
```python
# 測試搜索服務連接
from azure.search.documents import SearchClient
search_client = SearchClient(endpoint, index_name, credential)
results = search_client.search("*", top=1)
```

#### 驗證環境變數
```python
import os
print("搜索端點:", os.getenv("AZURE_SEARCH_ENDPOINT"))
print("專案端點:", os.getenv("PROJECT_ENDPOINT"))
```

## 📈 效能優化

### 搜索效能
- 使用適當的向量演算法配置
- 設定合理的搜索結果數量限制
- 優化索引欄位設計

### Agent 效能
- 設定適當的對話超時時間
- 優化提示詞設計
- 使用快取機制減少重複查詢

## 🔒 安全性考量

### 資料保護
- 定期輪換 API 金鑰
- 使用 Azure Key Vault 存儲敏感資訊
- 啟用網路存取限制

### 權限管理
- 使用最小權限原則
- 設定適當的角色和權限
- 啟用審計日誌

## 📚 延伸學習

### 相關文檔
- [Azure AI Search 官方文檔](https://docs.microsoft.com/azure/search/)
- [Azure AI Studio 指南](https://docs.microsoft.com/azure/ai-studio/)
- [Azure AI Projects SDK](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects)

### 進階主題
- 自訂嵌入模型訓練
- 大規模向量索引優化
- 多語言搜索支援
- 即時索引更新

### 範例專案
- 企業知識庫搜索
- 電商產品推薦
- 文檔問答系統
- 客戶服務機器人

## 🤝 貢獻指南

歡迎提交問題報告、功能請求或程式碼貢獻！

### 報告問題
1. 描述問題現象
2. 提供重現步驟
3. 包含錯誤訊息和日誌

### 提交改進
1. Fork 此專案
2. 創建功能分支
3. 提交變更
4. 發起 Pull Request

## 📄 授權條款

此專案採用 MIT 授權條款。詳見 LICENSE 檔案。

## 🙋‍♀️ 聯絡方式

如有問題或建議，請透過以下方式聯絡：

- 建立 GitHub Issue
- 發送電子郵件至專案維護者
- 參與社群討論

---

**注意**: 此專案僅供學習和演示使用。在生產環境中使用前，請確保進行充分的測試和安全性評估。