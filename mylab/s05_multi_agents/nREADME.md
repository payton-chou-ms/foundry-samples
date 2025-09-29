# Multi-Agent Integration with Semantic Kernel

這個目錄包含了整合多個 Azure AI 服務的代理程式系統，使用 Semantic Kernel 和 Magentic 編排。

## 檔案說明

### 單一代理程式檔案
- `step1_azure_ai_agent_retrieval_ai_search.py` - Azure AI Search 整合代理程式
- `step1_azure_ai_agent_sk_databricks.py` - Databricks 資料分析代理程式  
- `step1_azure_ai_agent_sk_fabric.py` - Microsoft Fabric 商業智慧代理程式
- `step1_azure_ai_agent_sk_logic_app.py` - Logic Apps 工作流程自動化代理程式

### 多代理程式整合檔案
- `step2_sk_multi_agent_magentic.py` - 整合所有單一代理程式的 Magentic 編排系統
- `step5_magentic.py` - 原始的 Magentic 編排範例

## 功能特色

### 1. Azure AI Search Agent (AISearchAgent)
- 文檔搜尋和資訊檢索
- 搜尋趨勢分析
- 內容相關性評估

### 2. Databricks Agent (DatabricksAnalyst)  
- 大數據分析和處理
- 資料倉庫查詢
- 機器學習作業執行

### 3. Microsoft Fabric Agent (FabricBusinessAnalyst)
- Lakehouse 資料查詢
- 商業智慧報告生成
- KPI 分析和洞察

### 4. Logic Apps Agent (LogicAppOrchestrator)
- 自動化工作流程執行
- 系統健康監控
- 通知和警示管理

## 安裝需求

```bash
pip install -r requirements.txt
```

## 環境變數設定

在 `.env` 檔案中設定以下變數：

```env
# Azure AI 專案設定
PROJECT_ENDPOINT=<your-project-endpoint>
MODEL_DEPLOYMENT_NAME=<your-model-deployment-name>

# Azure OpenAI 設定
MY_AZURE_OPENAI_ENDPOINT=<your-openai-endpoint>

# Databricks 設定 (可選)
FOUNDRY_PROJECT_ENDPOINT=<your-foundry-endpoint>
FOUNDRY_DATABRICKS_CONNECTION_NAME=<your-databricks-connection>

# Logic Apps 設定 (可選)
LOGIC_APP_NAME=<your-logic-app-name>
TRIGGER_NAME=<your-trigger-name>
```

## 使用方式

### 執行單一代理程式
```bash
# 執行 AI Search 代理程式
python step1_azure_ai_agent_retrieval_ai_search.py

# 執行 Databricks 代理程式
python step1_azure_ai_agent_sk_databricks.py

# 執行 Fabric 代理程式  
python step1_azure_ai_agent_sk_fabric.py

# 執行 Logic Apps 代理程式
python step1_azure_ai_agent_sk_logic_app.py
```

### 執行多代理程式整合系統
```bash
python step2_sk_multi_agent_magentic.py
```

## 架構說明

多代理程式系統使用 **Magentic 編排模式**，包含以下組件：

1. **StandardMagenticManager**: 負責協調各個代理程式的工作
2. **InProcessRuntime**: 提供代理程式執行環境
3. **Agent Plugins**: 每個代理程式的具體功能實作
4. **Response Callbacks**: 用於監控和記錄代理程式互動

## 範例任務

整合系統可以處理複雜的企業級任務，例如：

- **數位轉型分析**: 結合技術文檔搜尋、資料分析、商業洞察和流程自動化
- **客戶體驗優化**: 分析客戶行為、搜尋相關案例、生成改善建議並自動執行
- **營運效率提升**: 監控系統性能、分析使用模式、建議優化策略並實施自動化

## 技術特點

- ✅ **模組化設計**: 每個代理程式獨立運作，可單獨測試和部署
- ✅ **錯誤處理**: 完整的異常處理和資源清理機制  
- ✅ **擴展性**: 易於新增新的代理程式和功能
- ✅ **監控能力**: 內建觀察和記錄功能
- ✅ **企業級**: 支援大規模部署和高可用性需求

## 注意事項

1. 確保有適當的 Azure 服務權限和連接設定
2. 某些功能使用模擬資料進行示範，實際部署時需要連接真實服務
3. 建議在測試環境中先驗證所有連接和功能
4. 監控 Azure 服務的使用量和成本

## 支援和貢獻

如有問題或建議，請參考 Microsoft Azure AI 文檔或提出 issue。