# Tasks: <Feature name>

**Plan:** [plan.md](plan.md)

> Each task is one small test-first increment and one commit: red → green → refactor when the behavior is missing,
> or a verification test if it already passes. Do them in order.
> Each task names its test and the acceptance criterion (AC-#) it covers.
> Codex ticks the box when the task's tests pass. **You** commit.
>
> 📖 **Book:** red → green → refactor is test-driven development (TDD), [§2.3.2](https://www.swebook.org/chapters/02-software-development-processes/index.html#232-testing-make-it-central-to-development).

- [ ] **T1** — <what> · test: `<test name>` · covers: AC-?
- [ ] **T2** — …
- [ ] **T3** — …

## Done when
- [ ] Every acceptance criterion in `spec.md` has a passing test
- [ ] Full suite green: `python manage.py test`
- [ ] `python manage.py behave` passes
- [ ] Coverage ≥ 80%
- [ ] `AI-USAGE.md` updated
