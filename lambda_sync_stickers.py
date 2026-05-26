"""
AWS Lambda handler — Sticker Catalogue Sync (FIFA World Cup 2026 Adrenalyn XL)
Trigger: manual invocation or EventBridge one-shot before tournament start.

Uses official panini codes from the Adrenalyn XL catalogue (range 160-2014).
Per team: 1 Team Crest (Rare) + 11 Player (Common) cards.
Players listed with two panini codes also get a Fan Favourite (Epic) variant.

NOTE: Do not run alongside sync_stickers.py — that script uses internal
sequential codes (1000+) that overlap with this catalogue's official codes.
"""
import json
import logging
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Official FIFA World Cup 2026 Adrenalyn XL catalogue.
# Player format: "NAME [cite: code]" or "NAME [cite: code1, code2]"
#   code1 = regular Player card (Common)
#   code2 = Fan Favourite variant (Epic)
# Team format: "Name [cite: section_ref, team_crest_code]"
# ---------------------------------------------------------------------------
_CATALOGUE = [
    {"equipo": "Mexico [cite: 34, 160]", "jugadores": [
        "LUIS MALAGÓN [cite: 180]", "JOHAN VÁSQUEZ [cite: 181, 183]",
        "CÉSAR MONTES [cite: 191]", "JESÚS GALLARDO [cite: 192]",
        "ISRAEL REYES [cite: 165]", "EDSON ÁLVAREZ [cite: 166]",
        "MARCEL RUIZ [cite: 167]", "HIRVING LOZANO [cite: 182, 184]",
        "RAÚL JIMÉNEZ [cite: 185]", "ALEXIS VEGA [cite: 186, 187]",
        "ROBERTO ALVARADO [cite: 196]",
    ]},
    {"equipo": "South Africa [cite: 38, 197]", "jugadores": [
        "RONWEN WILLIAMS [cite: 214, 215]", "AUBREY MODIBA [cite: 216]",
        "MBEKEZELI MBOKAZI [cite: 223]", "SIYABONGA NGEZANA [cite: 224]",
        "KHULISO MUDAU [cite: 209]", "TEBOHO MOKOENA [cite: 210]",
        "VAVA SITHOLE [cite: 211]", "BATHUSI AUBAAS [cite: 217, 218]",
        "SIPHO MBULE [cite: 219]", "LYLE FOSTER [cite: 220]",
        "OSWIN APPOLLIS [cite: 231]",
    ]},
    {"equipo": "Korea Republic [cite: 41, 232]", "jugadores": [
        "HYEONWOO JO [cite: 252]", "MINJAE KIM [cite: 253]",
        "YUMIN CHO [cite: 263, 265]", "YOUNGWOO SEOL [cite: 264, 266]",
        "JAESUNG LEE [cite: 238]", "INBEOM HWANG [cite: 239]",
        "KANGIN LEE [cite: 240]", "JENS CASTROP [cite: 254, 257]",
        "HEUNGMIN SON [cite: 255, 258]", "HEECHAN HWANG [cite: 256, 259]",
        "HYEONGYU OH [cite: 270]",
    ]},
    {"equipo": "Czechia [cite: 46, 271]", "jugadores": [
        "MATEJ KOVÁŘ [cite: 298]", "LADISLAV KREJČÍ [cite: 299]",
        "VLADIMIR COUFAL [cite: 304, 306]", "JAROSLAV ZELENÝ [cite: 305, 307]",
        "LUKÁŠ PROVOD [cite: 283, 285]", "LUKÁŠ ČERV [cite: 284, 286]",
        "TOMÁŠ SOUČEK [cite: 287]", "PAVEL ŠULC [cite: 308, 309]",
        "VÁCLAV ČERNÝ [cite: 310]", "ADAM HLOŽEK [cite: 311]",
        "PATRIK SCHICK [cite: 316]",
    ]},
    {"equipo": "Canada [cite: 36, 317]", "jugadores": [
        "DAYNE ST. CLAIR [cite: 340]", "ALPHONSO DAVIES [cite: 341]",
        "RICHIE LARYEA [cite: 350]", "DEREK CORNELIUS [cite: 351, 352]",
        "STEPHEN EUSTAQUIO [cite: 323]", "ISMAEL KONE [cite: 324]",
        "JACOB SHAFFELBURG [cite: 325]", "NIKO SIGUR [cite: 342, 344]",
        "TAJON BUCHANAN [cite: 343, 345]", "CYLE LARIN [cite: 346]",
        "JONATHAN DAVID [cite: 359]",
    ]},
    {"equipo": "Bosnia-Herzegovina [cite: 39, 360]", "jugadores": [
        "NIKOLA VASILJ [cite: 383, 384]", "AMAR DEDIĆ [cite: 385]",
        "SEAD KOLAŠINAC [cite: 395]", "TARIK MUHAREMOVIĆ [cite: 396]",
        "NIKOLA KATIĆ [cite: 368]", "BENJAMIN TAHIROVIĆ [cite: 369]",
        "IVAN ŠUNJIĆ [cite: 370]", "ERMEDIN DEMIROVIĆ [cite: 386, 388]",
        "ESEMIR BAJRAKTAREVIĆ [cite: 387, 389]", "EDIN DŽEKO [cite: 390]",
        "AMAR MEMIĆ [cite: 401]",
    ]},
    {"equipo": "Qatar [cite: 43, 402]", "jugadores": [
        "MESHAAL BARSHAM [cite: 423, 424]", "SULTAN ALBRAKE [cite: 425]",
        "BOUALEM KHOUKHI [cite: 432]", "PEDRO MIGUEL [cite: 433]",
        "MOHAMMED MANNAI [cite: 409, 410]", "KARIM BOUDIAF [cite: 411]",
        "ASSIM MADIBO [cite: 412]", "EDMILSON JUNIOR [cite: 426, 427]",
        "AKRAM HASSAN AFIF [cite: 428]", "AHMED AL-GANEHI [cite: 429]",
        "ALMOEZ ALI [cite: 441]",
    ]},
    {"equipo": "Switzerland [cite: 48, 442]", "jugadores": [
        "GREGOR KOBEL [cite: 464, 468]", "MANUEL AKANJI [cite: 465, 469]",
        "RICARDO RODRÍGUEZ [cite: 475]", "NICO ELVEDI [cite: 476, 477]",
        "SILVAN WIDMER [cite: 449]", "GRANIT XHAKA [cite: 450]",
        "REMO FREULER [cite: 451]", "FABIAN RIEDER [cite: 466, 470]",
        "BREEL EMBOLO [cite: 467, 471]", "RUBÉN VARGAS [cite: 472]",
        "DAN NDOYE [cite: 486, 487]",
    ]},
    {"equipo": "Brazil [cite: 50, 488]", "jugadores": [
        "ALISSON [cite: 511]", "MARQUINHOS [cite: 512]",
        "ÉDER MILITÃO [cite: 518]", "GABRIEL MAGALHÃES [cite: 519]",
        "CASEMIRO [cite: 498]", "BRUNO GUIMARÃES [cite: 499]",
        "VINÍCIUS JÚNIOR [cite: 500]", "RODRYGO [cite: 513]",
        "MATHEUS CUNHA [cite: 510, 515]", "RAPHINHA [cite: 514]",
        "ESTÉVÃO [cite: 522]",
    ]},
    {"equipo": "Morocco [cite: 54, 526]", "jugadores": [
        "YASSINE BOUNOU [cite: 544, 545]", "ACHRAF HAKIMI [cite: 546]",
        "NOUSSAIR MAZRAOUI [cite: 554]", "NAYEF AGUERD [cite: 555]",
        "ROMAIN SAÏSS [cite: 537]", "SOFYAN AMRABAT [cite: 538]",
        "ELIESSE BEN SEGHIR [cite: 539]", "BILAL EL KHANNOUSS [cite: 547, 548]",
        "ISMAEL SAIBARI [cite: 549]", "YOUSSEF EN-NESYRI [cite: 556]",
        "BRAHIM DÍAZ [cite: 558]",
    ]},
    {"equipo": "Haiti [cite: 59, 559]", "jugadores": [
        "JOHNY PLACIDE [cite: 579, 580]", "CARLENS ARCUS [cite: 581]",
        "RICARDO ADE [cite: 591]", "DUKE LACROIX [cite: 592]",
        "LEVERTON PIERRE [cite: 565]", "DANLEY JEAN JACQUES [cite: 566]",
        "JEAN-RICNER BELLEGARDE [cite: 567]", "JOSUE CASIMIR [cite: 582, 585]",
        "RUBEN PROVIDENCE [cite: 583, 586]", "DUCKENS NAZON [cite: 584, 587]",
        "FRANTZDY PIERROT [cite: 596]",
    ]},
    {"equipo": "Scotland [cite: 63, 597]", "jugadores": [
        "ANGUS GUNN [cite: 620, 621]", "AARON HICKEY [cite: 622]",
        "ANDREW ROBERTSON [cite: 632]", "JOHN SOUTTAR [cite: 633]",
        "GRANT HANLEY [cite: 604]", "SCOTT MCTOMINAY [cite: 605, 606]",
        "LEWIS FERGUSON [cite: 607]", "RYAN CHRISTIE [cite: 623, 625]",
        "JOHN MCGINN [cite: 624, 626]", "CHE ADAMS [cite: 627]",
        "BEN DOAK [cite: 637]",
    ]},
    {"equipo": "USA [cite: 51, 638]", "jugadores": [
        "MATT FREESE [cite: 655, 659]", "CHRIS RICHARDS [cite: 656, 660]",
        "TIM REAM [cite: 668]", "MARK MCKENZIE [cite: 669, 670]",
        "TYLER ADAMS [cite: 642]", "WESTON MCKENNIE [cite: 643]",
        "TIMOTHY WEAH [cite: 644]", "MALIK TILLMAN [cite: 657, 661]",
        "CHRISTIAN PULISIC [cite: 658, 662]", "BRENDEN AARONSON [cite: 663]",
        "FOLARIN BALOGUN [cite: 675]",
    ]},
    {"equipo": "Paraguay [cite: 56, 676]", "jugadores": [
        "ORLANDO GILL [cite: 693]", "GUSTAVO GÓMEZ [cite: 694]",
        "JUAN JOSE CÁCERES [cite: 703]", "OMAR ALDERETE [cite: 704]",
        "JUNIOR ALONSO [cite: 686, 687]", "DIEGO GÓMEZ [cite: 688]",
        "ANDRÉS CUBAS [cite: 689, 690]", "JULIO ENCISO [cite: 695, 696]",
        "MIGUEL ALMIRÓN [cite: 697]", "RAMÓN SOSA [cite: 698]",
        "ANTONIO SANABRIA [cite: 707, 708]",
    ]},
    {"equipo": "Australia [cite: 62, 709]", "jugadores": [
        "MATHEW RYAN [cite: 727]", "HARRY SOUTTAR [cite: 728]",
        "AZIZ BEHICH [cite: 737]", "CAMERON BURGESS [cite: 738]",
        "LEWIS MILLER [cite: 720]", "JACKSON IRVINE [cite: 721, 722]",
        "RILEY MCGREE [cite: 723]", "AIDEN O'NEILL [cite: 729, 731]",
        "CONNOR METCALFE [cite: 730, 732]", "KUSINI YENGI [cite: 733]",
        "NESTORY IRANKUNDA [cite: 740]",
    ]},
    {"equipo": "Türkiye [cite: 66, 741]", "jugadores": [
        "UĞURCAN ÇAKIR [cite: 762]", "MERT MÜLDÜR [cite: 763]",
        "ABDULKERIM BARDAKCI [cite: 773]", "MERIH DEMIRAL [cite: 774]",
        "FERDI KADIOĞLU [cite: 748]", "HAKAN ÇALHANOĞLU [cite: 749]",
        "ORKUN KÖKÇÜ [cite: 750]", "ARDA GÜLER [cite: 764, 766]",
        "CAN UZUN [cite: 765, 767]", "KEREM AKTÜRKOĞLU [cite: 768]",
        "KENAN YILDIZ [cite: 779]",
    ]},
    {"equipo": "Germany [cite: 68, 780]", "jugadores": [
        "MARC-ANDRE TER STEGEN [cite: 800]", "ANTONIO RÜDIGER [cite: 801]",
        "JONATHAN TAH [cite: 808]", "DAVID RAUM [cite: 809, 810]",
        "FLORIAN WIRTZ [cite: 786]", "JOSHUA KIMMICH [cite: 789]",
        "LEON GORETZKA [cite: 790]", "JAMAL MUSIALA [cite: 802, 803]",
        "SERGE GNABRY [cite: 804]", "KAI HAVERTZ [cite: 805]",
        "NICK WOLTEMADE [cite: 817]",
    ]},
    {"equipo": "Curaçao [cite: 72, 818]", "jugadores": [
        "ELOY ROOM [cite: 827]", "ARMANDO OBISPO [cite: 828]",
        "SHEREL FLORANUS [cite: 831]", "ROSHON VAN EIJMA [cite: 832]",
        "SHURANDY SAMBO [cite: 836]", "LIVANO COMENENCIA [cite: 837]",
        "JUNINHO BACUNA [cite: 838]", "LEANDRO BACUNA [cite: 843]",
        "KENJI GORRÉ [cite: 844]", "JÜRGEN LOCADIA [cite: 845]",
        "SONTJE HANSEN [cite: 851]",
    ]},
    {"equipo": "Côte d'Ivoire [cite: 74, 852]", "jugadores": [
        "YAHIA FOFANA [cite: 875, 877]", "GHISLAIN KONAN [cite: 876, 878]",
        "WILFRIED SINGO [cite: 886, 887]", "EVAN NDICKA [cite: 888]",
        "WILLY BOLY [cite: 860]", "FRANCK KESSIE [cite: 861]",
        "SEKO FOFANA [cite: 862]", "IBRAHIM SANGARE [cite: 879]",
        "SEBASTIEN HALLER [cite: 880, 882]", "SIMON ADINGRA [cite: 881, 883]",
        "EVANN GUESSAND [cite: 895]",
    ]},
    {"equipo": "Ecuador [cite: 82, 896]", "jugadores": [
        "HERNAN GALÍNDEZ [cite: 918]", "PIERO HINCAPIÉ [cite: 919, 923]",
        "PERVIS ESTUPIÑÁN [cite: 930]", "WILLIAN PACHO [cite: 931]",
        "ANGELO PRECIADO [cite: 903]", "KENDRY PÁEZ [cite: 904]",
        "MOISES CAICEDO [cite: 905]", "ALAN FRANCO [cite: 920, 924]",
        "PEDRO VITE [cite: 921, 925]", "GONZALO PLATA [cite: 922, 926]",
        "ENNER VALENCIA [cite: 938]",
    ]},
    {"equipo": "Netherlands [cite: 70, 939]", "jugadores": [
        "BART VERBRUGGEN [cite: 960]", "VIRGIL VAN DIJK [cite: 961]",
        "MICKY VAN DE VEN [cite: 970]", "DENZEL DUMFRIES [cite: 971]",
        "TIJJANI REIJNDERS [cite: 945, 946]", "RYAN GRAVENBERCH [cite: 947]",
        "FRENKIE DE JONG [cite: 948]", "XAVI SIMONS [cite: 962]",
        "MEMPHIS DEPAY [cite: 963, 965]", "DONYELL MALEN [cite: 964, 966]",
        "CODY GAKPO [cite: 974]",
    ]},
    {"equipo": "Japan [cite: 77, 975]", "jugadores": [
        "ZION SUZUKI [cite: 994, 995]", "TSUYOSHI WATANABE [cite: 996]",
        "KAISHU SANO [cite: 1007]", "AO TANAKA [cite: 1008, 1009]",
        "DAICHI KAMADA [cite: 980]", "RITSU DOAN [cite: 981]",
        "KEITO NAKAMURA [cite: 982]", "TAKUMI MINAMINO [cite: 997, 1000]",
        "TAKEFUSA KUBO [cite: 998, 1001]", "SHUTO MACHINO [cite: 999, 1002]",
        "AYASE UEDA [cite: 1011]",
    ]},
    {"equipo": "Sweden [cite: 80, 1012]", "jugadores": [
        "VIKTOR JOHANSSON [cite: 1029]", "ISAK HIEN [cite: 1030]",
        "EMIL HOLM [cite: 1036]", "VICTOR NILSSON LINDELÖF [cite: 1037]",
        "LUCAS BERGVALL [cite: 1017]", "YASIN AYARI [cite: 1018]",
        "DANIEL SVENSSON [cite: 1019]", "DEJAN KULUSEVSKI [cite: 1031, 1038]",
        "ANTHONY ELANGA [cite: 1039]", "ALEXANDER ISAK [cite: 1040]",
        "VIKTOR GYÖKERES [cite: 1042]",
    ]},
    {"equipo": "Tunisia [cite: 84, 1045]", "jugadores": [
        "AYMEN DAHMEN [cite: 1067, 1072]", "MONTASSAR TALBI [cite: 1068, 1073]",
        "YASSINE MERIAH [cite: 1078]", "ALI ABDI [cite: 1079, 1080]",
        "FERJANI SASSI [cite: 1052]", "ELLYES SKHIRI [cite: 1053]",
        "AISSA LAÏDOUNI [cite: 1054]", "HANNIBAL MEJBRI [cite: 1069, 1074]",
        "NAIM SLITI [cite: 1070, 1075]", "ELIAS ACHOURI [cite: 1071, 1076]",
        "HAZEM MASTOURI [cite: 1083, 1084]",
    ]},
    {"equipo": "Belgium [cite: 86, 1085]", "jugadores": [
        "THIBAUT COURTOIS [cite: 1101, 1102]", "ARTHUR THEATE [cite: 1103]",
        "TIMOTHY CASTAGNE [cite: 1106]", "MAXIM DE CUYPER [cite: 1107]",
        "YOURI TIELEMANS [cite: 1091]", "KEVIN DE BRUYNE [cite: 1092]",
        "AMADOU ONANA [cite: 1093]", "JÉRÉMY DOKU [cite: 1110, 1111]",
        "CHARLES DE KETELAERE [cite: 1112, 1113]", "LEANDRO TROSSARD [cite: 1114, 1115]",
        "ROMELU LUKAKU [cite: 1121]",
    ]},
    {"equipo": "Egypt [cite: 90, 1122]", "jugadores": [
        "MOHAMED ELSHENAWY [cite: 1144, 1149]", "MOHAMED HANY [cite: 1145, 1150]",
        "YASSER IBRAHIM [cite: 1156]", "RAMY RABIA [cite: 1157]",
        "MARWAN ATTIA [cite: 1132, 1134]", "ZIZO [cite: 1133]",
        "HAMDY FATHY [cite: 1135]", "OMAR MARMOUSH [cite: 1146, 1151]",
        "MOHAMED SALAH [cite: 1147, 1152]", "MOSTAFA MOHAMED [cite: 1148, 1153]",
        "TREZEGUET [cite: 1163]",
    ]},
    {"equipo": "IR Iran [cite: 95, 1164]", "jugadores": [
        "ALIREZA BEIRANVAND [cite: 1185]", "SHOJA KHALILZADEH [cite: 1186]",
        "MILAD MOHAMMADI [cite: 1193]", "RAMIN REZAEIAN [cite: 1194]",
        "HOSSEIN KANAANI [cite: 1171]", "SAEID EZATOLAHI [cite: 1172, 1173]",
        "SAMAN GHODDOS [cite: 1174]", "MOHAMMAD MOHEBI [cite: 1187, 1188]",
        "MEHDI TAREMI [cite: 1189]", "SARDAR AZMOUN [cite: 1190]",
        "ALIREZA JAHANBAKHSH [cite: 1202, 1203]",
    ]},
    {"equipo": "New Zealand [cite: 100, 1204]", "jugadores": [
        "MAX CROCOMBE [cite: 1227, 1231]", "MICHAEL BOXALL [cite: 1228, 1232]",
        "LIBERATO CACACE [cite: 1240, 1242]", "TIM PAYNE [cite: 1241, 1243]",
        "FINN SURMAN [cite: 1213, 1214]", "MARKO STAMENIĆ [cite: 1215]",
        "JOE BELL [cite: 1216]", "SARPREET SINGH [cite: 1229, 1233]",
        "MATT GARBETT [cite: 1230, 1234]", "CHRIS WOOD [cite: 1235]",
        "ELIJAH JUST [cite: 1251]",
    ]},
    {"equipo": "Spain [cite: 88, 1252]", "jugadores": [
        "UNAI SIMÓN [cite: 1273]", "ROBIN LE NORMAND [cite: 1274]",
        "DEAN HUIJSEN [cite: 1281]", "MARC CUCURELLA [cite: 1282]",
        "RODRI [cite: 1259]", "MARTIN ZUBIMENDI [cite: 1258, 1261]",
        "PEDRI [cite: 1260]", "FABIAN RUIZ [cite: 1275, 1277]",
        "LAMINE YAMAL [cite: 1276]", "NICO WILLIAMS [cite: 1278]",
        "MIKEL OYARZABAL [cite: 1289, 1290]",
    ]},
    {"equipo": "Cabo Verde [cite: 92, 1291]", "jugadores": [
        "VOZINHA [cite: 1314]", "LOGAN COSTA [cite: 1315]",
        "PICO [cite: 1324]", "STEVEN MOREIRA [cite: 1325]",
        "JOÃO PAULO [cite: 1298]", "KEVIN PINA [cite: 1299]",
        "JAMIRO MONTEIRO [cite: 1300]", "VANNICK SEMEDO [cite: 1316, 1317]",
        "RYAN MENDES [cite: 1318]", "JOVANE CABRAL [cite: 1319]",
        "DÁRIO LIVRAMENTO [cite: 1327, 1328]",
    ]},
    {"equipo": "Saudi Arabia [cite: 97, 1329]", "jugadores": [
        "NAWAF ALAQIDI [cite: 1350, 1351]", "HASSAN ALTAMBAKTI [cite: 1352]",
        "JEHAD THIKRI [cite: 1358]", "SAUD ABDULHAMID [cite: 1359]",
        "NASSER ALDAWSARI [cite: 1340]", "ABDULLAH ALKHAIBARI [cite: 1341]",
        "MUSAB ALJUWAYR [cite: 1342]", "FERAS ALBRIKAN [cite: 1353]",
        "SALEM ALDAWSARI [cite: 1354]", "SALEH ABU ALSHAMAT [cite: 1355]",
        "SALEH ALSHEHRI [cite: 1364]",
    ]},
    {"equipo": "Uruguay [cite: 102, 1365]", "jugadores": [
        "SERGIO ROCHET [cite: 1386]", "JOSÉ MARÍA GIMÉNEZ [cite: 1387]",
        "RONALD ARAÚJO [cite: 1390]", "SEBASTIÁN CÁCERES [cite: 1391]",
        "MATHIAS OLIVERA [cite: 1375]", "NAHITAN NÁNDEZ [cite: 1376]",
        "FEDERICO VALVERDE [cite: 1377]", "RODRIGO BENTANCUR [cite: 1392]",
        "MANUEL UGARTE [cite: 1393]", "FACUNDO PELLISTRI [cite: 1394, 1395]",
        "DARWIN NÚÑEZ [cite: 1398]",
    ]},
    {"equipo": "France [cite: 104, 1399]", "jugadores": [
        "MIKE MAIGNAN [cite: 1418]", "WILLIAM SALIBA [cite: 1419, 1421]",
        "JULES KOUNDÉ [cite: 1428]", "THEO HERNÁNDEZ [cite: 1429, 1430]",
        "AURELIEN TCHOUAMÉNI [cite: 1411]", "EDUARDO CAMAVINGA [cite: 1412]",
        "OUSMANE DEMBÉLÉ [cite: 1413]", "KYLIAN MBAPPÉ [cite: 1420, 1422]",
        "BRADLEY BARCOLA [cite: 1423]", "DÉSIRÉ DOUÉ [cite: 1424]",
        "HUGO EKITIKÉ [cite: 1437]",
    ]},
    {"equipo": "Senegal [cite: 108, 1438]", "jugadores": [
        "EDOUARD MENDY [cite: 1461, 1462]", "KALIDOU KOULIBALY [cite: 1463]",
        "MOUSSA NIAKHATÉ [cite: 1473]", "EL HADJI MALICK DIOUF [cite: 1474, 1475]",
        "IDRISSA GANA GUEYE [cite: 1445, 1446]", "PAPE MATAR SARR [cite: 1447]",
        "SADIO MANÉ [cite: 1448]", "ILIMAN NDIAYE [cite: 1464, 1467]",
        "KREPIN DIATTA [cite: 1465, 1468]", "ISMAILA SARR [cite: 1466, 1469]",
        "NICOLAS JACKSON [cite: 1483]",
    ]},
    {"equipo": "Iraq [cite: 112, 1484]", "jugadores": [
        "JALAL HASSAN [cite: 1507, 1512]", "HUSSEIN ALI [cite: 1508, 1513]",
        "AKAM HASHEM [cite: 1519]", "MERCHAS DOSKI [cite: 1520, 1521]",
        "ZAID TAHSEEN [cite: 1491]", "ZIDANE IQBAL [cite: 1492, 1493]",
        "AMIR AL-AMMARI [cite: 1494]", "IBRAHIM BAYESH [cite: 1509, 1514]",
        "ALI JASSIM [cite: 1510, 1515]", "AYMEN SHER [cite: 1511, 1516]",
        "MOHANAD ALI [cite: 1529]",
    ]},
    {"equipo": "Norway [cite: 116, 1530]", "jugadores": [
        "ØRJAN NYLAND [cite: 1553, 1554]", "JULIAN RYERSON [cite: 1555]",
        "KRISTOFFER VASSBAKK AJER [cite: 1564]", "DAVID MØLLER WOLFE [cite: 1565, 1566]",
        "MARTIN ØDEGAARD [cite: 1537, 1539]", "SANDER BERGE [cite: 1538, 1540]",
        "PATRICK BERG [cite: 1541]", "ERLING HAALAND [cite: 1556, 1558]",
        "ANTONIO NUSA [cite: 1557, 1559]", "OSCAR BOBB [cite: 1560]",
        "ALEXANDER SØRLOTH [cite: 1569]",
    ]},
    {"equipo": "Argentina [cite: 106, 1570]", "jugadores": [
        "EMILIANO MARTÍNEZ [cite: 1590, 1591]", "NAHUEL MOLINA [cite: 1592]",
        "CRISTIAN ROMERO [cite: 1598]", "NICOLAS OTAMENDI [cite: 1599]",
        "ENZO FERNÁNDEZ [cite: 1578]", "ALEXIS MAC ALLISTER [cite: 1579, 1580]",
        "RODRIGO DE PAUL [cite: 1581]", "JULIAN ÁLVAREZ [cite: 1593]",
        "LIONEL MESSI [cite: 1594]", "GIULIANO SIMEONE [cite: 1595]",
        "LAUTARO MARTÍNEZ [cite: 1604, 1605]",
    ]},
    {"equipo": "Algeria [cite: 110, 1606]", "jugadores": [
        "ALEXIS GUENDOUZ [cite: 1627, 1628]", "RAYAN AÏT-NOURI [cite: 1629]",
        "RAMY BENSEBAINI [cite: 1638]", "YOUCEF ATAL [cite: 1639]",
        "AISSA MANDI [cite: 1616]", "NABIL BENTALEB [cite: 1617]",
        "RIYAD MAHREZ [cite: 1618]", "SAID BENRAHMA [cite: 1630, 1631]",
        "AMINE GOUIRI [cite: 1632]", "MOHAMED AMOURA [cite: 1633, 1634]",
        "BAGHDAD BOUNEDJAH [cite: 1645, 1646]",
    ]},
    {"equipo": "Austria [cite: 114, 1647]", "jugadores": [
        "ALEXANDER SCHLAGER [cite: 1665, 1666]", "DAVID ALABA [cite: 1667]",
        "KEVIN DANSO [cite: 1675]", "PHILIPP LIENHART [cite: 1676]",
        "KONRAD LAIMER [cite: 1653]", "NICOLAS SEIWALD [cite: 1654]",
        "MARCEL SABITZER [cite: 1655]", "FLORIAN GRILLITSCH [cite: 1668]",
        "MARKO ARNAUTOVIĆ [cite: 1669]", "CHRISTOPH BAUMGARTNER [cite: 1670, 1671]",
        "MICHAEL GREGORITSCH [cite: 1680]",
    ]},
    {"equipo": "Jordan [cite: 118, 1681]", "jugadores": [
        "YAZEED ABULAILA [cite: 1701]", "MOHAMMAD ABU HASHISH [cite: 1702]",
        "YAZAN AL-ARAB [cite: 1707]", "ABDALLAH NASIB [cite: 1708, 1709]",
        "IBRAHIM SAADEH [cite: 1690]", "NIZAR AL-RASHDAN [cite: 1691, 1692]",
        "NOOR AL-RAWABDEH [cite: 1693]", "YAZAN AL-NAIMAT [cite: 1703]",
        "MOUSA AL-TAAMARI [cite: 1712, 1713]", "MAHMOUD AL-MARDI [cite: 1714]",
        "ALI OLWAN [cite: 1716]",
    ]},
    {"equipo": "Portugal [cite: 120, 1717]", "jugadores": [
        "DIOGO COSTA [cite: 1730]", "RÚBEN DIAS [cite: 1731]",
        "NUNO MENDES [cite: 1742]", "VITINHA [cite: 1743]",
        "BERNARDO SILVA [cite: 1725]", "BRUNO FERNANDES [cite: 1726]",
        "RÚBEN NEVES [cite: 1727]", "CRISTIANO RONALDO [cite: 1732]",
        "JOÃO FÉLIX [cite: 1733]", "PEDRO NETO [cite: 1734]",
        "RAFAEL LEÃO [cite: 1745, 1746]",
    ]},
    {"equipo": "Congo DR [cite: 123, 1747]", "jugadores": [
        "LIONEL MPASI [cite: 1769]", "AARON WAN-BISSAKA [cite: 1770]",
        "AXEL TUANZEBE [cite: 1778]", "ARTHUR MASUAKU [cite: 1779]",
        "CHANCEL MBEMBA [cite: 1754]", "NGALAVEL MUKAU [cite: 1755]",
        "SAMUEL MOUTOUSSAMY [cite: 1756, 1757]", "NOAH SADIKI [cite: 1771, 1773]",
        "THEO BONGONDA [cite: 1772, 1774]", "YOANE WISSA [cite: 1775]",
        "CEDRIC BAKAMBU [cite: 1786]",
    ]},
    {"equipo": "Uzbekistan [cite: 128, 1787]", "jugadores": [
        "UTKIR YUSUPOV [cite: 1809, 1810]", "ABDUKODIR KHUSANOV [cite: 1811]",
        "FARRUKH SAYFIEV [cite: 1821]", "SHERZOD NASRULLAEV [cite: 1822]",
        "HUSNIDDIN ALIQULOV [cite: 1795]", "RUSTAM ASHURMATOV [cite: 1796]",
        "KHOJIAKBAR ALIJONOV [cite: 1797]", "ODILJON HAMROBEKOV [cite: 1812, 1815]",
        "OTABEK SHUKUROV [cite: 1813, 1816]", "ELDOR SHOMURODOV [cite: 1814, 1817]",
        "ABBOSBEK FAYZULLAEV [cite: 1825, 1826]",
    ]},
    {"equipo": "Colombia [cite: 133, 1827]", "jugadores": [
        "CAMILO VARGAS [cite: 1846, 1847]", "DAVINSON SÁNCHEZ [cite: 1848]",
        "YERRY MINA [cite: 1854]", "DANIEL MUÑOZ [cite: 1855]",
        "JAMES RODRÍGUEZ [cite: 1834]", "JEFFERSON LERMA [cite: 1835]",
        "RICHARD RÍOS [cite: 1836]", "JUAN FERNANDO QUINTERO [cite: 1849]",
        "LUIS DÍAZ [cite: 1850]", "JHON ARIAS [cite: 1851]",
        "LUIS SUÁREZ [cite: 1857, 1858]",
    ]},
    {"equipo": "England [cite: 121, 1859]", "jugadores": [
        "JORDAN PICKFORD [cite: 1879, 1880]", "REECE JAMES [cite: 1881]",
        "JOHN STONES [cite: 1888]", "JUDE BELLINGHAM [cite: 1889]",
        "DECLAN RICE [cite: 1866]", "JORDAN HENDERSON [cite: 1867, 1868]",
        "PHIL FODEN [cite: 1869]", "HARRY KANE [cite: 1882, 1883]",
        "BUKAYO SAKA [cite: 1884]", "COLE PALMER [cite: 1885]",
        "MARCUS RASHFORD [cite: 1896, 1897]",
    ]},
    {"equipo": "Croatia [cite: 125, 1898]", "jugadores": [
        "DOMINIK LIVAKOVIĆ [cite: 1916, 1917]", "DUJE ĆALETA-CAR [cite: 1918]",
        "JOŠKO GVARDIOL [cite: 1925]", "JOSIP STANIŠIĆ [cite: 1926]",
        "IVAN PERIŠIĆ [cite: 1905]", "LUKA MODRIĆ [cite: 1906]",
        "MATEO KOVAČIĆ [cite: 1907]", "LOVRO MAJER [cite: 1919, 1920]",
        "MARIO PAŠALIĆ [cite: 1921]", "ANTE BUDIMIR [cite: 1922]",
        "ANDREJ KRAMARIĆ [cite: 1935, 1936]",
    ]},
    {"equipo": "Ghana [cite: 130, 1937]", "jugadores": [
        "LAWRENCE ATI-ZIGI [cite: 1958]", "ALIDU SEIDU [cite: 1959]",
        "ALEXANDER DJIKU [cite: 1968]", "GIDEON MENSAH [cite: 1969]",
        "CALEB EKUBAN [cite: 1944]", "THOMAS PARTEY [cite: 1945]",
        "ABDUL ISSAHAKU FATAWU [cite: 1946]", "MOHAMMED KUDUS [cite: 1960, 1961]",
        "KAMALDEEN SULEMANA [cite: 1962]", "JORDAN AYEW [cite: 1963, 1964]",
        "ANTOINE SEMENVO [cite: 1975, 1976]",
    ]},
    {"equipo": "Panama [cite: 135, 1977]", "jugadores": [
        "ORLANDO MOSQUERA [cite: 1996]", "MICHAEL AMIR MURILLO [cite: 1997]",
        "ANDRES ANDRADE [cite: 2004]", "FIDEL ESCOBAR [cite: 2005, 2006]",
        "ANIBAL GODOY [cite: 1982]", "CRISTIAN MARTINEZ [cite: 1983]",
        "ADALBERTO CARRASQUILLA [cite: 1984]", "EDGAR BÁRCENAS [cite: 1998]",
        "JOSE FAJARDO [cite: 1999, 2001]", "ISMAEL DÍAZ [cite: 2000, 2002]",
        "JOSE LUIS RODRÍGUEZ [cite: 2013, 2014]",
    ]},
]

