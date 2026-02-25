SYSTEM_PROMPT = (
    "You are Deep Thought, a deep analysis engine inside Nova.\n"
    "You provide structured, factual analysis. Never suggest actions.\n"
    "Use clear sections if helpful. Maintain a neutral, professional tone.\n"
    "Do not refer to yourself as an external tool; just provide the analysis.\n"
)


def build_analysis_prompt(user_message: str, context: list[dict]) -> str:
    context_str = "\n".join(
        f"{message.get('role', 'unknown')}: {message.get('content', '')}" for message in (context or [])[-5:]
    )
    return f"{SYSTEM_PROMPT}\n\nRecent conversation:\n{context_str}\n\nUser: {user_message}\n\nAnalysis:"
