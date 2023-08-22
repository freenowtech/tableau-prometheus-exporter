import time
from unittest.mock import PropertyMock

import tableau_prometheus_exporter
from tableau_prometheus_exporter.server import DEFAULT_SLEEP_INTERVAL_SECONDS, Server

MOCK_TSM_CONFIG = {
    "host": "http://test.local",
    "username": "test",
    "password": "test",
    "bad_statuses": ["error", "not available"],
}

MOCK_CONFIG = {
    "metrics": {"port": 1234},
    "tableau_server_management": MOCK_TSM_CONFIG,
}

MOCK_STATUS = {
    "clusterStatus": {
        "nodes": [
            {
                "nodeId": "node1",
                "services": [
                    {
                        "serviceName": "service1",
                        "instances": [
                            {
                                "instanceId": "instance1",
                                "processStatus": "running",
                                "currentDeploymentState": "enabled",
                            },
                            {
                                "instanceId": "instance2",
                                "processStatus": "error",
                                "currentDeploymentState": "enabled",
                            },
                            {
                                "instanceId": "instance3",
                                "processStatus": "NotAvailable",
                                "currentDeploymentState": "disabled",
                            },
                        ],
                    }
                ],
            }
        ]
    }
}


def test_start_and_run_forever(mocker):
    mock_tableau_session = mocker.patch(
        "tableau_prometheus_exporter.server.TableauSession"
    )
    mock_manager = mock_tableau_session.return_value.__enter__.return_value
    mock_manager.status.return_value = {}
    mocker.patch("requests.Session", return_value=mocker.MagicMock())
    mocker.patch("tableau_prometheus_exporter.server.start_http_server")
    mocker.patch("time.sleep")

    server = Server(MOCK_CONFIG)
    assert server.RUNNING

    tableau_prometheus_exporter.server.Server.RUNNING = PropertyMock(
        side_effect=[True, False]
    )

    server.start_and_run_forever()

    # Assertions
    tableau_prometheus_exporter.server.start_http_server.assert_called_once()
    mock_tableau_session.assert_called_once_with(MOCK_TSM_CONFIG)
    mock_manager.status.assert_called_once()
    time.sleep.assert_called_with(DEFAULT_SLEEP_INTERVAL_SECONDS)


def test_parse_method():
    Server(MOCK_CONFIG).parse(MOCK_STATUS)

    metric_samples = list(
        tableau_prometheus_exporter.server.GAUGE_TABLEAU_SERVICE_STATUS.collect()
    )[0].samples

    assert len(metric_samples) == 3
    sample = metric_samples[0]

    assert sample.name == "tableau_service_status"
    assert sample.labels == {
        "node_id": "node1",
        "service_name": "service1",
        "instance_id": "instance1",
        "status": "running",
        "state": "enabled",
    }
    assert sample.value == 1.0

    sample = metric_samples[1]

    assert sample.name == "tableau_service_status"
    assert sample.labels == {
        "node_id": "node1",
        "service_name": "service1",
        "instance_id": "instance2",
        "status": "error",
        "state": "enabled",
    }
    assert sample.value == 0.0

    sample = metric_samples[2]

    assert sample.name == "tableau_service_status"
    assert sample.labels == {
        "node_id": "node1",
        "service_name": "service1",
        "instance_id": "instance3",
        "status": "NotAvailable",
        "state": "disabled",
    }
    assert sample.value == 0.0
