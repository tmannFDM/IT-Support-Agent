from __future__ import annotations

from src.schemas.ticket_create import TicketCreateRequest, TicketCreateResponse
from src.tools.ticket_store import add_ticket, generate_next_ticket_id


async def create_ticket(category: str, priority: str, summary: str) -> TicketCreateResponse:
    request = TicketCreateRequest(category=category, priority=priority, summary=summary)

    ticket_id = generate_next_ticket_id()
    ticket = {
        "ticket_id": ticket_id,
        "category": request.category,
        "priority": request.priority,
        "status": "open",
        "summary": request.summary,
    }
    add_ticket(ticket)

    return TicketCreateResponse(
        ticket_id=ticket_id,
        category=request.category,
        priority=request.priority,
        status="open",
        summary=request.summary,
    )
