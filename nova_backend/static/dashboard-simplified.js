/*
 * Task 1.3 — UI overload reduction runtime.
 *
 * Applies `nova-simplified` to <body> unless the user has opted out.
 * Injects a hamburger toggle (for nav) and a "Show full UI" toggle
 * (for widgets) into the header. Both persist to localStorage.
 *
 * Keep this file minimal and independent of the rest of dashboard.js —
 * it must run even if a later script errors.
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'nova.simplified';
  var NAV_OPEN_CLASS = 'nova-nav-open';
  var SIMPLIFIED_CLASS = 'nova-simplified';

  function readPref() {
    try {
      var raw = window.localStorage.getItem(STORAGE_KEY);
      // Default: simplified ON. Only explicit "false" opts out.
      if (raw === 'false') { return false; }
      return true;
    } catch (_) {
      return true;
    }
  }

  function writePref(value) {
    try { window.localStorage.setItem(STORAGE_KEY, value ? 'true' : 'false'); } catch (_) {}
  }

  function applyPref(simplified) {
    document.body.classList.toggle(SIMPLIFIED_CLASS, simplified);
    var toggle = document.getElementById('nova-ui-toggle');
    if (toggle) {
      toggle.textContent = simplified ? 'Show full UI' : 'Simplify';
      toggle.setAttribute('aria-pressed', simplified ? 'true' : 'false');
    }
  }

  function mountControls() {
    var header = document.querySelector('.header .header-left') || document.querySelector('.header');
    if (!header) { return; }

    // Hamburger — toggles nav visibility in simplified mode.
    if (!document.getElementById('nova-nav-toggle')) {
      var hamburger = document.createElement('button');
      hamburger.id = 'nova-nav-toggle';
      hamburger.className = 'nova-nav-toggle';
      hamburger.type = 'button';
      hamburger.setAttribute('aria-label', 'Toggle navigation');
      hamburger.textContent = '\u2630'; // ☰
      hamburger.addEventListener('click', function () {
        document.body.classList.toggle(NAV_OPEN_CLASS);
      });
      header.insertBefore(hamburger, header.firstChild);
    }

    // "Simplify / Show full UI" toggle — placed on the right side.
    var right = document.querySelector('.header-right .header-utility-strip') ||
                document.querySelector('.header-right') ||
                document.querySelector('.header');
    if (right && !document.getElementById('nova-ui-toggle')) {
      var btn = document.createElement('button');
      btn.id = 'nova-ui-toggle';
      btn.className = 'nova-ui-toggle';
      btn.type = 'button';
      btn.addEventListener('click', function () {
        var next = !document.body.classList.contains(SIMPLIFIED_CLASS);
        writePref(next);
        applyPref(next);
      });
      right.appendChild(btn);
    }
  }

  function updateActivePageAttribute() {
    var pages = document.querySelectorAll('[id^="page-"]');
    for (var i = 0; i < pages.length; i++) {
      if (!pages[i].hidden) {
        document.body.setAttribute('data-nova-page', pages[i].id.replace('page-', ''));
        return;
      }
    }
  }

  function trackActivePage() {
    // Watch which page is visible so CSS can selectively un-hide widgets
    // (e.g. show #news-widget when the user navigates to News).
    // Pages are sections like #page-news whose `hidden` attribute toggles.
    var observer = new MutationObserver(function () {
      updateActivePageAttribute();
    });
    var main = document.querySelector('.main') || document.body;
    observer.observe(main, { attributes: true, subtree: true, attributeFilter: ['hidden'] });
    updateActivePageAttribute();
  }

  function init() {
    var simplified = readPref();
    applyPref(simplified);
    mountControls();
    trackActivePage();
    // Re-apply once more in case dashboard.js re-renders the header
    // after mount. Cheap insurance.
    setTimeout(function () { applyPref(document.body.classList.contains(SIMPLIFIED_CLASS)); }, 500);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
