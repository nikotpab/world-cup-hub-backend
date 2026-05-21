"""
Seed completo del álbum FIFA World Cup 2026 Adrenalyn XL.
Fuente 1: JSON oficial (gemini-code-1778726997488.json) — hardcodeado abajo.
Fuente 2: API football-data.org /v4/competitions/WC/teams para jugadores adicionales.

Uso:
    python -m app.infrastructure.external.sync_stickers
    o desde Flask shell: from app.infrastructure.external.sync_stickers import sync; sync()
"""
import sys, os, random, requests, logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Datos JSON — FIFA World Cup 2026 Adrenalyn XL
# ---------------------------------------------------------------------------
_ESPECIALES = {
    "golden_ballers": {
        "category": "Golden Baller", "rarity": "Legendary",
        "items": [
            {"numero": 1,  "nombre": "MESSI",          "pais": "ARG"},
            {"numero": 2,  "nombre": "VINICIUS JUNIOR", "pais": "BRA"},
            {"numero": 3,  "nombre": "SALAH",           "pais": "EGY"},
            {"numero": 4,  "nombre": "KANE",            "pais": "ENG"},
            {"numero": 5,  "nombre": "MBAPPE",          "pais": "FRA"},
            {"numero": 6,  "nombre": "SON",             "pais": "KOR"},
            {"numero": 7,  "nombre": "HAALAND",         "pais": "NOR"},
            {"numero": 8,  "nombre": "RONALDO",         "pais": "POR"},
        ],
    },
    "top_keepers": {
        "category": "Top Keeper", "rarity": "Epic",
        "items": [
            {"numero": 550, "nombre": "MARTÍNEZ",    "pais": "ARG"},
            {"numero": 551, "nombre": "COURTOIS",    "pais": "BEL"},
            {"numero": 552, "nombre": "ALISSON",     "pais": "BRA"},
            {"numero": 553, "nombre": "MAIGNAN",     "pais": "FRA"},
            {"numero": 554, "nombre": "SUZUKI",      "pais": "JPN"},
            {"numero": 555, "nombre": "BOUNOU",      "pais": "MAR"},
            {"numero": 556, "nombre": "DIOGO COSTA", "pais": "POR"},
            {"numero": 557, "nombre": "SIMON",       "pais": "ESP"},
            {"numero": 558, "nombre": "KOBEL",       "pais": "SUI"},
        ],
    },
    "defensive_rocks": {
        "category": "Defensive Rock", "rarity": "Epic",
        "items": [
            {"numero": 559, "nombre": "EDER MILITÃO", "pais": "BRA"},
            {"numero": 560, "nombre": "DAVIES",       "pais": "CAN"},
            {"numero": 561, "nombre": "SALIBA",       "pais": "FRA"},
            {"numero": 562, "nombre": "RÜDIGER",      "pais": "GER"},
            {"numero": 563, "nombre": "KIM",          "pais": "KOR"},
            {"numero": 564, "nombre": "HAKIMI",       "pais": "MAR"},
            {"numero": 565, "nombre": "VAN DIJK",     "pais": "NED"},
            {"numero": 566, "nombre": "NUNO MENDES",  "pais": "POR"},
            {"numero": 567, "nombre": "HUIJSEN",      "pais": "ESP"},
        ],
    },
    "midfield_maestros": {
        "category": "Midfield Maestro", "rarity": "Rare",
        "items": [
            {"numero": 568, "nombre": "FERNÁNDEZ",    "pais": "ARG"},
            {"numero": 569, "nombre": "DE BRUYNE",    "pais": "BEL"},
            {"numero": 570, "nombre": "CASEMIRO",     "pais": "BRA"},
            {"numero": 571, "nombre": "MODRIC",       "pais": "CRO"},
            {"numero": 572, "nombre": "CAICEDO",      "pais": "ECU"},
            {"numero": 573, "nombre": "BELLINGHAM",   "pais": "ENG"},
            {"numero": 574, "nombre": "TCHOUAMÉNI",   "pais": "FRA"},
            {"numero": 575, "nombre": "WIRTZ",        "pais": "GER"},
            {"numero": 576, "nombre": "AMRABAT",      "pais": "MAR"},
            {"numero": 577, "nombre": "REIJNDERS",    "pais": "NED"},
            {"numero": 578, "nombre": "ØDEGAARD",     "pais": "NOR"},
            {"numero": 579, "nombre": "VITINHA",      "pais": "POR"},
            {"numero": 580, "nombre": "MCTOMINAY",    "pais": "SCO"},
            {"numero": 581, "nombre": "RODRI",        "pais": "ESP"},
            {"numero": 582, "nombre": "PEDRI",        "pais": "ESP"},
            {"numero": 583, "nombre": "XHAKA",        "pais": "SUI"},
            {"numero": 584, "nombre": "ADAMS",        "pais": "USA"},
            {"numero": 585, "nombre": "VALVERDE",     "pais": "URU"},
        ],
    },
    "goal_machines": {
        "category": "Goal Machine", "rarity": "Rare",
        "items": [
            {"numero": 586, "nombre": "ALVAREZ",     "pais": "ARG"},
            {"numero": 587, "nombre": "LUKAKU",      "pais": "BEL"},
            {"numero": 588, "nombre": "RAPHINHA",    "pais": "BRA"},
            {"numero": 589, "nombre": "DAVID",       "pais": "CAN"},
            {"numero": 590, "nombre": "DIAZ",        "pais": "COL"},
            {"numero": 591, "nombre": "KRAMARIĆ",    "pais": "CRO"},
            {"numero": 592, "nombre": "VALENCIA",    "pais": "ECU"},
            {"numero": 593, "nombre": "MARMOUSH",    "pais": "EGY"},
            {"numero": 594, "nombre": "RASHFORD",    "pais": "ENG"},
            {"numero": 595, "nombre": "KOLO MUANI",  "pais": "FRA"},
            {"numero": 596, "nombre": "HAVERTZ",     "pais": "GER"},
            {"numero": 597, "nombre": "HALLER",      "pais": "CIV"},
            {"numero": 598, "nombre": "JIMÉNEZ",     "pais": "MEX"},
            {"numero": 599, "nombre": "EN-NESYRI",   "pais": "MAR"},
            {"numero": 600, "nombre": "GAKPO",       "pais": "NED"},
            {"numero": 601, "nombre": "WOOD",        "pais": "NZL"},
            {"numero": 602, "nombre": "SØRLOTH",     "pais": "NOR"},
            {"numero": 603, "nombre": "JACKSON",     "pais": "SEN"},
            {"numero": 604, "nombre": "OYARZABAL",   "pais": "ESP"},
            {"numero": 605, "nombre": "EMBOLO",      "pais": "SUI"},
            {"numero": 606, "nombre": "PULISIC",     "pais": "USA"},
            {"numero": 607, "nombre": "NÚÑEZ",       "pais": "URU"},
        ],
    },
    "master_rookies": {
        "category": "Master Rookie", "rarity": "Rare",
        "items": [
            {"numero": 608, "nombre": "PAZ",          "pais": "ARG"},
            {"numero": 609, "nombre": "MASTANTUONO", "pais": "ARG"},
            {"numero": 610, "nombre": "DEBAST",      "pais": "BEL"},
            {"numero": 611, "nombre": "WESLEY",      "pais": "BRA"},
            {"numero": 612, "nombre": "ESTÊVÃO",     "pais": "BRA"},
            {"numero": 613, "nombre": "SUCIC",       "pais": "CRO"},
            {"numero": 614, "nombre": "PAEZ",        "pais": "ECU"},
            {"numero": 615, "nombre": "ROGERS",      "pais": "ENG"},
            {"numero": 616, "nombre": "DOUÉ",        "pais": "FRA"},
            {"numero": 617, "nombre": "BARCOLA",     "pais": "FRA"},
            {"numero": 618, "nombre": "WOLTEMADE",   "pais": "GER"},
            {"numero": 619, "nombre": "SIMONS",      "pais": "NED"},
            {"numero": 620, "nombre": "SCHJELDERUP", "pais": "NOR"},
            {"numero": 621, "nombre": "GOMEZ",       "pais": "PAR"},
            {"numero": 622, "nombre": "JOÃO NEVES",  "pais": "POR"},
            {"numero": 623, "nombre": "CUBARSI",     "pais": "ESP"},
        ],
    },
}

