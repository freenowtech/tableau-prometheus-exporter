from unittest.mock import Mock

from tableau_prometheus_exporter.tableau.utils import (
    build_url,
    format_server_address,
    process_response,
)


def test_format_server_address():
    server = "test.local"
    formatted_server = format_server_address(server)
    assert formatted_server == "https://test.local:8850"

    server_with_http = "http://test.local"
    formatted_server_with_http = format_server_address(server_with_http)
    assert formatted_server_with_http == "https://test.local:8850"

    server_with_port = "test.local:1234"
    formatted_server_with_port = format_server_address(server_with_port)
    assert formatted_server_with_port == "https://test.local:1234"

    server_with_http_and_port = "http://test.local:1234"
    formatted_server_with_http_and_port = format_server_address(
        server_with_http_and_port
    )
    assert formatted_server_with_http_and_port == "https://test.local:1234"


def test_build_url():
    server = "https://test.local:8850"
    endpoint = "backup"
    params = ["writePath=filename"]
    url = build_url(server, endpoint, params)
    expected_url = "https://test.local:8850/api/0.5/backup?writePath=filename"
    assert url == expected_url


def test_process_response_success():
    resp = Mock(status_code=200, text='{"key": "value"}')
    result = process_response(resp)
    assert result == {"key": "value"}

    resp_no_content = Mock(status_code=204)
    result_no_content = process_response(resp_no_content)
    assert result_no_content == {}


def test_process_response_error():
    resp_error = Mock(status_code=400, text="Bad Request")
    result = process_response(resp_error)
    assert result == {}
