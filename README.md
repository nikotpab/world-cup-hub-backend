# World Cup Hub — Backend Service

REST API backend for the World Cup Hub platform, managing the full operational lifecycle of the FIFA World Cup 2026: match data, ticketing, sticker albums, social communities, sports betting, and more.

---

## Table of Contents

- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Getting Started](#getting-started)
- [Running Tests](#running-tests)
- [Docker](#docker)
- [Deployment](#deployment)
- [API Reference](#api-reference)

---

## Architecture

The service follows a hexagonal (ports and adapters) architecture with four layers:

```
app/
  domain/          Core entities and business rules — no external dependencies
  application/     Use cases, DTOs, and repository interfaces
  infrastructure/  SQLAlchemy repositories, Redis cache, external service clients
  presentation/    Flask blueprints and request/response handling
```

Background processes run as daemon threads at startup:
- **TTL worker** — expires stale ticket reservations every 60 seconds.
- **Startup migrations** — applies incremental schema changes 5 seconds after the first worker is ready.

Daily pack distribution runs as a standalone AWS Lambda (`lambda_daily_packs.py`) triggered by EventBridge at 05:00 UTC.

---

## Technology Stack

| Concern | Technology |
|---|---|
| Language | Python 3.11 |
| Framework | Flask 3 + Gunicorn (gevent workers) |
| ORM | SQLAlchemy 2 + Flask-SQLAlchemy |
| Database | PostgreSQL (Azure Database for PostgreSQL, SSL required) |
| Cache | Redis (AWS ElastiCache) with in-memory fallback |
| Serialization | Marshmallow / marshmallow-sqlalchemy + Pydantic (DTOs) |
| Authentication | JWT (PyJWT) + Argon2 password hashing |
| Push notifications | Firebase Cloud Messaging (firebase-admin SDK) |
| Payments | Stripe (PaymentIntents) |
| External data | football-data.org v4 API, NewsAPI, TheSportsDB |
| Testing | pytest + pytest-mock |
| CI/CD | GitHub Actions → AWS ECR → Amazon ECS |
| Code quality | SonarCloud |
| Container | Docker (multi-stage Alpine build) |

---

## Project Structure

```
world-cup-hub-backend/
  app/
    __init__.py                    Application factory (create_app)
    config.py                      Development / Testing / Production configs
    domain/
      models/                      SQLAlchemy ORM models
        user.py, match.py, ticket.py, album.py, sticker.py,
        bet.py, sports_bet.py, community.py, post.py, ...
    application/
      dtos/                        Pydantic request/response schemas
      interfaces/                  Abstract repository interfaces
      services/                    Business logic (one service per domain)
        auth_service.py, ticket_service.py, album_service.py,
        bet_service.py, community_service.py, ...
    infrastructure/
      database/__init__.py         SQLAlchemy db instance
      cache/redis_client.py        Redis + fallback client
      repositories/                SQLAlchemy repository implementations
      external/
        football_data_service.py   football-data.org integration
        news_service.py            NewsAPI integration
        payment_service.py         Stripe integration
        notification_service.py    FCM push notification dispatcher
        email_service.py           SMTP (Hostinger) email client
        sync_stickers.py           Sticker catalogue sync utility
        secrets_manager.py         AWS Secrets Manager client
      logger.py                    Structured JSON logger
    presentation/
      api/                         Flask blueprints (one per domain)
      middlewares/
        auth.py                    JWT validation + role enforcement
        idempotency.py             Idempotency key middleware
  tests/
    conftest.py
    test_album_features.py
    test_bet_service.py
    test_community_service.py
  lambda_daily_packs.py            AWS Lambda: daily free pack distribution
  run.py                           Local development entry point
  Dockerfile                       Multi-stage Alpine image
  app-deploy-bg.yml                Kubernetes blue/green deployment manifest
  .github/workflows/ci-cd.yml      CI/CD pipeline
  requirements.txt
  .env.template                    Reference for all required environment variables
```

---

## Environment Variables

Copy `.env.template` to `.env` and fill in all values before running locally.

| Variable | Description |
|---|---|
| `FLASK_ENV` | `development`, `testing`, or `production` |
| `SECRET_KEY` | Flask session secret (generate with `secrets.token_hex(32)`) |
| `JWT_SECRET_KEY` | JWT signing secret |
| `DATABASE_URL` | PostgreSQL connection string |
| `CORS_ORIGINS` | Comma-separated list of allowed frontend origins |
| `REDIS_URL` | Redis connection URL (optional; falls back to in-memory dict) |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Firebase service account JSON (for FCM) |
| `SMTP_SERVER` / `SMTP_PORT` / `SMTP_EMAIL` / `SMTP_PASSWORD` | Email (Hostinger SMTP) |
| `FOOTBALL_API_URL` / `FOOTBALL_API_KEY` | football-data.org API |
| `NEWS_API_KEY` | NewsAPI key |
| `THESPORTSDB_API_KEY` | TheSportsDB API key |
| `PROXY_ALLOWED_HOSTS` | Comma-separated whitelist for the image proxy |
| `AWS_DEFAULT_REGION` | AWS region (injected by IAM role in production) |

In production, secrets are fetched from AWS Secrets Manager and injected as environment variables by the ECS task role — nothing is hardcoded.

---

## Getting Started

**Prerequisites:** Python 3.11, PostgreSQL (or SQLite for development), and optionally Redis.

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.template .env
# Edit .env with your values

# 4. Start the development server
python run.py
```

The server starts on `http://0.0.0.0:5001`. With `FLASK_ENV=development`, SQLite is used by default (`instance/dev.db`).

---

## Running Tests

```bash
# All tests
pytest

# With coverage report
pytest tests/ --cov=app --cov-report=term
```

The test suite uses an in-memory SQLite database (`SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"`) and mocks for external services.

---

## Docker

```bash
# Build the image
docker build -t world-cup-backend .

# Run with environment variables
docker run --env-file .env -p 8000:8000 world-cup-backend
```

The multi-stage Dockerfile compiles all native dependencies (psycopg2, gevent) in the builder stage and produces a minimal Alpine runtime image. The container runs as a non-root user (`nonrootuser`) and serves on port 8000 via Gunicorn with 4 gevent workers.

---

## Deployment

### CI/CD Pipeline (`.github/workflows/ci-cd.yml`)

| Stage | Trigger | Action |
|---|---|---|
| `test-and-analyze` | Every push to `main`, `develop`, `security` | Run pytest + coverage, SonarCloud scan |
| `build-and-push-ecr` | Push to `main` or `security` | Build Docker image, push to Amazon ECR |
| `deploy-ecs` | After ECR push | Force new ECS deployment (`world-cup-hub-cluster`) |
| `deploy-lambda` | Push to `main` only | Package and update the `worldcuphub-daily-packs` Lambda |

### Infrastructure

- **Compute:** Amazon ECS (Fargate) — see `app-deploy-bg.yml` for the Kubernetes blue/green manifest used in alternative environments.
- **Database:** Azure Database for PostgreSQL (SSL required).
- **Cache:** AWS ElastiCache (Redis).
- **Secrets:** AWS Secrets Manager.
- **Scheduled jobs:** AWS Lambda + EventBridge rule `cron(0 5 * * ? *)` for daily pack distribution.

---

## API Reference

All endpoints are prefixed with `/api/v1`.

Authentication is enforced by the `require_role` decorator. Roles: `1` = admin, `2` = standard user.

### Health

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness probe |

### Authentication

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/register` | Register a new user account |
| `POST` | `/auth/verify` | Verify email with OTP code |
| `POST` | `/auth/resend` | Resend verification email |
| `POST` | `/auth/login` | Authenticate and receive JWT |
| `POST` | `/auth/logout` | Invalidate session |

### Users

| Method | Path | Description |
|---|---|---|
| `POST` | `/users` | Create user profile |
| `GET` | `/users/{user_id}` | Get user profile |
| `GET` | `/users` | List all users (admin) |
| `GET` | `/users/{user_id}/notifications` | Get user notifications |
| `PUT` | `/users/{user_id}/profile-picture` | Update profile picture |
| `GET` | `/users/{user_id}/preferences` | Get user preferences |
| `PUT` | `/users/{user_id}/preferences` | Update user preferences |
| `POST` | `/users/{user_id}/fcm-token` | Register FCM push token |

### Matches

| Method | Path | Description |
|---|---|---|
| `POST` | `/matches` | Create a match (admin) |
| `GET` | `/matches` | List all matches |
| `GET` | `/matches/{match_id}` | Get match detail |
| `GET` | `/matches/live` | List live matches |
| `POST` | `/matches/{match_id}/finalize` | Finalize a match and settle bets (admin) |

### Ticketing

Tickets follow the state machine: `Disponible` → `Reservada` → `Pagada` → `Transferida` / `Reembolsada`. Reservations expire automatically after a configurable TTL.

| Method | Path | Description |
|---|---|---|
| `POST` | `/tickets` | Create available ticket (admin) |
| `GET` | `/tickets/{ticket_id}` | Get ticket detail |
| `GET` | `/users/{user_id}/tickets` | List tickets owned by a user |
| `GET` | `/tickets/{ticket_id}/history` | Full audit trail for a ticket |
| `POST` | `/tickets/reserve` | Reserve a ticket (`Disponible` → `Reservada`) |
| `POST` | `/tickets/{ticket_id}/pay` | Pay for a reservation (`Reservada` → `Pagada`) |
| `POST` | `/tickets/{ticket_id}/transfer` | Transfer by user ID (`Pagada` → `Transferida`) |
| `POST` | `/tickets/{ticket_id}/transfer-by-email` | Transfer by recipient email |
| `POST` | `/tickets/{ticket_id}/refund` | Refund a paid ticket |
| `POST` | `/admin/tickets/expire` | Manually trigger reservation expiry (admin) |
| `GET` | `/matches/ticketing` | List matches with available tickets and prices |

### Digital Album

| Method | Path | Description |
|---|---|---|
| `GET` | `/users/{user_id}/album` | Get user album with sticker inventory |
| `POST` | `/users/{user_id}/packs/open` | Open a sticker pack |
| `POST` | `/users/{user_id}/album/promo/redeem` | Redeem a promo code for packs |
| `POST` | `/users/{user_id}/album/duplicates/convert` | Convert duplicate stickers to coins |
| `POST` | `/users/{user_id}/album/store/buy-pack` | Purchase packs with coins |
| `POST` | `/album/exchange/propose` | Propose a sticker trade |
| `PUT` | `/album/exchange/{trade_id}/confirm` | Accept a trade proposal |
| `PUT` | `/album/exchange/{trade_id}/reject` | Reject a trade proposal |
| `GET` | `/users/{user_id}/trades/pending` | List pending trade proposals |
| `GET` | `/users/{user_id}/album/progress` | Album completion progress |

### Sports Betting

| Method | Path | Description |
|---|---|---|
| `GET` | `/matches/betting` | List matches available for betting with odds |
| `GET` | `/matches/{match_id}/odds` | Get odds for a specific match |
| `POST` | `/sports-bets` | Place a sports bet |
| `GET` | `/users/{user_id}/sports-bets` | Get user's sports bet history |

### Prediction Pools (Communities)

| Method | Path | Description |
|---|---|---|
| `POST` | `/communities` | Create a community |
| `POST` | `/communities/join` | Join a community |
| `GET` | `/communities/mine` | List user's communities |
| `GET` | `/communities/suggested` | Get suggested communities |
| `GET` | `/communities/{community_id}/ranking` | Community leaderboard |

### Match Prediction Bets

| Method | Path | Description |
|---|---|---|
| `POST` | `/bets` | Place a match prediction |
| `PUT` / `PATCH` | `/bets/{bet_id}` | Update a prediction |

### Social Feed

| Method | Path | Description |
|---|---|---|
| `GET` | `/feed` | Get feed posts |
| `POST` | `/feed` | Create a post |
| `PATCH` | `/feed/{post_id}` | Edit a post |
| `DELETE` | `/feed/{post_id}` | Delete a post |
| `POST` | `/feed/{post_id}/like` | Like or unlike a post |
| `GET` | `/feed/{post_id}/comments` | Get comments on a post |
| `POST` | `/feed/{post_id}/comments` | Add a comment |
| `DELETE` | `/feed/comments/{comment_id}` | Delete a comment |
| `POST` | `/feed/comments/{comment_id}/like` | Like or unlike a comment |

### News

| Method | Path | Description |
|---|---|---|
| `GET` | `/news` | Fetch aggregated football news |

### Image Proxy

| Method | Path | Description |
|---|---|---|
| `GET` | `/proxy/image?url=<url>` | Proxy an image from an allowlisted external host |

### Admin

| Method | Path | Description |
|---|---|---|
| `POST` | `/admin/users/{user_id}/block` | Block or unblock a user |
| `GET` | `/admin/users/{user_id}/timeline` | Full audit timeline for a user |
| `GET` | `/admin/reports/compliance` | Compliance report export |
| `POST` | `/admin/news` | Publish a platform news item |
| `PUT` | `/admin/settings/datasource` | Switch the external football data source |
| `GET` | `/admin/notification-log` | View notification delivery history |
