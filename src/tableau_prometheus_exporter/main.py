import argparse
import logging
import sys

import yaml

from tableau_prometheus_exporter import __version__
from tableau_prometheus_exporter.server import Server


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description="Tableau Server Manager Prometheus Exporter"
    )
    parser.add_argument(
        "--config-file",
        type=str,
        dest="configfile",
        help="Configuration file. For an example check /samples/config.yaml.template",
        default=None,
        required=True,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"tableau-prometheus-exporter {__version__}",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    log_format = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel,
        stream=sys.stdout,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main(args):
    """Wrapper allowing :func:`fib` to be called with string arguments in a CLI fashion

    Instead of returning the value from :func:`fib`, it prints the result to the
    ``stdout`` in a nicely formatted message.

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--verbose", "42"]``).
    """
    args = parse_args(args)
    setup_logging(args.loglevel if args.loglevel else logging.NOTSET)
    with open(args.configfile, "r") as conf:
        config = yaml.safe_load(conf)

    Server(config).start_and_run_forever()


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
