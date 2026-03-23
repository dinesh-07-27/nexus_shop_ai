import httpx
import numpy as np
from schemas.chat import ChatRequest, ChatResponse
from llm.gemini_client import generate_response
from rag.vector_store import store

async def process_chat(request: ChatRequest) -> ChatResponse:
    user_message = request.message.lower()

    # Tool Calling Example: Check if user intent is searching for a product
    if any(word in user_message for word in ["price", "find", "buy", "headphones", "phone"]):
        async with httpx.AsyncClient() as client:
            try:
                # Querying the internal product service directly (microservice-to-microservice)
                prod_res = await client.get(f"http://product_service:8000/products/search?query={request.message}", timeout=5.0)
                if prod_res.status_code == 200:
                    products = prod_res.json().get('results', [])
                    if products:
                        context = [f"Product Found: {p['name']} - ${p['price']} (Stock: {p['stock']})" for p in products[:3]]
                        bot_text = generate_response(request.message, context)
                        return ChatResponse(reply=bot_text, intent="product_search")
            except Exception as e:
                print(f"Product service query failed: {e}")

    # Tool Calling Example: Check if user is asking about an order tracking status
    if "order" in user_message and any(char.isdigit() for char in user_message):
        # Extract the integer ID
        order_id = ''.join(filter(str.isdigit, user_message))
        if order_id:
            async with httpx.AsyncClient() as client:
                try:
                    order_res = await client.get(f"http://order_service:8000/orders/{order_id}", timeout=5.0)
                    if order_res.status_code == 200:
                        order_data = order_res.json()
                        context = [f"Order ID {order_id} is currently {order_data['status']}"]
                        bot_text = generate_response(request.message, context)
                        return ChatResponse(reply=bot_text, intent="order_tracking")
                except Exception:
                    pass

    # Default RAG FAQ Flow
    # 1. Generate query embedding
    query_emb = np.random.rand(384).astype('float32')
    
    # 2. Search FAISS for related internal rules/policies
    context_docs = store.search(query_emb)

    # 3. Call Gemini LLM with augmented context
    reply = generate_response(user_message, context_docs)

    return ChatResponse(reply=reply, intent="faq_or_general")
