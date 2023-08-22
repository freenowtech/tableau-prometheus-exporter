import pytest

from tableau_prometheus_exporter.tableau.session import TableauSession


class MockResponse:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text
        self.raise_for_status = lambda: None


@pytest.fixture
def mock_config():
    return {
        "host": "https://test.local:8850",
        "username": "test",
        "password": "passwd",
    }


def test_tableau_session_init(mock_config):
    session = TableauSession(mock_config)
    assert session.host == "https://test.local:8850"
    assert session.username == "test"
    assert session.password == "passwd"


def test_tableau_session_login_logout(mocker, mock_config):
    mock_session = mocker.MagicMock()
    mocker.patch("requests.Session", return_value=mock_session)

    with TableauSession(mock_config) as session:
        mock_session.post.assert_called_with(
            "https://test.local:8850/api/0.5/login",
            data='{"authentication": {"name": "test", "password": "passwd"}}',
            headers={"content-type": "application/json"},
            verify=False,
        )
        assert session.host == "https://test.local:8850"
        assert session.username == "test"
        assert session.password == "passwd"

    mock_session.post.assert_called_with(
        "https://test.local:8850/api/0.5/logout",
        headers={"content-type": "application/json"},
        verify=False,
    )


def test_tableau_session_status(mocker, mock_config):
    mock_session = mocker.MagicMock()
    mocker.patch("requests.Session", return_value=mock_session)
    mock_response = MockResponse(200, '{"status": "OK"}')
    mock_session.get.return_value = mock_response

    with TableauSession(mock_config) as session:
        status = session.status()
        assert status == {"status": "OK"}

    mock_session.get.assert_called_once()
    assert mock_session.get.call_args[0][0] == "https://test.local:8850/api/0.5/status"
