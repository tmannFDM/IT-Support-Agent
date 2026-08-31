from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MEMORY_FILE_PATH = Path(__file__).with_name("user_memory.json")


def _ensure_store_file() -> None:
    MEMORY_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if MEMORY_FILE_PATH.exists():
        return
    MEMORY_FILE_PATH.write_text(json.dumps({"records": {}}, indent=2), encoding="utf-8")


def _read_store() -> dict[str, Any]:
    _ensure_store_file()
    raw = MEMORY_FILE_PATH.read_text(encoding="utf-8").strip()
    if not raw:
        return {"records": {}}

    payload = json.loads(raw)
    if not isinstance(payload, dict):
        return {"records": {}}

    records = payload.get("records")
    if not isinstance(records, dict):
        return {"records": {}}

    return {"records": records}


def _write_store(store: dict[str, Any]) -> None:
    _ensure_store_file()
    MEMORY_FILE_PATH.write_text(json.dumps(store, indent=2, sort_keys=True), encoding="utf-8")


def load_user_memory_records() -> dict[str, dict[str, Any]]:
    store = _read_store()
    records = store.get("records", {})
    if not isinstance(records, dict):
        return {}
    return records


def get_user_memory_facts(user_id: str) -> dict[str, str]:
    records = load_user_memory_records()
    record = records.get(user_id, {})
    if not isinstance(record, dict):
        return {}

    facts = record.get("facts", {})
    if not isinstance(facts, dict):
        return {}

    allowed = {"preferred_device_type", "office_region", "timezone"}
    return {k: v for k, v in facts.items() if k in allowed and isinstance(v, str)}


def upsert_user_memory_facts(user_id: str, facts: dict[str, str]) -> dict[str, str]:
    allowed = {"preferred_device_type", "office_region", "timezone"}
    sanitized = {k: v for k, v in facts.items() if k in allowed and isinstance(v, str) and v}

    if not sanitized:
        return get_user_memory_facts(user_id)

    store = _read_store()
    records = store.setdefault("records", {})
    if not isinstance(records, dict):
        records = {}
        store["records"] = records

    current = records.get(user_id)
    if not isinstance(current, dict):
        current = {}

    current_facts = current.get("facts", {})
    if not isinstance(current_facts, dict):
        current_facts = {}

    current_facts.update(sanitized)
    current["facts"] = current_facts
    current["updated_at"] = datetime.now(timezone.utc).isoformat()
    records[user_id] = current

    _write_store(store)
    return {k: v for k, v in current_facts.items() if k in allowed and isinstance(v, str)}


def reset_user_memory_store() -> None:
    _write_store({"records": {}})
