import logging
from fastapi import FastAPI
from pydantic import BaseModel
from decimal import Decimal
from demo_api.btc_eur_calculator_service import calculate_btceur_price
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

    return await calculate_btceur_price(btc_ask.amount)

