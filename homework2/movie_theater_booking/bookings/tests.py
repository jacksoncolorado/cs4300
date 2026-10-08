import importlib
import os
import subprocess
import sys
from datetime import date

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import SimpleTestCase, TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Booking, Movie, Seat
from .services import SeatBookingError, book_seat


class SeatAPITests(APITestCase):
    def setUp(self):
        Booking.objects.all().delete()
        Movie.objects.all().delete()
        Seat.objects.all().delete()

    def test_list_seats_without_movie_omits_available(self):
        available_seat = Seat.objects.create(seat_number="A1")
        unavailable_seat = Seat.objects.create(
            seat_number="A2",
            booking_status=True,
        )

        response = self.client.get("/api/seats/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        seats = {seat["seat_number"]: seat for seat in response.json()}
        self.assertEqual(
            seats,
            {
                "A1": {
                    "id": available_seat.id,
                    "seat_number": "A1",
                    "booking_status": False,
                },
                "A2": {
                    "id": unavailable_seat.id,
                    "seat_number": "A2",
                    "booking_status": True,
                },
            },
        )
        self.assertTrue(all("available" not in seat for seat in seats.values()))

    def test_list_seats_for_movie_shows_availability(self):
        movie = Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )
        available_seat = Seat.objects.create(seat_number="A1")
        booked_seat = Seat.objects.create(seat_number="A2")
        out_of_service_seat = Seat.objects.create(
            seat_number="A3",
            booking_status=True,
        )
        user = get_user_model().objects.create_user(username="sam")
        Booking.objects.create(
            movie=movie,
            seat=booked_seat,
            user=user,
        )

        response = self.client.get(f"/api/seats/?movie={movie.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        seats = {seat["seat_number"]: seat for seat in response.json()}
        self.assertTrue(seats[available_seat.seat_number]["available"])
        self.assertFalse(seats[booked_seat.seat_number]["available"])
        self.assertFalse(seats[out_of_service_seat.seat_number]["available"])

    def test_filter_unknown_movie_returns_field_error(self):
        response = self.client.get("/api/seats/?movie=9999")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"movie": ['Invalid pk "9999" - object does not exist.']},
        )

    def test_anonymous_api_booking_403(self):
        movie = Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )
        seat = Seat.objects.create(seat_number="A1")

        response = self.client.post(
            "/api/seats/book/",
            {"movie": movie.id, "seat": seat.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Booking.objects.exists())

    def test_book_available_seat_api_returns_created_booking(self):
        movie = Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )
        seat = Seat.objects.create(seat_number="A1")
        user = get_user_model().objects.create_user(username="sam")
        self.client.force_authenticate(user=user)

        response = self.client.post(
            "/api/seats/book/",
            {"movie": movie.id, "seat": seat.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        booking = Booking.objects.get()
        self.assertEqual(
            response.json(),
            {
                "id": booking.id,
                "movie": movie.id,
                "seat": seat.id,
                "user": user.id,
                "booking_date": date.today().isoformat(),
            },
        )

    def test_booking_user_is_request_user_not_request_data(self):
        movie = Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )
        seat = Seat.objects.create(seat_number="A1")
        signed_in_user = get_user_model().objects.create_user(username="sam")
        supplied_user = get_user_model().objects.create_user(username="alex")
        self.client.force_authenticate(user=signed_in_user)

        response = self.client.post(
            "/api/seats/book/",
            {"movie": movie.id, "seat": seat.id, "user": supplied_user.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        booking = Booking.objects.get()
        self.assertEqual(booking.user, signed_in_user)
        self.assertEqual(response.json()["user"], signed_in_user.id)

    def test_booking_unknown_movie_returns_field_error(self):
        seat = Seat.objects.create(seat_number="A1")
        user = get_user_model().objects.create_user(username="sam")
        self.client.force_authenticate(user=user)

        response = self.client.post(
            "/api/seats/book/",
            {"movie": 9999, "seat": seat.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"movie": ['Invalid pk "9999" - object does not exist.']},
        )
        self.assertFalse(Booking.objects.exists())

    def test_booking_unknown_seat_returns_field_error(self):
        movie = Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )
        user = get_user_model().objects.create_user(username="sam")
        self.client.force_authenticate(user=user)

        response = self.client.post(
            "/api/seats/book/",
            {"movie": movie.id, "seat": 9999},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"seat": ['Invalid pk "9999" - object does not exist.']},
        )
        self.assertFalse(Booking.objects.exists())

    def test_duplicate_booking_returns_error_not_500(self):
        movie = Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )
        seat = Seat.objects.create(seat_number="A1")
        user = get_user_model().objects.create_user(username="sam")
        Booking.objects.create(movie=movie, seat=seat, user=user)
        self.client.force_authenticate(user=user)

        response = self.client.post(
            "/api/seats/book/",
            {"movie": movie.id, "seat": seat.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"detail": "Seat A1 is already booked for Dune."},
        )
        self.assertEqual(Booking.objects.count(), 1)

    def test_out_of_service_seat_api_returns_detail_400(self):
        movie = Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )
        seat = Seat.objects.create(seat_number="A3", booking_status=True)
        user = get_user_model().objects.create_user(username="sam")
        self.client.force_authenticate(user=user)

        response = self.client.post(
            "/api/seats/book/",
            {"movie": movie.id, "seat": seat.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"detail": "Seat A3 is out of service."},
        )
        self.assertFalse(Booking.objects.exists())


