# tasks = []
# _next_id = 1

# def add_task(title: str, type: str, description: str = None, start_date: str = None, end_date: str = None, status: str = "pending"):
#     """
#     Adds a new task to the list. 
#     Required: title and type.
#     """
#     global _next_id
#     task = {
#         "code": _next_id,
#         "title": title,
#         "description": description,
#         "type": type,
#         "start_date": start_date,
#         "end_date": end_date,
#         "status": status
#     }
#     tasks.append(task)
#     _next_id += 1
#     return task

# def get_tasks(status: str = None, task_type: str = None):
#     """
#     Retrieves tasks. Can be filtered by status or type.
#     """
#     result = tasks
#     if status:
#         result = [t for t in result if t["status"] == status]
#     if task_type:
#         result = [t for t in result if t["type"] == task_type]
#     return result

# def update_task(code: int, status: str = None, title: str = None):
#     """
#     Updates an existing task by its code.
#     """
#     for task in tasks:
#         if task["code"] == code:
#             if status: task["status"] = status
#             if title: task["title"] = title
#             return task
#     return None

# def delete_task(code: int):
#     """
#     Deletes a task by its unique code.
#     """
#     global tasks
#     initial_length = len(tasks)
#     tasks = [t for t in tasks if t["code"] != code]
#     return len(tasks) < initial_length

tasks = []
_next_id = 1


def add_task(
    title: str,
    task_type: str,
    description: str = None,
    start_date: str = None,
    end_date: str = None,
    status: str = "pending"
):
    """
    Adds a new task to the list.
    Required: title and task_type.
    """
    global _next_id

    task = {
        "code": _next_id,
        "title": title,
        "description": description,
        "type": task_type,
        "start_date": start_date,
        "end_date": end_date,
        "status": status
    }

    tasks.append(task)
    _next_id += 1
    return task


def get_tasks(status: str = None, task_type: str = None):
    """
    Retrieves tasks. Can be filtered by status or type.
    """
    result = tasks

    if status:
        result = [t for t in result if t["status"] == status]

    if task_type:
        result = [t for t in result if t["type"] == task_type]

    return result


def update_task(
    code: int,
    title: str = None,
    status: str = None,
    description: str = None,
    start_date: str = None,
    end_date: str = None
):
    """
    Updates an existing task by its code.
    """
    for task in tasks:
        if task["code"] == code:
            if title is not None:
                task["title"] = title
            if status is not None:
                task["status"] = status
            if description is not None:
                task["description"] = description
            if start_date is not None:
                task["start_date"] = start_date
            if end_date is not None:
                task["end_date"] = end_date

            return task

    raise ValueError("Task not found")


def delete_task(code: int):
    """
    Deletes a task by its unique code.
    """
    global tasks

    initial_length = len(tasks)
    tasks = [t for t in tasks if t["code"] != code]

    if len(tasks) == initial_length:
        raise ValueError("Task not found")

    return True