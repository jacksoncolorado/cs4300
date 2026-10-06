# Spec: Seat booking

**Status:** Draft: **you finish this spec**
**Author:** <your name>  **Date:** <YYYY-MM-DD>

> The user stories (US-#) and first acceptance criteria (AC-#) are started for you. Every `TODO` is a decision **you**
> make. Compare with `001-movie-listings/spec.md` for the level of detail to aim for.

## 1. Problem
A moviegoer who has picked a movie needs to see which seats are free and reserve one.
(Homework 2, or HW2, §1 "Book seats via the API"; §3.3 `SeatViewSet` "for seat availability and booking";
§3.5 `/api/seats/`; template `seat_booking.html`.)

## 2. User stories
- **US-1:** As a moviegoer, I want to see which seats are available for a movie, so that I can choose one.
- **US-2:** As a moviegoer, I want to book an available seat, so that it's reserved for me.
- **US-3:** As an API client, I want to check seat availability and book seats through `/api/seats/`.
  (HW2 also has `/api/bookings/` create bookings; see AC-6 and feature 003.)
- TODO: anything else? (For example, can a moviegoer book more than one seat at a time?)

## 3. Acceptance criteria

**AC-1 (US-1): Seat availability page**
- Given the movie "Dune" and seats A1–A5, where A2 is already booked
- When I click "Book Now" for Dune
- Then I see the seat booking page for Dune, with A2 shown as unavailable and the others as available
- (This is where "Book Now" on the movie list, disabled in 001, becomes a real link.)

**AC-2 (US-2): Book an available seat**
- Given I am signed in and seat A1 is available for Dune
- When I book A1
- Then TODO: what does the user see, and what changes in the data?

**AC-3 (US-2): Seat already taken**
- Given seat A2 is already booked for Dune
- When I try to book A2
- Then TODO: what happens in the UI? What status code does the API return?

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

- TODO **AC-8:** What if the user isn't signed in?
- TODO **AC-9:** What if the seat or movie doesn't exist?
- TODO **AC-10+:** API criteria for `/api/seats/`: list, availability, booking.

## 4. Data
| Thing | Information | Rules |
|---|---|---|
| Seat | seat number, booking status | TODO: is the seat number unique? What format? Is booking status stored, or worked out from bookings? (See Open questions.) |
| Booking | movie, seat, user, booking date | User is always the signed-in user (AC-5). No two bookings of the same seat, enforced by the database (AC-4). TODO: "the same seat" means the same seat, or the same seat *for the same movie*? |

## 5. API / UI behavior
| Action | Input | Success result | Failure result |
|---|---|---|---|
| View seats for a movie (page) | movie | TODO | TODO |
| List seats (API) | TODO | TODO | TODO |
| Book a seat (API + page) | TODO | TODO | TODO |

## 6. Out of scope
- TODO: e.g., payments, seat maps with rows and aisles, holding a seat for 10 minutes

## 7. Open questions
- [ ] **The assignment's Seat model has no movie field.** Is a seat booked for *every* movie, or
      is availability per movie? How do the Seat and Booking models together answer that? Decide,
      and write down why.
- [ ] **One source of truth for "is this seat taken?"** Seat has a booking status, and Booking
      also records that the seat is taken. If they disagree (a booking exists but the status says
      "available"), which one is right? Decide: is the status **stored** on Seat, or **worked out**
      from bookings each time? A good answer says: (1) whether availability is global or per
      (movie, seat), (2) which data is the source of truth, (3) if you store the status, every place
      that must update it (book, cancel, admin, delete) and how you keep them in step, and (4) which
      AC and test would catch them disagreeing.
- [ ] **Where does "book a seat" live?** HW2 lets you book through `/api/seats/` *and*
      `/api/bookings/` (built in 003), and the page books too. All three must follow the same rules
      (AC-6 here, AC-7 in 003). Decide which one operation they all call. A good answer names the single
      place the rules (seat free? signed in? who's the user?) live, and why copying them would break AC-6.
- [ ] Can a booking be cancelled? If so, does that belong in this feature or in 003?
- [ ] TODO
