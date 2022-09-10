from typing import Optional, Dict
import websockets
import json
from json.decoder import JSONDecodeError


async def create_connection(url: str) -> Optional[websockets.WebSocketClientProtocol]:
    try:
        return await websockets.connect(url)
    except ConnectionRefusedError:
        return None


async def recv_json(connection: websockets.WebSocketClientProtocol, decompress_function=None) -> Dict:
    try:
        data = await connection.recv()
        if decompress_function is not None:
            data = decompress_function(data)

        if type(data) is bytes:
            data = data.decode()

        response = json.loads(data)
        return response
    except JSONDecodeError as error:
        raise ValueError(f"Could not parse the response from server: '{error}'")


async def send_json(connection: websockets.WebSocketClientProtocol, data: Dict):
    await connection.send(json.dumps(data))

