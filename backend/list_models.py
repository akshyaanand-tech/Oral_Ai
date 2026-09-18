import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

from google import genai

api_key = os.getenv("GEMINI_API_KEY", "")
client = genai.Client(api_key=api_key)

print("Available Gemini models:")
for m in client.models.list():
    if "gemini" in m.name.lower():
        print(" ", m.name)
