from fastapi.testclient import TestClient
from fastapi import status

from src.main import app
from src.exceptions import DIFFERENT_PARAMS_WITH_SAME_IDEMPOTENCY_KEY

client = TestClient(app)

def test_same_request_with_same_idempotency_key_returns_an_idempotent_response_on_subsequent_requests(test_postgresql, data):
    headers = {"X-Idempotency-Key":"28323232323"}
    response = client.post("/authorize", json=data, headers=headers)
        
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == data
    
    idempotent_response = client.post("/authorize", json=data, headers=headers)
    
    assert idempotent_response.status_code == status.HTTP_200_OK
    assert idempotent_response.json() == data
    assert idempotent_response.headers["x-idempotent-replayed"] == "true"

    second_idempotent_response = client.post("/authorize", json=data, headers=headers)

    assert second_idempotent_response.status_code == status.HTTP_200_OK
    assert second_idempotent_response.json() == data
    assert second_idempotent_response.headers["x-idempotent-replayed"] == "true"


def test_no_idempotency_key_in_request_returns_an_error(test_postgresql, data):
    response = client.post("/authorize", json=data)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json()["message"] ==  "Field: ('header', 'X-Idempotency-Key'), Error: Field required"
    
def test_same_idempotency_key_with_different_request_parameters_returns_an_error(test_postgresql, data):
    header = {"X-Idempotency-Key":"28323232323"}
    valid_response = client.post("/authorize", json=data, headers=header)
    
    assert valid_response.status_code == status.HTTP_200_OK
    
    diff_req_params = {
        "number": "292929", # card number is different
        "cvv": "231",
        "expiry_month": "12",
        "expiry_year": "2028"
    }
    
    invalid_response = client.post("/authorize", json=diff_req_params, headers=header)
    
    assert invalid_response.status_code == status.HTTP_409_CONFLICT
    assert invalid_response.json() == {"status":"error", "message":DIFFERENT_PARAMS_WITH_SAME_IDEMPOTENCY_KEY}
    
 