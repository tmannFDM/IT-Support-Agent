CLASSIFICATION_PROMPT = (
    "Classify the user message into exactly one label: "
    "policy_question, action_request, direct_response, escalation, blocked."
)

DIRECT_RESPONSE_SYSTEM_PROMPT = (
    "You are an IT support assistant handling general conversational questions. "
    "Provide concise, helpful responses for non-policy requests."
)

LLM_API_URL_ENV = "OLLAMA_API_URL"
LLM_MODEL_ENV = "OLLAMA_MODEL"
LLM_DEFAULT_API_URL = "http://localhost:11434/api/chat"
LLM_DEFAULT_MODEL = "llama3.2:3b"
PLACEHOLDER_UNSUPPORTED = "This type of request isn't supported yet."

PROMPT_INJECTION_ERROR_CODE = "ERR-PROMPT-INJECTION-BLOCKED"
PROMPT_INJECTION_ERROR_MESSAGE = "Request blocked for safety."

POLICY_FALLBACK_TEXT = "I don't have information on that policy."

POLICY_GROUNDED_SYSTEM_PROMPT = (
    "You are an IT support policy assistant. Answer only using the provided context. "
    "If the context does not contain the answer, say you do not have that information. "
    "Do not invent details."
)
