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
