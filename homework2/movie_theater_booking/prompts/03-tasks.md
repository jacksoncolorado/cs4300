# Prompt 3 — Break it into tasks

> 📖 **Book:** test-first tasks and red–green–refactor are [§2.3.2 test-driven development (TDD)](https://www.swebook.org/chapters/02-software-development-processes/index.html#232-testing-make-it-central-to-development); "every acceptance criterion (AC) is covered" is [§3.4.4 traceability](https://www.swebook.org/chapters/03-user-requirements/index.html#344-tracing-requirements-to-tests-and-backlog-items).

```
Read specs/<NNN-feature>/spec.md and plan.md. Fill in specs/<NNN-feature>/tasks.md.

Rules:
- Each task is one small test-first increment: write one test, and if the behavior is missing,
  watch it fail (red), then write the code that passes it (green), then clean up (refactor).
  If the test passes as soon as it's written, say so; it's a verification test, not a red→green cycle.
- Each task touches as few files as possible and fits in one small commit.
- Order them so the app still runs after every task (build from the models up).
- Each task names its test and the acceptance criterion it covers (AC-#).
- Every acceptance criterion (AC) in the spec must be covered by at least one task.
Don't write code yet.
```
