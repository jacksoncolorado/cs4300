# HW2 with Codex: Spec-Driven Development Template

**Optional.** Use this if you want to build **Homework 2 (HW2): Movie Theater Booking** with Codex,
the AI coding tool UCCS provides. You are not required to use AI.
Assignment: https://tghastings.github.io/cs4300andcs5300/homework_2.pdf

In spec-driven development (SDD), **you** decide what to build and write it down before any code
exists. Codex then works from your written spec, not from a one-line prompt. You end up with code
you can explain, tests that match your requirements, and the AI citation HW2 requires.

```
 1. SPECIFY   →   2. PLAN   →   3. TASKS   →   4. IMPLEMENT (test first)   →   5. REVIEW
   (you)          (you + AI)    (you + AI)       (AI, one task at a time)       (you)
```

---

## HW2 is split into three features

| Spec folder | Feature (from the HW2 objective) | State in this template |
|---|---|---|
| `specs/001-movie-listings/` | View movie listings (API + UI) | ✅ **Worked example**: spec, plan and tasks filled in. Read it, adjust it, build it. |
| `specs/002-seat-booking/` | Book seats (API + UI) | 🟡 **Started**: user stories and the first criteria are written. You finish the spec. |
| `specs/003-booking-history/` | Check booking history (API + UI) | 🟡 **Started**: user stories and the first criteria are written. You finish the spec. |

Deployment (Render) and documentation aren't features. They're on the checklist at the bottom.

## What's in here

| Path | What it is |
|---|---|
| `AGENTS.md` | Rules and HW2 project context that Codex reads automatically every session. |
| `specs/_template/` | Blank `spec.md`, `plan.md` and `tasks.md`, in case you add a feature of your own. |
| `specs/001–003/` | The three HW2 features above. |
| `prompts/` | Prompts to paste into Codex, one for each step. |
| `AI-USAGE.md` | A log of how you used AI. HW2 requires you to cite AI use in your README. |

