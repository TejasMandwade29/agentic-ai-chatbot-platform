import streamlit as st
import requests
import os
import uuid

st.set_page_config(
    page_title="Agentic Fintech Ops Platform",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ── Global CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* Hide Streamlit chrome */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDeployButton { display: none; }

/* Main background */
.stApp {
    background: #0a0a0f;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f0f18 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] span {
    color: #b0b0c3 !important;
    font-size: 0.875rem !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #e2e2f0 !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    font-weight: 600 !important;
}

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #c0c0d8 !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    padding: 0.4rem 0.8rem !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(102, 126, 234, 0.15) !important;
    border-color: rgba(102, 126, 234, 0.4) !important;
    color: #a78bfa !important;
}

/* New Chat button — accent */
[data-testid="stSidebar"] .stButton:first-of-type > button {
    background: linear-gradient(135deg, rgba(102,126,234,0.2), rgba(167,139,250,0.15)) !important;
    border: 1px solid rgba(102, 126, 234, 0.35) !important;
    color: #a78bfa !important;
    font-weight: 600 !important;
}

/* Dividers */
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.06) !important;
    margin: 0.5rem 0 !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    margin-bottom: 0.5rem !important;
}

/* Chat input bar */
[data-testid="stChatInput"] {
    background: #13131f !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(102, 126, 234, 0.5) !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
}

/* Audio input */
[data-testid="stAudioInput"] > div {
    background: #13131f !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
}

/* Status / reasoning box */
[data-testid="stStatus"] {
    background: rgba(102, 126, 234, 0.06) !important;
    border: 1px solid rgba(102, 126, 234, 0.2) !important;
    border-radius: 12px !important;
}

/* Warning box */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-size: 0.82rem !important;
}

/* Selectbox / radio */
[data-testid="stSelectbox"] > div,
.stRadio > div {
    background: transparent !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12); border-radius: 4px; }

/* Test data badge styling */
.txn-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

# ── Branded Header ───────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 1.5rem 0 1rem 0; border-bottom: 1px solid rgba(255,255,255,0.06); margin-bottom: 1.5rem;">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 0.4rem;">
        <div style="width: 36px; height: 36px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px;">⚡</div>
        <h1 style="margin: 0; font-size: 1.6rem; font-weight: 700; color: #f0f0ff; letter-spacing: -0.02em;">
            Agentic Fintech Ops
        </h1>
    </div>
    <p style="margin: 0; color: #6b6b8a; font-size: 0.9rem; padding-left: 48px;">
        Resolve transaction disputes and process refunds autonomously · Powered by LangGraph ReAct
    </p>
</div>
""", unsafe_allow_html=True)

from config import PERSONAS, MODEL_NAMES_GROQ, MODEL_NAMES_OPENAI

# --- 1. INITIALIZE CHAT SESSIONS ---
if "chats" not in st.session_state:
    initial_id = str(uuid.uuid4())
    st.session_state.chats = {
        initial_id: {"title": "New Chat", "messages": []}
    }
    st.session_state.active_chat = initial_id

# --- 2. SIDEBAR: CHAT NAVIGATION ---
st.sidebar.markdown("""
<div style="padding: 0.5rem 0 0.75rem 0;">
    <span style="font-size: 1.1rem; font-weight: 700; color: #e2e2f0; letter-spacing: -0.01em;">💬 Chats</span>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("＋  New Chat", use_container_width=True):
    new_id = str(uuid.uuid4())
    st.session_state.chats[new_id] = {"title": "New Chat", "messages": []}
    st.session_state.active_chat = new_id
    st.rerun()

st.sidebar.divider()

# Chat Selection List
chat_ids = list(st.session_state.chats.keys())
selected_chat_id = st.sidebar.radio(
    "Your Chats",
    options=chat_ids,
    format_func=lambda chat_id: st.session_state.chats[chat_id]["title"],
    index=chat_ids.index(st.session_state.active_chat)
)

