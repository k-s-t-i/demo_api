import json
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, call, patch
from decimal import Decimal
import websockets
from demo_api.btc_eur_calculator_service import BtcEurCalculatorService


class BtcEurCalculatorServiceTests(IsolatedAsyncioTestCase):

    @patch("websockets.connect", new_callable=AsyncMock)
    async def test_registration_procedure(self, websocket_connect_mock):
        """
        Testing connection initiation process
        """

        client = BtcEurCalculatorService()
        client._logger = MagicMock()  # Suppress logging
        client.send_outbound_message = AsyncMock()

        await client.start(1.0)

        websocket_connect_mock.assert_called_with("wss://ws.bitstamp.net")
        client.send_outbound_message.assert_called_once()

    async def test_outbound_message(self):
        """
        Test that outbound messages get sent over the Bitstamp websocket.
        """
        mock_websocket = AsyncMock()
        client = BtcEurCalculatorService()
        client._websocket = mock_websocket

        await client.send_outbound_message("test_message")

        mock_websocket.send.assert_called_with("test_message")

    async def test_socket_messages_read(self):
        """
        Test that our code reads inbound messages from the websocket.
        """
        websocket_response = {
            "timestamp": "546780987",
            "microtimestamp": "546780987109754",
            "bids": [["4000.00", "1.0"], ["4000.05", "0.2 "], ["4000.08", "0.6"]],
            "asks": [["4000.00", "1.0"], ["4000.05", "0.2 "], ["4000.08", "0.6"], ["4000.10", "0.92458373"]],
        }
        client = BtcEurCalculatorService()
        mock_websocket = AsyncMock()
        mock_websocket.__aiter__.return_value = websocket_response
        client._process_inbound_message = AsyncMock()

        await client._message_receive_loop(mock_websocket, Decimal(1.0))

        mock_websocket.__aiter__.assert_called_with()
        client._process_inbound_message.assert_has_calls([call('timestamp', Decimal('1')),
                                                             call('microtimestamp', Decimal('1')),
                                                             call('bids', Decimal('1')),
                                                             call('asks', Decimal('1'))])

    async def test_process_inbound_message_value_equal(self):
        """
        Test case to assert calculation result is equal to expected value.
        """
        websocket_response = {"data": {
            "timestamp": "546780987",
            "microtimestamp": "546780987109754",
            "bids": [["4000.00", "1.0"], ["4000.05", "0.2"], ["4000.08", "0.6"]],
            "asks": [["4000.00", "1.0"], ["4000.05", "0.2"], ["4000.08", "0.6"], ["4000.10", "2.5"]]
        }}
        client = BtcEurCalculatorService()
        json_string = json.dumps(websocket_response)
        res = await client._process_inbound_message(json_string, Decimal(3))
        self.assertAlmostEqual(res, Decimal(12000.18))

    async def test_process_inbound_message_value_not_equal(self):
        """
        Test for not_equal values.
        """
        websocket_response = {"data": {
            "timestamp": "546780987",
            "microtimestamp": "546780987109754",
            "bids": [["4000.00", "1.0"], ["4000.05", "0.2"], ["4000.08", "0.6"]],
            "asks": [["4000.00", "1.0"], ["4000.05", "0.2"], ["4000.08", "0.6"], ["4000.10", "2.5"]]
        }}
        client = BtcEurCalculatorService()

        json_string = json.dumps(websocket_response)
        res = await client._process_inbound_message(json_string, Decimal(3))
        self.assertNotAlmostEqual(res, Decimal(2000.00))

    async def test_process_inbound_message_btc_too_large(self):
        """
        Test for too large btc_ask.
        """
        websocket_response = {"data": {
            "timestamp": "546780987",
            "microtimestamp": "546780987109754",
            "bids": [["4000.00", "1.0"], ["4000.05", "0.2"], ["4000.08", "0.6"]],
            "asks": [["4000.00", "1.0"], ["4000.05", "0.2"], ["4000.08", "0.6"], ["4000.10", "2.5"]]
        }}
        client = BtcEurCalculatorService()

        json_string = json.dumps(websocket_response)
        res = await client._process_inbound_message(json_string, Decimal(5))
        self.assertAlmostEqual(res, "btc too large, total_price not available")

    async def test_process_inbound_message_equal_case2(self):
        """
        Test_equal case_2 for btc_ask at 0.2, an important edge case
        """
        websocket_response = {"data": {
            "timestamp": "546780987",
            "microtimestamp": "546780987109754",
            "bids": [["4000.00", "1.0"], ["4000.05", "0.2"], ["4000.08", "0.6"]],
            "asks": [["4000.00", "1.0"], ["4000.05", "0.2"], ["4000.08", "0.6"], ["4000.10", "2.5"]]
        }}
        client = BtcEurCalculatorService()
        json_string = json.dumps(websocket_response)
        res = await client._process_inbound_message(json_string, Decimal(0.2))
        self.assertAlmostEqual(res, Decimal(800.00))

    async def test_process_inbound_message_equal_case3(self):
        """
        Test_equal case_3 where btc_ask is 1.2
        """
        websocket_response = {"data": {
            "timestamp": "546780987",
            "microtimestamp": "546780987109754",
            "bids": [["4000.00", "1.0"], ["4000.05", "0.2"], ["4000.08", "0.6"]],
            "asks": [["4000.00", "1.0"], ["4000.05", "0.2"], ["4000.08", "0.6"], ["4000.10", "2.5"]]
        }}
        client = BtcEurCalculatorService()
        json_string = json.dumps(websocket_response)
        res = await client._process_inbound_message(json_string, Decimal(1.2))
        self.assertAlmostEqual(res, Decimal(4800.01))
