# Multi-Agent Orchestration with Semantic Kernel Magentic

This directory contains the design specification, implementation files, and documentation for orchestrating multiple AI agents using Semantic Kernel's magentic functionality.

## Directory Structure

- `design_specification.md` - Comprehensive design document for multi-agent orchestration
- `requirements_specification.md` - Software requirements specification
- `step5_magentic_ui.py` - Multi-agent Chainlit UI implementation 
- `orchestration_scenarios.md` - Three workflow scenarios documentation
- `agent_coordination.py` - Core orchestration logic
- `requirements.txt` - Python dependencies

## Agents Overview

The system orchestrates four specialized agents:

1. **Hotel Search Agent** (Azure AI Search) - Hotel recommendations and information
2. **Logic App Agent** (Azure Logic Apps) - Automated workflows and email notifications  
3. **Data Analysis Agent** (Microsoft Fabric) - Taxi trip data analysis
4. **Databricks Agent** (Azure Databricks) - Advanced data processing with Genie

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the multi-agent UI
chainlit run step5_magentic_ui.py
```

## Documentation

Please refer to the following documents for detailed information:
- [Design Specification](design_specification.md)
- [Requirements Specification](requirements_specification.md)
- [Orchestration Scenarios](orchestration_scenarios.md)