import re

with open('app/infrastructure/external/sync_stickers.py', 'r') as f:
    content = f.read()

with open('equipos_out_1000.py', 'r') as f:
    new_equipos = f.read()

pattern = re.compile(r'_EQUIPOS\s*=\s*\{.*?\n\}\n', re.DOTALL)
new_content = pattern.sub(new_equipos + '\n\n', content)

with open('app/infrastructure/external/sync_stickers.py', 'w') as f:
    f.write(new_content)
