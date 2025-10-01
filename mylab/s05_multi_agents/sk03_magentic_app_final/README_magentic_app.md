# 多代理程式企業智能助手 - 重構版本

這是一個企業級多代理程式系統的重構版本，採用了良好的軟體架構設計原則，提供更好的可維護性、可擴展性和可測試性。

## 🏗️ 架構設計

### 模組化結構

```
s05_multi_agents/
├── config/                    # 配置管理
│   ├── __init__.py
│   └── settings.py           # 環境變數和設定管理
├── plugins/                   # 功能插件
│   ├── __init__.py
│   ├── ai_search_plugin.py   # AI Search 功能
│   ├── databricks_plugin.py  # Databricks 數據分析
│   ├── fabric_plugin.py      # Microsoft Fabric 商業智慧
│   └── logic_app_plugin.py   # Logic App 工作流程
├── agents/                    # 代理程式管理
│   ├── __init__.py
│   └── agent_factory.py      # 代理程式工廠
├── orchestration/             # 編排邏輯
│   ├── __init__.py
│   └── magentic_orchestrator.py # Magentic 編排器
├── utils/                     # 工具模組
│   ├── __init__.py
│   ├── connection_manager.py  # 連接管理
│   ├── logic_app_manager.py   # Logic App 管理
│   └── menu_helper.py        # 選單和UI輔助
├── main.py                   # 主入口點
├── step2_sk_multi_agent_magentic.py  # 原始檔案（保留參考）
└── README_refactored.md      # 本文檔
```

### 設計原則

1. **單一職責原則 (SRP)**: 每個模組和類別都有明確的單一責任
2. **開放封閉原則 (OCP)**: 對擴展開放，對修改封閉
3. **依賴反轉原則 (DIP)**: 高層模組不依賴低層模組，都依賴抽象
4. **介面隔離原則 (ISP)**: 客戶端不應該依賴它不需要的介面
5. **模組化設計**: 清晰的模組邊界和職責分離

## 🚀 使用方式

### 快速開始

```bash
# 使用重構後的主程式
python main.py

# 或者使用原始檔案（向後相容）
python step2_sk_multi_agent_magentic.py
```

### 環境變數設定

確保設定以下環境變數：

```bash
# 必要設定
MY_AZURE_OPENAI_ENDPOINT=your_openai_endpoint
FOUNDRY_PROJECT_ENDPOINT=your_foundry_endpoint

# 可選設定
MODEL_DEPLOYMENT_NAME=gpt-4o-mini
FOUNDRY_DATABRICKS_CONNECTION_NAME=your_databricks_connection
FABRIC_CONNECTION_NAME=your_fabric_connection

# Logic App 設定（擇一）
LOGIC_APP_EMAIL_TRIGGER_URL=your_direct_url
# 或者
AZURE_SUBSCRIPTION_ID=your_subscription_id
AZURE_RESOURCE_GROUP=your_resource_group
LOGIC_APP_NAME=your_logic_app_name
TRIGGER_NAME=your_trigger_name
```

## 🔧 架構組件說明

### 1. 配置模組 (`config/`)

- **`settings.py`**: 統一管理所有環境變數和應用程式設定
- 提供配置驗證功能
- 集中化配置管理，易於維護

### 2. 插件模組 (`plugins/`)

每個插件封裝特定的業務邏輯：

- **`ai_search_plugin.py`**: Azure AI Search 功能
- **`databricks_plugin.py`**: Databricks Genie API 數據查詢
- **`fabric_plugin.py`**: Microsoft Fabric 商業智慧分析
- **`logic_app_plugin.py`**: Azure Logic Apps 工作流程自動化

### 3. 代理程式模組 (`agents/`)

- **`agent_factory.py`**: 使用工廠模式創建和配置代理程式
- 封裝代理程式創建邏輯
- 統一管理代理程式的配置和初始化

### 4. 編排模組 (`orchestration/`)

