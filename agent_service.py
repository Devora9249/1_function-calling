import json
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel

import todo_service

load_dotenv()

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
                    "title": {"type": "string"},
                    "task_type": {"type": "string"},
                    "description": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                    "status": {"type": "string"},
                },
                "required": ["title", "task_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_tasks",
            "description": "Get tasks with optional filters",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "task_type": {"type": "string"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update an existing task",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "integer"},
                    "title": {"type": "string"},
                    "status": {"type": "string"},
                },
                "required": ["code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task by code",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "integer"},
                },
                "required": ["code"],
            },
        },
    },
]

RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "AgentResponse",
        "schema": {
            "type": "object",
            "properties": {
                "reply": {"type": "string"},
            },
            "required": ["reply"],
        },
    },
}


class AgentResponse(BaseModel):
    reply: str


def _parse_agent_response(content: Optional[str]) -> AgentResponse:
    if not content:
        raise ValueError("Empty response from model.")

    trimmed = content.strip()
    if not trimmed:
        raise ValueError("Empty response from model.")

    try:
        payload = json.loads(trimmed)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON response: {exc.msg}") from exc

    return AgentResponse.model_validate(payload)


def _normalize_tool_call(tool_call: Any) -> Dict[str, Any]:
    if hasattr(tool_call, "model_dump"):
        return tool_call.model_dump()
    if isinstance(tool_call, dict):
        return tool_call

    return {
        "id": getattr(tool_call, "id", ""),
        "function": {
            "name": getattr(tool_call.function, "name", ""),
            "arguments": getattr(tool_call.function, "arguments", "{}"),
        },
        "type": getattr(tool_call, "type", "function"),
    }


def _run_tool_call(tool_call: Any) -> Any:
    tool_name = getattr(tool_call.function, "name", None)
    raw_args = getattr(tool_call.function, "arguments", None)

    if isinstance(raw_args, str):
        try:
            args = json.loads(raw_args)
        except json.JSONDecodeError:
            args = {}
    elif isinstance(raw_args, dict):
        args = raw_args
    else:
        args = {}

    if not isinstance(args, dict):
        args = {}

    if "code" in args:
        try:
            args["code"] = int(args["code"])
        except (TypeError, ValueError):
            pass

    try:
        if tool_name == "add_task":
            return todo_service.add_task(**args)
        if tool_name == "get_tasks":
            return todo_service.get_tasks(**args)
        if tool_name == "update_task":
            return todo_service.update_task(**args)
        if tool_name == "delete_task":
            return todo_service.delete_task(**args)
    except Exception as exc:
        raise RuntimeError(str(exc)) from exc

    raise ValueError(f"Unknown tool: {tool_name}")


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
            ),
        },
        {"role": "user", "content": query},
    ]

    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            response_format=RESPONSE_FORMAT,
            reasoning_format="hidden",
        )

        completion = response.choices[0]
        message = completion.message
        tool_calls = getattr(message, "tool_calls", None) or []

        print("=== RAW MODEL MESSAGE ===")
        print(message)
        print("tool_calls:", tool_calls)
        print("=========================")

        if not tool_calls:
            try:
                return _parse_agent_response(message.content).reply
            except ValueError:
                return message.content or ""

        messages.append(
            {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [_normalize_tool_call(call) for call in tool_calls],
            }
        )

        for tool_call in tool_calls:
            try:
                tool_result = _run_tool_call(tool_call)
            except Exception as exc:
                return f"שגיאה: {str(exc)}"

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result, ensure_ascii=False),
                }
            )