_TEAM_CREST = "TEAM CREST"

_EQUIPOS = {
    "ARGENTINA": {
        "items": [
            {"numero": 22, "nombre": "JULIAN ALVAREZ",    "tipo": "FF"},
            {"numero": 23, "nombre": _TEAM_CREST},
            {"numero": 24, "nombre": "LIONEL MESSI",      "tipo": "IC"},
            {"numero": 25, "nombre": "EMILIANO MARTÍNEZ"},
            {"numero": 26, "nombre": "NAHUEL MOLINA"},
            {"numero": 27, "nombre": "CRISTIAN ROMERO"},
            {"numero": 28, "nombre": "NICOLAS OTAMENDI"},
            {"numero": 29, "nombre": "ENZO FERNÁNDEZ"},
            {"numero": 30, "nombre": "ALEXIS MAC ALLISTER"},
            {"numero": 31, "nombre": "RODRIGO DE PAUL"},
            {"numero": 32, "nombre": "GIULIANO SIMEONE"},
            {"numero": 33, "nombre": "LAUTARO MARTINEZ"},
        ]
    },
    "COLOMBIA": {
        "items": [
            {"numero": 106, "nombre": "LUIS DÍAZ",       "tipo": "FF"},
            {"numero": 107, "nombre": _TEAM_CREST},
            {"numero": 108, "nombre": "JAMES RODRIGUEZ", "tipo": "IC"},
            {"numero": 109, "nombre": "CAMILO VARGAS"},
            {"numero": 110, "nombre": "DAVINSON SANCHEZ"},
            {"numero": 111, "nombre": "YERRY MINA"},
            {"numero": 112, "nombre": "DANIEL MUÑOZ"},
            {"numero": 113, "nombre": "JEFFERSON LERMA"},
            {"numero": 114, "nombre": "RICHARD RIOS"},
            {"numero": 115, "nombre": "JHON ARIAS"},
            {"numero": 116, "nombre": "CUCHO HERNANDEZ"},
            {"numero": 117, "nombre": "CARLOS CUESTA"},
        ]
    },
    "SPAIN": {
        "items": [
            {"numero": 442, "nombre": "LAMINE YAMAL",    "tipo": "FF"},
            {"numero": 443, "nombre": _TEAM_CREST},
            {"numero": 444, "nombre": "RODRI"},
            {"numero": 445, "nombre": "UNAI SIMON"},
            {"numero": 446, "nombre": "ROBIN LE NORMAND"},
            {"numero": 447, "nombre": "DEAN HUIJSEN"},
            {"numero": 448, "nombre": "MARC CUCURELLA"},
            {"numero": 449, "nombre": "MARTIN ZUBIMENDI"},
            {"numero": 450, "nombre": "PEDRI"},
            {"numero": 451, "nombre": "FABIAN RUIZ"},
            {"numero": 452, "nombre": "NICO WILLIAMS"},
            {"numero": 453, "nombre": "MIKEL OYARZABAL"},
        ]
    },
}

