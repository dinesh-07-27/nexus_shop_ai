import os
import google.generativeai as genai

KEY = "AIzaSyCpBOTGWykwJC3PH7H1WRv3uBkzxJOEWw4"
genai.configure(api_key=KEY)

print("Checking available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Failed to list models: {e}")

print("\nTesting gemini-pro...")
try:
    model1 = genai.GenerativeModel('gemini-pro')
    response1 = model1.generate_content("Say hello")
    print("gemini-pro SUCCESS:", response1.text)
except Exception as e:
    print("gemini-pro FAILED:", e)

print("\nTesting gemini-1.5-flash...")
try:
    model2 = genai.GenerativeModel('gemini-1.5-flash')
    response2 = model2.generate_content("Say hello")
    print("gemini-1.5-flash SUCCESS:", response2.text)
except Exception as e:
    print("gemini-1.5-flash FAILED:", e)
