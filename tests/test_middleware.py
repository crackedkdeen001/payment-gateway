from fastapi.testclient import TestClient
from fastapi import status

from src.main import app
from src.exceptions import DIFFERENT_PARAMS_WITH_SAME_IDEMPOTENCY_KEY, IDEMPOTENCY_KEY_TOO_LONG

client = TestClient(app)

def test_same_request_with_same_idempotency_key_returns_an_idempotent_response_on_subsequent_requests(test_postgresql, data, idempotency_header):
    response = client.post("/authorize", json=data, headers=idempotency_header)
        
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == data
    
    idempotent_response = client.post("/authorize", json=data, headers=idempotency_header)
    
    assert idempotent_response.status_code == status.HTTP_200_OK
    assert idempotent_response.json() == data
    assert idempotent_response.headers["x-idempotent-replayed"] == "true"

    second_idempotent_response = client.post("/authorize", json=data, headers=idempotency_header)

    assert second_idempotent_response.status_code == status.HTTP_200_OK
    assert second_idempotent_response.json() == data
    assert second_idempotent_response.headers["x-idempotent-replayed"] == "true"


def test_no_idempotency_key_in_request_returns_an_error(test_postgresql, data):
    response = client.post("/authorize", json=data)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json()["message"] ==  "Field: ('header', 'X-Idempotency-Key'), Error: Field required"
    
def test_same_idempotency_key_with_different_request_parameters_returns_an_error(test_postgresql, data, idempotency_header):
    valid_response = client.post("/authorize", json=data, headers=idempotency_header)
    
    assert valid_response.status_code == status.HTTP_200_OK
    
    data["amount_in_cents"] = 400
    
    invalid_response = client.post("/authorize", json=data, headers=idempotency_header)
    
    assert invalid_response.status_code == status.HTTP_409_CONFLICT
    assert invalid_response.json() == {"status":"error", "message":DIFFERENT_PARAMS_WITH_SAME_IDEMPOTENCY_KEY}
    

def test_request_with_too_long_idempotency_key_should_return_an_error(test_postgresql, data) :
    idempotency_header = {"X-Idempotency-Key": "a"*101} # idempotency key should be at most 100 chars long
    
    response = client.post("/authorize", json=data, headers=idempotency_header)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["message"] == IDEMPOTENCY_KEY_TOO_LONG