# Magentic One Team System

A comprehensive multi-agent orchestration system that coordinates four specialized AI agents using Semantic Kernel's MagenticOrchestration framework.

## 🎯 System Overview

The Magentic One Team System orchestrates four specialized agents to handle complex travel planning and data analysis scenarios:

### 🏨 **Hotel Agent** - Azure AI Search Integration
- **Purpose**: Hotel search, recommendations, and amenity analysis
- **Data Source**: Azure AI Search with hotel information index
- **Capabilities**: Location-based search, rating analysis, parking availability, price comparisons

### 🚕 **Taxi Fabric Agent** - Microsoft Fabric Analytics  
- **Purpose**: Taxi trip data analysis using Microsoft Fabric lakehouse
- **Data Source**: Microsoft Fabric with NYC taxi trip dataset
- **Capabilities**: Holiday vs weekday patterns, day/night comparisons, geographic analysis, passenger distributions

### 🚕 **Taxi Genie Agent** - Databricks Genie Intelligence
- **Purpose**: Taxi data analysis using Databricks Genie natural language interface
- **Data Source**: Databricks Genie connected to `samples.nyctaxi.trips` dataset
- **Capabilities**: Natural language queries, fare statistics, time-based trends, distance correlations

### 📧 **Email Agent** - Azure Logic Apps Automation
- **Purpose**: Automated email notifications and communications
- **Integration**: Azure Logic Apps with HTTP triggers
- **Capabilities**: Travel summaries, data reports, decision packages, automated notifications

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Chainlit Web UI                             │
│              (Single Entry Point)                              │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│              MagenticTeamRuntime                               │  
│          (Semantic Kernel Orchestrator)                        │
├─────────────────────────┬───────────────────────────────────────┤
│    StandardMagenticManager + MagenticOrchestration            │
└─────────────────────────┬───────────────────────────────────────┘
                          │
            ┌─────────────┼─────────────┐
            │             │             │
    ┌───────▼──┐   ┌─────▼─────┐   ┌───▼────┐   ┌─────▼─────┐
    │ Hotel    │   │ Taxi      │   │ Taxi   │   │ Email     │
    │ Agent    │   │ Fabric    │   │ Genie  │   │ Agent     │
    │          │   │ Agent     │   │ Agent  │   │           │
    └─────┬────┘   └─────┬─────┘   └───┬────┘   └─────┬─────┘
          │              │             │              │
    ┌─────▼────┐   ┌─────▼─────┐   ┌───▼────┐   ┌─────▼─────┐
    │ Azure    │   │Microsoft  │   │Databricks │ │ Azure     │
    │AI Search │   │ Fabric    │   │ Genie     │ │Logic Apps │
    └──────────┘   └───────────┘   └──────────┘ └───────────┘
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.9+** with virtual environment support
2. **Azure Subscription** with appropriate permissions
3. **Azure AI Foundry Project** with model deployment
4. **Required Azure Services** (see Configuration section)

### Installation

1. **Clone and Setup Environment**
   ```bash
   git clone <repository-url>
   cd foundry-samples/app
   python -m venv magentic-env
   source magentic-env/bin/activate  # Linux/Mac
   # magentic-env\Scripts\activate   # Windows
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Azure service details
   ```

4. **Start the Application**
   ```bash
   chainlit run ui/chainlit_entry.py -w
   ```

5. **Access Web Interface**
   - Open browser to `http://localhost:8000`
   - Start with individual agent buttons or comprehensive scenarios

## ⚙️ Configuration

### Required Azure Resources

#### Hotel Agent Configuration
```bash
# Azure AI Search setup
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_API_KEY=your-search-api-key
AZURE_SEARCH_INDEX=vector-search-quickstart
```

**Setup Steps:**
1. Create Azure AI Search service
2. Run hotel agent's index creation script to populate with sample data
3. Verify index contains hotel documents

#### Taxi Fabric Agent Configuration  
```bash
# Microsoft Fabric setup
PROJECT_ENDPOINT=https://your-ai-project.cognitiveservices.azure.com
MODEL_DEPLOYMENT_NAME=gpt-4o
```

**Setup Steps:**
1. Set up Microsoft Fabric workspace
2. Create lakehouse with taxi trip data
3. Configure appropriate access permissions

