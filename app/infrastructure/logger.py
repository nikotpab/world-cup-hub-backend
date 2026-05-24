import logging
import json
from datetime import datetime, timezone

class JsonFormatter(logging.Formatter):
    """ Formatea todos los logs como objetos JSON para Elasticsearch/Splunk """
    def format(self, record):
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
        }
        
        if isinstance(record.msg, dict):
            # Si el mensaje ya es un diccionario, fusionarlo
            log_record.update(record.msg)
        else:
            log_record["message"] = record.getMessage()
            
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

class FilterSecrets(logging.Filter):
    """ Filtra parámetros sensibles del log para prevenir fugas (Shift-Left Security) """
    _SENSITIVE_KEYS = frozenset(['password', 'MFA_token', 'token', 'authorization'])

    def filter(self, record):
        if isinstance(record.msg, dict):
            record.msg = {
                k: '***REDACTED***' if k in self._SENSITIVE_KEYS else v
                for k, v in record.msg.items()
            }
        return super().filter(record)

class DatabaseAuditHandler(logging.Handler):
    """ Handler que captura eventos de auditoría y los persiste en la BD """
    def emit(self, record):
        if not isinstance(record.msg, dict) or not record.msg.get("audit"):
            return
        try:
            from flask import current_app
            if not current_app:
                return
            from app.domain.models.audit import Audit
            from app.infrastructure.database import db
            from sqlalchemy.orm import sessionmaker
            
            payload = record.msg
            correlation_id = payload.get("correlation_id") or payload.get("correlationId")
            affected_entity = payload.get("entity") or payload.get("event", "unknown").split("_")[0]
            action = payload.get("event") or record.levelname
            result = "SUCCESS" if record.levelname == "INFO" else "ERROR"
            
            # Redactar llaves sensibles
            clean_payload = {
                k: '***REDACTED***' if k in FilterSecrets._SENSITIVE_KEYS else v
                for k, v in payload.items() if k != "audit"
            }
            
            audit_entry = Audit(
                correlationId=correlation_id,
                payload=json.dumps(clean_payload),
                affectedEntity=affected_entity,
                action=action,
                result=result
            )
            
            # Usar una sesión independiente para evitar interferir con la transacción de la petición actual
            Session = sessionmaker(bind=db.engine)
            session = Session()
            try:
                session.add(audit_entry)
                session.commit()
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()
        except Exception as _e:
            import logging as _stdlib_logging
            _stdlib_logging.getLogger(__name__).debug("Audit log failed: %s", _e)

def setup_logger():
    logger = logging.getLogger("world_cup_hub")
    logger.setLevel(logging.INFO)
    
    # Prevenir que los logs se propaguen al root logger (evita duplicados si Gunicorn ya loguea)
    logger.propagate = False
    
    handler = logging.StreamHandler()
    
    # Usar el formateador JSON estructurado
    handler.setFormatter(JsonFormatter())
    
    # Agregar filtro de seguridad
    handler.addFilter(FilterSecrets())
    
    # Limpiar handlers previos para no duplicar en hot-reloads
    if logger.hasHandlers():
        logger.handlers.clear()
        
    logger.addHandler(handler)
    
    # Registrar el handler de base de datos para persistencia de auditoría
    db_handler = DatabaseAuditHandler()
    logger.addHandler(db_handler)
    
    return logger

app_logger = setup_logger()
