# backend/new_agent/real_llm_service.py
"""
Real LLM Service for Dynamic Course Creation
============================================

This service provides actual LLM-powered content generation using Google Gemini API.
"""

import asyncio
import json
import re
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("Warning: google-generativeai not installed. Install with: pip install google-generativeai")

from .llm_service import BaseLLMService


class RealLLMService(BaseLLMService):
    """Real LLM service that uses Google Gemini API for content generation"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        super().__init__(api_key, model_name)
        self.model_name = model_name
        self.model = None
        
        if not GENAI_AVAILABLE:
            raise RuntimeError("google-generativeai package is required. Install with: pip install google-generativeai")
        
        if not api_key or api_key == "demo-key":
            raise ValueError("Valid Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        # Configure Gemini API
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using actual Google Gemini API"""
        try:
            # Prepare generation config (e.g., response_mime_type)
            generation_config = kwargs.get("generation_config", {})
            if "response_mime_type" in kwargs:
                generation_config["response_mime_type"] = kwargs["response_mime_type"]

            # Make actual API call
            if generation_config:
                response = await asyncio.to_thread(
                    self.model.generate_content,
                    prompt,
                    generation_config=generation_config,
                )
            else:
                response = await asyncio.to_thread(self.model.generate_content, prompt)
            
            # Extract text from response
            if hasattr(response, 'text'):
                content = response.text
            else:
                content = str(response)
            
            # Update metrics
            self.request_count += 1
            self.total_tokens += len(prompt.split()) + len(content.split())
            
            return content
            
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            # Fallback to basic response
            return self._generate_fallback_content(prompt)
    
    async def generate_structured_response(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured response from Gemini API"""
        try:
            # Add JSON formatting instruction
            structured_prompt = f"""
{prompt}

IMPORTANT: Return ONLY valid JSON matching this exact schema:
{json.dumps(schema, indent=2)}

Do not include any markdown formatting, code blocks, or explanatory text.
Return raw JSON only.
"""
            
            response_text = await self.generate_response(structured_prompt)
            
            # Clean response - remove markdown code blocks if present
            cleaned = response_text.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.startswith('```'):
                cleaned = cleaned[3:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            # Parse JSON
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON response: {e}")
                print(f"Response was: {cleaned[:200]}...")
                # Try to extract JSON from text
                json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                # Fallback
                return self._generate_mock_structured_response(schema)
                
        except Exception as e:
            print(f"Error generating structured response: {e}")
            return self._generate_mock_structured_response(schema)
    
    def _generate_mock_structured_response(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback structured response"""
        response = {}
        for key, value_type in schema.items():
            if value_type == "string":
                response[key] = f"Generated {key}"
            elif value_type == "number":
                response[key] = 0.8
            elif value_type == "boolean":
                response[key] = True
            elif value_type == "array":
                response[key] = [f"Item {i}" for i in range(3)]
            else:
                response[key] = f"Generated {key}"
        return response
    
    def _generate_fallback_content(self, prompt: str) -> str:
        """Generate fallback content when API fails"""
        return """
# Course Content

## Introduction
This lesson provides comprehensive coverage of the requested topic.

## Key Concepts
1. Fundamental principles and core concepts
2. Practical applications and real-world examples
3. Best practices and industry standards
4. Common patterns and solutions

## Learning Objectives
- Understand the fundamental concepts
- Apply knowledge in practical scenarios
- Implement solutions effectively
- Troubleshoot common issues

## Detailed Content
The material covers essential topics with hands-on examples and practical exercises.
Each concept is explained clearly with step-by-step instructions and code examples.

## Practice Exercises
1. Complete the basic exercises to reinforce learning
2. Work through intermediate challenges
3. Tackle advanced problems for mastery

## Next Steps
- Review the key concepts covered
- Complete all practice exercises
- Apply the knowledge to your own projects
- Continue learning with advanced topics

Note: This is fallback content. For best results, ensure your API key is valid.
"""