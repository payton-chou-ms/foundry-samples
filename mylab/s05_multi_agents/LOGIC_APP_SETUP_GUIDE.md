# Logic App 設定指南

本指南說明如何設定和使用 Azure Logic App 與 Azure AI Agent。

## 改進內容

參考 `cli_logic_apps.py` 的最佳實踐，`step1_azure_ai_agent_sk_logic_app.py` 已進行以下改進：

### 1. 環境變數管理
- 支援多個端點環境變數：`PROJECT_ENDPOINT` 或 `FOUNDRY_PROJECT_ENDPOINT`
- 增加完整的 Logic App 設定選項
- 新增環境變數驗證和錯誤提示

### 2. Logic App 連接方式
支援兩種 Logic App 連接模式：

#### 選項 1：直接 URL 模式 (推薦用於測試)
```bash
LOGIC_APP_EMAIL_TRIGGER_URL=https://prod-xxx.eastus.logic.azure.com:443/workflows/xxx/triggers/When_a_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2F...
```

#### 選項 2：Azure Management API 模式 (需要額外套件)
```bash
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=your-resource-group
LOGIC_APP_NAME=your-logic-app-name
TRIGGER_NAME=When_a_HTTP_request_is_received
```

### 3. 錯誤處理和降級
- 自動檢測可用的 Logic App 設定
- 當 Logic App 不可用時，使用模擬模式
- 提供清晰的錯誤訊息和設定指南

### 4. 增強的 LogicAppManager 類別
- 統一的郵件發送介面
- 支援多種連接模式的自動切換
- 完整的錯誤處理和狀態回報

## 環境變數設定

創建 `.env` 檔案並設定以下變數：

```bash
# 必要設定
PROJECT_ENDPOINT=https://your-foundry-endpoint.services.ai.azure.com/api/projects/your-project
MODEL_DEPLOYMENT_NAME=gpt-4o-mini

# Logic App 設定 (二選一)
# 選項 1 - 直接 URL
LOGIC_APP_EMAIL_TRIGGER_URL=https://prod-xxx.logic.azure.com:443/workflows/xxx/triggers/xxx/paths/invoke?api-version=2016-10-01&sp=xxx

# 選項 2 - Azure Management API
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=your-resource-group
LOGIC_APP_NAME=your-logic-app-name
TRIGGER_NAME=When_a_HTTP_request_is_received

# 選用設定
RECIPIENT_EMAIL=your-email@example.com
```

## 套件需求

```bash
# 基本需求
pip install azure-ai-projects azure-identity semantic-kernel

# 如果使用 Azure Management API 模式
pip install azure-mgmt-logic
```

## Logic App HTTP 觸發器設定

您的 Logic App 應該包含一個 HTTP 觸發器，接受以下 JSON 格式：

```json
{
  "to": "recipient@example.com",
  "subject": "Email subject",
  "body": "Email body content"
}
```

## 執行結果

成功執行後，您會看到類似以下的輸出：

```
✅ 成功註冊 Logic App 'your-logic-app' 觸發器 'When_a_HTTP_request_is_received'
使用端點: https://foundry.services.ai.azure.com/api/projects/your-project
Logic App 已設定並準備就緒
Created agent definition, agent ID: asst_xxx
Function Call:> LogicAppPlugin-send_email_via_logic_app with arguments: {"recipient":"...","subject":"...","body":"..."}
Function Result:> {"status": "success", "message": "寄送成功", "recipient": "...", "subject": "..."}
郵件已成功寄送至 ... 
```

## 疑難排解

1. **環境變數問題**：確保所有必要的環境變數都已正確設定
2. **Logic App 權限**：確保您有存取 Logic App 的適當權限
3. **網路連線**：確保可以存取 Azure Logic App 端點
4. **套件版本**：確保使用最新版本的 Azure SDK 套件