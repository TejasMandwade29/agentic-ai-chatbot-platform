# Agentic AI Chatbot Platform

An AI-powered full-stack chatbot application built using FastAPI, Streamlit, LangGraph, and LangChain with support for multiple LLM providers including Groq and OpenAI. The application enables real-time conversational AI interactions with optional web search capabilities using Tavily Search API.

---

# Features

- Multi-LLM support (Groq & OpenAI)
- Real-time AI chatbot interaction
- ReAct-based AI agent workflow
- Dynamic model selection
- REST API integration using FastAPI
- Web search integration using Tavily Search API
- Streamlit-based frontend interface
- Environment variable management using `.env`
- Modular backend/frontend architecture

---

# Tech Stack

## Backend
- FastAPI
- Uvicorn

## Frontend
- Streamlit

## AI Frameworks
- LangChain
- LangGraph

## AI Providers
- Groq API
- OpenAI API

## Tools & APIs
- Tavily Search API
- REST APIs

## Language
- Python

---

# Project Architecture

```text
Frontend (Streamlit)
        ↓
REST API (FastAPI)
        ↓
AI Agent Layer (LangGraph + LangChain)
        ↓
Groq/OpenAI Models + Tavily Search
```

---

# Project Screenshots

## Chatbot Interface
(Add Screenshot Here)

## FastAPI Swagger Docs
(Add Screenshot Here)

## AI Response Example
(Add Screenshot Here)

---

# Installation & Setup

## 1. Clone Repository

```bash
git clone https://github.com/TejasMandwade29/agentic-ai-chatbot-platform.git
```

## 2. Navigate to Project

```bash
cd agentic-ai-chatbot-platform
```

## 3. Create Virtual Environment

```bash
pipenv shell
```

OR

```bash
python -m venv venv
```

---

# Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Configure Environment Variables

Create `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
```

---

# Run Backend Server

```bash
python backend.py
```

OR

```bash
uvicorn backend:app --reload --port 9999
```

---

# Run Frontend

Open another terminal:

```bash
streamlit run frontend.py
```

---

# API Endpoint

## Chat Endpoint

```http
POST /chat
```

Example Request:

```json
{
  "model_name": "llama-3.3-70b-versatile",
  "model_provider": "Groq",
  "system_prompt": "Act as a helpful AI Assistant",
  "messages": [
    "What is Artificial Intelligence?"
  ],
  "allow_search": true
}
```

---

# Resume Highlights

- Developed a full-stack Agentic AI chatbot system using FastAPI, Streamlit, LangGraph, and LangChain.
- Integrated REST APIs, multi-model LLM support, and AI agent workflows.
- Implemented web search functionality using Tavily Search API.
- Debugged backend/frontend integration, API communication, and LangGraph compatibility issues.

---

# Future Improvements

- Add conversation memory
- Add PDF/RAG support
- Add authentication system
- Deploy application to cloud
- Improve frontend UI/UX
- Add database integration

---

# Author

Tejas Mandwade

GitHub:
https://github.com/TejasMandwade29
