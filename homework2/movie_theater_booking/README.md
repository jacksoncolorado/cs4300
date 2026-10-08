# Homework 2 — Movie Theater Booking

A Django and Django REST Framework app for browsing movies, booking seats, and viewing your
booking history. Every feature works both as a web page and through the API.

**Live site:** https://movie-theater-booking-z7d3.onrender.com

## Features

- **Movie listings** — browse movies with release date and duration; full CRUD through the API
- **Seat booking** — see which seats are free for a given movie and reserve one. Availability is
  per movie, so the same physical seat can be free for one film and taken for another
- **Booking history** — see only your own bookings, newest first

## Project structure

```
homework2/movie_theater_booking/
├── bookings/
│   ├── models.py          Movie, Seat, Booking
│   ├── services.py        book_seat(), the one place the booking rules live
│   ├── serializers.py     API input and output shapes
│   ├── views.py           page views and DRF viewsets
│   ├── urls.py            page routes and the API router
│   ├── admin.py
│   ├── migrations/        schema plus idempotent seed data
│   ├── management/commands/seed_demo_user.py
│   ├── templates/bookings/   base, movie_list, seat_booking, booking_history
│   └── tests.py
├── features/              Behave scenarios and step definitions
├── specs/                 spec, plan and tasks for each of the three features
├── movie_theater_booking/ settings and root URLs
├── requirements.txt
└── manage.py
```

## Setup

```bash
cd homework2/movie_theater_booking
python3 -m venv myenv --system-site-packages
source myenv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

In DevEdu, run on port 3000 instead:

```bash
python manage.py runserver 0.0.0.0:3000
```

No environment variables are needed for local development. In production `DEBUG` is off and
`SECRET_KEY` must be supplied; both are read from the environment.

## Running the tests

```bash
python manage.py test                                              # 76 tests
python manage.py behave                                            # 13 BDD scenarios
coverage run --source=bookings manage.py test && coverage report   # 99%
```

## Pages

| URL | What it does |
|---|---|
| `/` | movie list |
| `/movies/<id>/seats/` | seat availability and booking for one movie (sign-in required) |
| `/bookings/` | your booking history (sign-in required) |
| `/accounts/login/` | sign in |
| `/admin/` | Django admin |

## API

| Method | Endpoint | Notes |
|---|---|---|
| GET, POST | `/api/movies/` | public |
| GET, PUT, PATCH, DELETE | `/api/movies/<id>/` | public |
| GET | `/api/seats/` | public; add `?movie=<id>` for per-movie availability |
| POST | `/api/seats/book/` | sign-in required; body `{movie, seat}` |
| GET | `/api/bookings/` | sign-in required; only your own bookings |
| GET | `/api/bookings/<id>/` | sign-in required; 404 for another user's booking |
| POST | `/api/bookings/` | sign-in required; body `{movie, seat}` |

The seat page, `/api/seats/book/` and `/api/bookings/` all call the same `book_seat()` service, so
the rules and error messages are identical no matter which one you use.

## For the grader

A `demo` account is created automatically on each deploy. The password is in the Canvas submission
comment rather than this repository, which is public.

Two notes about Render's free tier: the first request after a quiet period takes about 30 seconds
while the instance wakes up, and the disk is wiped on every deploy, so bookings made before a
deploy are gone afterwards. Movies, seats and the demo account are recreated automatically.

## Known limitations

- Movie create, update and delete are not restricted to staff. This was deliberately deferred in
  `specs/001-movie-listings/spec.md`.
- Bookings cannot be cancelled; `PUT`, `PATCH` and `DELETE` on a booking return 405.
- Seat availability runs one query per seat, which is fine for five seats but would need a single
  annotated query at larger scale.

## AI usage

**Tool:** Codex (UCCS). Claude and Pardot were also used for planning and review discussion.

**Used for:** reviewing the specs I wrote, drafting each feature's plan and task breakdown, and
implementing each task test-first.

**How I used the output:** I wrote all three specs myself and made the design decisions in them —
that seat availability is per (movie, seat) and derived from `Booking` rather than stored, that a
single `book_seat()` service owns the rules for all three entry points, and that another user's
booking returns 404 rather than 403 so the response cannot confirm it exists. Codex reviewed those
specs and raised questions I then answered, and implemented one task at a time. I read every diff
and ran the suite before each commit, and ran the final review in a separate Codex session so the
code was not evaluated by the session that wrote it. The full log is in `AI-USAGE.md`.
