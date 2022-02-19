import logging
import websockets
import json
from decimal import Decimal

log = logging.getLogger(__name__)


async def calculate_btceur_price(btc_ask: Decimal) -> dict:
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

        async for message in websocket:
            response_json = json.loads(message)
            response_data = response_json['data'].get('asks', [])
            # print(response_data)
            if len(response_data) > 0:
                for ask in response_data:
                    btc = Decimal(ask[1])
                    if ask == response_data[len(response_data)-1] and btc < remainder_btc:
                        return {'btc_ask': "btc too large, total_price not available"}
                    if btc <= remainder_btc:
                        result += Decimal(ask[0])*btc
                        remainder_btc -= btc
                    else:
                        result += Decimal(ask[0])*btc
                        break
                print(result)
                return {'btc_ask': result}


