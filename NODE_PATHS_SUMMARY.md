# Node.js, nvm, npm, npx 安裝路徑摘要

**檢查日期**: 2025-10-05  
**使用者**: chihengchou

---

## 📍 主要路徑總覽

| 工具 | 安裝路徑 | 狀態 |
|------|---------|------|
| **nvm** | `C:\Users\chihengchou\AppData\Local\nvm` | ✅ 已安裝 |
| **Node.js (當前)** | `C:\nvm4w\nodejs` (符號連結) | ✅ 指向 v22.18.0 |
| **Node.js (實際)** | `C:\Users\chihengchou\AppData\Local\nvm\v22.18.0` | ✅ 已安裝 |
| **node.exe** | `C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\node.exe` | ✅ 存在 |
| **npm** | `C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\npm` | ✅ 存在 |
| **npx** | `C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\npx` | ✅ 存在 |
| **copilot** | `C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\copilot` | ✅ 已安裝 |

---

## 🗂️ 詳細路徑資訊

### 1. nvm (Node Version Manager)

**安裝目錄**:
```
C:\Users\chihengchou\AppData\Local\nvm
```

**主要檔案**:
- `nvm.exe` - nvm 執行檔
- `settings.txt` - nvm 配置檔案

**配置內容**:
```
root: C:\Users\chihengchou\AppData\Local\nvm
path: C:\nvm4w\nodejs
```

**已安裝的 Node.js 版本**:
- ✅ v18.20.7 - `C:\Users\chihengchou\AppData\Local\nvm\v18.20.7`
- ✅ v20.12.2 - `C:\Users\chihengchou\AppData\Local\nvm\v20.12.2`
- ✅ v22.18.0 - `C:\Users\chihengchou\AppData\Local\nvm\v22.18.0` **(當前使用)**

---

### 2. Node.js

**符號連結路徑** (PATH 中應包含):
```
C:\nvm4w\nodejs
```
↓ 指向
```
C:\Users\chihengchou\AppData\Local\nvm\v22.18.0
```

**node.exe 完整路徑**:
```
C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\node.exe
```

**大小**: 85,202,416 bytes (~85 MB)

---

### 3. npm (Node Package Manager)

**安裝位置**:
```
C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\npm
```

**相關檔案**:
- `npm` (Unix shell script)
- `npm.cmd` (Windows batch file)
- `npm.ps1` (PowerShell script)

**npm 模組目錄**:
```
C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\node_modules\npm
```

**全域模組目錄**:
```
C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\node_modules
```

---

### 4. npx (npm Package Runner)

**安裝位置**:
```
C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\npx
```

**相關檔案**:
- `npx` (Unix shell script)
- `npx.cmd` (Windows batch file)
- `npx.ps1` (PowerShell script)

---

### 5. GitHub Copilot CLI

**安裝位置**:
```
C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\copilot
```

**相關檔案**:
- `copilot` (Unix shell script)
- `copilot.cmd` (Windows batch file)
- `copilot.ps1` (PowerShell script)

**安裝日期**: 2025-08-18 21:21

---

## 🔧 環境變數設定

### 需要在 PATH 中的路徑

為了讓 Node.js 工具在命令列中可用，以下路徑應該在您的 **PATH 環境變數**中：

1. **NVM 路徑**:
   ```
   C:\Users\chihengchou\AppData\Local\nvm
   ```

2. **當前 Node.js 路徑** (符號連結):
   ```
   C:\nvm4w\nodejs
   ```

### 檢查方法

在 PowerShell 中執行：
```powershell
$env:PATH -split ';' | Where-Object { $_ -like '*nvm*' -or $_ -like '*node*' }
```

在 CMD 中執行：
```cmd
echo %PATH% | findstr /i "nvm node"
```

---

## 🚀 使用方法

### 切換 Node.js 版本

```cmd
# 列出已安裝的版本
nvm list

# 切換到特定版本
nvm use 22.18.0
nvm use 20.12.2
nvm use 18.20.7

# 安裝新版本
nvm install 20.18.0
```

### 驗證安裝

