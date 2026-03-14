"""Registry for available MCP servers."""

from __future__ import annotations

from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from mcp_sre_agent.servers.cluster import create_cluster_server

ServerFactory = Callable[[], FastMCP]

SERVER_FACTORIES: dict[str, ServerFactory] = {
    "cluster": create_cluster_server,
}


def available_servers() -> tuple[str, ...]:
    """Return all registered server names."""

    return tuple(sorted(SERVER_FACTORIES))


def create_server(server_name: str) -> FastMCP:
    """Build a server by name."""

    try:
        factory = SERVER_FACTORIES[server_name]
    except KeyError as exc:
        names = ", ".join(available_servers())
        raise ValueError(f"Unknown server '{server_name}'. Available servers: {names}") from exc

    return factory()
