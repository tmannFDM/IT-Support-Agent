from __future__ import annotations

from langgraph.graph import END, StateGraph

from src.agent.nodes import classify_intent_node, generate_response_node
from src.agent.state import AgentState

_graph = StateGraph(AgentState)
_graph.add_node("classify_intent", classify_intent_node)
_graph.add_node("generate_response", generate_response_node)
_graph.set_entry_point("classify_intent")
_graph.add_edge("classify_intent", "generate_response")
_graph.add_edge("generate_response", END)
_compiled_graph = _graph.compile()


async def run_agent_graph(state: AgentState) -> AgentState:
    result = await _compiled_graph.ainvoke(state)
    return result
