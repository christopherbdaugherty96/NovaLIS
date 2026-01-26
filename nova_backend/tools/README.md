\# Runtime Tools (Not Committed)



This directory contains \*\*local runtime dependencies\*\* and is intentionally

excluded from version control.



\## ffmpeg



Nova uses ffmpeg for audio preprocessing.



\### Install (Windows)



1\. Download ffmpeg (essentials build):

&nbsp;  https://www.gyan.dev/ffmpeg/builds/



2\. Extract to:

&nbsp;  nova\_backend/tools/ffmpeg/



3\. Ensure `ffmpeg.exe` is available at runtime or on PATH.



\## Models



Speech models (e.g. Vosk) must be downloaded locally.



They are intentionally excluded from the repo to:

\- reduce repo size

\- avoid licensing ambiguity

\- keep builds reproducible



See documentation for model download instructions.



