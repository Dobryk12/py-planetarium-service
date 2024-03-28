from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import (
    PlanetariumDome,
    Ticket,
    ShowSession,
    ShowTheme,
    Reservation,
    AstronomyShow,
)


class PlanetariumDomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanetariumDome
        fields = ["id", "name", "seats_in_row", "rows", "capacity"]


class ShowSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowSession
        fields = [
            "id",
            "show_time",
            "astronomy_show",
            "planetarium_dome",
        ]


class ShowThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowTheme
        fields = ["id", "name"]


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            data["show_session"].planetarium_dome,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = [
            "id",
            "row",
            "seat",
            "show_session",
        ]


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Reservation
        fields = [
            "id",
            "tickets",
            "created_at",
        ]

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            reservation = Reservation.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)
            return reservation


class ReservationListSerializer(ReservationSerializer):
    tickets = TicketSerializer(many=True, read_only=True)


class AstronomyShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = AstronomyShow
        fields = [
            "id",
            "title",
            "description",
            "show_theme",
        ]


class AstronomyShowListSerializer(AstronomyShowSerializer):
    show_theme = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )

    class Meta:
        model = AstronomyShow
        fields = [
            "id",
            "title",
            "description",
            "show_theme",
            "image"
        ]


class AstronomyShowDetailsSerializer(AstronomyShowSerializer):
    show_theme = serializers.SlugRelatedField(
        many=False, read_only=True,
    )

    class Meta:
        model = AstronomyShow
        fields = [
            "id",
            "title",
            "description",
            "show_theme",
            "image"
        ]


class AstronomyShowImageSerializer(AstronomyShowSerializer):

    class Meta:
        model = AstronomyShow
        fields = [
            "id",
            "image"
        ]


class ShowSessionListSerializer(ShowSessionSerializer):
    astronomy_show = serializers.CharField(
        source="astronomy_show.title",
        read_only=True
    )
    planetarium_dome_name = serializers.CharField(
        source="planetarium_dome.name",
        read_only=True
    )
    astronomy_show_image = serializers.CharField(
        source="astronomy_show.image",
        read_only=True
    )
    planetarium_dome_capacity = serializers.CharField(
        source="planetarium_dome.capacity",
        read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = ShowSession
        fields = [
            "id",
            "astronomy_show",
            "astronomy_show_image",
            "planetarium_dome_name",
            "planetarium_dome_capacity",
            "tickets_available",
            ]


class TicketListSerializer(TicketSerializer):
    show_session = ShowSessionListSerializer(many=False, read_only=True)


class TicketSeatsSerializer(TicketSerializer):

    class Meta:
        model = Ticket
        fields = [
            "row",
            "seat",
        ]


class ShowSessionDetailSerializer(ShowSessionSerializer):
    astronomy_show = AstronomyShowSerializer(many=False, read_only=True)
    planetarium_dome = PlanetariumDomeSerializer(many=False, read_only=True)
    taken_places = TicketSeatsSerializer(
        source="tickets", many=True, read_only=True
    )

    class Meta:
        model = ShowSession
        fields = [
            "id",
            "show_time",
            "astronomy_show",
            "planetarium_dome",
            "taken_places",
        ]

