# Step 1: Load Environment Variables
from dotenv import load_dotenv
load_dotenv()

# Step 2: Setup API Keys
import os

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Step 3: Setup LLMs and Tools
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults

# Default Models
openai_llm = ChatOpenAI(model="gpt-4o-mini")
groq_llm = ChatGroq(model="llama-3.3-70b-versatile")

# Search Tool
search_tool = TavilySearchResults(max_results=2)

# Step 4: Setup AI Agent
from langgraph.prebuilt import create_react_agent
from langchain_core.messages.ai import AIMessage
from langchain_core.messages import HumanMessage, SystemMessage


def get_response_from_ai_agent(
    llm_id,
    query,
    allow_search,
    system_prompt,
    provider
):

    # Select Model Provider
    if provider == "Groq":
        llm = ChatGroq(model=llm_id)

    elif provider == "OpenAI":
        llm = ChatOpenAI(model=llm_id)

    else:
        return "Invalid provider selected"

    # Setup Tools
    tools = [search_tool] if allow_search else []

    # Create Agent
    agent = create_react_agent(
        model=llm,
        tools=tools
    )

    # Convert Query List to String
    user_query = query[0] if isinstance(query, list) else query

    # Proper Message Format
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_query)
    ]

    # Invoke Agent
    response = agent.invoke({
        "messages": messages
    })

    # Extract Messages
    response_messages = response.get("messages", [])

    # Extract AI Responses
    ai_responses = [
        message.content
        for message in response_messages
        if isinstance(message, AIMessage)
    ]

    # Return Final AI Response
    if ai_responses:
        return ai_responses[-1]

    return "No response generated"