- **`magentic_orchestrator.py`**: 封裝 Magentic 編排邏輯
- 管理多代理程式協作
- 提供統一的查詢處理介面

### 5. 工具模組 (`utils/`)

- **`connection_manager.py`**: 管理所有外部服務連接
- **`logic_app_manager.py`**: Logic App 專用管理器
- **`menu_helper.py`**: UI 和選單輔助功能

## 🎯 重構優勢

### 1. **可維護性**
- 程式碼按功能模組化，易於理解和修改
- 清晰的職責分離，降低耦合度
- 統一的錯誤處理和日誌記錄

### 2. **可擴展性**
- 新增代理程式只需在 `AgentFactory` 中添加方法
- 新增插件只需實現對應的插件類別
- 配置變更集中在 `settings.py`

### 3. **可測試性**
- 每個模組可以獨立進行單元測試
- 插件邏輯與代理程式邏輯分離
- 依賴注入模式便於模擬測試

### 4. **可重用性**
- 插件可以在不同代理程式間重用
- 連接管理器可以被其他系統使用
- 編排邏輯可以應用到不同的代理程式組合

## 📊 系統功能

### 支援的代理程式

1. **AI Search Agent** 🔍
   - 飯店推薦和搜尋
   - 技術文檔檢索
   - 企業知識庫查詢

2. **Databricks Agent** 📊
   - 大數據分析
   - 機器學習模型查詢
   - 商業指標計算

3. **Fabric Agent** 📈
   - 商業智慧分析
   - 計程車數據洞察
   - KPI 儀表板查詢

4. **Logic App Agent** ⚡
   - 電子郵件自動化
   - 工作流程編排
   - 時間和排程管理

### 支援的查詢類型

- **單一代理程式查詢**: 針對特定領域的專業問題
- **多代理程式協作**: 需要多個專業領域協作的複雜任務
- **跨領域整合**: 結合搜尋、分析、通知的完整業務流程

## 🔄 遷移指南

從原始檔案 (`step2_sk_multi_agent_magentic.py`) 遷移到新架構：

1. **配置遷移**: 環境變數設定保持不變
2. **功能保持**: 所有原有功能完全保留
3. **介面相容**: 使用者操作介面保持一致
4. **逐步遷移**: 可以同時運行兩個版本進行比較

## 🧪 測試建議

### 單元測試

```python
# 測試插件功能
def test_ai_search_plugin():
    plugin = AISearchPlugin()
    result = plugin.search_documents("test query")
    assert "已搜尋查詢" in result

# 測試配置管理
def test_settings_validation():
    from config import settings
    # 測試配置驗證邏輯
```

### 整合測試

```python
# 測試代理程式創建
async def test_agent_factory():
    factory = AgentFactory(connection_manager, logic_app_manager)
    agents = await factory.create_all_agents(client)
    assert len(agents) == 4
```

## 📝 開發指南

### 添加新代理程式

1. 在 `plugins/` 中創建新的插件類別
2. 在 `AgentFactory` 中添加創建方法
3. 更新 `create_all_agents` 方法
4. 添加對應的配置項目

### 添加新功能

1. 在對應插件中添加新的 `@kernel_function`
2. 更新代理程式的工具定義
3. 測試新功能的整合

### 修改配置

1. 在 `settings.py` 中添加新的配置項目
2. 更新配置驗證邏輯
3. 更新相關文檔

## 🔗 相關資源

- [Azure AI Foundry 文檔](https://docs.microsoft.com/azure/ai-foundry/)
- [Semantic Kernel 文檔](https://docs.microsoft.com/semantic-kernel/)
- [Azure Logic Apps 文檔](https://docs.microsoft.com/azure/logic-apps/)
- [Databricks Genie API](https://docs.databricks.com/genie/)
- [Microsoft Fabric 文檔](https://docs.microsoft.com/fabric/)

## 📞 支援

如有問題或建議，請聯繫開發團隊或提交 Issue。