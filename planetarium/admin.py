from django.contrib import admin

from .models import (
    ShowSession,
    Ticket,
    Reservation,
    AstronomyShow,
    PlanetariumDome,
    ShowTheme,
)
admin.site.register(ShowSession)
admin.site.register(Ticket)
admin.site.register(Reservation)
admin.site.register(AstronomyShow)
admin.site.register(PlanetariumDome)
admin.site.register(ShowTheme)
