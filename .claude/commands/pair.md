---
description: Run pair programming mode (DEV + REVIEWER interleaved)
argument-hint: <story-key>
---

Run Devflow pair programming for: $ARGUMENTS

Execute: `npx @pjmendonca/devflow pair $ARGUMENTS`

This runs DEV and REVIEWER in an interleaved pair programming mode:
- DEV implements code in small, reviewable chunks
- REVIEWER provides immediate feedback after each chunk
- DEV addresses issues before continuing to next chunk
- Results in higher quality code with fewer late-stage revisions

Benefits:
- Real-time feedback loops during implementation
- Issues caught early, not at final review
- Better knowledge sharing between agents
- Higher approval rates

Example:
- `/pair 3-5` - Run pair programming for story 3-5

