# 📚 Library Service Project

This project is a backend system for managing a library's books, borrowings, payments, and notifications.  
It was created as practice for solving a complex technical task.

The goal of the system is to replace the outdated paper-based process in a library, enabling:
- Managing book inventory
- Managing users and borrowings
- Handling payments (via Stripe)
- Sending notifications (via Telegram)
- Running scheduled background tasks (Celery)

---

## 🚀 Features

- **Books Service** – CRUD operations for books (inventory, daily fee, etc.)
- **Users Service** – registration, authentication (JWT), profile management
- **Borrowings Service** – borrow/return books, track overdue borrowings
- **Payments Service** – create payments, handle fines, integrate with Stripe
- **Notifications Service** – Telegram bot integration for borrowings, overdue reminders, payments
- **Background Tasks** – Celery workers & beat for periodic jobs

---

## 🛠️ Tech Stack

- **Backend:** Django + Django REST Framework
- **Database:** PostgreSQL
- **Task Queue:** Celery + Redis
- **Payments:** Stripe API
- **Notifications:** Telegram Bot API
- **Docker & docker-compose** for containerization

---

## ⚙️ Requirements

- Docker & Docker Compose
- Stripe test account (for payments)
- Telegram bot token (for notifications)

---

## 🐳 Running with Docker

```bash
git clone https://github.com/Codoeh/library-service
cd library-service
cp .env.sample .env
docker compose up --build
```

---

## 🧪 Running Tests

To run tests inside Docker:
```bash
docker compose run --rm django-web pytest
```

---

## 📡 API Endpoints (examples)

Books:
- POST /books/ – create book (admin only)
- GET /books/ – list books
- GET /books/<id>/ – get book detail

Users:
- POST /users/ – register
- POST /users/token/ – login (JWT)
- GET /users/me/ – get profile

Borrowings
- POST /borrowings/ – borrow a book
- GET /borrowings/?is_active=true – list active borrowings for admin only
- GET /borrowings/?user_id= - list of user's borrowing for admin only
- POST /borrowings/<id>/return_book/ – return book

Payments
- GET /payments/ – list payments
- GET /payments/<id>/ – payment details

---

## 🔔 Notifications

- On borrowing created → Telegram notification
- On overdue borrowings → Daily Telegram reminder
- On successful payment → Telegram confirmation