_OTROS = {
    "oficiales": {
        "category": "Official", "rarity": "Rare",
        "items": [
            {"numero": 624, "nombre": "OFFICIAL EMBLEM"},
            {"numero": 625, "nombre": "OFFICIAL MASCOT-MAPLE"},
            {"numero": 626, "nombre": "OFFICIAL MASCOT-CLUTCH"},
            {"numero": 627, "nombre": "OFFICIAL MASCOT-ZAYU"},
        ]
    },
    "eternos_22": {
        "category": "Eternal", "rarity": "Rare",
        "items": [
            {"numero": 628, "nombre": "DEFENDERS"},
            {"numero": 629, "nombre": "MIDFIELDERS"},
            {"numero": 630, "nombre": "FORWARDS"},
        ]
    },
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ensure_rarities(db):
    from app.domain.models.rarity_cat import RarityCat
    rarity_map = {}
    for name in ("Common", "Rare", "Epic", "Legendary"):
        rc = RarityCat.query.filter_by(name=name).first()
        if not rc:
            rc = RarityCat(name=name)
            db.session.add(rc)
            db.session.commit()
        rarity_map[name] = rc.rarityCatId
    return rarity_map


def _upsert(db, sticker_model, rarity_map, *, panini_code, name, team, category, rarity):
    existing = sticker_model.query.filter_by(paniniCode=str(panini_code)).first()
    if existing:
        return 0
    st = sticker_model(
        name=name,
        category=category,
        rarity=rarity,
        team=team,
        paniniCode=str(panini_code),
        raretyCatId=rarity_map[rarity],
    )
    db.session.add(st)
    return 1


# ---------------------------------------------------------------------------
# Main sync
# ---------------------------------------------------------------------------

def sync():
    from app import create_app
    from app.infrastructure.database import db
    from app.domain.models.sticker import Sticker

    app = create_app()
    with app.app_context():
        rarity_map = _ensure_rarities(db)
        added = 0

        # 1. Categorías especiales
        for _cat_key, cat_data in _ESPECIALES.items():
            for item in cat_data["items"]:
                added += _upsert(db, Sticker, rarity_map,
                                 panini_code=item["numero"],
                                 name=item["nombre"],
                                 team=item.get("pais", "WORLD"),
                                 category=cat_data["category"],
                                 rarity=cat_data["rarity"])

        # 2. Cartas por equipo
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
                added += _upsert(db, Sticker, rarity_map,
                                 panini_code=item["numero"],
                                 name=nombre,
                                 team=team_name,
                                 category=category,
                                 rarity=rarity)

        # 3. Otros items
        for _cat_key, cat_data in _OTROS.items():
            for item in cat_data["items"]:
                added += _upsert(db, Sticker, rarity_map,
                                 panini_code=item["numero"],
                                 name=item["nombre"],
                                 team="WORLD",
                                 category=cat_data["category"],
                                 rarity=cat_data["rarity"])

        db.session.commit()
        print(f"[JSON seed] {added} nuevas cartas insertadas.")

        # 4. Complementar con API football-data.org
        added_api = _sync_from_api(db, Sticker, rarity_map)
        print(f"[API seed]  {added_api} nuevas cartas de jugadores insertadas.")
        print(f"Total stickers en BD: {Sticker.query.count()}")


_LEGENDARIES = frozenset({
    "Lionel Messi", "Cristiano Ronaldo", "Kylian Mbappé", "Neymar Jr", "Lamine Yamal"
})
_EPICS = frozenset({
    "Vinicius Junior", "Jude Bellingham", "Harry Kane", "Erling Haaland",
    "Rodri", "Kevin De Bruyne", "Mohamed Salah", "Heung-Min Son",
})


def _get_player_rarity(p_name: str) -> str:
    if p_name in _LEGENDARIES:
        return "Legendary"
    if p_name in _EPICS:
        return "Epic"
    return "Common"


def _fetch_team_squad(api_url: str, team: dict, headers: dict) -> list:
    squad = team.get("squad") or []
    if squad:
        return squad
    try:
        import requests
        t_resp = requests.get(f"{api_url}/teams/{team['id']}", headers=headers, timeout=15)
        t_resp.raise_for_status()
        return t_resp.json().get("squad", [])
    except Exception:
        return []


def _sync_from_api(db, sticker_model, rarity_map) -> int:
    import os, requests
    api_url = os.environ.get("FOOTBALL_API_URL", "https://api.football-data.org/v4")
    api_key = os.environ.get("FOOTBALL_API_KEY", "")
    if not api_key:
        print("[API seed] FOOTBALL_API_KEY no configurada, saltando sync de API.")
        return 0

    headers = {"X-Auth-Token": api_key}
    added = 0

    try:
        resp = requests.get(f"{api_url}/competitions/WC/teams", headers=headers, timeout=15)
        resp.raise_for_status()
        teams = resp.json().get("teams", [])
    except Exception as e:
        print(f"[API seed] Error obteniendo equipos: {e}")
        return 0

    for team in teams:
        raw_name = team.get("shortName") or team.get("name", "UNKNOWN")
        team_name = raw_name.upper()  # normalise to uppercase so "Argentina" == "ARGENTINA"
        tla = team.get("tla", team_name[:3])

        # Skip teams already seeded from _EQUIPOS (they already have a "Team Crest" sticker)
        if sticker_model.query.filter_by(team=team_name, category="Team Crest").first():
            continue

        squad = _fetch_team_squad(api_url, team, headers)

        for idx, player in enumerate(squad):
            p_name = player.get("name", "")
            if not p_name:
                continue
            synthetic_code = f"{tla}-{player.get('id', idx)}"
            if sticker_model.query.filter_by(paniniCode=synthetic_code).first():
                continue

            rarity = _get_player_rarity(p_name)
            st = sticker_model(
                name=p_name,
                category="Player",
                rarity=rarity,
                team=team_name,
                paniniCode=synthetic_code,
                raretyCatId=rarity_map[rarity],
            )
            db.session.add(st)
            added += 1

        db.session.commit()

    return added


if __name__ == "__main__":
    sync()
