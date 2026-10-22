from django.contrib import admin

from .models import Event, Reservation


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "id", "title", "venue", "date", "total_seats",
        "available_seats", "status",
    )
    list_filter = ("status", "date")
    search_fields = ("title", "venue")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "id", "attendee_name", "attendee_email", "event",
        "seats_reserved", "status", "created_at",
    )
    list_filter = ("status",)
    search_fields = ("attendee_name", "attendee_email")
