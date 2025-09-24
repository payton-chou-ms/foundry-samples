#!/usr/bin/env python3
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
FILE: run_all_steps.py

DESCRIPTION:
    This script provides a convenient way to run all three steps of the vector search and AI agent integration demo.
    It can run all steps sequentially or individual steps based on command line arguments.

USAGE:
    python run_all_steps.py [--step STEP_NUMBER] [--skip-cleanup] [--interactive-cleanup]

    Options:
    --step 1|2|3        Run only a specific step
    --skip-cleanup      Run steps 1 and 2 but skip cleanup (step 3)
    --interactive-cleanup  Use interactive mode for cleanup
    --help              Show this help message
"""

import sys
import argparse
import subprocess
import os
from pathlib import Path


def run_step(step_number, additional_args=None):
    """Run a specific step script."""
    script_name = f"step{step_number}_"
    
    if step_number == 1:
        script_name += "create_search_index.py"
        description = "建立 AI Search 索引 / Creating AI Search Index"
    elif step_number == 2:
        script_name += "create_ai_agent.py"
        description = "建立 AI Foundry Agent / Creating AI Foundry Agent"
    elif step_number == 3:
        script_name += "cleanup_resources.py"
        description = "清理資源 / Cleaning up Resources"
    else:
        print(f"❌ 無效的步驟編號 / Invalid step number: {step_number}")
        return False
    
    print(f"\n🚀 執行步驟 {step_number}: {description}")
    print(f"🚀 Running Step {step_number}: {description}")
    print("=" * 60)
    
    # Build command
    cmd = [sys.executable, script_name]
    if additional_args:
        cmd.extend(additional_args)
    
    try:
        result = subprocess.run(cmd, check=True, cwd=Path(__file__).parent)
        print(f"✅ 步驟 {step_number} 完成 / Step {step_number} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 步驟 {step_number} 失敗 / Step {step_number} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ 找不到腳本文件 / Script file not found: {script_name}")
        return False


def check_environment():
    """Check if the environment is properly configured."""
    print("🔍 檢查環境設定 / Checking environment configuration...")
    
    env_file = Path(__file__).parent / ".env"
    env_example = Path(__file__).parent / ".env.example"
    
    if not env_file.exists():
        if env_example.exists():
            print("⚠️  未找到 .env 文件，請複製 .env.example 並填入您的設定")
            print("⚠️  .env file not found, please copy .env.example and fill in your settings")
            print(f"   cp {env_example} {env_file}")
        else:
            print("⚠️  需要創建 .env 文件來設定環境變數")
            print("⚠️  Need to create .env file for environment variables")
        return False
    
    # Check if required packages are installed
    try:
        import azure.search.documents
        import azure.ai.projects
        import azure.identity
        import dotenv
        print("✅ 所需套件已安裝 / Required packages are installed")
    except ImportError as e:
        print(f"⚠️  缺少必要套件 / Missing required package: {e}")
        print("請執行 / Please run: pip install -r requirements.txt")
        return False
    
    print("✅ 環境檢查通過 / Environment check passed")
    return True


def main():
    """Main function to parse arguments and run the appropriate steps."""
    parser = argparse.ArgumentParser(
        description="執行向量搜索和 AI Agent 整合示範的所有步驟 / Run all steps of vector search and AI agent integration demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例 / Examples:
  python run_all_steps.py                    # 執行所有步驟 / Run all steps
  python run_all_steps.py --step 1           # 僅執行步驟 1 / Run only step 1
  python run_all_steps.py --skip-cleanup     # 跳過清理步驟 / Skip cleanup step
  python run_all_steps.py --interactive-cleanup  # 使用互動式清理 / Use interactive cleanup
        """
    )
    
    parser.add_argument(
        "--step", 
        type=int, 
        choices=[1, 2, 3], 
        help="執行特定步驟 (1, 2, 或 3) / Run specific step (1, 2, or 3)"
    )
    parser.add_argument(
        "--skip-cleanup", 
        action="store_true", 
        help="執行步驟 1 和 2 但跳過清理 / Run steps 1 and 2 but skip cleanup"
    )
    parser.add_argument(
        "--interactive-cleanup", 
        action="store_true", 
        help="使用互動式清理模式 / Use interactive cleanup mode"
    )
    
    args = parser.parse_args()
    
    print("🎯 Azure AI Search 與 AI Foundry Agent 整合示範")
    print("🎯 Azure AI Search and AI Foundry Agent Integration Demo")
    print("=" * 80)
    
    # Check environment
    if not check_environment():
        print("\n❌ 環境檢查失敗，請修正後重試 / Environment check failed, please fix and retry")
        return 1
    
    success = True
    
    if args.step:
        # Run specific step
        additional_args = []
        if args.step == 3 and args.interactive_cleanup:
            additional_args.append("--interactive")
        
        success = run_step(args.step, additional_args)
        
    else:
        # Run multiple steps
        steps_to_run = [1, 2]
        if not args.skip_cleanup:
            steps_to_run.append(3)
        
        for step in steps_to_run:
            additional_args = []
            if step == 3 and args.interactive_cleanup:
                additional_args.append("--interactive")
            
            if not run_step(step, additional_args):
                success = False
                break
            
            # Add a pause between steps for better readability
            if step < max(steps_to_run):
                print(f"\n⏳ 準備執行下一步驟... / Preparing for next step...")
                print("-" * 40)
    
    # Final summary
    print(f"\n{'='*60}")
    if success:
        print("🎉 所有步驟執行完成！/ All steps completed successfully!")
        if not args.skip_cleanup and not args.step:
            print("✅ 資源已清理完畢 / Resources have been cleaned up")
        elif args.skip_cleanup:
            print("⚠️  請記得稍後清理資源 / Remember to clean up resources later")
            print("   python step3_cleanup_resources.py --interactive")
    else:
        print("❌ 執行過程中遇到錯誤 / Errors occurred during execution")
        print("💡 請檢查上方的錯誤訊息 / Please check the error messages above")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())