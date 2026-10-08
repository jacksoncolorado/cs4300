# Tasks: Seat booking

**Plan:** [plan.md](plan.md)

> Each task is one small test-first increment and one commit: red → green → refactor when the behavior is missing,
> or a verification test if earlier framework work already provides it. Do them in order.
> Each task names its test and acceptance criterion (AC-#). Codex ticks the box when its tests pass. **You** commit.

- [ ] **T1** — `Seat` model, defaults, `__str__` and schema migration · test: `test_seat_str_and_default_booking_status` · covers: AC-10, AC-12
- [ ] **T2** — Validate unique seat numbers and the uppercase-letter-plus-digits format · test: `test_seat_number_validation` · covers: AC-10
- [ ] **T3** — Idempotent A1–A5 seat data migration · test: `test_seed_seats_is_idempotent` · covers: AC-1, AC-10
- [ ] **T4** — `Booking` model, relationships, date and schema migration · test: `test_booking_records_user_movie_seat_and_date` · covers: AC-2, AC-5
- [ ] **T5** — Database uniqueness for `(movie, seat)` · test: `test_duplicate_booking_rejected_by_database` · covers: AC-4
- [ ] **T6** — Shared `book_seat` service creates a booking for its supplied user · test: `test_book_seat_creates_booking` · covers: AC-2, AC-5, AC-6
- [ ] **T7** — Shared service rejects a taken seat with the exact message · test: `test_book_seat_rejects_taken_seat` · covers: AC-3, AC-4, AC-6
- [ ] **T8** — Shared service rejects an out-of-service seat with the exact message · test: `test_book_seat_rejects_out_of_service_seat` · covers: AC-12
- [ ] **T9** — `SeatSerializer`, `SeatViewSet` and router; public `GET /api/seats/` omits `available` · test: `test_list_seats_without_movie_omits_available` · covers: AC-10
- [ ] **T10** — Movie-filtered seat API computes `available` · test: `test_list_seats_for_movie_shows_availability` · covers: AC-11, AC-12
- [ ] **T11** — Unknown movie filter returns the exact DRF field error · test: `test_filter_unknown_movie_returns_field_error` · covers: AC-9
- [ ] **T12** — Anonymous `POST /api/seats/book/` returns 403 · test: `test_anonymous_api_booking_403` · covers: AC-8
- [ ] **T13** — Authenticated API booking returns 201 with the created booking fields · test: `test_book_available_seat_api_returns_created_booking` · covers: AC-2
- [ ] **T14** — API ignores a client-supplied user and uses `request.user` · test: `test_booking_user_is_request_user_not_request_data` · covers: AC-5
- [ ] **T15** — API booking with an unknown movie returns its DRF field error · test: `test_booking_unknown_movie_returns_field_error` · covers: AC-9
- [ ] **T16** — API booking with an unknown seat returns its DRF field error · test: `test_booking_unknown_seat_returns_field_error` · covers: AC-9
- [ ] **T17** — Taken-seat API booking returns exact 400 instead of an integrity 500 · test: `test_duplicate_booking_returns_error_not_500` · covers: AC-3, AC-4
- [ ] **T18** — Out-of-service API booking returns exact `detail` and saves nothing · test: `test_out_of_service_seat_api_returns_detail_400` · covers: AC-12
- [ ] **T19** — Auth URLs, `LOGIN_REDIRECT_URL`, page route and anonymous login redirect · test: `test_anonymous_seat_page_redirects_to_login` · covers: AC-8
- [ ] **T20** — Login template extends the shared base layout · test: `test_login_uses_base_template` · covers: AC-8
- [ ] **T21** — Movie-list “Book Now” links to the named seat page · test: `test_movie_list_book_now_links_to_seat_page` · covers: AC-1
- [ ] **T22** — Seat page renders per-movie availability and disables unavailable seats · test: `test_seat_page_shows_per_movie_availability` · covers: AC-1, AC-12
- [ ] **T23** — Seat page extends `base.html` with the shared navbar · test: `test_seat_booking_uses_base_template` · covers: AC-7
- [ ] **T24** — Missing movie seat page returns 404 · test: `test_missing_movie_page_404` · covers: AC-9
- [ ] **T25** — Page POST books for the signed-in user, redirects, and shows the exact success message · test: `test_book_available_seat_from_page` · covers: AC-2, AC-5
- [ ] **T26** — Taken-seat page re-renders the exact error with its movie seat-page link · test: `test_taken_seat_page_shows_exact_error_and_back_link` · covers: AC-3
- [ ] **T27** — A page booking is refused through the API afterward · test: `test_seat_booked_via_page_refused_via_seats_api` · covers: AC-6
- [ ] **T28** — An API booking is refused through the page afterward · test: `test_seat_booked_via_seats_api_refused_via_page` · covers: AC-6
- [ ] **T29** — Out-of-service seat appears unavailable for every movie page · test: `test_out_of_service_seat_unavailable_for_every_movie` · covers: AC-12
- [ ] **T30** — `seed_demo_user` fails clearly without `DEMO_PASSWORD` · test: `test_seed_demo_user_requires_password` · covers: AC-13
- [ ] **T31** — `seed_demo_user` creates once, updates the password, and is included in Render's build command · test: `test_seed_demo_user_is_idempotent_and_updates_password` · covers: AC-13
- [ ] **T32** — Behave scenario “View available seats” · covers: AC-1
- [ ] **T33** — Behave scenario “Book an available seat” · covers: AC-2, AC-5
- [ ] **T34** — Behave scenario “Seat already taken” · covers: AC-3
- [ ] **T35** — Behave scenario “Sign in to book a seat” · covers: AC-8
- [ ] **T36** — Behave scenario “Out-of-service seat is unavailable” · covers: AC-12

## Done when
- [ ] Every acceptance criterion in `spec.md` has a passing test
- [ ] Full suite green: `python manage.py test`
- [ ] `python manage.py behave` passes
- [ ] Coverage ≥ 80% for `bookings`
- [ ] `AI-USAGE.md` updated
