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
    "BRAZIL": {
        "items": [
            {"numero": 34, "nombre": "RAPHINHA", "tipo": "FF"},
            {"numero": 35, "nombre": _TEAM_CREST},
            {"numero": 36, "nombre": "VINICIUS JUNIOR", "tipo": "IC"},
            {"numero": 37, "nombre": "ALISSON"},
            {"numero": 38, "nombre": "DANILO"},
            {"numero": 39, "nombre": "MARQUINHOS"},
            {"numero": 40, "nombre": "EDER MILITÃO"},
            {"numero": 41, "nombre": "CASEMIRO"},
            {"numero": 42, "nombre": "BRUNO GUIMARães"},
            {"numero": 43, "nombre": "LUCAS PAQUETA"},
            {"numero": 44, "nombre": "RODRYGO"},
            {"numero": 45, "nombre": "ENDRICK"},
        ]
    },
    "URUGUAY": {
        "items": [
            {"numero": 46, "nombre": "FEDERICO VALVERDE", "tipo": "FF"},
            {"numero": 47, "nombre": _TEAM_CREST},
            {"numero": 48, "nombre": "DARWIN NUÑEZ", "tipo": "IC"},
            {"numero": 49, "nombre": "SERGIO ROCHET"},
            {"numero": 50, "nombre": "NAHITAN NANDEZ"},
            {"numero": 51, "nombre": "RONALD ARAUJO"},
            {"numero": 52, "nombre": "JOSE GIMENEZ"},
            {"numero": 53, "nombre": "MATHIAS OLIVERA"},
            {"numero": 54, "nombre": "NICOLAS DE LA CRUZ"},
            {"numero": 55, "nombre": "RODRIGO BENTANCUR"},
            {"numero": 56, "nombre": "MAXIMILIANO ARAUJO"},
            {"numero": 57, "nombre": "FACUNDO PELLISTRI"},
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
    "ECUADOR": {
        "items": [
            {"numero": 118, "nombre": "MOISES CAICEDO", "tipo": "FF"},
            {"numero": 119, "nombre": _TEAM_CREST},
            {"numero": 120, "nombre": "ENNER VALENCIA", "tipo": "IC"},
            {"numero": 121, "nombre": "HERNAN GALINDEZ"},
            {"numero": 122, "nombre": "ANGELO PRECIADO"},
            {"numero": 123, "nombre": "FELIX TORRES"},
            {"numero": 124, "nombre": "PIERO HINCAPIÉ"},
            {"numero": 125, "nombre": "WILLIAN PACHO"},
            {"numero": 126, "nombre": "PERVIS ESTUPIÑAN"},
            {"numero": 127, "nombre": "ALAN FRANCO"},
            {"numero": 128, "nombre": "KENDRAY PAEZ"},
            {"numero": 129, "nombre": "KEVIN RODRIGUEZ"},
        ]
    },
    "VENEZUELA": {
        "items": [
            {"numero": 130, "nombre": "SALOMON RONDON", "tipo": "FF"},
            {"numero": 131, "nombre": _TEAM_CREST},
            {"numero": 132, "nombre": "YEFERSON SOTELDO", "tipo": "IC"},
            {"numero": 133, "nombre": "RAFAEL ROMO"},
            {"numero": 134, "nombre": "ALEXANDER GONZALEZ"},
            {"numero": 135, "nombre": "YORDAN OSORIO"},
            {"numero": 136, "nombre": "WILKER ANGEL"},
            {"numero": 137, "nombre": "MIGUEL NAVARRO"},
            {"numero": 138, "nombre": "JOSE MARTINEZ"},
            {"numero": 139, "nombre": "YANGEL HERRERA"},
            {"numero": 140, "nombre": "JEFFERSON SAVARINO"},
            {"numero": 141, "nombre": "DARWIN MACHIS"},
        ]
    },
    "USA": {
        "items": [
            {"numero": 142, "nombre": "CHRISTIAN PULISIC", "tipo": "FF"},
            {"numero": 143, "nombre": _TEAM_CREST},
            {"numero": 144, "nombre": "WESTON MCKENNIE", "tipo": "IC"},
            {"numero": 145, "nombre": "MATT TURNER"},
            {"numero": 146, "nombre": "SERGINO DEST"},
            {"numero": 147, "nombre": "CHRIS RICHARDS"},
            {"numero": 148, "nombre": "TIM REAM"},
            {"numero": 149, "nombre": "ANTONEE ROBINSON"},
            {"numero": 150, "nombre": "TYLER ADAMS"},
            {"numero": 151, "nombre": "YUNUS MUSAH"},
            {"numero": 152, "nombre": "GIO REYNA"},
            {"numero": 153, "nombre": "FOLARIN BALOGUN"},
        ]
    },
    "MEXICO": {
        "items": [
            {"numero": 154, "nombre": "SANTIAGO GIMÉNEZ", "tipo": "FF"},
            {"numero": 155, "nombre": _TEAM_CREST},
            {"numero": 156, "nombre": "EDSON ALVAREZ", "tipo": "IC"},
            {"numero": 157, "nombre": "GUILLERMO OCHOA"},
            {"numero": 158, "nombre": "JORGE SANCHEZ"},
            {"numero": 159, "nombre": "CESAR MONTES"},
            {"numero": 160, "nombre": "JOHAN VASQUEZ"},
            {"numero": 161, "nombre": "JESUS GALLARDO"},
            {"numero": 162, "nombre": "LUIS ROMO"},
            {"numero": 163, "nombre": "ORBELIN PINEDA"},
            {"numero": 164, "nombre": "HIRVING LOZANO"},
            {"numero": 165, "nombre": "JULIAN QUIÑONES"},
        ]
    },
    "CANADA": {
        "items": [
            {"numero": 166, "nombre": "ALPHONSO DAVIES", "tipo": "FF"},
            {"numero": 167, "nombre": _TEAM_CREST},
            {"numero": 168, "nombre": "JONATHAN DAVID", "tipo": "IC"},
            {"numero": 169, "nombre": "MAXIME CREPEAU"},
            {"numero": 170, "nombre": "ALISTAIR JOHNSTON"},
            {"numero": 171, "nombre": "DEREK CORNELIUS"},
            {"numero": 172, "nombre": "KAMAL MILLER"},
            {"numero": 173, "nombre": "STEPHEN EUSTAQUIO"},
            {"numero": 174, "nombre": "ISMAEL KONE"},
            {"numero": 175, "nombre": "TAJON BUCHANAN"},
            {"numero": 176, "nombre": "CYLE LARIN"},
            {"numero": 177, "nombre": "JACOB SHAFFELBURG"},
        ]
    },
    "COSTA RICA": {
        "items": [
            {"numero": 178, "nombre": "JOEL CAMPBELL", "tipo": "FF"},
            {"numero": 179, "nombre": _TEAM_CREST},
            {"numero": 180, "nombre": "KEYLOR NAVAS", "tipo": "IC"},
            {"numero": 181, "nombre": "FRANCISCO CALVO"},
            {"numero": 182, "nombre": "JUAN PABLO VARGAS"},
            {"numero": 183, "nombre": "KENDALL WASTON"},
            {"numero": 184, "nombre": "CELSO BORGES"},
            {"numero": 185, "nombre": "YELTSIN TEJEDA"},
            {"numero": 186, "nombre": "JEWISON BENNETTE"},
            {"numero": 187, "nombre": "ANTHONY CONTRERAS"},
            {"numero": 188, "nombre": "MANFRED UGALDE"},
            {"numero": 189, "nombre": "BRANDON AGUILERA"},
        ]
    },
    "PANAMA": {
        "items": [
            {"numero": 190, "nombre": "ADALBERTO CARRASQUILLA", "tipo": "FF"},
            {"numero": 191, "nombre": _TEAM_CREST},
            {"numero": 192, "nombre": "ANIBAL GODOY", "tipo": "IC"},
            {"numero": 193, "nombre": "ORLANDO MOSQUERA"},
            {"numero": 194, "nombre": "MICHAEL MURILLO"},
            {"numero": 195, "nombre": "FIDEL ESCOBAR"},
            {"numero": 196, "nombre": "ANDRES ANDRADE"},
            {"numero": 197, "nombre": "ERIC DAVIS"},
            {"numero": 198, "nombre": "EDGAR BARCENAS"},
            {"numero": 199, "nombre": "JOSE LUIS RODRIGUEZ"},
            {"numero": 200, "nombre": "ISMAEL DIAZ"},
            {"numero": 201, "nombre": "JOSE FAJARDO"},
        ]
    },
    "JAMAICA": {
        "items": [
            {"numero": 202, "nombre": "LEON BAILEY", "tipo": "FF"},
            {"numero": 203, "nombre": _TEAM_CREST},
            {"numero": 204, "nombre": "MICHAIL ANTONIO", "tipo": "IC"},
            {"numero": 205, "nombre": "ANDRE BLAKE"},
            {"numero": 206, "nombre": "DEXTER LEMBIKISA"},
            {"numero": 207, "nombre": "DAMION LOWE"},
            {"numero": 208, "nombre": "ETHAN PINNOCK"},
            {"numero": 209, "nombre": "AMARII BELL"},
            {"numero": 210, "nombre": "JOEL LATIBEAUDIERE"},
            {"numero": 211, "nombre": "KASEY PALMER"},
            {"numero": 212, "nombre": "DEMARAI GRAY"},
            {"numero": 213, "nombre": "SHAMAR NICHOLSON"},
        ]
    },
    "FRANCE": {
        "items": [
            {"numero": 214, "nombre": "KYLIAN MBAPPE", "tipo": "FF"},
            {"numero": 215, "nombre": _TEAM_CREST},
            {"numero": 216, "nombre": "ANTOINE GRIEZMANN", "tipo": "IC"},
            {"numero": 217, "nombre": "MIKE MAIGNAN"},
            {"numero": 218, "nombre": "JULES KOUNDE"},
            {"numero": 219, "nombre": "WILLIAM SALIBA"},
            {"numero": 220, "nombre": "DAYOT UPAMECANO"},
            {"numero": 221, "nombre": "THEO HERNANDEZ"},
            {"numero": 222, "nombre": "AURELIEN TCHOUAMÉNI"},
            {"numero": 223, "nombre": "ADRIEN RABIOT"},
            {"numero": 224, "nombre": "N'GOLO KANTE"},
            {"numero": 225, "nombre": "OUSMANE DEMBELE"},
        ]
    },
    "GERMANY": {
        "items": [
            {"numero": 226, "nombre": "FLORIAN WIRTZ", "tipo": "FF"},
            {"numero": 227, "nombre": _TEAM_CREST},
            {"numero": 228, "nombre": "JAMAL MUSIALA", "tipo": "IC"},
            {"numero": 229, "nombre": "MARC-ANDRE TER STEGEN"},
            {"numero": 230, "nombre": "JOSHUA KIMMICH"},
            {"numero": 231, "nombre": "ANTONIO RÜDIGER"},
            {"numero": 232, "nombre": "JONATHAN TAH"},
            {"numero": 233, "nombre": "DAVID RAUM"},
            {"numero": 234, "nombre": "MAXIMILIAN MITTELSTÄDT"},
            {"numero": 235, "nombre": "ILKAY GÜNDOGAN"},
            {"numero": 236, "nombre": "LEROY SANE"},
            {"numero": 237, "nombre": "KAI HAVERTZ"},
        ]
    },
    "ENGLAND": {
        "items": [
            {"numero": 238, "nombre": "JUDE BELLINGHAM", "tipo": "FF"},
            {"numero": 239, "nombre": _TEAM_CREST},
            {"numero": 240, "nombre": "HARRY KANE", "tipo": "IC"},
            {"numero": 241, "nombre": "JORDAN PICKFORD"},
            {"numero": 242, "nombre": "KYLE WALKER"},
            {"numero": 243, "nombre": "JOHN STONES"},
            {"numero": 244, "nombre": "MARC GUEHI"},
            {"numero": 245, "nombre": "KIERAN TRIPPIER"},
            {"numero": 246, "nombre": "DECLAN RICE"},
            {"numero": 247, "nombre": "TRENT ALEXANDER-ARNOLD"},
            {"numero": 248, "nombre": "BUKAYO SAKA"},
            {"numero": 249, "nombre": "PHIL FODEN"},
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
    "PORTUGAL": {
        "items": [
            {"numero": 454, "nombre": "CRISTIANO RONALDO", "tipo": "FF"},
            {"numero": 455, "nombre": _TEAM_CREST},
            {"numero": 456, "nombre": "BRUNO FERNANDES", "tipo": "IC"},
            {"numero": 457, "nombre": "DIOGO COSTA"},
            {"numero": 458, "nombre": "JOAO CANCELO"},
            {"numero": 459, "nombre": "RUBEN DIAS"},
            {"numero": 460, "nombre": "PEPE"},
            {"numero": 461, "nombre": "NUNO MENDES"},
            {"numero": 462, "nombre": "JOAO PALHINHA"},
            {"numero": 463, "nombre": "VITINHA"},
            {"numero": 464, "nombre": "BERNARDO SILVA"},
            {"numero": 465, "nombre": "RAFAEL LEAO"},
        ]
    },
    "NETHERLANDS": {
        "items": [
            {"numero": 466, "nombre": "CODY GAKPO", "tipo": "FF"},
            {"numero": 467, "nombre": _TEAM_CREST},
            {"numero": 468, "nombre": "VIRGIL VAN DIJK", "tipo": "IC"},
            {"numero": 469, "nombre": "BART VERBRUGGEN"},
            {"numero": 470, "nombre": "DENZEL DUMFRIES"},
            {"numero": 471, "nombre": "MATTHIJS DE LIGT"},
            {"numero": 472, "nombre": "NATHAN AKE"},
            {"numero": 473, "nombre": "DALEY BLIND"},
            {"numero": 474, "nombre": "FRENKIE DE JONG"},
            {"numero": 475, "nombre": "TIJJANI REIJNDERS"},
            {"numero": 476, "nombre": "XAVI SIMONS"},
            {"numero": 477, "nombre": "WOUT WEGHORST"},
        ]
    },
    "ITALY": {
        "items": [
            {"numero": 478, "nombre": "NICOLO BARELLA", "tipo": "FF"},
            {"numero": 479, "nombre": _TEAM_CREST},
            {"numero": 480, "nombre": "FEDERICO CHIESA", "tipo": "IC"},
            {"numero": 481, "nombre": "GIANLUIGI DONNARUMMA"},
            {"numero": 482, "nombre": "GIOVANNI DI LORENZO"},
            {"numero": 483, "nombre": "ALESSANDRO BASTONI"},
            {"numero": 484, "nombre": "RICCARDO CALAFIORI"},
            {"numero": 485, "nombre": "FEDERICO DIMARCO"},
            {"numero": 486, "nombre": "JORGINHO"},
            {"numero": 487, "nombre": "LORENZO PELLEGRINI"},
            {"numero": 488, "nombre": "DAVIDE FRATTESI"},
            {"numero": 489, "nombre": "GIANLUCA SCAMACCA"},
        ]
    },
    "CROATIA": {
        "items": [
            {"numero": 490, "nombre": "LUKA MODRIC", "tipo": "FF"},
            {"numero": 491, "nombre": _TEAM_CREST},
            {"numero": 492, "nombre": "JOSKO GVARDIOL", "tipo": "IC"},
            {"numero": 493, "nombre": "DOMINIK LIVAKOVIC"},
            {"numero": 494, "nombre": "JOSIP JURANOVIC"},
            {"numero": 495, "nombre": "JOSIP SUTALO"},
            {"numero": 496, "nombre": "BORNA SOSA"},
            {"numero": 497, "nombre": "MATEO KOVACIC"},
            {"numero": 498, "nombre": "MARCELO BROZOVIC"},
            {"numero": 499, "nombre": "MARIO PASALIC"},
            {"numero": 500, "nombre": "LOVRO MAJER"},
            {"numero": 501, "nombre": "ANDREJ KRAMARIC"},
        ]
    },
    "BELGIUM": {
        "items": [
            {"numero": 502, "nombre": "KEVIN DE BRUYNE", "tipo": "FF"},
            {"numero": 503, "nombre": _TEAM_CREST},
            {"numero": 504, "nombre": "ROMELU LUKAKU", "tipo": "IC"},
            {"numero": 505, "nombre": "KOEN CASTEELS"},
            {"numero": 506, "nombre": "TIMOTHY CASTAGNE"},
            {"numero": 507, "nombre": "WOUT FAES"},
            {"numero": 508, "nombre": "JAN VERTONGHEN"},
            {"numero": 509, "nombre": "ARTHUR THEATE"},
            {"numero": 510, "nombre": "AMADOU ONANA"},
            {"numero": 511, "nombre": "OUREL MANGALA"},
            {"numero": 512, "nombre": "JEREMY DOKU"},
            {"numero": 513, "nombre": "LEANDRO TROSSARD"},
        ]
    },
    "SWITZERLAND": {
        "items": [
            {"numero": 514, "nombre": "GRANIT XHAKA", "tipo": "FF"},
            {"numero": 515, "nombre": _TEAM_CREST},
            {"numero": 516, "nombre": "MANUEL AKANJI", "tipo": "IC"},
            {"numero": 517, "nombre": "YANN SOMMER"},
            {"numero": 518, "nombre": "SILVAN WIDMER"},
            {"numero": 519, "nombre": "NICO ELVEDI"},
            {"numero": 520, "nombre": "RICARDO RODRIGUEZ"},
            {"numero": 521, "nombre": "REMO FREULER"},
            {"numero": 522, "nombre": "MICHEL AEBISCHER"},
            {"numero": 523, "nombre": "XHERDAN SHAQIRI"},
            {"numero": 524, "nombre": "DAN NDOYE"},
            {"numero": 525, "nombre": "BREEL EMBOLO"},
        ]
    },
    "DENMARK": {
        "items": [
            {"numero": 526, "nombre": "CHRISTIAN ERIKSEN", "tipo": "FF"},
            {"numero": 527, "nombre": _TEAM_CREST},
            {"numero": 528, "nombre": "RASMUS HOJLUND", "tipo": "IC"},
            {"numero": 529, "nombre": "KASPER SCHMEICHEL"},
            {"numero": 530, "nombre": "JOACHIM ANDERSEN"},
            {"numero": 531, "nombre": "SIMON KJAER"},
            {"numero": 532, "nombre": "ANDREAS CHRISTENSEN"},
            {"numero": 533, "nombre": "JOAKIM MAEHLE"},
            {"numero": 534, "nombre": "PIERRE-EMILE HOJBJERG"},
            {"numero": 535, "nombre": "THOMAS DELANEY"},
            {"numero": 536, "nombre": "JONAS WIND"},
            {"numero": 537, "nombre": "YUSSUF POULSEN"},
        ]
    },
    "SWEDEN": {
        "items": [
            {"numero": 538, "nombre": "ALEXANDER ISAK", "tipo": "FF"},
            {"numero": 539, "nombre": _TEAM_CREST},
            {"numero": 540, "nombre": "DEJAN KULUSEVSKI", "tipo": "IC"},
            {"numero": 541, "nombre": "ROBIN OLSEN"},
            {"numero": 542, "nombre": "EMIL KRAFTH"},
            {"numero": 543, "nombre": "VICTOR LINDELOF"},
            {"numero": 544, "nombre": "ISAK HIEN"},
            {"numero": 545, "nombre": "LUDWIG AUGUSTINSSON"},
            {"numero": 546, "nombre": "MATTIAS SVANBERG"},
            {"numero": 547, "nombre": "JENS CAJUSTE"},
            {"numero": 548, "nombre": "EMIL FORSBERG"},
            {"numero": 549, "nombre": "ANTHONY ELANGA"},
        ]
    },
    "POLAND": {
        "items": [
            {"numero": 550, "nombre": "ROBERT LEWANDOWSKI", "tipo": "FF"},
            {"numero": 551, "nombre": _TEAM_CREST},
            {"numero": 552, "nombre": "PIOTR ZIELINSKI", "tipo": "IC"},
            {"numero": 553, "nombre": "WOJCIECH SZCZESNY"},
            {"numero": 554, "nombre": "MATTY CASH"},
            {"numero": 555, "nombre": "JAN BEDNAREK"},
            {"numero": 556, "nombre": "JAKUB KIWIOR"},
            {"numero": 557, "nombre": "PRZEMYSLAW FRANKOWSKI"},
            {"numero": 558, "nombre": "SEBASTIAN SZYMANSKI"},
            {"numero": 559, "nombre": "KAROL LINETTY"},
            {"numero": 560, "nombre": "NICOLA ZALEWSKI"},
            {"numero": 561, "nombre": "KAROL SWIDERSKI"},
        ]
    },
    "SERBIA": {
        "items": [
            {"numero": 562, "nombre": "DUSAN VLAHOVIC", "tipo": "FF"},
            {"numero": 563, "nombre": _TEAM_CREST},
            {"numero": 564, "nombre": "ALEKSANDAR MITROVIC", "tipo": "IC"},
            {"numero": 565, "nombre": "VANJA MILINKOVIC-SAVIC"},
            {"numero": 566, "nombre": "NIKOLA MILENKOVIC"},
            {"numero": 567, "nombre": "MILOS VELJKOVIC"},
            {"numero": 568, "nombre": "STRAHINJA PAVLOVIC"},
            {"numero": 569, "nombre": "ANDRIJA ZIVKOVIC"},
            {"numero": 570, "nombre": "SERGEJ MILINKOVIC-SAVIC"},
            {"numero": 571, "nombre": "SASA LUKIC"},
            {"numero": 572, "nombre": "FILIP KOSTIC"},
            {"numero": 573, "nombre": "DUSAN TADIC"},
        ]
    },
    "MOROCCO": {
        "items": [
            {"numero": 574, "nombre": "ACHRAF HAKIMI", "tipo": "FF"},
            {"numero": 575, "nombre": _TEAM_CREST},
            {"numero": 576, "nombre": "HAKIM ZIYECH", "tipo": "IC"},
            {"numero": 577, "nombre": "YASSINE BOUNOU"},
            {"numero": 578, "nombre": "NAYEF AGUERD"},
            {"numero": 579, "nombre": "ROMAIN SAISS"},
            {"numero": 580, "nombre": "NOUSSAIR MAZRAOUI"},
            {"numero": 581, "nombre": "SOFYAN AMRABAT"},
            {"numero": 582, "nombre": "AZZEDINE OUNAHI"},
            {"numero": 583, "nombre": "SELIM AMALLAH"},
            {"numero": 584, "nombre": "YOUSSEF EN-NESYRI"},
            {"numero": 585, "nombre": "BRAHIM DIAZ"},
        ]
    },
    "SENEGAL": {
        "items": [
            {"numero": 586, "nombre": "SADIO MANE", "tipo": "FF"},
            {"numero": 587, "nombre": _TEAM_CREST},
            {"numero": 588, "nombre": "KALIDOU KOULIBALY", "tipo": "IC"},
            {"numero": 589, "nombre": "EDOUARD MENDY"},
            {"numero": 590, "nombre": "YOUSSOUF SABALY"},
            {"numero": 591, "nombre": "MOUSSA NIAKHATE"},
            {"numero": 592, "nombre": "ABDOU DIALLO"},
            {"numero": 593, "nombre": "ISMAIL JAKOBS"},
            {"numero": 594, "nombre": "NAMPALYS MENDY"},
            {"numero": 595, "nombre": "IDRISSA GUEYE"},
            {"numero": 596, "nombre": "PAPE MATAR SARR"},
            {"numero": 597, "nombre": "ISMAILA SARR"},
        ]
    },
    "EGYPT": {
        "items": [
            {"numero": 598, "nombre": "MOHAMED SALAH", "tipo": "FF"},
            {"numero": 599, "nombre": _TEAM_CREST},
            {"numero": 600, "nombre": "OMAR MARMOUSH", "tipo": "IC"},
            {"numero": 601, "nombre": "MOHAMED EL SHENAWY"},
            {"numero": 602, "nombre": "MOHAMED HANY"},
            {"numero": 603, "nombre": "AHMED HEGAZY"},
            {"numero": 604, "nombre": "MOHAMED ABDELMONEM"},
            {"numero": 605, "nombre": "AHMED FATOUH"},
            {"numero": 606, "nombre": "MOHAMED ELNENY"},
            {"numero": 607, "nombre": "MARWAN ATTIA"},
            {"numero": 608, "nombre": "MAHMOUD TREZEGUET"},
            {"numero": 609, "nombre": "MOSTAFA MOHAMED"},
        ]
    },
    "NIGERIA": {
        "items": [
            {"numero": 610, "nombre": "VICTOR OSIMHEN", "tipo": "FF"},
            {"numero": 611, "nombre": _TEAM_CREST},
            {"numero": 612, "nombre": "ADEMOLA LOOKMAN", "tipo": "IC"},
            {"numero": 613, "nombre": "STANLEY NWABALI"},
            {"numero": 614, "nombre": "OLA AINA"},
            {"numero": 615, "nombre": "WILLIAM TROOST-EKONG"},
            {"numero": 616, "nombre": "SEMI AJAYI"},
            {"numero": 617, "nombre": "ZAIDU SANUSI"},
            {"numero": 618, "nombre": "FRANK ONYEKA"},
            {"numero": 619, "nombre": "ALEX IWOBI"},
            {"numero": 620, "nombre": "SAMUEL CHUKWUEZE"},
            {"numero": 621, "nombre": "KELECHI IHEANACHO"},
        ]
    },
    "CAMEROON": {
        "items": [
            {"numero": 622, "nombre": "VINCENT ABOUBAKAR", "tipo": "FF"},
            {"numero": 623, "nombre": _TEAM_CREST},
            {"numero": 624, "nombre": "ANDRE ONANA", "tipo": "IC"},
            {"numero": 625, "nombre": "COLLINS FAI"},
            {"numero": 626, "nombre": "JEAN-CHARLES CASTELLETTO"},
            {"numero": 627, "nombre": "CHRISTOPHER WOOH"},
            {"numero": 628, "nombre": "NOUHOU TOLO"},
            {"numero": 629, "nombre": "FRANK ANGUISSA"},
            {"numero": 630, "nombre": "OLIVIER NTCHAM"},
            {"numero": 631, "nombre": "KARL TOKO EKAMBI"},
            {"numero": 632, "nombre": "BRYAN MBEUMO"},
            {"numero": 633, "nombre": "ERIC MAXIM CHOUPO-MOTING"},
        ]
    },
    "ALGERIA": {
        "items": [
            {"numero": 634, "nombre": "RIYAD MAHREZ", "tipo": "FF"},
            {"numero": 635, "nombre": _TEAM_CREST},
            {"numero": 636, "nombre": "ISMAEL BENNACER", "tipo": "IC"},
            {"numero": 637, "nombre": "ANTHONY MANDREA"},
            {"numero": 638, "nombre": "YOUCEF ATAL"},
            {"numero": 639, "nombre": "AISSA MANDI"},
            {"numero": 640, "nombre": "RAMY BENSEBAINI"},
            {"numero": 641, "nombre": "RAYAN AIT-NOURI"},
            {"numero": 642, "nombre": "NABIL BENTALEB"},
            {"numero": 643, "nombre": "RAMIZ ZERROUKI"},
            {"numero": 644, "nombre": "FARES CHAIBI"},
            {"numero": 645, "nombre": "BAGHDAD BOUNEDJAH"},
        ]
    },
    "IVORY COAST": {
        "items": [
            {"numero": 646, "nombre": "SEBASTIEN HALLER", "tipo": "FF"},
            {"numero": 647, "nombre": _TEAM_CREST},
            {"numero": 648, "nombre": "FRANCK KESSIE", "tipo": "IC"},
            {"numero": 649, "nombre": "YAHIA FOFANA"},
            {"numero": 650, "nombre": "SERGE AURIER"},
            {"numero": 651, "nombre": "ODILON KOSSONOU"},
            {"numero": 652, "nombre": "EVAN NDICKA"},
            {"numero": 653, "nombre": "GHISLAIN KONAN"},
            {"numero": 654, "nombre": "IBRAHIM SANGARE"},
            {"numero": 655, "nombre": "SEKO FOFANA"},
            {"numero": 656, "nombre": "MAX GRADEL"},
            {"numero": 657, "nombre": "SIMON ADINGRA"},
        ]
    },
    "GHANA": {
        "items": [
            {"numero": 658, "nombre": "MOHAMMED KUDUS", "tipo": "FF"},
            {"numero": 659, "nombre": _TEAM_CREST},
            {"numero": 660, "nombre": "THOMAS PARTEY", "tipo": "IC"},
            {"numero": 661, "nombre": "LAWRENCE ATI-ZIGI"},
            {"numero": 662, "nombre": "ALIDU SEIDU"},
            {"numero": 663, "nombre": "ALEXANDER DJIKU"},
            {"numero": 664, "nombre": "MOHAMMED SALISU"},
            {"numero": 665, "nombre": "GIDEON MENSAH"},
            {"numero": 666, "nombre": "SALIS ABDUL SAMED"},
            {"numero": 667, "nombre": "MAJEED ASHIMERU"},
            {"numero": 668, "nombre": "JORDAN AYEW"},
            {"numero": 669, "nombre": "INAKI WILLIAMS"},
        ]
    },
    "MALI": {
        "items": [
            {"numero": 670, "nombre": "YVES BISSOUMA", "tipo": "FF"},
            {"numero": 671, "nombre": _TEAM_CREST},
            {"numero": 672, "nombre": "AMADOU HAIDARA", "tipo": "IC"},
            {"numero": 673, "nombre": "DJIGUI DIARRA"},
            {"numero": 674, "nombre": "HAMARI TRAORE"},
            {"numero": 675, "nombre": "BOUBACAR KOUYATE"},
            {"numero": 676, "nombre": "SIKOU NIAKATE"},
            {"numero": 677, "nombre": "AMADOU DANTE"},
            {"numero": 678, "nombre": "DIADIE SAMASSEKOU"},
            {"numero": 679, "nombre": "MOHAMED CAMARA"},
            {"numero": 680, "nombre": "KAMORY DOUMBIA"},
            {"numero": 681, "nombre": "LASSINE SINAYOKO"},
        ]
    },
    "JAPAN": {
        "items": [
            {"numero": 682, "nombre": "TAKEFUSA KUBO", "tipo": "FF"},
            {"numero": 683, "nombre": _TEAM_CREST},
            {"numero": 684, "nombre": "KAORU MITOMA", "tipo": "IC"},
            {"numero": 685, "nombre": "ZION SUZUKI"},
            {"numero": 686, "nombre": "YUKINARI SUGAWARA"},
            {"numero": 687, "nombre": "KO ITAKURA"},
            {"numero": 688, "nombre": "TAKEHIRO TOMIYASU"},
            {"numero": 689, "nombre": "HIROKI ITO"},
            {"numero": 690, "nombre": "WATARU ENDO"},
            {"numero": 691, "nombre": "HIDEMASA MORITA"},
            {"numero": 692, "nombre": "TAKUMI MINAMINO"},
            {"numero": 693, "nombre": "AYASE UEDA"},
        ]
    },
    "IRAN": {
        "items": [
            {"numero": 694, "nombre": "MEHDI TAREMI", "tipo": "FF"},
            {"numero": 695, "nombre": _TEAM_CREST},
            {"numero": 696, "nombre": "SARDAR AZMOUN", "tipo": "IC"},
            {"numero": 697, "nombre": "ALIREZA BEIRANVAND"},
            {"numero": 698, "nombre": "RAMIN REZAEIAN"},
            {"numero": 699, "nombre": "HOSSEIN KANAANI"},
            {"numero": 700, "nombre": "SHOJA KHALILZADEH"},
            {"numero": 701, "nombre": "EHSAN HAJSAFI"},
            {"numero": 702, "nombre": "SAEID EZATOLAHI"},
            {"numero": 703, "nombre": "SAMAN GHODDOS"},
            {"numero": 704, "nombre": "ALIREZA JAHANBAKHSH"},
            {"numero": 705, "nombre": "MOHAMMAD MOHEBI"},
        ]
    },
    "SOUTH KOREA": {
        "items": [
            {"numero": 706, "nombre": "HEUNG-MIN SON", "tipo": "FF"},
            {"numero": 707, "nombre": _TEAM_CREST},
            {"numero": 708, "nombre": "MIN-JAE KIM", "tipo": "IC"},
            {"numero": 709, "nombre": "SEUNG-GYU KIM"},
            {"numero": 710, "nombre": "YOUNG-WOO SEOL"},
            {"numero": 711, "nombre": "SEUNG-HYUN JUNG"},
            {"numero": 712, "nombre": "YOUNG-GWON KIM"},
            {"numero": 713, "nombre": "JIN-SU KIM"},
            {"numero": 714, "nombre": "IN-BEOM HWANG"},
            {"numero": 715, "nombre": "YONG-WOO PARK"},
            {"numero": 716, "nombre": "KANG-IN LEE"},
            {"numero": 717, "nombre": "GUE-SUNG CHO"},
        ]
    },
    "AUSTRALIA": {
        "items": [
            {"numero": 718, "nombre": "JACK IRVINE", "tipo": "FF"},
            {"numero": 719, "nombre": _TEAM_CREST},
            {"numero": 720, "nombre": "MATHEW RYAN", "tipo": "IC"},
            {"numero": 721, "nombre": "NATHANIEL ATKINSON"},
            {"numero": 722, "nombre": "HARRY SOUTTAR"},
            {"numero": 723, "nombre": "KYE ROWLES"},
            {"numero": 724, "nombre": "AZIZ BEHICH"},
            {"numero": 725, "nombre": "KEANU BACCUS"},
            {"numero": 726, "nombre": "JACKSON IRVINE"},
            {"numero": 727, "nombre": "CRAIG GOODWIN"},
            {"numero": 728, "nombre": "RILEY MCGREE"},
            {"numero": 729, "nombre": "MITCHELL DUKE"},
        ]
    },
    "SAUDI ARABIA": {
        "items": [
            {"numero": 730, "nombre": "SALEM AL-DAWSARI", "tipo": "FF"},
            {"numero": 731, "nombre": _TEAM_CREST},
            {"numero": 732, "nombre": "SALEH AL-SHEHRI", "tipo": "IC"},
            {"numero": 733, "nombre": "MOHAMMED AL-OWAIS"},
            {"numero": 734, "nombre": "SAUD ABDULHAMID"},
            {"numero": 735, "nombre": "HASSAN TAMBAKTI"},
            {"numero": 736, "nombre": "ALI AL-BULAIHI"},
            {"numero": 737, "nombre": "YASSER AL-SHAHRANI"},
            {"numero": 738, "nombre": "MOHAMED KANNO"},
            {"numero": 739, "nombre": "ABDULLAH AL-KHAIBARI"},
            {"numero": 740, "nombre": "FIARAS AL-BURAIKAN"},
            {"numero": 741, "nombre": "ABDULRAHMAN GHAREEB"},
        ]
    },
    "QATAR": {
        "items": [
            {"numero": 742, "nombre": "AKRAM AFIF", "tipo": "FF"},
            {"numero": 743, "nombre": _TEAM_CREST},
            {"numero": 744, "nombre": "ALMOEZ ALI", "tipo": "IC"},
            {"numero": 745, "nombre": "MESHAAL BARSHAM"},
            {"numero": 746, "nombre": "PEDRO MIGUEL"},
            {"numero": 747, "nombre": "TAREK SALMAN"},
            {"numero": 748, "nombre": "BOUALEM KHOUKHI"},
            {"numero": 749, "nombre": "LUCAS MENDES"},
            {"numero": 750, "nombre": "JASSIM GABER"},
            {"numero": 751, "nombre": "AHMED FATHI"},
            {"numero": 752, "nombre": "HASSAN AL-HAYDOS"},
            {"numero": 753, "nombre": "YUSUF ABDURISAG"},
        ]
    },
    "IRAQ": {
        "items": [
            {"numero": 754, "nombre": "AYMEN HUSSEIN", "tipo": "FF"},
            {"numero": 755, "nombre": _TEAM_CREST},
            {"numero": 756, "nombre": "ALI JASSIM", "tipo": "IC"},
            {"numero": 757, "nombre": "JALAL HASSAN"},
            {"numero": 758, "nombre": "HUSSEIN ALI"},
            {"numero": 759, "nombre": "SAAD NATIQ"},
            {"numero": 760, "nombre": "REBIN SULAKA"},
            {"numero": 761, "nombre": "MERCHAS DOSKI"},
            {"numero": 762, "nombre": "OSAMA RASHID"},
            {"numero": 763, "nombre": "AMIR AL-AMMARI"},
            {"numero": 764, "nombre": "IBRAHIM BAYESH"},
            {"numero": 765, "nombre": "ZIDANE IQBAL"},
        ]
    },
    "UZBEKISTAN": {
        "items": [
            {"numero": 766, "nombre": "ELDOR SHOMURODOV", "tipo": "FF"},
            {"numero": 767, "nombre": _TEAM_CREST},
            {"numero": 768, "nombre": "ABBOSBEK FAYZULLAEV", "tipo": "IC"},
            {"numero": 769, "nombre": "UTKIR YUSUPOV"},
            {"numero": 770, "nombre": "HOJIRO MATOV"},
            {"numero": 771, "nombre": "RUSTAM ASHURMATOV"},
            {"numero": 772, "nombre": "ABDULLA ABDULLAEV"},
            {"numero": 773, "nombre": "FARRUKH SAYFIEV"},
            {"numero": 774, "nombre": "ODILJON HAMROBEKOV"},
            {"numero": 775, "nombre": "OTABEK SHUKUROV"},
            {"numero": 776, "nombre": "JALOLIDDIN MASHARIPOV"},
            {"numero": 777, "nombre": "OSTON URUNOV"},
        ]
    },
    "UAE": {
        "items": [
            {"numero": 778, "nombre": "ALI MABKHOUT", "tipo": "FF"},
            {"numero": 779, "nombre": _TEAM_CREST},
            {"numero": 780, "nombre": "FABIO LIMA", "tipo": "IC"},
            {"numero": 781, "nombre": "KHALID EISA"},
            {"numero": 782, "nombre": "KHALID AL-HASHEMI"},
            {"numero": 783, "nombre": "KHALIFA AL-HAMMADI"},
            {"numero": 784, "nombre": "BADER NASSER"},
            {"numero": 785, "nombre": "ABDULLA IDREES"},
            {"numero": 786, "nombre": "ALI SALMEEN"},
            {"numero": 787, "nombre": "YAHYA NADER"},
            {"numero": 788, "nombre": "TAHNOON AL-ZAABI"},
            {"numero": 789, "nombre": "CAIO CANEDO"},
        ]
    },
    "NEW ZEALAND": {
        "items": [
            {"numero": 790, "nombre": "CHRIS WOOD", "tipo": "FF"},
            {"numero": 791, "nombre": _TEAM_CREST},
            {"numero": 792, "nombre": "LIBERATO CACACE", "tipo": "IC"},
            {"numero": 793, "nombre": "MAX CROCOMBE"},
            {"numero": 794, "nombre": "TIM PAYNE"},
            {"numero": 795, "nombre": "MICHAEL BOXALL"},
            {"numero": 796, "nombre": "NANDO PIJNAKER"},
            {"numero": 797, "nombre": "TOMMY SMITH"},
            {"numero": 798, "nombre": "JOE BELL"},
            {"numero": 799, "nombre": "MATTHEW GARBETT"},
            {"numero": 800, "nombre": "SARPREET SINGH"},
            {"numero": 801, "nombre": "ELIJAH JUST"},
        ]
    },
    "PERU": {
        "items": [
            {"numero": 802, "nombre": "GIANLUCA LAPADULA", "tipo": "FF"},
            {"numero": 803, "nombre": _TEAM_CREST},
            {"numero": 804, "nombre": "PEDRO GALLESE", "tipo": "IC"},
            {"numero": 805, "nombre": "ALDO CORZO"},
            {"numero": 806, "nombre": "CARLOS ZAMBRANO"},
            {"numero": 807, "nombre": "ALEXANDER CALLENS"},
            {"numero": 808, "nombre": "MARCOS LOPEZ"},
            {"numero": 809, "nombre": "RENATO TAPIA"},
            {"numero": 810, "nombre": "YOSHIMAR YOTUN"},
            {"numero": 811, "nombre": "PIERO QUISPE"},
            {"numero": 812, "nombre": "ANDRE CARRILLO"},
            {"numero": 813, "nombre": "BRYAN REYNA"},
        ]
    },
    "CHILE": {
        "items": [
            {"numero": 814, "nombre": "ALEXIS SANCHEZ", "tipo": "FF"},
            {"numero": 815, "nombre": _TEAM_CREST},
            {"numero": 816, "nombre": "CLAUDIO BRAVO", "tipo": "IC"},
            {"numero": 817, "nombre": "MAURICIO ISLA"},
            {"numero": 818, "nombre": "GARY MEDEL"},
            {"numero": 819, "nombre": "GUILLERMO MARIPAN"},
            {"numero": 820, "nombre": "PAULO DIAZ"},
            {"numero": 821, "nombre": "GABRIEL SUAZO"},
            {"numero": 822, "nombre": "ERICK PULGAR"},
            {"numero": 823, "nombre": "MARCELINO NUÑEZ"},
            {"numero": 824, "nombre": "VICTOR DAVILA"},
            {"numero": 825, "nombre": "BEN BRERETON"},
        ]
    },
    "WALES": {
        "items": [
            {"numero": 826, "nombre": "GARETH BALE", "tipo": "FF"},
            {"numero": 827, "nombre": _TEAM_CREST},
            {"numero": 828, "nombre": "BRENNAN JOHNSON", "tipo": "IC"},
            {"numero": 829, "nombre": "DANNY WARD"},
            {"numero": 830, "nombre": "CONNOR ROBERTS"},
            {"numero": 831, "nombre": "CHRIS MEPHAM"},
            {"numero": 832, "nombre": "JOE RODON"},
            {"numero": 833, "nombre": "NECO WILLIAMS"},
            {"numero": 834, "nombre": "ETHAN AMPADU"},
            {"numero": 835, "nombre": "HARRY WILSON"},
            {"numero": 836, "nombre": "AARON RAMSEY"},
            {"numero": 837, "nombre": "KIEFFER MOORE"},
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
