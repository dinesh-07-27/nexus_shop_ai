<div align="center">
  <h1>🚀 NexusShop AI</h1>
  <h3>An Elite Microservices E-Commerce Architecture 🛒</h3>
  <p>Production-Grade Backend featuring Event-Driven Sagas (RabbitMQ), High-Speed Fuzzy Search (ElasticSearch), and an Integrated Applied AI Chatbot (FAISS RAG + Gemini).</p>
</div>

<br>

---

## 🏗️ High-Level System Architecture

This project strictly adheres to a domain-driven **Microservices Architecture**. It decouples a traditional e-commerce monolith into 5 independent, horizontally scalable APIs.

### The 5 Microservices
1. **API Gateway (FastAPI + SlowAPI)**
   - Acts as the single entry point.
   - Enforces IP-based rate limiting to prevent DDoS.
   - Secure Reverse Proxy routing via async `httpx` and DNS container resolution.
2. **User Service (FastAPI + PostgreSQL + Redis)**
   - Manages secure user authentication via Bcrypt hashing.
   - Issues and validates JWT Bearer tokens for Role-Based Access Control (Admin/User).
3. **Product Catalog Service (FastAPI + PostgreSQL + ElasticSearch)**
   - Dual-write pattern: Ensures ACID inventory tracking in PostgreSQL while pushing asynchronous indexes to an ElasticSearch cluster.
   - The `/search` endpoint utilizes `multi_match` fuzzy text lookup for lightning-fast catalog querying.
4. **Order Service (Django + Celery + RabbitMQ)**
   - Handles the entire checkout lifecycle securely.
   - Implements the **Saga Pattern**: When an order is placed, an asynchronous background event is published to a RabbitMQ message queue so the rest of the infrastructure can adjust inventory autonomously.
5. **Smart AI Assistant (FastAPI + FAISS + Gemini 1.5 Pro)**
   - The crown jewel: A specialized Applied AI service.
   - **RAG Pipeline**: Retrieves store policies via FAISS vector similarity search and augments the LLM generation context.
   - **Tool Calling/Agents**: The LLM intelligently parses user intents and triggers secure internal network requests to both the Product Service (`"Buy headphones"`) and Order Service (`"Where is order #123?"`) before responding.

---

## 🛠️ Infrastructure & Tech Stack

| Domain | Technology Let |
| --- | --- |
| **Code Frameworks** | Python 3.11, FastAPI, Django, Pydantic |
| **Databases** | PostgreSQL (Relational), ElasticSearch (Fuzzy Lookup) |
| **Brokers & Caching** | RabbitMQ (Message Queues), Redis (Caching) |
| **Applied AI** | FAISS (Vector Store), Google Gemini (LLM & Agents) |
| **DevOps & QA** | Docker, Docker Compose, Pytest, GitHub Actions |

---

## ⚡ Setup & Deployment

The entire 9-container architecture (4 Databases + 5 Services) can be spun up locally with a single command. 

### Local Development Environment
```bash
# Clone the repository
git clone https://github.com/yourusername/nexus_shop_ai.git
cd nexus_shop_ai

# Boot the entire infrastructure via Docker Network
docker-compose up --build
```

### Production Deployment Strategy (CI/CD)
This project is configured natively with **GitHub Actions**. Every commit to the `main` branch automatically triggers an isolated pipeline consisting of:
1. Bootstrapping PostgreSQL and Redis test containers.
2. Installing Python environments.
3. Running comprehensive `Pytest` suites to enforce a >90% code coverage SLA.
4. Packaging independent Docker images.

---

<div align="center">
  <i>Developed and architected by K Dinesh Reddy.</i><br>
  <a href="https://linkedin.com/in/dinesh-reddy-vit">LinkedIn</a> • <a href="https://github.com/dinesh-07-27">GitHub</a>
</div>
