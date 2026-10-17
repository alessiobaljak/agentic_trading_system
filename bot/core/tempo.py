"""IL GIORNO DEL PROPRIETARIO (28 set 2026).

PERCHE'. Il proprietario legge le giornate in ora italiana; i report e il
controllo orario le contavano per giorno UTC di uscita; la dashboard contava
solo i trade delle validate decisi dalla strategia mentre il report del
portafoglio sommava tutto (28 set: «+3,25 sul conto, +1,26 sulle sole validate»
per lo stesso 27 settembre). Tre conti diversi per la stessa parola «giornata».

Qui vive UNA sola definizione di giorno, usata da tutti i lettori che dicono
«oggi» o «ultime 7 giornate»: il controllo orario (`bot/learning/controllo.py`),
il portafoglio simulato (`bot/risk/portafoglio.py`, `scripts/portafoglio_backtest.py`)
e `scripts/trade_stats.py`. Le candele e i timestamp dei trade restano in UTC
(`exit_ts`, `open_time`): cambia solo il modo di raggrupparli per giorno.

Il fuso e' `Europe/Rome` via `zoneinfo` (ora legale compresa). Se il sistema
non ha il database dei fusi (tzdata assente) si ripiega su UTC+2 FISSO e lo si
dice una volta: in inverno sbaglierebbe di un'ora sul confine, meglio di
tornare in silenzio all'UTC.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone, tzinfo

#: il fuso delle giornate: quello del proprietario
GIORNO_TZ = "Europe/Rome"

_FUSO: tzinfo | None = None
_RIPIEGO = False


def fuso() -> tzinfo:
    """Il tzinfo di `GIORNO_TZ`; UTC+2 fisso se tzdata manca (dichiarato)."""
    global _FUSO, _RIPIEGO
    if _FUSO is None:
        try:
            from zoneinfo import ZoneInfo
            _FUSO = ZoneInfo(GIORNO_TZ)
        except Exception:  # noqa: BLE001 — tzdata assente o modulo mancante
            _FUSO = timezone(timedelta(hours=2), "UTC+2")
            _RIPIEGO = True
            print(f"[tempo] fuso {GIORNO_TZ} non disponibile: giornate a UTC+2 fisso")
    return _FUSO


def ripiego_attivo() -> bool:
    """True se le giornate sono a UTC+2 fisso perche' manca tzdata."""
    fuso()
    return _RIPIEGO


def giorno_locale(ts: float) -> str:
    """`YYYY-MM-DD` del giorno in ora italiana in cui cade l'epoch `ts`."""
    return datetime.fromtimestamp(float(ts), tz=fuso()).strftime("%Y-%m-%d")


def inizio_giorno_locale(ts: float) -> float:
    """L'epoch della mezzanotte italiana del giorno in cui cade `ts`."""
    d = datetime.fromtimestamp(float(ts), tz=fuso())
    return d.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()


def giorno_da_iso(raw) -> str | None:
    """Il giorno italiano di una stringa ISO (naive = UTC); None se illeggibile."""
    if not raw:
        return None
    try:
        d = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(fuso()).strftime("%Y-%m-%d")
