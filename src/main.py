import asyncio
import logging
import json

from binance.lib.utils import config_logging
from binance.websocket.spot.websocket_stream import SpotWebsocketStreamClient

config_logging(logging, logging.DEBUG)


async def main():
    def message_handler(meta, arg):
        print(arg)
        var = json.loads(arg)
        print(var)

    ws_client = SpotWebsocketStreamClient(on_message=message_handler)

    ws_client.mini_ticker(
        # symbol='notusdt',
        callback=message_handler
    )

    # await asyncio.sleep(10)

    # Combine selected streams
    # ws_client.subscribe(
    #     stream=['bnbusdt@bookTicker', 'ethusdt@bookTicker'],
    #     callback=message_handler,
    # )
    # ws_client.stop()


asyncio.run(main())
