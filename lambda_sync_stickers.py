"""
AWS Lambda handler — Sticker Catalogue Sync
Trigger: manual invocation or EventBridge one-shot before tournament start.

Seeds the full FIFA World Cup 2026 Adrenalyn XL catalogue from the hardcoded
JSON dataset and optionally enriches it with player cards from football-data.org.

Environment variables required:
    DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY, FLASK_ENV=production
    FOOTBALL_API_KEY (optional — enriches player cards via football-data.org)
"""
import json
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, context):
    os.environ.setdefault("FLASK_ENV", "production")

    from app.infrastructure.external.sync_stickers import (
        _ensure_rarities,
        _ESPECIALES,
        _EQUIPOS,
        _OTROS,
        _upsert,
        _sync_from_api,
    )
    from app import create_app

    app = create_app()
    with app.app_context():
        from app.infrastructure.database import db
        from app.domain.models.sticker import Sticker

        rarity_map = _ensure_rarities(db)
        added_json = 0

        for cat_data in _ESPECIALES.values():
            for item in cat_data["items"]:
                added_json += _upsert(
                    db, Sticker, rarity_map,
                    panini_code=item["numero"],
                    name=item["nombre"],
                    team=item.get("pais", "WORLD"),
                    category=cat_data["category"],
                    rarity=cat_data["rarity"],
                )

        _TEAM_CREST = "TEAM CREST"
        for team_name, team_data in _EQUIPOS.items():
            for item in team_data["items"]:
                tipo, nombre = item.get("tipo"), item["nombre"]
                if nombre == _TEAM_CREST:
                    category, rarity = "Team Crest", "Rare"
                elif tipo == "IC":
                    category, rarity = "Icon Card", "Legendary"
                elif tipo == "FF":
                    category, rarity = "Fan Favourite", "Epic"
                else:
                    category, rarity = "Player", "Common"
                added_json += _upsert(
                    db, Sticker, rarity_map,
                    panini_code=item["numero"],
                    name=nombre,
                    team=team_name,
                    category=category,
                    rarity=rarity,
                )

        for cat_data in _OTROS.values():
            for item in cat_data["items"]:
                added_json += _upsert(
                    db, Sticker, rarity_map,
                    panini_code=item["numero"],
                    name=item["nombre"],
                    team="WORLD",
                    category=cat_data["category"],
                    rarity=cat_data["rarity"],
                )

        db.session.commit()
        added_api = 0
        total = Sticker.query.count()

    logger.info({
        "event": "sticker_sync_complete",
        "added_json": added_json,
        "added_api": added_api,
        "total": total,
    })

    return {
        "statusCode": 200,
        "body": json.dumps({
            "added_json": added_json,
            "added_api": added_api,
            "total": total,
        }),
    }
