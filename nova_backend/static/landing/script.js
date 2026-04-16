/*
 * Nova landing page — waitlist submission (Task 1.5).
 *
 * Submits to Formspree (https://formspree.io) so we don't need a
 * server-side endpoint. To activate:
 *
 *   1. Sign up at https://formspree.io (free tier: 50 submissions/mo).
 *   2. Create a new form, copy the endpoint URL (looks like
 *      https://formspree.io/f/xxxxxxxx).
 *   3. Replace the FORM_ENDPOINT constant below.
 *   4. (Optional) In the Formspree settings, set the "Allowed Domain"
 *      to the domain you publish this page on.
 *
 * Until the endpoint is replaced, the form falls back to a graceful
 * "we're not collecting yet" message instead of throwing.
 */
(function () {
  'use strict';

  // TODO(Tier 1.5 activation): replace with real Formspree endpoint.
  var FORM_ENDPOINT = 'https://formspree.io/f/REPLACE_WITH_REAL_ID';

  var form = document.getElementById('waitlist-form');
  var email = document.getElementById('waitlist-email');
  var submit = document.getElementById('waitlist-submit');
  var status = document.getElementById('waitlist-status');

  function setStatus(message, kind) {
    status.textContent = message || '';
    status.classList.remove('success', 'error');
    if (kind) { status.classList.add(kind); }
  }

  function isValidEmail(value) {
    // Permissive: one @, a dot after it, no spaces. Server will do the
    // authoritative check.
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    var value = (email.value || '').trim();
    if (!isValidEmail(value)) {
      setStatus('Please enter a valid email address.', 'error');
      email.focus();
      return;
    }

    if (FORM_ENDPOINT.indexOf('REPLACE_WITH_REAL_ID') !== -1) {
      // Not yet configured — don't pretend to save.
      setStatus(
        "Thanks! The waitlist isn't live yet. Check back soon, or follow the repo on GitHub.",
        'success'
      );
      submit.disabled = true;
      return;
    }

    submit.disabled = true;
    setStatus('Sending…');

    fetch(FORM_ENDPOINT, {
      method: 'POST',
      headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: value, source: 'nova-landing' }),
    })
      .then(function (response) {
        if (response.ok) {
          setStatus("You're on the list. We'll email when the installer is ready.", 'success');
          form.reset();
        } else {
          return response.json().then(function (data) {
            var msg = (data && data.errors && data.errors[0] && data.errors[0].message) ||
                      'Something went wrong. Please try again.';
            setStatus(msg, 'error');
            submit.disabled = false;
          }).catch(function () {
            setStatus('Something went wrong. Please try again.', 'error');
            submit.disabled = false;
          });
        }
      })
      .catch(function () {
        setStatus('Network error. Please try again.', 'error');
        submit.disabled = false;
      });
  });
})();
