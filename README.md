# Autonomous Factory Manager (AFM) v2.0

The **Autonomous Factory Manager** is a dynamic simulation where an AI agent acts as the operator of a digital manufacturing plant. This AI agent continuously monitors key business metrics like inventory, funds, and machine status to make autonomous, strategic decisions that optimize production efficiency. It adapts to changing market conditions and operational challenges, demonstrating how AI agents can independently manage complex workflows and drive successful outcomes in a simulated industrial environment.

## Features

- **Agentic Controller**: Powered by Google Gemini 2.5 Flash using the Google Agent Development Kit (ADK).
- **State Engine**: A Python-based digital twin simulation of a factory.
- **Dynamic Forecasting**: Market demand and prices fluctuate based on a sine-wave model.
- **Persistent Memory**: Factory state and job history are logged to a local SQLite database (`factory.db`).
- **Production-Ready**: Runs asynchronously with robust session management.

## Setup

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd digital_factory
    ```

2.  **Create a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install google-adk google-generativeai
    ```

4.  **Set up your API Key**:
    Ensure you have a Google Cloud Project with the Gemini API enabled.
    ```bash
    export GOOGLE_API_KEY="your_api_key_here"
    ```

## Usage

Run the main application:
```bash
python3 main.py
```

Interact with the agent via the command line. You can ask it to:
- "Start a job for 10 units"
- "Check factory status"
- "Get market forecast"
- "Analyze financials"

## Components

- `main.py`: Entry point for the simulation.
- `agent.py`: The AI agent implementation using Google ADK.
- `state_engine.py`: The core logic of the factory simulation.
- `tools.py`: The interface between the agent and the state engine.