# Maps JSON team name (as extracted from the equipo string) to canonical DB name.
# Must match the keys used in album_service._get_flags_mapping fallback_flags.
_TEAM_NAME_MAP = {
    "Mexico":            "MEXICO",
    "South Africa":      "SOUTH AFRICA",
    "Korea Republic":    "SOUTH KOREA",
    "Czechia":           "CZECHIA",
    "Canada":            "CANADA",
    "Bosnia-Herzegovina": "BOSNIA AND HERZEGOVINA",
    "Qatar":             "QATAR",
    "Switzerland":       "SWITZERLAND",
    "Brazil":            "BRAZIL",
    "Morocco":           "MOROCCO",
    "Haiti":             "HAITI",
    "Scotland":          "SCOTLAND",
    "USA":               "USA",
    "Paraguay":          "PARAGUAY",
    "Australia":         "AUSTRALIA",
    "Türkiye":           "TURKEY",
    "Germany":           "GERMANY",
    "Curaçao":           "CURACAO",
    "Côte d'Ivoire":     "IVORY COAST",
    "Ecuador":           "ECUADOR",
    "Netherlands":       "NETHERLANDS",
    "Japan":             "JAPAN",
    "Sweden":            "SWEDEN",
    "Tunisia":           "TUNISIA",
    "Belgium":           "BELGIUM",
    "Egypt":             "EGYPT",
    "IR Iran":           "IRAN",
    "New Zealand":       "NEW ZEALAND",
    "Spain":             "SPAIN",
    "Cabo Verde":        "CAPE VERDE",
    "Saudi Arabia":      "SAUDI ARABIA",
    "Uruguay":           "URUGUAY",
    "France":            "FRANCE",
    "Senegal":           "SENEGAL",
    "Iraq":              "IRAQ",
    "Norway":            "NORWAY",
    "Argentina":         "ARGENTINA",
    "Algeria":           "ALGERIA",
    "Austria":           "AUSTRIA",
    "Jordan":            "JORDAN",
    "Portugal":          "PORTUGAL",
    "Congo DR":          "DR CONGO",
    "Uzbekistan":        "UZBEKISTAN",
    "Colombia":          "COLOMBIA",
    "England":           "ENGLAND",
    "Croatia":           "CROATIA",
    "Ghana":             "GHANA",
    "Panama":            "PANAMA",
}

