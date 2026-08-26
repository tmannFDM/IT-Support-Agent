from __future__ import annotations

import re
from copy import deepcopy

TicketStoreEntry = dict[str, str]

_TICKET_ID_PATTERN = re.compile(r"^TKT-(\d{4})$")

_SEEDED_TICKETS: dict[str, TicketStoreEntry] = {
    "TKT-1001": {
        "ticket_id": "TKT-1001",
        "category": "VPN",
        "priority": "medium",
        "status": "open",
        "summary": "VPN access not connecting from home network",
    },
    "TKT-1002": {
        "ticket_id": "TKT-1002",
        "category": "Access",
        "priority": "high",
        "status": "open",
        "summary": "Admin portal access denied after role change",
    },
    "TKT-1003": {
        "ticket_id": "TKT-1003",
        "category": "Hardware",
        "priority": "low",
        "status": "open",
        "summary": "Laptop docking station flickers intermittently",
    },
}

TICKET_STORE: dict[str, TicketStoreEntry] = deepcopy(_SEEDED_TICKETS)


def reset_ticket_store() -> None:
    TICKET_STORE.clear()
    TICKET_STORE.update(deepcopy(_SEEDED_TICKETS))


def list_ticket_ids() -> list[str]:
    return sorted(TICKET_STORE.keys())


def list_tickets() -> list[TicketStoreEntry]:
    return [TICKET_STORE[ticket_id].copy() for ticket_id in list_ticket_ids()]


def get_ticket(ticket_id: str) -> TicketStoreEntry | None:
    normalized = ticket_id.upper()
    ticket = TICKET_STORE.get(normalized)
    if ticket is None:
        return None
    return ticket.copy()


def add_ticket(ticket: TicketStoreEntry) -> None:
    ticket_id = ticket["ticket_id"].upper()
    if ticket_id in TICKET_STORE:
        raise ValueError(f"Ticket {ticket_id} already exists")
    TICKET_STORE[ticket_id] = {**ticket, "ticket_id": ticket_id}


def generate_next_ticket_id() -> str:
    seeded_floor = 1001
    parsed_ids: list[int] = []

    for ticket_id in TICKET_STORE:
        match = _TICKET_ID_PATTERN.match(ticket_id)
        if not match:
            continue
        parsed_ids.append(int(match.group(1)))

    candidate = max(parsed_ids + [seeded_floor]) + 1
    while f"TKT-{candidate:04d}" in TICKET_STORE:
        candidate += 1

    return f"TKT-{candidate:04d}"
