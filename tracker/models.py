import os
from django.dispatch import receiver

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class StreamingService(models.Model):
    """
    Represents a streaming platform a movie may be available on.
    Examples: Netflix, Disney+, Prime Video, Physical Media, etc.
    """

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=200)
    year = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField(blank=True)

    runtime_minutes = models.PositiveSmallIntegerField(blank=True, null=True)

    starring = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated list of main actors",
    )
    director = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated if multiple",
    )
    writer = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated if multiple",
    )

    recommended_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recommended_movies",
        help_text="User who recommended this movie",
    )

    categories = models.ManyToManyField(Category, related_name="movies", blank=True)
    streaming_services = models.ManyToManyField(
        StreamingService, related_name="movies", blank=True
    )

    poster = models.ImageField(
        upload_to="posters/",
        blank=True,
        null=True,
        help_text="Upload a movie poster image"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = Movie.objects.get(pk=self.pk)
            if old_instance.poster and old_instance.poster != self.poster:
                old_instance.poster.delete(save=False)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

@receiver(models.signals.post_delete, sender=Movie)
def auto_delete_movie_poster_on_delete(sender, instance, **kwargs):
    if instance.poster:
        if os.path.isfile(instance.poster.path):
            os.remove(instance.poster.path)

class Viewing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    watched_on = models.DateField(blank=True, null=True)
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="Rating from 0–5 (half-star increments allowed)",
    )
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "movie")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} watched {self.movie}"
