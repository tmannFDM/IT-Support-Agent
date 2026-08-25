from fastmcp import FastMCP

from src.schemas.ticket_status import TicketStatusRequest
from src.tools.ticket_store import get_ticket_status

mcp = FastMCP(name="ticket-status-tools")


@mcp.tool()
def ticket_status_lookup(ticket_id: str) -> dict[str, str] | None:
    request = TicketStatusRequest(ticket_id=ticket_id)
    response = get_ticket_status(request.ticket_id)
    if response is None:
        return None
    return response.model_dump()
