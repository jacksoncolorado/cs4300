from datetime import date

from behave import given, then, when
from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model

from bookings.models import Booking, Movie, Seat


@given('I am signed in as "{username}"')
def sign_in(context, username):
    """Authenticate the moviegoer through Django's test client."""

    context.user = get_user_model().objects.create_user(username=username)
    context.test.client.force_login(context.user)


@given("I am not signed in")
def sign_out(context):
    """Ensure the seat page request has no authenticated session."""

    context.test.client.logout()


@given('the movie "{title}" has seats "{first_seat}" and "{second_seat}"')
def create_movie_with_seats(context, title, first_seat, second_seat):
    """Create a movie and the two physical seats used by the scenario."""

    Booking.objects.all().delete()
    Movie.objects.all().delete()
    Seat.objects.all().delete()
    context.movie = Movie.objects.create(
        title=title,
        description="A noble family becomes embroiled in a war.",
        release_date="2021-10-22",
        duration=155,
    )
    for seat_number in (first_seat, second_seat):
        Seat.objects.create(seat_number=seat_number)


@given('seat "{seat_number}" is booked for "{title}"')
def create_existing_booking(context, seat_number, title):
    """Make one seat unavailable for the selected movie."""

    Booking.objects.create(
        movie=Movie.objects.get(title=title),
        seat=Seat.objects.get(seat_number=seat_number),
        user=context.user,
    )


@given('seat "{seat_number}" is out of service')
def mark_seat_out_of_service(context, seat_number):
    """Mark a physical seat unavailable for every movie."""

    seat = Seat.objects.get(seat_number=seat_number)
    seat.booking_status = True
    seat.save(update_fields=["booking_status"])


@given('the movie "{title}" has available seat "{seat_number}"')
def create_movie_with_available_seat(context, title, seat_number):
    """Create a movie with one seat that has no booking."""

    create_movie_with_seats(context, title, seat_number, "A2")


@when('I open the seat page for "{title}"')
def open_seat_page(context, title):
    """Open the selected movie's authenticated seat page."""

    movie = Movie.objects.get(title=title)
    context.response = context.test.client.get(f"/movies/{movie.id}/seats/")


@when('I book seat "{seat_number}" for "{title}"')
def book_available_seat(context, seat_number, title):
    """Submit the seat page form and follow its success redirect."""

    movie = Movie.objects.get(title=title)
    seat = Seat.objects.get(seat_number=seat_number)
    context.response = context.test.client.post(
        f"/movies/{movie.id}/seats/",
        {"seat": seat.id},
        follow=True,
    )


def _seat_card(context, seat_number):
    page = BeautifulSoup(context.response.content, "html.parser")
    return next(
        card
        for card in page.select("div.card")
        if f"Seat {seat_number}" in card.get_text(" ", strip=True)
    )


@then('seat "{seat_number}" is shown as available')
def seat_is_available(context, seat_number):
    """Verify that the page offers the seat for booking."""

    card = _seat_card(context, seat_number)
    assert "Available" in card.get_text(" ", strip=True)
    assert card.find("button", string="Book seat") is not None


@then('seat "{seat_number}" is shown as unavailable')
def seat_is_unavailable(context, seat_number):
    """Verify that the page does not offer the seat for booking."""

    card = _seat_card(context, seat_number)
    assert "Unavailable" in card.get_text(" ", strip=True)
    assert card.find("button", string="Book seat") is None


@then('seat "{seat_number}" is booked for "{title}" by "{username}" today')
def booking_has_expected_data(context, seat_number, title, username):
    """Verify ownership, relationships, and the automatic booking date."""

    booking = Booking.objects.get(
        movie__title=title,
        seat__seat_number=seat_number,
    )
    assert booking.user.username == username
    assert booking.booking_date == date.today()


@then('I see "{message}"')
def see_message(context, message):
    """Check an exact user-facing result message."""

    page = BeautifulSoup(context.response.content, "html.parser")
    assert message in page.get_text(" ", strip=True)


@then('I see a link back to the seat page for "{title}"')
def see_movie_seat_page_link(context, title):
    """Verify that an error offers the movie-specific return link."""

    movie = Movie.objects.get(title=title)
    page = BeautifulSoup(context.response.content, "html.parser")
    link = page.find("a", string="Back to seats")
    assert link is not None
    assert link["href"] == f"/movies/{movie.id}/seats/"


@then('exactly one booking exists for seat "{seat_number}" and "{title}"')
def exactly_one_booking_exists(context, seat_number, title):
    """Verify that retrying a taken seat did not create a duplicate."""

    count = Booking.objects.filter(
        movie__title=title,
        seat__seat_number=seat_number,
    ).count()
    assert count == 1


@then("I am redirected to sign in before booking")
def redirected_to_sign_in(context):
    """Verify Django preserved the requested seat page in the login redirect."""

    expected_url = f"/accounts/login/?next=/movies/{context.movie.id}/seats/"
    assert context.response.status_code == 302
    assert context.response["Location"] == expected_url


@then('no booking exists for seat "{seat_number}" and "{title}"')
def no_booking_exists(context, seat_number, title):
    """Verify a rejected seat request made no database change."""

    exists = Booking.objects.filter(
        movie__title=title,
        seat__seat_number=seat_number,
    ).exists()
    assert not exists
