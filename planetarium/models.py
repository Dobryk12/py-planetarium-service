import os
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    @property
    def capacity(self):
        return self.seats_in_row * self.rows

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        app_label = "planetarium"


class ShowTheme(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        app_label = "planetarium"


def astronomy_show_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"


class AstronomyShow(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    show_theme = models.ManyToManyField(ShowTheme, blank=True, related_name="astronomy_shows")
    image = models.ImageField(null=True, upload_to=astronomy_show_image_file_path)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]
        app_label = "planetarium"


class ShowSession(models.Model):
    astronomy_show = models.ForeignKey(
        AstronomyShow,
        on_delete=models.CASCADE
    )
    planetarium_dome = models.ForeignKey(
        PlanetariumDome,
        on_delete=models.CASCADE
    )
    show_time = models.DateTimeField()

    def __str__(self):
        return self.astronomy_show.title + " " + str(self.show_time)

    class Meta:
        ordering = ["-show_time"]
        app_label = "planetarium"


class Reservation(models.Model):
    created_at = models.DateTimeField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return str({self.created_at})

    class Meta:
        ordering = ["-created_at"]
        app_label = "planetarium"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    show_session = models.ForeignKey(
        ShowSession,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    @staticmethod
    def validate_ticket(row, seat, planetarium_dome, error_message):
        for ticket_attr_value, ticket_attr_name,planetarium_dome_name in [
        (row, "row", "rows"),
        (seat, "seat", "seats"),

        ]:
            count_attrs = getattr(planetarium_dome, planetarium_dome_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_message(
                    f"{ticket_attr_name} must be between 1 and {count_attrs}"
                )

    def clean(self):
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.show_session.planetarium_dome,
            ValidationError,
        )

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return (
            f"{str(self.show_session)} (row: {self.row}, seat: {self.seat})"
        )
