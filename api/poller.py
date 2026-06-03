import asyncio
import logging
import httpx
from .models import Server

logger = logging.getLogger(__name__)


async def poll_server(server_id: int, url: str, store: dict) -> None:
    """Check a single server's health endpoint and update its status in store."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{url}/health")
        if resp.status_code == 200:
            store[server_id].status = "UP"
        else:
            store[server_id].status = "DEGRADED"
        logger.info("Server %d — %s", server_id, store[server_id].status)
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        store[server_id].status = "DOWN"
        logger.warning("Server %d — DOWN (%s)", server_id, e)


async def run_poll_loop(store: dict, interval: int = 10) -> None:
    """Infinite loop that polls all servers concurrently every interval seconds."""
    while True:
        if store:
            await asyncio.gather(*[
                poll_server(sid, server.base_url(), store)
                for sid, server in store.items()
            ])
        await asyncio.sleep(interval)