from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

from dotenv import load_dotenv
load_dotenv()

import asyncio

async def main():
    client=MultiServerMCPClient(
        {
            "math":{
                "command":"python",
                "args":["mathserver.py"], ## Ensure correct absolute path
                "transport":"stdio",
            
            },
            "weather": {
                "url": "http://localhost:8000/mcp",  # Ensure server is running here
                "transport": "streamable_http",
            }

        }
    )

    import os
    os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")

    tools=await client.get_tools()
    # Try mixtral which often handles tool calls better
    model=ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    
    # Add prompt to clarify tool usage
#     from langchain_core.prompts import ChatPromptTemplate
#     prompt = ChatPromptTemplate.from_messages([
#         ("system", """You are a helpful assistant that uses tools to solve math problems.
# IMPORTANT: When you need to use multiple tools:
# 1. Call ONE tool at a time with concrete values (numbers, strings, etc.)
# 2. Wait for the tool result
# 3. Use that result in the next tool call
# 4. NEVER nest function calls or pass function objects as parameters
# 5. Each tool parameter must be a concrete value (integer, string, etc.), not another function call"""),
#         ("placeholder", "{messages}")
#     ])
    
    agent=create_react_agent(
        model,
        tools
    )

    math_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
    )

    print("Math response:", math_response['messages'][-1].content)

    weather_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what is the weather in California?"}]}
    )
    print("Weather response:", weather_response['messages'][-1].content)

asyncio.run(main())