"""
Standalone Gemini API key tester for OralAI backend.

Run this BEFORE starting the backend to confirm your API key and model work:
    python test_gemini.py

Steps:
  1. Paste your new key in .env (GEMINI_API_KEY=AQ.your_new_key...)
  2. Run: python test_gemini.py
  3. If both tests pass, restart the backend: uvicorn app.main:app --reload
"""

import os
import io
from dotenv import load_dotenv

# Load from .env so you only need to update one place
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL   = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")


def test_text():
    """Test 1: Basic text generation."""
    print(f"\n{'='*55}")
    print(f"TEST 1 - Text generation ({MODEL})")
    print(f"{'='*55}")
    try:
        from google import genai
        from google.genai import types as genai_types

        client = genai.Client(api_key=API_KEY)
        response = client.models.generate_content(
            model=MODEL,
            contents="Hello! Reply with exactly: API is working!",
            config=genai_types.GenerateContentConfig(temperature=0.0),
        )
        text = response.text.strip()
        print(f"[PASS]  Response: {text}")
        return True
    except Exception as e:
        print(f"[FAIL]  {e}")
        return False


def test_vision():
    """Test 2: Image vision (mirrors the actual dental analysis pipeline)."""
    print(f"\n{'='*55}")
    print(f"TEST 2 - Vision / image analysis ({MODEL})")
    print(f"{'='*55}")
    try:
        from google import genai
        from google.genai import types as genai_types
        from PIL import Image

        # Minimal test image
        buf = io.BytesIO()
        Image.new("RGB", (100, 100), color=(255, 255, 255)).save(buf, format="JPEG")
        img_bytes = buf.getvalue()

        client = genai.Client(api_key=API_KEY)
        parts = [
            genai_types.Part.from_text(text="Describe this image in one sentence."),
            genai_types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
        ]
        response = client.models.generate_content(
            model=MODEL,
            contents=parts,
            config=genai_types.GenerateContentConfig(temperature=0.1),
        )
        text = response.text.strip()
        print(f"[PASS]  Vision response: {text}")
        return True
    except Exception as e:
        print(f"[FAIL]  {e}")
        return False


def main():
    print("\n[OralAI] Gemini API Key Tester")
    print(f"   Key   : {API_KEY[:10]}...{API_KEY[-4:] if len(API_KEY) > 14 else '***'}")
    print(f"   Model : {MODEL}")

    if not API_KEY:
        print("\n[ERROR] GEMINI_API_KEY is not set in .env - aborting.")
        return

    t1 = test_text()
    t2 = test_vision()

    print(f"\n{'='*55}")
    if t1 and t2:
        print("[SUCCESS] ALL TESTS PASSED - real live AI analysis is ready!")
        print("   Restart backend: uvicorn app.main:app --reload")
    elif t1:
        print("[WARNING] Text works but vision failed.")
        print("   Check that your model supports image input.")
    else:
        print("[FAILED] Tests failed. Check the error above.")
        print("   Regenerate key at: https://aistudio.google.com/app/apikey")
        print("   Update GEMINI_API_KEY in backend/.env")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
