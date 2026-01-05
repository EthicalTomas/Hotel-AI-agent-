"""
AI Agent Module for Hotel Customer Service

This module handles AI-powered responses to customer inquiries
using OpenAI's GPT models with hotel-specific knowledge.
"""

import os
import json
import logging
from typing import Dict, List, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class HotelAIAgent:
    """AI Agent for handling hotel customer inquiries"""
    
    def __init__(self, hotel_info_file: str):
        """
        Initialize the AI agent with hotel information
        
        Args:
            hotel_info_file: Path to the JSON file containing hotel information
        """
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.hotel_info = self._load_hotel_info(hotel_info_file)
        self.system_prompt = self._create_system_prompt()
        
    def _load_hotel_info(self, file_path: str) -> Dict:
        """Load hotel information from JSON file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Hotel info file not found: {file_path}")
            raise
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in hotel info file: {file_path}")
            raise
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt with hotel information"""
        hotel_data = json.dumps(self.hotel_info, indent=2)
        
        prompt = f"""You are a professional and friendly AI assistant for {self.hotel_info.get('name', 'our hotel')}. 
Your role is to help customers with their inquiries about the hotel, including:
- Room availability and pricing
- Hotel facilities and amenities
- Booking procedures
- Hotel policies (cancellation, pets, etc.)
- Dining options
- Special services
- Nearby attractions
- General questions about the hotel

Here is the complete hotel information:

{hotel_data}

Guidelines for responses:
1. Be professional, friendly, and helpful at all times
2. Provide accurate information based only on the hotel data provided
3. If you don't have specific information, politely say so and offer to connect them with staff
4. Keep responses concise but informative
5. For booking requests, acknowledge the request and explain that a team member will process it
6. Always maintain a warm, welcoming tone that reflects excellent customer service
7. If asked about pricing, mention the base price and note that prices may vary by season and availability
8. For complex requests or complaints, acknowledge the issue and assure them that management will address it promptly

Remember: You represent the hotel's brand, so always maintain professionalism and courtesy."""
        
        return prompt
    
    def generate_response(self, customer_message: str, conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Generate an AI response to a customer message
        
        Args:
            customer_message: The customer's message/question
            conversation_history: Optional list of previous messages in format [{"role": "user/assistant", "content": "..."}]
            
        Returns:
            AI-generated response string
        """
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)
            
            # Add the current message
            messages.append({"role": "user", "content": customer_message})
            
            # Generate response using OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content.strip()
            logger.info(f"Generated AI response for message: {customer_message[:50]}...")
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return self._get_fallback_response()
    
    def _get_fallback_response(self) -> str:
        """Provide a fallback response when AI generation fails"""
        return (
            f"Thank you for contacting {self.hotel_info.get('name', 'us')}. "
            f"We're experiencing technical difficulties with our automated system. "
            f"Please contact us directly at {self.hotel_info.get('phone')} or "
            f"{self.hotel_info.get('email')} for immediate assistance. "
            f"We apologize for the inconvenience."
        )
    
    def get_hotel_info(self) -> Dict:
        """Return the hotel information dictionary"""
        return self.hotel_info
