import logging
from fastapi import FastAPI
from pydantic import BaseModel
from decimal import Decimal
from demo_api.btc_eur_calculator_service import BtcEurCalculatorService
import sys
import asyncio
if sys.platform == "win32" and (3, 8, 0) <= sys.version_info < (3, 9, 0):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI(title="Bitstack Demo API")

log = logging.getLogger(__name__)


class RequestModel(BaseModel):
    amount: Decimal


@app.get("/")
def root_get():
    return {"description": "Hello coder!"}


@app.post("/btceur")
async def btc_eur_price(btc_ask: RequestModel):
    try:
        if btc_ask.amount <= Decimal(0):
            return 0
    except ValueError:
        log.error()
        return "Please provide a valid btc ask"
    btc_eur = BtcEurCalculatorService()
    resp = await btc_eur.start(btc_ask.amount)
    result = resp.pop(0)
    return result
    # return calculate_btceur_price(btc_ask.amount)
    # return btc_eurhandlers
