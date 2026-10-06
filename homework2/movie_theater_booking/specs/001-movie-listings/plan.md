# Plan: Movie listings

**Spec:** [spec.md](spec.md)   **Status:** Approved (worked example)

## 1. Approach
One `Movie` model, a `ModelSerializer`, and a Django REST Framework (DRF) `ModelViewSet` registered on a
`DefaultRouter` at `/api/movies/`. That gives full create, read, update, delete (CRUD) support with correct status codes and very little
code. The UI is a plain Django view that renders `movie_list.html` from the same model, so the
page and the API always show the same data.
**Rejected:** writing separate `APIView`s for list, create and detail. It's more code, and the
assignment specifically asks for viewsets.

> 📖 **Book:** Django's Model-Template-View (MTV) pattern applies ideas closely related to [§7.3 Model-View-Controller](https://www.swebook.org/chapters/07-architectural-patterns/index.html#73-user-interfaces-model-view-controller), with different names and role boundaries; a viewset exposes a resource through HTTP verbs, [§7.5.4 RESTful APIs](https://www.swebook.org/chapters/07-architectural-patterns/index.html#754-restful-apis).

## 2. Data model
Each **Spec ref** names the acceptance criterion (AC-#) in [spec.md](spec.md) that the row serves.

| Model | Field | Type | Constraints | Spec ref |
|---|---|---|---|---|
| Movie | title | CharField | max_length=200, required | AC-6 |
| Movie | description | TextField | `blank=True` (optional) | AC-1 |
| Movie | release_date | DateField | required | AC-3, AC-6 |
| Movie | duration | PositiveIntegerField | required; minutes; > 0 (validator, because the field allows 0) | AC-3, AC-6 |
| Movie | — | `Meta.ordering = ["-release_date"]`, `__str__` returns title | — | Open Q |

## 3. Endpoints / views
| Method | URL | View / ViewSet | Returns | Spec ref |
|---|---|---|---|---|
| GET | `/api/movies/` | MovieViewSet.list | 200 list | AC-4 |
| POST | `/api/movies/` | MovieViewSet.create | 201 / 400 | AC-5, AC-6 |
| GET | `/api/movies/<id>/` | MovieViewSet.retrieve | 200 / 404 | AC-8 |
| PUT/PATCH | `/api/movies/<id>/` | MovieViewSet.update | 200 / 400 / 404 | AC-7 |
| DELETE | `/api/movies/<id>/` | MovieViewSet.destroy | 204 / 404 | AC-7 |
| GET | `/` (named `movie_list`) | `movie_list` view → `movie_list.html` | HTML | AC-1–3, AC-9 |

## 4. Files to create / change
| File | Change |
|---|---|
| `movie_theater_booking/settings.py` | add `rest_framework`, `bookings`, `behave_django` to `INSTALLED_APPS` |
| `movie_theater_booking/urls.py` | include `bookings.urls` |
| `bookings/models.py` | `Movie` |
| `bookings/serializers.py` | `MovieSerializer` (duration > 0 validation) |
| `bookings/views.py` | `MovieViewSet`, `movie_list` |
| `bookings/urls.py` | router + `movie_list` route |
| `bookings/templates/bookings/base.html` | Bootstrap CSS link, navbar (Movies only for now), `{% block content %}` |
| `bookings/templates/bookings/movie_list.html` | list + empty state; "Book Now" is a disabled button with no `{% url %}` yet (see Risks) |
| `bookings/tests.py` | model, API and view tests |
| `features/movie_listings.feature`, `features/steps/` | Behave scenarios, run with `python manage.py behave` (behave-django sets up Django, so there's no hand-written `environment.py`) |

## 5. Test strategy
| Spec ref | Test type | Test name / scenario |
|---|---|---|
| AC-1 | Behave | "Browse the movie list" |
| AC-2 | view test + Behave | `test_movie_list_empty_state`, "No movies showing" |
| AC-3 | view test | `test_movie_list_shows_release_date_and_duration` |
| AC-4 | API | `test_list_movies` |
| AC-5 | API | `test_create_movie` |
| AC-6 | API | `test_create_movie_missing_title_400`, `test_create_movie_missing_release_date_400`, `test_create_movie_zero_duration_400` |
| AC-7 | API | `test_update_movie`, `test_delete_movie` |
| AC-8 | API | `test_retrieve_movie`, `test_get_missing_movie_404` |
| AC-9 | view test | `test_movie_list_uses_base_template` (`assertTemplateUsed`) |

## 6. Risks & decisions
- Anyone can create, update or delete movies for now (see Out of scope). Say so in the README.
- `Seat` and `Booking` are left to features 002 and 003. Don't add them here "while we're at it."
- "Book Now" can't link anywhere yet. `{% url 'book_seat' movie.id %}` would raise `NoReverseMatch`
  and break the page until 002 adds that route. So 001 renders a disabled button, and 002 turns it
  into the link (and tests it). The same goes for the navbar's My Bookings link, which 003 adds.
