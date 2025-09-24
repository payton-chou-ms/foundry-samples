#!/usr/bin/env python3
"""
Demo version of the Azure AI Search Agent with Chainlit
This version works without real Azure credentials for demonstration purposes.
此版本無需真實的 Azure 憑證即可進行演示。
"""

import chainlit as cl
import asyncio


# Mock Azure Agent for demo purposes
class MockAzureAgent:
    def __init__(self):
        self.responses = [
            "我找到了幾個高評分的酒店推薦給您：\n\n🏨 **Grand Palace Hotel** - 評分: 4.8/5\n📍 位置: 市中心\n✨ 設施: 游泳池, 健身房, 免費WiFi\n\n🏨 **Ocean View Resort** - 評分: 4.6/5\n📍 位置: 海濱區\n✨ 設施: 海景房, 餐廳, 停車場\n\n這些酒店都有很好的評價和完善的設施。您想了解更多關於哪一家的資訊嗎？",
            
            "根據搜索結果，以下酒店提供停車服務：\n\n🅿️ **City Business Hotel**\n- 提供免費室內停車場\n- 24小時代客泊車服務\n\n🅿️ **Grand Central Lodge**\n- 地下停車庫（需付費）\n- 方便的位置\n\n🅿️ **Suburban Inn**\n- 免費戶外停車位\n- 充足的停車空間\n\n您需要更多關於停車費用或位置的詳細資訊嗎？",
            
            "我為您推薦幾家精品酒店：\n\n🎨 **Boutique Art Hotel**\n- 獨特的藝術裝潢\n- 精心設計的客房\n- 評分: 4.7/5\n\n🌿 **Garden Boutique Inn**\n- 花園景觀\n- 個性化服務\n- 評分: 4.5/5\n\n🏛️ **Heritage Boutique Hotel**\n- 歷史建築改造\n- 復古風格裝潢\n- 評分: 4.6/5\n\n這些精品酒店都有自己的特色和魅力。您對哪種風格比較感興趣？",
            
            "基於搜索結果，我找到了紐約的一些優質酒店：\n\n🗽 **New York Central Hotel**\n- 位於曼哈頓中心\n- 靠近時代廣場\n- 評分: 4.4/5\n\n🌆 **Manhattan Sky Tower**\n- 高樓層城市景觀\n- 現代化設施\n- 評分: 4.6/5\n\n🎭 **Broadway District Inn**\n- 靠近百老匯劇院區\n- 便利的交通\n- 評分: 4.3/5\n\n紐約有很多選擇，您有特定的地區偏好或預算範圍嗎？"
        ]
        self.current_response = 0
    
    async def get_response(self, user_message: str) -> str:
        # Simulate processing time
        await asyncio.sleep(2)
        
        # Simple keyword matching for demo
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ["高評分", "high-rated", "推薦", "recommend"]):
            return self.responses[0]
        elif any(word in message_lower for word in ["停車", "parking", "park"]):
            return self.responses[1]
        elif any(word in message_lower for word in ["精品", "boutique"]):
            return self.responses[2]
        elif any(word in message_lower for word in ["紐約", "new york", "manhattan"]):
            return self.responses[3]
        else:
            # Default response
            return f"""感謝您的詢問：「{user_message}」

🔍 我正在搜索相關的酒店資訊...

基於 Azure AI Search 的搜索結果，我找到了一些相關資訊：

🏨 **搜索結果摘要**
- 找到多家符合條件的酒店
- 包含詳細的評分和設施資訊
- 提供地理位置和價格範圍

您可以嘗試更具體的查詢，例如：
- "請推薦高評分的酒店"
- "哪些酒店有停車設施？"  
- "我想找精品酒店"
- "紐約有什麼好酒店？"

需要其他協助嗎？"""


# Global mock agent
mock_agent = MockAzureAgent()


@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    
    welcome_msg = """🎉 歡迎使用 Azure AI Search Agent (演示版)！
Welcome to Azure AI Search Agent (Demo Version)!

我是您的智能搜索助手，能夠幫您搜索和查找酒店相關資訊。
I'm your intelligent search assistant, able to help you search and find hotel-related information.

📝 **範例查詢 / Example Queries:**
- "請推薦一些高評分的酒店" / "Please recommend some high-rated hotels"
- "有哪些酒店提供停車服務？" / "Which hotels offer parking facilities?"  
- "告訴我關於精品酒店的資訊" / "Tell me about boutique hotels"
- "搜尋紐約的酒店" / "Search for hotels in New York"

💡 **演示說明 / Demo Note:** 
這是演示版本，使用模擬的搜索結果。在實際部署中，會連接到真實的 Azure AI Search 服務。
This is a demo version using simulated search results. In actual deployment, it would connect to real Azure AI Search services.

開始對話吧！/ Let's start chatting!"""
    
    await cl.Message(
        content=welcome_msg,
        author="Azure AI Search Agent (Demo)"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages and generate responses."""
    
    try:
        # Show typing indicator
        async with cl.Step(name="🤖 AI Agent 搜索中... / AI Agent searching...") as step:
            step.output = f"正在處理您的查詢：{message.content[:100]}..."
            
            # Get response from mock agent
            response = await mock_agent.get_response(message.content)
            
            step.output = "搜索完成，正在生成回覆... / Search completed, generating response..."
        
        # Send the response
        await cl.Message(
            content=response,
            author="Azure AI Search Agent"
        ).send()
        
    except Exception as e:
        error_msg = f"處理訊息時發生錯誤 / Error processing message: {str(e)}"
        await cl.Message(
            content=f"❌ {error_msg}",
            author="System"
        ).send()


@cl.on_chat_end
def end():
    """Clean up when chat session ends."""
    print("💬 演示會話已結束 / Demo session ended")


if __name__ == "__main__":
    print("🚀 啟動 Azure AI Search Agent 演示版...")
    print("🚀 Starting Azure AI Search Agent Demo...")
    print("📍 請在瀏覽器中開啟 http://localhost:8000")
    print("📍 Please open http://localhost:8000 in your browser")