class BookingServiceTests(TestCase):
    def setUp(self):
        Booking.objects.all().delete()
        Movie.objects.all().delete()
        Seat.objects.all().delete()
        self.movie = Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )
        self.seat = Seat.objects.create(seat_number="A1")
        self.user = get_user_model().objects.create_user(username="sam")

    def test_book_seat_creates_booking(self):
        booking = book_seat(self.user, self.movie, self.seat)

        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.movie, self.movie)
        self.assertEqual(booking.seat, self.seat)
        self.assertEqual(Booking.objects.count(), 1)

    def test_book_seat_rejects_taken_seat(self):
        Booking.objects.create(
            user=self.user,
            movie=self.movie,
            seat=self.seat,
        )

        with self.assertRaisesMessage(
            SeatBookingError,
            "Seat A1 is already booked for Dune.",
        ):
            book_seat(self.user, self.movie, self.seat)

        self.assertEqual(Booking.objects.count(), 1)

    def test_book_seat_rejects_out_of_service_seat(self):
        self.seat.booking_status = True
        self.seat.save()

        with self.assertRaisesMessage(
            SeatBookingError,
            "Seat A1 is out of service.",
        ):
            book_seat(self.user, self.movie, self.seat)

        self.assertFalse(Booking.objects.exists())


class BookingModelTests(TestCase):
    def setUp(self):
        Booking.objects.all().delete()
        Movie.objects.all().delete()
        Seat.objects.all().delete()
        self.movie = Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )
        self.seat = Seat.objects.create(seat_number="A1")
        self.user = get_user_model().objects.create_user(username="sam")

    def test_booking_records_user_movie_seat_and_date(self):
        booking = Booking.objects.create(
            movie=self.movie,
            seat=self.seat,
            user=self.user,
        )

        self.assertEqual(booking.movie, self.movie)
        self.assertEqual(booking.seat, self.seat)
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.booking_date, date.today())

    def test_duplicate_booking_rejected_by_database(self):
        Booking.objects.create(
            movie=self.movie,
            seat=self.seat,
            user=self.user,
        )
        another_user = get_user_model().objects.create_user(username="alex")

        with self.assertRaises(IntegrityError), transaction.atomic():
            Booking.objects.create(
                movie=self.movie,
                seat=self.seat,
                user=another_user,
            )

        self.assertEqual(Booking.objects.count(), 1)


