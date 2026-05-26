import pytest
from datetime import datetime, timedelta, timezone
from app.application.services.ticket_service import TicketService
from app.infrastructure.repositories.ticket_repository import SqlAlchemyTicketRepository
from app.domain.models.user import User
from app.domain.models.match import Match
from app.domain.models.ticket import Ticket
from app.domain.models.role import Role
from app.infrastructure.database import db

@pytest.fixture
def ticket_service():
    repo = SqlAlchemyTicketRepository()
    return TicketService(repository=repo)

@pytest.fixture
def test_user():
    # Ensure client role exists or create user
    role = Role.query.filter_by(idRole=2).first()
    if not role:
        role = Role(idRole=2, roleName="Cliente")
        db.session.add(role)
        db.session.commit()
        
    user = User(
        firstName="Ticket",
        lastName="User",
        email="ticketuser@example.com",
        password="password",
        identification=12312312,
        idRole=2
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def other_user():
    user = User(
        firstName="Other",
        lastName="TicketUser",
        email="otherticket@example.com",
        password="password",
        identification=32132132,
        idRole=2
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def setup_match():
    match = Match(
        scheduledAt=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=2),
        ticket_price=100.0,
        home_team_name="Colombia",
        away_team_name="Ecuador"
    )
    db.session.add(match)
    db.session.commit()
    return match

def test_ticket_purchase_limit(test_user, setup_match, ticket_service):
    # Add 10 available tickets
    tickets = []
    for _ in range(10):
        t = Ticket(matchId=setup_match.matchId, status="Disponible", price=100.0)
        db.session.add(t)
        tickets.append(t)
    db.session.commit()

    # Reserve and pay 4 tickets (the proposed limit of 4)
    # Let's change limit in ticket_service.py to 4 and see if it fails on the 5th
    # We will verify what happens.
    for _ in range(4):
        res = ticket_service.reserve_ticket({
            "userId": test_user.idUser,
            "matchId": setup_match.matchId
        })
        assert res.status == "Reservada"
        # To count towards daily purchase limit, it must be PAID
        pay_res = ticket_service.process_payment(res.ticketId, {
            "userId": test_user.idUser,
            "paymentToken": "tok_visa"
        })
        assert pay_res["status"] == "Pagada"

    # The 5th reservation should fail because daily purchases limit is 4
    with pytest.raises(ValueError) as exc:
        ticket_service.reserve_ticket({
            "userId": test_user.idUser,
            "matchId": setup_match.matchId
        })
    assert "Límite diario" in str(exc.value)

def test_ticket_transfer_limit(test_user, other_user, setup_match, ticket_service):
    # Create 5 paid tickets for test_user
    tickets = []
    for _ in range(5):
        t = Ticket(
            matchId=setup_match.matchId,
            status="Pagada",
            price=100.0,
            userId=test_user.idUser,
            paidAt=datetime.now(timezone.utc).replace(tzinfo=None)
        )
        db.session.add(t)
        tickets.append(t)
    db.session.commit()

    # Transfer 3 tickets (limit is 3)
    for i in range(3):
        res = ticket_service.transfer_ticket(tickets[i].ticketId, {
            "fromUserId": test_user.idUser,
            "toUserId": other_user.idUser
        })
        assert res["success"] is True

    # The 4th transfer should fail
    with pytest.raises(ValueError) as exc:
        ticket_service.transfer_ticket(tickets[3].ticketId, {
            "fromUserId": test_user.idUser,
            "toUserId": other_user.idUser
        })
    assert "Límite diario" in str(exc.value)

def test_get_user_daily_stats_api(app_context, test_user):
    client = app_context.test_client()
    response = client.get(f"/api/v1/users/{test_user.idUser}/tickets/daily-stats")
    assert response.status_code == 200
    data = response.get_json()
    assert "purchasesToday" in data
    assert "maxPurchasesPerDay" in data
    assert "transfersToday" in data
    assert "maxTransfersPerDay" in data
    assert data["purchasesToday"] == 0
    assert data["transfersToday"] == 0
    assert data["maxPurchasesPerDay"] == 4
    assert data["maxTransfersPerDay"] == 3
