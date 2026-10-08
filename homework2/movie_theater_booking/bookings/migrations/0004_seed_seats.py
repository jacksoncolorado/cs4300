from django.db import migrations


def seed_seats(apps, schema_editor):
    """Create the five sample seats without duplicating existing rows."""

    Seat = apps.get_model("bookings", "Seat")
    for seat_number in ("A1", "A2", "A3", "A4", "A5"):
        Seat.objects.get_or_create(seat_number=seat_number)


class Migration(migrations.Migration):
    dependencies = [
        ("bookings", "0003_seat"),
    ]

    operations = [
        migrations.RunPython(seed_seats, migrations.RunPython.noop),
    ]
