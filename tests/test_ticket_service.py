import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from app.application.services.TicketingService import TicketingService, TicketingError

@pytest.fixture
def mock_ticket():
    ticket = MagicMock()
    ticket.ticketId = 101
    ticket.status = 'Disponible'
    ticket.matchId = 1
    ticket.userId = None
    ticket.reservationDate = None
    ticket.expirationDate = None
    return ticket

class TestTicketingService:

    @patch('src.database.db.session.commit')
    @patch('src.models.ticket.Ticket.query')
    def test_reserve_ticket_success(self, mock_query, mock_commit, mock_ticket):
        query_filter = mock_query.filter_by.return_value
        query_for_update = query_filter.with_for_update.return_value
        query_for_update.first.return_value = mock_ticket

        reserved_ticket = TicketingService.reserve_ticket(match_id=1, user_id=42)

        assert reserved_ticket.status == 'Reservada'
        assert reserved_ticket.userId == 42
        assert reserved_ticket.expirationDate is not None
        assert mock_commit.call_count == 1

    @patch('src.database.db.session.rollback')
    @patch('src.models.ticket.Ticket.query')
    def test_reserve_ticket_sold_out(self, mock_query, mock_rollback):
        query_filter = mock_query.filter_by.return_value
        query_for_update = query_filter.with_for_update.return_value
        query_for_update.first.return_value = None

        with pytest.raises(TicketingError) as excinfo:
            TicketingService.reserve_ticket(match_id=1, user_id=42)
            
        assert str(excinfo.value) == "No hay entradas disponibles para este partido"
        assert excinfo.value.status_code == 404
        assert mock_rollback.call_count == 1

    @patch('src.database.db.session.commit')
    @patch('src.models.ticket.Ticket.query')
    def test_process_payment_success(self, mock_query, mock_commit, mock_ticket):
        mock_ticket.status = 'Reservada'
        mock_ticket.userId = 42
        mock_ticket.expirationDate = datetime.utcnow() + timedelta(minutes=10)
        mock_query.get.return_value = mock_ticket

        result = TicketingService.process_payment(ticket_id=101, user_id=42, payment_token="tok_sandbox_success")

        assert result["success"] is True
        assert mock_ticket.status == 'Pagada'
        assert mock_commit.call_count == 1

    @patch('src.models.ticket.Ticket.query')
    def test_process_payment_resale_forbidden(self, mock_query, mock_ticket):
        mock_ticket.status = 'Reservada'
        mock_ticket.userId = 42
        mock_query.get.return_value = mock_ticket

        with pytest.raises(TicketingError) as excinfo:
            TicketingService.process_payment(ticket_id=101, user_id=99, payment_token="tok_token")

        assert "BR-001" in str(excinfo.value)
        assert excinfo.value.status_code == 403

    @patch('src.models.ticket.Ticket.query')
    def test_process_payment_expired(self, mock_query, mock_ticket):
        mock_ticket.status = 'Reservada'
        mock_ticket.userId = 42
        mock_ticket.expirationDate = datetime.utcnow() - timedelta(minutes=5)
        mock_query.get.return_value = mock_ticket

        with pytest.raises(TicketingError) as excinfo:
            TicketingService.process_payment(ticket_id=101, user_id=42, payment_token="tok_token")

        assert "ha expirado" in str(excinfo.value)
        assert excinfo.value.status_code == 400
