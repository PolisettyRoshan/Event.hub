# Postman Test Guide

Base URL: `http://127.0.0.1:8000`

For POST requests, select **Body → raw → JSON**.

## 1. Create event
POST `{{base_url}}/api/events/`

```json
{
  "title": "Python Developer Conference",
  "venue": "Hyderabad Convention Centre",
  "date": "2027-03-20",
  "total_seats": 3,
  "available_seats": 3,
  "status": "upcoming"
}
```

Record the returned event `id`.

## 2. Successful reservation
POST `{{base_url}}/api/reservations/`

```json
{
  "event": 1,
  "attendee_name": "Priya Sharma",
  "attendee_email": "priya@example.com",
  "seats_reserved": 2
}
```

Replace `1` with the event ID from step 1. Expected: `201 Created`.

## 3. Overbooking failure
With only one seat left, POST a second reservation for two seats. Expected: `400 Bad Request`.

## 4. Cancel reservation
POST `{{base_url}}/api/reservations/1/cancel/`

Replace `1` with the reservation ID from step 2. No body is needed. Expected: `200 OK`.

## 5. Filtering
- GET `{{base_url}}/api/events/?status=upcoming`
- GET `{{base_url}}/api/events/?venue=Hyderabad`
- GET `{{base_url}}/api/reservations/?event_id=1`

Create a Postman environment variable named `base_url` with value `http://127.0.0.1:8000`, or replace `{{base_url}}` with the full URL.
