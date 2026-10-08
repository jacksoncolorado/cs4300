# Spec: Seat booking

**Status:** Complete
**Author:** Jackson McGuire  **Date:** 2026-10-07

## 1. Problem
A moviegoer who has picked a movie needs to see which seats are free and reserve one.
(Homework 2, or HW2, §1 "Book seats via the API"; §3.3 `SeatViewSet` "for seat availability and booking";
§3.5 `/api/seats/`; template `seat_booking.html`.)

## 2. User stories
- **US-1:** As a moviegoer, I want to see which seats are available for a movie, so that I can choose one.
- **US-2:** As a moviegoer, I want to book an available seat, so that it's reserved for me.
- **US-3:** As an API client, I want to check seat availability and book seats through `/api/seats/`.
  (HW2 also has `/api/bookings/` create bookings; see AC-6 and feature 003.)

## 3. Acceptance criteria

**AC-1 (US-1): Seat availability page**
- Given the movie "Dune" and seats A1–A5, where A2 is already booked
- When I click "Book Now" for Dune
- Then I see the seat booking page for Dune, with A2 shown as unavailable and the others as available
- The page uses `GET /movies/<movie_id>/seats/`, named `book_seat`.
- (This is where "Book Now" on the movie list, disabled in 001, becomes a real link.)

**AC-2 (US-2): Book an available seat**
- Given I am signed in and seat A1 is available for Dune
- When I book A1
- Then a Booking is created for me, that movie and that seat, with today's date
- And I am returned to the seat page for Dune with a success message
- And A1 now shows as unavailable
- The form posts to the page's own URL: `POST /movies/<movie_id>/seats/`.
- The page success message is `Seat A1 booked for Dune.`, using the selected seat number and movie title.
- A successful `POST /api/seats/book/` returns 201 with the created booking's `id`, `movie`, `seat`,
  `user` and `booking_date`; `user` is the signed-in user's id.

**AC-3 (US-2): Seat already taken**
- Given seat A2 is already booked for Dune
- When I try to book A2
- Then the API returns 400 with `{"detail": "Seat A2 is already booked for Dune."}`, the page
  re-renders with the same message and a link back, and no second booking is created
- The link back points to `GET /movies/<movie_id>/seats/` for that movie.

**AC-4 (US-2): No double booking, even at the same moment**
- Given seat A1 is available for Dune
- When two requests to book A1 for Dune arrive at the same moment, or code saves a second booking
  of A1 for Dune without going through the page or API checks
- Then only one booking of A1 for Dune exists. The second save is refused, and a user or client
  making the second request gets the same answer as AC-3 (never a 500 error)
- (Checking "is it taken?" before saving isn't enough: two requests can both pass the check before
  either one saves. The database itself has to refuse the duplicate.)
