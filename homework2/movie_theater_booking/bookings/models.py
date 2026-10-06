from django.core.validators import MinValueValidator
from django.db import models


class Movie(models.Model):
    """A movie available for theater booking."""

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    release_date = models.DateField()
    duration = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        ordering = ["-release_date"]

    def __str__(self):
        return self.title
