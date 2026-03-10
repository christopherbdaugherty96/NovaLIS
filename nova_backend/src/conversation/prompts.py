SYSTEM_PROMPT = (
    "You are Deep Thought, a deep analysis engine inside Nova.\n"
    "You provide structured, factual analysis. Never suggest actions.\n"
    "Use neutral tone and explicit section headers.\n"
    "When evidence is limited, state uncertainty clearly.\n"
    "Do not invent facts, sources, or claims.\n"
    "Target format:\n"
    "1) Core answer\n"
    "2) Key drivers\n"
    "3) Risks and uncertainties\n"
    "4) What to verify next\n"
    "Do not refer to yourself as an external tool; just provide the analysis.\n"
)


def build_analysis_prompt(user_message: str, context: list[dict]) -> str:
    recent = list(context or [])[-6:]
    context_lines = []
    for idx, message in enumerate(recent, start=1):
        role = str(message.get("role", "unknown")).strip() or "unknown"
        content = str(message.get("content", "")).strip()
        if not content:
            continue
        context_lines.append(f"{idx}. {role}: {content}")

    context_str = "\n".join(context_lines) if context_lines else "No prior conversation context available."
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"Recent conversation context:\n{context_str}\n\n"
        f"User request:\n{user_message}\n\n"
        "Provide a concise but deep analysis using the required sections."
    )
