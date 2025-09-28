# 多代理程式協作系統 (Multi-Agent Handoff System)

本系統整合了四個專門的 AI 代理程式，支援智慧移交和協作來完成複雜任務。

## 🤖 代理程式概覽

### 1. Azure AI Search Agent (搜尋代理)
- **專長**: 酒店搜尋、資訊檢索、向量搜尋
- **基於**: `step2_cli_create_ai_agent.py`
- **移交情況**: 當用戶要求發送郵件或數據分析時

### 2. Logic Apps Agent (自動化代理)  
- **專長**: 郵件發送、工作流程自動化、API 整合
- **基於**: `cli_logic_apps.py`
- **移交情況**: 當用戶要求搜尋或數據分析時

### 3. Microsoft Fabric Agent (數據分析代理)
- **專長**: 計程車數據分析、統計查詢、趨勢分析
- **基於**: `cli_agents_fabric.py`
- **移交情況**: 當用戶要求搜尋、郵件或複雜查詢時

### 4. Databricks Agent (資料科學代理)
- **專長**: 複雜查詢、機器學習、大數據處理
- **基於**: `cli_agent_adb_genie.py`  
- **移交情況**: 當用戶要求簡單任務時，可能降級移交

## 🚀 快速開始

### 1. 安裝依賴
```bash
pip install -r requirements.txt
```

### 2. 環境設定
```bash
cp .env.template .env
# 編輯 .env 檔案，填入你的實際配置值
```

### 3. 運行系統
```bash
python multi_agent_system.py
```

## 🔧 環境變數說明

### 必需變數
- `PROJECT_ENDPOINT`: Azure AI Foundry 專案端點
- `MODEL_DEPLOYMENT_NAME`: AI 模型部署名稱

### 選用變數 (各代理專用)

#### Azure AI Search Agent
- `AZURE_SEARCH_ENDPOINT`: 搜尋服務端點
- `AZURE_SEARCH_API_KEY`: 搜尋服務 API 金鑰
- `AZURE_SEARCH_INDEX`: 搜尋索引名稱

#### Logic Apps Agent  
- `AZURE_SUBSCRIPTION_ID`: Azure 訂閱 ID
- `AZURE_RESOURCE_GROUP`: 資源群組名稱
- `LOGIC_APP_NAME`: Logic App 名稱
- `TRIGGER_NAME`: 觸發器名稱
- `RECIPIENT_EMAIL`: 收件人郵件地址

#### Databricks Agent
- `FOUNDRY_PROJECT_ENDPOINT`: Foundry 專案端點
- `FOUNDRY_DATABRICKS_CONNECTION_NAME`: Databricks 連接名稱

## 💡 使用範例

### 互動模式
系統提供互動式選單，包含：
1. 預設示例任務
2. 系統狀態查看
3. 移交歷史記錄
4. 自定義任務執行

### 程式化使用
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

## 🔄 移交機制

### 移交類型
1. **FORWARD**: 轉發給特定代理
2. **ESCALATE**: 升級給更專業的代理  
3. **COLLABORATE**: 多代理協作
4. **COMPLETE**: 任務完成

### 移交邏輯示例
- 搜尋代理收到郵件請求 → 移交給自動化代理
- 數據代理收到複雜 ML 請求 → 升級給 Databricks 代理
- 任何代理收到跨領域請求 → 協作模式

## 📁 檔案結構

```
mylab/s05_multi_agents/
├── step4_handoff.py           # 移交基礎架構
├── specialized_agents.py     # 專門代理實現
├── multi_agent_system.py     # 主系統程式
├── requirements.txt          # 依賴套件
├── .env.template            # 環境變數模板
└── README.md               # 本文檔
```

## 🧪 測試案例

### 1. 單一代理任務
- "搜尋紐約的精品酒店" (Search Agent)
- "發送包含時間的郵件" (Logic Apps Agent)
- "分析計程車日夜行程差異" (Fabric Agent)

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

## 🛠 自定義擴展

### 添加新代理
1. 繼承 `BaseAgent` 類
2. 實現 `should_handoff()` 方法
3. 在 `specialized_agents.py` 中註冊
4. 在主系統中整合

### 自定義移交邏輯
修改各代理的 `should_handoff()` 方法，定義移交條件和目標代理。

## 🚨 故障排除

### 常見問題
1. **初始化失敗**: 檢查環境變數設定
2. **移交循環**: 檢查移交邏輯，避免循環引用
3. **代理無回應**: 檢查 Azure 連接和權限

### 日誌檢查
系統使用標準 Python logging，可調整日誌等級查看詳細信息。

## 📝 開發注意事項

- 各代理可獨立運行，無外部依賴時使用 mock 功能
- 移交機制防止無限循環 (最多 10 次移交)
- 支援異步處理，提升效能
- 完整的錯誤處理和資源清理

## 🎯 未來改進

- [ ] 添加更多移交策略
- [ ] 實現代理學習和優化
- [ ] 支援並行多代理執行
- [ ] 增強監控和分析功能
- [ ] WebUI 介面支援