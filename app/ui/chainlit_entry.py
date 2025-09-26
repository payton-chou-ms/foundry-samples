# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
Unified Chainlit UI entry point for the Magentic One team system.
Provides interactive interface for all 4 agents and orchestrated workflows.

USAGE:
    chainlit run chainlit_entry.py -w

FEATURES:
    - Individual agent interaction buttons
    - Comprehensive multi-agent scenario execution
    - Real-time status monitoring
    - Agent lifecycle management
    - Mock mode for testing without full configuration
"""

import os
import asyncio
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import chainlit as cl

from ..config.settings import load_settings, get_mock_settings, MagenticTeamSettings
from ..orchestrator import MagenticTeamRuntime
from ..agents import HotelAgent, TaxiFabricAgent, TaxiGenieAgent, EmailLogicAppsAgent

# Load environment variables
load_dotenv()

# Global runtime instance
magentic_runtime: Optional[MagenticTeamRuntime] = None
individual_agents: Dict[str, Any] = {}
settings: Optional[MagenticTeamSettings] = None
mock_mode = False

# Sample questions for each agent
HOTEL_SAMPLE_QUESTIONS = [
    "What hotels do you know about? Can you tell me about them?",
    "Can you recommend a boutique hotel in New York?",
    "Tell me about hotels with high ratings.",
    "What amenities are available at the Old Century Hotel?",
    "Are there any hotels with parking included?"
]

TAXI_FABRIC_SAMPLE_QUESTIONS = [
    "Compare taxi trips on holidays vs weekdays with fare analysis",
    "Count trips with fare >$70 and calculate percentage",
    "Compare day (7-19h) vs night (19-7h) trips and fares",
    "Identify top 5 pickup zip codes by trip volume",
    "Show passenger count distribution across all trips"
]

TAXI_GENIE_SAMPLE_QUESTIONS = [
    "What is the average fare amount per trip?",
    "How do trips vary by hour of day or day of week?",
    "What's the correlation between trip distance and fare?",
    "Which pickup zip codes have highest average fares?",
    "Find outlier trips with unusually high fares vs distance"
]

EMAIL_SAMPLE_ACTIONS = [
    "Send travel summary email with hotel and taxi analysis",
    "Send data consistency report comparing Fabric vs Genie", 
    "Send decision package with recommendations",
    "Send automated notification with current timestamp"
]

COMPREHENSIVE_SCENARIOS = [
    "Find NYC hotels with parking, analyze day/night taxi costs, and email me the summary",
    "Compare last 30 days taxi data between Fabric and Genie, report differences >5%",
    "Recommend 3 high-rated hotels near Times Square with parking, analyze nearby taxi hotspots, email decision package",
    "Help me plan a business trip: find downtown hotels with good ratings, check taxi availability patterns, and send me a comprehensive report"
]


@cl.on_chat_start
async def start():
    """Initialize the Magentic One team system when Chainlit UI starts."""
    global magentic_runtime, individual_agents, settings, mock_mode
    
    try:
        # Try to load real settings first
        try:
            settings = load_settings()
            mock_mode = False
            await cl.Message(content="🟢 **Full Configuration Mode** - All services available").send()
        except Exception as e:
            # Fall back to mock mode
            settings = get_mock_settings()
            mock_mode = True
            await cl.Message(
                content=f"🟡 **Mock Mode** - Some services unavailable: {str(e)}\n"
                       "Using mock responses for demonstration."
            ).send()
        
        # Initialize Magentic runtime
        magentic_runtime = MagenticTeamRuntime(settings)
        
        # Set custom response callback for UI
        def ui_callback(message):
            asyncio.create_task(
                cl.Message(
                    content=f"**{message.name}**\n{message.content}",
                    author=message.name
                ).send()
            )
        
        magentic_runtime.set_response_callback(ui_callback)
        
        # Initialize individual agents
        individual_agents = {
            'hotel': HotelAgent(settings.hotel),
            'taxi_fabric': TaxiFabricAgent(settings.taxi_fabric), 
            'taxi_genie': TaxiGenieAgent(settings.taxi_genie),
            'email': EmailLogicAppsAgent(settings.email)
        }
        
        # Store in session
        cl.user_session.set("magentic_runtime", magentic_runtime)
        cl.user_session.set("individual_agents", individual_agents)
        cl.user_session.set("mock_mode", mock_mode)
        
        # Display welcome message with team overview
        welcome_msg = f"""# 🤝 Welcome to Magentic One Team System!

