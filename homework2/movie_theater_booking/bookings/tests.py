import importlib
import os
import subprocess
import sys
from datetime import date, timedelta
from unittest.mock import patch

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction
from django.test import SimpleTestCase, TestCase
from django.utils.formats import date_format
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


class BookingAPITests(APITestCase):
    def setUp(self):
        Booking.objects.all().delete()
        Movie.objects.all().delete()
        Seat.objects.all().delete()
        self.user = get_user_model().objects.create_user(username="sam")
        self.other_user = get_user_model().objects.create_user(username="alex")

    def create_booking(self, title, seat_number, user=None):
        movie = Movie.objects.create(
            title=title,
            description=f"Description for {title}.",
            release_date="2021-10-22",
            duration=120,
        )
        seat = Seat.objects.create(seat_number=seat_number)
        return Booking.objects.create(
            movie=movie,
            seat=seat,
            user=user or self.user,
        )

    def test_list_bookings_only_returns_own(self):
        own_booking = self.create_booking("Dune", "A1")
        self.create_booking("Up", "A2", user=self.other_user)
        self.client.force_authenticate(user=self.user)

        response = self.client.get("/api/bookings/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            [
                {
                    "id": own_booking.id,
                    "movie": own_booking.movie_id,
                    "seat": own_booking.seat_id,
                    "user": self.user.id,
                    "booking_date": own_booking.booking_date.isoformat(),
                }
            ],
        )

    def test_booking_api_uses_default_ordering(self):
        oldest_booking = self.create_booking("Dune", "A1")
        same_day_lower_id = self.create_booking("Up", "A2")
        same_day_higher_id = self.create_booking("Dune: Part Two", "A3")
        Booking.objects.filter(pk=oldest_booking.pk).update(
            booking_date=date.today() - timedelta(days=1)
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get("/api/bookings/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [booking["id"] for booking in response.json()],
            [same_day_higher_id.id, same_day_lower_id.id, oldest_booking.id],
        )

    def test_anonymous_booking_list_returns_403(self):
        self.create_booking("Dune", "A1")

        response = self.client.get("/api/bookings/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_retrieve_another_users_booking(self):
        other_booking = self.create_booking("Up", "A2", user=self.other_user)
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f"/api/bookings/{other_booking.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotContains(response, "Up", status_code=404)

    def test_retrieve_own_booking_returns_five_field_shape(self):
        booking = self.create_booking("Dune", "A1")
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f"/api/bookings/{booking.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "id": booking.id,
                "movie": booking.movie_id,
                "seat": booking.seat_id,
                "user": self.user.id,
                "booking_date": booking.booking_date.isoformat(),
            },
        )

    def test_booking_update_and_delete_methods_not_allowed(self):
        booking = self.create_booking("Dune", "A1")
        self.client.force_authenticate(user=self.user)

        responses = (
            self.client.put(f"/api/bookings/{booking.id}/", {}),
            self.client.patch(f"/api/bookings/{booking.id}/", {}),
            self.client.delete(f"/api/bookings/{booking.id}/"),
        )

        for response in responses:
            with self.subTest(method=response.request["REQUEST_METHOD"]):
                self.assertEqual(
                    response.status_code,
                    status.HTTP_405_METHOD_NOT_ALLOWED,
                )

    def test_create_booking_returns_five_field_shape(self):
        movie = Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )
        seat = Seat.objects.create(seat_number="A1")
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/bookings/",
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
                "user": self.user.id,
                "booking_date": date.today().isoformat(),
            },
        )

    def test_create_booking_ignores_user_in_request_data(self):
        movie = Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )
        seat = Seat.objects.create(seat_number="A1")
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/bookings/",
            {
                "movie": movie.id,
                "seat": seat.id,
                "user": self.other_user.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        booking = Booking.objects.get()
        self.assertEqual(booking.user, self.user)
        self.assertEqual(response.json()["user"], self.user.id)

    def test_anonymous_booking_create_returns_403(self):
        movie = Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )
        seat = Seat.objects.create(seat_number="A1")

        response = self.client.post(
            "/api/bookings/",
            {"movie": movie.id, "seat": seat.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Booking.objects.exists())

    def test_taken_seat_returns_matching_detail(self):
        booking = self.create_booking("Dune", "A1")
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/bookings/",
            {"movie": booking.movie_id, "seat": booking.seat_id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"detail": "Seat A1 is already booked for Dune."},
        )
        self.assertEqual(Booking.objects.count(), 1)

    def test_out_of_service_seat_returns_matching_detail(self):
        movie = Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )
        seat = Seat.objects.create(seat_number="A3", booking_status=True)
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/bookings/",
            {"movie": movie.id, "seat": seat.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"detail": "Seat A3 is out of service."},
        )
        self.assertFalse(Booking.objects.exists())

    def test_create_booking_unknown_ids_return_field_errors(self):
        movie = Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )
        seat = Seat.objects.create(seat_number="A1")
        self.client.force_authenticate(user=self.user)

        responses = (
            (
                self.client.post(
                    "/api/bookings/",
                    {"movie": 9999, "seat": seat.id},
                    format="json",
                ),
                {"movie": ['Invalid pk "9999" - object does not exist.']},
            ),
            (
                self.client.post(
                    "/api/bookings/",
                    {"movie": movie.id, "seat": 9999},
                    format="json",
                ),
                {"seat": ['Invalid pk "9999" - object does not exist.']},
            ),
        )

        for response, expected_error in responses:
            with self.subTest(field=next(iter(expected_error))):
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.json(), expected_error)
        self.assertFalse(Booking.objects.exists())

    def test_create_booking_missing_fields_return_field_errors(self):
        movie = Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )
        seat = Seat.objects.create(seat_number="A1")
        self.client.force_authenticate(user=self.user)

        responses = (
            (
                self.client.post(
                    "/api/bookings/",
                    {"seat": seat.id},
                    format="json",
                ),
                {"movie": ["This field is required."]},
            ),
            (
                self.client.post(
                    "/api/bookings/",
                    {"movie": movie.id},
                    format="json",
                ),
                {"seat": ["This field is required."]},
            ),
        )

        for response, expected_error in responses:
            with self.subTest(field=next(iter(expected_error))):
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.json(), expected_error)
        self.assertFalse(Booking.objects.exists())

    def test_seat_booked_via_seats_api_refused_via_bookings_api(self):
        movie = Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )
        seat = Seat.objects.create(seat_number="A1")
        self.client.force_authenticate(user=self.user)

        seat_api_response = self.client.post(
            "/api/seats/book/",
            {"movie": movie.id, "seat": seat.id},
            format="json",
        )
        bookings_api_response = self.client.post(
            "/api/bookings/",
            {"movie": movie.id, "seat": seat.id},
            format="json",
        )

        self.assertEqual(seat_api_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            bookings_api_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            bookings_api_response.json(),
            {"detail": "Seat A1 is already booked for Dune."},
        )
        self.assertEqual(Booking.objects.count(), 1)

    def test_seat_booked_via_page_refused_via_bookings_api(self):
        movie = Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )
        seat = Seat.objects.create(seat_number="A1")
        self.client.force_login(self.user)

        page_response = self.client.post(
            f"/movies/{movie.id}/seats/",
            {"seat": seat.id},
        )
        bookings_api_response = self.client.post(
            "/api/bookings/",
            {"movie": movie.id, "seat": seat.id},
            format="json",
        )

        self.assertRedirects(
            page_response,
            f"/movies/{movie.id}/seats/",
        )
        self.assertEqual(
            bookings_api_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            bookings_api_response.json(),
            {"detail": "Seat A1 is already booked for Dune."},
        )
        self.assertEqual(Booking.objects.count(), 1)


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

    def test_book_seat_translates_database_duplicate_to_booking_error(self):
        Booking.objects.create(
            user=self.user,
            movie=self.movie,
            seat=self.seat,
        )

        with patch("bookings.services.Booking.objects.filter") as booking_filter:
            booking_filter.return_value.exists.return_value = False
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

    def test_booking_str(self):
        booking = Booking.objects.create(
            movie=self.movie,
            seat=self.seat,
            user=self.user,
        )

        self.assertEqual(str(booking), "Dune - A1 - sam")

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

    def test_booking_default_ordering_newest_date_then_highest_id(self):
        oldest_booking = Booking.objects.create(
            movie=self.movie,
            seat=self.seat,
            user=self.user,
        )
        second_movie = Movie.objects.create(
            title="Up",
            description="A widower travels to South America in his house.",
            release_date="2009-05-29",
            duration=96,
        )
        second_seat = Seat.objects.create(seat_number="A2")
        same_day_lower_id = Booking.objects.create(
            movie=second_movie,
            seat=second_seat,
            user=self.user,
        )
        third_movie = Movie.objects.create(
            title="Dune: Part Two",
            description="Paul Atreides unites with Chani and the Fremen.",
            release_date="2024-03-01",
            duration=166,
        )
        third_seat = Seat.objects.create(seat_number="A3")
        same_day_higher_id = Booking.objects.create(
            movie=third_movie,
            seat=third_seat,
            user=self.user,
        )
        Booking.objects.filter(pk=oldest_booking.pk).update(
            booking_date=date.today() - timedelta(days=1)
        )

        self.assertEqual(
            list(Booking.objects.all()),
            [same_day_higher_id, same_day_lower_id, oldest_booking],
        )


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

    def test_create_movie_negative_duration_400(self):
        movie_data = {
            "title": "Up",
            "description": "A widower travels to South America in his house.",
            "release_date": "2009-05-29",
            "duration": -1,
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
        self.assertContains(response, "Book Now")

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

    def test_movie_list_book_now_links_to_seat_page(self):
        movie = Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )

        response = self.client.get("/")

        self.assertContains(
            response,
            f'<a class="btn btn-primary" href="/movies/{movie.id}/seats/">'
            "Book Now</a>",
            html=True,
        )


