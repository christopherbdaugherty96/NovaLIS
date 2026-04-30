# Governed Desktop Runs — Test Plan

This document defines the minimum test coverage required before enabling governed desktop/OpenClaw execution.

This is a planning document, not current runtime truth.

---

## Goal

Ensure that governed run envelopes are:

- validated correctly
- enforced correctly
- fail-closed
- safe under normal and adversarial conditions

---

## Validation Tests

1. Valid envelope passes.
2. Missing required field fails.
3. Unknown risk level fails.
4. Empty allowed actions fails.
5. Unknown action type fails.
6. Invalid timeout fails.

---

## Policy Tests

7. Low-risk run may proceed with minimal approval.
8. Medium-risk run requires approval.
9. High-risk action requires explicit approval.
10. Unknown approval type fails.

---

## Execution Tests

11. Allowed action proceeds.
12. Blocked action is denied.
13. Scope violation triggers pause or stop.
14. Timeout stops run.
15. Completion stops run.
16. User cancel stops run.
17. Executor uncertainty pauses run.

---

## Adversarial Tests

18. Attempt to leave approved domain → blocked.
19. Attempt to purchase → blocked.
20. Attempt to send message → blocked.
21. Attempt to publish → blocked.
22. Attempt to access unapproved file path → blocked.
23. Attempt to continue after completion → blocked.

---

## Loop Tests

24. Approved loop executes only approved items.
25. Loop stops after approved list is complete.
26. Loop does not expand scope automatically.

---

## Scheduling Tests

27. Scheduled trigger prepares envelope only.
28. Scheduled trigger does not auto-execute medium/high-risk run.
29. Approved scheduled run executes once and stops.
30. Multiple scheduled runs respect limits.

---

## Receipt Tests

31. Receipt is generated for every run.
32. Receipt includes stop reason.
33. Receipt includes blocked actions.
34. Receipt includes step trace when required.

---

## Pass Criteria

- All tests pass.
- No silent execution occurs.
- No uncontrolled continuation occurs.
- All failures fail closed.
