from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import google.generativeai as genai
import os
from datetime import datetime
from dotenv import load_dotenv

router = APIRouter()
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- MODEL NAME CHANGE IS HERE ---
GEMINI_MODEL_NAME = "gemini-2.5-flash"
# ---

# System prompt for the AI Tutor
TUTOR_SYSTEM_PROMPT = """You are an Adaptive AI Tutor designed to help students master any concept through personalized dialogue. Unlike regular chatbots, your goal is not to answer questions directly — your goal is to *teach effectively*.

### BEHAVIOR RULES

1. **Context Awareness**
 - Always remember the student's current topic, progress, and past mistakes within this session.
 - Use that context to decide your next question or explanation.
 - Never reset tone or forget what was discussed.

2. **Adaptive Difficulty**
 - If the student answers correctly twice in a row, increase question difficulty slightly.
 - If the student struggles or says "I don't get it," switch to simpler, step-by-step explanations.
 - Adjust examples to match the student's prior performance.

3. **Engaged Teaching**
 - Don't just explain. Occasionally quiz the student with small checkpoints (1-2 questions).
 - If they get it right, briefly praise and move on. If not, explain where they went wrong.
 - Mix direct teaching and Socratic questioning ("Why do you think that happens?").

4. **Reasoning Transparency**
 - When showing a solution, explain *how* you reached it and *why* each step matters.
 - Avoid dumping full answers unless the student requests it.

5. **Tone Modes**
 - Default tone: motivating and confident, like a personal coach who cares about results.
 - If the user says "go easy" or "be strict," adapt tone accordingly.
 - Avoid empty compliments; focus on growth-based feedback.

6. **Retention Reinforcement**
 - After every 5–10 interactions, summarize key takeaways naturally: ("So far, you've learned how to calculate acceleration using Newton's 2nd law.")
 - Occasionally suggest short revision challenges.

7. **Empathy + Focus**
 - Detect signs of confusion or frustration ("hmm", "I don't get it", long pauses).
 - Offer optional help paths: ("Would you like a simpler example or a visual breakdown?")
 - Stay encouraging but never patronizing.

8. **End-of-Topic Flow**
 - When a student masters a concept, offer transitions: ("You've nailed this. Want to move to related topics or a short quiz to reinforce it?")

### OUTPUT STYLE
- Keep messages concise.
- Use examples, analogies, and simple math or visuals when helpful.
- Prefer clarity over jargon.
- Occasionally use markdown for neat formatting (tables, bullets, formulas).
- Never break immersion by mentioning you are an AI model.

Your mission: make every message count for learning, not just chatting."""


class Message(BaseModel):
  role: str
  content: str
  timestamp: datetime


class SessionContext(BaseModel):
  topic: Optional[str] = None
  difficulty: str = "medium"
  correctStreak: int = 0
  strugglingCount: int = 0


class ChatRequest(BaseModel):
  message: str
  conversationHistory: List[Message]
  sessionContext: SessionContext


class ChatResponse(BaseModel):
  response: str
  updatedContext: SessionContext


def analyze_student_response(message: str, context: SessionContext) -> SessionContext:
  """Analyze student's message to update session context"""
  new_context = context.model_copy()
 
  # Detect confusion indicators
  confusion_indicators = [
    "i don't get it", "confused", "don't understand",
    "what", "huh", "hmm", "help", "lost", "unclear"
  ]
 
  if any(indicator in message.lower() for indicator in confusion_indicators):
    new_context.strugglingCount += 1
    new_context.correctStreak = 0
   
    # Lower difficulty if student is struggling
    if new_context.strugglingCount >= 2:
      if new_context.difficulty == "hard":
        new_context.difficulty = "medium"
      elif new_context.difficulty == "medium":
        new_context.difficulty = "easy"
 
  # Detect understanding indicators
  understanding_indicators = [
    "i see", "got it", "understand", "makes sense",
    "okay", "thanks", "clear now", "i think"
  ]
 
  if any(indicator in message.lower() for indicator in understanding_indicators):
    new_context.correctStreak += 1
    new_context.strugglingCount = 0
   
    # Increase difficulty if student is doing well
    if new_context.correctStreak >= 2:
      if new_context.difficulty == "easy":
        new_context.difficulty = "medium"
      elif new_context.difficulty == "medium":
        new_context.difficulty = "hard"
      new_context.correctStreak = 0 # Reset after difficulty increase
 
  # Detect topic from first meaningful message
  if not new_context.topic and len(message.split()) > 3:
    # Simple topic extraction - in production, use NLP
    keywords = message.lower().split()
    if any(word in keywords for word in ["physics", "math", "chemistry", "biology", "history"]):
      for word in keywords:
        if word in ["physics", "math", "chemistry", "biology", "history"]:
          new_context.topic = word.capitalize()
          break
 
  return new_context


