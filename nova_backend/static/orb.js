// ============================================
// NOVA ORB - Stabilized ambient presence
// Contained energy / core visual with no state coupling
// ============================================

(function () {
  const canvas = document.getElementById("nova-orb");
  if (!canvas) return;

  const ctx = canvas.getContext("2d", { alpha: true, desynchronized: true });
  if (!ctx) return;

  const field = {
    t: 0,
    lastTs: 0,
    dpr: 1,
    width: 0,
    height: 0,
    reduceMotion: window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches
  };

  function noise(t, a, b, c) {
    return Math.sin(t * a) * 0.5 + Math.sin(t * b) * 0.3 + Math.sin(t * c) * 0.2;
  }

  function resizeCanvas() {
    const rect = canvas.getBoundingClientRect();
    field.dpr = Math.min(window.devicePixelRatio || 1, 2);
    field.width = rect.width;
    field.height = rect.height;
    canvas.width = Math.max(1, Math.floor(rect.width * field.dpr));
    canvas.height = Math.max(1, Math.floor(rect.height * field.dpr));
    ctx.setTransform(field.dpr, 0, 0, field.dpr, 0, 0);
  }

  function drawOrb(t) {
    const w = field.width;
    const h = field.height;
    const cx = w * 0.5;
    const cy = h * 0.5;
    const baseR = Math.min(w, h) * 0.36;

    // very low-amplitude, slow drift (stabilized presence)
    const driftX = noise(t * 0.035, 0.07, 0.11, 0.18) * baseR * 0.01;
    const driftY = noise(t * 0.031, 0.06, 0.10, 0.16) * baseR * 0.01;
    const radius = baseR * (1 + noise(t * 0.021, 0.05, 0.08, 0.13) * 0.006);

    const x = cx + driftX;
    const y = cy + driftY;

    ctx.clearRect(0, 0, w, h);

    // ambient containment bloom
    const halo = ctx.createRadialGradient(x, y, radius * 0.32, x, y, radius * 1.8);
    halo.addColorStop(0, "rgba(40, 84, 156, 0.18)");
    halo.addColorStop(0.5, "rgba(30, 60, 118, 0.10)");
    halo.addColorStop(0.8, "rgba(58, 44, 74, 0.07)");
    halo.addColorStop(1, "rgba(5, 6, 10, 0)");
    ctx.fillStyle = halo;
    ctx.beginPath();
    ctx.arc(x, y, radius * 1.8, 0, Math.PI * 2);
    ctx.fill();

    // stable primary body (deep electric blue → violet base)
    const body = ctx.createRadialGradient(
      x - radius * 0.18,
      y - radius * 0.24,
      radius * 0.02,
      x,
      y,
      radius
    );
    body.addColorStop(0, "rgba(72, 120, 194, 0.85)");
    body.addColorStop(0.34, "rgba(28, 66, 132, 0.92)");
    body.addColorStop(0.72, "rgba(14, 36, 84, 0.95)");
    body.addColorStop(1, "rgba(45, 31, 63, 0.92)");

    ctx.fillStyle = body;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fill();

    // subtle internal density layers (convection-like, non-readable)
    ctx.save();
    ctx.beginPath();
    ctx.arc(x, y, radius * 0.985, 0, Math.PI * 2);
    ctx.clip();

    const layerAOffset = noise(t * 0.028, 0.04, 0.07, 0.11) * radius * 0.025;
    const layerAGrad = ctx.createLinearGradient(x - radius, y - radius + layerAOffset, x + radius, y + radius + layerAOffset);
    layerAGrad.addColorStop(0, "rgba(130, 182, 255, 0)");
    layerAGrad.addColorStop(0.48, "rgba(118, 170, 246, 0.11)");
    layerAGrad.addColorStop(0.52, "rgba(118, 170, 246, 0.15)");
    layerAGrad.addColorStop(1, "rgba(130, 182, 255, 0)");
    ctx.fillStyle = layerAGrad;
    ctx.fillRect(x - radius, y - radius, radius * 2, radius * 2);

    const layerBOffset = noise(t * 0.024, 0.03, 0.06, 0.09) * radius * 0.02;
    const layerBGrad = ctx.createLinearGradient(x - radius, y + radius + layerBOffset, x + radius, y - radius + layerBOffset);
    layerBGrad.addColorStop(0, "rgba(112, 96, 154, 0)");
    layerBGrad.addColorStop(0.48, "rgba(112, 96, 154, 0.08)");
    layerBGrad.addColorStop(0.52, "rgba(126, 108, 168, 0.12)");
    layerBGrad.addColorStop(1, "rgba(112, 96, 154, 0)");
    ctx.fillStyle = layerBGrad;
    ctx.fillRect(x - radius, y - radius, radius * 2, radius * 2);

    ctx.restore();

    // contained core nucleus (denser center, no pulse)
    const coreR = radius * 0.52;
    const core = ctx.createRadialGradient(
      x,
      y,
      0,
      x,
      y,
      coreR
    );
    core.addColorStop(0, "rgba(244, 249, 255, 0.30)");
    core.addColorStop(0.42, "rgba(178, 205, 246, 0.16)");
    core.addColorStop(1, "rgba(74, 124, 200, 0)");
    ctx.fillStyle = core;
    ctx.beginPath();
    ctx.arc(x, y, coreR, 0, Math.PI * 2);
    ctx.fill();

    // faint containment edge
    ctx.strokeStyle = "rgba(224, 240, 255, 0.085)";
    ctx.lineWidth = 0.65;
    ctx.beginPath();
    ctx.arc(x, y, radius * 0.997, 0, Math.PI * 2);
    ctx.stroke();
  }

  function drawReduced() {
    const w = field.width;
    const h = field.height;
    const x = w * 0.5;
    const y = h * 0.5;
    const r = Math.min(w, h) * 0.36;

    ctx.clearRect(0, 0, w, h);
    const g = ctx.createRadialGradient(x, y, r * 0.05, x, y, r);
    g.addColorStop(0, "rgba(92, 144, 220, 0.62)");
    g.addColorStop(0.72, "rgba(18, 48, 102, 0.86)");
    g.addColorStop(1, "rgba(58, 44, 74, 0.9)");

    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fill();

    ctx.strokeStyle = "rgba(224, 240, 255, 0.08)";
    ctx.lineWidth = 0.65;
    ctx.beginPath();
    ctx.arc(x, y, r * 0.997, 0, Math.PI * 2);
    ctx.stroke();
  }

  function loop(ts) {
    if (!field.lastTs) field.lastTs = ts;
    const dt = Math.min((ts - field.lastTs) / 1000, 0.05);
    field.lastTs = ts;
    field.t += dt;

    if (field.reduceMotion) {
      drawReduced();
      return;
    }

    drawOrb(field.t);
    requestAnimationFrame(loop);
  }

  function init() {
    resizeCanvas();
    window.addEventListener("resize", resizeCanvas, { passive: true });

    if (field.reduceMotion) {
      drawReduced();
      return;
    }

    requestAnimationFrame(loop);
  }

  init();
})();
