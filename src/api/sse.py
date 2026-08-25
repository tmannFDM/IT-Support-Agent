from src.schemas.chat import ChatStreamEvent


def format_sse(event: ChatStreamEvent) -> str:
    return f"data: {event.model_dump_json()}\n\n"