- 📖 **Book:** the data store owns integrity constraints and concurrency control, [§7.2.1 The Shared-Data Pattern](https://www.swebook.org/chapters/07-architectural-patterns/index.html#721-the-shared-data-pattern).

**AC-5 (US-2, US-3): The booking belongs to whoever is signed in**
- Given I am signed in as Sam
- When I book a seat through the page or the API, even if the request data names another user
- Then the booking's user is Sam
- A client-supplied `user` value is ignored; it never changes the booking owner.
- 📖 **Book:** [§11.2.1 A01: Broken Access Control](https://www.swebook.org/chapters/11-software-security/index.html#1121-a01-broken-access-control)

**AC-6 (US-2, US-3): Same rules everywhere**
- Given seat A1 has been booked for Dune through the seat booking page
- When anyone tries to book A1 for Dune through `/api/seats/` (or the other way round)
- Then it is refused exactly as in AC-3, because both follow one set of booking rules
- (003 adds `/api/bookings/` as a third way to book. It must follow the same rules: 003's AC-7.)

**AC-7 (UI): Consistent layout**
- Given the seat booking page for a movie
- When it renders
- Then it extends `base.html`, with the same navbar as the movie list

**AC-8 (US-2): Not signed in**
- Given I am not signed in
- When I open the seat booking page, I am redirected to the login page
- And when I POST a booking to the API, I get 403 and no booking is created
- Django's built-in authentication URLs live under `/accounts/`; the login template is
  `bookings/templates/registration/login.html`, it extends `base.html`, and a successful login
  redirects to `/` by default.

**AC-9: Seat or movie does not exist**
- Given no movie with id 9999 and no seat with id 9999 exist
- When I open the seat page for movie 9999, I get 404
- And when I POST to /api/seats/book/ naming either id, I get 400 with a field error for that id
- Unknown IDs use DRF's default related-field errors, for example
  `{"seat": ["Invalid pk \"9999\" - object does not exist."]}`.
- `GET /api/seats/?movie=9999` returns 400 with
  `{"movie": ["Invalid pk \"9999\" - object does not exist."]}` rather than using the
  no-movie response shape.

**AC-10 (US-3): List seats via API**
- Given seats A1-A5 exist
- When a client sends GET /api/seats/ with no movie
- Then the response is 200 with every seat's id, seat number and booking status
- The computed `available` field is absent when no movie is supplied.
- (No movie means no availability answer, since availability only exists per (movie, seat). `booking_status` here is the out-of-service flag, not "booked". AC-11 is the per-movie view.)

**AC-11 (US-3): Seat availability for a movie via API**
- Given seats A1-A5 exist and A2 is booked for Dune
- When a client sends GET /api/seats/?movie=<Dune's id>
- Then the response is 200 and each seat includes a computed boolean field named `available`;
  A2 has `available: false` and the rest have `available: true`

**AC-12 (US-2): Out-of-service seat**
- Given seat A3 has booking_status set to out of service
- When I try to book A3 for any movie
- Then the API returns 400 with `{"detail": "Seat A3 is out of service."}`, no booking is created, and the page
  shows A3 as unavailable for every movie

**AC-13: Seed the grader's demo user**
- Given `DEMO_PASSWORD` is set in the environment
- When `python manage.py seed_demo_user` runs one or more times
- Then one user named `demo` exists and its password is updated to the environment value

## 4. Data
| Thing | Information | Rules |
|---|---|---|
| Seat | seat number, booking status | `seat_number` is required and unique, and matches one uppercase letter followed by one or more digits. A1–A5 are seeded examples, not the only valid values. `booking_status` is `BooleanField(default=False)`; `True` means the seat is out of service entirely, not booked for a movie. |
| Booking | movie, seat, user, booking date | `booking_date` is `DateField(auto_now_add=True)`. User is always the signed-in user (AC-5). A UniqueConstraint on (movie, seat) makes the database refuse a duplicate (AC-4). "The same seat" means the same seat for the same movie. |

## 5. API / UI behavior
| Action | Input | Success result | Failure result |
|---|---|---|---|
| View seats for a movie (page) | `GET /movies/<movie_id>/seats/` | 200, every seat shown available or unavailable for that movie | 404 if the movie does not exist; redirect to `/accounts/login/` if not signed in |
| Book a seat (page) | `POST /movies/<movie_id>/seats/` with the seat id; user comes from the session | redirect to the same seat page with `Seat <seat> booked for <movie>.` | re-render with the AC-3 or AC-12 message and a link to that movie's seat page; redirect to login if not signed in |
| List seats (API) | `GET /api/seats/` with optional `movie` query param | Public 200; includes per-movie `available` only when a valid movie is supplied | 400 with a `movie` field error when the supplied movie id is unknown |
| List movies (API) | `GET /api/movies/` | Public 200 | — |
| Book a seat (API) | `POST /api/seats/book/` with `{movie, seat}`; any `user` input is ignored | Authenticated 201 with `{id, movie, seat, user, booking_date}` | 400 with `detail` for taken/out-of-service; DRF field errors for missing/unknown ids; 403 if not signed in |
| Seed demo user (deployment) | `python manage.py seed_demo_user`; password from `DEMO_PASSWORD` | exactly one `demo` user exists with the supplied password | command error if `DEMO_PASSWORD` is absent |

## 6. Out of scope
- Payments, seat maps with rows and aisles, holding a seat temporarily
- Booking several seats in one request
- Cancelling a booking

## 7. Open Questions
- [x] **Seat has no movie field.** Availability is per (movie, seat). Seat stays as the assignment specifies and Booking carries the movie, so one set of five seats serves every movie. Putting a movie on Seat would mean duplicating all five seats for every movie.
- [x] **One source of truth.** Availability is worked out from Booking each time, never stored. A seat is taken for a movie when a Booking exists for that (movie, seat), so there is nothing to keep in step and the two can never disagree. Seat's `booking_status` keeps the field the assignment requires and means out of service. AC-4 and AC-6 would catch a disagreement.
- [x] **Where booking lives.** One function, `book_seat(user, movie, seat)` in `bookings/services.py`. The page view, SeatViewSet and (in 003) BookingViewSet all call it. Copying the rules into each would let them drift apart and break AC-6.
- [x] **Cancelling:** out of scope, not in the assignment.
- [x] **Grader access:** an idempotent `seed_demo_user` management command creates or updates the
      `demo` user using the `DEMO_PASSWORD` environment variable. Render's build command runs it after
      migrations. The password is never committed; it is given in the Canvas submission comment, so
      the repo stays clean even though it is public.
