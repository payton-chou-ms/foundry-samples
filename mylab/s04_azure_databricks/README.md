# AI Foundry Connections - Azure Databricks with Genie

This repository hosts samples and examples for using AI Foundry Connections with Agents, specifically for Azure Databricks integration with Genie API.

## Overview

AI Foundry Connections provides integration capabilities between various resources and AI Foundry Agent. This repository contains example implementations, best practices, and starter templates to help you build intelligent applications using AI Foundry.

## Samples

The samples in this repository demonstrate:
- How to connect AI Foundry services with agents
- Integration patterns for different use cases  
- Best practices for implementation
- Interactive Chainlit UI for data analysis with sample question buttons

## Available Applications

### 1. Command Line Samples
- `sample_agent_adb_genie_conversation.py` - Agent with conversation context


### 2. **Chainlit Interactive UI** 🆕
- `chainlit_agent_adb_genie.py` - **Full interactive web UI with sample question buttons**
- Features:
  - 🚕 **Interactive chat interface** for NYC taxi data analysis
  - 📊 **Pre-configured sample question buttons** (fare stats, time trends, etc.)
  - 🆔 **Agent lifecycle management** (displays agent ID, auto-cleanup)
  - ⚡ **Real-time analysis** through Databricks Genie API
  - 🔄 **Session management** with conversation context

## Quick Start - Chainlit UI

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.template .env
   # Edit .env with your Azure AI Foundry project details
   ```

3. **Run the interactive UI:**
   ```bash
   chainlit run chainlit_agent_adb_genie.py
   ```

4. **Open your browser** to the URL shown (usually http://localhost:8000)

5. **Click the sample question buttons** or type your own questions about NYC taxi data!

See [CHAINLIT_README.md](CHAINLIT_README.md) for detailed instructions.

## Agent Configuration

The agent is specifically configured for **NYC taxi trip data analysis** with instructions based on `sample.txt`:

- **Dataset**: Connected to Databricks "samples.nyctaxi.trips" dataset  
- **Capabilities**: Fare statistics, time-based trends, distance vs fare analysis, geographic comparisons, outlier detection
- **Sample Questions**: 5 pre-configured buttons for common analysis tasks
- **Response Style**: Clear explanations with SQL queries and natural language summaries

## Prerequisites

- Python 3.12 or later.
- An [Azure subscription][azure_sub].
- A [project in Azure AI Foundry](https://learn.microsoft.com/azure/ai-studio/how-to/create-projects).
- The Project endpoints. It can be found in your Azure AI Foundry project overview page.
- Entra ID is needed to authenticate the client. Your application needs an object that implements the [TokenCredential](https://learn.microsoft.com/python/api/azure-core/azure.core.credentials.tokencredential) interface. Code samples here use [DefaultAzureCredential](https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential). To get that working, you will need:
  * An appropriate role assignment. see [Role-based access control in Azure AI Foundry portal](https://learn.microsoft.com/azure/ai-foundry/concepts/rbac-ai-foundry). Role assigned can be done via the "Access Control (IAM)" tab of your Azure AI Project resource in the Azure portal.
  * [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed.
  * You are logged into your Azure account by running `az login`.
  * Note that if you have multiple Azure subscriptions, the subscription that contains your Azure AI Project resource must be your default subscription. Run `az account list --output table` to list all your subscription and see which one is the default. Run `az account set --subscription "Your Subscription ID or Name"` to change your default subscription.

