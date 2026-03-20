# Speech And Input Naturalness Plan
Date: 2026-03-20
Status: Planning packet only; post-Conversational-Core and Style-Layer design plan grounded in current `main`
Scope: Make Nova easier to talk to and easier for the user to talk to without changing authority, routing, or trust boundaries

## Core Rule
Nova should be easier to talk to, but not harder to trust.

That is the anchor sentence for this plan.

Nova may become better at:
- understanding casual phrasing
- understanding rough grammar and minor misspellings
- handling spoken-style fragments
- using lighter spoken acknowledgments and repair prompts

Nova may not become better at:
- guessing hidden execution intent
- widening command interpretation thresholds
- acting on ambiguous action requests without clarification
- sounding falsely confident about unclear input

## Why This Packet Exists
The current conversational baseline on `main` is now materially stronger:
- session-scoped thread handling
- adaptive presentation shaping
- bounded semantic/reference resolution
- short clarification discipline for weak anchors

That means the next practical improvement is not broader semantic ambition.
It is naturalness on both sides of the conversation.

There are two distinct needs here:
1. input tolerance
2. spoken-style output naturalness

This packet defines both as bounded presentation and interpretation improvements.
It does not authorize looser execution inference.
It does not authorize personality learning.

## Goal
Make Nova more forgiving of natural, informal, or imperfect input, and make Nova's short spoken responses feel more natural and less formal.

In plain language:
- users should not need formal grammar to be understood
- small mistakes should not break the interaction
- Nova should be able to say things like `Gotcha` or `Sure thing` in the right places
- explanations should still stay clear and grounded

## Two Layers

### 1. Input Tolerance
Nova should better tolerate:
- minor misspellings
- casual grammar
- speech fragments
- shorthand
- rough spoken phrasing
- incomplete but close-enough sentences

Examples:
- `whats that one do again`
- `say again`
- `show me that one`
- `do the simpler one`
- `turn that down a bit`

This should be achieved through:
- normalization
- tolerant parsing
- bounded reference resolution
- one short clarification when ambiguity matters

This should not be achieved through:
- wild guessing
- hidden intent inference
- silent authority expansion

### 2. Spoken Output Naturalness
Nova should sound less formal in short acknowledgments, repair prompts, and light follow-up offers.

Good examples:
- `Gotcha.`
- `Sure thing.`
- `Okay.`
- `Say that again?`
- `I can explain that more simply.`
- `Want the short version or the detailed one?`

Less good if overused:
- `Absolutely!`
- `Totally!`
- `No worries!`
- `Awesome!`
- `I'd love to!`

The target feel is:
- helpful human assistant
- calm and restrained
- lightly casual when appropriate
- not robotic
- not chirpy

## Output Style Boundary
Light casual phrasing should be used mostly for:
- acknowledgments
- repair prompts
- short clarifications
- short confirmations
- rewrite/help offers

Longer explanations should still be:
- clear
- grounded
- readable
- not stuffed with filler

Example:
- `Gotcha. A GPU is the part of the computer that handles graphics and parallel processing.`

This is better than:
- `Understood. A GPU is...`
- `Absolutely! Great question - a GPU is...`

## Input Tolerance Boundary
The key rule:
be forgiving on wording, strict on authority

Meaning:
- Nova can interpret rough phrasing for conversational intent
- Nova can normalize misspellings and spoken variants
- Nova must still clarify when action/execution requests are ambiguous

Examples:
- `say again?` -> repeat or rephrase the last answer
- `whats that one mean` -> resolve if the anchor is clear, otherwise clarify
- `turn that down a bit` -> only act if the governed interpretation is explicit enough; otherwise ask

## Surface Scope
This layer should apply to:
- input normalization for casual and spoken phrasing
- chat repair prompts
- short acknowledgments
- speech-oriented clarification language
- TTS-friendly phrasing for short responses

This layer should not redefine:
- governed action semantics
- confirmation requirements
- capability routing rules
- trust/failure truth
- policy wording that must remain exact

## Architectural Boundary
Speech and input naturalness should sit in the conversation and presentation layers, not in the authority layer.

Meaning:
- normalization may make input easier to interpret
- presentation may make output sound more natural
- Governor-mediated execution rules still decide what may happen

This layer must not:
- infer action intent beyond current governed thresholds
- bypass confirmation
- silently reinterpret ambiguous external-effect requests as authorized actions

## Safe Build Order

### Stage 1 - Input Tolerance Contract
Goal:
- define what kinds of informal input Nova should tolerate safely

Tasks:
- catalogue tolerated misspellings and spoken-style variants
- define the safe boundary between tolerant parsing and required clarification
- separate conversational tolerance from governed command certainty

Primary files:
- `nova_backend/src/conversation/response_style_router.py`
- `nova_backend/src/conversation/conversation_router.py`
- `nova_backend/src/skills/general_chat.py`

### Stage 2 - Spoken Acknowledgments And Repair Prompts
Goal:
- make short responses sound more natural without becoming chirpy

Tasks:
- allow light acknowledgments like `Gotcha` and `Sure thing`
- improve `say that again` / repair prompts
- keep longer explanations grounded and low-filler

Primary files:
- `nova_backend/src/conversation/response_formatter.py`
- `nova_backend/src/personality/interface_agent.py`
- `nova_backend/src/skills/general_chat.py`

### Stage 3 - Speech-Oriented Clarification And Repeat Behavior
Goal:
- improve what Nova does when spoken input is partially understood

Tasks:
- distinguish:
  - repeat request
  - rewrite request
  - weak semantic reference
  - ambiguous action request
- use one short clarification where needed

Primary files:
- `nova_backend/src/skills/general_chat.py`
- `nova_backend/src/brain_server.py`
- `nova_backend/src/conversation/response_formatter.py`

### Stage 4 - Evaluate Before Broadening
Goal:
- stop and assess whether Nova now feels easier to talk to in practice

Evaluation questions:
- does Nova understand rough input better without acting more loosely?
- do short acknowledgments sound natural without becoming generic assistant chatter?
- do repair prompts feel useful and brief?
- does trust remain intact when spoken/action requests are ambiguous?

## Proof Rule
Each slice should end with:
- one focused normalization or formatting proof
- one live chat/session proof when applicable
- no routing regression
- no authority regression
- a clean checkpoint commit

Recommended proof files:
- `nova_backend/tests/conversation/test_response_formatter.py`
- `nova_backend/tests/conversation/test_conversation_router.py`
- `nova_backend/tests/conversation/test_general_chat_tone.py`
- `nova_backend/tests/phase45/test_brain_server_basic_conversation.py`
- `nova_backend/tests/phase45/test_brain_server_tone_commands.py`

## Definition Of Done
This layer is in a good stopping state when:
- casual, slightly messy input is more often understood correctly
- short spoken replies feel lighter and more natural
- ambiguity still triggers brief clarification instead of unsafe guessing
- authority and routing rules are unchanged

It does not require:
- speech-recognition model changes
- adaptive personality
- user-specific voice learning
- broader action inference

## Explicit Non-Goals
This plan does not include:
- personality learning
- silent style drift
- autonomous conversation steering
- broader execution authority
- changing the Governor threshold for ambiguous actions

## Practical Next Slice
If coding starts from this packet, the best first bounded slice is:
- define the input tolerance contract for casual phrasing, misspellings, and spoken fragments

After that:
- light spoken acknowledgments and repair prompts
- speech-oriented clarification behavior
