#!/usr/bin/env python3
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Starter script for Azure AI Search Agent with Chainlit
Azure AI 搜索代理 Chainlit 啟動腳本

This script helps set up and run the Chainlit application.
此腳本協助設定並執行 Chainlit 應用程式。
"""

import os
import sys
import subprocess
from pathlib import Path


def check_requirements():
    """Check if all required packages are installed.
    檢查是否已安裝所有必要套件。
    """
    print("🔍 檢查套件安裝狀況 / Checking package installation...")
    
    required_packages = [
        "chainlit",
        "azure-ai-projects", 
        "azure-identity",
        "python-dotenv"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package} - 未安裝 / Not installed")
    
    if missing_packages:
        print("\n⚠️  缺少必要套件 / Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 請執行安裝指令 / Please run installation command:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ 所有套件已安裝 / All packages installed")
    return True


def check_env_file():
    """Check if .env file exists and has required variables.
    檢查 .env 檔案是否存在且包含必要變數。
    """
    print("\n🔍 檢查環境設定 / Checking environment configuration...")
    
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ .env 檔案不存在 / .env file not found")
        print("📝 請複製 .env.example 到 .env 並填入您的設定")
        print("📝 Please copy .env.example to .env and fill in your configuration")
        print("   cp .env.example .env")
        return False
    
    # Check for required environment variables
    required_vars = [
        "PROJECT_ENDPOINT",
        "MODEL_DEPLOYMENT_NAME", 
        "AZURE_AI_CONNECTION_ID"
    ]
    
    missing_vars = []
    
    with open(env_file, 'r', encoding='utf-8') as f:
        env_content = f.read()
    
    for var in required_vars:
        if f"{var}=" not in env_content or f"{var}=your-" in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  .env 檔案中缺少或未設定以下變數 / Missing or unset variables in .env:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 請編輯 .env 檔案並填入正確的 Azure 服務資訊")
        print("📝 Please edit .env file and fill in correct Azure service information")
        return False
    
    print("✅ 環境設定檔案正常 / Environment configuration file OK")
    return True


def run_chainlit():
    """Run the Chainlit application.
    執行 Chainlit 應用程式。
    """
    print("\n🚀 啟動 Chainlit 應用程式 / Starting Chainlit application...")
    print("📍 應用程式將在瀏覽器中開啟 http://localhost:8000")
    print("📍 Application will open in browser at http://localhost:8000")
    print("\n⏹️  按 Ctrl+C 停止應用程式 / Press Ctrl+C to stop the application")
    print("=" * 60)
    
    try:
        # Run chainlit with auto-reload enabled
        subprocess.run([
            sys.executable, "-m", "chainlit", "run", "app.py", "-w", "--port", "8000"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 啟動失敗 / Startup failed: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 應用程式已停止 / Application stopped")
        return True


def main():
    """Main function to run all checks and start the application.
    主函數，執行所有檢查並啟動應用程式。
    """
    print("🎯 Azure AI Search Agent with Chainlit")
    print("🎯 Azure AI 搜索代理 Chainlit 版本")
    print("=" * 60)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Run checks
    if not check_requirements():
        sys.exit(1)
    
    if not check_env_file():
        sys.exit(1)
    
    # All checks passed, start the application
    print("\n✅ 所有檢查通過，啟動應用程式 / All checks passed, starting application")
    success = run_chainlit()
    
    if success:
        print("\n👋 感謝使用！/ Thank you for using!")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()