import os
import google.generativeai as genai

# Using an environment variable for the API key in production
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "dummy_key_for_initialization")
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

def generate_response(prompt: str, context: list = None) -> str:
    """
    Generates an AI response using Gemini, injecting RAG context blocks.
    """
    full_prompt = prompt
    if context:
        context_str = "\n".join(context)
        full_prompt = f"Context from Company FAQs:\n{context_str}\n\nUser Question: {prompt}\n\nPlease act as a helpful Customer Support Agent and answer based on the context."
    
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print(f"CRITICAL GEMINI ERROR: {str(e)}")
        return "I am currently offline or experiencing heavy load. Please try again later."