# Switch chat if radio selection changes
if selected_chat_id != st.session_state.active_chat:
    st.session_state.active_chat = selected_chat_id
    st.rerun()

st.sidebar.divider()

# Rename Chat
new_title = st.sidebar.text_input("Rename Chat", value=st.session_state.chats[st.session_state.active_chat]["title"])
if st.sidebar.button("Rename"):
    st.session_state.chats[st.session_state.active_chat]["title"] = new_title
    st.rerun()

# Delete Chat
if st.sidebar.button("🗑  Delete Chat"):
    del st.session_state.chats[st.session_state.active_chat]
    if len(st.session_state.chats) == 0:
        new_id = str(uuid.uuid4())
        st.session_state.chats = {new_id: {"title": "New Chat", "messages": []}}
        st.session_state.active_chat = new_id
    else:
        st.session_state.active_chat = list(st.session_state.chats.keys())[0]
    st.rerun()

st.sidebar.divider()

st.sidebar.warning("⚠️ Chats are lost on page refresh.")

st.sidebar.divider()

# --- 3. SIDEBAR: AGENT CONFIGURATION ---
st.sidebar.markdown("### ⚙️ Agent Config")

selected_persona = st.sidebar.selectbox("AI Persona", list(PERSONAS.keys()))
system_prompt = PERSONAS[selected_persona]

provider = st.sidebar.radio("Provider", ("Groq", "OpenAI"))

if provider == "Groq":
    selected_model = st.sidebar.selectbox("Model", MODEL_NAMES_GROQ)
elif provider == "OpenAI":
    selected_model = st.sidebar.selectbox("Model", MODEL_NAMES_OPENAI)

allow_web_search = st.sidebar.checkbox("🌐  Allow Web Search")

st.sidebar.divider()

