# Step 1: Load Environment Variables
from dotenv import load_dotenv
load_dotenv()

# Step 2: Setup API Keys
import os
import json

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Step 3: Setup LLMs and Tools
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain.tools import tool

import mock_db

# Default Models
openai_llm = ChatOpenAI(model="gpt-4o-mini")
groq_llm = ChatGroq(model="llama-3.3-70b-versatile")

# Search Tool (Optional fallback for general queries)
search_tool = TavilySearch(max_results=2)

# --- Fintech Domain Tools ---

@tool
def lookup_transaction(transaction_id: str) -> str:
    """Look up a transaction by its ID to get details like amount, status, date, and duplicate count."""
    data = mock_db.get_transaction(transaction_id)
    mock_db.log_audit_event("LOOKUP_TRANSACTION", {"transaction_id": transaction_id})
    return json.dumps(data)

@tool
def evaluate_refund_policy(transaction_id: str) -> str:
    """Evaluate whether a transaction is eligible for a refund based on company policy.
    Duplicate charges (duplicate_count > 1) are eligible, but amounts over $100 require human manager approval (High-Value Fraud Guardrail)."""
    data = mock_db.get_transaction(transaction_id)
    if "error" in data:
        return json.dumps({"eligible": False, "reason": data["error"]})

    amount = data.get("amount", 0.0)
    mock_db.log_audit_event("EVALUATE_POLICY", {"transaction_id": transaction_id, "amount": amount})

    if data.get("duplicate_count", 1) > 1:
        if amount > 100.0:
            return json.dumps({
                "eligible": False,
                "requires_manager_approval": True,
                "reason": f"High-value transaction (${amount} > $100 limit). Flagged for human manager review per Fraud Safety Guardrail.",
                "refund_amount": amount
            })
        return json.dumps({"eligible": True, "reason": "Duplicate charge detected.", "refund_amount": amount})

    return json.dumps({"eligible": False, "reason": "No valid refund reason found (not a duplicate charge)."})

@tool
def initiate_refund(transaction_id: str) -> str:
    """Initiate a refund for a given transaction ID. Must only be called after confirming eligibility via evaluate_refund_policy."""
    result = mock_db.update_transaction_status(transaction_id, "Refunded")
    mock_db.log_audit_event("INITIATE_REFUND", {"transaction_id": transaction_id, "result": result})
    return json.dumps(result)

@tool
def send_refund_receipt(transaction_id: str, customer_email: str) -> str:
    """Send an automated email receipt to the customer after a refund is processed."""
    audit_res = mock_db.log_audit_event("SEND_EMAIL_RECEIPT", {"transaction_id": transaction_id, "email": customer_email})
    return json.dumps({
        "status": "Email Sent",
        "recipient": customer_email,
        "message": f"Refund confirmation receipt for {transaction_id} sent successfully.",
        "audit": audit_res
    })


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

    # Setup Tools — fintech tools are always available; search is optional
    tools = [lookup_transaction, evaluate_refund_policy, initiate_refund, send_refund_receipt]
    if allow_search:
        tools.append(search_tool)

    # Create Agent
    agent = create_react_agent(
        model=llm,
        tools=tools
    )

    # Proper Message Format
    messages = [SystemMessage(content=system_prompt)]
    for msg in query:
        # Pydantic models from backend are passed as dicts via FastAPI
        role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", "")
        content = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", "")
        
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))

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