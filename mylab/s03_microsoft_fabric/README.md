# Microsoft Fabric 計程車數據分析助手

這是一個基於 Azure AI Agents 的持續對話代理，專門用於分析計程車行程數據。

## 功能特點

- **持續對話**: 與代理保持多輪對話，無需重新啟動
- **預設查詢**: 包含多種常用的數據查詢範例
- **自定義查詢**: 支援用戶輸入自定義問題
- **中文界面**: 友善的繁體中文使用界面
- **智能分析**: 自動調用適當的數據分析函數

## 查詢類型

1. **基礎查詢與彙總** - 日常統計、月度報表、車輛統計
2. **歷史趨勢** - 收入趨勢、成長區域分析
3. **異常與極端** - 高車資行程、異常短程
4. **地理分布與比較** - 區域分析、城市比較
5. **時間分析** - 日夜差異、尖峰時段
6. **乘客/駕駛行為** - 乘客分布、小費分析
7. **指定欄位統計** - 車資統計、支付方式分析
8. **綜合儀表板需求** - 完整的 KPI 摘要

## 環境要求

### 必要的環境變數

```bash
PROJECT_ENDPOINT=https://your-project.cognitiveservices.azure.com/
MODEL_DEPLOYMENT_NAME=your-model-deployment-name
```

### 安裝依賴

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
python sample_agents_fabric.py
```

### 互動界面

程式啟動後會顯示選單：
- 選擇預設查詢：輸入數字如 `1.1`, `2.2` 
- 自定義查詢：輸入 `9` 然後輸入您的問題
- 退出程式：輸入 `0`

### 查詢範例

- "2025-08-01 這一天的總行程數與總收入是多少？"
- "請按月份統計 2024 年的搭車趟數與總車資"
- "哪些區域在最近 6 個月的叫車量成長最多？"
- "找出異常短程但車資偏高的行程"

## 注意事項

- 目前使用模擬數據進行演示
- 在實際環境中需要連接到 Microsoft Fabric lakehouse
- 確保有適當的 Azure 權限和模型部署

## 文件結構

```
s03_microsoft_fabric/
├── sample_agents_fabric.py          # 主程式
├── taxi_query_functions.py          # 計程車數據查詢函數
├── requirements.txt                 # 依賴套件
└── README.md                       # 說明文件
```