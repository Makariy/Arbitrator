from typing import Optional
import websockets


async def create_connection(url: str) -> Optional[websockets.WebSocketClientProtocol]:
    try:
        return await websockets.connect(url)
    except ConnectionRefusedError:
        return None



