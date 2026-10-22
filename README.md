# EventHub - Event Ticketing API

EventHub is a Django REST Framework backend for a simplified event ticketing platform. It supports event browsing, seat reservations, cancellation, filtering, and request logging.

## Features
- Create, list, retrieve, update, and delete events.
- Filter events by status and venue.
- Create reservations with seat availability validation.
- Deduct seats when a reservation is confirmed.
- Cancel reservations and restore seats.
- Filter reservations by event ID.
- Show confirmed reservation counts on event responses.
- Log request method, path, response status, and duration.

## Technology
Python, Django, Django REST Framework, SQLite, Postman, Git/GitHub.

## Run on Windows
1. Extract the ZIP and open the `EventHub_Project` folder in VS Code.
2. Open Terminal in VS Code.
3. Create and activate a virtual environment:

   ```powershell
   python -m venv venv
   .\\venv\\Scripts\\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt and run `venv\\Scripts\\activate`.

4. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

5. Apply migrations:

   ```bash
   python manage.py migrate
   ```

6. Check the project:

   ```bash
   python manage.py check
   ```

7. Start the server:

   ```bash
   python manage.py runserver
   ```

Open http://127.0.0.1:8000/api/ to view the browsable API.

## Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/events/` | List events |
| POST | `/api/events/` | Create event |
| GET | `/api/events/{id}/` | Retrieve event |
| PUT/PATCH | `/api/events/{id}/` | Update event |
| DELETE | `/api/events/{id}/` | Delete event |
| GET | `/api/reservations/` | List reservations |
| POST | `/api/reservations/` | Create reservation |
| GET | `/api/reservations/{id}/` | Retrieve reservation |
| POST | `/api/reservations/{id}/cancel/` | Cancel reservation and restore seats |
| DELETE | `/api/reservations/{id}/` | Delete reservation and restore seats if confirmed |

### Filters
- `/api/events/?status=upcoming`
- `/api/events/?venue=Hyderabad`
- `/api/events/?status=upcoming&venue=Hyderabad`
- `/api/reservations/?event_id=1`

## Example: Create an event
POST `/api/events/`, Body → raw → JSON:

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

## Example: Reserve seats
POST `/api/reservations/`:

```json
{
  "event": 1,
  "attendee_name": "Priya Sharma",
  "attendee_email": "priya@example.com",
  "seats_reserved": 2
}
```

Use the actual event ID returned by your create-event request. A successful reservation returns HTTP `201 Created`.

## Test overbooking
If only one seat remains, submit a reservation for two seats. Expected response: HTTP `400 Bad Request` with an error indicating only one seat is available.

## Cancel a reservation
POST `/api/reservations/1/cancel/` with no body. Expected response: HTTP `200 OK` and status `cancelled`. Available seats are restored. Repeating cancellation returns HTTP `400 Bad Request`.

## Design decision
Reservation creation and cancellation use database transactions so the reservation change and seat-count change are committed together or rolled back together. `select_for_update()` requests row-level locking on databases that support it. SQLite is used for easy local setup; for stronger concurrent booking protection, configure PostgreSQL and test concurrent requests.

## Submission screenshots
Save genuine Postman screenshots showing:
1. Successful reservation (`201 Created`).
2. Overbooking failure (`400 Bad Request`).
3. Successful cancellation (`200 OK`).

## GitHub
After testing, create a public GitHub repository and push this project. Commit the source files and migrations, but do not commit `venv/` or `db.sqlite3`.

## Author
Replace this section with your name, roll number, and college details if required.
