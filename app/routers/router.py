from fastapi import APIRouter, HTTPException
from app.models import InputModel
from app.tasks import start_task, redis_client
import json

router = APIRouter()

@router.post("/analyze-pr")
def analyze_pr(data: InputModel):
    task = start_task.delay(data.dict())
    if not task:
        raise HTTPException(status_code=500, detail="Failed to start task.")
    return {"task_id": task.id, "status": "pending"}

@router.get("/status/{task_id}")
def get_task_status(task_id: str):
    status = redis_client.hget(task_id, "status")
    if not status:
        raise HTTPException(status_code=404, detail="Task ID not found.")
    return {"task_id": task_id, "status": status}

@router.get("/results/{task_id}")
def get_task_result(task_id: str):
    task_data = redis_client.hgetall(task_id)
    task_data["response"] = json.loads(task_data["response"])
    if not task_data:
        raise HTTPException(status_code=404, detail="Task ID not found.")
    return task_data
