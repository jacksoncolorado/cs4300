# Plan: Seat booking

**Spec:** [spec.md](spec.md)   **Status:** Complete

## 1. Approach
Add `Seat` and `Booking` models, then put every booking rule in one `book_seat(user, movie, seat)`
function in `bookings/services.py`. The HTML view and the custom `SeatViewSet` booking action call
that function, and feature 003 can reuse it from `BookingViewSet`. The service rejects out-of-service
or already-booked seats, creates the booking inside `transaction.atomic()`, and converts a database
uniqueness race into the same friendly error used by the pre-check (AC-2–AC-6, AC-12).

Use a read-only `SeatViewSet` for public seat listing plus a custom `POST book` action for authenticated
booking. A `SeatSerializer` conditionally adds computed per-movie availability when the view supplies a
movie; a separate booking-input serializer resolves `movie` and `seat` IDs but never accepts ownership
from the client (AC-5, AC-9–AC-11). The page view uses `login_required`, handles GET and POST at the
same URL, and renders the same model data and service results as the API (AC-1–AC-3, AC-6–AC-8, AC-12).

**Rejected:** putting booking checks in each view or serializer. That would duplicate the rules across
the page, `/api/seats/book/`, and feature 003, making inconsistent behavior likely and leaving race
conditions unless every path remembered the database constraint (AC-4, AC-6).

## 2. Data model
| Model | Field | Type | Constraints | Spec ref |
|---|---|---|---|---|
| Seat | `seat_number` | `CharField` | required; unique; regex `^[A-Z][0-9]+$` | AC-1, AC-9–AC-12 |
| Seat | `booking_status` | `BooleanField` | `default=False`; `True` means out of service | AC-10, AC-12 |
| Booking | `movie` | `ForeignKey(Movie)` | required; cascade with the movie | AC-2–AC-6 |
| Booking | `seat` | `ForeignKey(Seat)` | required; cascade with the seat | AC-2–AC-6 |
| Booking | `user` | `ForeignKey(settings.AUTH_USER_MODEL)` | required; always supplied from `request.user`; read-only in output serialization | AC-2, AC-5 |
| Booking | `booking_date` | `DateField` | `auto_now_add=True` | AC-2 |
| Booking | database constraint | `UniqueConstraint` | unique fields `("movie", "seat")` | AC-4 |
| Seat API only | `available` | computed boolean | absent without `?movie=`; otherwise false when out of service or already booked for that movie | AC-10–AC-12 |

Create the Seat schema first, then a separate idempotent data migration that seeds A1–A5 with
`get_or_create`, followed by the Booking schema and its uniqueness constraint. Availability is never
stored: it is derived from `booking_status` and the existence of a `Booking` for the requested
`(movie, seat)` pair (AC-1, AC-4, AC-10–AC-12).

## 3. Endpoints / views
| Method | URL | View / ViewSet | Returns | Spec ref |
|---|---|---|---|---|
| GET | `/movies/<int:movie_id>/seats/` (named `book_seat`) | login-required `book_seat_view` → `seat_booking.html` | 200 with per-movie availability; 302 to login; 404 for missing movie | AC-1, AC-7–AC-9, AC-12 |
| POST | `/movies/<int:movie_id>/seats/` (named `book_seat`) | same `book_seat_view`, calling the shared service | 302 back with `Seat <seat> booked for <movie>.`; re-render errors with a link to this GET URL | AC-2, AC-3, AC-5, AC-6, AC-8, AC-12 |
| GET | `/api/seats/` | public `SeatViewSet.list` | 200 with `id`, `seat_number`, `booking_status`; add `available` only for valid `?movie=<id>`; unknown movie returns 400 field error | AC-9–AC-12 |
| POST | `/api/seats/book/` | authenticated `SeatViewSet.book`, calling the shared service | 201 with `{id, movie, seat, user, booking_date}`; 400 with `detail` or DRF field errors; 403 when anonymous | AC-2–AC-6, AC-8, AC-9, AC-12 |
| GET | `/api/movies/` | existing public `MovieViewSet.list` | unchanged public 200 | 001 AC-4; 002 permissions decision |
| GET/POST | `/accounts/login/` | Django `auth_views.LoginView` via `django.contrib.auth.urls` | built-in login flow using `registration/login.html` | AC-8 |

`SeatViewSet.get_permissions()` allows public list requests and requires `IsAuthenticated` for the
custom booking action. The booking-input serializer exposes only `movie` and `seat`; an extra `user`
key is ignored and `request.user` is passed directly to the service (AC-5, AC-8).

