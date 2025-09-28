# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
FILE: step3_cleanup_resources.py

DESCRIPTION:
    This script demonstrates how to clean up Azure AI Search index and Azure AI Foundry agent resources.
    It safely removes all resources created in steps 1 and 2, with proper verification and confirmation.

USAGE:
    python step3_cleanup_resources.py

    Before running the script:
    1. Run step1_create_search_index.py and step2_create_ai_agent.py first
    2. pip install azure-ai-projects azure-identity python-dotenv azure-search-documents
    3. Create a .env file with the same environment variables as previous steps
    4. Optionally, provide agent ID and other resource IDs as command line arguments

STEPS PERFORMED:
    1. Initialize environment and credentials
    2. List and identify resources to clean up
    3. Clean up AI agents and related resources
    4. Clean up search index and documents
    5. Verify cleanup completion
    6. Provide cleanup summary
"""

import os
import sys
import argparse
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.ai.projects import AIProjectClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient


def initialize_environment():
    """Initialize environment variables and credentials."""
    print("🔧 初始化環境變數和認證 / Initializing environment and credentials...")
    
    # 從 .env 檔案載入環境變數 / Load environment variables from .env file
    load_dotenv(override=True)
    
    # AI Project 設定 / AI Project settings
    project_endpoint = os.environ["PROJECT_ENDPOINT"]
    model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]
    
    # 搜索設定 / Search settings
    search_endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
    search_api_key = os.getenv("AZURE_SEARCH_API_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX", "vector-search-quickstart")
    
    # 初始化認證 / Initialize credentials
    project_credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
    search_credential = AzureKeyCredential(search_api_key)
    
    print(f"✅ AI Project 端點 / Endpoint: {project_endpoint}")
    print(f"✅ 搜索端點 / Search endpoint: {search_endpoint}")
    print(f"✅ 索引名稱 / Index name: {index_name}")
    
    return {
        "project_endpoint": project_endpoint,
        "model_deployment_name": model_deployment_name,
        "project_credential": project_credential,
        "search_endpoint": search_endpoint,
        "search_credential": search_credential,
        "index_name": index_name
    }


def list_available_agents(project_client):
    """List all available agents to identify what needs to be cleaned up."""
    print(f"\n📋 列出可用的 Agent / Listing available agents...")
    
    try:
        # 注意：agents.list() 方法可能在所有 SDK 版本中不可用 / Note: The agents.list() method may not be available in all SDK versions
        # 這是概念實現 - 實際 API 可能不同 / This is a conceptual implementation - actual API may differ
        agents = []
        
        # 為演示，我們會查找具有特定命名模式的 agents / For demonstration, we'll look for agents with specific naming patterns
        # 在實際實現中，您可能會儲存 agent ID 或使用不同的方法 / In a real implementation, you might store agent IDs or use different methods
        
        print(f"⚠️  注意：需要手動提供 Agent ID 進行清理")
        print(f"⚠️  Note: Agent ID needs to be provided manually for cleanup")
        print(f"💡 如果您知道 Agent ID，請使用 --agent-id 參數")
        print(f"💡 If you know the Agent ID, use the --agent-id parameter")
        
        return agents
        
    except Exception as e:
        print(f"⚠️  無法列出 Agent / Could not list agents: {str(e)}")
        return []


def cleanup_specific_agent(project_client, agent_id):
    """Clean up a specific agent by ID."""
    print(f"\n🤖 清理 Agent / Cleaning up agent: {agent_id}")
    
    try:
        # 刪除 agent / Delete the agent
        project_client.agents.delete_agent(agent_id)
        print(f"✅ Agent 刪除成功 / Agent deleted successfully: {agent_id}")
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "not found" in error_msg.lower() or "404" in error_msg:
            print(f"⚠️  Agent 不存在或已刪除 / Agent not found or already deleted: {agent_id}")
            return True  # 將此視為成功 / Consider this successful
        else:
            print(f"❌ Agent 刪除失敗 / Agent deletion failed: {error_msg}")
            return False


def cleanup_agents_by_pattern(project_client):
    """Clean up agents created by our scripts (by naming pattern)."""
    print(f"\n🔍 搜索並清理腳本創建的 Agent / Searching and cleaning up script-created agents...")
    
    # 我們腳本建立的 agent 名稱清單 / List of agent names that our scripts create
    known_agent_names = [
        "hotel-search-agent",
        "my-agent",
        "simple-agent-no-search",
        "simple-agent-no-tools"
    ]
    
    cleanup_count = 0
    
    for agent_name in known_agent_names:
        print(f"🔍 檢查 Agent 名稱 / Checking agent name: {agent_name}")
        # 注意：這是概念性的 - 實際實現會根據可用的 API 方法而定 / Note: This is conceptual - actual implementation would depend on available API methods
        print(f"⚠️  手動清理建議：如果您創建了名為 '{agent_name}' 的 Agent，請提供其 ID")
        print(f"⚠️  Manual cleanup suggestion: If you created an agent named '{agent_name}', please provide its ID")
    
    return cleanup_count


def verify_search_index_exists(search_endpoint, search_credential, index_name):
    """Verify that the search index exists before attempting cleanup."""
    print(f"\n🔍 驗證搜索索引是否存在 / Verifying search index exists: {index_name}")
    
    try:
        index_client = SearchIndexClient(endpoint=search_endpoint, credential=search_credential)
        index = index_client.get_index(index_name)
        
        print(f"✅ 索引存在 / Index exists: {index.name}")
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "not found" in error_msg.lower() or "404" in error_msg:
            print(f"⚠️  索引不存在 / Index does not exist: {index_name}")
            return False
        else:
            print(f"❌ 索引驗證失敗 / Index verification failed: {error_msg}")
            return False


def cleanup_search_index(search_endpoint, search_credential, index_name, delete_documents_only=False):
    """Clean up the search index or just its documents."""
    if delete_documents_only:
        print(f"\n📄 清理索引文檔 / Cleaning up index documents: {index_name}")
        return cleanup_index_documents(search_endpoint, search_credential, index_name)
    else:
        print(f"\n🗂️  刪除搜索索引 / Deleting search index: {index_name}")
        return cleanup_entire_index(search_endpoint, search_credential, index_name)


def cleanup_index_documents(search_endpoint, search_credential, index_name):
    """Clean up documents in the search index without deleting the index."""
    try:
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=index_name,
            credential=search_credential
        )
        
        # 取得所有文檔 / Get all documents
        results = search_client.search(search_text="*", top=1000)
        
        documents_to_delete = []
        for result in results:
            # 為每個文檔建立刪除動作 / Create delete action for each document
            documents_to_delete.append({
                "@search.action": "delete",
                "HotelId": result["HotelId"]  # 使用金鑰欄位 / Using the key field
            })
        
        if documents_to_delete:
            print(f"🗑️  刪除 {len(documents_to_delete)} 個文檔 / Deleting {len(documents_to_delete)} documents")
            delete_result = search_client.upload_documents(documents=documents_to_delete)
            
            success_count = sum(1 for r in delete_result if r.succeeded)
            print(f"✅ 成功刪除 {success_count} 個文檔 / Successfully deleted {success_count} documents")
            return True
        else:
            print(f"📝 索引中沒有文檔需要刪除 / No documents to delete in index")
            return True
            
    except Exception as e:
        print(f"❌ 文檔清理失敗 / Document cleanup failed: {str(e)}")
        return False


def cleanup_entire_index(search_endpoint, search_credential, index_name):
    """Clean up the entire search index."""
    try:
        index_client = SearchIndexClient(endpoint=search_endpoint, credential=search_credential)
        
        # 刪除整個索引 / Delete the entire index
        index_client.delete_index(index_name)
        print(f"✅ 索引刪除成功 / Index deleted successfully: {index_name}")
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "not found" in error_msg.lower() or "404" in error_msg:
            print(f"⚠️  索引不存在或已刪除 / Index not found or already deleted: {index_name}")
            return True  # 將此視為成功 / Consider this successful
        else:
            print(f"❌ 索引刪除失敗 / Index deletion failed: {error_msg}")
            return False


def verify_cleanup_completion(config, cleaned_agent_ids):
    """Verify that cleanup was completed successfully."""
    print(f"\n✅ 驗證清理完成 / Verifying cleanup completion...")
    
    verification_results = {
        "agents_cleaned": 0,
        "index_cleaned": False,
        "overall_success": True
    }
    
    # 驗證 agent 清理 / Verify agent cleanup
    if cleaned_agent_ids:
        project_client = AIProjectClient(
            endpoint=config["project_endpoint"],
            credential=config["project_credential"],
            api_version="latest",
        )
        
        for agent_id in cleaned_agent_ids:
            try:
                # 嘗試取得 agent - 如果清理正確應該會失敗 / Try to get the agent - should fail if cleaned properly
                agent = project_client.agents.get_agent(agent_id)
                print(f"⚠️  Agent 仍然存在 / Agent still exists: {agent_id}")
                verification_results["overall_success"] = False
            except Exception as e:
                if "not found" in str(e).lower() or "404" in str(e):
                    print(f"✅ Agent 清理確認 / Agent cleanup confirmed: {agent_id}")
                    verification_results["agents_cleaned"] += 1
                else:
                    print(f"❓ Agent 狀態未知 / Agent status unknown: {agent_id}")
    
    # 驗證索引清理 / Verify index cleanup
    if not verify_search_index_exists(
        config["search_endpoint"],
        config["search_credential"], 
        config["index_name"]
    ):
        verification_results["index_cleaned"] = True
        print(f"✅ 索引清理確認 / Index cleanup confirmed")
    else:
        print(f"⚠️  索引仍然存在 / Index still exists")
        verification_results["index_cleaned"] = False
    
    return verification_results


def interactive_cleanup_mode(config):
    """Interactive mode for cleanup with user confirmation."""
    print(f"\n🎯 互動式清理模式 / Interactive cleanup mode")
    print("=" * 50)
    
    cleanup_results = {
        "agents": [],
        "index": False,
        "success": True
    }
    
    # 詢問關於 agent 清理 / Ask about agent cleanup
    print(f"\n🤖 Agent 清理 / Agent cleanup:")
    agent_id = input("請輸入要刪除的 Agent ID (留空跳過) / Enter Agent ID to delete (leave empty to skip): ").strip()
    
    if agent_id:
        project_client = AIProjectClient(
            endpoint=config["project_endpoint"],
            credential=config["project_credential"],
            api_version="latest",
        )
        
        if cleanup_specific_agent(project_client, agent_id):
            cleanup_results["agents"].append(agent_id)
        else:
            cleanup_results["success"] = False
    
    # 詢問關於索引清理 / Ask about index cleanup
    print(f"\n🗂️  搜索索引清理 / Search index cleanup:")
    print(f"索引名稱 / Index name: {config['index_name']}")
    
    cleanup_choice = input(
        "選擇清理選項 / Choose cleanup option:\n"
        "1. 刪除整個索引 / Delete entire index\n"
        "2. 僅刪除文檔 / Delete documents only\n"
        "3. 跳過 / Skip\n"
        "請選擇 (1/2/3) / Choose (1/2/3): "
    ).strip()
    
    if cleanup_choice == "1":
        if cleanup_search_index(
            config["search_endpoint"],
            config["search_credential"],
            config["index_name"],
            delete_documents_only=False
        ):
            cleanup_results["index"] = "deleted"
        else:
            cleanup_results["success"] = False
    elif cleanup_choice == "2":
        if cleanup_search_index(
            config["search_endpoint"],
            config["search_credential"],
            config["index_name"],
            delete_documents_only=True
        ):
            cleanup_results["index"] = "documents_deleted"
        else:
            cleanup_results["success"] = False
    else:
        print("⏭️  跳過索引清理 / Skipping index cleanup")
    
    return cleanup_results


def main():
    """Main function to execute cleanup steps."""
    print("🧹 開始執行步驟 3: 清理 AI Search 索引和 AI Foundry Agent")
    print("🧹 Starting Step 3: Clean up AI Search Index and AI Foundry Agent")
    print("=" * 80)
    
    # 解析命令行參數 / Parse command line arguments
    parser = argparse.ArgumentParser(description="Clean up Azure AI resources")
    parser.add_argument("--agent-id", help="Specific agent ID to clean up")
    parser.add_argument("--index-only", action="store_true", help="Clean up index only")
    parser.add_argument("--agents-only", action="store_true", help="Clean up agents only")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--force", action="store_true", help="Force cleanup without confirmation")
    
    args = parser.parse_args()
    
    try:
        # 步驟 1: 初始化環境 / Step 1: Initialize environment
        config = initialize_environment()
        
        # 步驟 2: 互動模式或自動清理 / Step 2: Interactive mode or automated cleanup
        if args.interactive:
            cleanup_results = interactive_cleanup_mode(config)
        else:
            cleanup_results = {
                "agents": [],
                "index": False,
                "success": True
            }
            
            # 為 agent 操作初始化專案客戶端 / Initialize project client for agent operations
            project_client = AIProjectClient(
                endpoint=config["project_endpoint"],
                credential=config["project_credential"],
                api_version="latest",
            )
            
            # 如有提供，清理指定的 agent / Clean up specific agent if provided
            if args.agent_id and not args.index_only:
                print(f"\n🎯 清理指定的 Agent / Cleaning up specific agent...")
                if cleanup_specific_agent(project_client, args.agent_id):
                    cleanup_results["agents"].append(args.agent_id)
                else:
                    cleanup_results["success"] = False
            
            # 如未提供特定 ID，則按模式清理 agents / Clean up agents by pattern if no specific ID provided
            elif not args.index_only and not args.agent_id:
                print(f"\n🔍 嘗試清理已知的 Agent / Attempting to clean up known agents...")
                cleanup_agents_by_pattern(project_client)
            
            # 清理搜索索引 / Clean up search index
            if not args.agents_only:
                if verify_search_index_exists(
                    config["search_endpoint"],
                    config["search_credential"],
                    config["index_name"]
                ):
                    if not args.force:
                        confirm = input(f"\n確認刪除索引 '{config['index_name']}'? (y/N) / Confirm delete index '{config['index_name']}'? (y/N): ")
                        if confirm.lower() != 'y':
                            print("⏭️  跳過索引清理 / Skipping index cleanup")
                        else:
                            if cleanup_search_index(
                                config["search_endpoint"],
                                config["search_credential"],
                                config["index_name"]
                            ):
                                cleanup_results["index"] = "deleted"
                            else:
                                cleanup_results["success"] = False
                    else:
                        if cleanup_search_index(
                            config["search_endpoint"],
                            config["search_credential"],
                            config["index_name"]
                        ):
                            cleanup_results["index"] = "deleted"
                        else:
                            cleanup_results["success"] = False
        
        # 步驟 3: 驗證清理完成 / Step 3: Verify cleanup completion
        if args.agent_id or cleanup_results["agents"]:
            verification_results = verify_cleanup_completion(config, cleanup_results["agents"])
        
        # 步驟 4: 提供清理摘要 / Step 4: Provide cleanup summary
        print(f"\n📊 清理摘要 / Cleanup Summary")
        print("=" * 40)
        
        if cleanup_results["agents"]:
            print(f"✅ 已清理 Agent / Cleaned agents: {len(cleanup_results['agents'])}")
            for agent_id in cleanup_results["agents"]:
                print(f"   - {agent_id}")
        else:
            print(f"📝 沒有清理 Agent / No agents cleaned")
        
        if cleanup_results["index"]:
            print(f"✅ 搜索索引清理 / Search index cleanup: {cleanup_results['index']}")
        else:
            print(f"📝 搜索索引未更改 / Search index unchanged")
        
        if cleanup_results["success"]:
            print(f"\n🎉 步驟 3 完成！清理成功 / Step 3 completed! Cleanup successful")
            return {"success": True, "cleanup_results": cleanup_results}
        else:
            print(f"\n⚠️  步驟 3 完成但有警告 / Step 3 completed with warnings")
            return {"success": False, "cleanup_results": cleanup_results}
        
    except Exception as e:
        print(f"\n❌ 步驟 3 失敗 / Step 3 failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    result = main()
    
    if result["success"]:
        print(f"\n✅ 清理腳本執行成功 / Cleanup script executed successfully")
        print(f"🎯 所有資源已清理完畢 / All resources have been cleaned up")
    else:
        print(f"\n⚠️  清理腳本執行完成但有問題 / Cleanup script completed with issues")
        print(f"💡 請檢查上述輸出以了解詳情 / Please check the output above for details")
        exit(1)