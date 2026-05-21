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
            {"numero": 1000, "nombre": "JULIAN ALVAREZ", "tipo": "FF"},
            {"numero": 1001, "nombre": _TEAM_CREST},
            {"numero": 1002, "nombre": "LIONEL MESSI", "tipo": "IC"},
            {"numero": 1003, "nombre": "EMILIANO MARTÍNEZ"},
            {"numero": 1004, "nombre": "NAHUEL MOLINA"},
            {"numero": 1005, "nombre": "CRISTIAN ROMERO"},
            {"numero": 1006, "nombre": "NICOLAS OTAMENDI"},
            {"numero": 1007, "nombre": "ENZO FERNÁNDEZ"},
            {"numero": 1008, "nombre": "ALEXIS MAC ALLISTER"},
            {"numero": 1009, "nombre": "RODRIGO DE PAUL"},
            {"numero": 1010, "nombre": "GIULIANO SIMEONE"},
            {"numero": 1011, "nombre": "LAUTARO MARTINEZ"},
        ]
    },
    "BRAZIL": {
        "items": [
            {"numero": 1012, "nombre": "RAPHINHA", "tipo": "FF"},
            {"numero": 1013, "nombre": _TEAM_CREST},
            {"numero": 1014, "nombre": "VINICIUS JUNIOR", "tipo": "IC"},
            {"numero": 1015, "nombre": "ALISSON"},
            {"numero": 1016, "nombre": "DANILO"},
            {"numero": 1017, "nombre": "MARQUINHOS"},
            {"numero": 1018, "nombre": "EDER MILITÃO"},
            {"numero": 1019, "nombre": "CASEMIRO"},
            {"numero": 1020, "nombre": "BRUNO GUIMARães"},
            {"numero": 1021, "nombre": "LUCAS PAQUETA"},
            {"numero": 1022, "nombre": "RODRYGO"},
            {"numero": 1023, "nombre": "ENDRICK"},
        ]
    },
    "URUGUAY": {
        "items": [
            {"numero": 1024, "nombre": "FEDERICO VALVERDE", "tipo": "FF"},
            {"numero": 1025, "nombre": _TEAM_CREST},
            {"numero": 1026, "nombre": "DARWIN NUÑEZ", "tipo": "IC"},
            {"numero": 1027, "nombre": "SERGIO ROCHET"},
            {"numero": 1028, "nombre": "NAHITAN NANDEZ"},
            {"numero": 1029, "nombre": "RONALD ARAUJO"},
            {"numero": 1030, "nombre": "JOSE GIMENEZ"},
            {"numero": 1031, "nombre": "MATHIAS OLIVERA"},
            {"numero": 1032, "nombre": "NICOLAS DE LA CRUZ"},
            {"numero": 1033, "nombre": "RODRIGO BENTANCUR"},
            {"numero": 1034, "nombre": "MAXIMILIANO ARAUJO"},
            {"numero": 1035, "nombre": "FACUNDO PELLISTRI"},
        ]
    },
    "COLOMBIA": {
        "items": [
            {"numero": 1036, "nombre": "LUIS DÍAZ", "tipo": "FF"},
            {"numero": 1037, "nombre": _TEAM_CREST},
            {"numero": 1038, "nombre": "JAMES RODRIGUEZ", "tipo": "IC"},
            {"numero": 1039, "nombre": "CAMILO VARGAS"},
            {"numero": 1040, "nombre": "DAVINSON SANCHEZ"},
            {"numero": 1041, "nombre": "YERRY MINA"},
            {"numero": 1042, "nombre": "DANIEL MUÑOZ"},
            {"numero": 1043, "nombre": "JEFFERSON LERMA"},
            {"numero": 1044, "nombre": "RICHARD RIOS"},
            {"numero": 1045, "nombre": "JHON ARIAS"},
            {"numero": 1046, "nombre": "CUCHO HERNANDEZ"},
            {"numero": 1047, "nombre": "CARLOS CUESTA"},
        ]
    },
    "ECUADOR": {
        "items": [
            {"numero": 1048, "nombre": "MOISES CAICEDO", "tipo": "FF"},
            {"numero": 1049, "nombre": _TEAM_CREST},
            {"numero": 1050, "nombre": "ENNER VALENCIA", "tipo": "IC"},
            {"numero": 1051, "nombre": "HERNAN GALINDEZ"},
            {"numero": 1052, "nombre": "ANGELO PRECIADO"},
            {"numero": 1053, "nombre": "FELIX TORRES"},
            {"numero": 1054, "nombre": "PIERO HINCAPIÉ"},
            {"numero": 1055, "nombre": "WILLIAN PACHO"},
            {"numero": 1056, "nombre": "PERVIS ESTUPIÑAN"},
            {"numero": 1057, "nombre": "ALAN FRANCO"},
            {"numero": 1058, "nombre": "KENDRAY PAEZ"},
            {"numero": 1059, "nombre": "KEVIN RODRIGUEZ"},
        ]
    },
    "VENEZUELA": {
        "items": [
            {"numero": 1060, "nombre": "SALOMON RONDON", "tipo": "FF"},
            {"numero": 1061, "nombre": _TEAM_CREST},
            {"numero": 1062, "nombre": "YEFERSON SOTELDO", "tipo": "IC"},
            {"numero": 1063, "nombre": "RAFAEL ROMO"},
            {"numero": 1064, "nombre": "ALEXANDER GONZALEZ"},
            {"numero": 1065, "nombre": "YORDAN OSORIO"},
            {"numero": 1066, "nombre": "WILKER ANGEL"},
            {"numero": 1067, "nombre": "MIGUEL NAVARRO"},
            {"numero": 1068, "nombre": "JOSE MARTINEZ"},
            {"numero": 1069, "nombre": "YANGEL HERRERA"},
            {"numero": 1070, "nombre": "JEFFERSON SAVARINO"},
            {"numero": 1071, "nombre": "DARWIN MACHIS"},
        ]
    },
    "USA": {
        "items": [
            {"numero": 1072, "nombre": "CHRISTIAN PULISIC", "tipo": "FF"},
            {"numero": 1073, "nombre": _TEAM_CREST},
            {"numero": 1074, "nombre": "WESTON MCKENNIE", "tipo": "IC"},
            {"numero": 1075, "nombre": "MATT TURNER"},
            {"numero": 1076, "nombre": "SERGINO DEST"},
            {"numero": 1077, "nombre": "CHRIS RICHARDS"},
            {"numero": 1078, "nombre": "TIM REAM"},
            {"numero": 1079, "nombre": "ANTONEE ROBINSON"},
            {"numero": 1080, "nombre": "TYLER ADAMS"},
            {"numero": 1081, "nombre": "YUNUS MUSAH"},
            {"numero": 1082, "nombre": "GIO REYNA"},
            {"numero": 1083, "nombre": "FOLARIN BALOGUN"},
        ]
    },
    "MEXICO": {
        "items": [
            {"numero": 1084, "nombre": "SANTIAGO GIMÉNEZ", "tipo": "FF"},
            {"numero": 1085, "nombre": _TEAM_CREST},
            {"numero": 1086, "nombre": "EDSON ALVAREZ", "tipo": "IC"},
            {"numero": 1087, "nombre": "GUILLERMO OCHOA"},
            {"numero": 1088, "nombre": "JORGE SANCHEZ"},
            {"numero": 1089, "nombre": "CESAR MONTES"},
            {"numero": 1090, "nombre": "JOHAN VASQUEZ"},
            {"numero": 1091, "nombre": "JESUS GALLARDO"},
            {"numero": 1092, "nombre": "LUIS ROMO"},
            {"numero": 1093, "nombre": "ORBELIN PINEDA"},
            {"numero": 1094, "nombre": "HIRVING LOZANO"},
            {"numero": 1095, "nombre": "JULIAN QUIÑONES"},
        ]
    },
    "CANADA": {
        "items": [
            {"numero": 1096, "nombre": "ALPHONSO DAVIES", "tipo": "FF"},
            {"numero": 1097, "nombre": _TEAM_CREST},
            {"numero": 1098, "nombre": "JONATHAN DAVID", "tipo": "IC"},
            {"numero": 1099, "nombre": "MAXIME CREPEAU"},
            {"numero": 1100, "nombre": "ALISTAIR JOHNSTON"},
            {"numero": 1101, "nombre": "DEREK CORNELIUS"},
            {"numero": 1102, "nombre": "KAMAL MILLER"},
            {"numero": 1103, "nombre": "STEPHEN EUSTAQUIO"},
            {"numero": 1104, "nombre": "ISMAEL KONE"},
            {"numero": 1105, "nombre": "TAJON BUCHANAN"},
            {"numero": 1106, "nombre": "CYLE LARIN"},
            {"numero": 1107, "nombre": "JACOB SHAFFELBURG"},
        ]
    },
    "COSTA RICA": {
        "items": [
            {"numero": 1108, "nombre": "JOEL CAMPBELL", "tipo": "FF"},
            {"numero": 1109, "nombre": _TEAM_CREST},
            {"numero": 1110, "nombre": "KEYLOR NAVAS", "tipo": "IC"},
            {"numero": 1111, "nombre": "FRANCISCO CALVO"},
            {"numero": 1112, "nombre": "JUAN PABLO VARGAS"},
            {"numero": 1113, "nombre": "KENDALL WASTON"},
            {"numero": 1114, "nombre": "CELSO BORGES"},
            {"numero": 1115, "nombre": "YELTSIN TEJEDA"},
            {"numero": 1116, "nombre": "JEWISON BENNETTE"},
            {"numero": 1117, "nombre": "ANTHONY CONTRERAS"},
            {"numero": 1118, "nombre": "MANFRED UGALDE"},
            {"numero": 1119, "nombre": "BRANDON AGUILERA"},
        ]
    },
    "PANAMA": {
        "items": [
            {"numero": 1120, "nombre": "ADALBERTO CARRASQUILLA", "tipo": "FF"},
            {"numero": 1121, "nombre": _TEAM_CREST},
            {"numero": 1122, "nombre": "ANIBAL GODOY", "tipo": "IC"},
            {"numero": 1123, "nombre": "ORLANDO MOSQUERA"},
            {"numero": 1124, "nombre": "MICHAEL MURILLO"},
            {"numero": 1125, "nombre": "FIDEL ESCOBAR"},
            {"numero": 1126, "nombre": "ANDRES ANDRADE"},
            {"numero": 1127, "nombre": "ERIC DAVIS"},
            {"numero": 1128, "nombre": "EDGAR BARCENAS"},
            {"numero": 1129, "nombre": "JOSE LUIS RODRIGUEZ"},
            {"numero": 1130, "nombre": "ISMAEL DIAZ"},
            {"numero": 1131, "nombre": "JOSE FAJARDO"},
        ]
    },
    "JAMAICA": {
        "items": [
            {"numero": 1132, "nombre": "LEON BAILEY", "tipo": "FF"},
            {"numero": 1133, "nombre": _TEAM_CREST},
            {"numero": 1134, "nombre": "MICHAIL ANTONIO", "tipo": "IC"},
            {"numero": 1135, "nombre": "ANDRE BLAKE"},
            {"numero": 1136, "nombre": "DEXTER LEMBIKISA"},
            {"numero": 1137, "nombre": "DAMION LOWE"},
            {"numero": 1138, "nombre": "ETHAN PINNOCK"},
            {"numero": 1139, "nombre": "AMARII BELL"},
            {"numero": 1140, "nombre": "JOEL LATIBEAUDIERE"},
            {"numero": 1141, "nombre": "KASEY PALMER"},
            {"numero": 1142, "nombre": "DEMARAI GRAY"},
            {"numero": 1143, "nombre": "SHAMAR NICHOLSON"},
        ]
    },
    "FRANCE": {
        "items": [
            {"numero": 1144, "nombre": "KYLIAN MBAPPE", "tipo": "FF"},
            {"numero": 1145, "nombre": _TEAM_CREST},
            {"numero": 1146, "nombre": "ANTOINE GRIEZMANN", "tipo": "IC"},
            {"numero": 1147, "nombre": "MIKE MAIGNAN"},
            {"numero": 1148, "nombre": "JULES KOUNDE"},
            {"numero": 1149, "nombre": "WILLIAM SALIBA"},
            {"numero": 1150, "nombre": "DAYOT UPAMECANO"},
            {"numero": 1151, "nombre": "THEO HERNANDEZ"},
            {"numero": 1152, "nombre": "AURELIEN TCHOUAMÉNI"},
            {"numero": 1153, "nombre": "ADRIEN RABIOT"},
            {"numero": 1154, "nombre": "N'GOLO KANTE"},
            {"numero": 1155, "nombre": "OUSMANE DEMBELE"},
        ]
    },
    "GERMANY": {
        "items": [
            {"numero": 1156, "nombre": "FLORIAN WIRTZ", "tipo": "FF"},
            {"numero": 1157, "nombre": _TEAM_CREST},
            {"numero": 1158, "nombre": "JAMAL MUSIALA", "tipo": "IC"},
            {"numero": 1159, "nombre": "MARC-ANDRE TER STEGEN"},
            {"numero": 1160, "nombre": "JOSHUA KIMMICH"},
            {"numero": 1161, "nombre": "ANTONIO RÜDIGER"},
            {"numero": 1162, "nombre": "JONATHAN TAH"},
            {"numero": 1163, "nombre": "DAVID RAUM"},
            {"numero": 1164, "nombre": "MAXIMILIAN MITTELSTÄDT"},
            {"numero": 1165, "nombre": "ILKAY GÜNDOGAN"},
            {"numero": 1166, "nombre": "LEROY SANE"},
            {"numero": 1167, "nombre": "KAI HAVERTZ"},
        ]
    },
    "ENGLAND": {
        "items": [
            {"numero": 1168, "nombre": "JUDE BELLINGHAM", "tipo": "FF"},
            {"numero": 1169, "nombre": _TEAM_CREST},
            {"numero": 1170, "nombre": "HARRY KANE", "tipo": "IC"},
            {"numero": 1171, "nombre": "JORDAN PICKFORD"},
            {"numero": 1172, "nombre": "KYLE WALKER"},
            {"numero": 1173, "nombre": "JOHN STONES"},
            {"numero": 1174, "nombre": "MARC GUEHI"},
            {"numero": 1175, "nombre": "KIERAN TRIPPIER"},
            {"numero": 1176, "nombre": "DECLAN RICE"},
            {"numero": 1177, "nombre": "TRENT ALEXANDER-ARNOLD"},
            {"numero": 1178, "nombre": "BUKAYO SAKA"},
            {"numero": 1179, "nombre": "PHIL FODEN"},
        ]
    },
    "SPAIN": {
        "items": [
            {"numero": 1180, "nombre": "LAMINE YAMAL", "tipo": "FF"},
            {"numero": 1181, "nombre": _TEAM_CREST},
            {"numero": 1182, "nombre": "RODRI", "tipo": "IC"},
            {"numero": 1183, "nombre": "UNAI SIMON"},
            {"numero": 1184, "nombre": "ROBIN LE NORMAND"},
            {"numero": 1185, "nombre": "DEAN HUIJSEN"},
            {"numero": 1186, "nombre": "MARC CUCURELLA"},
            {"numero": 1187, "nombre": "MARTIN ZUBIMENDI"},
            {"numero": 1188, "nombre": "PEDRI"},
            {"numero": 1189, "nombre": "FABIAN RUIZ"},
            {"numero": 1190, "nombre": "NICO WILLIAMS"},
            {"numero": 1191, "nombre": "MIKEL OYARZABAL"},
        ]
    },
    "PORTUGAL": {
        "items": [
            {"numero": 1192, "nombre": "CRISTIANO RONALDO", "tipo": "FF"},
            {"numero": 1193, "nombre": _TEAM_CREST},
            {"numero": 1194, "nombre": "BRUNO FERNANDES", "tipo": "IC"},
            {"numero": 1195, "nombre": "DIOGO COSTA"},
            {"numero": 1196, "nombre": "JOAO CANCELO"},
            {"numero": 1197, "nombre": "RUBEN DIAS"},
            {"numero": 1198, "nombre": "PEPE"},
            {"numero": 1199, "nombre": "NUNO MENDES"},
            {"numero": 1200, "nombre": "JOAO PALHINHA"},
            {"numero": 1201, "nombre": "VITINHA"},
            {"numero": 1202, "nombre": "BERNARDO SILVA"},
            {"numero": 1203, "nombre": "RAFAEL LEAO"},
        ]
    },
    "NETHERLANDS": {
        "items": [
            {"numero": 1204, "nombre": "CODY GAKPO", "tipo": "FF"},
            {"numero": 1205, "nombre": _TEAM_CREST},
            {"numero": 1206, "nombre": "VIRGIL VAN DIJK", "tipo": "IC"},
            {"numero": 1207, "nombre": "BART VERBRUGGEN"},
            {"numero": 1208, "nombre": "DENZEL DUMFRIES"},
            {"numero": 1209, "nombre": "MATTHIJS DE LIGT"},
            {"numero": 1210, "nombre": "NATHAN AKE"},
            {"numero": 1211, "nombre": "DALEY BLIND"},
            {"numero": 1212, "nombre": "FRENKIE DE JONG"},
            {"numero": 1213, "nombre": "TIJJANI REIJNDERS"},
            {"numero": 1214, "nombre": "XAVI SIMONS"},
            {"numero": 1215, "nombre": "WOUT WEGHORST"},
        ]
    },
    "ITALY": {
        "items": [
            {"numero": 1216, "nombre": "NICOLO BARELLA", "tipo": "FF"},
            {"numero": 1217, "nombre": _TEAM_CREST},
            {"numero": 1218, "nombre": "FEDERICO CHIESA", "tipo": "IC"},
            {"numero": 1219, "nombre": "GIANLUIGI DONNARUMMA"},
            {"numero": 1220, "nombre": "GIOVANNI DI LORENZO"},
            {"numero": 1221, "nombre": "ALESSANDRO BASTONI"},
            {"numero": 1222, "nombre": "RICCARDO CALAFIORI"},
            {"numero": 1223, "nombre": "FEDERICO DIMARCO"},
            {"numero": 1224, "nombre": "JORGINHO"},
            {"numero": 1225, "nombre": "LORENZO PELLEGRINI"},
            {"numero": 1226, "nombre": "DAVIDE FRATTESI"},
            {"numero": 1227, "nombre": "GIANLUCA SCAMACCA"},
        ]
    },
    "CROATIA": {
        "items": [
            {"numero": 1228, "nombre": "LUKA MODRIC", "tipo": "FF"},
            {"numero": 1229, "nombre": _TEAM_CREST},
            {"numero": 1230, "nombre": "JOSKO GVARDIOL", "tipo": "IC"},
            {"numero": 1231, "nombre": "DOMINIK LIVAKOVIC"},
            {"numero": 1232, "nombre": "JOSIP JURANOVIC"},
            {"numero": 1233, "nombre": "JOSIP SUTALO"},
            {"numero": 1234, "nombre": "BORNA SOSA"},
            {"numero": 1235, "nombre": "MATEO KOVACIC"},
            {"numero": 1236, "nombre": "MARCELO BROZOVIC"},
            {"numero": 1237, "nombre": "MARIO PASALIC"},
            {"numero": 1238, "nombre": "LOVRO MAJER"},
            {"numero": 1239, "nombre": "ANDREJ KRAMARIC"},
        ]
    },
    "BELGIUM": {
        "items": [
            {"numero": 1240, "nombre": "KEVIN DE BRUYNE", "tipo": "FF"},
            {"numero": 1241, "nombre": _TEAM_CREST},
            {"numero": 1242, "nombre": "ROMELU LUKAKU", "tipo": "IC"},
            {"numero": 1243, "nombre": "KOEN CASTEELS"},
            {"numero": 1244, "nombre": "TIMOTHY CASTAGNE"},
            {"numero": 1245, "nombre": "WOUT FAES"},
            {"numero": 1246, "nombre": "JAN VERTONGHEN"},
            {"numero": 1247, "nombre": "ARTHUR THEATE"},
            {"numero": 1248, "nombre": "AMADOU ONANA"},
            {"numero": 1249, "nombre": "OUREL MANGALA"},
            {"numero": 1250, "nombre": "JEREMY DOKU"},
            {"numero": 1251, "nombre": "LEANDRO TROSSARD"},
        ]
    },
    "SWITZERLAND": {
        "items": [
            {"numero": 1252, "nombre": "GRANIT XHAKA", "tipo": "FF"},
            {"numero": 1253, "nombre": _TEAM_CREST},
            {"numero": 1254, "nombre": "MANUEL AKANJI", "tipo": "IC"},
            {"numero": 1255, "nombre": "YANN SOMMER"},
            {"numero": 1256, "nombre": "SILVAN WIDMER"},
            {"numero": 1257, "nombre": "NICO ELVEDI"},
            {"numero": 1258, "nombre": "RICARDO RODRIGUEZ"},
            {"numero": 1259, "nombre": "REMO FREULER"},
            {"numero": 1260, "nombre": "MICHEL AEBISCHER"},
            {"numero": 1261, "nombre": "XHERDAN SHAQIRI"},
            {"numero": 1262, "nombre": "DAN NDOYE"},
            {"numero": 1263, "nombre": "BREEL EMBOLO"},
        ]
    },
    "DENMARK": {
        "items": [
            {"numero": 1264, "nombre": "CHRISTIAN ERIKSEN", "tipo": "FF"},
            {"numero": 1265, "nombre": _TEAM_CREST},
            {"numero": 1266, "nombre": "RASMUS HOJLUND", "tipo": "IC"},
            {"numero": 1267, "nombre": "KASPER SCHMEICHEL"},
            {"numero": 1268, "nombre": "JOACHIM ANDERSEN"},
            {"numero": 1269, "nombre": "SIMON KJAER"},
            {"numero": 1270, "nombre": "ANDREAS CHRISTENSEN"},
            {"numero": 1271, "nombre": "JOAKIM MAEHLE"},
            {"numero": 1272, "nombre": "PIERRE-EMILE HOJBJERG"},
            {"numero": 1273, "nombre": "THOMAS DELANEY"},
            {"numero": 1274, "nombre": "JONAS WIND"},
            {"numero": 1275, "nombre": "YUSSUF POULSEN"},
        ]
    },
    "SWEDEN": {
        "items": [
            {"numero": 1276, "nombre": "ALEXANDER ISAK", "tipo": "FF"},
            {"numero": 1277, "nombre": _TEAM_CREST},
            {"numero": 1278, "nombre": "DEJAN KULUSEVSKI", "tipo": "IC"},
            {"numero": 1279, "nombre": "ROBIN OLSEN"},
            {"numero": 1280, "nombre": "EMIL KRAFTH"},
            {"numero": 1281, "nombre": "VICTOR LINDELOF"},
            {"numero": 1282, "nombre": "ISAK HIEN"},
            {"numero": 1283, "nombre": "LUDWIG AUGUSTINSSON"},
            {"numero": 1284, "nombre": "MATTIAS SVANBERG"},
            {"numero": 1285, "nombre": "JENS CAJUSTE"},
            {"numero": 1286, "nombre": "EMIL FORSBERG"},
            {"numero": 1287, "nombre": "ANTHONY ELANGA"},
        ]
    },
    "POLAND": {
        "items": [
            {"numero": 1288, "nombre": "ROBERT LEWANDOWSKI", "tipo": "FF"},
            {"numero": 1289, "nombre": _TEAM_CREST},
            {"numero": 1290, "nombre": "PIOTR ZIELINSKI", "tipo": "IC"},
            {"numero": 1291, "nombre": "WOJCIECH SZCZESNY"},
            {"numero": 1292, "nombre": "MATTY CASH"},
            {"numero": 1293, "nombre": "JAN BEDNAREK"},
            {"numero": 1294, "nombre": "JAKUB KIWIOR"},
            {"numero": 1295, "nombre": "PRZEMYSLAW FRANKOWSKI"},
            {"numero": 1296, "nombre": "SEBASTIAN SZYMANSKI"},
            {"numero": 1297, "nombre": "KAROL LINETTY"},
            {"numero": 1298, "nombre": "NICOLA ZALEWSKI"},
            {"numero": 1299, "nombre": "KAROL SWIDERSKI"},
        ]
    },
    "SERBIA": {
        "items": [
            {"numero": 1300, "nombre": "DUSAN VLAHOVIC", "tipo": "FF"},
            {"numero": 1301, "nombre": _TEAM_CREST},
            {"numero": 1302, "nombre": "ALEKSANDAR MITROVIC", "tipo": "IC"},
            {"numero": 1303, "nombre": "VANJA MILINKOVIC-SAVIC"},
            {"numero": 1304, "nombre": "NIKOLA MILENKOVIC"},
            {"numero": 1305, "nombre": "MILOS VELJKOVIC"},
            {"numero": 1306, "nombre": "STRAHINJA PAVLOVIC"},
            {"numero": 1307, "nombre": "ANDRIJA ZIVKOVIC"},
            {"numero": 1308, "nombre": "SERGEJ MILINKOVIC-SAVIC"},
            {"numero": 1309, "nombre": "SASA LUKIC"},
            {"numero": 1310, "nombre": "FILIP KOSTIC"},
            {"numero": 1311, "nombre": "DUSAN TADIC"},
        ]
    },
    "MOROCCO": {
        "items": [
            {"numero": 1312, "nombre": "ACHRAF HAKIMI", "tipo": "FF"},
            {"numero": 1313, "nombre": _TEAM_CREST},
            {"numero": 1314, "nombre": "HAKIM ZIYECH", "tipo": "IC"},
            {"numero": 1315, "nombre": "YASSINE BOUNOU"},
            {"numero": 1316, "nombre": "NAYEF AGUERD"},
            {"numero": 1317, "nombre": "ROMAIN SAISS"},
            {"numero": 1318, "nombre": "NOUSSAIR MAZRAOUI"},
            {"numero": 1319, "nombre": "SOFYAN AMRABAT"},
            {"numero": 1320, "nombre": "AZZEDINE OUNAHI"},
            {"numero": 1321, "nombre": "SELIM AMALLAH"},
            {"numero": 1322, "nombre": "YOUSSEF EN-NESYRI"},
            {"numero": 1323, "nombre": "BRAHIM DIAZ"},
        ]
    },
    "SENEGAL": {
        "items": [
            {"numero": 1324, "nombre": "SADIO MANE", "tipo": "FF"},
            {"numero": 1325, "nombre": _TEAM_CREST},
            {"numero": 1326, "nombre": "KALIDOU KOULIBALY", "tipo": "IC"},
            {"numero": 1327, "nombre": "EDOUARD MENDY"},
            {"numero": 1328, "nombre": "YOUSSOUF SABALY"},
            {"numero": 1329, "nombre": "MOUSSA NIAKHATE"},
            {"numero": 1330, "nombre": "ABDOU DIALLO"},
            {"numero": 1331, "nombre": "ISMAIL JAKOBS"},
            {"numero": 1332, "nombre": "NAMPALYS MENDY"},
            {"numero": 1333, "nombre": "IDRISSA GUEYE"},
            {"numero": 1334, "nombre": "PAPE MATAR SARR"},
            {"numero": 1335, "nombre": "ISMAILA SARR"},
        ]
    },
    "EGYPT": {
        "items": [
            {"numero": 1336, "nombre": "MOHAMED SALAH", "tipo": "FF"},
            {"numero": 1337, "nombre": _TEAM_CREST},
            {"numero": 1338, "nombre": "OMAR MARMOUSH", "tipo": "IC"},
            {"numero": 1339, "nombre": "MOHAMED EL SHENAWY"},
            {"numero": 1340, "nombre": "MOHAMED HANY"},
            {"numero": 1341, "nombre": "AHMED HEGAZY"},
            {"numero": 1342, "nombre": "MOHAMED ABDELMONEM"},
            {"numero": 1343, "nombre": "AHMED FATOUH"},
            {"numero": 1344, "nombre": "MOHAMED ELNENY"},
            {"numero": 1345, "nombre": "MARWAN ATTIA"},
            {"numero": 1346, "nombre": "MAHMOUD TREZEGUET"},
            {"numero": 1347, "nombre": "MOSTAFA MOHAMED"},
        ]
    },
    "NIGERIA": {
        "items": [
            {"numero": 1348, "nombre": "VICTOR OSIMHEN", "tipo": "FF"},
            {"numero": 1349, "nombre": _TEAM_CREST},
            {"numero": 1350, "nombre": "ADEMOLA LOOKMAN", "tipo": "IC"},
            {"numero": 1351, "nombre": "STANLEY NWABALI"},
            {"numero": 1352, "nombre": "OLA AINA"},
            {"numero": 1353, "nombre": "WILLIAM TROOST-EKONG"},
            {"numero": 1354, "nombre": "SEMI AJAYI"},
            {"numero": 1355, "nombre": "ZAIDU SANUSI"},
            {"numero": 1356, "nombre": "FRANK ONYEKA"},
            {"numero": 1357, "nombre": "ALEX IWOBI"},
            {"numero": 1358, "nombre": "SAMUEL CHUKWUEZE"},
            {"numero": 1359, "nombre": "KELECHI IHEANACHO"},
        ]
    },
    "CAMEROON": {
        "items": [
            {"numero": 1360, "nombre": "VINCENT ABOUBAKAR", "tipo": "FF"},
            {"numero": 1361, "nombre": _TEAM_CREST},
            {"numero": 1362, "nombre": "ANDRE ONANA", "tipo": "IC"},
            {"numero": 1363, "nombre": "COLLINS FAI"},
            {"numero": 1364, "nombre": "JEAN-CHARLES CASTELLETTO"},
            {"numero": 1365, "nombre": "CHRISTOPHER WOOH"},
            {"numero": 1366, "nombre": "NOUHOU TOLO"},
            {"numero": 1367, "nombre": "FRANK ANGUISSA"},
            {"numero": 1368, "nombre": "OLIVIER NTCHAM"},
            {"numero": 1369, "nombre": "KARL TOKO EKAMBI"},
            {"numero": 1370, "nombre": "BRYAN MBEUMO"},
            {"numero": 1371, "nombre": "ERIC MAXIM CHOUPO-MOTING"},
        ]
    },
    "ALGERIA": {
        "items": [
            {"numero": 1372, "nombre": "RIYAD MAHREZ", "tipo": "FF"},
            {"numero": 1373, "nombre": _TEAM_CREST},
            {"numero": 1374, "nombre": "ISMAEL BENNACER", "tipo": "IC"},
            {"numero": 1375, "nombre": "ANTHONY MANDREA"},
            {"numero": 1376, "nombre": "YOUCEF ATAL"},
            {"numero": 1377, "nombre": "AISSA MANDI"},
            {"numero": 1378, "nombre": "RAMY BENSEBAINI"},
            {"numero": 1379, "nombre": "RAYAN AIT-NOURI"},
            {"numero": 1380, "nombre": "NABIL BENTALEB"},
            {"numero": 1381, "nombre": "RAMIZ ZERROUKI"},
            {"numero": 1382, "nombre": "FARES CHAIBI"},
            {"numero": 1383, "nombre": "BAGHDAD BOUNEDJAH"},
        ]
    },
    "IVORY COAST": {
        "items": [
            {"numero": 1384, "nombre": "SEBASTIEN HALLER", "tipo": "FF"},
            {"numero": 1385, "nombre": _TEAM_CREST},
            {"numero": 1386, "nombre": "FRANCK KESSIE", "tipo": "IC"},
            {"numero": 1387, "nombre": "YAHIA FOFANA"},
            {"numero": 1388, "nombre": "SERGE AURIER"},
            {"numero": 1389, "nombre": "ODILON KOSSONOU"},
            {"numero": 1390, "nombre": "EVAN NDICKA"},
            {"numero": 1391, "nombre": "GHISLAIN KONAN"},
            {"numero": 1392, "nombre": "IBRAHIM SANGARE"},
            {"numero": 1393, "nombre": "SEKO FOFANA"},
            {"numero": 1394, "nombre": "MAX GRADEL"},
            {"numero": 1395, "nombre": "SIMON ADINGRA"},
        ]
    },
    "GHANA": {
        "items": [
            {"numero": 1396, "nombre": "MOHAMMED KUDUS", "tipo": "FF"},
            {"numero": 1397, "nombre": _TEAM_CREST},
            {"numero": 1398, "nombre": "THOMAS PARTEY", "tipo": "IC"},
            {"numero": 1399, "nombre": "LAWRENCE ATI-ZIGI"},
            {"numero": 1400, "nombre": "ALIDU SEIDU"},
            {"numero": 1401, "nombre": "ALEXANDER DJIKU"},
            {"numero": 1402, "nombre": "MOHAMMED SALISU"},
            {"numero": 1403, "nombre": "GIDEON MENSAH"},
            {"numero": 1404, "nombre": "SALIS ABDUL SAMED"},
            {"numero": 1405, "nombre": "MAJEED ASHIMERU"},
            {"numero": 1406, "nombre": "JORDAN AYEW"},
            {"numero": 1407, "nombre": "INAKI WILLIAMS"},
        ]
    },
    "MALI": {
        "items": [
            {"numero": 1408, "nombre": "YVES BISSOUMA", "tipo": "FF"},
            {"numero": 1409, "nombre": _TEAM_CREST},
            {"numero": 1410, "nombre": "AMADOU HAIDARA", "tipo": "IC"},
            {"numero": 1411, "nombre": "DJIGUI DIARRA"},
            {"numero": 1412, "nombre": "HAMARI TRAORE"},
            {"numero": 1413, "nombre": "BOUBACAR KOUYATE"},
            {"numero": 1414, "nombre": "SIKOU NIAKATE"},
            {"numero": 1415, "nombre": "AMADOU DANTE"},
            {"numero": 1416, "nombre": "DIADIE SAMASSEKOU"},
            {"numero": 1417, "nombre": "MOHAMED CAMARA"},
            {"numero": 1418, "nombre": "KAMORY DOUMBIA"},
            {"numero": 1419, "nombre": "LASSINE SINAYOKO"},
        ]
    },
    "JAPAN": {
        "items": [
            {"numero": 1420, "nombre": "TAKEFUSA KUBO", "tipo": "FF"},
            {"numero": 1421, "nombre": _TEAM_CREST},
            {"numero": 1422, "nombre": "KAORU MITOMA", "tipo": "IC"},
            {"numero": 1423, "nombre": "ZION SUZUKI"},
            {"numero": 1424, "nombre": "YUKINARI SUGAWARA"},
            {"numero": 1425, "nombre": "KO ITAKURA"},
            {"numero": 1426, "nombre": "TAKEHIRO TOMIYASU"},
            {"numero": 1427, "nombre": "HIROKI ITO"},
            {"numero": 1428, "nombre": "WATARU ENDO"},
            {"numero": 1429, "nombre": "HIDEMASA MORITA"},
            {"numero": 1430, "nombre": "TAKUMI MINAMINO"},
            {"numero": 1431, "nombre": "AYASE UEDA"},
        ]
    },
    "IRAN": {
        "items": [
            {"numero": 1432, "nombre": "MEHDI TAREMI", "tipo": "FF"},
            {"numero": 1433, "nombre": _TEAM_CREST},
            {"numero": 1434, "nombre": "SARDAR AZMOUN", "tipo": "IC"},
            {"numero": 1435, "nombre": "ALIREZA BEIRANVAND"},
            {"numero": 1436, "nombre": "RAMIN REZAEIAN"},
            {"numero": 1437, "nombre": "HOSSEIN KANAANI"},
            {"numero": 1438, "nombre": "SHOJA KHALILZADEH"},
            {"numero": 1439, "nombre": "EHSAN HAJSAFI"},
            {"numero": 1440, "nombre": "SAEID EZATOLAHI"},
            {"numero": 1441, "nombre": "SAMAN GHODDOS"},
            {"numero": 1442, "nombre": "ALIREZA JAHANBAKHSH"},
            {"numero": 1443, "nombre": "MOHAMMAD MOHEBI"},
        ]
    },
    "SOUTH KOREA": {
        "items": [
            {"numero": 1444, "nombre": "HEUNG-MIN SON", "tipo": "FF"},
            {"numero": 1445, "nombre": _TEAM_CREST},
            {"numero": 1446, "nombre": "MIN-JAE KIM", "tipo": "IC"},
            {"numero": 1447, "nombre": "SEUNG-GYU KIM"},
            {"numero": 1448, "nombre": "YOUNG-WOO SEOL"},
            {"numero": 1449, "nombre": "SEUNG-HYUN JUNG"},
            {"numero": 1450, "nombre": "YOUNG-GWON KIM"},
            {"numero": 1451, "nombre": "JIN-SU KIM"},
            {"numero": 1452, "nombre": "IN-BEOM HWANG"},
            {"numero": 1453, "nombre": "YONG-WOO PARK"},
            {"numero": 1454, "nombre": "KANG-IN LEE"},
            {"numero": 1455, "nombre": "GUE-SUNG CHO"},
        ]
    },
    "AUSTRALIA": {
        "items": [
            {"numero": 1456, "nombre": "JACK IRVINE", "tipo": "FF"},
            {"numero": 1457, "nombre": _TEAM_CREST},
            {"numero": 1458, "nombre": "MATHEW RYAN", "tipo": "IC"},
            {"numero": 1459, "nombre": "NATHANIEL ATKINSON"},
            {"numero": 1460, "nombre": "HARRY SOUTTAR"},
            {"numero": 1461, "nombre": "KYE ROWLES"},
            {"numero": 1462, "nombre": "AZIZ BEHICH"},
            {"numero": 1463, "nombre": "KEANU BACCUS"},
            {"numero": 1464, "nombre": "JACKSON IRVINE"},
            {"numero": 1465, "nombre": "CRAIG GOODWIN"},
            {"numero": 1466, "nombre": "RILEY MCGREE"},
            {"numero": 1467, "nombre": "MITCHELL DUKE"},
        ]
    },
    "SAUDI ARABIA": {
        "items": [
            {"numero": 1468, "nombre": "SALEM AL-DAWSARI", "tipo": "FF"},
            {"numero": 1469, "nombre": _TEAM_CREST},
            {"numero": 1470, "nombre": "SALEH AL-SHEHRI", "tipo": "IC"},
            {"numero": 1471, "nombre": "MOHAMMED AL-OWAIS"},
            {"numero": 1472, "nombre": "SAUD ABDULHAMID"},
            {"numero": 1473, "nombre": "HASSAN TAMBAKTI"},
            {"numero": 1474, "nombre": "ALI AL-BULAIHI"},
            {"numero": 1475, "nombre": "YASSER AL-SHAHRANI"},
            {"numero": 1476, "nombre": "MOHAMED KANNO"},
            {"numero": 1477, "nombre": "ABDULLAH AL-KHAIBARI"},
            {"numero": 1478, "nombre": "FIARAS AL-BURAIKAN"},
            {"numero": 1479, "nombre": "ABDULRAHMAN GHAREEB"},
        ]
    },
    "QATAR": {
        "items": [
            {"numero": 1480, "nombre": "AKRAM AFIF", "tipo": "FF"},
            {"numero": 1481, "nombre": _TEAM_CREST},
            {"numero": 1482, "nombre": "ALMOEZ ALI", "tipo": "IC"},
            {"numero": 1483, "nombre": "MESHAAL BARSHAM"},
            {"numero": 1484, "nombre": "PEDRO MIGUEL"},
            {"numero": 1485, "nombre": "TAREK SALMAN"},
            {"numero": 1486, "nombre": "BOUALEM KHOUKHI"},
            {"numero": 1487, "nombre": "LUCAS MENDES"},
            {"numero": 1488, "nombre": "JASSIM GABER"},
            {"numero": 1489, "nombre": "AHMED FATHI"},
            {"numero": 1490, "nombre": "HASSAN AL-HAYDOS"},
            {"numero": 1491, "nombre": "YUSUF ABDURISAG"},
        ]
    },
    "IRAQ": {
        "items": [
            {"numero": 1492, "nombre": "AYMEN HUSSEIN", "tipo": "FF"},
            {"numero": 1493, "nombre": _TEAM_CREST},
            {"numero": 1494, "nombre": "ALI JASSIM", "tipo": "IC"},
            {"numero": 1495, "nombre": "JALAL HASSAN"},
            {"numero": 1496, "nombre": "HUSSEIN ALI"},
            {"numero": 1497, "nombre": "SAAD NATIQ"},
            {"numero": 1498, "nombre": "REBIN SULAKA"},
            {"numero": 1499, "nombre": "MERCHAS DOSKI"},
            {"numero": 1500, "nombre": "OSAMA RASHID"},
            {"numero": 1501, "nombre": "AMIR AL-AMMARI"},
            {"numero": 1502, "nombre": "IBRAHIM BAYESH"},
            {"numero": 1503, "nombre": "ZIDANE IQBAL"},
        ]
    },
    "UZBEKISTAN": {
        "items": [
            {"numero": 1504, "nombre": "ELDOR SHOMURODOV", "tipo": "FF"},
            {"numero": 1505, "nombre": _TEAM_CREST},
            {"numero": 1506, "nombre": "ABBOSBEK FAYZULLAEV", "tipo": "IC"},
            {"numero": 1507, "nombre": "UTKIR YUSUPOV"},
            {"numero": 1508, "nombre": "HOJIRO MATOV"},
            {"numero": 1509, "nombre": "RUSTAM ASHURMATOV"},
            {"numero": 1510, "nombre": "ABDULLA ABDULLAEV"},
            {"numero": 1511, "nombre": "FARRUKH SAYFIEV"},
            {"numero": 1512, "nombre": "ODILJON HAMROBEKOV"},
            {"numero": 1513, "nombre": "OTABEK SHUKUROV"},
            {"numero": 1514, "nombre": "JALOLIDDIN MASHARIPOV"},
            {"numero": 1515, "nombre": "OSTON URUNOV"},
        ]
    },
    "UAE": {
        "items": [
            {"numero": 1516, "nombre": "ALI MABKHOUT", "tipo": "FF"},
            {"numero": 1517, "nombre": _TEAM_CREST},
            {"numero": 1518, "nombre": "FABIO LIMA", "tipo": "IC"},
            {"numero": 1519, "nombre": "KHALID EISA"},
            {"numero": 1520, "nombre": "KHALID AL-HASHEMI"},
            {"numero": 1521, "nombre": "KHALIFA AL-HAMMADI"},
            {"numero": 1522, "nombre": "BADER NASSER"},
            {"numero": 1523, "nombre": "ABDULLA IDREES"},
            {"numero": 1524, "nombre": "ALI SALMEEN"},
            {"numero": 1525, "nombre": "YAHYA NADER"},
            {"numero": 1526, "nombre": "TAHNOON AL-ZAABI"},
            {"numero": 1527, "nombre": "CAIO CANEDO"},
        ]
    },
    "NEW ZEALAND": {
        "items": [
            {"numero": 1528, "nombre": "CHRIS WOOD", "tipo": "FF"},
            {"numero": 1529, "nombre": _TEAM_CREST},
            {"numero": 1530, "nombre": "LIBERATO CACACE", "tipo": "IC"},
            {"numero": 1531, "nombre": "MAX CROCOMBE"},
            {"numero": 1532, "nombre": "TIM PAYNE"},
            {"numero": 1533, "nombre": "MICHAEL BOXALL"},
            {"numero": 1534, "nombre": "NANDO PIJNAKER"},
            {"numero": 1535, "nombre": "TOMMY SMITH"},
            {"numero": 1536, "nombre": "JOE BELL"},
            {"numero": 1537, "nombre": "MATTHEW GARBETT"},
            {"numero": 1538, "nombre": "SARPREET SINGH"},
            {"numero": 1539, "nombre": "ELIJAH JUST"},
        ]
    },
    "PERU": {
        "items": [
            {"numero": 1540, "nombre": "GIANLUCA LAPADULA", "tipo": "FF"},
            {"numero": 1541, "nombre": _TEAM_CREST},
            {"numero": 1542, "nombre": "PEDRO GALLESE", "tipo": "IC"},
            {"numero": 1543, "nombre": "ALDO CORZO"},
            {"numero": 1544, "nombre": "CARLOS ZAMBRANO"},
            {"numero": 1545, "nombre": "ALEXANDER CALLENS"},
            {"numero": 1546, "nombre": "MARCOS LOPEZ"},
            {"numero": 1547, "nombre": "RENATO TAPIA"},
            {"numero": 1548, "nombre": "YOSHIMAR YOTUN"},
            {"numero": 1549, "nombre": "PIERO QUISPE"},
            {"numero": 1550, "nombre": "ANDRE CARRILLO"},
            {"numero": 1551, "nombre": "BRYAN REYNA"},
        ]
    },
    "CHILE": {
        "items": [
            {"numero": 1552, "nombre": "ALEXIS SANCHEZ", "tipo": "FF"},
            {"numero": 1553, "nombre": _TEAM_CREST},
            {"numero": 1554, "nombre": "CLAUDIO BRAVO", "tipo": "IC"},
            {"numero": 1555, "nombre": "MAURICIO ISLA"},
            {"numero": 1556, "nombre": "GARY MEDEL"},
            {"numero": 1557, "nombre": "GUILLERMO MARIPAN"},
            {"numero": 1558, "nombre": "PAULO DIAZ"},
            {"numero": 1559, "nombre": "GABRIEL SUAZO"},
            {"numero": 1560, "nombre": "ERICK PULGAR"},
            {"numero": 1561, "nombre": "MARCELINO NUÑEZ"},
            {"numero": 1562, "nombre": "VICTOR DAVILA"},
            {"numero": 1563, "nombre": "BEN BRERETON"},
        ]
    },
    "WALES": {
        "items": [
            {"numero": 1564, "nombre": "GARETH BALE", "tipo": "FF"},
            {"numero": 1565, "nombre": _TEAM_CREST},
            {"numero": 1566, "nombre": "BRENNAN JOHNSON", "tipo": "IC"},
            {"numero": 1567, "nombre": "DANNY WARD"},
            {"numero": 1568, "nombre": "CONNOR ROBERTS"},
            {"numero": 1569, "nombre": "CHRIS MEPHAM"},
            {"numero": 1570, "nombre": "JOE RODON"},
            {"numero": 1571, "nombre": "NECO WILLIAMS"},
            {"numero": 1572, "nombre": "ETHAN AMPADU"},
            {"numero": 1573, "nombre": "HARRY WILSON"},
            {"numero": 1574, "nombre": "AARON RAMSEY"},
            {"numero": 1575, "nombre": "KIEFFER MOORE"},
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
