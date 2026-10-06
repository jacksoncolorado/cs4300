# Tasks: Movie listings

**Plan:** [plan.md](plan.md)

> Each task (T#) is one small test-first increment and one commit: red → green → refactor when the behavior is missing.
> Each task names its test and the acceptance criterion (AC-#) it covers. Codex ticks the box. **You** commit.
> Some tests pass as soon as they're written, because `ModelViewSet` already does the work (T7–T10).
> Those are verification tests, not red → green cycles. That's fine: Codex should say so, and not invent code just to see red.
>
> 📖 **Book:** test-driven development (TDD), [§2.3.2](https://www.swebook.org/chapters/02-software-development-processes/index.html#232-testing-make-it-central-to-development). T14–T15 are behavior-driven development (BDD) acceptance tests, [§10.2.3](https://www.swebook.org/chapters/10-testing/index.html#1023-functional-system-and-acceptance-testing).

- [ ] **T1** — `Movie` model + migration + `__str__` + ordering · test: `test_movie_str_and_ordering` · covers: Data
- [ ] **T2** — `MovieSerializer` + `MovieViewSet` + router; `GET /api/movies/` · test: `test_list_movies` · covers: AC-4
- [ ] **T3** — `POST /api/movies/` · test: `test_create_movie` · covers: AC-5
- [ ] **T4** — Validation: missing title → 400 · test: `test_create_movie_missing_title_400` · covers: AC-6
- [ ] **T5** — Validation: missing release date → 400 · test: `test_create_movie_missing_release_date_400` · covers: AC-6
- [ ] **T6** — Validation: duration ≤ 0 → 400 · test: `test_create_movie_zero_duration_400` · covers: AC-6
- [ ] **T7** — `GET /api/movies/<id>/` · test: `test_retrieve_movie` · covers: AC-8
- [ ] **T8** — Missing movie → 404 · test: `test_get_missing_movie_404` · covers: AC-8
- [ ] **T9** — `PUT`/`PATCH /api/movies/<id>/` · test: `test_update_movie` · covers: AC-7
- [ ] **T10** — `DELETE /api/movies/<id>/` · test: `test_delete_movie` · covers: AC-7
- [ ] **T11** — `base.html` (Bootstrap + navbar) + `movie_list` view/template (disabled "Book Now") · test: `test_movie_list_uses_base_template` · covers: AC-9
- [ ] **T12** — Show release date and duration · test: `test_movie_list_shows_release_date_and_duration` · covers: AC-3
- [ ] **T13** — Empty state · test: `test_movie_list_empty_state` · covers: AC-2
- [ ] **T14** — behave-django setup (`behave_django` in `INSTALLED_APPS`) + scenario "Browse the movie list" · covers: AC-1
- [ ] **T15** — Scenario "No movies showing" · covers: AC-2

## Done when
- [ ] Every acceptance criterion in `spec.md` has a passing test
- [ ] `python manage.py test` and `python manage.py behave` pass
- [ ] Coverage ≥ 80% for `bookings`
- [ ] `AI-USAGE.md` updated
