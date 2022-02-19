import logging
import websockets
import json
from decimal import Decimal

log = logging.getLogger(__name__)


async def calculate_btceur_price(btc_ask: Decimal) -> dict:
    """
        calculate the total USD price of btc_ask from bitstamp order book
        connects to bitstamp via websocket considering latency
    """

    if btc_ask <= 0.0:
        log.error(f"Invalid btc_ask: {btc_ask}")
        raise ValueError(f"btc_ask should be greater than 0, but received {btc_ask} instead.")
    remainder_btc = btc_ask
    result = 0
    msgs = {"event": "bts:subscribe", "data": {"channel": "order_book_btceur"}}
    msgs = json.dumps(msgs)
    uri = "wss://ws.bitstamp.net"
    log.info(f"Connecting to bitstamp websocket at {uri} ...")
    async with websockets.connect(uri) as websocket:
        await websocket.send(msgs)
        async for message in websocket:                     # the response is a coroutine
            response_json = json.loads(message)
            response_data = response_json['data'].get('asks', [])
            if len(response_data) > 0:
                for ask in response_data:
                    btc = Decimal(ask[1])
                    if ask == response_data[len(response_data)-1] and btc < remainder_btc:  # for btc_ask(input) that is larger
                        return {'btc_ask': "btc too large, total_price not available"}      # than sum of the available ask btc
                    if btc <= remainder_btc:
                        result += Decimal(ask[0])*btc
                        remainder_btc -= btc
                    else:
                        result += Decimal(ask[0])*btc
                        break
                print(result)
                return {'btc_ask': result}


