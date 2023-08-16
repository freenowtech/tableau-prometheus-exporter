import logging
import sys
from unittest.mock import patch

import tableau_prometheus_exporter
from tableau_prometheus_exporter.main import main, parse_args, run, setup_logging

MOCK_CONFIG = {
    "metrics": {"port": 1234},
    "tableau_server_management": {
        "host": "http://test.local",
        "username": "test",
        "password": "test",
    },
}

SAMPLE_CLI_ARGS = ["--config-file", "mock_config.yaml"]

MOCK_CONFIG_CONTENT = """
metrics:
  metrics_port: 1234
tableau_server_management:
  sleep_interval_seconds: 10
"""


def test_parse_args():
    args = parse_args(SAMPLE_CLI_ARGS)
    assert args.configfile == "mock_config.yaml"


def test_setup_logging():
    with patch("logging.basicConfig") as mock_basic_config:
        setup_logging(logging.DEBUG)
        mock_basic_config.assert_called_once_with(
            level=logging.DEBUG,
            stream=sys.stdout,
            format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


def test_main(mocker):
    # Mock functions and objects required for main function
    mocker.patch("builtins.open", mocker.mock_open(read_data=MOCK_CONFIG_CONTENT))
    mocker.patch("yaml.safe_load", return_value=MOCK_CONFIG)
    mocker.patch("tableau_prometheus_exporter.main.setup_logging")
    mocker.patch("tableau_prometheus_exporter.server.Server.start_and_run_forever")

    # Call the main function with sample CLI arguments
    main(SAMPLE_CLI_ARGS)

    # Assertions
    tableau_prometheus_exporter.main.setup_logging.assert_called_once_with(
        logging.NOTSET
    )
    tableau_prometheus_exporter.server.Server.start_and_run_forever.assert_called_once()


def test_run(mocker):
    mocker.patch("sys.argv", ["your_script_name.py"] + SAMPLE_CLI_ARGS)
    mocker.patch("tableau_prometheus_exporter.main.main")
    run()
    tableau_prometheus_exporter.main.main.assert_called_once_with(SAMPLE_CLI_ARGS)