## 🎯 **Team Overview**
Four specialized AI agents working together using Semantic Kernel orchestration:

### 🏨 **Hotel Agent** - Azure AI Search
- Hotel information and recommendations
- Ratings and amenities analysis
- Parking and location convenience

### 🚕 **Taxi Fabric Agent** - Microsoft Fabric
- Holiday vs weekday trip patterns  
- Day/night fare comparisons
- Geographic pickup analysis

### 🚕 **Taxi Genie Agent** - Databricks Genie
- Fare statistics and distributions
- Time-based usage patterns
- Distance correlation analysis

### 📧 **Email Agent** - Azure Logic Apps
- Automated email notifications
- Travel summary delivery
- Decision package distribution

{'**Mode**: ' + ('Mock Mode (Demo)' if mock_mode else 'Full Configuration') }
        
## 🚀 **How to Use**
1. **Individual Agents**: Click agent buttons below for single-agent tasks
2. **Comprehensive Scenarios**: Use the text input for multi-agent workflows
3. **Sample Questions**: Try the suggested questions for each agent
"""

        await cl.Message(content=welcome_msg).send()
        
        # Create agent interaction buttons
        await create_agent_buttons()
        
        # Create comprehensive scenario buttons
        await create_scenario_buttons()
        
        # Show system status
        await show_system_status()
        
    except Exception as e:
        await cl.Message(
            content=f"❌ **System Initialization Failed**: {str(e)}\n"
                   "Please check your configuration and try again."
        ).send()


async def create_agent_buttons():
    """Create buttons for individual agent interactions."""
    
    # Hotel Agent buttons
    hotel_actions = []
    for i, question in enumerate(HOTEL_SAMPLE_QUESTIONS):
        hotel_actions.append(
            cl.Action(
                name=f"hotel_q{i}",
                value=question,
                description=f"Hotel Question {i+1}",
                label=f"🏨 {question[:40]}{'...' if len(question) > 40 else ''}",
                payload={"agent": "hotel", "question": question}
            )
        )
    
    await cl.Message(
        content="## 🏨 **Hotel Agent** - Azure AI Search Integration\n"
               "Specializes in hotel search, recommendations, and amenity analysis.",
        actions=hotel_actions
    ).send()
    
    # Taxi Fabric Agent buttons
    fabric_actions = []
    for i, question in enumerate(TAXI_FABRIC_SAMPLE_QUESTIONS):
        fabric_actions.append(
            cl.Action(
                name=f"fabric_q{i}",
                value=question,
                description=f"Fabric Analysis {i+1}",
                label=f"🚕 {question[:40]}{'...' if len(question) > 40 else ''}",
                payload={"agent": "taxi_fabric", "question": question}
            )
        )
    
    await cl.Message(
        content="## 🚕 **Taxi Fabric Agent** - Microsoft Fabric Analytics\n"
               "Analyzes taxi trip patterns, fares, and geographic distributions.",
        actions=fabric_actions
    ).send()
    
    # Taxi Genie Agent buttons
    genie_actions = []
    for i, question in enumerate(TAXI_GENIE_SAMPLE_QUESTIONS):
        genie_actions.append(
            cl.Action(
                name=f"genie_q{i}",
                value=question,
                description=f"Genie Analysis {i+1}",
                label=f"🚕 {question[:40]}{'...' if len(question) > 40 else ''}",
                payload={"agent": "taxi_genie", "question": question}
            )
        )
    
    await cl.Message(
        content="## 🚕 **Taxi Genie Agent** - Databricks Genie Intelligence\n"
               "Queries NYC taxi dataset using natural language through Genie API.",
        actions=genie_actions
    ).send()
    
    # Email Agent buttons
    email_actions = []
    for i, action in enumerate(EMAIL_SAMPLE_ACTIONS):
        email_actions.append(
            cl.Action(
                name=f"email_a{i}",
                value=action,
                description=f"Email Action {i+1}",
                label=f"📧 {action[:40]}{'...' if len(action) > 40 else ''}",
                payload={"agent": "email", "action": action}
            )
        )
    
    await cl.Message(
        content="## 📧 **Email Agent** - Azure Logic Apps Automation\n"
               "Sends emails, notifications, and automated communications.",
        actions=email_actions
    ).send()


async def create_scenario_buttons():
    """Create buttons for comprehensive multi-agent scenarios."""
    scenario_actions = []
    
    for i, scenario in enumerate(COMPREHENSIVE_SCENARIOS):
        scenario_actions.append(
            cl.Action(
                name=f"scenario_{i}",
                value=scenario,
                description=f"Scenario {i+1}",
                label=f"🎯 Scenario {i+1}: {scenario[:50]}{'...' if len(scenario) > 50 else ''}",
                payload={"type": "comprehensive", "scenario": scenario}
            )
        )
    
    await cl.Message(
        content="## 🎯 **Comprehensive Scenarios** - Multi-Agent Orchestration\n"
               "Click below for complex workflows involving multiple agents:",
        actions=scenario_actions
    ).send()
    
    await cl.Message(
        content="## 💬 **Custom Queries**\n"
               "Or type your own comprehensive question in the message box below!\n\n"
               "**Examples:**\n"
               "• *\"Find luxury hotels in Manhattan with spa facilities, analyze taxi costs for airport transfers, and email me a travel guide\"*\n"
               "• *\"Compare weekend vs weekday taxi patterns between Fabric and Genie data sources\"*\n"
               "• *\"Help me choose between 3 hotels near Central Park and send booking recommendations\"*"
    ).send()


async def show_system_status():
    """Display current system initialization status."""
    status_msg = "## 📊 **System Status**\n"
    
    if mock_mode:
        status_msg += "- 🟡 **Mock Mode Active** - Using simulated responses\n"
        status_msg += "- ⚠️ Some external services may not be available\n"
    else:
        status_msg += "- 🟢 **Full Configuration Mode** - All services connected\n"
        status_msg += "- ✅ Real Azure services integration enabled\n"
    
    status_msg += f"\n**Agent Status:**\n"
    status_msg += "- 🏨 Hotel Agent: Ready\n"
    status_msg += "- 🚕 Taxi Fabric Agent: Ready\n"  
    status_msg += "- 🚕 Taxi Genie Agent: Ready\n"
    status_msg += "- 📧 Email Agent: Ready\n"
    status_msg += "- 🎯 Magentic Orchestrator: Initializing...\n"
    
    await cl.Message(content=status_msg).send()


# Action callbacks for hotel agent
@cl.action_callback("hotel_q0")
@cl.action_callback("hotel_q1")  
@cl.action_callback("hotel_q2")
@cl.action_callback("hotel_q3")
@cl.action_callback("hotel_q4")
async def on_hotel_question(action):
    """Handle hotel agent question clicks."""
    await handle_individual_agent_query("hotel", action.payload["question"])


# Action callbacks for taxi fabric agent  
@cl.action_callback("fabric_q0")
@cl.action_callback("fabric_q1")
@cl.action_callback("fabric_q2")
@cl.action_callback("fabric_q3")
@cl.action_callback("fabric_q4")
async def on_fabric_question(action):
    """Handle taxi fabric agent question clicks."""
    await handle_individual_agent_query("taxi_fabric", action.payload["question"])


# Action callbacks for taxi genie agent
@cl.action_callback("genie_q0")
@cl.action_callback("genie_q1")
@cl.action_callback("genie_q2")
@cl.action_callback("genie_q3")
@cl.action_callback("genie_q4")
async def on_genie_question(action):
    """Handle taxi genie agent question clicks."""
    await handle_individual_agent_query("taxi_genie", action.payload["question"])


# Action callbacks for email agent
@cl.action_callback("email_a0")
@cl.action_callback("email_a1")
@cl.action_callback("email_a2")
@cl.action_callback("email_a3")
async def on_email_action(action):
    """Handle email agent action clicks."""
    await handle_individual_agent_query("email", action.payload["action"])


# Action callbacks for comprehensive scenarios
@cl.action_callback("scenario_0")
@cl.action_callback("scenario_1")
@cl.action_callback("scenario_2")
@cl.action_callback("scenario_3")
async def on_scenario(action):
    """Handle comprehensive scenario clicks."""
    await handle_comprehensive_scenario(action.payload["scenario"])


async def handle_individual_agent_query(agent_name: str, query: str):
    """Handle individual agent queries."""
    individual_agents = cl.user_session.get("individual_agents", {})
    mock_mode = cl.user_session.get("mock_mode", False)
    
    agent = individual_agents.get(agent_name)
    if not agent:
        await cl.Message(content=f"❌ {agent_name} agent not available").send()
        return
    
    # Show user query
    await cl.Message(content=f"**👤 You asked {agent_name}:** {query}", author="You").send()
    
    # Show processing message
    processing_msg = await cl.Message(content="🤔 Processing your request...").send()
    
    try:
        # Initialize agent if needed
        if not hasattr(agent, 'agent') or agent.agent is None:
            init_result = agent.create()
            if not init_result.get('success', False):
                error_msg = init_result.get('error', 'Unknown initialization error')
                if mock_mode:
                    error_msg += " (This is expected in mock mode)"
                
                processing_msg.content = f"⚠️ Agent initialization issue: {error_msg}"
                await processing_msg.update()
                return
        
        # Execute query
        if mock_mode and agent_name in ['hotel', 'email']:
            # Provide mock responses for services that require external connections
            mock_response = get_mock_response(agent_name, query)
            processing_msg.content = f"**🤖 {agent_name.title()} Agent Response (Mock Mode):**\n\n{mock_response}"
        else:
            # Try real execution
            result = agent.run(agent.thread.id, query)
            
            if result.get('success', False):
                processing_msg.content = f"**🤖 {agent_name.title()} Agent Response:**\n\n{result.get('response', 'No response received')}"
            else:
                error_msg = result.get('error', 'Unknown execution error')
                if mock_mode:
                    mock_response = get_mock_response(agent_name, query) 
                    processing_msg.content = f"**🤖 {agent_name.title()} Agent Response (Mock):**\n\n{mock_response}\n\n*Note: {error_msg}*"
                else:
                    processing_msg.content = f"❌ **Execution Failed:** {error_msg}"
        
        await processing_msg.update()
        
    except Exception as e:
        processing_msg.content = f"❌ **Error:** {str(e)}"
        await processing_msg.update()


async def handle_comprehensive_scenario(scenario: str):
    """Handle comprehensive multi-agent scenario execution."""
    magentic_runtime = cl.user_session.get("magentic_runtime")
    mock_mode = cl.user_session.get("mock_mode", False)
    
    await cl.Message(content=f"**🎯 Comprehensive Scenario:** {scenario}", author="You").send()
    
    processing_msg = await cl.Message(content="🚀 Initializing multi-agent orchestration...").send()
    
    try:
        if mock_mode:
            # Provide mock orchestrated response
            mock_response = get_mock_orchestration_response(scenario)
            processing_msg.content = f"**🎯 Magentic Orchestration Result (Mock Mode):**\n\n{mock_response}"
            await processing_msg.update()
            return
        
        # Initialize Magentic runtime if needed
        if not magentic_runtime:
            processing_msg.content = "❌ Magentic runtime not available"
            await processing_msg.update() 
            return
        
        processing_msg.content = "🔄 Initializing agent coordination..."
        await processing_msg.update()
        
        # Initialize the orchestration system
        init_result = await magentic_runtime.initialize()
        
        if not init_result.get('success', False):
            processing_msg.content = f"❌ **Orchestration Initialization Failed:** {init_result.get('error', 'Unknown error')}"
            await processing_msg.update()
            return
        
        processing_msg.content = "⚡ Executing multi-agent workflow..."
        await processing_msg.update()
        
        # Execute the scenario
        result = await magentic_runtime.execute_scenario(scenario, "auto")
        
        if result.get('success', False):
            processing_msg.content = f"**🎯 Magentic Orchestration Complete!**\n\n**Scenario Type:** {result.get('scenario_type', 'Unknown')}\n\n**Result:**\n{result.get('result', 'No result available')}"
        else:
            processing_msg.content = f"❌ **Orchestration Failed:** {result.get('error', 'Unknown error')}"
        
        await processing_msg.update()
        
    except Exception as e:
        processing_msg.content = f"❌ **Orchestration Error:** {str(e)}"
        await processing_msg.update()


def get_mock_response(agent_name: str, query: str) -> str:
    """Generate mock responses for agents in demo mode."""
    responses = {
        "hotel": f"""🏨 **Hotel Search Results for: "{query}"**

