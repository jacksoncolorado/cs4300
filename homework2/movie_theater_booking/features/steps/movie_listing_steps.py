from behave import given, then, when
from bs4 import BeautifulSoup

from bookings.models import Movie


@given('the movies "{first_title}" and "{second_title}" exist')
def create_movies(context, first_title, second_title):
    """Create the two movies used by the browsing scenario."""

    Movie.objects.all().delete()
    movie_details = {
        "Dune": {
            "description": "A noble family becomes embroiled in a war.",
            "release_date": "2021-10-22",
            "duration": 155,
        },
        "Up": {
            "description": "A widower travels to South America in his house.",
            "release_date": "2009-05-29",
            "duration": 96,
        },
    }
    context.movies = [
        Movie.objects.create(title=title, **movie_details[title])
        for title in (first_title, second_title)
    ]


@given("no movies exist")
def no_movies_exist(context):
    """Establish an empty movie catalog for the scenario."""

    Movie.objects.all().delete()


@when("I open the movie list page")
def open_movie_list(context):
    """Request the movie listing through Django's test client."""

    context.response = context.test.client.get("/")


@then('I see both movies with their descriptions and disabled "Book Now" buttons')
def see_movies_with_booking_buttons(context):
    """Check that each movie has its details and disabled booking control."""

    assert context.response.status_code == 200
    page = BeautifulSoup(context.response.content, "html.parser")
    cards = page.select("article.card")
    assert len(cards) == len(context.movies)

    for movie in context.movies:
        card = next(
            card for card in cards if movie.title in card.get_text(" ", strip=True)
        )
        card_text = card.get_text(" ", strip=True)
        assert movie.description in card_text
        button = card.find("button", string="Book Now")
        assert button is not None
        assert button.has_attr("disabled")


@then('I see "{message}" instead of a movie list')
def see_empty_movie_message(context, message):
    """Check that an empty catalog renders its user-facing explanation."""

    assert context.response.status_code == 200
    page = BeautifulSoup(context.response.content, "html.parser")
    assert message in page.get_text(" ", strip=True)
    assert not page.select("article.card")
