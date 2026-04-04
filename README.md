# KanMind Backend

Backend for a Kanban application built with Django and Django REST Framework.

The project is structured in a modular way and follows common backend patterns like separation of concerns (models, serializers, views, permissions).

---

## Features

- User registration
- Login with token authentication
- User profile with fullname
- Basic project structure for boards and tasks

---

## Tech Stack

- Python
- Django
- Django REST Framework
- Token Authentication
- SQLite (for development)

---

## Project Structure

core/  
→ main project config (settings, urls)

auth_app/  
→ handles authentication and user profile

kanban_app/  
→ will handle boards and tasks

---

## Setup

Clone the repo:

```bash
git clone https://github.com/MarcAndreBuck/kanmind-backend.git
cd kanmind-backend
```

Create virtual environment:

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
python manage.py migrate
```

Start server:

```bash
python manage.py runserver
```

---

## API Endpoints

### Register

POST `/api/registration/`

```json
{
  "fullname": "Marc Buck",
  "email": "test@mail.de",
  "password": "123456",
  "repeated_password": "123456"
}
```

Response:

```json
{
  "token": "your_token",
  "fullname": "Marc Buck",
  "email": "test@mail.de",
  "user_id": 1
}
```

---

### Login

POST `/api/login/`

```json
{
  "email": "test@mail.de",
  "password": "123456"
}
```

Response:

```json
{
  "token": "your_token",
  "fullname": "Marc Buck",
  "email": "test@mail.de",
  "user_id": 1
}
```
---

### Logout

POST `/api/logout/`

Header:

Authorization: Token <your_token>

Response:

200 OK

```json
{
  "detail": "Logout successful. Token has been deleted."
}
```
---

## Notes

- Uses Django default User model
- Fullname is stored in a separate UserProfile model
- Email is used as login identifier
- Passwords are hashed using Django's built-in system

---

## Status

Work in progress.

Authentication is implemented, next step is building boards and tasks.

---

## Author

Marc-André Buck
