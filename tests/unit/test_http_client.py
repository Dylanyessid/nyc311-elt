import httpx
import pytest
import logging
from nyc311_elt.http_client import get_with_retries


def test_reintenta_en_503_y_termina_con_exito():
    llamadas = []
    respuestas = [
        httpx.Response(503),
        httpx.Response(503),
        httpx.Response(200, json=[{"unique_key": "1"}]),
    ]
    

    def handler(request: httpx.Request) -> httpx.Response:
        llamadas.append(request)
        return respuestas[len(llamadas) - 1]

    client = httpx.Client(transport=httpx.MockTransport(handler))

    resultado = get_with_retries(
        client, "https://fake.test/data.json", {}, backoff_base=0
    )

    assert resultado == [{"unique_key": "1"}]
    assert len(llamadas) == 3

def test_not_retry_at_400_code():
    llamadas = []
    respuestas = [
        httpx.Response(400),
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        llamadas.append(request)
        return respuestas[len(llamadas) - 1]

    client = httpx.Client(transport=httpx.MockTransport(handler))

    with pytest.raises(httpx.HTTPStatusError):
        get_with_retries(client, "https://fake.test/data.json", {}, backoff_base=0)

    assert len(llamadas) == 1


def test_reintenta_en_error_de_red_y_termina_con_exito():
    llamadas = []

    def handler(request: httpx.Request) -> httpx.Response:
        llamadas.append(request)
        if len(llamadas) == 1:
            raise httpx.ConnectError("sin red", request=request)
        return httpx.Response(200, json=[{"unique_key": "1"}])

    client = httpx.Client(transport=httpx.MockTransport(handler))

    resultado = get_with_retries(
        client, "https://fake.test/data.json", {}, backoff_base=0
    )

    assert resultado == [{"unique_key": "1"}]
    assert len(llamadas) == 2