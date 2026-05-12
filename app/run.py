import uvicorn
from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from api import router

# app monta tudo
app = FastAPI(
    title="monks media agent",
    description="agente ia analista junior de midia — mvp",
    version="0.1.0",
)

import os

base_path = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(base_path, "static")

# servir interface de chat
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/chat")
async def chat_ui():
    return RedirectResponse(url="/static/index.html")

app.include_router(router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run("run:app", host="0.0.0.0", port=8000, reload=True)
