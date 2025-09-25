#!/usr/bin/env python3
"""
Demo version of the Chainlit agent application that can run without Azure dependencies
for demonstration purposes.
"""

import os
import chainlit as cl
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Sample questions from sample.txt
SAMPLE_QUESTIONS = [
    "What is the average fare amount per trip? (平均車資)",
    "How does the number of trips vary by hour of the day or day of the week? (依時間的趨勢)",
    "What is the correlation between trip distance and fare amount? (距離 vs 車資關係)",
    "Which pickup zip codes have the highest average fares? (地區比較)",
    "Are there any outlier trips with unusually high fare amounts compared to their distance? (異常值分析)"
]

@cl.on_chat_start
async def start():
    """Initialize the demo UI components when chat starts."""
    
    # Simulate agent ID for demo
    agent_id = "demo-agent-12345"
    
    # Send welcome message with agent ID and sample questions
    welcome_msg = f"""# Welcome to Databricks Taxi Data Analysis Agent! 🚕

**Agent ID:** `{agent_id}`

I'm here to help you analyze the NYC taxi trip dataset. You can ask me questions about fare statistics, time-based trends, distance vs fare relationships, geographic comparisons, and outlier detection.

**Try these sample questions:**"""

    await cl.Message(content=welcome_msg).send()

    # Create sample question buttons
    actions = []
    for i, question in enumerate(SAMPLE_QUESTIONS):
        actions.append(
            cl.Action(
                name=f"sample_question_{i}",
                value=question.split("(")[0].strip(),  # Remove Chinese translation for cleaner button text
                label=f"📊 {question}",
                description=f"Ask: {question.split('(')[0].strip()}"
            )
        )

    await cl.Message(
        content="**DEMO MODE**: Click any button below to see how sample questions would work:",
        actions=actions
    ).send()

@cl.action_callback("sample_question_0")
async def sample_question_0(action):
    await handle_sample_question(action.value)

@cl.action_callback("sample_question_1") 
async def sample_question_1(action):
    await handle_sample_question(action.value)

@cl.action_callback("sample_question_2")
async def sample_question_2(action):
    await handle_sample_question(action.value)

@cl.action_callback("sample_question_3")
async def sample_question_3(action):
    await handle_sample_question(action.value)

@cl.action_callback("sample_question_4")
async def sample_question_4(action):
    await handle_sample_question(action.value)

async def handle_sample_question(question):
    """Handle sample question button clicks (demo version)."""
    # Send the question as a user message
    await cl.Message(
        content=question,
        author="You"
    ).send()
    
    # Simulate processing
    await cl.Message(content="🤔 *DEMO: Analyzing your question...*").send()
    
    # Provide demo response
    demo_responses = {
        "What is the average fare amount per trip?": """
**Demo Analysis Result:**

Based on the NYC taxi dataset analysis:
- **Average fare amount**: $13.42 per trip
- **Query used**: `SELECT AVG(fare_amount) FROM samples.nyctaxi.trips`
- **Dataset size**: ~1.4 million trips analyzed

The average fare shows typical NYC taxi pricing, with most trips falling in the $8-$20 range.
        """,
        "How does the number of trips vary by hour of the day or day of the week?": """
**Demo Analysis Result:**

Time-based trip patterns:
- **Peak hours**: 6-9 AM and 5-8 PM (rush hours)
- **Busiest day**: Friday (22% more trips than average)
- **Lowest activity**: 3-5 AM (only 2% of daily trips)

This shows typical urban transportation patterns with clear commuter peaks.
        """,
        "What is the correlation between trip distance and fare amount?": """
**Demo Analysis Result:**

Distance vs Fare correlation:
- **Correlation coefficient**: 0.78 (strong positive correlation)
- **Average fare per mile**: $4.20
- **Base fare**: ~$2.50 (y-intercept)

The strong correlation indicates fair pricing based on distance, with additional base fare component.
        """,
        "Which pickup zip codes have the highest average fares?": """
**Demo Analysis Result:**

Top 5 pickup zones by average fare:
1. **Newark Airport**: $45.20 avg (long-distance trips)
2. **JFK Airport**: $42.15 avg (airport surcharges)
3. **Manhattan Financial District**: $18.35 avg
4. **Midtown West**: $16.80 avg
5. **Upper East Side**: $15.25 avg

Airport pickups show significantly higher fares due to distance and surcharges.
        """,
        "Are there any outlier trips with unusually high fare amounts compared to their distance?": """
**Demo Analysis Result:**

Outlier Detection Summary:
- **Outliers identified**: 1,247 trips (0.09% of total)
- **Criteria**: Fare > 3x expected based on distance
- **Highest outlier**: $847.50 for 2.1 mile trip
- **Common causes**: Wait time charges, toll roads, surge pricing

Most outliers are legitimate due to traffic delays or special circumstances.
        """
    }
    
    response = demo_responses.get(question, "This is a demo response showing how the agent would analyze your taxi data question.")
    
    await cl.Message(
        content=response,
        author="Databricks Agent (Demo)"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """Handle user messages (demo version)."""
    await cl.Message(
        content=f"**DEMO MODE**: In the real application, I would analyze your question: '{message.content}' using the Databricks Genie API and return actual taxi data insights.",
        author="Databricks Agent (Demo)"
    ).send()

@cl.on_stop
async def on_stop():
    """Clean up demo when session ends."""
    print("🧹 Demo session ended - in real app, agent would be deleted here")

if __name__ == "__main__":
    print("Demo version - to run: chainlit run demo_chainlit_app.py")