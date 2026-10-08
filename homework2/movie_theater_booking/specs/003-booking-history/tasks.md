# Tasks: Booking history

**Plan:** [plan.md](plan.md)

> Each task is one small test-first increment and one commit: red → green → refactor when the behavior is missing,
> or a verification test if it already passes. Do them in order.
> Each task names its test and the acceptance criterion (AC-#) it covers.
> Codex ticks the box when the task's tests pass. **You** commit.

- [x] **T1** — Add deterministic `Booking` model ordering and its migration · test: `test_booking_default_ordering_newest_date_then_highest_id` · covers: AC-8
- [x] **T2** — Add the authenticated booking-list API with user isolation and model ordering · tests: `test_list_bookings_only_returns_own`, `test_booking_api_uses_default_ordering`, `test_anonymous_booking_list_returns_403` · covers: AC-2, AC-6, AC-8
- [x] **T3** — Add private booking retrieval and keep update/delete methods unavailable · tests: `test_cannot_retrieve_another_users_booking`, `test_retrieve_own_booking_returns_five_field_shape`, `test_booking_update_and_delete_methods_not_allowed` · covers: AC-3, AC-9
- [x] **T4** — Add authenticated booking creation with the shared five-field response and server-owned user · tests: `test_create_booking_returns_five_field_shape`, `test_create_booking_ignores_user_in_request_data`, `test_anonymous_booking_create_returns_403` · covers: AC-6, AC-7
- [x] **T5** — Reuse 002 booking failures and validation across the bookings API · tests: `test_taken_seat_returns_matching_detail`, `test_out_of_service_seat_returns_matching_detail`, `test_create_booking_unknown_ids_return_field_errors`, `test_create_booking_missing_fields_return_field_errors`, `test_seat_booked_via_seats_api_refused_via_bookings_api`, `test_seat_booked_via_page_refused_via_bookings_api` · covers: AC-7
- [x] **T6** — Add the login-required history page, formatted booking details, shared layout and authenticated-only navbar link · tests: `test_booking_history_shows_movie_seat_and_formatted_date`, `test_booking_history_uses_base_template`, `test_navbar_shows_my_bookings_only_when_authenticated`, `test_anonymous_booking_history_redirects_to_login` · covers: AC-1, AC-4, AC-6
- [x] **T7** — Keep the history page private, ordered and explicit when empty · tests: `test_booking_history_page_only_shows_own`, `test_booking_history_empty_state`, `test_booking_history_page_uses_default_ordering` · covers: AC-2, AC-5, AC-8
- [x] **T8** — Add Behave scenarios “View my booking history,” “Only my bookings are shown,” and “Newest bookings appear first” · covers: AC-1, AC-2, AC-8
- [x] **T9** — Add Behave scenarios “Authenticated booking navigation,” “No booking history yet,” and “Sign in to view booking history” · covers: AC-4, AC-5, AC-6
- [x] **T10** — Add authenticated Sign out form, movie-list redirect, and anonymous Sign in link · tests: `test_navbar_shows_sign_out_when_authenticated`, `test_sign_out_returns_to_movie_list` · covers: AC-10

## Done when
- [x] Every acceptance criterion in `spec.md` has a passing test
- [x] Full suite green: `python manage.py test`
- [x] `python manage.py behave` passes
- [x] Coverage ≥ 80%
- [x] `AI-USAGE.md` updated
