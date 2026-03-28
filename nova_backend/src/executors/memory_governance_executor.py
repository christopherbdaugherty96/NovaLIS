from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.actions.action_result import ActionResult
from src.memory.governed_memory_store import GovernedMemoryStore


class MemoryGovernanceExecutor:
    """Explicit, user-invoked memory filing operations."""

    def __init__(self, *, ledger=None, store: GovernedMemoryStore | None = None) -> None:
        self._ledger = ledger
        self._store = store

    def execute(self, request) -> ActionResult:
        params = dict(request.params or {})
        action = str(params.get("action") or "list").strip().lower()
        store = self._resolve_store(params)

        try:
            if action in {"overview", "status", "review"}:
                return self._overview(request, store)
            if action == "recent":
                return self._recent(request, params, store)
            if action == "search":
                return self._search(request, params, store)
            if action == "save":
                return self._save(request, params, store)
            if action == "save_thread_snapshot":
                return ActionResult.failure(
                    "Thread snapshot save requires orchestration context.",
                    request_id=request.request_id,
                    authority_class="persistent_change",
                    external_effect=False,
                    reversible=True,
                )
            if action == "save_thread_decision":
                return ActionResult.failure(
                    "Thread decision save requires orchestration context.",
                    request_id=request.request_id,
                    authority_class="persistent_change",
                    external_effect=False,
                    reversible=True,
                )
            if action == "list":
                return self._list(request, params, store)
            if action == "show":
                return self._show(request, params, store)
            if action == "export":
                return self._export(request, store)
            if action == "lock":
                return self._lock(request, params, store)
            if action == "defer":
                return self._defer(request, params, store)
            if action == "unlock":
                return self._unlock(request, params, store)
            if action == "delete":
                return self._delete(request, params, store)
            if action == "supersede":
                return self._supersede(request, params, store)
        except PermissionError as exc:
            return ActionResult.refusal(
                f"{exc} Reply with explicit confirmation to proceed.",
                request_id=request.request_id,
                authority_class="persistent_change",
                external_effect=False,
                reversible=False,
            )
        except KeyError:
            return ActionResult.failure(
                "I could not find that memory item.",
                request_id=request.request_id,
                authority_class="persistent_change",
                external_effect=False,
                reversible=True,
            )
        except ValueError as exc:
            return ActionResult.failure(
                str(exc),
                request_id=request.request_id,
                authority_class="persistent_change",
                external_effect=False,
                reversible=True,
            )
        except Exception:
            return ActionResult.failure(
                "Memory operation failed.",
                request_id=request.request_id,
                authority_class="persistent_change",
                external_effect=False,
                reversible=True,
            )

        return ActionResult.failure(
            "Unsupported memory action.",
            request_id=request.request_id,
            authority_class="persistent_change",
            external_effect=False,
            reversible=True,
        )

    def _overview(self, request, store: GovernedMemoryStore) -> ActionResult:
        overview = store.summarize_overview()
        tier_counts = dict(overview.get("tier_counts") or {})
        active_count = int(tier_counts.get("active") or 0)
        locked_count = int(tier_counts.get("locked") or 0)
        deferred_count = int(tier_counts.get("deferred") or 0)
        total_count = int(overview.get("total_count") or 0)
        linked_threads = list(overview.get("linked_threads") or [])
        recent_items = list(overview.get("recent_items") or [])

        self._log(
            "MEMORY_OVERVIEW_VIEWED",
            {
                "total_count": total_count,
                "active_count": active_count,
                "locked_count": locked_count,
                "deferred_count": deferred_count,
            },
        )

        lines = ["Governed Memory Overview", ""]
        lines.append(f"Total items: {total_count}")
        lines.append(f"Active: {active_count} | Locked: {locked_count} | Deferred: {deferred_count}")
        lines.append("")

        if linked_threads:
            lines.append("Linked project threads")
            for thread in linked_threads[:4]:
                thread_name = str(thread.get("thread_name") or thread.get("thread_key") or "Unnamed thread").strip()
                thread_count = int(thread.get("memory_count") or 0)
                latest_title = str(thread.get("latest_title") or "").strip()
                latest_decision = str(thread.get("latest_decision") or "").strip()
                if latest_title:
                    lines.append(f"- {thread_name}: {thread_count} items | latest '{latest_title}'")
                else:
                    lines.append(f"- {thread_name}: {thread_count} items")
                if latest_decision:
                    lines.append(f"  Latest decision: {latest_decision}")
            lines.append("")

        if recent_items:
            lines.append("Recent memory")
            for item in recent_items[:5]:
                item_id = str(item.get("id") or "").strip()
                title = str(item.get("title") or "").strip() or item_id
                tier = str(item.get("tier") or "").strip().lower() or "active"
                thread_name = str(item.get("thread_name") or "").strip()
                thread_suffix = f" | thread:{thread_name}" if thread_name else ""
                lines.append(f"- {item_id} | {tier} | {title}{thread_suffix}")
        else:
            lines.append("No memory items are stored yet.")

        lines.extend(
            [
                "",
                "Try next:",
                "- memory list",
                "- recent memories",
                "- search memories for <topic>",
                "- memory show <id>",
                "- memory save <title>: <content>",
            ]
        )
        if linked_threads:
            first_thread = str(linked_threads[0].get("thread_name") or "").strip()
            if first_thread:
                lines.append(f"- memory list thread {first_thread}")

        follow_up_prompts = [
            "memory list",
            "recent memories",
            "search memories for <topic>",
            "memory show <id>",
            "memory save <title>: <content>",
        ]
        if linked_threads:
            first_thread = str(linked_threads[0].get("thread_name") or "").strip()
            if first_thread:
                follow_up_prompts.append(f"memory list thread {first_thread}")

        return ActionResult.ok(
            message="\n".join(lines),
            data={
                "memory_overview": overview,
                "follow_up_prompts": follow_up_prompts,
            },
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )

    def _export(self, request, store: GovernedMemoryStore) -> ActionResult:
        payload = store.export_payload()
        item_count = int(payload.get("item_count") or 0)
        exported_at = str(payload.get("exported_at") or datetime.now(timezone.utc).isoformat())
        self._log(
            "MEMORY_EXPORT_REQUESTED",
            {
                "item_count": item_count,
                "exported_at": exported_at,
                "includes_deleted": bool(payload.get("includes_deleted")),
            },
        )
        return ActionResult.ok(
            message=(
                f"Prepared memory export with {item_count} item{'s' if item_count != 1 else ''}.\n"
                "Use the Memory page export control to download the full JSON snapshot."
            ),
            data={
                "memory_export": payload,
                "follow_up_prompts": [
                    "memory overview",
                    "recent memories",
                    "list memories",
                    "show that memory",
                ],
            },
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )

    def _resolve_store(self, params: dict[str, Any]) -> GovernedMemoryStore:
        if self._store is not None:
            return self._store
        custom_path = str(params.get("memory_store_path") or "").strip()
        if custom_path:
            return GovernedMemoryStore(custom_path)
        return GovernedMemoryStore()

    def _save(self, request, params: dict[str, Any], store: GovernedMemoryStore) -> ActionResult:
        title = str(params.get("title") or "").strip()
        body = str(params.get("body") or "").strip()
        scope = str(params.get("scope") or "project").strip().lower()
        source = str(params.get("source") or "explicit_user_save").strip()
        session_id = str(params.get("session_id") or "").strip()
        user_visible = bool(params.get("user_visible", True))
        tags_raw = params.get("tags")
        tags: list[Any]
        if isinstance(tags_raw, list):
            tags = list(tags_raw)
        elif isinstance(tags_raw, str):
            tags = [token.strip() for token in tags_raw.split(",") if token.strip()]
        else:
            tags = []
        thread_name = str(params.get("thread_name") or "").strip()
        thread_key = str(params.get("thread_key") or "").strip()
        if thread_key and thread_key not in tags:
            tags.append(thread_key)

        item = store.save_item(
            title=title,
            body=body,
            scope=scope,
            tags=tags,
            thread_name=thread_name,
            thread_key=thread_key,
            source=source,
            session_id=session_id,
            user_visible=user_visible,
        )
        links = dict(item.get("links") or {})
        self._log(
            "MEMORY_ITEM_SAVED",
            {
                "item_id": item["id"],
                "tier": item["tier"],
                "scope": item["scope"],
                "source": str(item.get("source") or ""),
                "thread_key": str(links.get("project_thread_key") or ""),
            },
        )
        thread_note = ""
        if str(links.get("project_thread_name") or "").strip():
            thread_note = f" [thread: {str(links.get('project_thread_name'))}]"
        display = str(item.get("content_display") or item.get("title") or item["id"]).strip()
        message = (
            f'Saved. Memory {item["id"]}: "{display}".{thread_note}\n'
            f"Tier: {item['tier']} | Scope: {item['scope']} | Source: {item.get('source')}\n\n"
            f"Try next:\n"
            f"- memory show {item['id']}\n"
            f"- recent memories\n"
            f"- memory lock {item['id']}"
        )
        return ActionResult.ok(
            message=message,
            data={
                "memory_item": item,
                "follow_up_prompts": [
                    f"memory show {item['id']}",
                    "recent memories",
                    f"memory lock {item['id']}",
                ],
            },
            request_id=request.request_id,
            authority_class="persistent_change",
            external_effect=False,
            reversible=True,
        )

    def _list(self, request, params: dict[str, Any], store: GovernedMemoryStore) -> ActionResult:
        tier = str(params.get("tier") or "").strip().lower()
        scope = str(params.get("scope") or "").strip().lower()
        thread_name = str(params.get("thread_name") or "").strip()
        thread_key = str(params.get("thread_key") or "").strip()
        items = store.list_items(
            tier=tier,
            scope=scope,
            thread_name=thread_name,
            thread_key=thread_key,
            limit=30,
        )
        self._log(
            "MEMORY_ITEM_LISTED",
            {
                "tier_filter": tier,
                "scope_filter": scope,
                "thread_key_filter": thread_key,
                "count": len(items),
            },
        )
        if not items:
            return ActionResult.ok(
                message="No memory items found for that filter.",
                data={"memory_items": []},
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )
        lines = [f"Memory Items ({len(items)})"]
        for item in items:
            links = dict(item.get("links") or {})
            thread_segment = ""
            thread_name_value = str(links.get("project_thread_name") or "").strip()
            if thread_name_value:
                thread_segment = f" | thread:{thread_name_value}"
            preview = str(item.get("content_display") or item.get("title") or "").strip()
            lines.append(f"- {item.get('id')} | {item.get('tier')} | {preview}{thread_segment}")
        lines.extend(
            [
                "",
                "Try next:",
                "- recent memories",
                "- search memories for <topic>",
                "- memory show <id>",
                "- edit memory <id>: <updated text>",
                "- delete memory <id>",
            ]
        )
        return ActionResult.ok(
            message="\n".join(lines),
            data={
                "memory_items": items,
                "follow_up_prompts": [
                    "recent memories",
                    "search memories for <topic>",
                    "memory show <id>",
                    "edit memory <id>: <updated text>",
                    "delete memory <id>",
                ],
            },
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )

    def _show(self, request, params: dict[str, Any], store: GovernedMemoryStore) -> ActionResult:
        item_id = str(params.get("item_id") or "").strip()
        if not item_id:
            raise ValueError("Please provide a memory item ID.")
        item = store.get_item(item_id)
        if item is None:
            raise KeyError(item_id)
        self._log("MEMORY_ITEM_VIEWED", {"item_id": item["id"], "tier": item["tier"]})
        links = dict(item.get("links") or {})
        thread_name = str(links.get("project_thread_name") or "").strip()
        thread_line = f"Thread: {thread_name}\n" if thread_name else ""
        tags = ", ".join(str(tag).strip() for tag in list(item.get("tags") or []) if str(tag).strip())
        tags_line = f"Tags: {tags}\n" if tags else ""
        source_line = f"Source: {str(item.get('source') or 'explicit_user_save')}\n"
        status_line = f"Status: {str(item.get('status') or item.get('tier') or 'active')}\n"
        created_line = f"Created: {str(item.get('created_at') or '')}\n"
        updated_line = f"Updated: {str(item.get('updated_at') or '')}\n"
        version_line = f"Version: {int(item.get('version') or 1)}\n"
        lock_meta = dict(item.get("lock") or {})
        lineage_parts: list[str] = []
        supersedes = [str(value).strip() for value in list(lock_meta.get("supersedes") or []) if str(value).strip()]
        if supersedes:
            lineage_parts.append(f"Supersedes {', '.join(supersedes)}")
        superseded_by = str(lock_meta.get("superseded_by") or "").strip()
        if superseded_by:
            lineage_parts.append(f"Superseded by {superseded_by}")
        lineage_line = f"Lineage: {' | '.join(lineage_parts)}\n" if lineage_parts else ""
        message = (
            f"{item['id']} ({item['tier']})\n"
            f"Title: {item['title']}\n"
            f"Scope: {item['scope']}\n"
            f"{status_line}"
            f"{source_line}\n"
            f"{created_line}"
            f"{updated_line}"
            f"{version_line}"
            f"{thread_line}"
            f"{tags_line}"
            f"{lineage_line}"
            f"{item['body']}\n\n"
            f"Try next:\n"
            f"- edit memory {item['id']}: <updated text>\n"
            f"- delete memory {item['id']}\n"
            f"- recent memories"
        )
        return ActionResult.ok(
            message=message,
            data={
                "memory_item": item,
                "follow_up_prompts": [
                    f"edit memory {item['id']}: <updated text>",
                    f"delete memory {item['id']}",
                    "recent memories",
                ],
            },
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )

    def _lock(self, request, params: dict[str, Any], store: GovernedMemoryStore) -> ActionResult:
        item_id = str(params.get("item_id") or "").strip()
        if not item_id:
            raise ValueError("Please provide a memory item ID.")
        item = store.lock_item(item_id)
        self._log("MEMORY_ITEM_LOCKED", {"item_id": item["id"]})
        return ActionResult.ok(
            message=f"Memory locked: {item['id']}\nTry next: memory show {item['id']} or memory list.",
            data={"memory_item": item},
            request_id=request.request_id,
            authority_class="persistent_change",
            external_effect=False,
            reversible=True,
        )

    def _defer(self, request, params: dict[str, Any], store: GovernedMemoryStore) -> ActionResult:
        item_id = str(params.get("item_id") or "").strip()
        if not item_id:
            raise ValueError("Please provide a memory item ID.")
        item = store.defer_item(item_id)
        self._log("MEMORY_ITEM_DEFERRED", {"item_id": item["id"]})
        return ActionResult.ok(
            message=f"Memory deferred: {item['id']}\nTry next: memory show {item['id']} or memory unlock {item['id']} confirm.",
            data={"memory_item": item},
            request_id=request.request_id,
            authority_class="persistent_change",
            external_effect=False,
            reversible=True,
        )

    def _unlock(self, request, params: dict[str, Any], store: GovernedMemoryStore) -> ActionResult:
        item_id = str(params.get("item_id") or "").strip()
        if not item_id:
            raise ValueError("Please provide a memory item ID.")
        confirmed = bool(params.get("confirmed"))
        item = store.unlock_item(item_id, confirmed=confirmed)
        self._log("MEMORY_ITEM_UNLOCKED", {"item_id": item["id"]})
        return ActionResult.ok(
            message=f"Memory unlocked: {item['id']}\nTry next: memory show {item['id']} or memory lock {item['id']}.",
            data={"memory_item": item},
            request_id=request.request_id,
            authority_class="persistent_change",
            external_effect=False,
            reversible=True,
        )

    def _delete(self, request, params: dict[str, Any], store: GovernedMemoryStore) -> ActionResult:
        item_id = str(params.get("item_id") or "").strip()
        if not item_id:
            raise ValueError("Please provide a memory item ID.")
        confirmed = bool(params.get("confirmed"))
        item = store.delete_item(item_id, confirmed=confirmed)
        self._log("MEMORY_ITEM_DELETED", {"item_id": item["id"]})
        return ActionResult.ok(
            message=f"Deleted memory {item['id']}.\nTry next:\n- list memories\n- memory overview",
            data={"memory_item": item},
            request_id=request.request_id,
            authority_class="persistent_change",
            external_effect=False,
            reversible=False,
        )

    def _supersede(self, request, params: dict[str, Any], store: GovernedMemoryStore) -> ActionResult:
        item_id = str(params.get("item_id") or "").strip()
        new_title = str(params.get("new_title") or "").strip()
        new_body = str(params.get("new_body") or "").strip()
        confirmed = bool(params.get("confirmed"))
        source = str(params.get("source") or "explicit_user_edit").strip()
        session_id = str(params.get("session_id") or "").strip()
        user_visible = params.get("user_visible")
        if not item_id:
            raise ValueError("Please provide a memory item ID.")
        replacement = store.supersede_item(
            item_id,
            new_title=new_title,
            new_body=new_body,
            confirmed=confirmed,
            source=source,
            session_id=session_id,
            user_visible=user_visible if isinstance(user_visible, bool) else None,
        )
        self._log(
            "MEMORY_ITEM_SUPERSEDED",
            {
                "item_id": replacement["id"],
                "supersedes": replacement.get("lock", {}).get("supersedes", []),
                "source": str(replacement.get("source") or ""),
            },
        )
        return ActionResult.ok(
            message=(
                f"Updated memory with replacement item {replacement['id']}.\n"
                f"Try next:\n- memory show {replacement['id']}\n- recent memories\n- memory unlock {replacement['id']}"
            ),
            data={"memory_item": replacement},
            request_id=request.request_id,
            authority_class="persistent_change",
            external_effect=False,
            reversible=True,
        )

    def _recent(self, request, params: dict[str, Any], store: GovernedMemoryStore) -> ActionResult:
        scope = str(params.get("scope") or "").strip().lower()
        thread_name = str(params.get("thread_name") or "").strip()
        thread_key = str(params.get("thread_key") or "").strip()
        items = store.list_recent_items(limit=8, scope=scope, thread_name=thread_name, thread_key=thread_key)
        self._log(
            "MEMORY_RECENT_VIEWED",
            {
                "scope_filter": scope,
                "thread_key_filter": thread_key,
                "count": len(items),
            },
        )
        if not items:
            return ActionResult.ok(
                message="No recent memory items are available for that filter.",
                data={"memory_items": []},
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )
        lines = [f"Recent Memory ({len(items)})"]
        for item in items:
            links = dict(item.get("links") or {})
            thread_segment = ""
            thread_name_value = str(links.get("project_thread_name") or "").strip()
            if thread_name_value:
                thread_segment = f" | thread:{thread_name_value}"
            preview = str(item.get("content_display") or item.get("title") or "").strip()
            lines.append(f"- {item.get('id')} | {item.get('tier')} | {preview}{thread_segment}")
        lines.extend(["", "Try next:", "- memory show <id>", "- search memories for <topic>", "- memory overview"])
        return ActionResult.ok(
            message="\n".join(lines),
            data={
                "memory_items": items,
                "follow_up_prompts": ["memory show <id>", "search memories for <topic>", "memory overview"],
            },
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )

    def _search(self, request, params: dict[str, Any], store: GovernedMemoryStore) -> ActionResult:
        query = str(params.get("query") or "").strip()
        thread_name = str(params.get("thread_name") or "").strip()
        thread_key = str(params.get("thread_key") or "").strip()
        if not query:
            raise ValueError("Please tell me what memory topic to search for.")
        items = store.find_relevant_items(query, thread_name=thread_name, thread_key=thread_key, limit=5)
        self._log(
            "MEMORY_SEARCH_VIEWED",
            {
                "query": query,
                "thread_key_filter": thread_key,
                "count": len(items),
            },
        )
        if not items:
            return ActionResult.ok(
                message="I could not find a strong governed memory match for that search yet.",
                data={"memory_items": []},
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )
        lines = [f"Memory Search Matches ({len(items)})", f"Query: {query}", ""]
        for item in items:
            links = dict(item.get("links") or {})
            thread_name_value = str(links.get("project_thread_name") or "").strip()
            preview = str(item.get("content_display") or item.get("title") or "").strip()
            score = int(item.get("match_score") or 0)
            suffix = f" | thread:{thread_name_value}" if thread_name_value else ""
            lines.append(f"- {item.get('id')} | score {score} | {preview}{suffix}")
        lines.extend(["", "Try next:", "- memory show <id>", "- recent memories", "- memory overview"])
        return ActionResult.ok(
            message="\n".join(lines),
            data={
                "memory_items": items,
                "follow_up_prompts": ["memory show <id>", "recent memories", "memory overview"],
            },
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )

    def _log(self, event_type: str, metadata: dict[str, Any]) -> None:
        if self._ledger is None:
            return
        try:
            self._ledger.log_event(event_type, metadata)
        except Exception:
            return