Based on your query, I found several excellent hotel options:

**1. The Grand Central Hotel** ⭐⭐⭐⭐⭐
- Rating: 4.8/5 stars
- Amenities: ✅ Parking, WiFi, Gym, Spa
- Location: Midtown Manhattan
- Price Range: $200-350/night

**2. Brooklyn Heights Inn** ⭐⭐⭐⭐
- Rating: 4.5/5 stars  
- Amenities: ✅ Parking, WiFi, Business Center
- Location: Brooklyn Heights
- Price Range: $150-250/night

**3. Queens Plaza Hotel** ⭐⭐⭐⭐
- Rating: 4.3/5 stars
- Amenities: ✅ Parking, WiFi, Restaurant
- Location: Long Island City
- Price Range: $120-200/night

*All hotels include parking as requested and have received excellent guest reviews.*""",
        
        "taxi_fabric": f"""🚕 **Taxi Data Analysis (Microsoft Fabric)**

**Query Analysis:** {query}

**Key Findings:**
• **Total Trips Analyzed:** 1,247,832 trips (last 30 days)
• **Day vs Night Comparison:**
  - Daytime (7-19h): 743,821 trips, avg fare $16.85
  - Nighttime (19-7h): 504,011 trips, avg fare $21.40
  - Night fares are 27% higher on average

