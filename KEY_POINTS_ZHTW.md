# Azure AI Foundry 範例程式庫重點摘要

本文件整理 Azure AI Foundry 範例程式庫的重點內容，供使用者快速了解專案架構與功能。

---

## 📋 儲存庫概述

**Azure AI Foundry Documentation Samples** 是 Azure AI Foundry 官方文件的範例程式碼儲存庫。包含：

- 完整的端對端範例
- 常見開發任務的程式碼片段
- Jupyter Notebooks
- 多語言程式碼範例

**目標**：讓使用者能在本機測試 Azure AI Foundry 各種情境。

---

## 🛠️ 主要功能與範例

### 1. AI Agent 服務範例（Python）

| 工具名稱 | 說明 |
|----------|------|
| **quickstart.py** | 快速入門範例，展示基本設定與使用方式 |
| **basic_agent.py** | 基礎 Agent 設定（無額外工具） |
| **azure_ai_search.py** | Azure AI Search 知識庫整合 |
| **bing_grounding.py** | 使用 Bing 進行資料接地 |
| **code_interpreter** | 程式碼直譯器工具 |
| **file_search.py** | 檔案上傳與管理功能 |
| **functions_calling.py** | 本機函數呼叫示範 |
| **azure_functions.py** | 持久性 Azure Functions 呼叫 |
| **logic_apps.py** | Logic Apps 工作流程整合 |
| **enterprise_search.py** | 企業搜尋整合 |
| **openapi** | 外部 API 呼叫（OpenAPI 規格） |

### 2. Mistral AI 模型範例

- 在 Azure Foundry 平台上使用 Mistral AI 模型的程式碼範例
- 支援 `uv` 套件管理器或 `pip`
- 提供 Jupyter Notebook 整合

---

## 💻 支援的程式語言

儲存庫提供多種程式語言的範例：

- **Python** - 主要範例語言
- **JavaScript** / **TypeScript**
- **C#**
- **Java**
- **REST API**

---

## 🏗️ 基礎設施設定（Infrastructure as Code）

Azure AI Agent Service 提供三種部署模式：

### 基礎設定（Basic Setup）
- 與 OpenAI Assistants 相容
- 使用平台內建儲存管理 Agent 狀態
- 支援非 OpenAI 模型及工具（如 Azure AI Search、Bing）
- **範例**：`40-basic-agent-setup`、`42-basic-agent-setup-with-customization`

### 標準設定（Standard Setup）
- 包含基礎設定所有功能
- 可使用自有 Azure 資源儲存客戶資料
- 檔案、對話執行緒、向量儲存均存放於自有資源
- **範例**：`41-standard-agent-setup`

### 標準設定搭配自有虛擬網路（BYO Virtual Network）
- 完全在自有虛擬網路內運作
- 嚴格控制資料流動，防止資料外洩
- **範例**：`15-private-network-standard-agent-setup`

### 其他設定選項
| 設定 | 說明 |
|------|------|
| `00-basic` | 基礎 Azure AI Foundry 設定 |
| `01-connections` | 連線設定 |
| `10-private-network-basic` | 基礎私有網路設定 |
| `20-user-assigned-identity` | 使用者指派身分識別 |
| `25-entraid-passthrough` | Entra ID 驗證傳遞 |
| `30-customer-managed-keys` | 客戶管理金鑰 |
| `45-basic-agent-bing` | 基礎 Agent 搭配 Bing |

---

## 📚 貢獻指南重點

### 貢獻前置作業
1. 簽署 Contributor License Agreement (CLA)
2. 遵守 Microsoft 開放原始碼行為準則

### 開發環境設定
1. **Fork 儲存庫**：建立自己的 Fork 並複製到本機
2. **安裝開發依賴套件**：
   ```bash
   python -m pip install -r dev-requirements.txt
   ```
3. **設定 pre-commit**：
   ```bash
   pre-commit install
   ```

### 程式碼品質工具
- **black**：Python 程式碼格式化
- **nb-clean**：清理 Jupyter Notebook 中繼資料
- **ruff**：Python 程式碼檢查

### 範例撰寫規範
- 每個範例建立獨立目錄
- 包含 README 說明文件
- Python 範例請使用 Jupyter Notebook 模板

---

## 🔒 安全性

- 請勿透過公開 GitHub Issues 回報安全漏洞
- 安全性問題請回報至 [Microsoft Security Response Center](https://msrc.microsoft.com/create-report)
- 或寄信至 secure@microsoft.com

---

## 📁 儲存庫結構

```
foundry-samples/
├── samples/
│   ├── microsoft/
│   │   ├── python/          # Python 範例
│   │   ├── javascript/      # JavaScript 範例
│   │   ├── typescript/      # TypeScript 範例
│   │   ├── csharp/          # C# 範例
│   │   ├── java/            # Java 範例
│   │   ├── REST/            # REST API 範例
│   │   ├── data/            # 範例資料
│   │   └── infrastructure-setup/  # IaC 模板
│   └── mistral/             # Mistral AI 範例
├── libs/                    # 預編譯程式庫
├── .infra/                  # 範本檔案
└── README.md
```

---

## 🔗 相關連結

- [Azure AI Foundry 官方文件](https://docs.microsoft.com/azure/ai-services/)
- [Microsoft 程式碼範例瀏覽器](https://docs.microsoft.com/samples)
- [貢獻者授權協議 (CLA)](https://cla.opensource.microsoft.com)

---

*本文件由 GitHub Copilot 自動產生，最後更新時間：2025年11月*
