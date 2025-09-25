# Chainlit Agent for Databricks Taxi Data Analysis

Welcome to the **Databricks Taxi Data Analysis Agent**! 🚕

This application provides an interactive Chainlit-based user interface for analyzing NYC taxi trip data using Azure AI Foundry and Databricks Genie.

## ✨ Features

- **Interactive UI**: Chat-based interface with sample question buttons
- **Agent Lifecycle Management**: Displays agent ID and automatically cleans up when session ends
- **Sample Questions**: Pre-configured buttons for common analysis tasks
- **Real-time Analysis**: Connects to Databricks Genie for live data analysis
- **Session Management**: Maintains conversation context across multiple questions

## 🚀 Getting Started

### Prerequisites

1. **Azure AI Foundry Project**: Set up with Databricks connection
2. **Environment Variables**: Configure the required variables
3. **Dependencies**: Install required Python packages

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your `.env` file:
```env
FOUNDRY_PROJECT_ENDPOINT=your_project_endpoint
FOUNDRY_DATABRICKS_CONNECTION_NAME=your_databricks_connection
MODEL_DEPLOYMENT_NAME=gpt-4o
```

3. Run the Chainlit application:
```bash
chainlit run chainlit_agent_adb_genie.py
```

4. Open your browser to the URL shown in the terminal (usually `http://localhost:8000`)

## 🎯 Sample Questions

The application provides pre-configured buttons for these types of analysis:

1. **Fare Statistics** (平均車資)
   - "What is the average fare amount per trip?"

2. **Time-based Trends** (依時間的趨勢)
   - "How does the number of trips vary by hour of the day or day of the week?"

3. **Distance vs Fare Analysis** (距離 vs 車資關係)
   - "What is the correlation between trip distance and fare amount?"

4. **Geographic Comparisons** (地區比較)
   - "Which pickup zip codes have the highest average fares?"

5. **Outlier Detection** (異常值分析)
   - "Are there any outlier trips with unusually high fare amounts compared to their distance?"

## 🔧 Agent Configuration

The agent is configured with specialized instructions for taxi data analysis:

- **Dataset**: Connected to Databricks "samples.nyctaxi.trips" dataset
- **Role**: Data analysis specialist for taxi trip data
- **Capabilities**: SQL query generation and result summarization
- **Response Style**: Clear explanations with both queries and natural language summaries

## 🔄 Agent Lifecycle

- **Creation**: Agent is created when you start a new chat session
- **Display**: Agent ID is shown in the welcome message
- **Management**: Session maintains agent state across multiple questions
- **Cleanup**: Agent is automatically deleted when you close the UI or session ends

## 🛠️ Technical Details

- **Framework**: Chainlit for interactive UI
- **AI Platform**: Azure AI Foundry
- **Data Source**: Databricks Genie API
- **Authentication**: Azure Default Credential
- **Model**: GPT-4o (configurable)

## 📝 Usage Tips

1. **Sample Questions**: Click the pre-configured buttons for quick analysis
2. **Custom Questions**: Type your own questions about taxi trip data
3. **Context**: The agent maintains conversation context across questions
4. **Agent ID**: Note the displayed agent ID for debugging or reference
5. **Session**: Each browser session creates a new agent instance

## 🔐 Security

- Uses Azure Default Credential for authentication
- Proper token management for Databricks access
- Automatic cleanup of resources on session end
- No sensitive data stored in local session

## 🆘 Troubleshooting

### Common Issues:

1. **Environment Variables**: Ensure all required variables are set
2. **Authentication**: Check Azure credentials are properly configured
3. **Connection**: Verify Databricks connection is of type 'genie'
4. **Dependencies**: Make sure all packages are installed correctly

### Error Messages:

- **"Agent not properly initialized"**: Refresh the page and check environment variables
- **"Connection is not of type 'genie'"**: Verify your Databricks connection configuration
- **Token errors**: Check Azure authentication and Databricks access permissions

---

*This application demonstrates the integration of Azure AI Foundry, Databricks Genie, and Chainlit for interactive data analysis.*