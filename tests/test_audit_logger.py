import json
import logging
from app.infrastructure.logger import app_logger
from app.domain.models.audit import Audit

def test_regular_log_is_not_audited(app_context):
    # Contar antes
    initial_count = Audit.query.count()
    
    app_logger.info("Esto es un log normal sin metadata de auditoria")
    
    # Debe ser el mismo contador
    assert Audit.query.count() == initial_count

def test_audit_log_persists_to_db(app_context):
    initial_count = Audit.query.count()
    
    # Emitir log con "audit": True
    app_logger.info({
        "event": "ticket_reserved",
        "ticket_id": 999,
        "user_id": 12,
        "correlation_id": "test-uuid-correlation-1234",
        "audit": True
    })
    
    # Debe incrementar por 1
    assert Audit.query.count() == initial_count + 1
    
    # Traer el ultimo record
    last_audit = Audit.query.order_by(Audit.idAudit.desc()).first()
    assert last_audit is not None
    assert last_audit.correlationId == "test-uuid-correlation-1234"
    assert last_audit.action == "ticket_reserved"
    assert last_audit.affectedEntity == "ticket"
    assert last_audit.result == "SUCCESS"
    
    payload = json.loads(last_audit.payload)
    assert payload["ticket_id"] == 999
    assert payload["user_id"] == 12
    assert "audit" not in payload  # Se limpia del payload

def test_audit_log_redacts_secrets(app_context):
    # Emitir log con campos sensibles y "audit": True
    app_logger.info({
        "event": "user_logged_in",
        "user_id": 45,
        "password": "my-secret-password-123",
        "token": "bearer-token-xyz",  # NOSONAR
        "correlation_id": "secret-audit-corr-id",
        "audit": True
    })
    
    last_audit = Audit.query.order_by(Audit.idAudit.desc()).first()
    assert last_audit is not None
    assert last_audit.correlationId == "secret-audit-corr-id"
    
    payload = json.loads(last_audit.payload)
    assert payload["password"] == "***REDACTED***"
    assert payload["token"] == "***REDACTED***"
    assert payload["user_id"] == 45

def test_get_user_timeline_includes_correct_logs(app_context):
    from app.infrastructure.repositories.admin_repository import SqlAlchemyAdminRepository
    
    # Emitir un log para el usuario 99
    app_logger.info({
        "event": "ticket_reserved",
        "ticket_id": 101,
        "user_id": 99,
        "correlation_id": "corr-user-99-a",
        "audit": True
    })
    
    # Emitir un log para el usuario 88
    app_logger.info({
        "event": "ticket_paid",
        "ticket_id": 102,
        "user_id": 88,
        "correlation_id": "corr-user-88-a",
        "audit": True
    })
    
    # Emitir otro log para el usuario 99
    app_logger.info({
        "event": "sports_bet_placed",
        "bet_id": 5,
        "user_id": 99,
        "stake": 50,
        "odds": 2.5,
        "correlation_id": "corr-user-99-b",
        "audit": True
    })
    
    repo = SqlAlchemyAdminRepository()
    timeline_99 = repo.get_user_timeline(99)
    timeline_88 = repo.get_user_timeline(88)
    
    # Usuario 99 debe tener 2 eventos ordenados por fecha descendente (el mas nuevo primero)
    assert len(timeline_99) == 2
    assert timeline_99[0]["action"] == "sports_bet_placed"
    assert timeline_99[1]["action"] == "ticket_reserved"

    # Usuario 88 debe tener 1 evento
    assert len(timeline_88) == 1
    assert timeline_88[0]["action"] == "ticket_paid"

def test_audit_logger_uses_independent_session(app_context):
    from unittest.mock import patch, MagicMock
    from app.infrastructure.logger import DatabaseAuditHandler
    
    handler = DatabaseAuditHandler()
    record = MagicMock()
    record.msg = {
        "event": "test_event",
        "correlation_id": "test_corr",
        "audit": True
    }
    record.levelname = "INFO"
    
    mock_session = MagicMock()
    with patch("sqlalchemy.orm.sessionmaker") as mock_sessionmaker:
        mock_sessionmaker.return_value = lambda: mock_session
        
        with patch("app.infrastructure.database.db.session") as mock_db_session:
            handler.emit(record)
            
            # Verificar que se agrego y confirmo en la sesion independiente
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()
            
            # Verificar que NO se modifico ni confirmo la sesion principal de Flask-SQLAlchemy
            mock_db_session.add.assert_not_called()
            mock_db_session.commit.assert_not_called()

