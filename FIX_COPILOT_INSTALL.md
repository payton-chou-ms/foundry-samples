# 修復 @github/copilot 安裝問題

**問題**: npm 安裝 @github/copilot 時出現 EPERM 和 EEXIST 錯誤

**日期**: 2025-10-05

---

## 🔍 問題分析

### 錯誤訊息

```
npm warn cleanup Failed to remove some directories
npm error code EEXIST
npm error path C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\copilot
npm error EEXIST: file already exists
```

### 原因

1. ❌ **殘留檔案**: copilot 執行檔已存在但模組不完整
2. ❌ **權限問題**: 無法刪除某些子目錄（semver, keytar-forked-forked, node-pty）
3. ❌ **鎖定檔案**: 可能有程序正在使用這些檔案

---

## 🛠️ 解決方案

### 方案 1: 使用 --force 強制安裝（推薦）

在 **Git Bash** 中執行：

```bash
npm install -g @github/copilot --force
```

或在 **PowerShell（以系統管理員身分執行）** 中執行：

```powershell
npm install -g @github/copilot --force
```

---

### 方案 2: 手動清理後重新安裝

#### 步驟 1: 關閉所有可能使用 Node.js 的程序

在 **PowerShell（以系統管理員身分執行）** 中：

```powershell
# 關閉 VS Code
Get-Process code -ErrorAction SilentlyContinue | Stop-Process -Force

# 關閉 Node.js 相關程序
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
```

#### 步驟 2: 刪除殘留檔案

```powershell
# 刪除 copilot 執行檔
Remove-Item "C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\copilot" -Force -ErrorAction SilentlyContinue
Remove-Item "C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\copilot.cmd" -Force -ErrorAction SilentlyContinue
Remove-Item "C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\copilot.ps1" -Force -ErrorAction SilentlyContinue

# 刪除 copilot 模組目錄
Remove-Item "C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\node_modules\@github\copilot" -Recurse -Force -ErrorAction SilentlyContinue

# 刪除 @github 目錄（如果是空的）
$githubDir = "C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\node_modules\@github"
if ((Get-ChildItem $githubDir -ErrorAction SilentlyContinue).Count -eq 0) {
    Remove-Item $githubDir -Force -ErrorAction SilentlyContinue
}
```

#### 步驟 3: 清理 npm 快取

```powershell
npm cache clean --force
```

#### 步驟 4: 重新安裝

```powershell
npm install -g @github/copilot
```

---

### 方案 3: 使用 npx 臨時運行（無需安裝）

如果安裝持續失敗，可以使用 npx 直接運行：

```bash
npx @github/copilot --version
```

**優點**: 
- 不需要全域安裝
- 每次使用時自動下載最新版本
- 避免權限問題

**缺點**: 
- 首次運行較慢
- 每次都需要輸入 `npx`

---

### 方案 4: 切換到不同的 Node.js 版本

使用 nvm 切換到乾淨的 Node.js 版本：

```bash
# 安裝新版本的 Node.js
nvm install 20.18.0

# 切換到新版本
nvm use 20.18.0

# 安裝 copilot
npm install -g @github/copilot

# 如果成功，可以切回原版本
nvm use 22.18.0
```

---

## 📋 完整的 PowerShell 腳本

將以下內容儲存為 `fix-copilot.ps1`，然後**以系統管理員身分**執行：

```powershell
# fix-copilot.ps1
# 修復 GitHub Copilot CLI 安裝問題

Write-Host "🔧 開始修復 GitHub Copilot CLI 安裝..." -ForegroundColor Cyan

# 1. 關閉相關程序
Write-Host "`n📌 步驟 1: 關閉相關程序..." -ForegroundColor Yellow
Get-Process code -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# 2. 刪除殘留檔案
Write-Host "`n📌 步驟 2: 刪除殘留檔案..." -ForegroundColor Yellow
$nvmPath = "C:\Users\chihengchou\AppData\Local\nvm\v22.18.0"

Remove-Item "$nvmPath\copilot" -Force -ErrorAction SilentlyContinue
Remove-Item "$nvmPath\copilot.cmd" -Force -ErrorAction SilentlyContinue
Remove-Item "$nvmPath\copilot.ps1" -Force -ErrorAction SilentlyContinue