#### Taxi Genie Agent Configuration
```bash
# Databricks Genie setup
FOUNDRY_PROJECT_ENDPOINT=https://your-foundry-project.cognitiveservices.azure.com
FOUNDRY_DATABRICKS_CONNECTION_NAME=your-databricks-connection
```

**Setup Steps:**
1. Create Databricks workspace with Genie enabled
2. Configure connection in AI Foundry as type 'genie'
3. Ensure access to `samples.nyctaxi.trips` dataset

#### Email Agent Configuration
```bash
# Azure Logic Apps setup
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=your-resource-group  
LOGIC_APP_NAME=your-logic-app-name
TRIGGER_NAME=When_a_HTTP_request_is_received
RECIPIENT_EMAIL=your-email@example.com
```

**Setup Steps:**
1. Create Logic App with HTTP request trigger
2. Add "Send an email" action 
3. Configure email connector with appropriate permissions

#### Orchestrator Configuration
```bash
# Semantic Kernel setup
MY_AZURE_OPENAI_ENDPOINT=https://your-openai-endpoint.openai.azure.com
BING_GROUNDING_CONNECTION_NAME=your-bing-connection  # Optional
```

## 🎯 Usage Scenarios

### 1. Travel Query + Notification
**User Input**: *"Find NYC hotels with parking, analyze day/night taxi costs, and email me the summary"*

**Workflow**:
1. Hotel Agent searches for hotels with parking
2. Both Taxi agents analyze day/night cost patterns
3. Data fusion reconciles any differences between sources
4. Email Agent sends comprehensive summary

### 2. Data Consistency Check  
**User Input**: *"Compare last 30 days taxi data between Fabric and Genie, report differences >5%"*

**Workflow**:
1. Fabric Agent pulls 30-day statistics
2. Genie Agent pulls equivalent data
3. Orchestrator performs consistency analysis
4. Optional email report with findings

### 3. Comprehensive Decision Package
**User Input**: *"Recommend 3 4.5★+ hotels near Times Square with parking, analyze nearby taxi hotspots, email decision package"*

**Workflow**:
1. Hotel Agent filters by rating and location requirements
2. Taxi Agent analyzes pickup hotspots near recommended hotels
3. Optional Genie validation of hotspot data
4. Email Agent delivers formatted decision package

## 🎨 User Interface Features

### Individual Agent Interactions
- **Hotel Agent Buttons**: Quick hotel search queries
- **Taxi Fabric Buttons**: Pre-configured data analysis questions
- **Taxi Genie Buttons**: Natural language query examples
- **Email Action Buttons**: Common automation tasks

### Comprehensive Scenarios
- **Multi-agent Workflows**: Complex queries involving multiple agents
- **Real-time Orchestration**: Watch agents coordinate in real-time
- **Status Monitoring**: Track task progress and agent coordination

### System Status
- **Agent Health**: Monitor individual agent availability
- **Mock Mode**: Demo functionality without full Azure setup
- **Error Handling**: Graceful degradation and user feedback

## 🔧 Development

### Project Structure
```
app/
├── agents/                 # Individual agent implementations
│   ├── hotel_agent.py
│   ├── taxi_fabric_agent.py  
│   ├── taxi_genie_agent.py
│   └── email_logicapps_agent.py
├── orchestrator/           # Multi-agent coordination
│   ├── magentic_runtime.py
│   └── task_graph.py
├── ui/                     # User interface
│   └── chainlit_entry.py
├── config/                 # Configuration management
│   └── settings.py
├── tests/                  # Test suites
├── requirements.txt
└── .env.example
```

### Agent Interface Contract
Each agent implements a standardized interface:
```python
def create() -> Dict[str, Any]           # Initialize agent
def run(thread_id: str, prompt: str) -> Dict[str, Any]  # Execute task
def tools() -> List[Dict[str, Any]]      # Available functions
def cleanup() -> bool                    # Resource cleanup
def get_agent_info() -> Dict[str, Any]   # Agent metadata
```

### Testing

#### Unit Tests
```bash
# Run individual agent tests
pytest tests/test_hotel_agent.py
pytest tests/test_taxi_fabric_agent.py
pytest tests/test_taxi_genie_agent.py
pytest tests/test_email_agent.py
```

