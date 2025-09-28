# Azure Logic Apps 與 Azure AI Foundry Agent 整合範例

這個範例展示如何使用 Azure AI Agents 與 Azure Logic Apps 整合，透過 Logic Apps 工作流程執行自動化任務（包括發送電子郵件等）。專案提供了命令行版本和 Chainlit Web UI 版本。

## 功能特色

- **Logic Apps 整合**: 透過 Azure Logic Apps 執行自動化工作流程
- **電子郵件自動化**: 使用 Logic Apps 發送自動化電子郵件
- **命令行介面**: `logic_apps.py` 提供基本的命令行執行
- **Web UI 介面**: `ui_logic_apps.py` 提供 Chainlit 互動式網頁介面
- **預設任務按鈕**: UI 版本包含5個預設自動化任務的快速執行按鈕
- **即時狀態更新**: 工作流程執行時的即時狀態回饋
- **自動資源清理**: 會話結束時自動清理 Agent 資源
- **繁體中文 UI**: 使用者介面採用繁體中文，技術術語保留英文

## 先決條件

1. **Azure AI Foundry Project**: 已設定並部署模型的專案
2. **Azure Logic App**: 在與 AI Project 相同的資源群組中建立 Logic App
3. **Logic App 設定**: HTTP 觸發器設定為接受包含 'to'、'subject' 和 'body' 的 JSON 參數

## 檔案結構

```
mylab/s02_azure_logic_app/
├── logic_apps.py           # 命令行版本的 Logic App 整合
├── ui_logic_apps.py        # Chainlit Web UI 版本
├── user_logic_apps.py      # Logic Apps 工具類別實作
├── user_functions.py       # 工具函數（日期/時間、天氣、計算等）
├── requirements.txt        # Python 依賴套件清單
├── .env.example           # 環境變數範本檔案
└── README.md              # 本說明文件
```

## 安裝與設定

### 1. 安裝必要依賴

```bash
pip install -r requirements.txt
```

### 2. 設定環境變數

複製 `.env.example` 到 `.env` 並填入您的設定值：

```bash
cp .env.example .env
# 編輯 .env 檔案，填入您的實際設定值
```

### 3. 必要環境變數

- `PROJECT_ENDPOINT`: Azure AI Foundry 專案端點
- `MODEL_DEPLOYMENT_NAME`: AI 模型部署名稱
- `AZURE_SUBSCRIPTION_ID`: Azure 訂用帳戶 ID
- `AZURE_RESOURCE_GROUP`: Azure 資源群組名稱
- `LOGIC_APP_NAME`: Logic App 名稱
- `TRIGGER_NAME`: Logic App 觸發器名稱（通常為 "When_a_HTTP_request_is_received"）
- `RECIPIENT_EMAIL`: 預設收件人電子郵件地址

## 使用方式

### 命令行版本 (`logic_apps.py`)

執行命令行版本：

```bash
python logic_apps.py
```

這個版本會：
- 建立 Logic Apps Agent 並註冊 Logic App 工作流程
- 執行一次預設任務：發送包含目前日期時間的電子郵件
- 顯示執行結果並清理資源

### Web UI 版本 (`ui_logic_apps.py`)

執行 Chainlit Web 介面：

```bash
chainlit run ui_logic_apps.py
```

Web 介面會在 `http://localhost:8000`（或終端顯示的埠號）開啟。

## 功能說明

### 範例自動化任務

Web UI 版本提供 5 個預設的動作按鈕：

1. **發送目前日期時間** - 取得目前時間戳記並透過電子郵件發送
2. **發送天氣更新** - 取得紐約天氣資訊並發送郵件
3. **發送會議提醒** - 發送團隊會議提醒
4. **計算並發送結果** - 執行計算並透過郵件發送結果
5. **發送歡迎郵件** - 發送友善的歡迎訊息

### 自訂指令

您也可以在聊天介面中輸入自訂指令，例如：
- "發送電子郵件到 user@example.com，主旨是 'Test'，內容是 'Hello world'"
- "取得東京的目前天氣並發送給收件人"
- "計算 100 和 200 的總和，然後用電子郵件發送結果"

### Agent 功能

Logic Apps agent 可以：
- 執行 Logic Apps 工作流程
- 發送自動化電子郵件
- 擷取即時資料（日期/時間、天氣）
- 執行計算
- 將多個函數整合為工作流程

## 檔案結構

- `logic_apps.py` - 命令行版本的 Logic App 整合
- `ui_logic_apps.py` - Chainlit Web UI 版本
- `user_logic_apps.py` - Logic Apps 工具類別實作
- `user_functions.py` - 工具函數（日期/時間、天氣、計算等）
- `requirements.txt` - Python 依賴套件清單
- `.env.example` - 環境變數範本檔案
- `README.md` - 本說明文件

## 疑難排解

### 常見問題

1. **Logic App 註冊失敗**:
   - 驗證 Logic App 存在於指定的資源群組中
   - 檢查觸發器名稱完全相符（區分大小寫）
   - 確認您有適當的 Azure 權限

2. **找不到環境變數**:
   - 確認 `.env` 檔案在相同目錄中
   - 驗證所有必要變數都已設定
   - 檢查變數名稱是否有拼寫錯誤

3. **Agent 初始化失敗**:
   - 驗證 Azure AI Foundry 專案端點正確
   - 檢查模型部署名稱有效
   - 確認 Azure 憑證已正確設定

### 日誌與除錯

- Agent 和 thread ID 會顯示在歡迎訊息中
- 狀態訊息顯示執行進度
- 錯誤訊息提供特定的失敗詳細資訊
- 控制台輸出顯示資源清理資訊

## 版本比較

| 功能 | `logic_apps.py` | `ui_logic_apps.py` |
|------|----------------|-------------------|
| 介面 | 命令行/CLI | Web UI (Chainlit) |
| 互動 | 單次執行 | 互動式聊天 |
| 範例任務 | 無 | 5 個預設按鈕 |
| 狀態更新 | 基本 print 語句 | 即時 UI 更新 |
| 錯誤處理 | 控制台輸出 | 豐富的 UI 訊息 |
| 語言 | 英文/中文混合 | 繁體中文 + 英文 |
| 資源清理 | 手動 | 會話結束時自動 |

Web UI 版本提供更友善的用戶體驗，包含視覺回饋、互動元素和更好的錯誤處理。