# 強制刪除 copilot 模組目錄
$copilotModulePath = "$nvmPath\node_modules\@github\copilot"
if (Test-Path $copilotModulePath) {
    Write-Host "  正在刪除: $copilotModulePath" -ForegroundColor Gray
    
    # 移除唯讀屬性
    Get-ChildItem $copilotModulePath -Recurse -Force | ForEach-Object {
        $_.Attributes = 'Normal'
    }
    
    # 刪除目錄
    Remove-Item $copilotModulePath -Recurse -Force -ErrorAction SilentlyContinue
}

# 檢查並刪除空的 @github 目錄
$githubDir = "$nvmPath\node_modules\@github"
if (Test-Path $githubDir) {
    $items = Get-ChildItem $githubDir -Force -ErrorAction SilentlyContinue
    if ($items.Count -eq 0) {
        Remove-Item $githubDir -Force -ErrorAction SilentlyContinue
        Write-Host "  已刪除空目錄: @github" -ForegroundColor Gray
    }
}

# 3. 清理 npm 快取
Write-Host "`n📌 步驟 3: 清理 npm 快取..." -ForegroundColor Yellow
npm cache clean --force

# 4. 重新安裝
Write-Host "`n📌 步驟 4: 重新安裝 @github/copilot..." -ForegroundColor Yellow
npm install -g @github/copilot --force

# 5. 驗證安裝
Write-Host "`n📌 步驟 5: 驗證安裝..." -ForegroundColor Yellow
$copilotVersion = copilot --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ GitHub Copilot CLI 安裝成功！" -ForegroundColor Green
    Write-Host "   版本: $copilotVersion" -ForegroundColor Green
} else {
    Write-Host "❌ 安裝失敗，請查看錯誤訊息" -ForegroundColor Red
    Write-Host "   錯誤: $copilotVersion" -ForegroundColor Red
}

Write-Host "`n🎉 修復流程完成！" -ForegroundColor Cyan
```

### 執行方式

1. 將上述腳本儲存為 `fix-copilot.ps1`
2. 以系統管理員身分開啟 PowerShell
3. 執行：
   ```powershell
   cd C:\Users\chihengchou\Downloads\work\foundry-samples
   .\fix-copilot.ps1
   ```

---

## 🚀 快速指令

### Git Bash（當前終端機）

```bash
# 方案 A: 強制安裝（最簡單）
npm install -g @github/copilot --force

# 方案 B: 使用 npx（無需安裝）
npx @github/copilot --version
```

### PowerShell（以系統管理員身分執行）

```powershell
# 完整清理並重新安裝
Get-Process code,node -ErrorAction SilentlyContinue | Stop-Process -Force
Remove-Item "C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\copilot*" -Force
Remove-Item "C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\node_modules\@github\copilot" -Recurse -Force -ErrorAction SilentlyContinue
npm cache clean --force
npm install -g @github/copilot
```

---

## 🔍 驗證安裝

安裝完成後，驗證是否成功：

```bash
# 檢查版本
copilot --version

# 列出全域套件
npm list -g @github/copilot

# 測試 copilot 命令
copilot --help
```

---

## ⚠️ 常見問題

### Q1: 還是出現 EPERM 錯誤？

**解決方法**:
1. 確保以**系統管理員身分**執行 PowerShell
2. 關閉 VS Code 和所有終端機視窗
3. 重新啟動電腦後再試一次

### Q2: 刪除檔案時說「檔案正在使用中」？

**解決方法**:
```powershell
# 使用工作管理員結束所有 Node.js 和 Code.exe 程序
Get-Process | Where-Object {$_.Name -like '*node*' -or $_.Name -like '*code*'} | Stop-Process -Force
```

### Q3: 安裝後 copilot 命令找不到？

**解決方法**:
```bash
# 重新載入環境變數
source ~/.bashrc

# 或重新開啟終端機視窗
```

### Q4: 想要完全移除 copilot？

**解決方法**:
```bash
npm uninstall -g @github/copilot
```

---

## 📊 目前狀態

- ✅ Node.js v22.18.0 已安裝
- ✅ npm 10.9.3 已安裝
- ✅ nvm 1.2.2 已安裝
- ❌ @github/copilot 安裝不完整（有殘留檔案）

**建議**: 先嘗試 **方案 1** 的 `--force` 選項，這是最簡單快速的解決方法。

---

## 📝 相關檔案

- npm 錯誤日誌: `C:\Users\chihengchou\AppData\Local\npm-cache\_logs\2025-10-04T23_56_13_622Z-debug-0.log`
- copilot 安裝位置: `C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\node_modules\@github\copilot`
- copilot 執行檔: `C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\copilot`

---

**更新日期**: 2025-10-05  
**狀態**: 等待修復
