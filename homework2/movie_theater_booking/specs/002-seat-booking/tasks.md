# Tasks: Seat booking

**Plan:** [plan.md](plan.md)

> Each task is one test-first increment and one commit: write all named tests first, run them red (or
> identify verification tests that already pass), implement the grouped behavior, then refactor green.
> Tasks are ordered model → service → API → UI → BDD. Codex ticks the box when its tests pass. **You** commit.

- [x] **T1** — `Seat` model, validation, schema migration and idempotent A1–A5 seed migration · tests: `test_seat_str_and_default_booking_status`, `test_seat_number_validation`, `test_seed_seats_is_idempotent` · covers: AC-1, AC-10, AC-12
- [x] **T2** — `Booking` model, relationships, automatic date and `(movie, seat)` constraint · tests: `test_booking_records_user_movie_seat_and_date`, `test_duplicate_booking_rejected_by_database` · covers: AC-2, AC-4, AC-5
- [x] **T3** — Shared atomic `book_seat` service for success, taken seats and out-of-service seats · tests: `test_book_seat_creates_booking`, `test_book_seat_rejects_taken_seat`, `test_book_seat_rejects_out_of_service_seat` · covers: AC-2, AC-3, AC-4, AC-5, AC-6, AC-12
- [x] **T4** — Public seat-list API, conditional movie availability and invalid movie-filter error · tests: `test_list_seats_without_movie_omits_available`, `test_list_seats_for_movie_shows_availability`, `test_filter_unknown_movie_returns_field_error` · covers: AC-9, AC-10, AC-11, AC-12
- [x] **T5** — Booking API authentication and successful 201 representation · tests: `test_anonymous_api_booking_403`, `test_book_available_seat_api_returns_created_booking` · covers: AC-2, AC-8
- [x] **T6** — Booking API ownership and unknown-ID field errors · tests: `test_booking_user_is_request_user_not_request_data`, `test_booking_unknown_movie_returns_field_error`, `test_booking_unknown_seat_returns_field_error` · covers: AC-5, AC-9
- [x] **T7** — Booking service/API translate database duplicates and taken/out-of-service failures into exact errors · tests: `test_book_seat_translates_database_duplicate_to_booking_error`, `test_duplicate_booking_returns_error_not_500`, `test_out_of_service_seat_api_returns_detail_400` · covers: AC-3, AC-4, AC-12
- [x] **T8** — Django auth URLs, login redirect, `LOGIN_REDIRECT_URL` and shared login template · tests: `test_anonymous_seat_page_redirects_to_login`, `test_login_uses_base_template`, `test_successful_login_redirects_to_movie_list` · covers: AC-8
- [x] **T9** — Movie link and seat page show per-movie availability using the shared layout · tests: `test_movie_list_book_now_links_to_seat_page`, `test_seat_page_shows_per_movie_availability`, `test_seat_booking_uses_base_template` · covers: AC-1, AC-7, AC-12
- [x] **T10** — Seat page 404 plus successful signed-in page booking and exact success message · tests: `test_missing_movie_page_404`, `test_book_available_seat_from_page` · covers: AC-2, AC-5, AC-9
- [x] **T11** — Seat page shows exact taken/out-of-service states and the movie-specific back link · tests: `test_taken_seat_page_shows_exact_error_and_back_link`, `test_out_of_service_seat_unavailable_for_every_movie` · covers: AC-3, AC-12
- [x] **T12** — Page and API enforce the same booking rules in both directions · tests: `test_seat_booked_via_page_refused_via_seats_api`, `test_seat_booked_via_seats_api_refused_via_page` · covers: AC-6
- [x] **T13** — Idempotent `seed_demo_user` command and Render build invocation · tests: `test_seed_demo_user_requires_password`, `test_seed_demo_user_is_idempotent_and_updates_password` · covers: AC-13
- [x] **T14** — Behave scenarios “View available seats” and “Book an available seat” · covers: AC-1, AC-2, AC-5
- [x] **T15** — Behave scenarios “Seat already taken,” “Sign in to book a seat,” and “Out-of-service seat is unavailable” · covers: AC-3, AC-8, AC-12

## Done when
- [x] Every acceptance criterion in `spec.md` has a passing test
- [x] Full suite green: `python manage.py test`
- [x] `python manage.py behave` passes
- [x] Coverage ≥ 80% for `bookings`
- [x] `AI-USAGE.md` updated
