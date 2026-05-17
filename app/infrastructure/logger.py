import logging
import json
from datetime import datetime

class JsonFormatter(logging.Formatter):
    """ Formatea todos los logs como objetos JSON para Elasticsearch/Splunk """
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
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
    def filter(self, record):
        if not isinstance(record.msg, dict):
            return True
            
        sensitive_keys = ['password', 'MFA_token', 'token', 'authorization']
        sanitized_msg = record.msg.copy()
        
        for key in sensitive_keys:
            if key in sanitized_msg:
                sanitized_msg[key] = '***REDACTED***'
                
        record.msg = sanitized_msg # El JsonFormatter se encarga de hacer el json.dumps
        return True

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
