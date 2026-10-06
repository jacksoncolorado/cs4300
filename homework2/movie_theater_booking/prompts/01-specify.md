# Prompt 1 — Review my spec

> 📖 **Book:** what a reviewer checks for: [§3.4.1 user stories and Given/When/Then](https://www.swebook.org/chapters/03-user-requirements/index.html#341-guidelines-for-effective-user-stories), [§3.1.2 requirements challenges](https://www.swebook.org/chapters/03-user-requirements/index.html#312-requirements-challenges) (ambiguity).

Paste into Codex, replacing `<NNN-feature>`:

```
Read AGENTS.md, then read specs/<NNN-feature>/spec.md. I wrote this spec. Do NOT write code
and do NOT rewrite the spec for me.

Review it like a senior engineer and give me:
1. Ambiguities: places where two developers could reasonably build different things.
2. Missing acceptance criteria, especially error cases, edge cases and empty states.
3. Acceptance criteria that can't be tested as written, and why.
4. Anything that describes HOW (implementation) instead of WHAT (behavior).
5. Anything that conflicts with, or is missing from, the Homework 2 (HW2) requirements
   (https://tghastings.github.io/cs4300andcs5300/homework_2.pdf).
6. Up to 5 questions I should answer before planning.

Keep it to a numbered list. I'll decide what to change.
```
