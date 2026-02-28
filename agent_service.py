import json
import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

import todo_service


client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL = "llama-3.3-70b-versatile"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Add a new task",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": { "type": "string" },
                    "task_type": { "type": "string" },
                    "description": { "type": "string" },
                    "start_date": { "type": "string" },
                    "end_date": { "type": "string" },
                    "status": { "type": "string" }
                },
                "required": ["title", "task_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_tasks",
            "description": "Get tasks with optional filters",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": { "type": "string" },
                    "task_type": { "type": "string" }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update an existing task",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": { "type": "integer" },
                    "title": { "type": "string" },
                    "status": { "type": "string" }
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task by code",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": { "type": "integer" }
                },
                "required": ["code"]
            }
        }
    }
]

def agent(query: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a task management agent.\n"
                "You have access ONLY to the tasks stored in the system tools.\n"
                "You must NEVER invent tasks, categories, or lists.\n"
                "If the user asks to see their tasks, you MUST call get_tasks.\n"
                "If there are no tasks, say explicitly that the task list is empty.\n"
                "If the user asks a question that requires task data, you MUST use a tool.\n"
                "If a request cannot be fulfilled with the available tools, say so clearly.\n"
                "Do NOT provide generic productivity advice.\n"
                "Answer in Hebrew.\n"
            )
        },
        {
            "role": "user",
            "content": query
        }
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )

    message = response.choices[0].message

    print("=== RAW MODEL MESSAGE ===")
    print(message)
    print("tool_calls:", message.tool_calls)
    print("=========================")

    # אם המודל בחר להפעיל פונקציה
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        
        tool_name = tool_call.function.name

        raw_args = tool_call.function.arguments

        # ⬅️ זה הקריטי
        if raw_args:
            args = json.loads(raw_args)
        else:
            args = {}

        # הגנה מלאה
        if not isinstance(args, dict):
            args = {}

        # casting בטוח
        if "code" in args:
            args["code"] = int(args["code"])

        try:
            if tool_name == "add_task":
                result = todo_service.add_task(**args)
            elif tool_name == "get_tasks":
                result = todo_service.get_tasks(**args)
            elif tool_name == "update_task":
                result = todo_service.update_task(**args)
            elif tool_name == "delete_task":
                result = todo_service.delete_task(**args)
            else:
                result = "Unknown action"

        except Exception as e:
            return f"שגיאה: {str(e)}"

        # ניסוח תשובה אנושית
        final_response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Explain the result to the user in a friendly, human way (Hebrew)."
                },
                {
                    "role": "user", "content": query
                },
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=False)
                }
            ]
        )

        return final_response.choices[0].message.content

    # אם לא נבחר tool
    return message.content