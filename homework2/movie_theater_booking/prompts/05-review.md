# Prompt 5 — Review the feature against the spec

> 📖 **Book:** [§9.3 code reviews](https://www.swebook.org/chapters/09-static-checking/index.html#93-code-reviews-check-intent-and-trust), [§13.7.2 the generator and the evaluator](https://www.swebook.org/chapters/13-ai-across-the-lifecycle/index.html#1372-the-generator-and-the-evaluator), [§10.3 code coverage](https://www.swebook.org/chapters/10-testing/index.html#103-code-coverage-i-white-box-testing), [§10.1.3 test adequacy](https://www.swebook.org/chapters/10-testing/index.html#1013-test-adequacy-deciding-when-to-stop).

**Run this review in a fresh Codex session that did not implement the feature.** The book's point in
§13.7.2 is that the evaluator must not be the generator: a session that wrote the code tends to approve it.

```
Read specs/<NNN-feature>/spec.md. Don't change any code.

For every acceptance criterion, report:
- ✅ met: name the test that proves it
- ⚠️ partial: what's missing
- ❌ not met

Then list:
- Behavior in the code that is NOT in the spec (scope creep)
- Edge cases with no test
- Places where plan.md and the code disagree
- Anything a code reviewer would flag (naming, duplication, missing docstrings, security)
```

**Then you:** fix the gaps (each fix is a new task), run `coverage report` and `python manage.py behave`, and
work through the "Before you submit" checklist in README.md.
