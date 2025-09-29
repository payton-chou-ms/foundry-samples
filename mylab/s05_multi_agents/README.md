# 多代理程式協作系統 (Multi-Agent Handoff System)

本系統整合了四個專門的 AI 代理程式，支援智慧移交和協作來完成複雜任務。提供兩種實現方式：Azure AI Projects 版本和 Semantic Kernel 版本。

## 🎯 系統概覽

本系統基於四個 CLI 腳本轉換而來的代理程式，整合了 handoff 功能，成為支援多代理協作的完整系統。

### 四個專門代理程式

1. **Azure AI Search Agent (搜尋代理)**
   - 專長：酒店搜尋、資訊檢索、向量搜尋
   - 基於：`step2_cli_create_ai_agent.py`
   - 移交情況：當用戶要求發送郵件或數據分析時

2. **Logic Apps Agent (自動化代理)**
   - 專長：郵件發送、工作流程自動化、API 整合
   - 基於：`cli_logic_apps.py`
   - 移交情況：當用戶要求搜尋或數據分析時

3. **Microsoft Fabric Agent (數據分析代理)**
   - 專長：計程車數據分析、統計查詢、趋勢分析
   - 基於：`cli_agents_fabric.py`
   - 移交情況：當用戶要求搜尋、郵件或複雜查詢時

4. **Databricks Agent (資料科學代理)**
   - 專長：複雜查詢、機器學習、大數據處理
   - 基於：`cli_agent_adb_genie.py`
   - 移交情況：當用戶要求簡單任務時，可能降級移交

## 🏗️ 系統架構

### Azure AI Projects 版本架構
```
MultiAgentSystem
├── HandoffOrchestrator          # 移交協調器
├── AzureAISearchAgent          # Azure AI 搜尋代理
├── LogicAppsAgent              # Logic Apps 自動化代理
├── FabricAgent                 # Microsoft Fabric 數據分析代理
└── DatabricksAgent             # Azure Databricks 資料科學代理
```

### Semantic Kernel 版本架構
```
SemanticKernelMultiAgentSystem
├── SemanticKernelOrchestrator   # SK 移交協調器
├── SemanticKernelSearchAgent    # SK 搜尋代理
├── SemanticKernelLogicAgent     # SK 自動化代理
├── SemanticKernelFabricAgent    # SK 數據分析代理
└── SemanticKernelDatabricksAgent # SK 資料科學代理
```

## 🔄 移交機制

### 移交類型
1. **FORWARD**: 轉發給特定代理
2. **ESCALATE**: 升級給更專業的代理
3. **COLLABORATE**: 多代理協作
4. **COMPLETE**: 任務完成

### 移交邏輯示例

| 起始代理 | 任務類型 | 移交目標 | 移交類型 |
|---------|---------|---------|---------|
| Search Agent | 郵件發送 | Logic Apps Agent | Forward |
| Logic Apps Agent | 搜尋查詢 | Search Agent | Forward |
| Fabric Agent | 複雜ML分析 | Databricks Agent | Escalate |
| Databricks Agent | 簡單統計 | Fabric Agent | Forward |

## 🚀 安裝與設定

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 環境變數設定

複製環境變數模板：
```bash
cp .env.template .env
```

#### Azure AI Projects 版本必需變數
```bash
PROJECT_ENDPOINT=https://your-project-endpoint.com
MODEL_DEPLOYMENT_NAME=your-model-deployment
```

#### Semantic Kernel 版本必需變數
```bash
AZURE_OPENAI_ENDPOINT=https://your-openai-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
MODEL_DEPLOYMENT_NAME=gpt-4o
```

#### 各代理專用環境變數

**Azure AI Search Agent**
```bash
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_API_KEY=your-search-api-key
AZURE_SEARCH_INDEX=your-index-name
```

**Logic Apps Agent**
```bash
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=your-resource-group
LOGIC_APP_NAME=your-logic-app-name
TRIGGER_NAME=your-trigger-name
RECIPIENT_EMAIL=recipient@example.com
```

**Databricks Agent**
```bash
FOUNDRY_PROJECT_ENDPOINT=your-foundry-endpoint
FOUNDRY_DATABRICKS_CONNECTION_NAME=your-databricks-connection
```

## 💻 使用方式

### Azure AI Projects 版本

```bash
# 互動模式
python multi_agent_system.py
```

### Semantic Kernel 版本

```bash
# 互動模式
python multi_agent_system_sk.py
```

### 程式化使用

#### Azure AI Projects 版本
```python
from multi_agent_system import MultiAgentSystem

async def example():
    system = MultiAgentSystem()
    await system.initialize()
    
    # 執行任務，支援自動移交
    result = await system.execute_task(
        task="搜尋紐約的精品酒店並發郵件通知",
        initial_agent="search"
    )
    
    await system.cleanup()
```

#### Semantic Kernel 版本
```python
from multi_agent_system_sk import SemanticKernelMultiAgentSystem

async def example():
    system = SemanticKernelMultiAgentSystem()
    await system.initialize()
    
    result = await system.execute_task(
        task="搜尋紐約的精品酒店並發郵件通知",
        initial_agent="search"
    )
    
    await system.cleanup()
```

## 📊 兩種實現比較

| 特性 | Azure AI Projects | Semantic Kernel |
|------|------------------|-----------------|
| 代理基礎 | AIProjectClient.agents | ChatCompletionAgent |
| 函數系統 | ToolSet + FunctionTool | @kernel_function |
| 運行時 | Azure AI Projects Runtime | InProcessRuntime |
| 擴展性 | 受限於 Azure AI Projects | 豐富的 SK 生態系 |
| 學習曲線 | Azure 特定 | 業界標準 |
| 社區支持 | Azure 文檔 | 開源社區 |

