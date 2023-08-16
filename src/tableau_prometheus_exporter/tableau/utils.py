import json
import logging
import re

import requests
from requests import Response
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Do not verify the SSL certificate because this is a self-signed certificate.
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# The TSM API version.
VERSION = "0.5"

_logger = logging.getLogger(__name__)


def format_server_address(server):
    """Return a formatted server string."""

    # If http is specified explicitly, switch to https
    http_re = re.compile("http://", re.IGNORECASE)
    if re.search(http_re, server):
        _logger.warning("TSM requires HTTPS. Updating the request URL.")
        server = http_re.sub("https://", server)

    # If neither http nor https was specified, insert https
    if not re.search("https://", server):
        server = "https://{0}".format(server)

    # If no port number was specified, use default
    if not re.search(":[.0-9]", server):
        _logger.warning("No port number specified. Using 8850 as the default.")
        server = "{0}:8850".format(server)

    return server


def build_url(server, endpoint, params=None):
    """Returns a formatted request URL.

    Example: https://your-server:8850/api/1.0/backup?writePath=filename
    """
    query_string = ""

    if params is not None:
        # Returns query params with '&' as a delimiter.
        query_string = "?" + "&".join(params)

    url = f"{server}/api/{VERSION}/{endpoint}{query_string}"
    return url


def process_response(resp: Response):
    """
    For successful 2xx response codes, process the response. Otherwise, raise an error.
    """
    resp.raise_for_status()

    try:
        return json.loads(resp.text)
    except Exception:
        _logger.warning(
            f"Not a valid json. Status code <{resp.status_code}>."
            f"Error: <{resp.text}>"
        )

    return {}
