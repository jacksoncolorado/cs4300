# Spec: Booking history

**Status:** Ready for plan
**Author:** Jackson McGuire  **Date:** 2026-10-08

## 1. Problem
Moviegoers need to see what they've booked. (Homework 2, or HW2, §1 "Check their booking history via the API";
§3.3 `BookingViewSet` "for users to book seats and view their booking history"; §3.5
`/api/bookings/`; template `booking_history.html`.)

## 2. User stories
- **US-1:** As a moviegoer, I want to see a list of my bookings, so that I know what I've reserved.
- **US-2:** As an API client, I want to view booking history and create bookings through `/api/bookings/`.
- **US-3:** As a moviegoer, I want my bookings kept private, so that other users can't see them.
- **US-4:** As a moviegoer, I want my newest bookings first, so that what I just reserved is at the top.

## 3. Acceptance criteria

**AC-1 (US-1): See my bookings**
- Given I am signed in and have booked seat A1 for "Dune"
- When I open My Bookings
- Then I see Dune, seat A1 and the booking date formatted as `F j, Y`, for example `October 8, 2026`

**AC-2 (US-1, US-3): Only my bookings**
- Given users Sam and Alex each have bookings
- When Sam opens My Bookings, or sends `GET /api/bookings/`
- Then only Sam's bookings appear, and none of Alex's

**AC-3 (US-3): Retrieve one booking without leaking another user's data**
- Given Alex has a booking with id 7
- When Sam sends `GET /api/bookings/7/`
- Then the response is 404 and none of Alex's booking data is returned
- Given Sam has one of his own bookings
- When Sam sends `GET /api/bookings/<id>/` for that booking
- Then the response is 200 with `{id, movie, seat, user, booking_date}` for Sam's booking
- 404 rather than 403 for Alex's booking prevents the response from confirming that the row exists.

**AC-4 (UI): Consistent layout and authenticated navigation**
- Given I am signed in and the My Bookings page renders
- Then it extends `base.html`, and the navbar links to both Movies and My Bookings
- Given I am not signed in and a page using `base.html` renders
- Then the navbar shows Movies but does not show the My Bookings link

**AC-5 (US-1): Empty state**
- Given I am signed in and have no bookings
- When I open My Bookings
- Then I see "You have no bookings yet." instead of an empty list

**AC-6 (US-1, US-2): Not signed in**
- Given I am not signed in, when I open My Bookings, then I am redirected to the login page
- Given I am not signed in, when I send `GET /api/bookings/`, then I get 403
- Given I am not signed in, when I send `POST /api/bookings/`, then I get 403 and no booking is created

**AC-7 (US-2): Create a booking through `/api/bookings/`**
- Given I am signed in and seat A1 is available for Dune
- When I send `POST /api/bookings/` with `{movie, seat}`
- Then the response is 201 with `{id, movie, seat, user, booking_date}`, where `movie`, `seat` and `user` are ids
- And its user is me even if the request data names someone else
- When the seat is already booked for that movie through the page or `/api/seats/book/`
- Then the response is 400 with `{"detail": "Seat A1 is already booked for Dune."}`
- When the seat is out of service
- Then the response is 400 with `{"detail": "Seat A3 is out of service."}`
- Unknown or missing movie and seat values return DRF's default field errors, including
  `{"seat": ["Invalid pk \"9999\" - object does not exist."]}` and
  `{"movie": ["This field is required."]}`.

**AC-8 (US-4): Order of the list**
- Given I have bookings made on different dates
- When I open My Bookings or send `GET /api/bookings/`
- Then the most recent booking date is first
- Given I have two bookings made on the same date
- When I open My Bookings or send `GET /api/bookings/`
- Then the booking with the higher id is first

**AC-9 (US-2): Booking history is read-only after creation**
- Given a booking exists
- When I send `PUT`, `PATCH` or `DELETE` to `/api/bookings/<id>/`
- Then each response is 405

## 4. Data
| Thing | Information | Rules |
|---|---|---|
| Booking | movie, seat, user, booking date | Only ever shown to its own user (AC-2, AC-3); returned as `{id, movie, seat, user, booking_date}` with relationship values as ids; newest booking date first and higher id first within the same date (AC-8). |

## 5. API / UI behavior
| Action | Input | Success result | Failure result |
|---|---|---|---|
| My Bookings page | `GET /bookings/` | 200, my bookings newest first with dates formatted as `F j, Y`, or the empty-state message | redirect to `/accounts/login/` if not signed in |
| List bookings (API) | `GET /api/bookings/` | 200, only my bookings, newest first; each item is `{id, movie, seat, user, booking_date}` | 403 if not signed in |
| Get one booking (API) | `GET /api/bookings/<id>/` | 200 with `{id, movie, seat, user, booking_date}` if it is mine | 404 if it is not mine or does not exist; 403 if not signed in |
| Create booking (API) | `POST /api/bookings/` with `{movie, seat}`; any `user` input is ignored | 201 with `{id, movie, seat, user, booking_date}` | exact 002 `detail` error for taken/out-of-service; DRF field errors for missing/unknown ids; 403 if not signed in |
| Change or cancel booking (API) | `PUT`, `PATCH` or `DELETE /api/bookings/<id>/` | — | 405 |

All booking API responses use the same serializer and the same five-field shape established in 002.

## 6. Required design decisions
- `BookingViewSet.get_queryset()` filters by `request.user` so list and retrieve inherit the same privacy boundary (AC-2, AC-3).
- Booking creation calls 002's `book_seat()` service and does not rewrite its rules (AC-7).
- `Booking` model ordering is `("-booking_date", "-id")` so page and API ordering agree, including same-day bookings (AC-8).
- The API exposes only list, retrieve and create; update and delete actions are not registered (AC-9).

## 7. Out of scope
- Cancelling or changing a booking
- Filtering or searching the history
- Staff or admin views of everyone's bookings

## 8. Open questions
- [x] **Why it's a security requirement.** Showing another user's bookings is broken access control (OWASP A01), not a missing feature: the data is already there and only the authenticated-user boundary stops it leaking. Staff views are out of scope; `/admin/` already serves that need for this assignment.
- [x] **404 not 403** for another user's booking, so the response never confirms the row exists.
- [x] **One API representation.** List, retrieve and create reuse 002's `BookingSerializer`; relationships are ids, not nested objects.
- [x] **Read-only after creation.** `PUT`, `PATCH` and `DELETE` return 405 because changing or cancelling a booking is out of scope.
- [x] **Authenticated navigation.** My Bookings appears in the shared navbar only for signed-in users.
