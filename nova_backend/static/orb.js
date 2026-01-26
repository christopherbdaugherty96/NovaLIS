// ============================================
// NOVA ORB - Phase-3 Compliant (Visual Only)
// Contract: No interaction, no anthropomorphism, no semantic states
// ============================================

(function () {
  // Phase-3: Single anonymous internal state only
  const orbField = { t: 0, lastTs: 0 };
  
  // Canvas setup
  const canvas = document.getElementById("nova-orb");
  if (!canvas) return;
  
  const ctx = canvas.getContext("2d");
  
  // Phase-3: No interaction listeners
  // No mouse/touch/pointer/keyboard events
  // No exported API, no public functions
  
  // ==================== INITIALIZATION ====================
  
  function init() {
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    requestAnimationFrame(loop);
  }
  
  function resizeCanvas() {
    const rect = canvas.getBoundingClientRect();
    
    // Clamp DPR scaling for consistent performance
    const maxDPR = 2;
    const rawDPR = window.devicePixelRatio || 1;
    const dpr = Math.min(rawDPR, maxDPR);
    
    canvas.width = Math.floor(rect.width * dpr);
    canvas.height = Math.floor(rect.height * dpr);
    
    // Reset transform to avoid cumulative scaling (edge-case safety)
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.scale(dpr, dpr);
  }
  
  // ==================== DETERMINISTIC VISUAL MATH ====================
  
  // Simple deterministic noise for organic motion (no external inputs)
  function simpleNoise(t, frequency = 0.5) {
    return Math.sin(t * frequency) * 0.5 + 
           Math.sin(t * frequency * 1.7) * 0.3 + 
           Math.sin(t * frequency * 2.3) * 0.2;
  }
  
  // Phase-3: No semantic states, only time-based transforms
  function calculateVisuals(t, width, height) {
    const cx = width / 2;
    const cy = height / 2;
    const baseR = Math.min(width, height) * 0.4;
    
    // Deterministic motion: slow drift
    const driftX = simpleNoise(t * 0.2, 0.3) * 8;
    const driftY = simpleNoise(t * 0.25, 0.35) * 6;
    
    // Deterministic pulse: non-rhythmic, gentle
    const pulse = 1 + simpleNoise(t * 0.3, 0.4) * 0.08;
    
    return {
      centerX: cx + driftX,
      centerY: cy + driftY,
      radius: baseR * pulse,
      coreRadius: baseR * 0.6 * pulse,
      // Phase-3: Fixed visual identity (blue energy field)
      // No state-dependent color changes
      hue: 220,
      saturation: 100,
      lightness: 70
    };
  }
  
  // ==================== RENDERING ====================
  
  function drawFrame(t, dt) {
    const { width, height } = canvas.getBoundingClientRect();
    const vis = calculateVisuals(t, width, height);
    
    // Clear with subtle fade for motion trail
    ctx.fillStyle = 'rgba(5, 5, 20, 0.1)';
    ctx.fillRect(0, 0, width, height);
    
    // Outer glow (energy field)
    const gradient = ctx.createRadialGradient(
      vis.centerX, vis.centerY, vis.radius * 0.3,
      vis.centerX, vis.centerY, vis.radius * 2
    );
    
    gradient.addColorStop(0, `hsla(${vis.hue}, ${vis.saturation}%, ${vis.lightness}%, 0.5)`);
    gradient.addColorStop(0.5, `hsla(${vis.hue + 20}, ${vis.saturation}%, ${vis.lightness + 20}%, 0.2)`);
    gradient.addColorStop(1, 'hsla(0, 0%, 0%, 0)');
    
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(vis.centerX, vis.centerY, vis.radius * 2, 0, Math.PI * 2);
    ctx.fill();
    
    // Main orb body
    const orbGradient = ctx.createRadialGradient(
      vis.centerX - vis.radius * 0.2, 
      vis.centerY - vis.radius * 0.2, 
      0,
      vis.centerX, 
      vis.centerY, 
      vis.radius
    );
    
    orbGradient.addColorStop(0, `hsla(${vis.hue}, ${vis.saturation}%, ${vis.lightness}%, 0.9)`);
    orbGradient.addColorStop(0.7, `hsla(${vis.hue + 30}, ${vis.saturation}%, ${vis.lightness + 10}%, 0.6)`);
    orbGradient.addColorStop(1, 'hsla(0, 0%, 0%, 0)');
    
    ctx.fillStyle = orbGradient;
    ctx.beginPath();
    ctx.arc(vis.centerX, vis.centerY, vis.radius, 0, Math.PI * 2);
    ctx.fill();
    
    // Inner core (subtle wobble)
    const coreWobbleX = simpleNoise(t * 1.5, 0.8) * vis.radius * 0.08;
    const coreWobbleY = simpleNoise(t * 1.3, 0.7) * vis.radius * 0.08;
    
    const coreGradient = ctx.createRadialGradient(
      vis.centerX + coreWobbleX, 
      vis.centerY + coreWobbleY, 
      0,
      vis.centerX, 
      vis.centerY, 
      vis.coreRadius
    );
    
    coreGradient.addColorStop(0, 'hsla(0, 0%, 100%, 0.9)');
    coreGradient.addColorStop(0.5, `hsla(${vis.hue + 30}, ${vis.saturation}%, ${vis.lightness + 10}%, 0.7)`);
    coreGradient.addColorStop(1, 'hsla(0, 0%, 0%, 0)');
    
    ctx.fillStyle = coreGradient;
    ctx.beginPath();
    ctx.arc(vis.centerX, vis.centerY, vis.coreRadius, 0, Math.PI * 2);
    ctx.fill();
  }
  
  // ==================== ANIMATION LOOP ====================
  
  function loop(ts) {
    if (!orbField.lastTs) orbField.lastTs = ts;
    const dt = (ts - orbField.lastTs) / 1000;
    orbField.lastTs = ts;
    orbField.t += dt;
    
    drawFrame(orbField.t, dt);
    requestAnimationFrame(loop);
  }
  
  // ==================== START ====================
  
  // Phase-3: No initialization of interaction, no state setting
  // Just start the visual animation loop
  init();
})();