# Plan: Seat booking

**Spec:** [spec.md](spec.md)   **Status:** Draft | Approved

> This says **how** the spec will be built. Codex drafts it (prompts/02-plan.md) and you approve it. Don't approve
> anything you can't explain. The rows already filled in come from acceptance criteria (AC) numbered AC-4 to AC-7, which every
> Homework 2 (HW2) solution needs. Keep them, and replace each `TODO` with your decision.

## 1. Approach
<!-- A short paragraph: the overall design and why it was chosen over the alternatives. -->
- **One booking operation.** The seat booking page and `SeatViewSet` (and `BookingViewSet` in 003)
  all call one shared operation that holds the booking rules (AC-6). TODO: where does it live (a model
  method, a function in its own module, the serializer?), and why there?

## 2. Data model
| Model | Field | Type | Constraints | Spec ref |
|---|---|---|---|---|
| Booking | user | ForeignKey to the user model | set from `request.user` on the server; read-only in the serializer | AC-5 |
| Booking | — | a database unique constraint on TODO: `(seat)` or `(movie, seat)`? (must match your availability decision) | — | AC-4 |
| Seat | booking_status | TODO: stored field, or worked out from bookings? | TODO | Open Q |
|  |  |  |  | AC-? |

## 3. Endpoints / views
| Method | URL | View / ViewSet | Returns | Spec ref |
|---|---|---|---|---|
| GET | TODO (named `book_seat`, takes the movie id) | seat booking page → `seat_booking.html` | HTML | AC-1, AC-7 |
|  |  |  |  | AC-? |

## 4. Files to create / change
| File | Change |
|---|---|
| `bookings/templates/bookings/movie_list.html` | Turn 001's disabled "Book Now" into `{% url 'book_seat' movie.id %}` |
|  |  |

## 5. Test strategy
| Spec ref | Test type (unit / integration / Behave) | Test name / scenario |
|---|---|---|
| AC-1 | view test + Behave | TODO, plus `test_movie_list_book_now_links_to_seat_page` |
| AC-4 | unit | `test_duplicate_booking_rejected_by_database` (saving a second booking directly raises `IntegrityError`) |
| AC-4 | API | `test_duplicate_booking_returns_error_not_500` |
| AC-5 | API | `test_booking_user_is_request_user_not_request_data` |
| AC-6 | view + API | `test_seat_booked_via_page_refused_via_seats_api`, and the reverse |
| AC-7 | view test | `test_seat_booking_uses_base_template` (`assertTemplateUsed`) |

## 6. Risks & decisions
<!-- Tradeoffs made, anything that could go wrong, anything you chose not to do. -->
- **Double booking is a race.** A "seat already taken?" check in the serializer or view is still
  needed for a friendly error, but on its own it's race-prone: two requests can both pass it before
  either one saves. The database unique constraint is what actually guarantees AC-4. Save inside
  `transaction.atomic()` and turn the `IntegrityError` into the same response as AC-3, not a 500.
  📖 **Book:** [§7.2.1 The Shared-Data Pattern](https://www.swebook.org/chapters/07-architectural-patterns/index.html#721-the-shared-data-pattern)
- **Never trust the client for `user`.** It is set from `request.user` (AC-5). A `user` value in
  the request data is ignored or rejected. TODO: which, and what does the client see?
- TODO: how do you keep Seat's booking status and Booking consistent? (See spec, Open questions.)
