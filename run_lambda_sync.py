import json
from lambda_sync_stickers import handler

result = handler({}, None)
print(json.dumps(result, indent=2))
