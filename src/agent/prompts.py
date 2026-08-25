CLASSIFICATION_PROMPT = (
    "Classify the user message into exactly one label: "
    "policy_question, action_request, direct_response, escalation, blocked."
)

DIRECT_RESPONSE_SYSTEM_PROMPT = (
    "You are an IT support assistant handling general conversational questions. "
    "Provide concise, helpful responses for non-policy requests."
)

LLM_API_URL_ENV = "LLM_API_URL"
LLM_API_KEY_ENV = "LLM_API_KEY"
LLM_MODEL_ENV = "LLM_MODEL"
LLM_DEFAULT_API_URL = "https://api.openai.com/v1/chat/completions"
LLM_DEFAULT_MODEL = "gpt-4o-mini"
PLACEHOLDER_UNSUPPORTED = "This type of request isn't supported yet."
