from datetime import timedelta
import hypothesis
import requests
import schemathesis
from starlette.testclient import TestClient
from demo_api.app import app

schemathesis.fixups.install(["fast_api"])
schema = schemathesis.from_asgi("/openapi.json", app)

client = TestClient(app)


# @schema.parametrize()
# @hypothesis.settings(
#     suppress_health_check=[
#         hypothesis.HealthCheck.filter_too_much,
#         hypothesis.HealthCheck.too_slow,
#     ]
# )
# def test_fuzz(case):
#     response: requests.Response = case.call(
#         session=client,
#     )
#     assert response.elapsed < timedelta(milliseconds=500)
#     case.validate_response(response)

def test_btceur_calculator_endpoint_success():
    request_json = {"amount": 0.00011}
    response = client.post("/btceur", json=request_json)
    assert response.status_code == 200


def test_negative_value_case():
    request_json = {"amount": -1}
    response = client.post("/btceur", json=request_json)
    assert response.status_code == 200


def test_zero_value_case():
    request_json = {"amount": 0}
    response = client.post("/btceur", json=request_json)
    assert response.status_code == 200


def test_url_not_found():
    request_json = {"amount": 6}
    response = client.post("/btceury", json=request_json)
    assert response.status_code == 404
