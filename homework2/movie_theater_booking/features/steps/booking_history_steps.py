from datetime import date, timedelta

from behave import given, then, when
from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.utils.formats import date_format

from bookings.models import Booking, Movie, Seat


def _movie(title):
    movie, _ = Movie.objects.get_or_create(
        title=title,
        defaults={
            "description": f"Description for {title}.",
            "release_date": "2021-10-22",
            "duration": 120,
        },
    )
    return movie


def _seat(seat_number):
    seat, _ = Seat.objects.get_or_create(seat_number=seat_number)
    return seat


@given('"{username}" has booked seat "{seat_number}" for "{title}"')
def create_booking(context, username, seat_number, title):
    """Create one reservation owned by the named moviegoer."""

    user, _ = get_user_model().objects.get_or_create(username=username)
    Booking.objects.create(
        user=user,
        movie=_movie(title),
        seat=_seat(seat_number),
    )


@when("I open My Bookings")
def open_booking_history(context):
    """Request the signed-in moviegoer's history page."""

    context.response = context.test.client.get("/bookings/")


@then('I see booking "{title}" with seat "{seat_number}" and today\'s formatted date')
def see_booking_details(context, title, seat_number):
    """Verify all user-visible fields for one booking."""

    page_text = BeautifulSoup(context.response.content, "html.parser").get_text(
        " ", strip=True
    )
    assert title in page_text
    assert seat_number in page_text
    assert date_format(date.today(), "F j, Y") in page_text


@then('I see the booking for "{title}"')
def see_own_booking(context, title):
    """Verify an owned booking is visible."""

    page = BeautifulSoup(context.response.content, "html.parser")
    assert page.find("h2", string=title) is not None


@then('I do not see the booking for "{title}"')
def do_not_see_other_booking(context, title):
    """Verify another moviegoer's booking is absent."""

    page = BeautifulSoup(context.response.content, "html.parser")
    assert page.find("h2", string=title) is None


@given('"{username}" has bookings on different and matching dates')
def create_ordered_booking_examples(context, username):
    """Create an older booking and two same-day bookings for ordering."""

    user = get_user_model().objects.get(username=username)
    oldest_booking = Booking.objects.create(
        user=user,
        movie=_movie("Dune"),
        seat=_seat("A1"),
    )
    same_day_lower_id = Booking.objects.create(
        user=user,
        movie=_movie("Up"),
        seat=_seat("A2"),
    )
    same_day_higher_id = Booking.objects.create(
        user=user,
        movie=_movie("Dune: Part Two"),
        seat=_seat("A3"),
    )
    Booking.objects.filter(pk=oldest_booking.pk).update(
        booking_date=date.today() - timedelta(days=1)
    )
    context.expected_booking_titles = [
        same_day_higher_id.movie.title,
        same_day_lower_id.movie.title,
        oldest_booking.movie.title,
    ]


@then("the bookings are shown by newest date and highest id first")
def bookings_are_ordered(context):
    """Verify rendered booking cards follow the model's deterministic order."""

    page = BeautifulSoup(context.response.content, "html.parser")
    actual_titles = [
        heading.get_text(strip=True) for heading in page.select("article h2")
    ]
    assert actual_titles == context.expected_booking_titles
