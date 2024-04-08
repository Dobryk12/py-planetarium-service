from django.urls import path, include
from rest_framework import routers

from planetarium.views import (
    PlanetariumDomeViewSet,
    ReservationViewSet,
    ShowThemeViewSet,
    ShowSessionViewSet,
    AstronomyShowViewSet,
)

router = routers.DefaultRouter()
router.register("planetarium_dome", PlanetariumDomeViewSet)
router.register("reservations", ReservationViewSet)
router.register("show_themes", ShowThemeViewSet)
router.register("show_session", ShowSessionViewSet)
router.register("astronomy_shows", AstronomyShowViewSet)


urlpatterns = [path("", include(router.urls))]

app_name = "planetarium"
