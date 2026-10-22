from django.db import transaction
from rest_framework import serializers

from .models import Event, Reservation


class EventSerializer(serializers.ModelSerializer):
    reservations_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id", "title", "venue", "date", "total_seats",
            "available_seats", "status", "created_at", "reservations_count",
        ]
        read_only_fields = ["id", "created_at", "reservations_count"]

    def validate(self, data):
        total_seats = data.get(
            "total_seats",
            self.instance.total_seats if self.instance else None,
        )
        available_seats = data.get(
            "available_seats",
            self.instance.available_seats if self.instance else None,
        )
        if (
            total_seats is not None
            and available_seats is not None
            and available_seats > total_seats
        ):
            raise serializers.ValidationError({
                "available_seats": "available_seats cannot exceed total_seats."
            })
        return data

    def get_reservations_count(self, obj):
        return obj.reservations.filter(status="confirmed").count()


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = [
            "id", "event", "attendee_name", "attendee_email",
            "seats_reserved", "status", "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]

    def validate_seats_reserved(self, value):
        if value < 1:
            raise serializers.ValidationError("Must reserve at least 1 seat.")
        return value

    def validate(self, data):
        if self.instance is not None:
            raise serializers.ValidationError(
                "Reservations cannot be edited. Cancel this reservation "
                "and create a new one instead."
            )

        event = data.get("event")
        seats = data.get("seats_reserved", 0)
        if event is not None:
            if event.status not in ("upcoming", "ongoing"):
                raise serializers.ValidationError(
                    f"Cannot reserve seats for a {event.status} event."
                )
            if seats > event.available_seats:
                raise serializers.ValidationError(
                    f"Only {event.available_seats} seat(s) available."
                )
        return data

    @transaction.atomic
    def create(self, validated_data):
        event_id = validated_data["event"].pk
        seats = validated_data["seats_reserved"]

        # Row-level locking is effective on databases such as PostgreSQL.
        # The availability check is repeated here to avoid relying only on
        # the earlier serializer validation.
        event = Event.objects.select_for_update().get(pk=event_id)

        if event.status not in ("upcoming", "ongoing"):
            raise serializers.ValidationError(
                f"Cannot reserve seats for a {event.status} event."
            )
        if seats > event.available_seats:
            raise serializers.ValidationError(
                f"Only {event.available_seats} seat(s) available."
            )

        event.available_seats -= seats
        event.save(update_fields=["available_seats"])

        validated_data["event"] = event
        return Reservation.objects.create(**validated_data)
