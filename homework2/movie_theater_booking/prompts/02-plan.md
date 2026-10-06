# Prompt 2 — Draft the plan

> 📖 **Book:** the Plan phase of [§13.5 Spec-Driven Development](https://www.swebook.org/chapters/13-ai-across-the-lifecycle/index.html#135-spec-driven-development); Django's Model-Template-View (MTV) pattern draws on the separation of concerns in [§7.3 Model-View-Controller](https://www.swebook.org/chapters/07-architectural-patterns/index.html#73-user-interfaces-model-view-controller), and the API is [§7.5.4 RESTful APIs](https://www.swebook.org/chapters/07-architectural-patterns/index.html#754-restful-apis).

```
Read AGENTS.md and specs/<NNN-feature>/spec.md. Look at the existing code so the plan fits
what's already here.

Fill in specs/<NNN-feature>/plan.md using its template. Rules:
- Every model field, endpoint and test must reference the acceptance criterion it serves (AC-#).
- Anything not traceable to the spec doesn't go in the plan.
- In "Approach," name one alternative you rejected and why.
- Don't write any application code yet.

Then list anything in the plan you're unsure about.
```

**After Codex answers:** read the plan and ask about anything you can't explain, for example
*"Why a separate model for X instead of a field?"* Edit it, then commit.
