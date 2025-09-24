# Azure Logic Apps 互動式演示系統

## 概述

這個增強版的 Azure Logic Apps 演示系統提供了一個功能完整的互動式聊天介面，展示了 Azure Logic Apps 與 Azure AI Foundry 的強大整合能力。系統支援多種 Logic Apps 應用場景，包括電子郵件發送、通知管理、資料處理等。

## 主要特色

### 🎯 核心功能
- **互動式聊天界面**: 提供自然語言對話體驗
- **多 Logic Apps 整合**: 支援同時管理多個 Logic Apps
- **即時回應處理**: 快速處理用戶請求並執行相應操作
- **詳細日誌記錄**: 完整的對話歷史和執行記錄
- **錯誤處理機制**: 完善的錯誤處理和用戶反饋

### 🔧 支援的功能模組

#### 📧 電子郵件服務
- 透過 Logic Apps 發送電子郵件
- 支援自訂收件人、主題和內容
- 即時發送狀態回饋

#### 🕒 時間與日期
- 獲取當前時間和日期
- 支援自訂時間格式
- 時區處理功能

#### 🌤️ 天氣資訊
- 查詢指定地區天氣
- 模擬天氣 API 整合
- 多地區天氣支援

#### 🧮 數學計算
- 基本數學運算
- 溫度單位轉換
- 數值處理功能

#### 📊 資料處理
- 字典合併操作
- 記錄批次處理
- 文字分析功能

#### 👤 用戶管理
- 用戶資訊查詢
- 使用者資料管理
- 身分驗證支援

## 系統架構

```
interactive_logic_apps_demo.py
├── InteractiveLogicAppsDemo (主要類別)
│   ├── __init__() - 系統初始化
│   ├── _load_configuration() - 載入設定檔
│   ├── _setup_clients() - 設定 Azure 客戶端
│   ├── _setup_logic_apps() - 設定 Logic Apps 工具
│   ├── _create_enhanced_functions() - 建立增強功能集
│   ├── _setup_agent() - 設定 AI 代理
│   ├── start_interactive_chat() - 啟動互動聊天
│   ├── run_demo_scenarios() - 執行演示場景
│   └── _cleanup() - 清理資源
├── user_functions.py (工具函數模組)
└── user_logic_apps.py (Logic Apps 整合模組)
```

## 環境設定

### 必要環境變數
```env
# Azure AI Foundry 設定
PROJECT_ENDPOINT=your-project-endpoint-here
MODEL_DEPLOYMENT_NAME=your-model-deployment-name

# Azure 訂閱設定
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=your-resource-group-name

# Logic Apps 設定
EMAIL_LOGIC_APP_NAME=your-email-logic-app-name
EMAIL_TRIGGER_NAME=When_a_HTTP_request_is_received
RECIPIENT_EMAIL=your-recipient-email@example.com
```

### 可選環境變數
```env
# 額外的 Logic Apps 設定
NOTIFICATION_LOGIC_APP_NAME=your-notification-logic-app-name
DATA_PROCESSING_LOGIC_APP_NAME=your-data-processing-logic-app-name
```

## 安裝與設定

### 1. 安裝相依套件
```bash
pip install azure-ai-projects azure-ai-agents azure-identity python-dotenv requests
```

### 2. 設定環境檔案
1. 複製 `.env.example` 為 `.env`
2. 填入實際的 Azure 設定值
3. 確保所有必要變數都已設定

### 3. Azure 資源準備

#### Logic Apps 設定
1. 在 Azure Portal 建立 Logic Apps
2. 設定 HTTP 請求觸發器
3. 配置適當的 JSON 結構描述：
   ```json
   {
       "type": "object",
       "properties": {
           "to": {"type": "string"},
           "subject": {"type": "string"},
           "body": {"type": "string"}
       }
   }
   ```

#### Azure AI Foundry 設定
1. 建立 Azure AI Foundry 專案
2. 部署適當的語言模型
3. 取得專案端點和模型部署名稱

## 使用方式