## 4. Files to create / change
| File | Change |
|---|---|
| `bookings/models.py` | Add `Seat`, `Booking`, seat-number validation, relationships, booking date, and `(movie, seat)` uniqueness constraint |
| `bookings/migrations/0003_seat.py` | Create the Seat table |
| `bookings/migrations/0004_seed_seats.py` | Idempotently seed A1–A5 |
| `bookings/migrations/0005_booking.py` | Create the Booking table and `(movie, seat)` constraint |
| `bookings/services.py` | Add the shared atomic `book_seat` operation and booking-domain exception(s) with the exact AC-3/AC-12 messages |
| `bookings/serializers.py` | Add seat listing, conditional availability, booking-input, and read-only booking-output serialization |
| `bookings/views.py` | Add the login-required GET/POST seat page and `SeatViewSet` list/book actions |
| `bookings/urls.py` | Add the named page route and register `SeatViewSet` at `/api/seats/` |
| `movie_theater_booking/urls.py` | Include Django authentication URLs under `/accounts/` |
| `movie_theater_booking/settings.py` | Set `LOGIN_REDIRECT_URL = "/"` |
| `bookings/templates/bookings/movie_list.html` | Replace the disabled button with `{% url 'book_seat' movie.id %}` |
| `bookings/templates/bookings/seat_booking.html` | Show the movie, every seat's computed availability, the POST form, success/error messages, and error link |
| `bookings/templates/registration/login.html` | Extend `base.html` and render Django's login form |
| `bookings/management/commands/seed_demo_user.py` | Idempotently create or update the demo user from `DEMO_PASSWORD` without committing a password |
| Render build-command configuration/documentation | Run migrations, then `python manage.py seed_demo_user` with `DEMO_PASSWORD` configured in Render |
| `bookings/tests.py` | Add model, service, page, authentication, API, cross-path, seed-command, and error-path tests |
| `features/seat_booking.feature` | Add user-visible seat availability, booking, taken-seat, authentication, and out-of-service scenarios |
| `features/steps/seat_booking_steps.py` | Implement the feature steps with explicit scenario setup |

## 5. Test strategy
| Spec ref | Test type | Test name / scenario |
|---|---|---|
| AC-1 | view + Behave | `test_movie_list_book_now_links_to_seat_page`, `test_seat_page_shows_per_movie_availability`; scenario “View available seats” |
| AC-2 | view + API + service + Behave | `test_book_available_seat_from_page`, `test_book_available_seat_api_returns_created_booking`; scenario “Book an available seat” verifies owner, movie, seat, date, exact success message, and updated availability |
| AC-3 | view + API + Behave | `test_taken_seat_page_shows_exact_error_and_back_link`, `test_taken_seat_api_returns_detail_400`; scenario “Seat already taken” |
| AC-4 | model + service + API | `test_duplicate_booking_rejected_by_database`, `test_book_seat_translates_database_duplicate_to_booking_error`, `test_duplicate_booking_returns_error_not_500` |
| AC-5 | view + API | `test_book_available_seat_from_page`, `test_booking_user_is_request_user_not_request_data` |
| AC-6 | integration | `test_seat_booked_via_page_refused_via_seats_api`, `test_seat_booked_via_seats_api_refused_via_page` |
| AC-7 | view | `test_seat_booking_uses_base_template` with `assertTemplateUsed` |
| AC-8 | view + API + Behave | `test_anonymous_seat_page_redirects_to_login`, `test_anonymous_api_booking_403`, `test_successful_login_redirects_to_movie_list`; scenario “Sign in to book a seat” |
| AC-9 | view + API | `test_missing_movie_page_404`, `test_booking_unknown_movie_returns_field_error`, `test_booking_unknown_seat_returns_field_error`, `test_filter_unknown_movie_returns_field_error` |
| AC-10 | API | `test_list_seats_without_movie_omits_available` |
| AC-11 | API | `test_list_seats_for_movie_shows_availability` |
| AC-12 | service + API + view + Behave | `test_out_of_service_seat_api_returns_detail_400`, `test_out_of_service_seat_unavailable_for_every_movie`; scenario “Out-of-service seat is unavailable” |
| AC-13 | command | `test_seed_demo_user_requires_password`, `test_seed_demo_user_is_idempotent_and_updates_password` |

Run `python manage.py test`, `python manage.py behave`, and
`coverage run --source=bookings manage.py test && coverage report`; coverage for `bookings` must remain
at least 80%.

## 6. Risks & decisions
- **Double booking is a race.** The service performs a friendly availability pre-check, then saves in
  `transaction.atomic()`. The `(movie, seat)` database constraint is authoritative; an
  `IntegrityError` is converted to `Seat <number> is already booked for <movie>.`, never a 500
  (AC-3, AC-4).
- **Never trust the client for `user`.** Booking input contains only `movie` and `seat`. Unknown keys,
  including `user`, are ignored by DRF; ownership always comes from `request.user` (AC-5).
- **One availability source.** `booking_status=True` means globally out of service. Otherwise,
  availability is computed from Booking for the requested movie, so no stored availability flag can
  drift out of sync (AC-6, AC-10–AC-12).
- **Conditional response shape.** `SeatSerializer` receives the selected movie in its context and
  removes `available` when there is no movie query parameter, preserving AC-10's exact distinction
  from AC-11.
- **Demo credentials stay outside Git.** `seed_demo_user` fails clearly when `DEMO_PASSWORD` is absent,
  uses the fixed non-secret username `demo`, and calls `set_password()` on both create and update before
  saving. Render supplies the password to its build command.
