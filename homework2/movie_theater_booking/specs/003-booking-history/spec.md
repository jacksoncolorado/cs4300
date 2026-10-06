# Spec: Booking history

**Status:** Draft: **you finish this spec**
**Author:** <your name>  **Date:** <YYYY-MM-DD>

> The user stories (US-#) and first acceptance criteria (AC-#) are started for you. Every `TODO` is a decision **you** make.

## 1. Problem
Moviegoers need to see what they've booked. (Homework 2, or HW2, §1 "Check their booking history via the API";
§3.3 `BookingViewSet` "for users to book seats and view their booking history"; §3.5
`/api/bookings/`; template `booking_history.html`.)

## 2. User stories
- **US-1:** As a moviegoer, I want to see a list of my bookings, so that I know what I've reserved.
- **US-2:** As an API client, I want to view booking history and create bookings through `/api/bookings/`.
- **US-3:** As a moviegoer, I want my bookings kept private, so that other users can't see them.
- TODO: anything else?

## 3. Acceptance criteria

**AC-1 (US-1): See my bookings**
- Given I am signed in and have booked seat A1 for "Dune"
- When I open My Bookings
- Then I see Dune, seat A1 and the booking date

**AC-2 (US-1, US-3): Only my bookings**
- Given users Sam and Alex each have bookings
- When Sam opens My Bookings, or sends `GET /api/bookings/`
- Then only Sam's bookings appear, and none of Alex's

**AC-3 (US-3): Someone else's booking**
- Given Alex has a booking with id 7
- When Sam sends `GET /api/bookings/7/`
- Then none of Alex's booking data is returned. TODO: 404 or 403? Decide, and say why.

**AC-4 (UI): Consistent layout**
- Given the My Bookings page
- When it renders
- Then it extends `base.html`, and the navbar now links to both Movies and My Bookings

- TODO **AC-5:** Empty state: what does a user with no bookings see?
- TODO **AC-6:** Not signed in: page behavior and API status code.
- TODO **AC-7:** Creating a booking with `POST /api/bookings/`: success, and a seat that's already taken.
  This must follow the same booking rules as 002 (002's AC-4, AC-5 and AC-6): a seat booked through
  `/api/seats/` or the page is refused here, and the booking's user is the signed-in user even if the
  request data names someone else. Reuse 002's booking operation. Don't build the rule twice.
- TODO **AC-8:** Order of the list.

## 4. Data
| Thing | Information | Rules |
|---|---|---|
| Booking | movie, seat, user, booking date | Only ever shown to its own user (AC-2, AC-3). TODO: anything else? |

## 5. API / UI behavior
| Action | Input | Success result | Failure result |
|---|---|---|---|
| My Bookings page | — | TODO | TODO |
| List bookings (API) | — | TODO | TODO |
| Create booking (API) | TODO | TODO | TODO |

## 6. Out of scope
- TODO

## 7. Open questions
- [ ] AC-2 and AC-3 say users only see their own bookings. Why is this a **security** requirement,
      not just a feature choice? Could an admin or staff user ever see everyone's? If so, write that
      as its own AC. 📖 **Book:** [§11.2.1 A01: Broken Access Control](https://www.swebook.org/chapters/11-software-security/index.html#1121-a01-broken-access-control)
- [ ] TODO
