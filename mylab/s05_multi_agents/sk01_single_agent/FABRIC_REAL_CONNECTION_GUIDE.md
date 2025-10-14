# step1_azure_ai_agent_sk_fabric.py - 真實 Fabric 連接版本說明

## 📋 更新摘要

此檔案已從**模擬版本**更新為**真實 Fabric 連接版本**，現在會執行實際的 Microsoft Fabric lakehouse 數據查詢。

---

## 🔄 主要變更

### 1. ❌ 移除的內容（模擬部分）

**移除了模擬的 query_fabric 函數**:
```python
# ❌ 舊版：使用 random 生成假數據
import random
holiday_trips = random.randint(45000, 55000)
weekday_trips = random.randint(65000, 75000)
```

**移除了模擬連接設定**:
```python
# ❌ 舊版：模擬連接
fabric_connection = {
    "name": "mock-fabric-connection",
    "target": "mock-fabric-endpoint", 
}
```

### 2. ✅ 新增的內容（真實連接）

**使用 Azure AI 原生的 FabricTool**:
```python
# ✅ 新版：使用真實的 FabricTool
from azure.ai.agents.models import FabricTool

fabric_tool = FabricTool(connection_id=fabric_connection_id)

agent_definition = sync_client.agents.create_agent(
    model=MODEL_DEPLOYMENT_NAME,
    name="FabricLakehouseAgent",
    tools=fabric_tool.definitions,      # ✅ 真實工具定義
    tool_resources=fabric_tool.resources, # ✅ 真實工具資源
)
```

**真實的連接 ID 取得**:
```python
# ✅ 新版：從 Azure AI Foundry 取得真實連接
connection = await client.connections.get(name=FABRIC_CONNECTION_NAME)
fabric_connection_id = connection.id
```

---

## 🎯 關鍵差異

| 項目 | 舊版（模擬） | 新版（真實） |
|------|------------|------------|
| **數據來源** | `random.randint()` | 真實 Fabric lakehouse |
| **連接方式** | 模擬字典 | `FabricTool` + connection ID |
| **查詢執行** | if/else 條件判斷 | Azure AI 服務執行實際 SQL |
| **結果準確性** | 隨機假數據 | 基於實際數據 |
| **需要 Fabric** | ❌ 不需要 | ✅ 需要實際的 Fabric lakehouse |

---

## 📋 環境變數設定

### 必要環境變數

```bash
# Azure AI Foundry Project 端點
PROJECT_ENDPOINT=https://your-project.openai.azure.com/

# 或使用
FOUNDRY_PROJECT_ENDPOINT=https://your-project.openai.azure.com/

# Microsoft Fabric 連接名稱（在 Azure AI Foundry 中設定）
FABRIC_CONNECTION_NAME=your-fabric-connection-name

# AI 模型部署名稱
MODEL_DEPLOYMENT_NAME=gpt-4o-mini
```

### 設定步驟

1. **在 Azure AI Foundry 中建立 Fabric 連接**:
   - 前往 Azure AI Foundry Portal
   - 選擇您的專案
   - 前往 "Connected resources"
   - 建立新的 Fabric 連接
   - 記下連接名稱

2. **設定環境變數**:
   ```bash
   # 複製範例檔案
   cp .env.example .env
   
   # 編輯 .env 檔案
   nano .env
   ```

3. **填入實際值**:
   ```properties
   PROJECT_ENDPOINT=<your-actual-endpoint>
   FABRIC_CONNECTION_NAME=<your-fabric-connection-name>
   MODEL_DEPLOYMENT_NAME=gpt-4o-mini
   ```

---

## 🚀 執行方式

### 1. 安裝相依套件

```bash
pip install azure-ai-projects azure-ai-agents azure-identity semantic-kernel python-dotenv
```

### 2. 執行程式

```bash
cd mylab/s05_multi_agents/sk01_single_agent
python step1_azure_ai_agent_sk_fabric.py
```

### 3. 預期輸出

