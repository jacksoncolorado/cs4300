# Spec: Seat booking

**Status:** Ready for plan
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
- (This is where "Book Now" on the movie list, disabled in 001, becomes a real link.)

**AC-2 (US-2): Book an available seat**
- Given I am signed in and seat A1 is available for Dune
- When I book A1
- Then a Booking is created for me, that movie and that seat, with today's date
- And I am returned to the seat page for Dune with a success message
- And A1 now shows as unavailable

**AC-3 (US-2): Seat already taken**
- Given seat A2 is already booked for Dune
- When I try to book A2
- Then the API returns 400 with a message naming the seat and the movie, the page re-renders with that message and a link back, and no second booking is created

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

**AC-9: Seat or movie does not exist**
- Given no movie with id 9999 and no seat with id 9999 exist
- When I open the seat page for movie 9999, I get 404
- And when I POST to /api/seats/book/ naming either id, I get 400 with a field error for that id

**AC-10 (US-3): List seats via API**
- Given seats A1-A5 exist
- When a client sends GET /api/seats/ with no movie
- Then the response is 200 with every seat's id, seat number and booking status
- (No movie means no availability answer, since availability only exists per (movie, seat). `booking_status` here is the out-of-service flag, not "booked". AC-11 is the per-movie view.)

**AC-11 (US-3): Seat availability for a movie via API**
- Given seats A1-A5 exist and A2 is booked for Dune
- When a client sends GET /api/seats/?movie=<Dune's id>
- Then the response is 200, A2 is marked unavailable, and the rest are available

**AC-12 (US-2): Out-of-service seat**
- Given seat A3 has booking_status set to out of service
- When I try to book A3 for any movie
- Then the API returns 400 saying the seat is out of service, no booking is created, and the page
  shows A3 as unavailable for every movie

## 4. Data
| Thing | Information | Rules |
|---|---|---|
| Seat | seat number, booking status | Seat number is required and unique, format letter + number (A1-A5). `booking_status` means the seat is out of service entirely, not booked for a movie. |
| Booking | movie, seat, user, booking date | User is always the signed-in user (AC-5). A UniqueConstraint on (movie, seat) makes the database refuse a duplicate (AC-4). "The same seat" means the same seat for the same movie. |

## 5. API / UI behavior
| Action | Input | Success result | Failure result |
|---|---|---|---|
| View seats for a movie (page) | movie id | 200, every seat shown available or unavailable for that movie | 404 if the movie does not exist; redirect to login if not signed in |
| List seats (API) | optional `movie` query param | 200, seats with availability for that movie when given | — |
| Book a seat (API + page) | `POST /api/seats/book/` with `{movie, seat}` in the body; user comes from the session | 201 from the API, redirect with a success message from the page | 400 if the seat is taken, out of service, missing or unknown; 403 if not signed in |

## 6. Out of scope
- Payments, seat maps with rows and aisles, holding a seat temporarily
- Booking several seats in one request
- Cancelling a booking

## 7. Open Questions
- [x] **Seat has no movie field.** Availability is per (movie, seat). Seat stays as the assignment specifies and Booking carries the movie, so one set of five seats serves every movie. Putting a movie on Seat would mean duplicating all five seats for every movie.
- [x] **One source of truth.** Availability is worked out from Booking each time, never stored. A seat is taken for a movie when a Booking exists for that (movie, seat), so there is nothing to keep in step and the two can never disagree. Seat's `booking_status` keeps the field the assignment requires and means out of service. AC-4 and AC-6 would catch a disagreement.
- [x] **Where booking lives.** One function, `book_seat(user, movie, seat)` in `bookings/services.py`. The page view, SeatViewSet and (in 003) BookingViewSet all call it. Copying the rules into each would let them drift apart and break AC-6.
- [x] **Cancelling:** out of scope, not in the assignment.
- [x] **Grader access:** the seed migration creates a demo user whose password comes from the `DEMO_PASSWORD` environment variable. The password is never committed; it is given in the Canvas submission comment, so the repo stays clean even though it is public.