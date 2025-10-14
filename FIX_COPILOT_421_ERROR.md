# 修復 GitHub Copilot CLI "421 Misdirected Request" 錯誤

**錯誤訊息**: `421 421 Misdirected Request`  
**發生時間**: 2025-10-05  
**Copilot 版本**: 0.0.334 (Commit: 26896a6)

---

## 🔍 問題分析

### 錯誤詳情

```
✗ Model call failed: "421 421 Misdirected Request\n"
✗ Execution failed: 421 421 Misdirected Request

Total usage est:       1 Premium request
Total duration (API):  0.0s
Total duration (wall): 4.5s
```

### 421 錯誤的可能原因

1. **認證問題** - GitHub Copilot 帳號未登入或 token 過期
2. **網路問題** - 代理伺服器配置錯誤或企業防火牆封鎖
3. **DNS/SSL 問題** - TLS/SSL 憑證驗證失敗
4. **訂閱問題** - GitHub Copilot 訂閱未啟用或已過期
5. **API 端點問題** - 請求被導向錯誤的伺服器
6. **企業網路限制** - REDMOND 企業網路可能有特殊限制

---

## 🛠️ 解決方案

### 方案 1: 重新登入 GitHub Copilot（推薦）

#### 步驟 1: 檢查當前認證狀態

```bash
# 啟動互動模式
copilot

# 在互動模式中執行
/logout
/login
```

#### 步驟 2: 使用瀏覽器登入

執行 `/login` 後會出現：
1. 瀏覽器自動開啟 GitHub 認證頁面
2. 輸入裝置代碼
3. 授權 GitHub Copilot CLI 存取

#### 步驟 3: 驗證登入

```bash
# 在互動模式中
/user show
```

---

### 方案 2: 檢查 GitHub Copilot 訂閱

#### 在瀏覽器中檢查

