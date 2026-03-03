# Tool-Calling Agent

An LLM Agent system that understands natural language questions and reaches the answer by **calling API tools in the correct order** (chaining).

## Architecture

The system has two separate FastAPI microservices:

```
User
   │
   │  POST /agent/chat  {"message": "..."}
   ▼
┌──────────────────────────────────────────────────────────┐
│  llm_service (port 6712)                                 │
│                                                          │
│  agent_service.py  ←  Agent loop (explained below)       │
│       │                                                  │
│       ├─ tools/definitions.py   → Tool schemas for LLM   │
│       ├─ tools/executor.py      → Tool name → function   │
│       └─ service/api_client.py  → HTTP calls to api_service │
│              │                                           │
└──────────────┼───────────────────────────────────────────┘
               │  HTTP (Bearer token auth)
               ▼
┌──────────────────────────────────────────────────────────┐
│  api_service (port 2198)                                 │
│                                                          │
│  router/auth.py      → POST /auth/login                  │
│  router/data_api.py  → REST endpoints                    │
│  service/mongo_service.py → MongoDB Atlas queries         │
│              │                                           │
└──────────────┼───────────────────────────────────────────┘
               │
               ▼
         MongoDB Atlas
        (tool_agent_demo)
```

### Project Structure

```
tool_call/
├── api_service/
│   ├── src/
│   │   ├── router/
│   │   │   ├── auth.py          # Login endpoint (static token)
│   │   │   └── data_api.py      # Users, transactions, fraud endpoints
│   │   ├── service/
│   │   │   ├── auth_service.py  # Token verification
│   │   │   └── mongo_service.py # MongoDB CRUD functions
│   │   └── utils/config.py      # Environment variables
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── llm_service/
│   ├── src/
│   │   ├── router/
│   │   │   └── agent.py         # POST /agent/chat endpoint
│   │   ├── service/
│   │   │   ├── agent_service.py # Agent loop (state management here)
│   │   │   └── api_client.py    # HTTP calls to api_service
│   │   ├── tools/
│   │   │   ├── definitions.py   # OpenAI function calling schemas
│   │   │   └── executor.py      # Tool name → function dispatcher
│   │   └── utils/config.py      # Environment variables
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── data/
│   └── seed.py                  # MongoDB test data
├── docker-compose.yml
├── .env.example
└── README.md
```

## State Management (Agent Loop)

The agent's state is the **`messages` list** inside `agent_service.py`. This list follows the OpenAI Chat Completions API format and is the **single source of truth** for the agent loop.

### How the Loop Works

```python
messages = [system_prompt, user_message]

for iteration in range(MAX_ITERATIONS):     # Safety limit: 10
    response = LLM(messages, tools=TOOLS)   # Send full history to LLM
    messages.append(assistant_message)       # Add LLM response to state

    if tool_calls exist:
        for tool_call in tool_calls:
            result = execute_tool(...)       # HTTP request to api_service
            messages.append(tool_result)     # Add result to state
        → loop continues (LLM decides again)
    else:
        → LLM returned plain text, loop ends, reply sent to user
```

### Example: Chained Tool Calls

User question: *"Why was my payment rejected on the account ali@sirket.com?"*

```
┌──────────────────────────────────────────────────────────────────────┐
│  messages (state)                                                    │
│                                                                      │
│  1. system  → SYSTEM_PROMPT                                          │
│  2. user    → "Why was my payment rejected on ali@sirket.com?"       │
│                                                                      │
│  ─── iteration 1 ───                                                 │
│  3. assistant → tool_calls: get_user_details(email="ali@sirket.com") │
│  4. tool      → {"user_id":"u_1001", "account_status":"active"}      │
│                                                                      │
│  ─── iteration 2 ───                                                 │
│  5. assistant → tool_calls: get_recent_transactions(user_id="u_1001")│
│  6. tool      → {"transactions": [{id:"tx_9001", status:"failed"}]}  │
│                                                                      │
│  ─── iteration 3 ───                                                 │
│  7. assistant → tool_calls: check_fraud_reason(tx_id="tx_9001")      │
│  8. tool      → {"reason_message": "Insufficient funds..."}          │
│                                                                      │
│  ─── iteration 4 ───                                                 │
│  9. assistant → "Your payment was rejected due to insufficient funds."│
│     (no tool_calls → loop ends, this text is returned to user)       │
└──────────────────────────────────────────────────────────────────────┘
```

### Why This Design?

- **LLM is the decision maker**: The LLM decides which tool to call and in what order. There is no hardcoded chain.
- **Full context every iteration**: As the `messages` list grows, the LLM sees all previous tool results and decides the next step.
- **Missing parameter handling**: If the user does not give an email, the LLM does not call a random tool. It asks the user for the missing information (system prompt rule).
- **Error handling**: If a tool returns an error (`{"error": "User not found"}`), this error is added to `messages`. The LLM sees it and explains the situation to the user in natural language.
- **Safety limit**: `MAX_ITERATIONS = 10` prevents infinite loops.
- **Audit log**: Every tool call is saved in `tool_calls_log` and returned with the response.

