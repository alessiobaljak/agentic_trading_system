"""
====================================================================================
 LIMITI DI SICUREZZA HARDCODED — NON MODIFICABILI DA NESSUNO
====================================================================================
Questi valori NON stanno su Firebase, NON stanno in config.py, NON entrano MAI nel
prompt dell'LLM. Sono l'ultima linea di difesa: né l'utente dalla dashboard, né
l'orchestratore LLM, né una strategia possono superarli.

Qualunque richiesta di trade passa dal `final_gate` del RiskManager che applica
questi cap. Modificare questo file è l'UNICO modo per cambiarli, ed è una scelta
deliberata di chi mantiene il codice (non un parametro operativo).
====================================================================================
"""
from __future__ import annotations

# --- Hard cap assoluti sui parametri di rischio ---
MAX_LEVERAGE: float = 5.0           # leva massima assoluta, mai superabile
MAX_RISK_PER_TRADE: float = 0.03    # 3% del capitale a rischio per trade, mai superabile

# --- Circuit breakers ---
DAILY_LOSS_LIMIT: float = 0.05      # stop totale se perdita giornaliera > 5% (catastrofe)
# pausa GLOBALE: ora è solo un backstop di sicurezza per un crollo sistemico (molti
# stop di fila su TUTTE le strategie). L'adattamento normale è per-strategia (panchina),
# così il bot non si ferma del tutto: continua con le strategie che funzionano.
CONSECUTIVE_SL_LIMIT: int = 6       # n. di stop loss consecutivi che innescano la pausa
CONSECUTIVE_SL_PAUSE: int = 2 * 3600  # pausa di 2 ore (secondi) dopo gli SL consecutivi
HIGH_VOL_SIGMA: float = 3.0         # volatilità > 3 sigma -> size dimezzata
HIGH_VOL_SIZE_FACTOR: float = 0.5   # fattore di riduzione size in alta volatilità
MACRO_FLAT_HOURS: float = 2.0       # flat obbligatorio 2h prima/dopo evento macro high-impact

# --- Riduzione automatica della leva in alta volatilità (scaglioni) ---
# soglia di volatilità (sigma) -> leva massima consentita dal sistema
VOLATILITY_LEVERAGE_CAPS: tuple[tuple[float, float], ...] = (
    (3.0, 2.0),   # vol > 3 sigma  -> max 2x
    (2.0, 3.0),   # vol > 2 sigma  -> max 3x
    (1.5, 4.0),   # vol > 1.5 sigma -> max 4x
)


def safety_leverage_cap(volatility_sigma: float) -> float:
    """
    Cap di leva calcolato dal SISTEMA in base alla volatilità corrente.
    È sempre <= MAX_LEVERAGE. La leva effettiva sarà il minimo tra questo,
    il valore utente e MAX_LEVERAGE.
    """
    cap = MAX_LEVERAGE
    for sigma_threshold, lev_cap in VOLATILITY_LEVERAGE_CAPS:
        if volatility_sigma >= sigma_threshold:
            cap = min(cap, lev_cap)
    return cap


def safety_risk_cap(volatility_sigma: float) -> float:
    """Cap di rischio calcolato dal sistema: size dimezzata se vol > 3 sigma."""
    if volatility_sigma >= HIGH_VOL_SIGMA:
        return MAX_RISK_PER_TRADE * HIGH_VOL_SIZE_FACTOR
    return MAX_RISK_PER_TRADE
