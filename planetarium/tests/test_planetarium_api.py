from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from planetarium.models import (
    PlanetariumDome,
    ShowSession,
    Reservation,
    Ticket
)
from planetarium.serializers import (
    ShowSessionSerializer,
    PlanetariumDomeSerializer,
    TicketSerializer
)
from user.models import User


class PlanetariumDomeTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_planetarium_dome(self):
        """Test creating a new planetarium dome"""
        payload = {
            "name": "Test Dome",
            "rows": 10,
            "seats_in_row": 15
        }
        response = self.client.post(reverse("planetarium:planetariumdome-list"), payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PlanetariumDome.objects.count(), 1)
        self.assertEqual(PlanetariumDome.objects.get().name, "Test Dome")


class ShowSessionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_show_session(self):
        """Test creating a new show session"""
        dome = PlanetariumDome.objects.create(name="Test Dome", rows=10, seats_in_row=15)
        payload = {
            "astronomy_show": 1,  # Assuming you have existing astronomy show with id=1
            "planetarium_dome": dome.id,
            "show_time": "2024-03-30T10:00:00Z"
        }
        response = self.client.post(reverse("planetarium:showsession-list"), payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ShowSession.objects.count(), 1)
        self.assertEqual(ShowSession.objects.get().astronomy_show, 1)


class ReservationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_reservation(self):
        """Test creating a new reservation"""
        user = User.objects.create_user(username="testuser", password="password123")
        payload = {
            "created_at": "2024-03-30T12:00:00Z",
            "user": user.id
        }
        response = self.client.post(reverse("planetarium:reservation-list"), payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reservation.objects.count(), 1)


class TicketTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_ticket(self):
        """Test creating a new ticket"""
        session = ShowSession.objects.create(
            astronomy_show_id=1,
            planetarium_dome_id=1,
            show_time="2024-03-30T10:00:00Z")
        reservation = Reservation.objects.create(created_at="2024-03-30T12:00:00Z", user_id=1)
        payload = {
            "row": 5,
            "seat": 10,
            "show_session": session.id,
            "reservation": reservation.id
        }
        response = self.client.post(reverse("planetarium:ticket-list"), payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ticket.objects.count(), 1)


class PlanetariumDomeSerializerTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_planetarium_dome_serializer(self):
        """Test PlanetariumDome serializer"""
        dome = PlanetariumDome.objects.create(name="Test Dome", rows=10, seats_in_row=15)
        serializer = PlanetariumDomeSerializer(dome)
        expected_data = {
            "id": dome.id,
            "name": "Test Dome",
            "seats_in_row": 15,
            "rows": 10,
            "capacity": 150  # Expected capacity calculation: 10 * 15 = 150
        }
        self.assertEqual(serializer.data, expected_data)


class ShowSessionSerializerTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_show_session_serializer(self):
        """Test ShowSession serializer"""
        dome = PlanetariumDome.objects.create(name="Test Dome", rows=10, seats_in_row=15)
        session = ShowSession.objects.create(
            astronomy_show_id=1, planetarium_dome_id=dome.id, show_time="2024-03-30T10:00:00Z"
        )
        serializer = ShowSessionSerializer(session)
        expected_data = {
            "id": session.id,
            "show_time": "2024-03-30T10:00:00Z",
            "astronomy_show": 1,  # Assuming you have existing astronomy show with id=1
            "planetarium_dome": dome.id
        }
        self.assertEqual(serializer.data, expected_data)


class TicketSerializerTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_ticket_serializer_validation(self):
        """Test Ticket serializer validation"""
        dome = PlanetariumDome.objects.create(name="Test Dome", rows=10, seats_in_row=15)
        session = ShowSession.objects.create(
            astronomy_show_id=1, planetarium_dome_id=dome.id, show_time="2024-03-30T10:00:00Z"
        )
        reservation = Reservation.objects.create(created_at="2024-03-30T12:00:00Z", user_id=1)
        # Create a ticket with invalid row and seat values
        ticket_data = {
            "row": 20,  # Invalid row value, should raise ValidationError
            "seat": 50,  # Invalid seat value, should raise ValidationError
            "show_session": session.id,
            "reservation": reservation.id
        }
        serializer = TicketSerializer(data=ticket_data)
        self.assertFalse(serializer.is_valid())