### 啟動互動式聊天
```bash
python interactive_logic_apps_demo.py
```

### 執行自動化演示
```bash
python interactive_logic_apps_demo.py --demo
```

## 功能演示範例

### 📧 發送電子郵件
**用戶輸入**: "幫我發送郵件給 john@example.com，主題是會議提醒，內容是明天下午2點有重要會議"

**系統回應**: 
```
✅ 電子郵件發送成功！
收件人: john@example.com
主題: 會議提醒
內容: 明天下午2點有重要會議
Logic App 執行狀態: 成功
```

### 🕒 時間查詢
**用戶輸入**: "現在幾點？"

**系統回應**:
```
📅 當前時間資訊：
時間: 2024-01-15 14:30:25
格式: 標準格式 (%Y-%m-%d %H:%M:%S)
```

### 🌤️ 天氣查詢
**用戶輸入**: "查詢台北的天氣"

**系統回應**:
```
🌤️ 天氣資訊：
地點: 台北
天氣狀況: 多雲，溫度 22°C
(註: 此為模擬資料，實際應用中會整合真實天氣 API)
```

### 🧮 數學計算
**用戶輸入**: "計算 45 加 55"

**系統回應**:
```
🧮 計算結果：
45 + 55 = 100
```

### 🌡️ 溫度轉換
**用戶輸入**: "將 25 度攝氏轉換為華氏"

**系統回應**:
```
🌡️ 溫度轉換：
25°C = 77.0°F
轉換公式: (°C × 9/5) + 32 = °F
```

## 進階功能

### 🔗 多 Logic Apps 整合
系統支援同時整合多個 Logic Apps：

```python
# 系統會自動偵測並註冊可用的 Logic Apps
logic_apps_config = {
    "email_app": "EmailLogicApp",
    "notification_app": "NotificationLogicApp", 
    "data_processing_app": "DataProcessingLogicApp"
}
```

### 📊 對話歷史記錄
系統會自動保存對話歷史：
- 時間戳記
- 用戶輸入
- 系統回應
- 處理時間
- 執行結果

### 🎛️ 自訂 Logic Apps 函數
可以動態建立自訂 Logic Apps 函數：

```python
def _create_logic_app_function(self, logic_app_name: str, function_name: str):
    """建立專用的 Logic App 調用函數"""
    def logic_app_function(payload_json: str) -> str:
        # 處理自訂 payload 並調用 Logic App
        payload = json.loads(payload_json)
        result = self.logic_app_tool.invoke_logic_app(logic_app_name, payload)
        return json.dumps(result)
    return logic_app_function
```

## 錯誤處理

### 常見問題與解決方案

#### 🔧 環境變數未設定
```
❌ 錯誤: 缺少必要的環境變數: PROJECT_ENDPOINT, MODEL_DEPLOYMENT_NAME
```
**解決方案**: 檢查 `.env` 檔案是否正確設定

#### 🔧 Logic App 註冊失敗
```
⚠️ Logic App 註冊失敗 (EmailLogicApp): No callback URL returned
```
**解決方案**: 
1. 檢查 Logic App 名稱是否正確
2. 確認觸發器名稱匹配
3. 驗證 Azure 權限設定

#### 🔧 AI 代理初始化失敗
```
❌ 智能代理設定失敗: Authentication failed
```
**解決方案**:
1. 檢查 Azure 認證設定
2. 驗證專案端點 URL
3. 確認模型部署狀態

### 除錯模式
可以啟用詳細日誌來協助除錯：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 效能最佳化

### 💡 最佳實務建議

#### 1. 環境設定
- 使用環境變數管理敏感資訊
- 定期更新 Azure SDK 版本
- 設定適當的超時時間

#### 2. Logic Apps 設計
- 使用適當的 JSON 結構描述
- 實作錯誤處理機制
- 設定重試原則

#### 3. 對話管理
- 限制對話歷史長度
- 實作對話狀態管理
- 設定合理的回應時間

## 安全性考量

### 🔒 安全措施