## 🎯 系統特色

1. **智慧移交**: 自動檢測任務需求並移交給最適合的代理
2. **無縫整合**: 四個原始CLI腳本完美轉換為協作代理
3. **彈性部署**: 支援完整Azure環境配置
4. **完整監控**: 詳細的執行歷史和移交記錄
5. **錯誤恢復**: 完善的錯誤處理和資源清理
6. **循環防護**: 防止代理間無限循環移交 (最多10次)
7. **上下文保持**: 移交時保留任務上下文和執行歷史

## 📁 檔案結構

```
mylab/s05_multi_agents/
├── step4_handoff.py                    # Azure AI Projects 移交基礎架構
├── specialized_agents.py               # Azure AI Projects 專門代理實現
├── multi_agent_system.py               # Azure AI Projects 主系統程式
├── step4_handoff_semantic_kernel.py    # SK 移交基礎架構
├── specialized_agents_sk.py            # SK 專門代理實現
├── multi_agent_system_sk.py           # SK 主系統程式
├── requirements.txt                    # 依賴套件
├── .env.template                      # 環境變數模板
└── COMPREHENSIVE_README.md            # 本文檔
```

## 🧪 使用案例

### 1. 單一代理任務
- "搜尋紐約的精品酒店" (Search Agent)
- "發送包含時間的郵件" (Logic Apps Agent)
- "分析計程車日夜行程差異" (Fabric Agent)
- "使用 Genie 進行複雜資料查詢" (Databricks Agent)

### 2. 跨代理協作
- "搜尋酒店並發郵件通知" (Search → Logic Apps)
- "分析數據並進行 ML 預測" (Fabric → Databricks)

### 3. 複雜工作流程
- "搜尋酒店，分析該地區交通，並發送報告郵件" (多代理協作)

## 📊 監控與日誌

系統提供：
- 執行歷史記錄
- 移交次數統計
- 代理狀態監控
- 錯誤日誌記錄
- 詳細的執行歷史和移交記錄

## 🛠 自定義擴展

### Azure AI Projects 版本

#### 添加新代理
1. 繼承 `BaseAgent` 類
2. 實現 `should_handoff()` 方法
3. 在 `specialized_agents.py` 中註冊
4. 在主系統中整合

#### 自定義移交邏輯
修改各代理的 `should_handoff()` 方法，定義移交條件和目標代理。

### Semantic Kernel 版本

#### 添加新的 Plugin
1. 創建 Plugin 類並使用 `@kernel_function` 裝飾器
2. 在代理初始化時添加 plugin
3. 在 instructions 中描述新功能

#### Plugin 開發範例
```python
from semantic_kernel.functions import kernel_function

class MyCustomPlugin:
    @kernel_function(name="my_function", description="自定義功能描述")
    def my_function(self, input_data: str) -> str:
        # 實現功能邏輯
        return f"處理結果: {input_data}"
```

## 🚨 故障排除

### 常見問題

1. **初始化失敗**: 檢查環境變數設定
2. **移交循環**: 檢查移交邏輯，避免循環引用
3. **代理無回應**: 檢查 Azure 連接和權限
4. **Semantic Kernel 未安裝**: `pip install semantic-kernel`
5. **OpenAI 配置錯誤**: 檢查 `AZURE_OPENAI_ENDPOINT` 和 `AZURE_OPENAI_API_KEY`

### 日誌檢查
系統使用標準 Python logging，可調整日誌等級查看詳細信息。

## 📝 開發注意事項

- 各代理可獨立運行，具有完整的錯誤處理
- 移交機制防止無限循環 (最多 10 次移交)
- 支援異步處理，提升效能
- 完整的錯誤處理和資源清理
- 兩種實現都提供相同的核心功能

## 🎯 技術實現總結

### 已完成項目

1. **四個 Single Agent 實現**
   - ✅ `AzureAISearchAgent` / `SemanticKernelSearchAgent`
   - ✅ `LogicAppsAgent` / `SemanticKernelLogicAgent`
   - ✅ `FabricAgent` / `SemanticKernelFabricAgent`
   - ✅ `DatabricksAgent` / `SemanticKernelDatabricksAgent`

2. **Handoff 多代理能力整合**
   - ✅ 移交基礎架構
   - ✅ 智慧移交邏輯 (自動檢測任務類型)
   - ✅ 多種移交類型 (Forward, Escalate, Collaborate, Complete)
   - ✅ 循環防護機制 (最多10次移交)
   - ✅ 上下文保持和執行歷史

3. **完整系統整合**
   - ✅ 主系統協調器
   - ✅ 互動式操作介面
   - ✅ 完整的錯誤處理和資源管理
   - ✅ 兩種實現方式 (Azure AI Projects + Semantic Kernel)

## 📚 相關資源

- [Semantic Kernel 官方文檔](https://learn.microsoft.com/en-us/semantic-kernel/)
- [Azure AI Projects 文檔](https://learn.microsoft.com/en-us/azure/ai-services/agents/)
- [Azure AI Search 文檔](https://learn.microsoft.com/en-us/azure/search/)
- [Azure Logic Apps 文檔](https://learn.microsoft.com/en-us/azure/logic-apps/)

## 🎉 結論

本多代理程式協作系統成功實現了：
- **完整的代理轉換**: 四個 CLI 腳本成功轉換為協作代理
- **智慧移交機制**: 自動檢測並移交給最適合的代理
- **雙重實現**: 提供 Azure AI Projects 和 Semantic Kernel 兩種版本
- **生產就緒**: 完整的錯誤處理、監控和文檔

系統已準備好在實際環境中部署使用，提供強大的多代理協作能力！