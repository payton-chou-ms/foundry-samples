# Microsoft Fabric Taxi Data Analysis Agent

This sample demonstrates how to use Azure AI Foundry agents to analyze taxi trip data from Microsoft Fabric lakehouse, with both CLI and web UI interfaces.

## Features

### Updated Agent Configuration
- Agent personality defined based on questions from `sample.txt`
- Focused on specific analysis capabilities:
  - Public holidays vs weekdays analysis
  - High-fare trip analysis (>$70)
  - Daytime vs nighttime patterns
  - Geographic pickup analysis
  - Passenger count distribution

### Two Interface Options

#### 1. Command Line Interface (CLI)
- Run: `python sample_agents_fabric.py`
- Interactive menu with sample questions
- Displays agent ID for tracking
- Automatic cleanup on exit

#### 2. Chainlit Web UI
- Run: `chainlit run chainlit_app.py`
- Interactive web interface
- Sample question hint buttons
- Agent lifecycle management (shows agent ID, auto-cleanup on UI close)
- Real-time chat interface

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   Copy `.env.template` to `.env` and set:
   ```
   PROJECT_ENDPOINT=your_azure_ai_foundry_project_endpoint
   MODEL_DEPLOYMENT_NAME=your_model_deployment_name
   ```

3. **Prerequisites**
   - Azure AI Foundry project with deployed model
   - Microsoft Fabric lakehouse with taxi trip data
   - Appropriate Azure credentials

## Usage

### CLI Version
```bash
python sample_agents_fabric.py
```

Choose from:
- 1-5: Sample questions from sample.txt
- 9: Custom query
- 0: Exit

### Chainlit Web UI Version  
```bash
chainlit run chainlit_app.py
```

Features:
- Click hint buttons to send sample questions
- Type custom queries in chat
- View agent ID in welcome message
- Automatic agent cleanup when closing browser

## Sample Questions (from sample.txt)

1. Compare taxi trips on public holidays vs regular weekdays
2. Analyze trips with fare amounts greater than $70
3. Compare daytime (7:00-19:00) vs nighttime (19:00-7:00) patterns
4. Identify top 5 pickup zip codes by trip volume
5. Determine passenger count distribution and mode

## Agent Capabilities

The agent can analyze various aspects of taxi trip data:
- Trip counts and revenue statistics
- Geographic patterns and hotspots
- Time-based analysis (hourly, daily, seasonal)
- Fare and payment pattern analysis
- Anomaly detection
- Trend analysis and insights

## File Structure

- `sample_agents_fabric.py` - CLI version with updated agent configuration
- `chainlit_app.py` - New Chainlit web UI implementation
- `taxi_query_functions.py` - Mock data functions (replace with real Fabric queries)
- `sample.txt` - Sample questions used for agent personality definition
- `requirements.txt` - Python dependencies
- `.env.template` - Environment variable template