## Tools

The agent can use 4 tools:

| Tool | Parameters | Description |
|------|-----------|-------------|
| `list_users` | — | Returns all registered users and their count |
| `get_user_details` | `email: str` | Email → user ID, account status |
| `get_recent_transactions` | `user_id: str`, `limit?: int` | User's recent transactions |
| `check_fraud_reason` | `transaction_id: str` | Why a failed transaction was rejected |

Tool definitions: `llm_service/src/tools/definitions.py`
Tool executor: `llm_service/src/tools/executor.py`
API client: `llm_service/src/service/api_client.py`

## API Endpoints

### api_service (port 2198)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | `{username, password}` → `{token}` |
| GET | `/api/users/list` | All users + count |
| POST | `/api/users/details` | `{email}` → user info |
| POST | `/api/transactions/recent` | `{user_id, limit?}` → recent transactions |
| POST | `/api/fraud/check` | `{transaction_id}` → rejection reason |
| GET | `/api/health` | DB connection check |

### llm_service (port 6712)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/agent/chat` | `{message}` → `{response, tool_calls_log}` |

## Setup

### 1. Environment Variables

```bash
cp .env.example .env
```

Edit the `.env` file:

```env
# MongoDB Atlas
MONGO_URI=mongodb+srv://<user>:<password>@cluster0.xxxxx.mongodb.net/?appName=Cluster0
MONGO_DB_NAME=tool_agent_demo

# API Service Auth
API_USERNAME=admin
API_PASSWORD=changeme
STATIC_TOKEN=changeme-static-token

# LLM (OpenRouter)
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=sk-or-...
LLM_MODEL=openai/gpt-4o-mini

# Service URLs (local: localhost / Docker: docker-compose overrides this)
API_SERVICE_URL=http://localhost:2198

# Ports
LLM_SERVICE_PORT=6712
API_SERVICE_PORT=2198
```

### 2. Seed Data

```bash
pip install pymongo[srv] python-dotenv
python data/seed.py
```

After seeding, the database contains:

| Collection | Count | Examples |
|------------|-------|---------|
| `users` | 3 | ali@sirket.com (active), ayse@sirket.com (suspended), mehmet@sirket.com (active) |
| `transactions` | 4 | u_1001→failed(1250.50), u_1001→success(500), u_1002→failed(220), u_1003→pending(780) |
| `fraud_logs` | 2 | tx_9001→INSUFFICIENT_FUNDS, tx_9003→SUSPICIOUS_ACTIVITY |

### 3a. Run Locally

Open two terminals:

```bash
# Terminal 1 — api_service
pip install -r api_service/requirements.txt
python api_service/app.py
```

```bash
# Terminal 2 — llm_service
pip install -r llm_service/requirements.txt
python llm_service/app.py
```

### 3b. Run with Docker

```bash
docker-compose up --build
```

> In Docker mode, `API_SERVICE_URL` is automatically overridden to `http://api_service:2198`
> (see `docker-compose.yml` → `environment` block). The `localhost` value in `.env` is only for local development.

Services:
- **api_service**: http://localhost:2198 — Swagger: http://localhost:2198/docs
- **llm_service**: http://localhost:6712 — Swagger: http://localhost:6712/docs

## Usage Examples

### Chained Tool Calls

```bash
curl -s -X POST http://localhost:6712/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "ali@sirket.com adresli hesabımla dün yapmaya çalıştığım ödeme neden reddedildi?"}' | python -m json.tool
```

Agent chain:
1. `get_user_details("ali@sirket.com")` → finds `u_1001`
2. `get_recent_transactions("u_1001")` → finds `tx_9001` (failed)
3. `check_fraud_reason("tx_9001")` → returns "Insufficient funds"
4. Generates a natural language answer for the user

### General Question

```bash
curl -s -X POST http://localhost:6712/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "sistemde kaç kişi kayıtlı?"}' | python -m json.tool
```

Agent calls `list_users()` → returns 3 users

### Missing Parameter Handling

```bash
curl -s -X POST http://localhost:6712/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "son işlemlerimi göster"}' | python -m json.tool
```

Agent does not call any tool. It asks the user for their email address.

### Error Handling

```bash
curl -s -X POST http://localhost:6712/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test@yok.com hesabımın durumu nedir?"}' | python -m json.tool
```

Agent calls `get_user_details("test@yok.com")` → API returns 404 → Agent tells the user "this email was not found".

## Testing Notes

- **Add new records**: Edit `data/seed.py` or add records directly to MongoDB to test the agent with new data.
- **Change API responses**: Edit functions in `api_service/src/service/mongo_service.py` or change MongoDB data directly. The agent will use the new data correctly.
- **Agent does not follow a fixed flow**: The LLM decides which tool to call. Even if the data changes, the agent takes the new data as a parameter and explains it to the user correctly.
- **`tool_calls_log`**: Every response includes which tools were called, in what order, and their results.