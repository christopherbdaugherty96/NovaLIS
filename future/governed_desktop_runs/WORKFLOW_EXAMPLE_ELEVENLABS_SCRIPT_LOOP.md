# Workflow Example — ElevenLabs Script Read / Voiceover Loop

This document describes how a future governed desktop run could support a script-to-voice workflow using ElevenLabs or a similar voice tool.

This is not current runtime behavior. It is a concrete design example for the governed desktop run model.

---

## User Goal

Generate voiceover audio from approved scripts while keeping NovaLIS governed.

Example request:

> Read the approved scripts, generate voiceovers in ElevenLabs, save the audio files, and stop.

---

## Important Boundary

NovaLIS should not be allowed to freely operate ElevenLabs, browser tabs, files, publishing tools, or accounts.

The run must be task-scoped:

> Generate voiceover files for specific approved scripts, save them to an approved folder, then stop.

---

## Workflow Type

Risk level: Medium by default.

Why medium:

- Uses an external service.
- May use paid account credits.
- Downloads generated files.
- Operates through browser or app automation.

It becomes high-risk if the workflow includes:

- purchasing credits
- changing account settings
- entering credentials
- uploading private files
- publishing content
- sending files externally

---

## Required Inputs

Before execution, NovaLIS needs:

- approved script folder or specific script files
- approved output folder
- approved voice/provider
- approved number of scripts
- approved naming convention
- allowed website/app surface
- timeout
- confirmation that no purchases or account changes are allowed

---

## Example Governed Run Envelope

```json
{
  "run_id": "generated_id",
  "intent": "generate_voiceovers_from_scripts",
  "goal": "Generate voiceover audio for approved script files using ElevenLabs and save the outputs locally.",
  "risk_level": "medium",
  "approved_steps": [
    "read approved script file list",
    "open ElevenLabs",
    "for each approved script: paste text, generate voice, download audio, save with approved filename",
    "stop after approved scripts are complete"
  ],
  "allowed_surfaces": [
    "approved_script_folder",
    "browser",
    "elevenlabs.io",
    "approved_output_folder"
  ],
  "allowed_actions": [
    "read_approved_script",
    "open_approved_url",
    "paste_approved_text",
    "click_generate_voice",
    "download_audio",
    "save_to_approved_folder",
    "rename_output_file"
  ],
  "blocked_actions": [
    "purchase",
    "account_change",
    "credential_entry",
    "publish",
    "send_message",
    "upload_unapproved_file",
    "browse_unrelated_site",
    "continue_after_completion"
  ],
  "required_approvals": [
    "start_run",
    "scope_expansion",
    "high_risk_action"
  ],
  "stop_conditions": [
    "all_approved_scripts_complete",
    "timeout",
    "user_cancel",
    "scope_violation",
    "executor_uncertain",
    "blocked_action_attempted"
  ],
  "timeout_seconds": 1200,
  "audit_level": "step_receipt"
}
```

---

## Trust Review Card Example

Before running, the user should see:

```text
Intent:
Generate voiceovers for approved scripts.

Allowed:
- Read scripts from approved folder
- Open ElevenLabs
- Paste script text
- Generate voice audio
- Download audio
- Save files to approved output folder

Blocked:
- Purchases
- Account changes
- Credential entry
- Publishing
- Unrelated browsing
- Uploading unrelated files
- Continuing after scripts are complete

Risk:
Medium

Stop:
When all approved scripts are processed, or if timeout/cancel/scope violation/uncertainty occurs.
```

---

## Step Loop

For each approved script:

1. Read script text.
2. Confirm script is inside approved folder/list.
3. Open or focus ElevenLabs.
4. Paste approved script text.
5. Generate audio.
6. Download audio.
7. Save or rename file inside approved output folder.
8. Log result.
9. Move to next approved script.
10. Stop when list is complete.

---

## Scope Rules

The run must pause or stop if:

- ElevenLabs requests login and credential entry is needed.
- The site asks to purchase credits.
- The output folder is unavailable.
- The script is outside the approved folder/list.
- The browser leaves the approved domain.
- A popup asks for account changes.
- The executor cannot identify the correct button or state.
- The script list is complete.

---

## Ledger / Receipt

The final receipt should include:

- run id
- approved script list
- output folder
- voice/provider used
- number of scripts attempted
- number of audio files generated
- files saved
- failures
- blocked actions
- stop reason

---

## Safer First Version

The first implementation should not operate ElevenLabs directly.

Safer first version:

1. Read approved scripts.
2. Produce a dry-run plan.
3. Show filenames and estimated steps.
4. Stop.

Second version:

1. Open ElevenLabs manually approved.
2. Process one script only.
3. Download one file.
4. Stop.

Only after that should multi-script looping be tested.

---

## Publishing Boundary

This workflow does not publish content.

Posting to YouTube, social platforms, or any public destination must be a separate high-risk workflow with final human approval.