• **Geographic Hotspots:**
  1. Manhattan Midtown: 234,567 trips (18.8%)
  2. JFK Airport: 145,223 trips (11.7%)
  3. LaGuardia Airport: 98,445 trips (7.9%)

• **Passenger Distribution:**
  - 1 passenger: 68.4%
  - 2 passengers: 22.1%
  - 3+ passengers: 9.5%

*Data sourced from Microsoft Fabric lakehouse with real-time processing.*""",
        
        "taxi_genie": f"""🚕 **Taxi Data Analysis (Databricks Genie)**

**Genie Query:** {query}

**Analysis Results:**
```
SELECT AVG(fare_amount), COUNT(*) FROM samples.nyctaxi.trips 
WHERE pickup_datetime >= '2024-01-01'
```

**Statistical Summary:**
• **Average Fare:** $18.32 (σ = $12.45)
• **Median Fare:** $14.80
• **Trip Volume:** 2.1M trips analyzed

**Time-based Patterns:**
- Peak hours: 8-9 AM, 5-7 PM
- Weekend surge: +15% fare premium
- Airport trips: $45-65 average

**Distance Correlation:**
- R² = 0.73 (distance vs fare)
- Short trips (<2 miles): $8-15
- Long trips (>10 miles): $35-80

*Powered by Databricks Genie with SQL optimization.*""",
        
        "email": f"""📧 **Email Automation Result**

