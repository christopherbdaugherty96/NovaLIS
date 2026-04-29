# Screenshot Capture Instructions

Screenshots were not captured during this pass.

To capture manually:

1. Start Nova locally:

   ```powershell
   cd C:\Nova-Project\nova_backend
   python -m uvicorn src.brain_server:app --host 127.0.0.1 --port 8000 --app-dir .
   ```

2. Open the dashboard at:

   ```text
   http://127.0.0.1:8000
   ```

3. Capture:

   - dashboard loaded
   - Chat page before prompt
   - response to `Can memory authorize actions?`
   - response to `What are the latest major AI model releases? Search with sources.`
   - response to `Draft an email to test@example.com about tomorrow's meeting.`
   - Trust/receipts page after governed prompts

4. Save screenshots in:

   ```text
   docs/demo_proof/brain_live_test/screenshots/
   ```

Do not add placeholder or fake screenshots.