#### 1. 認證與授權
- 使用 Azure AD 身分驗證
- 實作最小權限原則
- 定期輪替存取金鑰

#### 2. 資料保護
- 加密敏感資料傳輸
- 實作資料遮罩機制
- 設定適當的存取控制

#### 3. 日誌與監控
- 記錄重要操作事件
- 設定異常警報機制
- 實作審核追蹤功能

## 客製化與擴展

### 🎨 客製化選項

#### 1. 新增自訂函數
```python
def custom_business_function(param1: str, param2: int) -> str:
    """自訂業務邏輯函數"""
    # 實作自訂邏輯
    result = {"custom_result": f"{param1}_{param2}"}
    return json.dumps(result)

# 加入函數集合
user_functions.add(custom_business_function)
```

#### 2. 客製化 AI 指令
修改 `_get_agent_instructions()` 方法來自訂 AI 代理行為：

```python
def _get_agent_instructions(self) -> str:
    return """
    您是專門的業務助理，專精於：
    1. 客戶關係管理
    2. 訂單處理流程
    3. 庫存管理系統
    ... (自訂指令)
    """
```

#### 3. 擴展 Logic Apps 整合
新增更多 Logic Apps 類型：

```python
"crm_app": {
    "name": os.environ.get("CRM_LOGIC_APP_NAME"),
    "trigger": os.environ.get("CRM_TRIGGER_NAME")
},
"inventory_app": {
    "name": os.environ.get("INVENTORY_LOGIC_APP_NAME"), 
    "trigger": os.environ.get("INVENTORY_TRIGGER_NAME")
}
```

## 測試與驗證

### 🧪 測試策略

#### 1. 單元測試
```python
import pytest
from interactive_logic_apps_demo import InteractiveLogicAppsDemo

def test_configuration_loading():
    """測試設定檔載入功能"""
    demo = InteractiveLogicAppsDemo()
    assert demo.config["PROJECT_ENDPOINT"] is not None
    
def test_logic_app_function_creation():
    """測試 Logic App 函數建立"""
    demo = InteractiveLogicAppsDemo()
    func = demo._create_logic_app_function("TestApp", "test_function")
    assert callable(func)
```

#### 2. 整合測試
- 測試 Azure AI 連線
- 驗證 Logic Apps 註冊
- 檢查端到端對話流程

#### 3. 效能測試
- 回應時間測量
- 並發處理能力
- 記憶體使用量監控

## 部署指南

### 🚀 生產環境部署

#### 1. 容器化部署
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "interactive_logic_apps_demo.py"]
```

#### 2. Azure 容器執行個體
```bash
az container create \
    --resource-group myResourceGroup \
    --name logic-apps-demo \
    --image myregistry.azurecr.io/logic-apps-demo:latest \
    --environment-variables PROJECT_ENDPOINT=xxx MODEL_DEPLOYMENT_NAME=xxx
```

#### 3. 監控與警報
- 設定 Application Insights
- 配置健康狀態檢查
- 實作自動化重啟機制

## 問題回報與支援

如遇到問題，請提供以下資訊：

1. **錯誤訊息**: 完整的錯誤堆疊追蹤
2. **環境資訊**: Python 版本、Azure SDK 版本
3. **設定檔案**: 匿名化的環境變數設定
4. **重現步驟**: 詳細的操作步驟

### 📞 支援管道
- GitHub Issues: 功能請求與錯誤回報
- 技術文件: 詳細的 API 參考
- 社群論壇: 使用經驗分享與討論

## 版本歷史

### v1.0.0 (2024-01-15)
- ✨ 初版發布
- 🔧 基礎互動式聊天介面
- 📧 電子郵件 Logic Apps 整合
- 🧮 核心工具函數集
- 📝 繁體中文使用者介面

### 未來規劃
- 🌐 多語言支援
- 📱 行動裝置最佳化
- 🔐 進階安全功能
- 📊 分析與報告功能
- 🤖 進階 AI 功能整合

---

*此文件使用繁體中文撰寫，旨在提供完整的 Azure Logic Apps 互動式演示系統使用指南。*