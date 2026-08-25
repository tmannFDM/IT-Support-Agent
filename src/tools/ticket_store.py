from src.schemas.ticket_status import TicketStatusResponse

_SAMPLE_TICKETS: dict[str, dict[str, str]] = {
    "TKT-1001": {
        "status": "open",
        "priority": "high",
        "summary": "VPN access issue under investigation.",
        "last_updated": "2026-08-25T09:15:00Z",
    },
    "TKT-1002": {
        "status": "in_progress",
        "priority": "medium",
        "summary": "Email sync intermittent on mobile device.",
        "last_updated": "2026-08-25T11:40:00Z",
    },
    "TKT-1003": {
        "status": "resolved",
        "priority": "low",
        "summary": "Printer driver update applied successfully.",
        "last_updated": "2026-08-24T16:05:00Z",
    },
    "TKT-1004": {
        "status": "closed",
        "priority": "critical",
        "summary": "Production outage mitigated and postmortem completed.",
        "last_updated": "2026-08-23T20:30:00Z",
    },
}


def get_ticket_status(ticket_id: str) -> TicketStatusResponse | None:
    record = _SAMPLE_TICKETS.get(ticket_id)
    if record is None:
        return None
    return TicketStatusResponse(ticket_id=ticket_id, **record)