**Action:** {query}

✅ **Email Successfully Sent!**

**Details:**
- **To:** user@example.com
- **Subject:** Travel Analysis Summary
- **Timestamp:** 2025-01-01 10:30:00 UTC
- **Status:** Delivered
- **Tracking ID:** LA-EMAIL-001

**Content Summary:**
The email includes:
- Hotel recommendations with ratings and amenities
- Taxi cost analysis (day vs night patterns)
- Decision matrix with key insights
- Contact information for bookings

**Logic App Execution:**
- **Workflow:** SendEmailWorkflow
- **Duration:** 2.3 seconds
- **Status:** Completed successfully
- **Next Action:** None required

*Email automation powered by Azure Logic Apps.*"""
    }
    
    return responses.get(agent_name, f"Mock response for {agent_name}: {query}")


def get_mock_orchestration_response(scenario: str) -> str:
    """Generate mock orchestration response for comprehensive scenarios."""
    return f"""🎯 **Multi-Agent Orchestration Complete!**

**Scenario Executed:** {scenario}

**Agent Coordination Summary:**

**1. 🏨 Hotel Agent** - ✅ Completed
- Found 5 suitable hotels with parking
- Analyzed ratings, amenities, and locations
- Provided price comparisons and recommendations

**2. 🚕 Taxi Fabric Agent** - ✅ Completed  
- Analyzed 30-day trip patterns
- Calculated day/night fare differences (+22% night premium)
- Identified top pickup locations and peak hours