```
🔗 正在連接到 Azure AI Foundry Project...
   Endpoint: https://your-project.openai.azure.com/
   Fabric Connection: your-fabric-connection-name
   Model: gpt-4o-mini

🔗 正在取得 Fabric 連接...
✅ 成功取得 Fabric 連接 ID: <connection-id>

🤖 正在建立 Fabric Agent...
✅ Agent 創建成功，Agent ID: asst_xxxxx
   使用真實的 Microsoft Fabric 連接進行數據查詢

✅ Semantic Kernel Agent 初始化完成
✅ Agent 已配置使用 FabricTool 進行真實數據查詢

================================================================================
🚕 開始計程車數據分析
================================================================================

📝 查詢 1/1:
   比較國定假日與一般平日的計程車總行程數...

--------------------------------------------------------------------------------
🤔 Agent 正在分析（使用真實的 Fabric lakehouse 數據）...

💬 Agent 回應:
根據 Microsoft Fabric lakehouse 的實際數據分析：

【實際查詢結果會顯示在這裡，基於真實的 lakehouse 數據】

1. 平日總行程數：XX,XXX 趟
2. 國定假日總行程數：XX,XXX 趟
3. 差異：平日比假日多 XX,XXX 趟

[基於真實的 Fabric lakehouse 查詢結果]

================================================================================

🧹 正在清理資源...
✅ Thread 已刪除
✅ Agent 已刪除 (ID: asst_xxxxx)

✨ 程式執行完畢
```

---

## 🔧 技術細節

### 1. 同步與非同步 Client 混用

由於 Semantic Kernel 使用非同步 client，但建立 Agent 時需要使用同步的 `AIProjectClient`，程式中同時使用兩種 client：

```python
# 非同步 client（用於 Semantic Kernel）
async with AzureAIAgent.create_client(credential=creds, endpoint=FOUNDRY_PROJECT_ENDPOINT) as client:
    
    # 同步 client（用於建立 Agent with FabricTool）
    with AIProjectClient(credential=SyncDefaultAzureCredential(), endpoint=FOUNDRY_PROJECT_ENDPOINT) as sync_client:
        fabric_tool = FabricTool(connection_id=fabric_connection_id)
        agent_definition = sync_client.agents.create_agent(...)
```

### 2. 不需要自定義 Plugin

使用 Azure AI 原生的 `FabricTool` 時，**不需要**註冊自定義的 Semantic Kernel plugins：

```python
# ✅ 正確：使用原生 FabricTool 時不需要 plugins
agent = AzureAIAgent(
    client=client,
    definition=agent_definition,
    # 不需要 plugins - FabricTool 由 Azure AI 服務處理
)
```

### 3. FabricTool 工作原理

- `FabricTool` 是 Azure AI 的原生工具
- 它會自動連接到指定的 Fabric lakehouse
- Agent 會使用自然語言生成 SQL 查詢
- SQL 查詢在 Fabric lakehouse 中執行
- 結果返回給 Agent 進行分析和回應

---

## 🆚 與其他版本的比較

### 與 s03_microsoft_fabric/cli_agents_fabric.py 的關係

| 特性 | step1_azure_ai_agent_sk_fabric.py | s03/cli_agents_fabric.py |
|------|----------------------------------|-------------------------|
| **框架** | Semantic Kernel | 原生 Azure AI Projects SDK |
| **非同步** | ✅ 完全非同步 | ❌ 同步 |
| **Fabric 連接** | ✅ FabricTool | ✅ FabricTool |
| **串流回應** | ✅ invoke_stream | ❌ 無串流 |
| **互動選單** | ❌ 固定查詢 | ✅ 互動式選單 |
| **適用場景** | Semantic Kernel 整合示範 | 實際應用和測試 |

### 與 sk03_magentic_app_final/plugins/fabric_plugin.py 的關係

