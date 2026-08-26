from __future__ import annotations

from langgraph.graph import END, StateGraph

from src.agent.nodes import (
    answer_policy_question_node,
    classify_intent_node,
    guardrail_check_node,
    generate_response_node,
)
from src.agent.state import AgentState

_graph = StateGraph(AgentState)
_graph.add_node("guardrail_check", guardrail_check_node)
_graph.add_node("classify_intent", classify_intent_node)
_graph.add_node("answer_policy_question", answer_policy_question_node)
_graph.add_node("generate_response", generate_response_node)
_graph.set_entry_point("guardrail_check")


def _route_from_guardrail(state: AgentState) -> str:
    if state.get("error"):
        return END
    return "classify_intent"


_graph.add_conditional_edges(
    "guardrail_check",
    _route_from_guardrail,
    {
        END: END,
        "classify_intent": "classify_intent",
    },
)


def _route_from_intent(state: AgentState) -> str:
    if state.get("intent") == "policy_question":
        return "answer_policy_question"
    return "generate_response"


_graph.add_conditional_edges(
    "classify_intent",
    _route_from_intent,
    {
        "answer_policy_question": "answer_policy_question",
        "generate_response": "generate_response",
    },
)
_graph.add_edge("answer_policy_question", END)
_graph.add_edge("generate_response", END)
_compiled_graph = _graph.compile()


async def run_agent_graph(state: AgentState) -> AgentState:
    result = await _compiled_graph.ainvoke(state)
    return result
