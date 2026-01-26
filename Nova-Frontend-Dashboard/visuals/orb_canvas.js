/**
 * ================================================================
 * NOVA — ORB CANVAS RENDERER (PHASE-2 LOCK)
 * ================================================================
 *
 * STATUS: ARCHITECTURE LOCKED
 *
 * This file is responsible for rendering the Nova orb as a
 * physics-based visual presence using <canvas>.
 *
 * ---------------------------------------------------------------
 * HARD CONSTRAINTS — DO NOT VIOLATE
 * ---------------------------------------------------------------
 *
 * 1. This renderer MUST be:
 *    - Time-based only
 *    - Deterministic
 *    - Non-interactive
 *    - Non-semantic
 *
 * 2. This file MUST NOT:
 *    - React to system state
 *    - React to user input
 *    - React to network events
 *    - React to skill execution
 *    - React to "thinking", "idle", or "active" states
 *
 * 3. NO imports are allowed from:
 *    - UI logic (dashboard.js, chat, widgets)
 *    - Backend or WebSocket code
 *    - Skills or ActionRequest logic
 *
 * 4. Motion semantics are LOCKED:
 *    - Drift: slow, continuous energy circulation (time-based)
 *    - Impulse: rare, asymmetrical energy redistribution (non-rhythmic)
 *    - Glow: constant identity radiation (never spikes or fades)
 *    - Glare: optical artifact only (math-based, not logic-based)
 *
 * 5. The orb MUST NOT communicate meaning.
 *    If a viewer can infer what Nova is doing by looking at the orb,
 *    this file has violated its architectural contract.
 *
 * ---------------------------------------------------------------
 * SINGLE SOURCE OF MOTION
 * ---------------------------------------------------------------
 *
 * All motion MUST derive exclusively from time:
 *
 *     const t = performance.now();
 *
 * No other inputs are permitted.
 *
 * ---------------------------------------------------------------
 * CHANGE CONTROL
 * ---------------------------------------------------------------
 *
 * Allowed changes:
 *    - Rendering performance improvements
 *    - Bug fixes
 *    - Visual correctness
 *
 * Forbidden changes:
 *    - Re-theming
 *    - Event-driven behavior
 *    - State coupling
 *    - Semantic signaling
 *
 * Any change that violates the above requires an explicit
 * architectural unlock.
 *
 * ---------------------------------------------------------------
 * PHILOSOPHY
 * ---------------------------------------------------------------
 *
 * The orb is a contained energy field, not an indicator.
 * It exists regardless of Nova's activity.
 * It does not observe, think, react, or respond.
 *
 * ================================================================
 */
