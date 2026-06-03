import asyncio
import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from api.models import Server, ServerIn, ServerOut
from api.auth import verify_api_key
from api.metrics import get_system_metrics
from api.poller import run_poll_loop, poll_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s"
)
logger = logging.getLogger(__name__)

_store: dict[int, Server] = {}
_counter = 0
_poll_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _poll_task
    _poll_task = asyncio.create_task(run_poll_loop(_store))
    logger.info("Poll loop started")
    yield
    _poll_task.cancel()
    logger.info("Poll loop stopped")


app = FastAPI(title="DevOps Monitoring API", version="1.0", lifespan=lifespan)


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok"}


@app.get("/metrics", tags=["System"])
async def get_metrics():
    return get_system_metrics()


@app.websocket("/ws/metrics")
async def ws_metrics(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_text(json.dumps(get_system_metrics()))
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")


@app.post("/servers", response_model=ServerOut, status_code=201, tags=["Servers"])
async def register_server(server: ServerIn, _: str = Depends(verify_api_key)):
    global _counter
    _counter += 1
    record = Server(id=_counter, name=server.name, host=server.host,
                    port=server.port, tags=server.tags)
    _store[_counter] = record
    return record


@app.get("/servers", response_model=list[ServerOut], tags=["Servers"])
async def list_servers(status: str | None = None):
    servers = list(_store.values())
    if status:
        servers = [s for s in servers if s.status == status]
    return servers


@app.get("/servers/{server_id}", response_model=ServerOut, tags=["Servers"])
async def get_server(server_id: int):
    if server_id not in _store:
        raise HTTPException(status_code=404, detail="Server not found")
    return _store[server_id]


@app.delete("/servers/{server_id}", status_code=204, tags=["Servers"])
async def delete_server(server_id: int, _: str = Depends(verify_api_key)):
    if server_id not in _store:
        raise HTTPException(status_code=404, detail="Server not found")
    del _store[server_id]


@app.post("/servers/{server_id}/check", response_model=ServerOut, tags=["Servers"])
async def trigger_check(server_id: int):
    if server_id not in _store:
        raise HTTPException(status_code=404, detail="Server not found")
    await poll_server(server_id, _store[server_id].base_url(), _store)
    return _store[server_id]