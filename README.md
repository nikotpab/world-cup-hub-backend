# World Cup Hub - Backend Service

The backend service for the World Cup Hub platform provides a robust API to manage the logistical and operational requirements of the FIFA World Cup 2026.

## Project Overview

World Cup Hub manages the complexity of a multinational event, serving as the informational and operational core for both fans and administrative teams. The system prioritizes transparency and traceability, ensuring all relevant events are recorded in an auditable manner.

## Key Features

- **User Management**: Authentication and personal preference synchronization.
- **Match Tracking**: Integration of tournament data, including team statistics and real-time match results.
- **Prediction Pools**: A social gaming module with automated point calculations and rankings.
- **Digital Album**: A sticker collection system featuring pack openings and a trading marketplace.
- **Ticketing and Payments**: End-to-end lifecycle management of ticket reservations and payments with state-based traceability.
- **Auditing**: Comprehensive transaction logging for compliance and investigation.

## Technical Stack

- **Language**: Python 3.13
- **Framework**: Flask
- **ORM**: SQLAlchemy with PostgreSQL support
- **Serialization**: Marshmallow-SQLAlchemy
- **Security**: JWT (JSON Web Tokens) and Argon2 password hashing
- **Testing**: Pytest and unittest.mock

## Architecture and Structure

The service follows a layered architecture to ensure separation of concerns:

- `app/`: Primary application package.
  - `application/`: Application-specific business logic.
  - `domain/`: Core entities and domain logic.
  - `infrastructure/`: Persistence, database configuration, and external integrations.
  - `presentation/`: API endpoints and request handling.
- `tests/`: Comprehensive test suite for business logic validation.
- `config.py`: Environment-specific configurations.
- `run.py`: Application entry point.

## Getting Started

1. Set up a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables in a `.env` file (refer to `config.py`).

4. Execute the service:
   ```bash
   python run.py
   ```

## Development and Testing

To run the automated test suite:
```bash
pytest
```
