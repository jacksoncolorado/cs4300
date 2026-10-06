# Spec: Movie listings

**Status:** Reviewed (worked example: change anything you'd do differently)
**Author:** <your name>  **Date:** <YYYY-MM-DD>

## 1. Problem
Moviegoers need to see what's showing before they can book a seat. Staff need to add, update
and remove movies. (Homework 2, or HW2, §1 and §3.3: "View movie listings", and `MovieViewSet` "for CRUD operations",
where CRUD means create, read, update, delete.)

## 2. User stories
> 📖 **Book:** [§3.4.1 Guidelines for Effective User Stories](https://www.swebook.org/chapters/03-user-requirements/index.html#341-guidelines-for-effective-user-stories) (INVEST: Independent, Negotiable, Valuable, Estimable, Small, Testable)

Each user story (US-#) is numbered so the acceptance criteria can trace back to it.

- **US-1:** As a moviegoer, I want to see a list of movies, so that I can pick one to watch.
- **US-2:** As a moviegoer, I want to see a movie's details (description, release date,
  duration), so that I can decide whether to watch it.
- **US-3:** As an API client, I want to create, read, update and delete movies, so that the
  listings can be managed.

## 3. Acceptance criteria
Each acceptance criterion (AC-#) names the user story it checks, e.g., AC-1 (US-1).

> 📖 **Book:** [§3.4.1 Given / When / Then](https://www.swebook.org/chapters/03-user-requirements/index.html#given--when--then-writing-acceptance-criteria-as-scenarios). AC-6 tests the boundary (duration 0): [§10.4.2 boundary values](https://www.swebook.org/chapters/10-testing/index.html#1042-boundary-value-coverage).

**AC-1 (US-1): List movies in the UI**
- Given the movies "Dune" and "Up" exist
- When I open the movie list page
- Then I see both titles, each with its description and a "Book Now" button
- (The button is shown but disabled until feature 002 adds the seat booking page. 002 makes it a link.)

**AC-2 (US-1): Empty state**
- Given no movies exist
- When I open the movie list page
- Then I see "No movies are showing right now" instead of an empty list

**AC-3 (US-2): Movie details shown**
- Given "Dune" has a release date of 2021-10-22 and a duration of 155 minutes
- When I view the movie list
- Then Dune's release date and duration are shown in a readable format

**AC-4 (US-3): List via API**
- Given two movies exist
- When a client sends `GET /api/movies/`
- Then the response is 200 with a JSON list of 2 movies, each with id, title, description,
  release date and duration

**AC-5 (US-3): Create via API**
- Given valid movie data
- When a client sends `POST /api/movies/`
- Then the response is 201 and the movie appears in `GET /api/movies/`

**AC-6 (US-3): Reject invalid data**
- Given movie data with a missing title, a missing release date, or a duration of 0 or less
- When a client sends `POST /api/movies/`
- Then the response is 400 with an error for that field, and nothing is saved

**AC-7 (US-3): Update and delete**
- Given a movie exists
- When a client sends `PUT`/`PATCH /api/movies/<id>/`, then `DELETE /api/movies/<id>/`
- Then the update returns 200 with the new values, the delete returns 204, and the movie is gone

**AC-8 (US-3): Get one movie, or a missing one**
- Given "Dune" exists and no movie with id 9999 exists
- When a client sends `GET /api/movies/<Dune's id>/`, then `GET /api/movies/9999/`
- Then the first response is 200 with Dune's fields, and the second is 404

**AC-9 (UI): Consistent, responsive layout**
- Given the movie list page
- When it renders
- Then it extends `base.html` (Bootstrap), with a navbar linking to Movies
- (002 and 003 each add the same criterion, with its own test, for their page. 003 adds the
  My Bookings link to the navbar once that page exists.)

## 4. Data
| Thing | Information | Rules |
|---|---|---|
| Movie | title | **Required**; at most 200 characters |
| Movie | description | Optional (may be blank) |
| Movie | release date | **Required**; a valid date |
| Movie | duration | **Required**; whole minutes, greater than 0 |

## 5. API / UI behavior
| Action | Input | Success result | Failure result |
|---|---|---|---|
| View movie list page | — | page with every movie and a "Book Now" button | — |
| List movies (API) | — | 200, list | — |
| Get one movie (API) | id | 200, movie | 404 |
| Create movie (API) | title, description, release date, duration | 201, movie | 400 + field errors |
| Update movie (API) | id + fields | 200, movie | 400 / 404 |
| Delete movie (API) | id | 204 | 404 |

## 6. Out of scope
- Showtimes, theaters, posters, ratings, search
- Restricting movie create/update/delete to staff (a decision to note in the README; revisit if time allows)

## 7. Open questions
- [x] Duration in minutes or as `HH:MM`? → **Integer minutes.** Simpler to validate and test.
- [x] Order of the list? → **By release date, newest first.**
- [ ] TODO (decide): this example makes description optional and the other three fields required.
      Do you agree? Could a movie be announced before it has a release date? A good answer says,
      for each field, whether it's required, what the API returns when it's missing or invalid,
      and which AC and test prove it. If you change a rule, update §4, AC-6, the plan and the tasks.