class SeatBookingViewTests(TestCase):
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
        self.user = get_user_model().objects.create_user(username="sam")
        self.client.force_login(self.user)

    def test_seat_page_shows_per_movie_availability(self):
        available_seat = Seat.objects.create(seat_number="A1")
        booked_seat = Seat.objects.create(seat_number="A2")
        Booking.objects.create(
            movie=self.movie,
            seat=booked_seat,
            user=self.user,
        )

        response = self.client.get(f"/movies/{self.movie.id}/seats/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dune")
        availability = {
            option["seat"].seat_number: option["available"]
            for option in response.context["seat_options"]
        }
        self.assertEqual(
            availability,
            {available_seat.seat_number: True, booked_seat.seat_number: False},
        )
        self.assertContains(response, "Available")
        self.assertContains(response, "Unavailable")

    def test_seat_booking_uses_base_template(self):
        Seat.objects.create(seat_number="A1")

        response = self.client.get(f"/movies/{self.movie.id}/seats/")

        self.assertTemplateUsed(response, "bookings/seat_booking.html")
        self.assertTemplateUsed(response, "bookings/base.html")
        self.assertContains(response, "cdn.jsdelivr.net/npm/bootstrap")

    def test_missing_movie_page_404(self):
        response = self.client.get("/movies/9999/seats/")

        self.assertEqual(response.status_code, 404)

    def test_book_available_seat_from_page(self):
        seat = Seat.objects.create(seat_number="A1")

        response = self.client.post(
            f"/movies/{self.movie.id}/seats/",
            {"seat": seat.id},
            follow=True,
        )

        self.assertRedirects(
            response,
            f"/movies/{self.movie.id}/seats/",
        )
        booking = Booking.objects.get()
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.movie, self.movie)
        self.assertEqual(booking.seat, seat)
        self.assertEqual(booking.booking_date, date.today())
        self.assertContains(response, "Seat A1 booked for Dune.")
        availability = {
            option["seat"].seat_number: option["available"]
            for option in response.context["seat_options"]
        }
        self.assertFalse(availability[seat.seat_number])

    def test_taken_seat_page_shows_exact_error_and_back_link(self):
        seat = Seat.objects.create(seat_number="A2")
        Booking.objects.create(movie=self.movie, seat=seat, user=self.user)

        response = self.client.post(
            f"/movies/{self.movie.id}/seats/",
            {"seat": seat.id},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Seat A2 is already booked for Dune.")
        self.assertContains(
            response,
            f'<a href="/movies/{self.movie.id}/seats/">Back to seats</a>',
            html=True,
        )
        self.assertEqual(Booking.objects.count(), 1)

    def test_out_of_service_seat_unavailable_for_every_movie(self):
        other_movie = Movie.objects.create(
            title="Up",
            description="A widower travels to South America in his house.",
            release_date="2009-05-29",
            duration=96,
        )
        seat = Seat.objects.create(seat_number="A3", booking_status=True)

        responses = (
            self.client.get(f"/movies/{self.movie.id}/seats/"),
            self.client.get(f"/movies/{other_movie.id}/seats/"),
        )

        for response in responses:
            with self.subTest(movie=response.context["movie"].title):
                availability = {
                    option["seat"].seat_number: option["available"]
                    for option in response.context["seat_options"]
                }
                self.assertFalse(availability[seat.seat_number])
        self.assertFalse(Booking.objects.exists())

    def test_seat_booked_via_page_refused_via_seats_api(self):
        seat = Seat.objects.create(seat_number="A1")

        page_response = self.client.post(
            f"/movies/{self.movie.id}/seats/",
            {"seat": seat.id},
        )
        api_response = self.client.post(
            "/api/seats/book/",
            {"movie": self.movie.id, "seat": seat.id},
        )

        self.assertRedirects(
            page_response,
            f"/movies/{self.movie.id}/seats/",
        )
        self.assertEqual(api_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            api_response.json(),
            {"detail": "Seat A1 is already booked for Dune."},
        )
        self.assertEqual(Booking.objects.count(), 1)

    def test_seat_booked_via_seats_api_refused_via_page(self):
        seat = Seat.objects.create(seat_number="A1")

        api_response = self.client.post(
            "/api/seats/book/",
            {"movie": self.movie.id, "seat": seat.id},
        )
        page_response = self.client.post(
            f"/movies/{self.movie.id}/seats/",
            {"seat": seat.id},
        )

        self.assertEqual(api_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(page_response.status_code, 200)
        self.assertContains(
            page_response,
            "Seat A1 is already booked for Dune.",
        )
        self.assertEqual(Booking.objects.count(), 1)


class BookingHistoryViewTests(TestCase):
    def setUp(self):
        Booking.objects.all().delete()
        Movie.objects.all().delete()
        Seat.objects.all().delete()
        self.user = get_user_model().objects.create_user(username="sam")
        self.movie = Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )
        self.seat = Seat.objects.create(seat_number="A1")

    def test_booking_history_shows_movie_seat_and_formatted_date(self):
        booking = Booking.objects.create(
            movie=self.movie,
            seat=self.seat,
            user=self.user,
        )
        self.client.force_login(self.user)

        response = self.client.get("/bookings/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dune")
        self.assertContains(response, "A1")
        self.assertContains(
            response,
            date_format(booking.booking_date, "F j, Y"),
        )

    def test_booking_history_uses_base_template(self):
        self.client.force_login(self.user)

        response = self.client.get("/bookings/")

        self.assertTemplateUsed(response, "bookings/booking_history.html")
        self.assertTemplateUsed(response, "bookings/base.html")
        self.assertContains(response, "cdn.jsdelivr.net/npm/bootstrap")

    def test_navbar_shows_my_bookings_only_when_authenticated(self):
        anonymous_response = self.client.get("/")

        self.assertNotContains(anonymous_response, "My Bookings")
        self.client.force_login(self.user)

        authenticated_response = self.client.get("/")

        self.assertContains(
            authenticated_response,
            '<a class="nav-link" href="/bookings/">My Bookings</a>',
            html=True,
        )

    def test_navbar_shows_sign_out_when_authenticated(self):
        self.client.force_login(self.user)

        authenticated_response = self.client.get("/")

        self.assertContains(
            authenticated_response,
            '<form method="post" action="/accounts/logout/">',
        )
        self.assertContains(authenticated_response, "Sign out")
        self.assertNotContains(authenticated_response, "Sign in")

        self.client.logout()
        anonymous_response = self.client.get("/")

        self.assertContains(
            anonymous_response,
            '<a class="nav-link" href="/accounts/login/">Sign in</a>',
            html=True,
        )
        self.assertNotContains(anonymous_response, "Sign out")

    def test_sign_out_returns_to_movie_list(self):
        self.client.force_login(self.user)

        response = self.client.post("/accounts/logout/", follow=True)

        self.assertRedirects(response, "/")
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, "Sign in")

    def test_anonymous_booking_history_redirects_to_login(self):
        response = self.client.get("/bookings/")

        self.assertRedirects(
            response,
            "/accounts/login/?next=/bookings/",
        )

    def test_booking_history_page_only_shows_own(self):
        own_booking = Booking.objects.create(
            movie=self.movie,
            seat=self.seat,
            user=self.user,
        )
        other_user = get_user_model().objects.create_user(username="alex")
        other_movie = Movie.objects.create(
            title="Up",
            description="A widower travels to South America in his house.",
            release_date="2009-05-29",
            duration=96,
        )
        other_seat = Seat.objects.create(seat_number="A2")
        Booking.objects.create(
            movie=other_movie,
            seat=other_seat,
            user=other_user,
        )
        self.client.force_login(self.user)

        response = self.client.get("/bookings/")

        self.assertContains(response, own_booking.movie.title)
        self.assertNotContains(response, other_movie.title)
        self.assertEqual(list(response.context["bookings"]), [own_booking])

    def test_booking_history_empty_state(self):
        self.client.force_login(self.user)

        response = self.client.get("/bookings/")

        self.assertContains(response, "You have no bookings yet.")
        self.assertNotContains(response, '<article class="list-group-item">')

    def test_booking_history_page_uses_default_ordering(self):
        oldest_booking = Booking.objects.create(
            movie=self.movie,
            seat=self.seat,
            user=self.user,
        )
        second_movie = Movie.objects.create(
            title="Up",
            description="A widower travels to South America in his house.",
            release_date="2009-05-29",
            duration=96,
        )
        second_seat = Seat.objects.create(seat_number="A2")
        same_day_lower_id = Booking.objects.create(
            movie=second_movie,
            seat=second_seat,
            user=self.user,
        )
        third_movie = Movie.objects.create(
            title="Dune: Part Two",
            description="Paul Atreides unites with Chani and the Fremen.",
            release_date="2024-03-01",
            duration=166,
        )
        third_seat = Seat.objects.create(seat_number="A3")
        same_day_higher_id = Booking.objects.create(
            movie=third_movie,
            seat=third_seat,
            user=self.user,
        )
        Booking.objects.filter(pk=oldest_booking.pk).update(
            booking_date=date.today() - timedelta(days=1)
        )
        self.client.force_login(self.user)

        response = self.client.get("/bookings/")

        self.assertEqual(
            list(response.context["bookings"]),
            [same_day_higher_id, same_day_lower_id, oldest_booking],
        )


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

    def test_successful_login_redirects_to_movie_list(self):
        get_user_model().objects.create_user(
            username="sam",
            password="test-password",
        )

        response = self.client.post(
            "/accounts/login/",
            {"username": "sam", "password": "test-password"},
        )

        self.assertRedirects(response, "/")


class AdminRegistrationTests(SimpleTestCase):
    def test_booking_models_are_registered(self):
        self.assertIn(Movie, admin.site._registry)
        self.assertIn(Seat, admin.site._registry)
        self.assertIn(Booking, admin.site._registry)


class DemoUserCommandTests(TestCase):
    def test_seed_demo_user_requires_password(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesMessage(
                CommandError,
                "DEMO_PASSWORD environment variable is required.",
            ):
                call_command("seed_demo_user")

    def test_seed_demo_user_is_idempotent_and_updates_password(self):
        with patch.dict(os.environ, {"DEMO_PASSWORD": "first-password"}):
            call_command("seed_demo_user")

        demo_user = get_user_model().objects.get(username="demo")
        self.assertTrue(demo_user.check_password("first-password"))

        with patch.dict(os.environ, {"DEMO_PASSWORD": "updated-password"}):
            call_command("seed_demo_user")

        self.assertEqual(
            get_user_model().objects.filter(username="demo").count(),
            1,
        )
        demo_user.refresh_from_db()
        self.assertTrue(demo_user.check_password("updated-password"))


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
