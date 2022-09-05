from typing import Optional, Dict
import websockets
import json
from json.decoder import JSONDecodeError


async def create_connection(url: str) -> Optional[websockets.WebSocketClientProtocol]:
    try:
        return await websockets.connect(url)
    except ConnectionRefusedError:
        return None


async def recv_json(connection: websockets.WebSocketClientProtocol) -> Dict:
    try:
        response = json.loads(await connection.recv())
        return response
    except JSONDecodeError as error:
        raise ValueError(f"Could not parse the response from server: '{error}'")


async def send_json(connection: websockets.WebSocketClientProtocol, data: Dict):
    await connection.send(json.dumps(data))

