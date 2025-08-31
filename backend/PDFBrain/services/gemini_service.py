import json
import logging
import os
from typing import List, Dict, Any, Optional

from google import genai
from google.genai import types
from pydantic import BaseModel

from config import settings

logger = logging.getLogger(__name__)

# Initialize Gemini client
client = genai.Client(api_key=settings.GEMINI_API_KEY)

class GeminiService:
    def __init__(self):
        self.client = client
        self.default_model = "gemini-2.5-flash"
        self.pro_model = "gemini-2.5-pro"
    
    async def generate_summary(self, text: str) -> str:
        """Generate a concise summary of the PDF content"""
        try:
            prompt = f"""
            Please provide a comprehensive summary of the following document. 
            Include the main topics, key points, and important conclusions.
            Keep it informative but concise (2-3 paragraphs maximum).
            
            Document content:
            {text}
            """
            
            response = self.client.models.generate_content(
                model=self.default_model,
                contents=prompt
            )
            
            return response.text or "Failed to generate summary"
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise Exception(f"Failed to generate summary: {str(e)}")
    
    async def answer_question(self, question: str, context: str, chat_history: Optional[List[Dict]] = None) -> str:
        """Answer a question based on the PDF content and chat history"""
        try:
            # Build context with chat history
            conversation_context = ""
            if chat_history:
                for msg in chat_history[-5:]:  # Last 5 messages for context
                    conversation_context += f"Human: {msg.get('user_message', '')}\n"
                    conversation_context += f"Assistant: {msg.get('ai_response', '')}\n"
            
            prompt = f"""
            You are a helpful AI assistant that answers questions based on the provided document content.
            Use the document content as your primary source of information.
            If the question cannot be answered from the document, clearly state that.
            Be accurate, helpful, and conversational.
            
            Document content:
            {context}
            
            Previous conversation:
            {conversation_context}
            
            Current question: {question}
            
            Please provide a helpful and accurate answer:
            """
            
            response = self.client.models.generate_content(
                model=self.default_model,
                contents=prompt
            )
            
            return response.text or "I'm sorry, I couldn't generate a response to your question."
            
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            raise Exception(f"Failed to answer question: {str(e)}")
    
    async def manipulate_content(self, text: str, operation: str, custom_prompt: Optional[str] = None) -> str:
        """Manipulate content based on the specified operation"""
        try:
            if custom_prompt:
                prompt = f"{custom_prompt}\n\nContent:\n{text}"
            else:
                operation_prompts = {
                    "summarize": f"Provide a detailed summary of the following content:\n\n{text}",
                    "explain": f"Explain the following content in simple, easy-to-understand terms:\n\n{text}",
                    "restructure": f"Restructure and reorganize the following content for better clarity and flow:\n\n{text}",
                    "outline": f"Create a detailed outline of the following content:\n\n{text}",
                    "bullet_points": f"Convert the following content into well-organized bullet points:\n\n{text}"
                }
                
                prompt = operation_prompts.get(operation, f"Process the following content according to '{operation}':\n\n{text}")
            
            response = self.client.models.generate_content(
                model=self.default_model,
                contents=prompt
            )
            
            return response.text or f"Failed to {operation} the content"
            
        except Exception as e:
            logger.error(f"Error in content manipulation: {str(e)}")
            raise Exception(f"Failed to {operation} content: {str(e)}")
    
    async def generate_quiz_questions(self, text: str, num_questions: int, question_types: List[str], difficulty: str = "medium") -> List[Dict[str, Any]]:
        """Generate quiz questions from the PDF content"""
        try:
            # Prepare question types string
            types_str = ", ".join(question_types)
            
            prompt = f"""
            Based on the following document content, generate {num_questions} quiz questions.
            
            Requirements:
            - Question types: {types_str}
            - Difficulty level: {difficulty}
            - Questions should test understanding of key concepts
            - Provide clear, unambiguous questions
            - Include explanations for correct answers
            
            For MCQ questions: Provide 4 options (A, B, C, D)
            For True/False: Provide true or false questions
            For Fill-in-the-blank: Provide questions with one clear blank to fill
            
            Return the response as a JSON array with this structure:
            [
                {{
                    "question_type": "mcq|true_false|fill_blank",
                    "question_text": "The question text",
                    "correct_answer": "The correct answer",
                    "options": ["A", "B", "C", "D"] (only for MCQ),
                    "explanation": "Explanation of why this is correct"
                }}
            ]
            
            Document content:
            {text}
            """
            
            response = self.client.models.generate_content(
                model=self.pro_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            if response.text:
                try:
                    questions = json.loads(response.text)
                    return questions if isinstance(questions, list) else []
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing JSON response: {str(e)}")
                    return []
            
            return []
            
        except Exception as e:
            logger.error(f"Error generating quiz questions: {str(e)}")
            raise Exception(f"Failed to generate quiz questions: {str(e)}")

# Global instance
gemini_service = GeminiService()
