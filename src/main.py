import logging
import time

from binance.lib.utils import config_logging
from binance.websocket.spot.websocket_stream import SpotWebsocketStreamClient

config_logging(logging, logging.DEBUG)


def main():
    def message_handler(meta, arg):
        print(meta)

    ws_client = SpotWebsocketStreamClient(on_message=message_handler)

    ws_client.mini_ticker(
        symbol='notusdt',
        callback=message_handler
    )

    # Combine selected streams
    # ws_client.subscribe(
    #     stream=['bnbusdt@bookTicker', 'ethusdt@bookTicker'],
    #     callback=message_handler,
    # )
    ws_client.stop()


main()
