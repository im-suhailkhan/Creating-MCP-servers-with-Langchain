# MCP Server Creation

A comprehensive demonstration of creating and integrating multiple Model Context Protocol (MCP) servers with LangChain agents using Groq AI models.

## Overview

This project showcases how to:
- Create multiple MCP servers using FastMCP (Math and Weather servers)
- Connect multiple MCP servers to a LangChain agent using `MultiServerMCPClient`
- Use different transport protocols (stdio and streamable HTTP)
- Build an AI agent that can dynamically use tools from multiple servers

## Features

- **Multiple MCP Servers**: Two example servers demonstrating different transport mechanisms
  - **Math Server**: Provides arithmetic operations (addition, multiplication) via stdio transport
  - **Weather Server**: Provides weather information via HTTP transport
- **Multi-Server Client**: Seamlessly connects to and manages multiple MCP servers
- **LangChain Integration**: Uses LangGraph's ReAct agent pattern for tool orchestration
- **Groq AI Models**: Leverages fast inference with Groq's Llama models

## Architecture

```
┌─────────────┐
│   Client    │
│  (LangChain)│
└──────┬──────┘
       │
       ├─────────────────┐
       │                 │
┌──────▼──────┐   ┌───────▼──────┐
│ Math Server │   │Weather Server│
│  (stdio)    │   │   (HTTP)     │
└─────────────┘   └──────────────┘
```

## Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip
- Groq API key (get one at [console.groq.com](https://console.groq.com))

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd MCP_Server_Creation
```

2. Install dependencies using uv:
```bash
uv sync
```

Or using pip:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```bash
cp env.example .env
# Then edit .env and add your actual Groq API key
```

Or manually create `.env`:
```bash
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```

## Project Structure

```
MCP_Server_Creation/
├── app.py             # Streamlit web UI (recommended interface)
├── client.py          # Command-line client connecting to multiple MCP servers
├── mathserver.py      # Math MCP server (stdio transport)
├── weather.py         # Weather MCP server (HTTP transport)
├── requirements.txt   # Python dependencies
├── pyproject.toml     # Project configuration
├── env.example        # Environment variables template
└── README.md          # This file
```

## Usage

### Option 1: Web UI (Recommended)

The easiest way to interact with the MCP servers is through the Streamlit web interface.

#### Step 1: Update your `.env` file

Make sure your `.env` file contains:
```bash
GROQ_API_KEY=your_groq_api_key_here
WEATHER_API_KEY=your_weather_api_key_here
```

#### Step 2: Start the Weather Server

In a separate terminal, start the HTTP-based weather server:

```bash
uv run python weather.py
```

The server will start on `http://localhost:8000/mcp`.

#### Step 3: Run the Streamlit UI

In another terminal, start the web interface:

```bash
uv run streamlit run app.py
```

The UI will open in your browser automatically. You can then:
- Chat with the agent
- Ask math questions: "What's (3 + 5) × 12?"
- Ask weather questions: "What is the weather in New York?"
- Combine operations: "Add 25 and 17, then multiply by 3"

### Option 2: Command Line Client

If you prefer the command line interface:

#### Step 1: Start the Weather Server

```bash
uv run python weather.py
```

#### Step 2: Run the Client

In another terminal:

```bash
uv run python client.py
```

The client will:
1. Connect to both the Math server (via stdio) and Weather server (via HTTP)
2. Create a LangChain agent with tools from both servers
3. Process example queries:
   - Math calculation: "(3 + 5) x 12"
   - Weather query: "what is the weather in California?"

## How It Works

### Math Server (`mathserver.py`)
- Uses FastMCP to create a server with two tools: `add` and `multiply`
- Runs via stdio transport (standard input/output)
- Automatically spawned by the client when needed

### Weather Server (`weather.py`)
- Uses FastMCP with HTTP transport
- Provides a `get_weather` tool
- Must be running independently before the client connects

### Client (`client.py`)
- Uses `MultiServerMCPClient` to manage multiple MCP servers
- Creates a ReAct agent using LangGraph's `create_react_agent`
- Dynamically loads tools from all connected servers
- Uses Groq's LLM for fast inference

## Technologies Used

- **MCP (Model Context Protocol)**: Protocol for connecting AI models to external tools
- **FastMCP**: Fast and easy way to create MCP servers in Python
- **LangChain**: Framework for building LLM applications
- **LangGraph**: Build stateful, multi-actor applications with LLMs
- **LangChain MCP Adapters**: Integration layer between LangChain and MCP
- **Groq**: High-performance AI inference platform
- **uv**: Fast Python package installer and resolver

## Example Output

```
Processing request of type ListToolsRequest
Math response: The result is 96
Weather response: It's always raining in California
```

## Configuration

### Changing the AI Model

Edit `client.py` to use a different Groq model:

```python
model=ChatGroq(model="llama-3.1-8b-instant", temperature=0)
```

Available models include:
- `llama-3.1-8b-instant`
- `llama-3.3-70b-versatile`
- `mixtral-8x7b-32768`

### Adding More Servers

To add additional MCP servers, update the `MultiServerMCPClient` configuration in `client.py`:

```python
client=MultiServerMCPClient(
    {
        "math": {...},
        "weather": {...},
        "your_server": {
            "command": "python",
            "args": ["yourserver.py"],
            "transport": "stdio",
        }
    }
)
```

## Troubleshooting

### ModuleNotFoundError

If you get import errors, ensure you're using `uv run`:

```bash
uv run python client.py
```

This ensures you're using the virtual environment with all dependencies installed.

### Port Already in Use

If port 8000 is already in use:

```bash
# Find the process using port 8000
lsof -ti:8000

# Kill the process
kill <process_id>
```

### Server Connection Errors

Ensure the weather server is running before starting the client:
```bash
# Terminal 1
uv run python weather.py

# Terminal 2
uv run python client.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Add your license here]

## Acknowledgments

- Built with [MCP](https://modelcontextprotocol.io/)
- Powered by [Groq](https://groq.com/)
- Uses [LangChain](https://www.langchain.com/) and [LangGraph](https://langchain-ai.github.io/langgraph/)

