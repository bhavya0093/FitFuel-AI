from google import genai
import os
from django.conf import settings

# Initialize the new Google GenAI Client
client = genai.Client(api_key=getattr(settings, 'GEMINI_API_KEY', None) or os.getenv("GEMINI_API_KEY") or "DUMMY_KEY")

class ModelWrapper:
    def generate_content(self, prompt):
        return client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

model = ModelWrapper()