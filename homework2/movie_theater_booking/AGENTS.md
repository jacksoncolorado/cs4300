# AGENTS.md — Rules for Codex (CS 4300/5300 Homework 2)

This project uses **spec-driven development**. A student in CS 4300/5300 at UCCS owns this code
and must be able to explain every line of it. You are a pair programmer, not the author.

## Project context: Homework 2 (HW2), Movie Theater Booking
- Assignment: https://tghastings.github.io/cs4300andcs5300/homework_2.pdf
- The Django project is `movie_theater_booking` and lives in the student's `homework2/` folder.
  The app is `bookings`.
- Models required by the assignment:
  - **Movie:** title, description, release date, duration
  - **Seat:** seat number, booking status
  - **Booking:** movie, seat, user, booking date
- API: Django REST Framework (DRF) serializers plus `MovieViewSet`, `SeatViewSet` and `BookingViewSet`,
  routed to `/api/movies/`, `/api/seats/` and `/api/bookings/`.
- UI: Django templates in `bookings/templates/bookings/`: `base.html` (Bootstrap CSS link),
  `movie_list.html`, `seat_booking.html` and `booking_history.html`. The UI shows and changes the
  same data as the API.
- Tests: unit and integration tests (`python manage.py test`) plus behavior-driven development (BDD) tests with **Behave** through
  **behave-django** (`features/`, run with `python manage.py behave`; `behave_django` is in
  `INSTALLED_APPS`). The course requires **≥ 80% coverage**.
- In DevEdu, run with `python manage.py runserver 0.0.0.0:3000`. The app is deployed on **Render**.

## Source of truth
- Features are defined in `specs/<NNN-feature>/spec.md`. Build **only** what the spec says.
- If something is ambiguous or missing, **ask** or add it under "Open Questions." Never invent
  requirements, fields, endpoints or UI. Where the assignment and the spec disagree, point it out.
- `plan.md` says *how* and `tasks.md` says *in what order*. Keep them in sync with the code.

## How to work
1. **One task at a time.** Implement only the next unchecked task in `tasks.md`, then stop and
   report back. Don't start the next task until the student says so.
2. **Test first (red → green → refactor).**
   - Write the test first and run it to show that it fails, and why. If it already passes,
     say so and why (it's a verification test); don't invent code just to see red.
   - Write the least code that makes it pass, then run the full suite.
   - Refactor only while the tests stay green.
3. **Small diffs.** Touch only the files the task needs. No drive-by reformatting or renaming.
4. **Explain.** After each task, summarize in plain language what changed and why, and name the
   one Django/DRF concept the student should understand from this step.
5. Tick the task's box in `tasks.md` when its tests pass.

## Acceptance criteria → tests
- Each Given/When/Then criterion must map to at least one test: a Behave scenario for behavior
  users see in the UI, and a Django `TestCase` / DRF `APITestCase` for models, serializers and endpoints.
- Test error paths (400/401/403/404, invalid data, double-booking) and not just the happy path.
- Check coverage with `coverage run --source=bookings manage.py test && coverage report`.

## Conventions
- Follow Django conventions: app layout, `urls.py` (project routes include the app routes),
  templates namespaced under `bookings/`, and migrations committed with model changes.
- Return correct HTTP status codes from the API.
- Booking a seat happens through **one** shared booking operation. The seat booking page,
  `/api/seats/` and `/api/bookings/` all call it. Never copy the booking rules into a second place.
- Add new dependencies to `requirements.txt` in the same change.
- Write docstrings, and comments that explain *why*, not *what*.

## Never
- Never put secrets (the Django `SECRET_KEY`, passwords, Render environment values) in code, tests or commits.
- Never take a booking's user from request data. It is always the signed-in user (`request.user`),
  and booking lists only ever show that user's bookings.
- Never delete or weaken a test just to make it pass. If you think a test is wrong, say so and ask.
- Never run `git push`, `git reset --hard` or force-push, or rewrite history. The student commits and pushes.
- Never change files outside `homework2/`.

## When you finish a feature
List each acceptance criterion from `spec.md` and mark it ✅ met (naming the test that proves
it), ⚠️ partial, or ❌ missing. Remind the student to update `AI-USAGE.md`.
