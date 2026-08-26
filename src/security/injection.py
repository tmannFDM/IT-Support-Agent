from __future__ import annotations

from dataclasses import dataclass
import re

INJECTION_PATTERNS = (
    "ignore previous instructions",
    "ignore all previous",
    "ignore the above",
    "disregard previous instructions",
    "disregard the above",
    "reveal your system prompt",
    "show me your system prompt",
    "what are your instructions",
    "repeat your instructions",
    "print your prompt",
    "you are now",
    "act as if you",
    "act as a different",
    "act as an unrestricted",
    "you must act as"
    "pretend you are",
    "pretend to be",
    "from now on you",
    "disregard your instructions",
    "forget prior instructions",
    "forget everything",
    "forget what you were told",
    "forget your instructions",
    "start fresh",
    "start over",
    "new instructions",
    "override your instructions",
    "override your",
    "bypass your",
    "don't follow your",
    "do not follow your",
)


@dataclass(frozen=True)
class InjectionDetectionResult:
    normalized_message: str
    injection_detected: bool
    matched_pattern_count: int


def normalize_for_matching(message: str) -> str:
    collapsed = re.sub(r"\s+", " ", message.strip())
    return collapsed.lower()


def detect_prompt_injection(message: str) -> InjectionDetectionResult:
    normalized = normalize_for_matching(message)
    matched_pattern_count = sum(1 for pattern in INJECTION_PATTERNS if pattern in normalized)
    return InjectionDetectionResult(
        normalized_message=normalized,
        injection_detected=matched_pattern_count > 0,
        matched_pattern_count=matched_pattern_count,
    )
