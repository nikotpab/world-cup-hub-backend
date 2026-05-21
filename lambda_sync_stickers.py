"""
AWS Lambda handler — Sticker Catalogue Sync
Trigger: manual invocation or EventBridge one-shot before tournament start.

Seeds the full FIFA World Cup 2026 Adrenalyn XL catalogue.
"""
import json
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TEAMS_JSON = [
  "Mexico", "South Africa", "South Korea", "Czechia", "Canada", 
  "Bosnia and Herzegovina", "Qatar", "Switzerland", "Brazil", "Morocco", "Haiti", 
  "Scotland", "USA", "Paraguay", "Australia", "Turkey", "Germany", 
  "Curacao", "Ivory Coast", "Ecuador", "Netherlands", "Japan", "Sweden", 
  "Tunisia", "Belgium", "Egypt", "Iran", "New Zealand", "Spain", 
  "Cape Verde", "Saudi Arabia", "Uruguay", "France", "Senegal", "Iraq", 
  "Norway", "Argentina", "Algeria", "Austria", "Jordan", "Portugal", 
  "DR Congo", "Uzbekistan", "Colombia", "England", "Croatia", "Ghana", 
  "Panama"
]

def handler(event, context):
    os.environ.setdefault("FLASK_ENV", "production")

    from app import create_app
    app = create_app()

    with app.app_context():
        from app.infrastructure.database import db
        from app.domain.models.sticker import Sticker
        from app.domain.models.rarity_cat import RarityCat

        # Ensure rarities
        rarity_map = {}
        for name in ("Common", "Rare", "Epic", "Legendary"):
            rc = RarityCat.query.filter_by(name=name).first()
            if not rc:
                rc = RarityCat(name=name)
                db.session.add(rc)
                db.session.commit()
            rarity_map[name] = rc.rarityCatId

        # Get existing codes to ensure idempotency
        existing_codes = {st.paniniCode for st in Sticker.query.all()}
        
        added = 0
        current_id = 1000

        # Generate exactly 12 cards for each of the 48 teams
        for team_name in TEAMS_JSON:
            team_upper = team_name.upper()
            
            # Fan Favourite
            if str(current_id) not in existing_codes:
                st = Sticker(
                    name=f"Jugador FF {team_upper}",
                    category="Fan Favourite",
                    rarity="Epic",
                    team=team_upper,
                    paniniCode=str(current_id),
                    raretyCatId=rarity_map["Epic"]
                )
                db.session.add(st)
                added += 1
            current_id += 1

            # Team Crest
            if str(current_id) not in existing_codes:
                st = Sticker(
                    name="TEAM CREST",
                    category="Team Crest",
                    rarity="Rare",
                    team=team_upper,
                    paniniCode=str(current_id),
                    raretyCatId=rarity_map["Rare"]
                )
                db.session.add(st)
                added += 1
            current_id += 1

            # Icon Card
            if str(current_id) not in existing_codes:
                st = Sticker(
                    name=f"Jugador IC {team_upper}",
                    category="Icon Card",
                    rarity="Legendary",
                    team=team_upper,
                    paniniCode=str(current_id),
                    raretyCatId=rarity_map["Legendary"]
                )
                db.session.add(st)
                added += 1
            current_id += 1

            # 9 Common Players
            for i in range(1, 10):
                if str(current_id) not in existing_codes:
                    st = Sticker(
                        name=f"Jugador {i} {team_upper}",
                        category="Player",
                        rarity="Common",
                        team=team_upper,
                        paniniCode=str(current_id),
                        raretyCatId=rarity_map["Common"]
                    )
                    db.session.add(st)
                    added += 1
                current_id += 1

        db.session.commit()
        total = Sticker.query.count()

    logger.info({
        "event": "sticker_sync_complete",
        "added": added,
        "total": total,
    })

    return {
        "statusCode": 200,
        "body": json.dumps({
            "added": added,
            "total": total,
        }),
    }
