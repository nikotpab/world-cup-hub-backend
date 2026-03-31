# World Cup Hub - Backend Service

![Python](https://img.shields.io/badge/python-3.13+-blue.svg)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=flat\&logo=flask\&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat\&logo=postgresql\&logoColor=white)

## 1. Project Description

**World Cup Hub** is a platform focused on the digital experience of the FIFA World Cup 2026. This backend service manages the logistical complexity of a multinational event, providing an informational and operational core for fans and operations teams.

The system emphasizes **transparency and traceability**, recording every relevant event (schedule changes, notifications, transfers) in an auditable manner.

## 2. Key Features (MVP)

* **User and Preferences Management**: Registration, login, and configuration of personal schedules based on favorite teams and venues.
* **Match Tracking**: Ingestion of data from external providers regarding teams, matches, and real-time results.
* **Football Prediction Pools Module**: Social prediction game with a points system, including automatic score calculation and rankings.
* **Digital Album**: Sticker collection system with pack opening and user-to-user trading within the community.
* **Ticketing and Payments**: Management of the ticket lifecycle (Available → Reserved → Paid) with traceable state transitions.
* **Auditing and Support**: Transaction logging for case investigation and compliance.

## 3. Technology Stack

* **Language**: Python 3.13
* **Web Framework**: Flutter
* **Persistence**: SQLAlchemy ORM with PostgreSQL support
* **Serialization**: Marshmallow-SQLAlchemy for model and schema management
* **Security**: JWT (JSON Web Tokens) authentication and password hashing with Argon2
* **Testing**: Pytest and unittest.mock for business logic validation

## 4. Project Structure

The backend follows a service-oriented architecture with a clear separation of concerns:

```text
src/
├── database/          # Database and persistence configuration
├── models/            # Domain entity definitions (User, Match, Ticket, etc.)
├── services/          # Business logic and services (AuthenticationService)
├── test/              # Unit test suite and mocks
├── __init__.py        # Application factory
config.py              # Environment configurations (Development/Production)
run.py                 # Server entry point
```
