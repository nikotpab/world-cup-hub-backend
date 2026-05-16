"""
Motor de cuotas deportivas basado en distribución de Poisson (modelo Dixon-Coles simplificado).

Fórmula:
    λ_local  = μ × (ataque_local  / defensa_visitante) × ventaja_local
    λ_visita = μ × (ataque_visita / defensa_local)

    P(goles = k) = e^-λ × λ^k / k!

    P(local gana) = Σ P(h > a)   para h,a ∈ [0..MAX_GOALS]
    cuota decimal  = (1 / P) × (1 − margen_casa)
"""
import math
from typing import Dict, Any

# ── Parámetros globales ──────────────────────────────────────────────────────
MU              = 1.30   # goles promedio por equipo en WC (histórico)
HOME_ADVANTAGE  = 1.10   # ventaja de jugar como local
MARGIN          = 0.07   # margen de la casa (7 %)
MAX_GOALS       = 8      # máximo de goles simulados

# ── Fuerza por equipo: (ataque, defensa) ─────────────────────────────────────
# Defensa: menor = mejor (concede menos goles)
TEAM_STRENGTH: Dict[str, Dict[str, float]] = {
    # Elite
    "Argentina":      {"atk": 1.80, "def": 0.72},
    "Francia":        {"atk": 1.70, "def": 0.75},
    "Brasil":         {"atk": 1.72, "def": 0.74},
    "España":         {"atk": 1.68, "def": 0.74},
    "Alemania":       {"atk": 1.55, "def": 0.82},
    "Portugal":       {"atk": 1.58, "def": 0.80},
    "Inglaterra":     {"atk": 1.52, "def": 0.83},
    "Países Bajos":   {"atk": 1.45, "def": 0.85},
    # Fuertes
    "Bélgica":        {"atk": 1.42, "def": 0.88},
    "Uruguay":        {"atk": 1.38, "def": 0.87},
    "Colombia":       {"atk": 1.30, "def": 0.92},
    "Croacia":        {"atk": 1.35, "def": 0.88},
    "Suiza":          {"atk": 1.28, "def": 0.90},
    "Marruecos":      {"atk": 1.25, "def": 0.88},
    "Estados Unidos": {"atk": 1.35, "def": 0.90},
    "México":         {"atk": 1.32, "def": 0.92},
    "Canadá":         {"atk": 1.12, "def": 0.95},
    # Medios
    "Japón":          {"atk": 1.20, "def": 0.94},
    "Corea del Sur":  {"atk": 1.22, "def": 0.95},
    "Senegal":        {"atk": 1.18, "def": 0.96},
    "Ecuador":        {"atk": 1.15, "def": 0.97},
    "Noruega":        {"atk": 1.15, "def": 0.96},
    "Austria":        {"atk": 1.10, "def": 0.98},
    "Turquía":        {"atk": 1.12, "def": 0.97},
    "Suecia":         {"atk": 1.08, "def": 0.98},
    "Australia":      {"atk": 1.05, "def": 1.00},
    "Polonia":        {"atk": 1.10, "def": 0.98},
    "Escocia":        {"atk": 1.02, "def": 1.02},
    "Paraguay":       {"atk": 1.05, "def": 1.00},
    "Ghana":          {"atk": 1.08, "def": 1.00},
    "Túnez":          {"atk": 1.00, "def": 1.02},
    "Egipto":         {"atk": 1.05, "def": 1.00},
    "Costa de Marfil":{"atk": 1.10, "def": 0.98},
    "Argelia":        {"atk": 1.00, "def": 1.02},
    "Catar":          {"atk": 0.95, "def": 1.05},
    "Arabia Saudita": {"atk": 0.98, "def": 1.03},
    "Irán":           {"atk": 1.00, "def": 1.02},
    "Irak":           {"atk": 0.92, "def": 1.05},
    "Jordania":       {"atk": 0.90, "def": 1.06},
    "Nueva Zelanda":  {"atk": 0.88, "def": 1.08},
    "Panamá":         {"atk": 0.90, "def": 1.06},
    "Uzbekistán":     {"atk": 0.92, "def": 1.05},
    "Curazao":        {"atk": 0.85, "def": 1.10},
    "Haití":          {"atk": 0.85, "def": 1.10},
    "Bosnia y Herzegovina": {"atk": 1.05, "def": 1.00},
    "República Checa":      {"atk": 1.05, "def": 1.00},
    "Cabo Verde":           {"atk": 0.95, "def": 1.05},
    "Congo RD":             {"atk": 0.95, "def": 1.05},
    "Sudáfrica":            {"atk": 0.95, "def": 1.05},
}

_DEFAULT = {"atk": 1.00, "def": 1.00}