# --- 4. SIDEBAR: TEST DATA ---
st.sidebar.markdown("### 🧪 Mock DB — Test IDs")
st.sidebar.markdown("""
<div style="font-size: 0.82rem; line-height: 1.9; color: #9090b0;">
  <div>🟢 <b style="color:#e2e2f0;">TXN-1001</b> &nbsp;Normal &nbsp;<span style="color:#6b6b8a;">$49.99</span></div>
  <div>🔴 <b style="color:#e2e2f0;">TXN-1002</b> &nbsp;Duplicate &nbsp;<span style="color:#6b6b8a;">$99.00</span> ✓ Auto-Refund</div>
  <div>⚫ <b style="color:#e2e2f0;">TXN-1003</b> &nbsp;Failed &nbsp;<span style="color:#6b6b8a;">$15.00</span></div>
  <div>⚠️ <b style="color:#e2e2f0;">TXN-1004</b> &nbsp;High-Value &nbsp;<span style="color:#6b6b8a;">$250.00</span> 🛡️ Manager Escalate</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### 📚 RAG Vector Search")
st.sidebar.markdown("""
<div style="font-size: 0.8rem; color: #9090b0; line-height: 1.5;">
  <i>Try asking:</i><br/>
  • 💬 "What is the policy for international card disputes?"<br/>
  • 💬 "What is the SLA processing time for refunds?"
</div>
""", unsafe_allow_html=True)

st.sidebar.divider()

# --- 5. SIDEBAR: UTILITIES ---
active_messages = st.session_state.chats[st.session_state.active_chat]["messages"]

def format_chat_history():
    formatted_text = ""
    for msg in active_messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        formatted_text += f"{role}: {msg['content']}\n\n"
    return formatted_text

if active_messages:
    chat_text = format_chat_history()
    st.sidebar.download_button(
        label="⬇️  Export Chat",
        data=chat_text,
        file_name=f"{st.session_state.chats[st.session_state.active_chat]['title']}_export.txt",
        mime="text/plain"
    )
else:
    st.sidebar.caption("No conversation to export yet.")

if st.sidebar.button("🧹  Clear Chat"):
    st.session_state.chats[st.session_state.active_chat]["messages"] = []
    st.rerun()


# --- 6. MAIN UI: CHAT WINDOW ---
# Empty state prompt
if not active_messages:
    st.markdown("""
    <div style="text-align: center; padding: 3rem 1rem; color: #3a3a55;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">⚡</div>
        <p style="font-size: 1rem; color: #5a5a7a; margin-bottom: 0.4rem;">Ask me about a transaction dispute or refund.</p>
        <p style="font-size: 0.82rem; color: #3a3a55;">Try: <em>"I was charged twice. Check TXN-1002."</em></p>
    </div>
    """, unsafe_allow_html=True)

# Display active chat messages
for message in active_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Backend URL configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:9999/chat")
TRANSCRIBE_URL = os.getenv("TRANSCRIBE_URL", "http://127.0.0.1:9999/transcribe")

# Initialize a dynamic key for the audio input widget to force reset it
if "audio_key" not in st.session_state:
    st.session_state.audio_key = str(uuid.uuid4())

# Voice Input Handling
audio_value = st.audio_input("Speak your message", key=st.session_state.audio_key)
voice_prompt = None
if audio_value:
    with st.spinner("Transcribing audio..."):
        try:
            files = {"file": ("audio.wav", audio_value.getvalue(), "audio/wav")}
            transcription_response = requests.post(TRANSCRIBE_URL, files=files)
            if transcription_response.status_code == 200:
                transcription_data = transcription_response.json()
                if "error" in transcription_data:
                    st.error(f"Transcription error: {transcription_data['error']}")
                else:
                    voice_prompt = transcription_data.get("text")
            else:
                st.error("Failed to transcribe audio.")
        except Exception as e:
            st.error(f"Audio processing error: {e}")

text_prompt = st.chat_input("Ask about a transaction or dispute...")
# Text input takes precedence if both are somehow present
prompt = text_prompt if text_prompt else voice_prompt

if prompt:
    # Clear the audio widget completely for the next interaction to prevent infinite loops
    st.session_state.audio_key = str(uuid.uuid4())
         
    # Auto Chat Title Logic (Triggered on first message)
    if len(active_messages) == 0:
        words = prompt.split()
        auto_title = " ".join(words[:4])
        if len(words) > 4:
            auto_title += "..."
        st.session_state.chats[st.session_state.active_chat]["title"] = auto_title

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Append to active chat
    st.session_state.chats[st.session_state.active_chat]["messages"].append({"role": "user", "content": prompt})
    
    payload = {
        "model_name": selected_model,
        "model_provider": provider,
        "system_prompt": system_prompt,
        "messages": st.session_state.chats[st.session_state.active_chat]["messages"],
        "allow_search": allow_web_search
    }

    with st.status("🧠 Agent Workflow Running...", expanded=True) as status:
        st.write("✅ Request received by FastAPI")
        st.write("🔍 Running `lookup_transaction`...")
        st.write("⚖️ Evaluating refund policy...")
        st.write("💳 Executing tool calls via LangGraph ReAct...")
        
        try:
            response = requests.post(BACKEND_URL, json=payload)
            if response.status_code == 200:
                response_data = response.json()
                if "error" in response_data:
                    status.update(label="❌ Agent Execution Failed", state="error", expanded=False)
                    st.error(response_data["error"])
                else:
                    status.update(label="✅ Agent completed · Response ready", state="complete", expanded=False)
                    with st.chat_message("assistant"):
                        st.markdown(response_data)
                    st.session_state.chats[st.session_state.active_chat]["messages"].append({"role": "assistant", "content": response_data})
                    st.rerun()
            else:
                status.update(label="❌ Agent Execution Failed", state="error", expanded=False)
                st.error(f"Backend error: Received status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            status.update(label="❌ Agent Execution Failed", state="error", expanded=False)
            st.error("Unable to connect to backend service. Please try again later.")