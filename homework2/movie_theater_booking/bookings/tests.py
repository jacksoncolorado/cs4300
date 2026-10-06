from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Movie


class MovieModelTests(TestCase):
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
