import os
os.environ.setdefault("FLASK_ENV", "production")
from app import create_app
from app.infrastructure.database import db
from app.domain.models.sticker import Sticker
from app.infrastructure.external.sync_stickers import _EQUIPOS, _ensure_rarities

app = create_app()
with app.app_context():
    rarity_map = _ensure_rarities(db)
    
    existing_codes = {st.paniniCode for st in Sticker.query.all()}
    
    new_stickers = []
    _TEAM_CREST = "TEAM CREST"
    
    for team_name, team_data in _EQUIPOS.items():
        for item in team_data["items"]:
            tipo = item.get("tipo")
            nombre = item["nombre"]
            if nombre == _TEAM_CREST:
                category, rarity = "Team Crest", "Rare"
            elif tipo == "IC":
                category, rarity = "Icon Card", "Legendary"
            elif tipo == "FF":
                category, rarity = "Fan Favourite", "Epic"
            else:
                category, rarity = "Player", "Common"
                
            code = str(item["numero"])
            if code not in existing_codes:
                st = Sticker(
                    name=nombre,
                    category=category,
                    rarity=rarity,
                    team=team_name,
                    paniniCode=code,
                    raretyCatId=rarity_map[rarity],
                )
                new_stickers.append(st)
                existing_codes.add(code)
                
    if new_stickers:
        print(f"Bulk saving {len(new_stickers)} new base stickers...")
        db.session.bulk_save_objects(new_stickers)
        db.session.commit()
        print("Done!")
    else:
        print("No new stickers to add.")
        
