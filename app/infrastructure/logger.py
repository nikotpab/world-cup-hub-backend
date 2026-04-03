import logging
import json

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
                
        record.msg = json.dumps(sanitized_msg)
        return True

def setup_logger():
    logger = logging.getLogger("world_cup_hub")
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Agregar filtro
    handler.addFilter(FilterSecrets())
    
    logger.addHandler(handler)
    return logger

app_logger = setup_logger()
