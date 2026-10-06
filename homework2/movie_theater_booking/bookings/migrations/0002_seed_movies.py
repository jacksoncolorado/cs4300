from django.db import migrations


def seed_sample_movies(apps, schema_editor):
    """Create the deployment samples once, without duplicating them on re-run."""

    Movie = apps.get_model("bookings", "Movie")
    sample_movies = [
        {
            "title": "Dune",
            "description": "A noble family becomes embroiled in a war.",
            "release_date": "2021-10-22",
            "duration": 155,
        },
        {
            "title": "Up",
            "description": "A widower travels to South America in his house.",
            "release_date": "2009-05-29",
            "duration": 96,
        },
        {
            "title": "The Matrix",
            "description": "A hacker discovers the truth about his reality.",
            "release_date": "1999-03-31",
            "duration": 136,
        },
    ]

    for movie in sample_movies:
        Movie.objects.get_or_create(title=movie["title"], defaults=movie)


class Migration(migrations.Migration):
    dependencies = [
        ("bookings", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_sample_movies, migrations.RunPython.noop),
    ]
