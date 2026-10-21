# D1 Gate 0 — bundled Windows toast library

Date: 2026-10-21  
Machine: Samsung 730QDA, Windows 11 Home 10.0.26200  
Account: standard, non-elevated user  
Result: **PASS**

## Selected and pinned package set

- `Windows-Toasts==1.3.1`
- `winrt-runtime==3.2.1`
- `winrt-Windows.Data.Xml.Dom==3.2.1`
- `winrt-Windows.Foundation==3.2.1`
- `winrt-Windows.Foundation.Collections==3.2.1`
- `winrt-Windows.UI.Notifications==3.2.1`
- `typing_extensions==4.16.0`

The exact wheels were downloaded once, then installed into a fresh Python 3.10 virtual environment with `--no-index --find-links <local wheelhouse>`. The account token reported `elevated=False`; installation and notification display required no administrator rights.

## Size

- Complete offline wheelhouse: **857,853 bytes** (approximately 838 KiB).
- Installed package files, including all WinRT support packages and metadata: **2,968,291 bytes** (approximately 2.83 MiB).

The installed total excludes the virtual environment's copies of pip and setuptools; it includes `windows_toasts`, every required `winrt` projection/runtime, `typing_extensions`, and their distribution metadata.

## License evidence from installed files

`windows_toasts-1.3.1.dist-info/licenses/LICENSE` begins:

> Apache License  
> Version 2.0, January 2004  
> TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

Each installed WinRT distribution's `METADATA` contains:

> License-Expression: MIT

`typing_extensions-4.16.0.dist-info/licenses/LICENSE` contains the Python Software Foundation licence history and terms; its installed metadata identifies the expression as `PSF-2.0`.

Production bundling must retain the installed licence files/notices.

## Execution-boundary check

A source scan of `windows_toasts` found no PowerShell, `subprocess`, `os.system`, socket, requests, or HTTP-client execution path. Its `urllib` imports are URL/path parsing only. The probe used the Python package directly and created no subprocess.

## Owner-watched visibility proof

First probe:

- Windows accepted the library call with no failure callback.
- The owner was not watching the banner.
- The owner later verified `Nova reminder test` in Win + N, grouped under sender **Nova**.

Second probe:

- Do Not Disturb was turned off first.
- Announced target: 12:37:30 PM ET.
- Actual library submission: 12:37:34 PM ET (four seconds of interpreter/process startup delay).
- Title: `Nova reminder test 2`.
- Library failure callbacks: none.
- Owner observed the bottom-right banner: **yes**.
- Sender shown: **Nova**.
- Retained in Win + N afterward: **yes**.

This establishes the Gate 0 requirement that a real Windows notification from the bundled library is visible on the owner's laptop.

## Gate result

Gate 0 passes. D1 may build on this exact pinned package set. A failure of the production adapter or packaged/offline installer remains blocking; PowerShell is not an authorized fallback.