# Lineup order → position label (Adrenalyn XL standard ordering)
_POSITION_BY_INDEX = {
    0: "GK",
    1: "DEF", 2: "DEF", 3: "DEF",
    4: "MID", 5: "MID", 6: "MID",
    7: "FWD", 8: "FWD", 9: "FWD", 10: "FWD",
}


def _parse(raw: str):
    """Return (clean_name, [panini_codes]) from a cite-annotated string."""
    m = re.search(r'\[cite:\s*([0-9, \t]+)\]', raw)
    if not m:
        return raw.strip(), []
    name = raw[: m.start()].strip()
    codes = [int(c.strip()) for c in m.group(1).split(",") if c.strip().isdigit()]
    return name, codes


def _process_players(entry, team, add_fn):
    for idx, raw_player in enumerate(entry["jugadores"]):
        player_name, player_codes = _parse(raw_player)
        if not player_codes:
            continue
        position = _POSITION_BY_INDEX.get(idx, "FWD")
        add_fn(name=player_name, category="Player", rarity="Common",
               team=team, panini_code=player_codes[0], position=position)
        if len(player_codes) > 1:
            add_fn(name=player_name, category="Fan Favourite", rarity="Epic",
                   team=team, panini_code=player_codes[1], position=position)


def handler(event, context):
    import os
    os.environ.setdefault("FLASK_ENV", "production")

    from app import create_app
    app = create_app()

    with app.app_context():
        from app.infrastructure.database import db
        from app.domain.models.sticker import Sticker
        from app.domain.models.rarity_cat import RarityCat

        rarity_map = {}
        for name in ("Common", "Rare", "Epic", "Legendary"):
            rc = RarityCat.query.filter_by(name=name).first()
            if not rc:
                rc = RarityCat(name=name)
                db.session.add(rc)
                db.session.commit()
            rarity_map[name] = rc.rarityCatId

        existing_codes = {st.paniniCode for st in Sticker.query.all()}
        added = 0

        def _add(*, name, category, rarity, team, panini_code, position=None):
            nonlocal added
            code = str(panini_code)
            if code in existing_codes:
                return
            db.session.add(Sticker(
                name=name,
                category=category,
                rarity=rarity,
                team=team,
                paniniCode=code,
                position=position,
                raretyCatId=rarity_map[rarity],
            ))
            existing_codes.add(code)
            added += 1

        for entry in _CATALOGUE:
            raw_team, team_codes = _parse(entry["equipo"])
            team = _TEAM_NAME_MAP.get(raw_team, raw_team.upper())

            # Team Crest uses the second cite code (official team intro card number)
            crest_code = team_codes[1] if len(team_codes) > 1 else team_codes[0]
            _add(name="TEAM CREST", category="Team Crest", rarity="Rare",
                 team=team, panini_code=crest_code)

            _process_players(entry, team, _add)

        db.session.commit()
        total = Sticker.query.count()

    logger.info({"event": "sticker_sync_complete", "added": added, "total": total})
    return {
        "statusCode": 200,
        "body": json.dumps({"added": added, "total": total}),
    }