1. 前往 [GitHub Copilot 設定](https://github.com/settings/copilot)
2. 確認訂閱狀態：
   - ✅ Active subscription (個人訂閱)
   - ✅ Enabled by organization (企業訂閱)
3. 檢查 CLI 存取權限是否啟用

#### 檢查企業政策

如果您在 REDMOND (Microsoft) 網路下：
- 前往 [GitHub 企業設定](https://github.com/enterprises)
- 確認 Copilot CLI 未被組織政策封鎖
- 聯絡 IT 管理員確認 Copilot API 端點未被防火牆封鎖

---

### 方案 3: 配置網路代理

如果您在企業網路環境下，可能需要配置代理：

#### 設定 HTTP/HTTPS 代理

在 **Git Bash** 中：

```bash
# 設定代理（如果需要）
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080

# 或設定為系統代理
export HTTP_PROXY=$http_proxy
export HTTPS_PROXY=$https_proxy

# 測試 copilot
copilot -p "Hello" --allow-all-tools
```

#### 在 ~/.bashrc 中永久設定

```bash
# 添加到 ~/.bashrc
echo '# Proxy settings for corporate network' >> ~/.bashrc
echo 'export HTTP_PROXY=http://proxy.company.com:8080' >> ~/.bashrc
echo 'export HTTPS_PROXY=http://proxy.company.com:8080' >> ~/.bashrc
echo 'export NO_PROXY=localhost,127.0.0.1,.microsoft.com' >> ~/.bashrc

# 重新載入
source ~/.bashrc
```

---

### 方案 4: 檢查 SSL 憑證問題

如果是企業環境的 SSL 憑證問題：

```bash
# 暫時跳過 SSL 驗證（僅用於測試）
export NODE_TLS_REJECT_UNAUTHORIZED=0

# 測試 copilot
copilot -p "Hello" --allow-all-tools

# 如果成功，問題出在 SSL 憑證
# 需要安裝企業的根憑證
```

**警告**: `NODE_TLS_REJECT_UNAUTHORIZED=0` 會降低安全性，僅用於診斷問題，不建議長期使用。

---

### 方案 5: 使用 VS Code 內建的 Copilot

如果 CLI 持續失敗，可以使用 VS Code 的 GitHub Copilot 擴充功能：

1. 安裝 [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) 擴充功能
2. 在 VS Code 中登入 GitHub
3. 使用 Copilot Chat (Ctrl+Shift+I 或 Cmd+Shift+I)

**優點**:
- 與 VS Code 整合更好
- 通常有較少的網路問題
- 支援更多功能（內聯建議、Chat、解釋程式碼等）

---

### 方案 6: 清除快取並重新安裝

```bash
# 1. 登出（如果可以）
copilot
# 在互動模式中輸入 /logout

# 2. 清除 copilot 快取和配置
rm -rf ~/.copilot/

# 3. 清除 npm 快取
npm cache clean --force

# 4. 重新安裝
npm uninstall -g @github/copilot
npm install -g @github/copilot

# 5. 重新登入
copilot
# 在互動模式中輸入 /login
```

---

## 🔧 診斷步驟

### 1. 檢查網路連線

```bash
# 測試 GitHub API 連線
curl -I https://api.github.com

# 測試 GitHub Copilot API
curl -I https://copilot-proxy.githubusercontent.com

# 檢查 DNS 解析
nslookup api.github.com
nslookup copilot-proxy.githubusercontent.com
```

### 2. 檢查環境變數

```bash
# 顯示相關環境變數
env | grep -i proxy
env | grep -i github
env | grep -i copilot
```

### 3. 啟用詳細日誌

```bash
# 使用 debug 日誌模式
copilot --log-level debug --log-dir ./copilot-logs -p "test" --allow-all-tools

# 檢查日誌
ls -la ./copilot-logs/
cat ./copilot-logs/*.log
```

### 4. 測試基本功能

```bash
# 測試版本
copilot --version

# 測試幫助
copilot --help

# 測試簡單提示
copilot -p "What is 2+2?" --allow-all-tools
```

---

## 📋 快速修復腳本

將以下內容儲存為 `fix-copilot-421.sh`:

```bash
#!/bin/bash
# fix-copilot-421.sh
# 修復 GitHub Copilot CLI 421 錯誤

echo "🔧 開始診斷 GitHub Copilot CLI 問題..."

# 1. 檢查版本
echo -e "\n📌 Copilot 版本:"
copilot --version

# 2. 檢查網路
echo -e "\n📌 檢查網路連線:"
if curl -s -I https://api.github.com | head -n 1 | grep -q "200"; then
    echo "✅ GitHub API 連線正常"
else
    echo "❌ GitHub API 連線失敗"
fi

if curl -s -I https://copilot-proxy.githubusercontent.com | head -n 1 | grep -q "200\|301\|302"; then
    echo "✅ Copilot API 連線正常"
else
    echo "❌ Copilot API 連線失敗"
fi

# 3. 檢查代理設定
echo -e "\n📌 代理設定:"
if [ -n "$HTTP_PROXY" ] || [ -n "$HTTPS_PROXY" ]; then
    echo "HTTP_PROXY: $HTTP_PROXY"
    echo "HTTPS_PROXY: $HTTPS_PROXY"
else
    echo "無代理設定"
fi

# 4. 清除快取
echo -e "\n📌 清除快取..."
if [ -d ~/.copilot/ ]; then
    echo "發現 ~/.copilot/ 目錄"
    read -p "是否刪除? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf ~/.copilot/
        echo "✅ 快取已清除"
    fi
fi

# 5. 測試連線
echo -e "\n📌 測試 Copilot 連線..."
copilot --log-level debug -p "test connection" --allow-all-tools 2>&1 | head -n 20

echo -e "\n🎉 診斷完成！"
echo -e "\n💡 建議:"
echo "1. 如果網路連線失敗，請檢查代理設定"
echo "2. 如果是認證問題，請執行: copilot 然後輸入 /login"
echo "3. 如果是訂閱問題，請前往 https://github.com/settings/copilot 檢查"
echo "4. 如果在企業網路，請聯絡 IT 管理員確認 Copilot API 未被封鎖"
```

執行方式：

```bash
chmod +x fix-copilot-421.sh
./fix-copilot-421.sh
```

---

## 🌐 Microsoft/REDMOND 企業網路特別注意事項

由於您的帳號顯示 `REDMOND+chihengchou`，您可能在 Microsoft 企業網路環境中。

### 企業網路常見問題

1. **SSL 中間人攔截**
   - 企業防火牆可能替換 SSL 憑證
   - 需要安裝企業根憑證

2. **代理伺服器**
   - 可能需要配置 HTTP/HTTPS 代理
   - 檢查系統設定中的代理配置

3. **防火牆規則**
   - GitHub Copilot API 端點可能被封鎖
   - 聯絡 IT 開放以下端點：
     - `api.github.com`
     - `copilot-proxy.githubusercontent.com`
     - `*.githubcopilot.com`

4. **VPN 問題**
   - 嘗試在 VPN 連線時和斷線時分別測試
   - 某些 VPN 配置可能干擾 API 存取

### Microsoft 內部資源

如果您是 Microsoft 員工：
- 查看內部文件關於 GitHub Copilot 的配置
- 使用 ServiceNow 提交 IT 支援票證
- 加入內部 Teams 頻道尋求協助

---

## 📞 取得協助

### GitHub Copilot 支援

- [GitHub Copilot 文件](https://docs.github.com/en/copilot)
- [GitHub Copilot CLI 文件](https://githubnext.com/projects/copilot-cli)
- [GitHub 社群討論區](https://github.com/orgs/community/discussions/categories/copilot)

### 回報問題

如果問題持續存在，請在 GitHub 回報：
- [GitHub Copilot Discussions](https://github.com/orgs/community/discussions/categories/copilot)
- 提供日誌檔案（使用 `--log-level debug`）
- 說明您的網路環境（企業/個人）

---

## ✅ 成功標準

完成修復後，應該能夠：

```bash
# 1. 成功執行簡單提示
copilot -p "What is the capital of France?" --allow-all-tools

# 2. 查看使用情況
copilot
# 輸入 /usage

# 3. 執行程式碼相關任務
copilot -p "Explain this file" --allow-all-tools --add-dir .
```

---

**狀態**: 等待修復  
**優先順序**: 高  
**預估修復時間**: 15-30 分鐘

**最可能的原因**: 認證問題或企業網路限制

**建議首先嘗試**: 方案 1 (重新登入) 和方案 2 (檢查訂閱)