#### End-to-End Tests
```bash
# Run scenario tests
pytest tests/test_end_to_end_flow1.py
pytest tests/test_end_to_end_flow2.py  
pytest tests/test_end_to_end_flow3.py
```

#### Mock Mode Testing
```bash
# Test without external dependencies
chainlit run ui/chainlit_entry.py -w
# System automatically falls back to mock mode if services unavailable
```

## 🚨 Troubleshooting

### Common Issues

#### Search Index Not Found
```bash
Error: Search index 'vector-search-quickstart' not available
Solution: Run hotel agent's index creation script first
```

#### Databricks Connection Error
```bash
Error: Connection is not of type 'genie'
Solution: Verify Databricks connection type in AI Foundry
```

#### Logic App Trigger Error
```bash
Error: No callback URL returned for Logic App
Solution: Check Logic App name and trigger name match configuration
```

#### Model Not Found
```bash
Error: Model deployment 'gpt-4o' not found
Solution: Verify model deployment name in AI Foundry project
```

#### Permission Errors
```bash
Error: Forbidden - insufficient permissions
Solution: Ensure proper RBAC roles assigned to Azure resources
```

### Debug Mode

Enable verbose logging:
```bash
export CHAINLIT_DEBUG=true
chainlit run ui/chainlit_entry.py -w
```

View agent communication:
```bash
# Check console output for agent message flows
# Each agent interaction is logged with timestamps
```

### Mock Mode

If external services are unavailable, the system automatically enters mock mode:
- Hotel searches return sample hotel data
- Taxi analysis returns synthetic statistics
- Email actions return success confirmations
- Orchestration shows workflow completion

## 📊 Monitoring and Observability

### Agent Metrics
- **Response Times**: Individual agent execution latency
- **Success Rates**: Task completion statistics  
- **Error Patterns**: Common failure modes and resolution

### Orchestration Metrics  
- **Task Graphs**: Visual representation of multi-agent workflows
- **Coordination Efficiency**: Agent interaction patterns
- **Resource Utilization**: Azure service usage tracking

### User Analytics
- **Query Patterns**: Most common user requests
- **Scenario Usage**: Popular multi-agent workflows
- **Satisfaction**: Success/failure rates by scenario type

## 🔐 Security Considerations

### Authentication
- Uses `DefaultAzureCredential` for seamless Azure authentication
- Supports managed identity in Azure environments
- Optional service principal configuration for development

### Data Privacy
- No user data persisted between sessions
- All credentials stored in environment variables only
- Email content only sent to configured recipient addresses

### Network Security
- HTTPS connections to all Azure services
- Logic Apps secured with callback URL authentication
- Databricks integration uses Entra ID tokens

## 🛣️ Roadmap

### Version 1.1 (Planned)
- [ ] Advanced conflict resolution strategies
- [ ] Custom agent plugin framework
- [ ] Persistent conversation history
- [ ] Advanced error recovery mechanisms

### Version 1.2 (Future)
- [ ] Multi-language support (中文 interface)
- [ ] Custom orchestration patterns
- [ ] Integration with additional Azure services
- [ ] Performance optimization and caching

### Version 2.0 (Long-term)
- [ ] Voice interaction support
- [ ] Mobile-responsive UI
- [ ] Advanced analytics dashboard
- [ ] Multi-tenant support

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Install development dependencies: `pip install -r requirements.txt`
4. Run tests: `pytest`
5. Submit pull request

### Code Standards
- Follow PEP 8 style guidelines
- Include type hints for all public functions
- Write docstrings for modules, classes, and functions
- Add unit tests for new functionality

### Documentation
- Update README for new features
- Include inline code comments for complex logic
- Provide configuration examples
- Document breaking changes

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Resources
- [Azure AI Foundry Documentation](https://docs.microsoft.com/en-us/azure/ai-services/)
- [Semantic Kernel Documentation](https://learn.microsoft.com/en-us/semantic-kernel/)
- [Chainlit Documentation](https://docs.chainlit.io/)

### Getting Help
1. Check troubleshooting section above
2. Review existing issues in the repository
3. Create new issue with detailed description
4. Include error logs and configuration (sanitized)

---

*Built with ❤️ using Azure AI Services, Semantic Kernel, and Chainlit*