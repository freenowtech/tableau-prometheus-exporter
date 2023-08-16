"""
Sign in and out of TSM.
"""

import json
import logging
from typing import Dict

import requests
from requests import Session

from tableau_prometheus_exporter.tableau.utils import build_url, process_response

_logger = logging.getLogger(__name__)

HEADERS = {"content-type": "application/json"}


class TableauSession:
    def __init__(self, config: Dict):
        self.host = config["tableau_server_management"]["host"]
        self.username = config["tableau_server_management"]["username"]
        self.password = config["tableau_server_management"]["password"]

    def __enter__(self):
        self.session = self._login()
        return self

    def __exit__(self, *args):
        self._logout()

    def status(self):
        """Returns the status of the server as a JSON object."""
        _logger.info("Getting server status...")

        url = build_url(self.host, "status")
        resp = self.session.get(url, headers=HEADERS, verify=False)
        return process_response(resp)

    def _login(self) -> Session:
        """
        Signs in to TSM.

        :return: A session object that contains an authentication cookie.
        """

        url = build_url(self.host, "login")

        body = {"authentication": {"name": self.username, "password": self.password}}

        session = requests.Session()
        _logger.info("Signing in to TSM...")
        resp = session.post(url, data=json.dumps(body), headers=HEADERS, verify=False)

        process_response(resp)

        return session

    def _logout(self) -> None:
        """
        Signs out of TSM.

        :return: None
        """

        url = build_url(self.host, "logout")

        _logger.info("Signing out of TSM...")
        self.session.post(url, headers=HEADERS, verify=False)
