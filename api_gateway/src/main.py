import os

import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Mentor Bot API Gateway")

SERVICES = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://auth_service:8000"),
    "checklist": os.getenv("CHECKLIST_SERVICE_URL", "http://checklist-service:8001"),
    "knowledge": os.getenv("KNOWLEDGE_SERVICE_URL", "http://knowledge-service:8002"),
    "meeting": os.getenv("MEETING_SERVICE_URL", "http://meeting-service:8003"),
    "notification": os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8004"),
    "search": os.getenv("SEARCH_SERVICE_URL", "http://search-service:8005"),
}


@app.middleware("http")
async def route_requests(request, call_next):
    path = request.url.path
    method = request.method

    if path.startswith("/api/auth"):
        service_url = SERVICES["auth"]
        target_path = path.replace("/api/auth", "")
    elif path.startswith("/api/checklists"):
        service_url = SERVICES["checklist"]
        target_path = path.replace("/api/checklists", "")
    elif path.startswith("/api/knowledge"):
        service_url = SERVICES["knowledge"]
        target_path = path.replace("/api/knowledge", "")
    elif path.startswith("/api/meetings"):
        service_url = SERVICES["meeting"]
        target_path = path.replace("/api/meetings", "")
    elif path.startswith("/api/search"):
        service_url = SERVICES["search"]
        target_path = path.replace("/api/search", "")
    elif path.startswith("/api/notifications"):
        service_url = SERVICES["notification"]
        target_path = path.replace("/api/notifications", "")
    else:
        return await call_next(request)

    async with httpx.AsyncClient() as client:
        target_url = f"{service_url}{target_path}"

        headers = dict(request.headers)
        headers.pop("host", None)

        response = await client.request(method=method, url=target_url, headers=headers, content=await request.body())

        return JSONResponse(content=response.json(), status_code=response.status_code, headers=dict(response.headers))
