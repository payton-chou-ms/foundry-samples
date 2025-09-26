# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
Hotel Agent module - abstracts Azure AI Search hotel search functionality
from step2_ui_create_ai_agent.py into a reusable agent interface.
"""

import os
from typing import Optional, Dict, Any, List
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import MessageRole, ListSortOrder
from azure.search.documents import SearchClient
from ..config.settings import HotelAgentSettings


class HotelAgent:
    """
    Hotel search assistant agent using Azure AI Search integration.
    Provides standardized create/run/tools interface for the Magentic orchestrator.
    """
    
    def __init__(self, settings: HotelAgentSettings):
        """Initialize the Hotel agent with configuration."""
        self.settings = settings
        self.project_client: Optional[AIProjectClient] = None
        self.agent = None
        self.thread = None
        self._search_client = None
        
    def verify_search_index(self) -> bool:
        """Verify that the search index exists and has documents."""
        try:
            search_client = SearchClient(
                endpoint=self.settings.azure_search_endpoint,
                index_name=self.settings.azure_search_index,
                credential=AzureKeyCredential(self.settings.azure_search_api_key)
            )
            
            # Try to search for documents
            results = search_client.search(search_text="*", top=1)
            for result in results:
                return True  # Found at least one document
                
            return False  # Index exists but no documents
            
        except Exception:
            return False
    
    def create(self) -> Dict[str, Any]:
        """
        Create the hotel agent and conversation thread.
        
        Returns:
            Dict with agent and thread information
        """
        try:
            # Verify search index first
            if not self.verify_search_index():
                return {
                    "success": False,
                    "error": f"Search index '{self.settings.azure_search_index}' not available or empty"
                }
            
            # Initialize the AI Project Client
            self.project_client = AIProjectClient(
                endpoint=self.settings.project_endpoint,
                credential=DefaultAzureCredential(exclude_interactive_browser_credential=False),
            )
            
            # Create the AI agent with hotel search capabilities
            self.agent = self.project_client.agents.create_agent(
                model=self.settings.model_deployment_name,
                name="hotel-search-assistant",
                instructions="""你是一位專業的酒店搜索助理，專門協助客戶尋找合適的酒店住宿。
You are a professional hotel search assistant specializing in helping clients find suitable hotel accommodations.

🏨 您的專業領域包括：
Your areas of expertise include:
• 酒店信息查詢和推薦 / Hotel information inquiry and recommendations
• 精品酒店和特色住宿 / Boutique hotels and unique accommodations  
• 酒店評分和設施分析 / Hotel ratings and amenities analysis
• 停車和位置便利性 / Parking and location convenience
• 價格比較和性價比建議 / Price comparison and value recommendations

🔍 當用戶提問時，請：
When users ask questions, please:
1. 根據問題類型提供專業且詳細的回答
   Provide professional and detailed answers based on question type
2. 如有相關數據，引用具體的酒店名稱、評分和設施
   If relevant data is available, cite specific hotel names, ratings, and amenities
3. 用親切友好的語調回應，就像經驗豐富的旅行顧問
   Respond in a friendly tone like an experienced travel consultant
4. 如需更多信息，主動詢問客戶的具體需求
   Proactively ask about specific needs if more information is required

💡 您可以協助解答的問題包括：
Questions you can help answer include:
• 酒店信息和特色介紹 / Hotel information and feature introductions
• 特定地區的酒店推薦 / Hotel recommendations for specific areas
• 高評分酒店的詳細信息 / Detailed information about highly-rated hotels
• 特定酒店的設施和服務 / Amenities and services of specific hotels  
• 包含停車服務的酒店選項 / Hotel options with parking included

請始終保持專業、友善和有幫助的態度！
Always maintain a professional, friendly, and helpful attitude!""",
            )
            
            # Create conversation thread
            self.thread = self.project_client.agents.threads.create()
            
            return {
                "success": True,
                "agent_id": self.agent.id,
                "thread_id": self.thread.id,
                "agent_name": self.agent.name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create hotel agent: {str(e)}"
            }
    
    def run(self, thread_id: str, prompt: str) -> Dict[str, Any]:
        """
        Run the hotel agent with a user prompt.
        
        Args:
            thread_id: The conversation thread ID
            prompt: User's question or request
            
        Returns:
            Dict with response and status information
        """
        try:
            if not self.project_client or not self.agent:
                return {
                    "success": False,
                    "error": "Hotel agent not properly initialized"
                }
            
            # Create a message in the thread
            message = self.project_client.agents.messages.create(
                thread_id=thread_id,
                role=MessageRole.USER,
                content=prompt
            )
            
            # Create and process the run
            run = self.project_client.agents.runs.create_and_process(
                thread_id=thread_id,
                agent_id=self.agent.id
            )
            
            if run.status == "completed":
                # Get the agent's response
                messages = self.project_client.agents.messages.list(
                    thread_id=thread_id,
                    order=ListSortOrder.DESCENDING,
                    limit=1
                )
                
                message_list = list(messages)
                if message_list:
                    latest_message = message_list[0]
                    if latest_message.role == MessageRole.AGENT:
                        response_text = ""
                        if latest_message.content:
                            for content in latest_message.content:
                                if hasattr(content, 'text') and content.text:
                                    if hasattr(content.text, 'value'):
                                        response_text += content.text.value
                        
                        return {
                            "success": True,
                            "response": response_text,
                            "run_status": run.status
                        }
                        
                return {
                    "success": False,
                    "error": "No valid agent response found"
                }
                
            elif run.status == "failed":
                return {
                    "success": False,
                    "error": f"Agent run failed: {run.last_error}",
                    "run_status": run.status
                }
            else:
                return {
                    "success": False,
                    "error": f"Unexpected run status: {run.status}",
                    "run_status": run.status
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Hotel agent run failed: {str(e)}"
            }
    
    def tools(self) -> List[Dict[str, Any]]:
        """
        Return available tools/functions for this agent.
        Currently returns empty list as search is handled internally.
        
        Returns:
            List of tool definitions
        """
        # Hotel agent currently uses internal Azure AI Search integration
        # In a full implementation, this could return search tool definitions
        return []
    
    def get_sample_questions(self) -> List[str]:
        """
        Get sample questions that showcase the hotel agent's capabilities.
        
        Returns:
            List of sample questions
        """
        return [
            "What hotels do you know about? Can you tell me about them?",
            "Can you recommend a boutique hotel in New York?",
            "Tell me about hotels with high ratings.",
            "What amenities are available at the Old Century Hotel?",
            "Are there any hotels with parking included?"
        ]
    
    def cleanup(self) -> bool:
        """
        Clean up the agent resources.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.project_client and self.agent:
                self.project_client.agents.delete_agent(self.agent.id)
                return True
            return False
        except Exception:
            return False
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get agent information for display purposes.
        
        Returns:
            Dict with agent details
        """
        if self.agent and self.thread:
            return {
                "name": "Hotel Search Assistant",
                "role": "Hotel Search & Recommendations",
                "agent_id": self.agent.id,
                "thread_id": self.thread.id,
                "description": "專業酒店搜索助理，協助尋找合適住宿 / Professional hotel search assistant for accommodation recommendations",
                "capabilities": [
                    "酒店信息查詢 / Hotel information lookup",
                    "精品酒店推薦 / Boutique hotel recommendations",
                    "評分和設施分析 / Rating and amenity analysis", 
                    "停車便利性 / Parking convenience",
                    "價格比較 / Price comparison"
                ]
            }
        return {"name": "Hotel Search Assistant", "status": "Not initialized"}