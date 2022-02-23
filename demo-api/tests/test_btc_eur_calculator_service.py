from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch
from demo_api.btc_eur_calculator_service import calculate_btceur_price

websocket_response = {
    "timestamp": "546780987",
    "microtimestamp": "546780987109754",
    "bids": [["4000.00", "1.0"], ["4000.05", "0.2 "], ["4000.08", "0.6"]],
    "asks": [["4000.00", "1.0"], ["4000.05", "0.2 "], ["4000.08", "0.6"], ["4000.10", "0.92458373"]],
}


def mocked_websocket_response(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data):
            self.json_data = json_data

        def json(self):
            return self.json_data

    if args[0]:
        return MockResponse(websocket_response)

    return MockResponse(None)


class TestBtcEurCalculatorService(IsolatedAsyncioTestCase):
    @patch("websockets.connect", side_effect=mocked_websocket_response)
    async def test_validate_equal(self):
        self.assertEqual(await calculate_btceur_price(3.0), {'btc_ask': 12000.18})
        self.assertEqual(await calculate_btceur_price(1.0), {'btc_ask': 4000.00})
        self.assertEqual(await calculate_btceur_price(1.2), {'btc_ask': 4000.81})

    async def test_too_large_btc(self):
        self.assertEqual(await calculate_btceur_price(10), {'btc_ask': "btc too large, total_price not available"})

    async def test_validate_not_equal(self):
        self.assertNotEqual(await calculate_btceur_price(3), {'btc_ask': 2000.00})

    async def test_negative_or_zero_btc_ask(self):
        self.assertRaises(ValueError, await calculate_btceur_price(0), 0)
        self.assertRaises(ValueError, await calculate_btceur_price(-1), -1)
