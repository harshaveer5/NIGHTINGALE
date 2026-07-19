import re
from typing import Dict, Optional


def _normalize(question: str) -> str:
    normalized = question.lower().strip()
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def _contains_any(text: str, phrases: list[str]) -> bool:
    return any(phrase in text for phrase in phrases)


GENERIC_RESPONSES = {
    "greeting": {
        "patterns": [
            "hi",
            "hello",
            "hello there",
            "hey",
            "how are you",
            "good morning",
            "good afternoon",
            "good evening",
            "good night",
        ],
        "answer": (
            "Hello. I can help explain uploaded medical reports, summarize "
            "patient documents, compare reports, identify documented abnormal "
            "values, and suggest questions to discuss with a clinician."
        ),
    },
    "goodbye": {
        "patterns": [
            "bye",
            "goodbye",
            "see you",
            "thanks bye",
            "thank you bye",
        ],
        "answer": (
            "Goodbye. Keep copies of your reports handy, and contact a "
            "qualified healthcare professional for diagnosis, treatment, or "
            "urgent medical concerns."
        ),
    },
    "thanks": {
        "patterns": [
            "thanks",
            "thank you",
            "thx",
        ],
        "answer": (
            "You're welcome. I can keep helping with uploaded reports, lab "
            "values, document summaries, and safe doctor-discussion questions."
        ),
    },
}

ROLE_PATTERNS = [
    "what can you do",
    "what are your roles",
    "what are your responsibilities",
    "your role",
    "your responsibility",
    "who are you",
    "what is your name",
    "what is your purpose",
    "how can you help",
]

EMERGENCY_PATTERNS = [
    "emergency",
    "cpr",
    "cardiopulmonary resuscitation",
    "not breathing",
    "unconscious",
    "collapsed",
    "heart attack",
    "stroke",
    "choking",
    "severe bleeding",
    "heavy bleeding",
    "overdose",
    "seizure",
    "burn",
]


ROLE_RESPONSE = (
    "I am a medical-document assistant. I can explain uploaded reports, "
    "summarize records, compare patient documents, search across uploaded "
    "documents, and help prepare questions for a healthcare professional.\n\n"
    "I do not diagnose diseases, prescribe medication, recommend treatment, "
    "or replace a clinician."
)


CPR_RESPONSE = (
    "If this is happening now, call emergency services immediately.\n\n"
    "For an unresponsive adult who is not breathing or only gasping:\n"
    "1. Make sure the scene is safe.\n"
    "2. Call emergency services or tell someone nearby to call.\n"
    "3. Put the person on their back on a firm, flat surface.\n"
    "4. Start chest compressions with two hands in the center of the chest.\n"
    "5. Push hard and fast at about 100 to 120 compressions per minute.\n"
    "6. If trained and able, give cycles of 30 compressions and 2 breaths.\n"
    "7. Use an AED as soon as one is available and follow its prompts.\n\n"
    "This is emergency first-aid guidance, not a substitute for emergency "
    "services or certified CPR training."
)


GENERAL_EMERGENCY_RESPONSE = (
    "If this may be an emergency, call local emergency services now. Do not "
    "wait for an AI response.\n\n"
    "While waiting for help: keep the person as safe as possible, follow "
    "dispatcher instructions, do not give food or drink to an unconscious "
    "person, and use first-aid skills only if you are trained and it is safe "
    "to do so.\n\n"
    "For chest pain, stroke symptoms, severe bleeding, overdose, trouble "
    "breathing, choking, loss of consciousness, or a seizure that does not "
    "stop quickly, treat it as urgent and seek emergency care immediately."
)


def get_cached_response(question: str) -> Optional[Dict]:
    normalized = _normalize(question)

    if not normalized:
        return None

    for response_type, config in GENERIC_RESPONSES.items():
        for pattern in config["patterns"]:
            if normalized == pattern:
                return {
                    "answer": config["answer"],
                    "intent": f"CACHED_{response_type.upper()}",
                    "warning": None,
                }

    if _contains_any(normalized, ROLE_PATTERNS):
        return {
            "answer": ROLE_RESPONSE,
            "intent": "CACHED_ROLE_INFO",
            "warning": None,
        }

    if "cpr" in normalized or "cardiopulmonary resuscitation" in normalized:
        return {
            "answer": CPR_RESPONSE,
            "intent": "CACHED_EMERGENCY_CPR",
            "warning": (
                "Emergency guidance only. Call emergency services immediately "
                "if someone may be in danger."
            ),
        }

    if _contains_any(normalized, EMERGENCY_PATTERNS):
        return {
            "answer": GENERAL_EMERGENCY_RESPONSE,
            "intent": "CACHED_EMERGENCY_GUIDANCE",
            "warning": (
                "Emergency guidance only. Call emergency services immediately "
                "if someone may be in danger."
            ),
        }

    return None
