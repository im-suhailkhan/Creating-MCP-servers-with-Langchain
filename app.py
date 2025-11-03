import streamlit as st
import asyncio
import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="MCP Server Chat",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = None
if "initialized" not in st.session_state:
    st.session_state.initialized = False
if "tool_names" not in st.session_state:
    st.session_state.tool_names = []

async def _initialize_agent():
    """Initialize the MCP client and agent"""
    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": ["mathserver.py"],
                "transport": "stdio",
            },
            "weather": {
                "url": "http://localhost:8000/mcp",
                "transport": "streamable_http",
            }
        }
    )
    
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
    
    tools = await client.get_tools()
    
    # Debug: Print available tools and store in session state
    tool_names = [tool.name for tool in tools]
    print(f"Available tools: {tool_names}")
    st.session_state.tool_names = tool_names
    
    # Verify get_weather tool exists
    if "get_weather" not in tool_names:
        print("WARNING: get_weather tool not found in loaded tools!")
        print(f"Actual tools loaded: {tool_names}")
    
    # Create system message - extremely direct and forceful
    system_message = f"""YOU HAVE ACCESS TO REAL-TIME WEATHER DATA VIA THE get_weather TOOL.

Available tools: {', '.join(tool_names)}

MANDATORY INSTRUCTIONS:
1. When asked about weather/temperature/climate ANYWHERE, you MUST use get_weather tool
2. DO NOT say you don't have access - you DO have get_weather
3. For "weather in San Francisco" → IMMEDIATELY call get_weather("San Francisco")
4. DO NOT make excuses - just call the tool
5. Report the tool result directly to the user

Tool format: get_weather("City Name") where city is a string parameter"""

    from langchain_core.prompts import ChatPromptTemplate
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("placeholder", "{messages}")
    ])
    
    model = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    agent = create_react_agent(model, tools, prompt=prompt)
    
    return agent

@st.cache_resource
def initialize_agent():
    """Initialize the MCP client and agent (cached to avoid reinitialization)"""
    # Run async initialization
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    agent = loop.run_until_complete(_initialize_agent())
    return agent

def get_agent_response(user_input: str):
    """Get response from the agent"""
    if st.session_state.agent is None:
        with st.spinner("Initializing agent and connecting to MCP servers..."):
            st.session_state.agent = initialize_agent()
    
    agent = st.session_state.agent
    
    # Create event loop if needed
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Configure with higher recursion limit to prevent infinite loops
    config = {
        "recursion_limit": 50,  # Increase from default 25
        "configurable": {
            "thread_id": "1"
        }
    }
    
    # Get response from agent
    try:
        response = loop.run_until_complete(
            agent.ainvoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config=config
            )
        )
        return response['messages'][-1].content
    except Exception as e:
        error_msg = str(e)
        if "recursion limit" in error_msg.lower():
            return "I got stuck in a loop. Please try rephrasing your question. For weather queries, try: 'Get weather for New York' or 'What's the weather in New York?'"
        raise

# Sidebar for instructions
with st.sidebar:
    st.header("🤖 MCP Server Chat")
    st.markdown("""
    ### Available Tools
    - **Math Server**: 
      - `add(a, b)` - Add two numbers
      - `multiply(a, b)` - Multiply two numbers
    
    - **Weather Server**: 
      - `get_weather(location)` - Get current weather
    
    ### Example Queries
    - "What's (3 + 5) × 12?"
    - "What is the weather in New York?"
    - "Add 25 and 17, then multiply by 3"
    """)
    
    if st.button("🔄 Reset Chat"):
        st.session_state.messages = []
        st.session_state.initialized = False
        st.session_state.agent = None
        initialize_agent.clear()  # Clear cache
        st.rerun()
    
    st.markdown("---")
    st.markdown("**Status:**")
    if st.session_state.agent is not None:
        st.success("✅ Agent Ready")
        
        # Show loaded tools
        if st.session_state.tool_names:
            st.info(f"📦 Tools: {', '.join(st.session_state.tool_names)}")
        
        # Check if weather server is running
        import requests
        try:
            response = requests.get("http://localhost:8000/mcp", timeout=2)
            st.success("✅ Weather Server Connected")
        except:
            st.warning("⚠️ Weather Server Not Running\nStart with: `uv run python weather.py`")
    else:
        st.info("⏳ Initializing...")

# Main chat interface
st.title("🤖 MCP Server Chat Interface")
st.markdown("Ask me anything! I can help with math calculations and weather information.")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = get_agent_response(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

