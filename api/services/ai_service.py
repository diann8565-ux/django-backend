
import os
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class AIService:
    API_URL = os.environ.get("AI_API_URL", "https://one.apprentice.cyou/api/v1/chat/completions")
    API_KEY = os.environ.get("AI_API_KEY", "")
    MODEL = os.environ.get("AI_MODEL", "gemini-2.5-flash")

    @classmethod
    def generate_response(cls, messages, stream=False):
        """
        Generates a response from the AI model.
        """
        try:
            payload = {
                "model": cls.MODEL,
                "messages": messages,
                "stream": stream
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            if cls.API_KEY:
                headers["Authorization"] = f"Bearer {cls.API_KEY}"
            
            response = requests.post(cls.API_URL, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            return response.json()
        except requests.RequestException as e:
            logger.error(f"AI Service Error: {str(e)}")
            raise e

    @classmethod
    def analyze_file(cls, file_content_summary):
        """
        Analyzes file content (stub).
        """
        messages = [
            {"role": "system", "content": "You are a helpful assistant that analyzes files."},
            {"role": "user", "content": f"Analyze this file content summary: {file_content_summary}"}
        ]
        return cls.generate_response(messages)
