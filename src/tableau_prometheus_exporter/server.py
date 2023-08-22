import logging
import time
from typing import Dict

from prometheus_client import Gauge, start_http_server

from tableau_prometheus_exporter.tableau.session import TableauSession

_logger = logging.getLogger(__name__)

DEFAULT_SLEEP_INTERVAL_SECONDS = 30

DEFAULT_METRICS_PORT = 8000

GAUGE_TABLEAU_SERVICE_STATUS: Gauge = Gauge(
    name="tableau_service_status",
    documentation="description",
    labelnames=[
        "node_id",
        "service_name",
        "instance_id",
        "status",
        "state",
    ],
)


class Server:
    def __init__(self, config: Dict):
        self.tsm_config = config["tableau_server_management"]
        self.metrics_port = config["metrics"].get("metrics_port", DEFAULT_METRICS_PORT)
        self.sleep_interval = self.tsm_config.get(
            "sleep_interval_seconds", DEFAULT_SLEEP_INTERVAL_SECONDS
        )
        self.bad_statuses = [
            s.replace(" ", "").lower() for s in self.tsm_config.get("bad_statuses", [])
        ]

    RUNNING = True

    def parse(self, status: Dict) -> None:
        """
        Parse Tableau Server Management Status and export as Prometheus Gauge

        :return: None
        """

        GAUGE_TABLEAU_SERVICE_STATUS.clear()

        for node in status.get("clusterStatus", {}).get("nodes", []):
            for service in node.get("services", []):
                for instance in service.get("instances", []):
                    value = (
                        0
                        if instance.get("processStatus", "").replace(" ", "").lower()
                        in self.bad_statuses
                        else 1
                    )
                    GAUGE_TABLEAU_SERVICE_STATUS.labels(
                        node.get("nodeId", ""),
                        service.get("serviceName", ""),
                        instance.get("instanceId", ""),
                        instance.get("processStatus", ""),
                        instance.get("currentDeploymentState", ""),
                    ).set(value)

    def start_and_run_forever(self) -> None:
        """
        Start up the server to expose the metrics.
        Forwards it from the Tableau system info endpoints to Prometheus
        Runs until interrupted.

        :return: None
        """
        _logger.info("Starting Metrics Server...")

        start_http_server(port=self.metrics_port)
        while self.RUNNING:
            with TableauSession(self.tsm_config) as session:
                status = session.status()
                self.parse(status)

            time.sleep(self.sleep_interval)