```cmd
# 檢查 Node.js 版本
node --version

# 檢查 npm 版本
npm --version

# 檢查 npx 版本
npx --version

# 檢查 copilot
copilot --version
```

### 全域安裝套件

```cmd
# 安裝到當前版本的 node_modules
npm install -g <package-name>

# 安裝位置
C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\node_modules\<package-name>
```

---

## ⚠️ 當前問題分析

### 問題：npm 安裝 @github/copilot 失敗

**錯誤原因**:
1. ✅ **copilot 已經安裝** - 檔案存在於 `C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\copilot`
2. ❌ **權限問題** - EPERM: 無法刪除 `node-pty` 目錄
3. ❌ **檔案衝突** - EEXIST: copilot 檔案已存在

**解決方案**:

#### 方案 1: 使用已安裝的版本
```cmd
# copilot 已經安裝，直接使用
copilot --version
```

#### 方案 2: 強制重新安裝
```powershell
# 在 PowerShell (以系統管理員身分執行)
npm install -g @github/copilot --force
```

#### 方案 3: 手動清理後重新安裝
```powershell
# 1. 關閉所有 VS Code 和 Node.js 相關程序

# 2. 刪除現有安裝
Remove-Item "C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\copilot*" -Force -Recurse -ErrorAction SilentlyContinue
Remove-Item "C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\node_modules\@github\copilot" -Force -Recurse -ErrorAction SilentlyContinue

# 3. 重新安裝
npm install -g @github/copilot
```

---

## 📝 PATH 環境變數建議

### 當前應該包含的路徑

```
C:\Users\chihengchou\AppData\Local\nvm
C:\nvm4w\nodejs
```

### 設定方法

1. **使用系統設定**:
   - 按 `Win + X` → 選擇「系統」
   - 點擊「進階系統設定」
   - 點擊「環境變數」
   - 在「系統變數」中找到 `Path`
   - 確認包含上述兩個路徑

2. **使用 PowerShell**:
   ```powershell
   # 檢查當前 PATH
   $env:PATH -split ';'
   
   # 臨時添加到 PATH (當前會話)
   $env:PATH += ";C:\nvm4w\nodejs"
   ```

---

## 🔍 故障排除

### Node.js 命令找不到

**症狀**: `bash: node: command not found`

**原因**: 
- PATH 環境變數未正確設定
- Git Bash 未載入 Windows PATH

**解決方法**:
1. 使用 PowerShell 或 CMD 而非 Git Bash
2. 在 Git Bash 中手動添加路徑：
   ```bash
   export PATH="/c/nvm4w/nodejs:$PATH"
   ```

### npm 全域套件找不到

**症狀**: 安裝後命令找不到

**解決方法**:
1. 確認安裝成功：
   ```cmd
   npm list -g --depth=0
   ```

2. 檢查檔案是否存在：
   ```cmd
   dir "C:\Users\chihengchou\AppData\Local\nvm\v22.18.0"
   ```

3. 重新啟動終端機

---

## 📊 系統資訊

- **作業系統**: Windows (REDMOND domain)
- **使用者名稱**: chihengchou
- **nvm 版本**: 已安裝 (需執行 `nvm version` 確認)
- **當前 Node.js**: v22.18.0
- **安裝日期**: 2025-08-18
- **最後更新**: 2025-10-05

---

## 🎯 快速參考

```bash
# Node.js 相關
node.exe        → C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\node.exe
npm             → C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\npm
npx             → C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\npx
copilot         → C:\Users\chihengchou\AppData\Local\nvm\v22.18.0\copilot

# nvm 相關
nvm.exe         → C:\Users\chihengchou\AppData\Local\nvm\nvm.exe
settings.txt    → C:\Users\chihengchou\AppData\Local\nvm\settings.txt

# 符號連結
C:\nvm4w\nodejs → C:\Users\chihengchou\AppData\Local\nvm\v22.18.0
```

---

**建議**: 使用 PowerShell 或 CMD 執行 Node.js 命令，而不是 Git Bash，因為 Git Bash 可能無法正確載入 Windows PATH。