**3. 🚕 Taxi Genie Agent** - ✅ Completed
- Validated Fabric analysis with Genie dataset
- Cross-referenced fare statistics (95% consistency)
- Provided additional distance correlation insights

**4. 📧 Email Agent** - ✅ Completed
- Compiled comprehensive travel decision package  
- Sent formatted email with all recommendations
- Confirmed delivery with tracking information

**Key Insights Generated:**
• Best hotel option: Grand Central Hotel (4.8⭐, parking included)
• Optimal travel times: Avoid 8-9 AM and 5-7 PM for lower fares
• Estimated transportation costs: $15-25 typical rides, $35-50 airport
• Email summary delivered successfully to your inbox

**Total Execution Time:** 45 seconds
**Agents Coordinated:** 4/4 successful
**Decision Confidence:** 92%

*This coordinated analysis combines hotel search, data analytics, and automated communication to provide comprehensive travel planning support.*"""


@cl.on_message
async def main(message: cl.Message):
    """Handle user messages for comprehensive queries."""
    await handle_comprehensive_scenario(message.content)


@cl.on_stop
async def on_stop():
    """Clean up resources when the session stops."""
    try:
        magentic_runtime = cl.user_session.get("magentic_runtime")
        individual_agents = cl.user_session.get("individual_agents", {})
        
        if magentic_runtime:
            await magentic_runtime.cleanup()
            print("🧹 Cleaned up Magentic runtime")
        
        for agent_name, agent in individual_agents.items():
            try:
                agent.cleanup()
                print(f"🧹 Cleaned up {agent_name} agent")
            except Exception as e:
                print(f"⚠️ Error cleaning up {agent_name}: {e}")
                
    except Exception as e:
        print(f"⚠️ Error during session cleanup: {e}")


if __name__ == "__main__":
    print("To run the Magentic One team system, use:")
    print("chainlit run chainlit_entry.py -w")
    print("\nThis will start the unified interface for all 4 agents and orchestration.")