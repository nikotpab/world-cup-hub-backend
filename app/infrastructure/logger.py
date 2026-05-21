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
    return logger

app_logger = setup_logger()
