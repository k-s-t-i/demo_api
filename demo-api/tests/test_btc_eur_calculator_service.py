import unittest
from unittest.mock import patch
from decimal import Decimal
from demo_api.btc_eur_calculator_service import calculate_btceur_price
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s')
logging.info("Just like that!")
#> 2019-02-17 11:40:38,254 :: INFO :: Just like that!
websocket_response = {
    "timestamp": "1642474746",
    "microtimestamp": "1642474746109754",
    "bids": [["4000.00", "1.0"], ["4000.05", "0.2 "], ["4000.08", "0.6"]],
    "asks": [["4000.00", "1.0"], ["4000.05", "0.2 "], ["4000.08", "0.6"],["4000.10", "0.92458373"]],
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

class TestBtcEurCalculatorService(unittest.TestCase):
@patch("websockets.connect", side_effect=mocked_websocket_response)

def test_validate_equal(self):
    self.assertEqual(calculate_btceur_price(3.0), {'btc_ask': 12000.18})
    self.assertEqual(calculate_btceur_price(1.0), {'btc_ask': 4000.00})
    self.assertEqual(calculate_btceur_price(1.2), {'btc_ask': 4000.81})
def test_too_large_btc(self):
    self.assertEqual(calculate_btceur_price(10), {'btc_ask': "btc too large, total_price not available"})
def test_validate_not_equal(self):
    self.assertNotEqual(calculate_btceur_price(3), {'btc_ask': 2000.00})
def test_negative_or_zero_btc_ask(self):
    self.assertRaises(ValueError,calculate_btceur_price(0), 0)
    self.assertRaises(ValueError,calculate_btceur_price(-1), -1)