def build_context_string(context: SessionContext, history: List[Message]) -> str:
  """Build a context string for the AI"""
  context_parts = []
 
  if context.topic:
    context_parts.append(f"Current topic: {context.topic}")
 
  context_parts.append(f"Difficulty level: {context.difficulty}")
  context_parts.append(f"Correct streak: {context.correctStreak}")
  context_parts.append(f"Struggling count: {context.strugglingCount}")
 
  # Add hints based on context
  if context.strugglingCount >= 2:
    context_parts.append("⚠️ Student is struggling - use simpler explanations and more examples")
  elif context.correctStreak >= 2:
    context_parts.append("✅ Student is doing well - consider increasing challenge level")
 
  # Add recent interaction count
  context_parts.append(f"Conversation length: {len(history)} messages")
  if len(history) >= 10 and len(history) % 5 == 0:
    context_parts.append("💡 Consider summarizing key takeaways soon")
 
  return "\n".join(context_parts)


@router.post("/chat", response_model=ChatResponse)
async def chat_with_tutor(request: ChatRequest):
  """
  Main endpoint for AI tutor chat interaction
  """
  try:
    # Update session context based on student's message
    updated_context = analyze_student_response(request.message, request.sessionContext)
   
    # Build conversation history for Gemini
    conversation_history = []
   
    # Add recent messages (last 10 to keep context manageable)
    recent_history = request.conversationHistory[-10:] if len(request.conversationHistory) > 10 else request.conversationHistory
   
    for msg in recent_history:
      conversation_history.append({
        "role": "user" if msg.role == "user" else "model",
        "parts": [{"text": msg.content}] # Changed "parts": [msg.content] to "parts": [{"text": msg.content}] for consistency with the new SDK version's chat history structure
      })
   
    # Build context information
    context_info = build_context_string(updated_context, request.conversationHistory)
   
    # Create the model
    model = genai.GenerativeModel(
      model_name=GEMINI_MODEL_NAME, # Using the new variable
      system_instruction=TUTOR_SYSTEM_PROMPT
    )
   
    # Start chat with history
    chat = model.start_chat(history=conversation_history[:-1]) # Exclude current message
   
    # Add context as a prefix to the user's message
    enhanced_message = f"[Session Context: {context_info}]\n\nStudent: {request.message}"
   
    # Generate response
    response = chat.send_message(enhanced_message)
   
    return ChatResponse(
      response=response.text,
      updatedContext=updated_context
    )
   
  except Exception as e:
    print(f"Error in chat_with_tutor: {str(e)}")
    raise HTTPException(
      status_code=500,
      detail=f"Failed to generate response: {str(e)}"
    )


@router.post("/reset-session")
async def reset_session():
  """Reset the tutoring session"""
  return {
    "message": "Session reset successfully",
    "sessionContext": SessionContext().model_dump() # Changed .dict() to .model_dump() for Pydantic v2
  }


@router.get("/health")
async def health_check():
  """Health check endpoint"""
  try:
    # Test if Gemini API is configured
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
      return {
        "status": "warning",
        "message": "GEMINI_API_KEY not configured"
      }
   
    return {
      "status": "healthy",
      "message": "AI Tutor service is running",
      "model": GEMINI_MODEL_NAME # Using the new variable
    }
  except Exception as e:
    return {
      "status": "error",
      "message": str(e)
    }