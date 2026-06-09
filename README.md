# Task Management Chat Agent

This app is a task management chat agent.


## What it does

- Serves a FastAPI backend at `main.py`
- Uses `agent_service.py` to send user requests to the Groq chat API
- Supports tool-based task management operations via `todo_service.py`
- Handles task creation, listing, updating, and deletion through structured tool calls
- Provides a React client in `todo-chat-client/` for a browser interface

## Backend overview

- `main.py` starts a FastAPI server and exposes one endpoint:
  - `POST /chat`
- `agent_service.py`:
  - builds the chat prompt
  - defines available tools for task management
  - sends requests to the Groq API
  - processes tool calls and returns a final response
- `todo_service.py` stores tasks in memory and implements:
  - `add_task`
  - `get_tasks`
  - `update_task`
  - `delete_task`

## Requirements

- Python 3.13+ (project virtual environment is stored in `.venv/`)
- Node.js + npm (only if you want to run the React frontend)

## Setup

1. Open PowerShell in the project root:
   ```powershell
   cd "C:\Users\user1\Downloads\ZioNet Course\1_function_calling"
   ```

2. Activate the Python virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. Install backend dependencies if needed:
   ```powershell
   py -m pip install fastapi uvicorn pydantic python-dotenv groq
   ```

4. Create or update `.env` with API keys:
   ```text
   GROQ_API_KEY=your_groq_api_key
      ```

## Run the backend

```powershell
py -m uvicorn main:app --reload
```

The API will be available at:

- `http://127.0.0.1:8000`

## Run the React frontend (optional)

1. Open a terminal in `todo-chat-client/`

```powershell
cd todo-chat-client
npm install
npm start
```

2. Open the browser at:

- `http://localhost:3000`

## Usage

- Send a chat request to the backend via `POST /chat`
- The backend routes messages through `agent_service.py`
- If the model triggers a tool call, the backend executes it in `todo_service.py`
- The final response is returned as:
  - `{ "reply": "..." }`


