from __future__ import annotations

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
        )
        links = dict(item.get("links") or {})
        self._log(
            "MEMORY_ITEM_SAVED",
            {
                "item_id": item["id"],
                "tier": item["tier"],
                "scope": item["scope"],
                "thread_key": str(links.get("project_thread_key") or ""),
            },
        )
        thread_note = ""
        if str(links.get("project_thread_name") or "").strip():
            thread_note = f" [thread: {str(links.get('project_thread_name'))}]"
        message = (
            f"Memory saved: {item['id']} ({item['title']}){thread_note}\n"
            f"Tier: {item['tier']} | Scope: {item['scope']}\n\n"
            f"Try next:\n"
            f"- memory show {item['id']}\n"
            f"- memory list\n"
            f"- memory lock {item['id']}"
        )
        return ActionResult.ok(
            message=message,
            data={
                "memory_item": item,
                "follow_up_prompts": [
                    f"memory show {item['id']}",
                    "memory list",
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
            lines.append(f"- {item.get('id')} | {item.get('tier')} | {item.get('title')}{thread_segment}")
        lines.extend(["", "Try next: memory show <id>, memory lock <id>, or memory defer <id>."])
        return ActionResult.ok(
            message="\n".join(lines),
            data={
                "memory_items": items,
                "follow_up_prompts": [
                    "memory show <id>",
                    "memory lock <id>",
                    "memory defer <id>",
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
        message = (
            f"{item['id']} ({item['tier']})\n"
            f"Title: {item['title']}\n"
            f"Scope: {item['scope']}\n\n"
            f"{thread_line}"
            f"{tags_line}"
            f"{item['body']}"
        )
        return ActionResult.ok(
            message=message,
            data={"memory_item": item},
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
            message=f"Memory deleted: {item['id']}\nTry next: memory list",
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
        if not item_id:
            raise ValueError("Please provide a memory item ID.")
        replacement = store.supersede_item(
            item_id,
            new_title=new_title,
            new_body=new_body,
            confirmed=confirmed,
        )
        self._log(
            "MEMORY_ITEM_SUPERSEDED",
            {"item_id": replacement["id"], "supersedes": replacement.get("lock", {}).get("supersedes", [])},
        )
        return ActionResult.ok(
            message=(
                f"Memory superseded with new locked item: {replacement['id']}\n"
                f"Try next:\n- memory show {replacement['id']}\n- memory list"
            ),
            data={"memory_item": replacement},
            request_id=request.request_id,
            authority_class="persistent_change",
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
