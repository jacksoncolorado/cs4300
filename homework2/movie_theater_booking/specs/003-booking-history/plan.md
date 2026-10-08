# Plan: Booking history

**Spec:** [spec.md](spec.md)   **Status:** Draft

## 1. Approach
Add default ordering to `Booking`, then expose the model through one authenticated DRF viewset limited
to list, retrieve and create. Its queryset always starts at `request.user.bookings`, so both collection
and detail requests share the same privacy boundary. Creation validates only `movie` and `seat`, calls
002's existing `book_seat()` service, and returns the existing read-only `BookingSerializer`, keeping
ownership, availability rules, errors and response shape identical across both booking APIs.

Add a login-required `booking_history` page that uses the same user-filtered, model-ordered bookings.
The shared navbar conditionally shows My Bookings only to authenticated users. This keeps HTML and API
behavior aligned without duplicating booking or privacy rules.

**Rejected:** a full `ModelViewSet`, because it would expose update and delete actions that conflict
with AC-9. Also rejected filtering only inside list/template code, because retrieve could then disclose
another user's booking.

## 2. Data model
| Model | Field / option | Type | Constraints | Spec ref |
|---|---|---|---|---|
| Booking | existing fields | unchanged | `movie`, `seat`, `user`, `booking_date` remain as built in 002 | AC-1–AC-3, AC-7 |
| Booking | `Meta.ordering` | tuple | `("-booking_date", "-id")` | AC-8 |

Create one schema-state migration for the `Booking` ordering option. It does not alter stored rows, but
keeps Django's migration state synchronized with the model.

## 3. Endpoints / views
| Method | URL | View / ViewSet | Returns | Spec ref |
|---|---|---|---|---|
| GET | `/bookings/` (named `booking_history`) | login-required `booking_history` view | 200 with only the signed-in user's ordered bookings, or the exact empty state; anonymous users redirect to login | AC-1, AC-2, AC-4–AC-6, AC-8 |
| GET | `/api/bookings/` | `BookingViewSet.list`; authenticated, user-filtered queryset | 200 list of `{id, movie, seat, user, booking_date}` in model order; 403 anonymous | AC-2, AC-6, AC-8 |
| GET | `/api/bookings/<id>/` | `BookingViewSet.retrieve`; same filtered queryset | 200 for own booking; 404 for another user's or unknown booking; 403 anonymous | AC-3, AC-6 |
| POST | `/api/bookings/` | `BookingViewSet.create`; validate with `SeatBookingInputSerializer`, call `book_seat(request.user, movie, seat)` | 201 with the existing five-field `BookingSerializer`; 400 with matching 002 service/field errors; 403 anonymous | AC-6, AC-7 |
| PUT/PATCH/DELETE | `/api/bookings/<id>/` | no corresponding mixin/action | 405 | AC-9 |

Implement `BookingViewSet` with `CreateModelMixin`, `ListModelMixin`, `RetrieveModelMixin` and
`GenericViewSet`, plus `IsAuthenticated`. `get_queryset()` returns
`Booking.objects.filter(user=request.user)`; model ordering supplies `("-booking_date", "-id")`.

## 4. Files to create / change
| File | Change |
|---|---|
| `bookings/models.py` | Add `Booking.Meta.ordering = ("-booking_date", "-id")` alongside the existing uniqueness constraint |
| `bookings/migrations/0006_alter_booking_options.py` | Record the Booking ordering option |
| `bookings/views.py` | Add the authenticated, restricted `BookingViewSet` and login-required booking-history page |
| `bookings/urls.py` | Register `BookingViewSet` at `/api/bookings/` and add the named `/bookings/` page route |
| `bookings/templates/bookings/base.html` | Show My Bookings in the navbar only when `user.is_authenticated` |
| `bookings/templates/bookings/booking_history.html` | Extend `base.html`; show movie, seat and `F j, Y` booking date, or the exact empty state |
| `bookings/tests.py` | Add model-ordering, API privacy/creation/error/method, and page tests |
| `features/booking_history.feature` | Add user-visible history, privacy, empty-state and sign-in scenarios |
| `features/steps/booking_history_steps.py` | Implement the booking-history scenario setup and assertions |

No new serializer is needed: `SeatBookingInputSerializer` validates create input and
`BookingSerializer` provides the single output representation required by AC-3 and AC-7.

## 5. Test strategy
| Spec ref | Test type | Test name / scenario |
|---|---|---|
| AC-1 | view + Behave | `test_booking_history_shows_movie_seat_and_formatted_date`; scenario “View my booking history” |
| AC-2 | API + view + Behave | `test_list_bookings_only_returns_own`, `test_booking_history_page_only_shows_own`; scenario “Only my bookings are shown” |
| AC-3 | API | `test_cannot_retrieve_another_users_booking`, `test_retrieve_own_booking_returns_five_field_shape` |
| AC-4 | view | `test_booking_history_uses_base_template`, `test_navbar_shows_my_bookings_only_when_authenticated` |
| AC-5 | view + Behave | `test_booking_history_empty_state`; scenario “No booking history yet” |
| AC-6 | view + API + Behave | `test_anonymous_booking_history_redirects_to_login`, `test_anonymous_booking_list_returns_403`, `test_anonymous_booking_create_returns_403`; scenario “Sign in to view booking history” |
| AC-7 | API integration | `test_create_booking_returns_five_field_shape`, `test_create_booking_ignores_user_in_request_data`, `test_taken_seat_returns_matching_detail`, `test_out_of_service_seat_returns_matching_detail`, `test_create_booking_unknown_ids_return_field_errors`, `test_create_booking_missing_fields_return_field_errors`, `test_seat_booked_via_seats_api_refused_via_bookings_api` |
| AC-8 | model + API + view | `test_booking_default_ordering_newest_date_then_highest_id`, `test_booking_api_uses_default_ordering`, `test_booking_history_page_uses_default_ordering` |
| AC-9 | API | `test_booking_update_and_delete_methods_not_allowed` |

Run `python manage.py test`, `python manage.py behave`, and
`coverage run --source=bookings manage.py test && coverage report`; coverage for `bookings` must remain
at least 80%.

## 6. Risks & decisions
- **Privacy must apply to detail routes too.** Filtering in `get_queryset()` makes another user's id
  indistinguishable from a nonexistent id and avoids accidental leakage from retrieve or future actions.
- **Creation has two serializers.** The input serializer accepts only `movie` and `seat`; the existing
  output serializer is read-only and returns all five fields. Client-supplied `user` is ignored and
  `request.user` is passed directly to `book_seat()`.
- **Service errors cross an API boundary.** Catch only `SeatBookingError` and translate it to the same
  400 `detail` response used by `SeatViewSet`; let DRF produce its standard input-field errors.
- **Ordering by date needs an id tie-breaker.** `booking_date` cannot distinguish bookings created on
  the same day, so descending id makes both UI and API deterministic.
- **Query count is secondary to privacy and clarity.** The history view can use `select_related("movie", "seat")`
  to avoid per-row lookups without changing the required user filter or ordering.
