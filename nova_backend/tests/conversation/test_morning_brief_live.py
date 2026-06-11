"""Live WebSocket test for the morning brief flow.

Run manually with: python -m pytest tests/conversation/test_morning_brief_live.py -v -s
Requires Nova backend running on 127.0.0.1:8010.
"""
from __future__ import annotations

import asyncio
import json
import sys

import websockets


async def run_brief_test():
    uri = "ws://127.0.0.1:8010/ws"
    results = {
        "connected": False,
        "model_unlocked": False,
        "brief_sent": False,
        "messages": [],
        "widgets": [],
        "chat_text": [],
        "errors": [],
        "chat_done": False,
    }

    try:
        async with websockets.connect(uri) as ws:
            results["connected"] = True

            # Drain the initial greeting (server sends greeting + chat_done on connect)
            for _ in range(10):
                raw = await asyncio.wait_for(ws.recv(), timeout=15)
                msg = json.loads(raw)
                if msg.get("type") == "chat_done":
                    break

            # Unlock model inference
            await ws.send(json.dumps({"text": "confirm model update", "channel": "text"}))
            for _ in range(20):
                raw = await asyncio.wait_for(ws.recv(), timeout=15)
                msg = json.loads(raw)
                if msg.get("type") == "chat_done":
                    results["model_unlocked"] = True
                    break

            # Send morning brief trigger
            await ws.send(json.dumps({"text": "morning brief", "channel": "text"}))
            results["brief_sent"] = True

            for _ in range(40):
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=45)
                    msg = json.loads(raw)
                    results["messages"].append(msg)
                    mtype = msg.get("type", "")

                    if mtype == "widget":
                        results["widgets"].append(msg.get("widget_type", "unknown"))
                    elif mtype == "chat":
                        results["chat_text"].append(
                            str(msg.get("message", ""))[:300]
                        )
                    elif mtype == "chat_done":
                        results["chat_done"] = True
                        break
                    elif mtype == "error":
                        results["errors"].append(str(msg.get("message", "")))

                except asyncio.TimeoutError:
                    results["errors"].append("timeout waiting for messages")
                    break

    except Exception as exc:
        results["errors"].append(f"connection error: {exc}")

    return results


def main():
    results = asyncio.run(run_brief_test())

    print("=" * 60)
    print("MORNING BRIEF LIVE TEST RESULTS")
    print("=" * 60)
    print(f"Connected:      {results['connected']}")
    print(f"Model unlocked: {results['model_unlocked']}")
    print(f"Brief sent:     {results['brief_sent']}")
    print(f"Chat done:      {results['chat_done']}")
    print(f"Total messages: {len(results['messages'])}")
    print(f"Widget types:   {results['widgets']}")
    print(f"Chat messages:  {len(results['chat_text'])}")
    print(f"Errors:         {results['errors']}")
    print()

    for i, txt in enumerate(results["chat_text"]):
        safe = txt.encode("ascii", errors="replace").decode("ascii")
        print(f"Chat[{i}]: {safe}")

    print()
    for i, msg in enumerate(results["messages"]):
        mtype = msg.get("type", "?")
        preview = str(msg.get("message", msg.get("data", "")))[:150]
        safe = preview.encode("ascii", errors="replace").decode("ascii")
        print(f"  msg[{i}] [{mtype}] {safe}")

    if results["errors"]:
        print()
        print("ERRORS:")
        for e in results["errors"]:
            print(f"  - {e}")
        sys.exit(1)

    if not results["chat_done"]:
        print("FAIL: never received chat_done")
        sys.exit(1)

    if not results["chat_text"]:
        print("FAIL: no chat text received")
        sys.exit(1)

    print()
    print("PASS: Morning brief flow completed successfully")


if __name__ == "__main__":
    main()
