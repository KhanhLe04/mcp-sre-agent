"""CLI entrypoint for running MCP servers from this package."""

from __future__ import annotations

import argparse

from mcp_sre_agent.adapters.kubernetes import planned_connection_info
from mcp_sre_agent.app.config import get_settings
from mcp_sre_agent.app.logging import configure_logging, log_server_start
from mcp_sre_agent.servers.registry import available_servers, create_server


def build_parser() -> argparse.ArgumentParser:
    """Create the top-level CLI parser."""

    settings = get_settings()
    parser = argparse.ArgumentParser(description="Run MCP servers for SRE workflows.")
    parser.add_argument(
        "server",
        nargs="?",
        default=settings.default_server,
        choices=available_servers(),
        help="The server to run.",
    )
    parser.add_argument(
        "--transport",
        choices=("stdio", "sse", "streamable-http"),
        default=settings.default_transport,
        help="Transport to expose for the selected MCP server.",
    )
    return parser


def main() -> None:
    """Run the selected MCP server."""

    settings = get_settings()
    configure_logging(settings)
    args = build_parser().parse_args()
    kube_info = planned_connection_info() if args.server == "cluster" else None
    log_server_start(
        settings=settings,
        server_name=args.server,
        transport=args.transport,
        kube=kube_info,
    )
    server = create_server(args.server)
    server.run(transport=args.transport)
