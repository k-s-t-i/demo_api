import json
import logging
from typing import List
import websockets
from decimal import Decimal


class BtcEurCalculatorService:
    """

    """

    def __init__(self):
        """
        Remember to call start() before attempting to use your new instance!
        """

        self._logger = logging.getLogger(__name__)

        # """
        # result holder
        # """
        self.handlers: List["result"] = []

        """
        Our socket to Bitstamp.
        """
        self._websocket: "WebSocketClientProtocol" = None

    async def start(self, btc_ask: Decimal):
        uri = "wss://ws.bitstamp.net"
        self._websocket = await websockets.connect(uri)

        # Send order-book websockets event message:
        await self.send_outbound_message(json.dumps({"event": "bts:subscribe",
                                                     "data": {"channel": "order_book_btceur"}}))

        try:
            # This is an infinite loop until the connection dies:
            await self._message_receive_loop(self._websocket, btc_ask)

        finally:
            await self._websocket.close()
        self._logger.warning("Websockets to Bitstamp Disconnected!")
        return self.handlers

    def result_handler(self, result):
        """
        Receives the result
        whenever the data from the bitstamp stream is processed.
        """
        self.handlers.append(result)

    async def send_outbound_message(self, message: str) -> None:
        """
        Send a message from this service to the Bitstamp websockets server.
        """
        if not self._websocket:
            raise Exception(
                "Bitstamp websockets is not open! Failed to send message.")

        self._logger.info(
            f"Sending outbound message to Bitstamp websockets. Message: {message}")
        await self._websocket.send(message)

    async def _message_receive_loop(self, websocket: websockets.WebSocketClientProtocol, btc_ask: Decimal):
        """
        Loop of waiting for and processing inbound websocket messages, until the
        connection dies.
        """
        async for message in websocket:
            print(message)
            self._logger.info(
                f"Received inbound message from Bitstamp websockets: {message}")

            await self._process_inbound_message(message, btc_ask)

    async def _process_inbound_message(self, message: str, btc_ask: Decimal):
        """
        Process one individual inbound websocket message.
        """
        remainder_btc = btc_ask
        result = Decimal(0)
        try:
            parsed_event = json.loads(message)
        except:
            """
            When receiving invalid data from the Bitstamp websockets, our socket
            is in a questionable state... Let the error propagate. Possible restart.
            """
            self._logger.exception(
                "Failed to parse Stream Deck message as JSON! Message: {message}")
            raise

        response_data = parsed_event['data'].get('asks', [])
        if len(response_data) > 0:
            for ask in response_data:
                btc = Decimal(ask[1])
                if ask == response_data[
                    len(response_data) - 1] and btc < remainder_btc:  # for btc_ask(input) that is larger
                    # return {'btc_ask': "btc too large, total_price not available"}  # than sum of the available ask btc
                    result = "btc too large, total_price not available"
                    self.result_handler(result)
                    if self._websocket is not None:
                        await self._websocket.close()
                    return result
                if btc <= remainder_btc:
                    result += Decimal(ask[0]) * btc
                    remainder_btc = remainder_btc - btc
                elif remainder_btc == 0:
                    break
                else:
                    result += Decimal(ask[0]) * remainder_btc
                    break
            result = result.quantize(Decimal("0.00"))
            print(result)
            self.result_handler(result)
            if self._websocket is not None:
                await self._websocket.close()
            return result
