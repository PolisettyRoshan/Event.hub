from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Event, Reservation
from .serializers import EventSerializer, ReservationSerializer


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = Event.objects.all()
        status_param = self.request.query_params.get("status")
        venue_param = self.request.query_params.get("venue")

        if status_param:
            queryset = queryset.filter(status=status_param)
        if venue_param:
            queryset = queryset.filter(venue__icontains=venue_param)
        return queryset


class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer

    def get_queryset(self):
        queryset = Reservation.objects.select_related("event").all()
        event_id = self.request.query_params.get("event_id")
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        return queryset

    def update(self, request, *args, **kwargs):
        return Response(
            {"error": "Reservations cannot be edited. Cancel and create a new reservation."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def partial_update(self, request, *args, **kwargs):
        return Response(
            {"error": "Reservations cannot be edited. Cancel and create a new reservation."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def destroy(self, request, *args, **kwargs):
        # Prevent deleting a confirmed reservation without restoring its seats.
        with transaction.atomic():
            reservation = get_object_or_404(
                Reservation.objects.select_for_update(), pk=kwargs["pk"]
            )
            if reservation.status == "confirmed":
                event = Event.objects.select_for_update().get(
                    pk=reservation.event_id
                )
                event.available_seats += reservation.seats_reserved
                event.save(update_fields=["available_seats"])
            reservation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        with transaction.atomic():
            reservation = get_object_or_404(
                Reservation.objects.select_for_update(), pk=pk
            )
            if reservation.status == "cancelled":
                return Response(
                    {"error": "Already cancelled."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            event = Event.objects.select_for_update().get(
                pk=reservation.event_id
            )
            event.available_seats += reservation.seats_reserved
            event.save(update_fields=["available_seats"])

            reservation.status = "cancelled"
            reservation.save(update_fields=["status"])

        reservation.refresh_from_db()
        return Response(
            self.get_serializer(reservation).data,
            status=status.HTTP_200_OK,
        )
