import streamlit as st
import requests
import os
import uuid

st.set_page_config(page_title="LangGraph Agent UI", layout="centered")
st.title("AI Chatbot Agents")
st.write("Create and Interact with the AI Agents!")

from config import PERSONAS, MODEL_NAMES_GROQ, MODEL_NAMES_OPENAI

# --- 1. INITIALIZE CHAT SESSIONS ---
if "chats" not in st.session_state:
    initial_id = str(uuid.uuid4())
    st.session_state.chats = {
        initial_id: {"title": "New Chat", "messages": []}
    }
    st.session_state.active_chat = initial_id

# --- 2. SIDEBAR: CHAT NAVIGATION ---
if st.sidebar.button("+ New Chat", use_container_width=True):
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
if st.sidebar.button("Delete Chat"):
    del st.session_state.chats[st.session_state.active_chat]
    # Prevent empty state by creating a new chat if all are deleted
    if len(st.session_state.chats) == 0:
        new_id = str(uuid.uuid4())
        st.session_state.chats = {new_id: {"title": "New Chat", "messages": []}}
        st.session_state.active_chat = new_id
    else:
        st.session_state.active_chat = list(st.session_state.chats.keys())[0]
    st.rerun()

st.sidebar.divider()

# Refresh Warning
st.sidebar.warning("Chats will be lost if page refreshes.")

st.sidebar.divider()

# --- 3. SIDEBAR: AGENT CONFIGURATION ---
st.sidebar.header("Agent Configuration")

selected_persona = st.sidebar.selectbox("Select AI Persona:", list(PERSONAS.keys()))
system_prompt = PERSONAS[selected_persona]

provider = st.sidebar.radio("Select Provider:", ("Groq", "OpenAI"))

if provider == "Groq":
    selected_model = st.sidebar.selectbox("Select Groq Model:", MODEL_NAMES_GROQ)
elif provider == "OpenAI":
    selected_model = st.sidebar.selectbox("Select OpenAI Model:", MODEL_NAMES_OPENAI)

allow_web_search = st.sidebar.checkbox("Allow Web Search")

st.sidebar.divider()

# --- 4. SIDEBAR: UTILITIES ---
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
        label="Download Chat",
        data=chat_text,
        file_name=f"{st.session_state.chats[st.session_state.active_chat]['title']}_export.txt",
        mime="text/plain"
    )
else:
    st.sidebar.write("No conversation available to export.")

if st.sidebar.button("Clear Chat"):
    st.session_state.chats[st.session_state.active_chat]["messages"] = []
    st.rerun()


# --- 5. MAIN UI: CHAT WINDOW ---
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

text_prompt = st.chat_input("Ask Anything!")
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

    with st.status("🧠 Agent Workflow Initiated", expanded=True) as status:
        st.write("✅ Request Received")
        if allow_web_search:
            st.write("🔍 Preparing Tavily Search")
        st.write("⚙️ Executing LangGraph Agent")
        st.write("📝 Generating Response")
        
        try:
            response = requests.post(BACKEND_URL, json=payload)
            if response.status_code == 200:
                response_data = response.json()
                if "error" in response_data:
                    status.update(label="❌ Agent Execution Failed", state="error", expanded=False)
                    st.error(response_data["error"])
                else:
                    status.update(label="✅ Response Generated Successfully", state="complete", expanded=False)
                    with st.chat_message("assistant"):
                        st.markdown(response_data)
                    st.session_state.chats[st.session_state.active_chat]["messages"].append({"role": "assistant", "content": response_data})
                    st.rerun() # Refresh to update the Auto-Title in the sidebar immediately
            else:
                status.update(label="❌ Agent Execution Failed", state="error", expanded=False)
                st.error(f"Backend error: Received status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            status.update(label="❌ Agent Execution Failed", state="error", expanded=False)
            st.error("Unable to connect to backend service. Please try again later.")