(function () {
  const canvas = document.getElementById("nova-orb");
  const container = document.getElementById("orb-container");
  if (!canvas || !container) return;

  const ctx = canvas.getContext("2d", { alpha: true, desynchronized: true });
  if (!ctx) return;

  const reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const state = {
    t: 0,
    last: 0,
    dpr: 1,
    width: 0,
    height: 0,
  };

  function resize() {
    const rect = canvas.getBoundingClientRect();
    state.dpr = Math.min(window.devicePixelRatio || 1, 2);
    state.width = Math.max(1, rect.width);
    state.height = Math.max(1, rect.height);
    canvas.width = Math.floor(state.width * state.dpr);
    canvas.height = Math.floor(state.height * state.dpr);
    ctx.setTransform(state.dpr, 0, 0, state.dpr, 0, 0);
  }

  function mix(a, b, t) {
    return a + (b - a) * t;
  }

  function oscillate(t, a, b, c) {
    return Math.sin(t * a) * 0.52 + Math.sin(t * b) * 0.31 + Math.sin(t * c) * 0.17;
  }

  function getStateProfile() {
    return {
      glow: "rgba(104, 177, 255, 0.2)",
      rim: "rgba(163, 210, 255, 0.28)",
      coreA: "rgba(150, 210, 255, 0.86)",
      coreB: "rgba(44, 96, 156, 0.95)",
      drift: 0.72,
      pulse: 1.0,
    };
  }

  function drawFrame(t) {
    const profile = getStateProfile();
    const w = state.width;
    const h = state.height;
    const cx = w * 0.5;
    const cy = h * 0.5;
    const base = Math.min(w, h) * 0.34;

    const driftScale = reduceMotion ? 0 : profile.drift;
    const dx = oscillate(t * 0.34, 0.08, 0.13, 0.19) * base * 0.03 * driftScale;
    const dy = oscillate(t * 0.29, 0.07, 0.11, 0.17) * base * 0.026 * driftScale;
    const pulse = reduceMotion ? 1 : mix(0.992, 1.018 * profile.pulse, (Math.sin(t * 0.8) + 1) * 0.5);
    const radius = base * pulse;
    const x = cx + dx;
    const y = cy + dy;

    ctx.clearRect(0, 0, w, h);

    const halo = ctx.createRadialGradient(x, y, radius * 0.34, x, y, radius * 1.95);
    halo.addColorStop(0, profile.glow);
    halo.addColorStop(0.56, "rgba(66, 118, 190, 0.08)");
    halo.addColorStop(1, "rgba(3, 8, 18, 0)");
    ctx.fillStyle = halo;
    ctx.beginPath();
    ctx.arc(x, y, radius * 1.95, 0, Math.PI * 2);
    ctx.fill();

    const body = ctx.createRadialGradient(
      x - radius * 0.24,
      y - radius * 0.26,
      radius * 0.03,
      x,
      y,
      radius
    );
    body.addColorStop(0, profile.coreA);
    body.addColorStop(0.35, "rgba(66, 144, 222, 0.82)");
    body.addColorStop(0.72, profile.coreB);
    body.addColorStop(1, "rgba(24, 47, 90, 0.94)");

    ctx.fillStyle = body;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fill();

    ctx.save();
    ctx.beginPath();
    ctx.arc(x, y, radius * 0.985, 0, Math.PI * 2);
    ctx.clip();

    const waveA = ctx.createLinearGradient(x - radius, y - radius, x + radius, y + radius);
    waveA.addColorStop(0, "rgba(190, 231, 255, 0)");
    waveA.addColorStop(0.5, "rgba(181, 226, 255, 0.14)");
    waveA.addColorStop(1, "rgba(190, 231, 255, 0)");
    ctx.fillStyle = waveA;
    const yShiftA = oscillate(t * 0.22, 0.05, 0.09, 0.12) * radius * 0.08;
    ctx.fillRect(x - radius, y - radius + yShiftA, radius * 2, radius * 2);

    const waveB = ctx.createLinearGradient(x - radius, y + radius, x + radius, y - radius);
    waveB.addColorStop(0, "rgba(124, 163, 228, 0)");
    waveB.addColorStop(0.5, "rgba(124, 163, 228, 0.12)");
    waveB.addColorStop(1, "rgba(124, 163, 228, 0)");
    ctx.fillStyle = waveB;
    const yShiftB = oscillate(t * 0.19, 0.04, 0.08, 0.11) * radius * 0.06;
    ctx.fillRect(x - radius, y - radius + yShiftB, radius * 2, radius * 2);

    ctx.restore();

    const core = ctx.createRadialGradient(x, y, 0, x, y, radius * 0.58);
    core.addColorStop(0, "rgba(246, 251, 255, 0.34)");
    core.addColorStop(0.45, "rgba(193, 222, 255, 0.17)");
    core.addColorStop(1, "rgba(90, 152, 226, 0)");
    ctx.fillStyle = core;
    ctx.beginPath();
    ctx.arc(x, y, radius * 0.58, 0, Math.PI * 2);
    ctx.fill();

    ctx.strokeStyle = profile.rim;
    ctx.lineWidth = 0.8;
    ctx.beginPath();
    ctx.arc(x, y, radius * 0.996, 0, Math.PI * 2);
    ctx.stroke();
  }

  function frame(ts) {
    if (!state.last) state.last = ts;
    const dt = Math.min((ts - state.last) / 1000, 0.05);
    state.last = ts;
    state.t += dt;
    drawFrame(state.t);
    requestAnimationFrame(frame);
  }

  resize();
  window.addEventListener("resize", resize, { passive: true });
  requestAnimationFrame(frame);
})();
