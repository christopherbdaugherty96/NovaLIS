"""Conversational memory skill for the memory loop.

Handles explicit, user-initiated memory operations:
  remember  — save a new memory item
  review    — list or overview saved memory
  update    — supersede/correct an existing item
  forget    — delete an item (confirmed)
  why-used  — explain what memory context is active and why

Non-authorizing:
  - Memory provides context; it never authorizes action.
  - All write operations are explicit (user-initiated only).
  - Auto-extracted items (source='auto_extracted') are readable via
    review and removable via forget, so auto-save is not permanent or
    invisible.

No new capability is registered. No external effects.
"""

from __future__ import annotations

import re
from typing import Any

from src.base_skill import BaseSkill, SkillResult
from src.executors.memory_governance_executor import MemoryGovernanceExecutor
from src.memory.governed_memory_store import GovernedMemoryStore
from src.memory.user_memory_store import user_memory_store


# ---------------------------------------------------------------------------
# Intent patterns
# ---------------------------------------------------------------------------

_REMEMBER_RE = re.compile(
    r"""
    \b(
        remember\s+(?:this|that|it|the following|my|the)?[:\s]  # "remember this:"
      | save\s+(?:this|that|to\s+memory)[:\s]                   # "save this to memory"
      | make\s+a\s+note\b                                        # "make a note"
      | add\s+to\s+(?:memory|notes)\b                           # "add to memory"
      | note\s+(?:this|that|down)[:\s]?                         # "note this:"
      | keep\s+(?:this|that)\s+(?:in\s+mind|saved)\b            # "keep this in mind"
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)

_REVIEW_RE = re.compile(
    r"""
    \b(
        (review|list|show|display)\s+(my\s+)?mem(ory|ories)
      | what\s+(do\s+you\s+)?know\s+about\s+me\b
      | what\s+(have\s+you\s+|do\s+you\s+)(remember|recall|have\s+saved)\b
      | what\s+did\s+i\s+(tell|save|store)\s+(you\b)?
      | recent\s+mem(ory|ories)\b
      | memory\s+(overview|status|list|review)\b
      | show\s+my\s+(saved\s+)?mem(ory|ories)\b
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)

_FORGET_RE = re.compile(
    r"""
    \b(
        forget\s+(?:that|this|it|my|the|memory\s+\S+|\S+)\b
      | delete\s+(that\s+)?mem(ory|ories)?\b
      | remove\s+(that\s+)?mem(ory|ories)?\b
      | clear\s+(that\s+)?mem(ory|ories)?\b
      | don'?t\s+(remember|save|keep|store)\s+(that|this)\b
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)

_UPDATE_RE = re.compile(
    r"""
    \b(
        (update|change|edit|correct|fix)\s+(my\s+)?(memory|note|that)\b
      | that'?s?\s+(not\s+right|wrong|incorrect)\b
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)

_WHY_USED_RE = re.compile(
    r"""
    \b(
        why\s+(did\s+you\s+)?(use|bring\s+up|mention|include|inject)\s+(that|my|the)?\s*(memory|context|note|preference)\b
      | why\s+(is|was)\s+(that|this)\s+in\s+(your|the)\s+context\b
      | what\s+(memory|context)\s+(are\s+you|did\s+you)\s+using\b
      | what\s+do\s+you\s+know\s+about\s+me\s+right\s+now\b
      | show\s+(me\s+)?(?:your|the)\s+(active\s+)?memory\s+context\b
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)


# ---------------------------------------------------------------------------
# MemorySkill
# ---------------------------------------------------------------------------

class MemorySkill(BaseSkill):
    name = "memory"
    description = "Explicit user-initiated memory: remember, review, update, forget, why-used."

    _MAX_TITLE = 120
    _MAX_BODY = 600

    def __init__(
        self,
        *,
        store: GovernedMemoryStore | None = None,
        ledger=None,
    ) -> None:
        self._store = store
        self._ledger = ledger
        self._executor = MemoryGovernanceExecutor(ledger=ledger, store=store)

    def can_handle(self, query: str) -> bool:
        q = str(query or "").strip()
        return bool(
            _REMEMBER_RE.search(q)
            or _REVIEW_RE.search(q)
            or _FORGET_RE.search(q)
            or _UPDATE_RE.search(q)
            or _WHY_USED_RE.search(q)
        )

    async def handle(
        self,
        query: str,
        context: list[dict[str, Any]] | None = None,
        session_state: dict[str, Any] | None = None,
    ) -> SkillResult | None:
        q = str(query or "").strip()
        if not q:
            return None
        state = dict(session_state or {})

        if _WHY_USED_RE.search(q):
            return self._handle_why_used(q, state)
        if _REMEMBER_RE.search(q):
            return self._handle_remember(q, state)
        if _FORGET_RE.search(q):
            return self._handle_forget(q, state)
        if _UPDATE_RE.search(q):
            return self._handle_update(q, state)
        if _REVIEW_RE.search(q):
            return self._handle_review(state)

        return None

    # ------------------------------------------------------------------
    # Operation handlers
    # ------------------------------------------------------------------

    def _handle_remember(self, query: str, session_state: dict[str, Any]) -> SkillResult:
        content = _extract_remember_content(query)
        if not content:
            return SkillResult(
                success=False,
                message="I didn't catch what you'd like me to remember. Try: \"remember my project goal is X\"",
                skill=self.name,
            )

        title = content[:self._MAX_TITLE]
        body = content[:self._MAX_BODY]
        session_id = str(session_state.get("session_id") or "")
        store = self._resolve_store()

        item = store.save_item(
            title=title,
            body=body,
            scope="project",
            source="explicit_user_save",
            session_id=session_id,
            user_visible=True,
        )
        item_id = str(item.get("id") or "")
        self._log("MEMORY_ITEM_SAVED", {
            "item_id": item_id,
            "source": "explicit_user_save",
            "title": title[:80],
            "session_id": session_id,
        })

        return SkillResult(
            success=True,
            message=f"Saved to memory: \"{title[:80]}\" (id: {item_id})\nYou can review it with \"review memories\" or remove it with \"forget memory {item_id}\".",
            data={
                "memory_item": item,
                "action": "saved",
            },
            skill=self.name,
        )

    def _handle_review(self, session_state: dict[str, Any]) -> SkillResult:
        store = self._resolve_store()
        overview = store.summarize_overview()
        total = int(overview.get("total_count") or 0)
        recent = list(overview.get("recent_items") or [])

        if not total:
            # Also check user memory store for any auto-extracted personal facts
            user_entries = user_memory_store.get_all(limit=5)
            if user_entries:
                lines = ["No project memory items saved yet.", ""]
                lines.append("Auto-extracted personal facts (source: auto_extracted):")
                for entry in user_entries[:5]:
                    key = str(entry.get("key") or "")
                    value = str(entry.get("value") or "")
                    source = str(entry.get("source") or "")
                    entry_id = str(entry.get("id") or "")
                    lines.append(f"  [{source}] {key}: {value}  (id: {entry_id})")
                lines.append("")
                lines.append("To remove a personal fact, say \"forget [id]\".")
                return SkillResult(
                    success=True,
                    message="\n".join(lines),
                    data={"user_memory_entries": user_entries, "governed_total": 0},
                    skill=self.name,
                )
            return SkillResult(
                success=True,
                message="No memory items are saved yet. Say \"remember X\" to save something.",
                data={"governed_total": 0},
                skill=self.name,
            )

        lines = [f"Saved memory: {total} item{'s' if total != 1 else ''}", ""]
        for item in recent[:5]:
            item_id = str(item.get("id") or "")
            title = str(item.get("title") or "").strip() or "(untitled)"
            tier = str(item.get("tier") or "active")
            lines.append(f"  {item_id} [{tier}] {title[:80]}")

        if total > 5:
            lines.append(f"  ... and {total - 5} more")
        lines.extend(["", "Say \"forget [id]\" to remove an item, or \"memory show [id]\" for details."])

        return SkillResult(
            success=True,
            message="\n".join(lines),
            data={"memory_overview": overview},
            skill=self.name,
        )

    def _handle_forget(self, query: str, session_state: dict[str, Any]) -> SkillResult:
        item_id = _extract_item_id(query)

        # Check user memory store first (auto-extracted personal facts)
        if item_id and item_id.startswith("UM-"):
            deleted = user_memory_store.remove(item_id)
            if deleted:
                self._log("MEMORY_ITEM_DELETED", {"item_id": item_id, "source": "explicit_user_forget"})
                return SkillResult(
                    success=True,
                    message=f"Removed personal fact {item_id} from memory. I won't use it again.",
                    data={"deleted_id": item_id, "action": "forgotten"},
                    skill=self.name,
                )
            return SkillResult(
                success=False,
                message=f"Couldn't find {item_id} in memory. It may already be gone.",
                skill=self.name,
            )

        if not item_id:
            # No specific ID — ask the user to confirm which one
            return SkillResult(
                success=False,
                message=(
                    "Which memory would you like to forget? "
                    "Say \"review memories\" to see IDs, then \"forget [id]\"."
                ),
                skill=self.name,
            )

        store = self._resolve_store()
        try:
            store.delete_item(item_id, confirmed=True)
            self._log("MEMORY_ITEM_DELETED", {"item_id": item_id, "source": "explicit_user_forget"})
            return SkillResult(
                success=True,
                message=f"Forgot memory {item_id}. It won't appear in future context.",
                data={"deleted_id": item_id, "action": "forgotten"},
                skill=self.name,
            )
        except KeyError:
            return SkillResult(
                success=False,
                message=f"Couldn't find memory {item_id}. It may already be gone.",
                skill=self.name,
            )
        except Exception:
            return SkillResult(
                success=False,
                message="Memory delete failed. Try again or check the memory ID.",
                skill=self.name,
            )

    def _handle_update(self, query: str, session_state: dict[str, Any]) -> SkillResult:
        item_id = _extract_item_id(query)
        new_content = _extract_update_content(query)

        if not item_id or not new_content:
            return SkillResult(
                success=False,
                message=(
                    "To update a memory item, say: \"update memory [id]: new content here\". "
                    "Say \"review memories\" to see current IDs."
                ),
                skill=self.name,
            )

        store = self._resolve_store()
        session_id = str(session_state.get("session_id") or "")
        try:
            item = store.supersede_item(
                item_id,
                new_title="",
                new_body=new_content[:self._MAX_BODY],
                confirmed=True,
                source="explicit_user_edit",
                session_id=session_id,
            )
            new_id = str(item.get("id") or "")
            self._log("MEMORY_ITEM_SAVED", {
                "item_id": new_id,
                "supersedes": item_id,
                "source": "explicit_user_edit",
            })
            return SkillResult(
                success=True,
                message=f"Updated memory (new id: {new_id}, superseded: {item_id}).",
                data={"memory_item": item, "action": "updated", "superseded_id": item_id},
                skill=self.name,
            )
        except KeyError:
            return SkillResult(
                success=False,
                message=f"Couldn't find memory {item_id} to update.",
                skill=self.name,
            )
        except Exception:
            return SkillResult(
                success=False,
                message="Memory update failed. Try again or check the memory ID.",
                skill=self.name,
            )

    def _handle_why_used(self, query: str, session_state: dict[str, Any]) -> SkillResult:
        """Explain what memory context is active and how it was selected."""
        context_block = user_memory_store.render_context_block(max_chars=600)
        user_entries = user_memory_store.get_all(limit=20)

        store = self._resolve_store()
        governed_recent = store.list_recent_items(limit=5)

        lines: list[str] = ["Active memory context", ""]

        if context_block.strip():
            lines.append("Personal facts in current context:")
            lines.append(context_block.strip())
            lines.append("")
        else:
            lines.append("No personal facts are currently in context.")
            lines.append("")

        if user_entries:
            lines.append(f"Stored personal facts: {len(user_entries)} item(s)")
            for entry in user_entries[:5]:
                key = str(entry.get("key") or "")
                value = str(entry.get("value") or "")
                source = str(entry.get("source") or "")
                entry_id = str(entry.get("id") or "")
                lines.append(f"  [{source}] {key}: {value}  (id: {entry_id})")
            if len(user_entries) > 5:
                lines.append(f"  ... and {len(user_entries) - 5} more")
            lines.append("")

        if governed_recent:
            lines.append("Recent project memory:")
            for item in governed_recent[:3]:
                item_id = str(item.get("id") or "")
                title = str(item.get("title") or "").strip() or "(untitled)"
                lines.append(f"  {item_id}: {title[:80]}")
            lines.append("")

        lines.append("How memory is selected:")
        lines.append("  Personal facts: all stored facts are injected when a response is generated.")
        lines.append("  Project memory: items are matched by relevance to the current query.")
        lines.append("  Source labels: 'explicit_user_save' = you saved it explicitly;")
        lines.append("                 'auto_extracted' = extracted from your messages by pattern.")
        lines.append("")
        lines.append("To remove any item, say \"forget [id]\".")

        return SkillResult(
            success=True,
            message="\n".join(lines),
            data={
                "active_context_block": context_block,
                "user_entry_count": len(user_entries),
                "governed_recent_count": len(governed_recent),
            },
            skill=self.name,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _resolve_store(self) -> GovernedMemoryStore:
        return self._store if self._store is not None else GovernedMemoryStore()

    def _log(self, event_type: str, metadata: dict[str, Any]) -> None:
        if self._ledger is None:
            return
        try:
            self._ledger.log_event(event_type, metadata)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Text extraction helpers
# ---------------------------------------------------------------------------

_REMEMBER_STRIP_RE = re.compile(
    r"^(?:please\s+)?(?:remember|save\s+(?:this|that)(?:\s+to\s+memory)?|"
    r"make\s+a\s+note(?:\s+(?:of|that))?|add\s+(?:this\s+)?to\s+(?:memory|notes)|"
    r"note\s+(?:this|that|down)|keep\s+(?:this|that)\s+(?:in\s+mind|saved))"
    r"[:\s]+",
    re.IGNORECASE,
)

_ITEM_ID_RE = re.compile(r"\b(MEM-\d{8}-\d{6}-[0-9A-Fa-f]{4}|UM-[0-9a-fA-F]{8})\b")

_UPDATE_COLON_RE = re.compile(
    r"^(?:update|change|edit|correct|fix)\s+(?:my\s+)?(?:memory|note|that)(?:\s+\S+)?\s*:\s*",
    re.IGNORECASE,
)


def _extract_remember_content(query: str) -> str:
    match = _REMEMBER_STRIP_RE.search(query.strip())
    if not match:
        return ""
    cleaned = query.strip()[match.end():].strip()
    return cleaned[:600]


def _extract_item_id(query: str) -> str:
    match = _ITEM_ID_RE.search(query)
    return match.group(1) if match else ""


def _extract_update_content(query: str) -> str:
    match = _UPDATE_COLON_RE.search(query.strip())
    if match:
        cleaned = query.strip()[match.end():].strip()
        return cleaned[:600] if cleaned else ""
    colon_pos = query.find(":")
    if colon_pos >= 0:
        cleaned = query[colon_pos + 1:].strip()
        return cleaned[:600] if cleaned else ""
    return ""
