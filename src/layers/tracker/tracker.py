import logging
import asyncio

from lib.database import Database
from .services.connect_services import create_connection
from websockets import WebSocketClientProtocol


logger = logging.getLogger(__package__)
database = Database()


async def _run_tracker(args):
    input = args.input
    output = args.output
    logger.info(f"Start tracking from {input} to {output}")
    import json

    try:
        connection: WebSocketClientProtocol = await create_connection("wss://ws-api.kucoin.com/endpoint?token=2neAiuYvAU61ZDXANAGAsiL4-iAExhsBXZxftpOeh_55i3Ysy2q2LEsEWU64mdzUOPusi34M_wGoSf7iNyEWJ1_JgXDB8YtrNOyI44h2oQs28wGuiBzOitiYB9J6i9GjsxUuhPw3BlrzazF6ghq4L31_hO0zCJmZbniHVHp_hk4=.Tld23FrITRJoOgagK1sF-w==")
        if connection is None:
            logger.error(f"Server refused to accept the connection")
            return

        response = json.loads(await connection.recv())

        subscription = {
            "id": response.get('id'),  # Хз, нахуй не понимаю что это
            "type": "subscribe",
            "topic": "/spotMarket/level2Depth50:BTC-USDT",
            "privateChannel": False,
            "response": True
        }
        await connection.send(json.dumps(subscription))
        for i in range(100):
            response = json.loads(await connection.recv())
            print(response)

        await connection.close()

    except ConnectionError as error:
        logger.error(f"Server closed the connection: {error}")


def run_tracker(args):
    asyncio.run(_run_tracker(args))
