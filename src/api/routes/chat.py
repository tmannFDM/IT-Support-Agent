import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from src.agent.graph import run_agent_graph
from src.api.sse import format_sse
from src.schemas.chat import ChatRequest, ChatStreamEvent

router = APIRouter(prefix="/chat", tags=["chat"])


async def generate_chat_events(
    payload: ChatRequest,
    is_disconnected: Callable[[], Awaitable[bool]],
    graph_runner: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]] = run_agent_graph,
) -> AsyncIterator[str]:
    state = await graph_runner(
        {
            "user_id": payload.user_id,
            "session_id": payload.session_id,
            "message": payload.message,
        }
    )

    intent = ChatStreamEvent(event_type="intent", data=state["intent"])

    if await is_disconnected():
        return

    yield format_sse(intent)
    await asyncio.sleep(0)

    if await is_disconnected():
        return

    if "error" in state:
        error_event = ChatStreamEvent(event_type="error", data=state["error"])
        yield format_sse(error_event)
        return

    response_text = state.get("response", "")
    token_parts = response_text.split() if response_text.strip() else [response_text]

    for index, part in enumerate(token_parts):
        token = ChatStreamEvent(event_type="token", data=part if part else response_text)
        yield format_sse(token)
        if index < len(token_parts) - 1:
            await asyncio.sleep(0)

        if await is_disconnected():
            return

    done = ChatStreamEvent(event_type="done", data="")
    yield format_sse(done)


@router.post("/stream")
async def stream_chat(http_request: Request, payload: ChatRequest) -> StreamingResponse:
    async def stream() -> AsyncIterator[str]:
        try:
            async for event in generate_chat_events(payload, http_request.is_disconnected):
                yield event
        except asyncio.CancelledError:
            return

    return StreamingResponse(stream(), media_type="text/event-stream")
