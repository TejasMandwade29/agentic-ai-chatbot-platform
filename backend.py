import os
from pydantic import BaseModel
from typing import List, Dict, Any
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from ai_agent import get_response_from_ai_agent
from config import ALLOWED_MODEL_NAMES
import groq
class Message(BaseModel):
    role: str
    content: str

class RequestState(BaseModel):
    model_name: str
    model_provider: str
    system_prompt: str
    messages: List[Message]
    allow_search: bool

app=FastAPI(title="LangGraph AI Agent")

# Add CORS Middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    API Endpoint to transcribe audio using Groq's Whisper model.
    """
    try:
        # Initialize Groq client
        client = groq.Groq(api_key=os.environ.get("GROQ_API_KEY"))
        
        # Read the file bytes
        audio_bytes = await file.read()
        
        # Groq requires a tuple of (filename, bytes) for the file upload
        file_tuple = (file.filename, audio_bytes)
        
        
        transcription = client.audio.transcriptions.create(
            file=file_tuple,
            model="whisper-large-v3",
            response_format="text"
        )
        
        return {"text": transcription}
    except Exception as e:
        return {"error": str(e)}

@app.post("/chat")
def chat_endpoint(request: RequestState): 
    """
    API Endpoint to interact with the Chatbot using LangGraph and search tools.
    It dynamically selects the model specified in the request
    """
    if request.model_name not in ALLOWED_MODEL_NAMES:
        return {"error": "Invalid model name. Kindly select a valid AI model"}
    
    llm_id = request.model_name
    query = request.messages
    allow_search = request.allow_search
    system_prompt = request.system_prompt
    provider = request.model_provider

    # Create AI Agent and get response from it! 
    response=get_response_from_ai_agent(llm_id, query, allow_search, system_prompt, provider)
    return response

if __name__ == "__main__":
    import uvicorn
    # Use dynamic port for deployment
    port = int(os.getenv("PORT", 9999))
    uvicorn.run(app, host="0.0.0.0", port=port)