# 🧑‍💼 freelance-user-service

This microservice handles **user authentication**, **registration**, and **token management** for the Freelance Platform.  
Built using **FastAPI**, it includes JWT-based OAuth2 authentication, Redis-powered token revocation, and Kafka event publishing for user lifecycle events.

---

## 🚀 Features

- 🧾 **User Registration & Login**
- 🔐 **JWT Authentication** (access + refresh tokens)
- ♻️ **Token Revocation** with Redis (blacklist)
- 📤 **Kafka Producer Integration**
  - `user_registered`
  - `user_logged_in`
  - `user_logged_out`
- 📦 Built on **FastAPI + PostgreSQL + Redis + Kafka**
- ♻️ Clean architecture (services, domain, infrastructure layers)

---

## 📦 Tech Stack

- **FastAPI** — REST API framework
- **PostgreSQL** — user data storage
- **Redis** — token blacklist (logout)
- **Kafka** — event streaming
- **Docker** — containerization
- **Uvicorn** — ASGI server

---

## 🗃 Kafka Topics

| Event            | Topic Name           |
|------------------|----------------------|
| User Registered  | `user.registered`    |
| User Logged In   | `user.logged_in`     |
| User Logged Out  | `user.logged_out`    |

---

## 📂 Folder Structure
```
app/
├── cmd/ # Entry point
├── config/ # Settings and Kafka config
├── domain/ # Entities, repositories, exceptions
├── infrastructure/ # DB, Kafka, Redis, security
├── presentation/ # Routers & handlers
├── services/ # Business logic
```
## 🧪 Endpoints

- `POST /auth/register` — register new user
- `POST /auth/login` — authenticate and return tokens
- `POST /auth/logout` — revoke refresh token
- `POST /auth/refresh` — refresh access token
- `GET /auth/me` — get current user ID

---

🐳 Docker

Start the service with:

make build
make up
make logs

This uses the Makefile for running the project from the parent directory.

Also make sure Docker network config is created:

docker network create config


Make sure Docker network config is created:
docker network create config

✅ Next Steps

Add gRPC methods (GetUserById, GetUserRole)

Connect to ProjectService

Add tests and CI
