# Plan: Booking history

**Spec:** [spec.md](spec.md)   **Status:** Draft | Approved

> This says **how** the spec will be built. Codex drafts it (prompts/02-plan.md) and you approve it. Don't approve
> anything you can't explain. The rows already filled in come from acceptance criteria (AC) numbered AC-2 to AC-4 and AC-7, which every
> Homework 2 (HW2) solution needs. Keep them, and replace each `TODO` with your decision.

## 1. Approach
<!-- A short paragraph: the overall design and why it was chosen over the alternatives. -->

## 2. Data model
| Model | Field | Type | Constraints | Spec ref |
|---|---|---|---|---|
|  |  |  |  | AC-? |

## 3. Endpoints / views
| Method | URL | View / ViewSet | Returns | Spec ref |
|---|---|---|---|---|
| GET | `/api/bookings/` | BookingViewSet.list: `get_queryset()` returns only `request.user`'s bookings | 200 list | AC-2 |
| GET | `/api/bookings/<id>/` | BookingViewSet.retrieve: same filtered queryset | 200 / TODO (404 or 403) | AC-3 |
| POST | `/api/bookings/` | BookingViewSet.create: calls 002's booking operation, with `user=request.user` | TODO | AC-7 |
|  |  |  |  | AC-? |

## 4. Files to create / change
| File | Change |
|---|---|
| `bookings/templates/bookings/base.html` | Add the My Bookings link to the navbar, now that its route exists |
|  |  |

## 5. Test strategy
| Spec ref | Test type (unit / integration / Behave) | Test name / scenario |
|---|---|---|
| AC-1 |  |  |
| AC-2 | API + view test | `test_list_bookings_only_returns_own`, `test_booking_history_page_only_shows_own` |
| AC-3 | API | `test_cannot_retrieve_another_users_booking` |
| AC-4 | view test | `test_booking_history_uses_base_template` (`assertTemplateUsed`) |
| AC-7 | API | TODO, plus `test_create_booking_ignores_user_in_request_data`, `test_seat_booked_via_seats_api_refused_via_bookings_api` |

## 6. Risks & decisions
<!-- Tradeoffs made, anything that could go wrong, anything you chose not to do. -->
- Filter in `get_queryset()`, not only in the template or the list view. Otherwise
  `/api/bookings/<id>/` (and update/delete, if you allow them) would still expose other users' bookings.
-
