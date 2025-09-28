# Semantic Kernel 多代理程式協作系統 (Multi-Agent Handoff System with Semantic Kernel)

本系統提供兩種實現方式：
1. **Azure AI Projects 版本** - 使用 Azure AI Projects agents（原始版本）
2. **Semantic Kernel 版本** - 使用 Microsoft Semantic Kernel framework（新版本）

## 🤖 Semantic Kernel 代理程式概覽

### 1. SemanticKernelSearchAgent (搜尋代理)
- **專長**: 酒店搜尋、資訊檢索、向量搜尋
- **基於**: Semantic Kernel ChatCompletionAgent + AzureSearchPlugin
- **移交情況**: 當用戶要求發送郵件或數據分析時

### 2. SemanticKernelLogicAgent (自動化代理)  
- **專長**: 郵件發送、工作流程自動化、API 整合
- **基於**: Semantic Kernel ChatCompletionAgent + LogicAppsPlugin
- **移交情況**: 當用戶要求搜尋或數據分析時

### 3. SemanticKernelFabricAgent (數據分析代理)
- **專長**: 計程車數據分析、統計查詢、趨勢分析
- **基於**: Semantic Kernel ChatCompletionAgent + FabricPlugin
- **移交情況**: 當用戶要求搜尋、郵件或複雜查詢時

### 4. SemanticKernelDatabricksAgent (資料科學代理)
- **專長**: 複雜查詢、機器學習、大數據處理
- **基於**: Semantic Kernel ChatCompletionAgent + DatabricksPlugin
- **移交情況**: 當用戶要求簡單任務時，可能降級移交

## 🚀 Semantic Kernel 版本快速開始

### 1. 安裝依賴
```bash
pip install semantic-kernel azure-identity python-dotenv
```

### 2. 環境設定
```bash
cp .env.template .env
# 編輯 .env 檔案，填入你的實際配置值
```

#### 必需變數 (Semantic Kernel)
```bash
AZURE_OPENAI_ENDPOINT=https://your-openai-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key  # 或使用 DefaultAzureCredential
MODEL_DEPLOYMENT_NAME=gpt-4o
```

### 3. 運行 Semantic Kernel 系統
```bash
# 互動模式
python multi_agent_system_sk.py

# 演示模式
python demo_sk.py
```

## 🔧 Semantic Kernel 架構特色

### 核心組件
- **SemanticKernelOrchestrator**: 基於 Semantic Kernel 的協調器
- **SemanticKernelBaseAgent**: 基於 ChatCompletionAgent 的基礎代理類
- **Plugin System**: 使用 Semantic Kernel 的 plugin 架構
- **InProcessRuntime**: Semantic Kernel 的運行時管理

### 優勢
1. **標準化 Plugin 系統**: 使用 Semantic Kernel 標準的 @kernel_function 裝飾器
2. **統一的 Kernel**: 所有代理共享同一個 Kernel 實例，提高效率
3. **豐富的生態系**: 可以直接使用 Semantic Kernel 社區的 plugins
4. **更好的可擴展性**: 更容易添加新的功能和整合

## 💡 使用範例

### 程式化使用 (Semantic Kernel)
```python
from multi_agent_system_sk import SemanticKernelMultiAgentSystem

async def example():
    system = SemanticKernelMultiAgentSystem()
    await system.initialize()
    
    # 執行任務，支援自動移交
    result = await system.execute_task(
        task="搜尋東京的商務酒店並發郵件通知",
        initial_agent="search"
    )
    
    await system.cleanup()
```

### Plugin 開發範例
```python
from semantic_kernel.functions import kernel_function

class MyCustomPlugin:
    @kernel_function(name="my_function", description="自定義功能描述")
    def my_function(self, input_data: str) -> str:
        # 實現你的功能邏輯
        return f"處理結果: {input_data}"
```

## 🔄 兩種實現比較

| 特性 | Azure AI Projects | Semantic Kernel |
|------|------------------|-----------------|
| 代理基礎 | AIProjectClient.agents | ChatCompletionAgent |
| 函數系統 | ToolSet + FunctionTool | @kernel_function |
| 運行時 | Azure AI Projects Runtime | InProcessRuntime |
| 擴展性 | 受限於 Azure AI Projects | 豐富的 SK 生態系 |
| 學習曲線 | Azure 特定 | 業界標準 |
| 社區支持 | Azure 文檔 | 開源社區 |

## 📁 Semantic Kernel 檔案結構

```
mylab/s05_multi_agents/
├── step4_handoff_semantic_kernel.py    # SK 移交基礎架構
├── specialized_agents_sk.py            # SK 專門代理實現
├── multi_agent_system_sk.py           # SK 主系統程式
├── demo_sk.py                          # SK 演示腳本
├── README_SK.md                        # SK 版本文檔
└── requirements.txt                    # 包含 semantic-kernel
```

## 🧪 測試案例 (Semantic Kernel)

### 1. 基本功能測試
```bash
python -c "
import asyncio
from multi_agent_system_sk import SemanticKernelMultiAgentSystem

async def test():
    system = SemanticKernelMultiAgentSystem()
    await system.initialize()
    result = await system.execute_task('測試 SK 系統', 'search')
    print('✅ SK 系統測試成功' if result.get('success') else '❌ SK 系統測試失敗')
    await system.cleanup()

asyncio.run(test())
"
```

### 2. 完整演示
```bash
python demo_sk.py
```

## 🛠 自定義擴展 (Semantic Kernel)

### 添加新的 Plugin
1. 創建 Plugin 類並使用 @kernel_function 裝飾器
2. 在代理初始化時添加 plugin
3. 在 instructions 中描述新功能

### 自定義移交邏輯
修改各代理的 `should_handoff()` 方法，定義何時移交給其他代理。

## 🚨 故障排除 (Semantic Kernel)

### 常見問題
1. **Semantic Kernel 未安裝**: `pip install semantic-kernel`
2. **OpenAI 配置錯誤**: 檢查 `AZURE_OPENAI_ENDPOINT` 和 `AZURE_OPENAI_API_KEY`
3. **Plugin 函數未識別**: 確保使用正確的 @kernel_function 裝飾器

### Mock 模式
當依賴項未安裝時，系統會自動運行在 mock 模式，可用於開發和測試。

## 🎯 選擇建議

### 使用 Azure AI Projects 版本，如果：
- 你的團隊主要使用 Azure 生態系
- 需要與 Azure AI Foundry 深度整合
- 偏好 Azure 的官方支持

### 使用 Semantic Kernel 版本，如果：
- 需要更高的可擴展性和靈活性
- 想要利用 Semantic Kernel 的豐富生態系
- 偏好開源和社區驅動的解決方案
- 計劃與其他 AI 框架整合

兩種版本都提供相同的核心功能：智慧移交、多代理協作、完整的錯誤處理和資源管理。選擇取決於你的具體需求和技術偏好。