📖 Each step links to the course textbook; see [Connecting to the book](#connecting-to-the-book).

---

## Setup

1. Do HW2's **Project Setup** first (section 3.1 of the PDF): create
   `homework2/movie_theater_booking`, the virtual environment, and install `django` and
   `djangorestframework`.
2. Copy everything in this folder into **`homework2/movie_theater_booking/`**, next to
   `manage.py`. Codex reads `AGENTS.md` from the folder you start it in.
3. Install the test tools:
   `pip install coverage behave-django && pip freeze > requirements.txt`
   Plain `behave` doesn't know about Django. **behave-django** (the tool HW2 links to) runs your
   scenarios against a Django test database. Add `behave_django` to `INSTALLED_APPS` and run
   Behave with `python manage.py behave`.
4. Commit before you write any code:
   `git add . && git commit -m "HW2: add SDD template"`
5. Start Codex **from that folder**, then check that it read the rules by asking:
   *"Summarize AGENTS.md in 3 bullets."*

---

## The workflow (repeat for 001, then 002, then 003)

### 1. Specify: what and why (you)
- **001:** read the worked spec. Change anything you'd do differently. It's your app now.
- **002 / 003:** finish `spec.md`. Every `TODO` is a decision **you** make, such as what happens
  when someone books a seat that's already taken. Write acceptance criteria as
  **Given/When/Then**, because they become your Behave scenarios.

> **AC = acceptance criterion:** one specific, testable condition the feature must meet to count as
> done, numbered AC-1, AC-2, and so on. **US** = user story, numbered US-1, US-2, and so on. Every AC traces to a user story, and every
> AC gets at least one test, so "is this feature done?" has a yes/no answer.

Then paste `prompts/01-specify.md`. **Codex reviews your spec; it doesn't write it.**

> A spec is done when a classmate could read it and write the tests without asking you anything.

### 2. Plan: how (you + Codex)
Paste `prompts/02-plan.md`. Codex fills in `plan.md` with the models, serializers, viewsets,
URLs, templates and test strategy. **Read every line.** If you can't explain a decision, ask
Codex why or change it. Then commit.
- 001's plan is already filled in so you can see the level of detail to aim for.

### 3. Tasks: small steps (you + Codex)
Paste `prompts/03-tasks.md`. Each task is one small test-first increment and one commit.

### 4. Implement: one task at a time, test first
Paste `prompts/04-implement.md` **for each task**. Codex writes the failing test (🔴), the least
code that passes (🟢), cleans up (🔵), ticks the box, and **stops**. Then you read `git diff`, run
the tests, `git add` the files you reviewed, and commit with a meaningful message. HW2 asks for frequent pushes with good commit
messages, and one task per commit gives you exactly that.

### 5. Review: your name is on it
Paste `prompts/05-review.md`. Then run the checks yourself:
```bash
python manage.py test
coverage run --source=bookings manage.py test && coverage report   # HW2 needs ≥ 80%
python manage.py behave
python manage.py runserver 0.0.0.0:3000                            # then click "app" in DevEdu
```

---

## Connecting to the book

Every step above is a practice from the course textbook, [SWEBook](https://www.swebook.org).
The whole workflow is §13.5; the rows below point to where each piece is taught.

| In this template | 📖 SWEBook | How it connects |
|---|---|---|
| The workflow, `AGENTS.md` | [§13.5 Spec-Driven Development](https://www.swebook.org/chapters/13-ai-across-the-lifecycle/index.html#135-spec-driven-development), [§13.6 Context as Infrastructure](https://www.swebook.org/chapters/13-ai-across-the-lifecycle/index.html#136-context-as-infrastructure-claudemd-agentsmd-and-skills) | Specify → Plan → Tasks → Implement with a human checkpoint between each; `AGENTS.md` is the instructions file the agent loads every session. |
| User stories (US-#) | [§3.4.1 Guidelines for Effective User Stories](https://www.swebook.org/chapters/03-user-requirements/index.html#341-guidelines-for-effective-user-stories) | INVEST (Independent, Negotiable, Valuable, Estimable, Small, Testable): small, independent, testable stories. |
| Given/When/Then criteria (AC-#) | [§3.4.1 Given / When / Then](https://www.swebook.org/chapters/03-user-requirements/index.html#given--when--then-writing-acceptance-criteria-as-scenarios) | Criteria written as scenarios, which Behave then runs. |
| Open questions, spec review | [§3.1.2 Requirements Challenges](https://www.swebook.org/chapters/03-user-requirements/index.html#312-requirements-challenges) | Ambiguous language is what prompt 1 hunts for. |
| Out of scope | [§4.4.1 MoSCoW Prioritization](https://www.swebook.org/chapters/04-requirements-analysis/index.html#441-must-should-could-wont-moscow-prioritization) | MoSCoW (Must/Should/Could/Won't have): writing down "Won't have (this time)" stops scope creep. |
| AC → test (`Spec ref`, `covers:`) | [§3.4.4 Tracing Requirements to Tests](https://www.swebook.org/chapters/03-user-requirements/index.html#344-tracing-requirements-to-tests-and-backlog-items) | Every requirement traces forward to a test, and every test back to a requirement. |
| Plan: models, views, templates, API | [§7.3 Model-View-Controller](https://www.swebook.org/chapters/07-architectural-patterns/index.html#73-user-interfaces-model-view-controller), [§7.5.4 RESTful APIs](https://www.swebook.org/chapters/07-architectural-patterns/index.html#754-restful-apis) | Django's Model-Template-View (MTV) pattern applies closely related separation-of-concerns ideas, with different names and role boundaries; Django REST Framework (DRF) viewsets are resources + HTTP verbs. |
| Tasks, red → green → refactor | [§2.3.2 Testing: Make It Central to Development](https://www.swebook.org/chapters/02-software-development-processes/index.html#232-testing-make-it-central-to-development) | Test-driven development (TDD): failing test, least code to pass, clean up. A test that passes immediately is a verification test, not a red → green cycle. |
| Unit, API and Behave tests | [§10.2 Levels of Testing](https://www.swebook.org/chapters/10-testing/index.html#102-levels-of-testing) | Unit and integration tests, plus behavior-driven development (BDD) acceptance tests (§10.2.3). |
| Error cases, edge cases | [§10.4 Black-Box Testing](https://www.swebook.org/chapters/10-testing/index.html#104-input-coverage-i-black-box-testing) | Equivalence classes and boundary values (e.g., duration 0). |
| Coverage ≥ 80% | [§10.3 Code Coverage I](https://www.swebook.org/chapters/10-testing/index.html#103-code-coverage-i-white-box-testing), [§10.1.3 Test Adequacy](https://www.swebook.org/chapters/10-testing/index.html#1013-test-adequacy-deciding-when-to-stop) | What statement and branch coverage do (and don't) tell you. 80% is a floor, not the goal. |
| No double booking (002) | [§7.2.1 The Shared-Data Pattern](https://www.swebook.org/chapters/07-architectural-patterns/index.html#721-the-shared-data-pattern) | The data store owns consistency, concurrency control and integrity constraints. |
| Only your own bookings (002/003) | [§11.2.1 A01: Broken Access Control](https://www.swebook.org/chapters/11-software-security/index.html#1121-a01-broken-access-control) | Users can act only within their own permissions. |
| One task = one commit, no secrets | [§8.6 Habits That Make Git Work for a Team](https://www.swebook.org/chapters/08-version-control-git/index.html#86-habits-that-make-git-work-for-a-team) | Small focused commits, messages for the next reader, never commit secrets. |
| Review | [§9.3 Code Reviews](https://www.swebook.org/chapters/09-static-checking/index.html#93-code-reviews-check-intent-and-trust), [§13.7.2 The Generator and the Evaluator](https://www.swebook.org/chapters/13-ai-across-the-lifecycle/index.html#1372-the-generator-and-the-evaluator) | The evaluator isn't the generator: run Prompt 5 in a fresh Codex session, and treat generated code as unverified until a check shows it works. |
| `AI-USAGE.md`, README | [§13.2.10 The Team Project](https://www.swebook.org/chapters/13-ai-across-the-lifecycle/index.html#13210-the-team-project-appendix-a), [§8.7.3 The README](https://www.swebook.org/chapters/08-version-control-git/index.html#873-the-readme-your-projects-front-door) | Record where you used AI and how you verified it. |

---

## How this maps to the HW2 rubric

| Rubric (Table 1) | Pts | Where it comes from |
|---|---|---|
| Functionality | 35 | Features 001–003, each API endpoint **and** its template page |
| User Experience | 15 | The UI criteria in each spec: Bootstrap `base.html`, navigation, empty states |
| Code Quality | 15 | `AGENTS.md` rules: Django conventions, docstrings, small diffs |
| Testing | 20 | Every acceptance criterion → a unit/integration test or Behave scenario; ≥ 80% coverage |
| Deployment | 10 | The Render checklist below |
| Documentation | 5 | README with setup, structure, Render URL **and** your AI citation |

## Before you submit

- [ ] Every acceptance criterion in 001–003 has a passing test
- [ ] `python manage.py test` and `python manage.py behave` both pass
- [ ] Coverage ≥ 80%
- [ ] App runs in DevEdu on port 3000
- [ ] Deployed on Render and the URL works
- [ ] README: setup instructions, project structure, how to run, the Render URL, and the AI
      citation (copy the summary from `AI-USAGE.md`)
- [ ] Pushed to GitHub, and the zip is submitted in Canvas

---

## Rules of thumb

- **The spec is the source of truth.** If the code and the spec disagree, fix one of them on purpose.
- **If the requirements change, update the spec first**, then re-plan.
- **Small diffs.** If Codex wants to change 10 files for one task, the task is too big.
- **You must be able to explain every line.** "Codex wrote it" isn't an answer.
- **Never paste secrets** (such as your Django `SECRET_KEY` or Render environment variables) into Codex.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Codex ignores the rules | Start it in the folder containing `AGENTS.md`. Say "Re-read AGENTS.md." |
| Codex writes code before tests | "Stop. Test first. Revert the code and show me the failing test." |
| Codex invents requirements | "That's not in spec.md. Remove it or add it to Open Questions." |
| Huge diffs | "Undo that. Implement only the next unchecked task." Or run `git restore .` |
| App won't load in DevEdu | Use port 3000: `python manage.py runserver 0.0.0.0:3000` |
| Behave can't find Django | Run `python manage.py behave`, not plain `behave`, and check that `behave_django` is in `INSTALLED_APPS`. behave-django handles the setup, so you don't need a hand-written `features/environment.py`. |
