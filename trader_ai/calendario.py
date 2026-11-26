"""L'ora del giorno e il calendario fisso (controllo del 26 novembre 2026, punto 3.11): se la borsa di New York è aperta, i suoi giorni
di chiusura, gli orari del funding. Solo orari pubblici e fissi: nessuna notizia, nessun dato dell'altra sessione.

I giorni di chiusura e di chiusura anticipata della borsa di New York (NYSE) vanno aggiornati ogni anno (fonte: il calendario
pubblicato dalla NYSE); fuori dagli anni scritti qui il messaggio non dice niente sulle feste. L'ora legale degli Stati Uniti si
calcola con il fuso «America/New_York» (se la macchina non ha i fusi orari, la riga della borsa si toglie).
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from typing import Optional

#: Giorni in cui la borsa di New York è chiusa (2026 e 2027).
FESTE_USA = {
    "2026-01-01": "Capodanno", "2026-01-19": "Martin Luther King", "2026-02-16": "Presidents' Day", "2026-04-03": "Venerdì santo",
    "2026-05-25": "Memorial Day", "2026-06-19": "Juneteenth", "2026-07-03": "Indipendenza (spostata)", "2026-09-07": "Labor Day",
    "2026-11-26": "Ringraziamento", "2026-12-25": "Natale",
    "2027-01-01": "Capodanno", "2027-01-18": "Martin Luther King", "2027-02-15": "Presidents' Day", "2027-03-26": "Venerdì santo",
    "2027-05-31": "Memorial Day", "2027-06-18": "Juneteenth (spostata)", "2027-07-05": "Indipendenza (spostata)",
    "2027-09-06": "Labor Day", "2027-11-25": "Ringraziamento", "2027-12-24": "Natale (spostato)",
}
#: Giorni in cui la borsa di New York chiude alle 13:00 di New York.
CHIUSURA_ANTICIPATA = {"2026-11-27", "2026-12-24", "2027-11-26"}
ANNI_NOTI = {2026, 2027}
FASCE = ((0, 7, "00-07 UTC"), (7, 13, "07-13 UTC"), (13, 17, "13-17 UTC"), (17, 24, "17-24 UTC"))
GIORNI = ("lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica")


def fascia(ora: datetime) -> str:
    h = ora.astimezone(timezone.utc).hour
    return next(nome for da, a, nome in FASCE if da <= h < a)


def _new_york():
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo("America/New_York")
    except Exception:  # noqa: BLE001 - senza fusi orari sulla macchina la riga della borsa non c'è
        return None


def _giorno_di_borsa(d: date) -> bool:
    return d.weekday() < 5 and d.isoformat() not in FESTE_USA


def _orari(d: date, ny) -> tuple:
    """Apertura e chiusura della borsa di New York nel giorno `d` di New York, in UTC."""
    chiude = time(13, 0) if d.isoformat() in CHIUSURA_ANTICIPATA else time(16, 0)
    return (datetime.combine(d, time(9, 30), tzinfo=ny).astimezone(timezone.utc),
            datetime.combine(d, chiude, tzinfo=ny).astimezone(timezone.utc))


def _prossima(d: date, ny) -> Optional[str]:
    for k in range(1, 11):
        g = d + timedelta(days=k)
        if g.year not in ANNI_NOTI:
            return None
        if _giorno_di_borsa(g):
            apre, chiude = _orari(g, ny)
            anticipata = f", chiusura anticipata alle {chiude:%H:%M} UTC" if g.isoformat() in CHIUSURA_ANTICIPATA else ""
            return f"prossima apertura {GIORNI[g.weekday()]} {g:%d/%m} alle {apre:%H:%M} UTC{anticipata}"
    return None


def borsa_usa(ora: datetime) -> Optional[str]:
    """Una riga sulla borsa di New York, detta con l'ora di New York (fra mezzanotte e le 5 UTC a New York è ancora il giorno
    prima: revisione del 26 novembre 2026, punto M3), o None se non si può dire (fusi orari mancanti, anno non scritto qui)."""
    ny = _new_york()
    if ny is None:
        return None
    locale = ora.astimezone(ny)
    d = locale.date()
    if d.year not in ANNI_NOTI:
        return None
    testa = f"a New York è {GIORNI[locale.weekday()]} {locale:%d/%m %H:%M}"
    if _giorno_di_borsa(d):
        apre, chiude = _orari(d, ny)
        anticipata = " (chiusura anticipata)" if d.isoformat() in CHIUSURA_ANTICIPATA else ""
        if ora < apre:
            return f"{testa}: borsa non ancora aperta, apre alle {apre:%H:%M} UTC e chiude alle {chiude:%H:%M} UTC{anticipata}"
        if ora < chiude:
            return f"{testa}: borsa aperta fino alle {chiude:%H:%M} UTC{anticipata}"
        stato = "borsa già chiusa"
    elif d.isoformat() in FESTE_USA:
        stato = f"borsa chiusa tutto il giorno (festa: {FESTE_USA[d.isoformat()]})"
    else:
        stato = "borsa chiusa (fine settimana)"
    prossima = _prossima(d, ny)
    return f"{testa}: {stato}" + (f"; {prossima}" if prossima else "")


def riga_orari(ora: datetime) -> str:
    u = ora.astimezone(timezone.utc)
    parti = [f"{GIORNI[u.weekday()]} {u.strftime('%d/%m %H:%M')} UTC, fascia {fascia(u)}"]
    borsa = borsa_usa(u)
    if borsa:
        parti.append(borsa)
    parti.append("funding alle 00, 08 e 16 UTC")
    return "; ".join(parti)