# Alias inglés → español para equipos que vienen de la API
_NAME_ALIAS = {
    "Argentina": "Argentina", "France": "Francia", "Brazil": "Brasil",
    "Spain": "España", "Germany": "Alemania", "Portugal": "Portugal",
    "England": "Inglaterra", "Netherlands": "Países Bajos",
    "Belgium": "Bélgica", "Uruguay": "Uruguay", "Colombia": "Colombia",
    "Croatia": "Croacia", "Switzerland": "Suiza", "Morocco": "Marruecos",
    "USA": "Estados Unidos", "Mexico": "México", "Canada": "Canadá",
    "Japan": "Japón", "Korea Republic": "Corea del Sur", "Senegal": "Senegal",
    "Ecuador": "Ecuador", "Norway": "Noruega", "Austria": "Austria",
    "Turkey": "Turquía", "Sweden": "Suecia", "Australia": "Australia",
    "Poland": "Polonia", "Scotland": "Escocia", "Paraguay": "Paraguay",
    "Ghana": "Ghana", "Tunisia": "Túnez", "Egypt": "Egipto",
    "Ivory Coast": "Costa de Marfil", "Algeria": "Argelia",
    "Qatar": "Catar", "Saudi Arabia": "Arabia Saudita", "Iran": "Irán",
    "Iraq": "Irak", "Jordan": "Jordania", "New Zealand": "Nueva Zelanda",
    "Panama": "Panamá", "Uzbekistan": "Uzbekistán", "Curaçao": "Curazao",
    "Haiti": "Haití", "Bosnia-H.": "Bosnia y Herzegovina",
    "Czechia": "República Checa", "Cape Verde": "Cabo Verde",
    "Congo DR": "Congo RD", "South Africa": "Sudáfrica",
}


def _resolve(name: str) -> Dict[str, float]:
    spanish = _NAME_ALIAS.get(name, name)
    return TEAM_STRENGTH.get(spanish, TEAM_STRENGTH.get(name, _DEFAULT))


def _poisson(k: int, lam: float) -> float:
    return (lam ** k) * math.exp(-lam) / math.factorial(k)


def _decimal_odds(p: float) -> float:
    if p < 1e-6:
        return 99.0
    raw = 1.0 / p
    return round(raw * (1.0 - MARGIN), 2)


def calculate_odds(home_team: str, away_team: str, market_volumes: Dict[str, float] = None) -> Dict[str, Any]:
    h_str = _resolve(home_team)
    a_str = _resolve(away_team)

    # Dixon-Coles: λ = μ × ataque × resistencia_defensa_rival × ventaja_local
    lam_home = MU * h_str["atk"] * a_str["def"] * HOME_ADVANTAGE
    lam_away = MU * a_str["atk"] * h_str["def"]

    p_home = p_draw = p_away = 0.0
    score_probs: Dict[str, float] = {}

    for h in range(MAX_GOALS + 1):
        ph = _poisson(h, lam_home)
        for a in range(MAX_GOALS + 1):
            pa = _poisson(a, lam_away)
            p = ph * pa
            score_probs[f"{h}-{a}"] = p
            if h > a:
                p_home += p
            elif h == a:
                p_draw += p
            else:
                p_away += p

    # Normalizar estadísticas
    total_stat = p_home + p_draw + p_away
    p_home /= total_stat
    p_draw /= total_stat
    p_away /= total_stat

    # ── Ajuste Dinámico (Market Sentiment) ───────────────────────────────────
    # Si hay apuestas reales, mezclamos la probabilidad estadística con la del mercado
    if market_volumes:
        total_staked = sum(market_volumes.values())
        if total_staked > 0:
            # Probabilidades del mercado (qué porcentaje del dinero está en cada lado)
            m_home = market_volumes.get("home_win", 0) / total_staked
            m_draw = market_volumes.get("draw", 0) / total_staked
            m_away = market_volumes.get("away_win", 0) / total_staked
            
            # Peso de la estadística vs mercado (0.6 stat / 0.4 mercado)
            # Esto evita que una sola apuesta grande mueva la cuota a extremos absurdos
            W = 0.6 
            p_home = (p_home * W) + (m_home * (1 - W))
            p_draw = (p_draw * W) + (m_draw * (1 - W))
            p_away = (p_away * W) + (m_away * (1 - W))
            
            # Re-normalizar
            t = p_home + p_draw + p_away
            p_home /= t; p_draw /= t; p_away /= t

    # Top 8 marcadores por probabilidad (con cuota)
    top_scores = sorted(score_probs.items(), key=lambda x: -x[1])[:8]

    return {
        "home_win": _decimal_odds(p_home),
        "draw":     _decimal_odds(p_draw),
        "away_win": _decimal_odds(p_away),
        "prob_home": round(p_home * 100, 1),
        "prob_draw": round(p_draw * 100, 1),
        "prob_away": round(p_away * 100, 1),
        "expected_goals": {
            "home": round(lam_home, 2),
            "away": round(lam_away, 2),
        },
        "top_scores": [
            {"score": s, "odds": _decimal_odds(p / total_stat), "prob": round(p / total_stat * 100, 1)}
            for s, p in top_scores
        ],
    }
