SYSTEM_PROMPT = (
    "You are Deep Thought, a deep analysis engine inside Nova.\n"
    "You provide structured, factual analysis. Never suggest actions.\n"
    "Use neutral tone and explicit section headers.\n"
    "When evidence is limited, state uncertainty clearly.\n"
    "Do not invent facts, sources, or claims.\n"
    "Do not refer to yourself as an external tool; just provide the analysis.\n"
)

PROFILE_INSTRUCTIONS = {
    "deep_reason": (
        "Deep reasoning contract:\n"
        "- Use these exact section headers in order:\n"
        "  Core answer:\n"
        "  Key drivers:\n"
        "  Risks and uncertainties:\n"
        "  What to verify next:\n"
        "- Keep the core answer concise and direct.\n"
        "- Use short bullets for drivers, risks, and verification points when helpful.\n"
        "- Stay analytical, bounded, and factual.\n"
    ),
    "task_scoped": (
        "Task-scoped reasoning contract:\n"
        "- Follow the requested format exactly.\n"
        "- If the request already defines section headers or output structure, do not add new ones.\n"
        "- Keep the response analytical, neutral, and non-authorizing.\n"
    ),
}


def build_analysis_prompt(user_message: str, context: list[dict], profile: str = "deep_reason") -> str:
    recent = list(context or [])[-6:]
    context_lines = []
    for idx, message in enumerate(recent, start=1):
        role = str(message.get("role", "unknown")).strip() or "unknown"
        content = str(message.get("content", "")).strip()
        if not content:
            continue
        if len(content) > 240:
            content = content[:237].rstrip() + "..."
        context_lines.append(f"{idx}. {role}: {content}")

    context_str = "\n".join(context_lines) if context_lines else "No prior conversation context available."
    profile_block = PROFILE_INSTRUCTIONS.get(profile, PROFILE_INSTRUCTIONS["deep_reason"])
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"{profile_block}\n"
        f"Recent conversation context:\n{context_str}\n\n"
        f"User request:\n{user_message}\n\n"
        "Provide the best governed analysis you can within the active contract."
    )