| 特性 | step1 (本檔案) | sk03 fabric_plugin.py |
|------|---------------|----------------------|
| **Fabric 連接** | ✅ 真實 FabricTool | ❌ 模擬（random） |
| **架構** | 單檔範例 | 模組化企業架構 |
| **目的** | 學習 Fabric 整合 | 展示架構設計 |
| **可用於生產** | ✅ 可以 | ❌ 需要替換模擬部分 |

---

## ⚠️ 注意事項

### 1. 需要實際的 Fabric Lakehouse

此版本**需要**實際的 Microsoft Fabric lakehouse 設定：
- 必須有包含計程車數據的 lakehouse
- 必須在 Azure AI Foundry 中配置 Fabric 連接
- 連接必須有適當的權限

### 2. 費用考量

使用真實的 Fabric 連接會產生費用：
- **Azure AI Foundry**: Agent 運行時間和 token 使用
- **Microsoft Fabric**: 計算資源和查詢執行
- **Azure OpenAI**: 模型推理費用

建議在測試時：
- 使用較小的數據集
- 限制查詢次數
- 使用開發環境

### 3. 權限要求

執行此程式需要：
- Azure AI Foundry 專案的存取權限
- Fabric 連接的讀取權限
- Fabric lakehouse 的查詢權限

---

## 🐛 疑難排解

### 問題 1: 無法取得 Fabric 連接

**錯誤訊息**:
```
❌ 無法取得 Fabric 連接: Connection 'your-name' not found
```

**解決方法**:
1. 確認 `FABRIC_CONNECTION_NAME` 拼寫正確
2. 在 Azure AI Foundry Portal 檢查連接是否存在
3. 確認連接類型為 Fabric
4. 檢查您的 Azure 認證

### 問題 2: Agent 創建失敗

**錯誤訊息**:
```
❌ Error creating agent: Invalid connection_id
```

**解決方法**:
1. 確認 connection ID 正確取得
2. 檢查 Fabric 連接狀態是否為 Active
3. 確認模型部署名稱正確

### 問題 3: 查詢無結果

**現象**: Agent 回應但沒有實際數據

**可能原因**:
1. Fabric lakehouse 中沒有數據
2. 連接權限不足
3. SQL 查詢語法錯誤

**解決方法**:
- 在 Fabric Portal 中驗證數據存在
- 檢查連接權限設定
- 查看 Agent 的中間步驟輸出（Function Call/Result）

---

## 📚 延伸學習

### 相關檔案

- **真實應用版本**: `mylab/s03_microsoft_fabric/cli_agents_fabric.py`
- **UI 版本**: `mylab/s03_microsoft_fabric/ui_agents_fabric.py`
- **企業架構版本**: `mylab/s05_multi_agents/sk03_magentic_app_final/`
- **README**: `mylab/s03_microsoft_fabric/README.md`

### 官方文件

- [Microsoft Fabric Data Agent](https://learn.microsoft.com/zh-tw/fabric/data-science/data-agent-foundry)
- [Azure AI Foundry - Fabric Tools](https://learn.microsoft.com/zh-tw/azure/ai-foundry/agents/how-to/tools/fabric)
- [Semantic Kernel Agents](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/)

---

## 📝 總結

### ✅ 現在這個檔案是：

- ✅ **真實版本** - 使用真實的 Fabric 連接和數據
- ✅ **生產就緒** - 可以用於實際應用
- ✅ **Semantic Kernel 整合** - 展示正確的 SK + Fabric 整合方式
- ✅ **非同步實作** - 完全非同步的程式碼

### ❌ 這個檔案不再是：

- ❌ 模擬版本 - 不再使用 `random` 生成假數據
- ❌ 教學示範 - 已升級為可用於實際應用的版本
- ❌ 獨立運行 - 需要實際的 Azure 和 Fabric 設定

### 🎯 適用場景：

1. **學習 Semantic Kernel + Fabric 整合**
2. **建立真實的數據分析 Agent**
3. **整合到 Multi-Agent 系統**
4. **非同步 Agent 應用開發**

---

**最後更新**: 2025-10-01  
**版本**: 2.0.0 (Real Fabric Connection)  
**作者**: MyLab 團隊