class SeatModelTests(TestCase):
    def setUp(self):
        Seat.objects.all().delete()

    def test_seat_str_and_default_booking_status(self):
        seat = Seat.objects.create(seat_number="A1")

        self.assertEqual(str(seat), "A1")
        self.assertFalse(seat.booking_status)

    def test_seat_number_validation(self):
        Seat.objects.create(seat_number="A1")

        for invalid_number in ("a1", "AA1", "A", "1"):
            with self.subTest(seat_number=invalid_number):
                with self.assertRaises(ValidationError):
                    Seat(seat_number=invalid_number).full_clean()

        with self.assertRaises(ValidationError):
            Seat(seat_number="A1").full_clean()

        Seat(seat_number="Z123").full_clean()

    def test_seed_seats_is_idempotent(self):
        migration = importlib.import_module("bookings.migrations.0004_seed_seats")

        migration.seed_seats(importlib.import_module("django.apps").apps, None)
        migration.seed_seats(importlib.import_module("django.apps").apps, None)

        self.assertEqual(Seat.objects.count(), 5)
        self.assertEqual(
            set(Seat.objects.values_list("seat_number", flat=True)),
            {"A1", "A2", "A3", "A4", "A5"},
        )


class MovieModelTests(TestCase):
    def setUp(self):
        Movie.objects.all().delete()

    def test_movie_str_and_ordering(self):
        older_movie = Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )
        newer_movie = Movie.objects.create(
            title="Dune: Part Two",
            description="Paul Atreides unites with Chani and the Fremen.",
            release_date="2024-03-01",
            duration=166,
        )

        self.assertEqual(str(older_movie), "Dune")
        self.assertEqual(list(Movie.objects.all()), [newer_movie, older_movie])


class MovieAPITests(APITestCase):
    def setUp(self):
        Movie.objects.all().delete()

    def test_list_movies(self):
        older_movie = Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )
        newer_movie = Movie.objects.create(
            title="Dune: Part Two",
            description="Paul Atreides unites with Chani and the Fremen.",
            release_date="2024-03-01",
            duration=166,
        )

        response = self.client.get("/api/movies/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            [
                {
                    "id": newer_movie.id,
                    "title": "Dune: Part Two",
                    "description": "Paul Atreides unites with Chani and the Fremen.",
                    "release_date": "2024-03-01",
                    "duration": 166,
                },
                {
                    "id": older_movie.id,
                    "title": "Dune",
                    "description": "A noble family becomes embroiled in a war.",
                    "release_date": "2021-10-22",
                    "duration": 155,
                },
            ],
        )

    def test_create_movie(self):
        movie_data = {
            "title": "Up",
            "description": "A widower travels to South America in his house.",
            "release_date": "2009-05-29",
            "duration": 96,
        }

        create_response = self.client.post(
            "/api/movies/", movie_data, format="json"
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        movie = Movie.objects.get()
        self.assertEqual(
            create_response.json(),
            {"id": movie.id, **movie_data},
        )

        list_response = self.client.get("/api/movies/")
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.json(), [{"id": movie.id, **movie_data}])

    def test_create_movie_missing_title_400(self):
        movie_data = {
            "description": "A widower travels to South America in his house.",
            "release_date": "2009-05-29",
            "duration": 96,
        }

        response = self.client.post("/api/movies/", movie_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.json())
        self.assertFalse(Movie.objects.exists())

    def test_create_movie_missing_release_date_400(self):
        movie_data = {
            "title": "Up",
            "description": "A widower travels to South America in his house.",
            "duration": 96,
        }

        response = self.client.post("/api/movies/", movie_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("release_date", response.json())
        self.assertFalse(Movie.objects.exists())

    def test_create_movie_zero_duration_400(self):
        movie_data = {
            "title": "Up",
            "description": "A widower travels to South America in his house.",
            "release_date": "2009-05-29",
            "duration": 0,
        }

        response = self.client.post("/api/movies/", movie_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("duration", response.json())
        self.assertFalse(Movie.objects.exists())

    def test_retrieve_movie(self):
        movie = Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )

        response = self.client.get(f"/api/movies/{movie.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "id": movie.id,
                "title": "Dune",
                "description": "A noble family becomes embroiled in a war.",
                "release_date": "2021-10-22",
                "duration": 155,
            },
        )

    def test_get_missing_movie_404(self):
        response = self.client.get("/api/movies/9999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_movie(self):
        movie = Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )
        url = f"/api/movies/{movie.id}/"
        replacement_data = {
            "title": "Dune: Part Two",
            "description": "Paul Atreides unites with Chani and the Fremen.",
            "release_date": "2024-03-01",
            "duration": 166,
        }

        put_response = self.client.put(url, replacement_data, format="json")

        self.assertEqual(put_response.status_code, status.HTTP_200_OK)
        self.assertEqual(put_response.json(), {"id": movie.id, **replacement_data})
        movie.refresh_from_db()
        self.assertEqual(movie.title, "Dune: Part Two")
        self.assertEqual(movie.duration, 166)

        patch_response = self.client.patch(
            url, {"title": "Dune: Part Two — Extended"}, format="json"
        )

        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.json()["title"], "Dune: Part Two — Extended")
        movie.refresh_from_db()
        self.assertEqual(movie.title, "Dune: Part Two — Extended")

    def test_delete_movie(self):
        movie = Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )

        response = self.client.delete(f"/api/movies/{movie.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Movie.objects.filter(id=movie.id).exists())


class MovieViewTests(TestCase):
    def setUp(self):
        Movie.objects.all().delete()

    def test_movie_list_uses_base_template(self):
        Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookings/movie_list.html")
        self.assertTemplateUsed(response, "bookings/base.html")
        self.assertContains(response, "cdn.jsdelivr.net/npm/bootstrap")
        self.assertContains(response, '<a class="navbar-brand" href="/">Movies</a>')
        self.assertContains(
            response,
            '<button class="btn btn-primary" disabled>Book Now</button>',
            html=True,
        )

    def test_movie_list_shows_release_date_and_duration(self):
        Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )

        response = self.client.get("/")

        self.assertContains(response, "October 22, 2021")
        self.assertContains(response, "155 minutes")

    def test_movie_list_empty_state(self):
        response = self.client.get("/")

        self.assertContains(response, "No movies are showing right now")
        self.assertNotContains(response, "Book Now")


class AuthenticationViewTests(TestCase):
    def test_anonymous_seat_page_redirects_to_login(self):
        movie = Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )

        response = self.client.get(f"/movies/{movie.id}/seats/")

        self.assertRedirects(
            response,
            f"/accounts/login/?next=/movies/{movie.id}/seats/",
        )

    def test_login_uses_base_template(self):
        response = self.client.get("/accounts/login/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")
        self.assertTemplateUsed(response, "bookings/base.html")
        self.assertContains(response, "cdn.jsdelivr.net/npm/bootstrap")
        self.assertEqual(settings.LOGIN_REDIRECT_URL, "/")


class DeploymentSettingsTests(SimpleTestCase):
    def test_settings_use_environment_and_whitenoise(self):
        environment = os.environ.copy()
        environment["SECRET_KEY"] = "deployment-test-secret"
        environment["DEBUG"] = "True"
        enabled = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "from movie_theater_booking.settings import "
                    "DEBUG, MIDDLEWARE, SECRET_KEY; "
                    "assert SECRET_KEY == 'deployment-test-secret'; "
                    "assert DEBUG is True; "
                    "assert MIDDLEWARE[1] == "
                    "'whitenoise.middleware.WhiteNoiseMiddleware'"
                ),
            ],
            env=environment,
            capture_output=True,
            text=True,
        )
        self.assertEqual(enabled.returncode, 0, enabled.stderr)

        environment.pop("DEBUG")
        disabled = subprocess.run(
            [
                sys.executable,
                "-c",
                "from movie_theater_booking.settings import DEBUG; assert DEBUG is False",
            ],
            env=environment,
            capture_output=True,
            text=True,
        )
        self.assertEqual(disabled.returncode, 0, disabled.stderr)


class SampleMovieMigrationTests(TestCase):
    def test_seed_sample_movies_is_idempotent(self):
        Movie.objects.all().delete()
        migration = importlib.import_module("bookings.migrations.0002_seed_movies")

        migration.seed_sample_movies(importlib.import_module("django.apps").apps, None)
        migration.seed_sample_movies(importlib.import_module("django.apps").apps, None)

        self.assertEqual(Movie.objects.count(), 3)
        self.assertEqual(
            set(Movie.objects.values_list("title", flat=True)),
            {"Dune", "Up", "The Matrix"},
        )
