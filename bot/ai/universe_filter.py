"""FILTRO DI CONTESTO SULL'UNIVERSO — su cosa vale la pena spendere validazione.

Il gate valuta ~1464 coppie per passata e ne promuove una manciata. Ogni coin in
piu' nell'imbuto e' un'estrazione in piu' della lotteria: con abbastanza tentativi
qualcuno passa per caso. Ridurre l'universo a quello che ha senso studiare riduce
il confronto multiplo alla radice, che e' piu' efficace di qualsiasi soglia
applicata dopo.

Caso reale: BIRBUSDT, quotata da 191 giorni, e' stata validata (PF 1.51) e nel
paper ha fatto PF 0.16. Il gate non aveva modo di sapere che stava guardando i
primi mesi di vita di una listing nuova — una fase di mercato sola, molto
direzionale, che non si ripete. E' un giudizio di contesto, non una soglia.

FAIL-OPEN: senza AI, o se la risposta non copre un simbolo, quel simbolo RESTA.
Un filtro che sbaglia togliendo e' peggio di nessun filtro: il gate a valle sa
comunque bocciare, mentre una coin scartata qui non ha appello.
"""
from __future__ import annotations

from typing import Iterable, Optional

from bot.ai.client import ask_json, available
from bot.config import settings

SYSTEM = """\
Ricevi coin di crypto futures con qualche misura oggettiva. Devi dire su quali
vale la pena spendere una validazione statistica costosa, e su quali no.

Scarta una coin quando c'e' una ragione STRUTTURALE per cui i risultati storici
non si ripeteranno:
- storia troppo corta o interamente dentro la fase di scoperta del prezzo di una
  listing recente (un solo regime, molto direzionale, non rappresentativo);
- liquidita' cosi' bassa che spread e slippage mangerebbero qualunque edge;
- token il cui prezzo dipende da eventi discreti (unlock, migrazioni, airdrop)
  piu' che dalla dinamica di mercato.

NON scartare una coin solo perche' e' volatile o piccola: la volatilita' e'
materia prima, non un difetto. Nel dubbio, TIENI: a valle c'e' un gate severo,
mentre una coin scartata qui non viene mai piu' guardata.

Rispondi ESCLUSIVAMENTE con JSON:
{"escludi": [{"symbol": "XUSDT", "motivo": "..."}]}
Elenca SOLO le coin da escludere. Le altre si intendono tenute."""


def _fmt(m: dict) -> str:
    bits = [m["symbol"]]
    if m.get("history_days") is not None:
        bits.append(f"storia {m['history_days']:.0f}gg")
    if m.get("volume_24h"):
        bits.append(f"volume24h ${m['volume_24h'] / 1e6:.1f}M")
    if m.get("atr_pct") is not None:
        bits.append(f"ATR {m['atr_pct'] * 100:.2f}%")
    return " · ".join(bits)


def filter_universe(metrics: Iterable[dict],
                    regime: Optional[str] = None) -> tuple[list[str], dict]:
    """(simboli da tenere, {simbolo: motivo di esclusione}).

    `metrics`: dizionari con almeno `symbol`, e quando disponibili
    `history_days`, `volume_24h`, `atr_pct`.
    """
    rows = [m for m in metrics if m.get("symbol")]
    keep_all = [m["symbol"] for m in rows]
    if not settings.AI_UNIVERSE_FILTER or not available() or not rows:
        return keep_all, {}

    user = ((f"Regime di mercato corrente: {regime}\n\n" if regime else "")
            + "Coin candidate:\n" + "\n".join(_fmt(m) for m in rows))
    out = ask_json(SYSTEM, user, max_tokens=2000, label="ai-universe")
    if not isinstance(out, dict):
        return keep_all, {}

    valid = set(keep_all)
    dropped: dict = {}
    for item in (out.get("escludi") or []):
        if not isinstance(item, dict):
            continue
        sym = item.get("symbol")
        if sym in valid:                     # mai inventare simboli non proposti
            dropped[sym] = str(item.get("motivo") or "")[:200]

    # GUARDIA: se il modello vuole svuotare l'universo, non gli si da' retta. Una
    # risposta che scarta quasi tutto e' quasi sempre un fraintendimento, e il
    # danno (nessuna coppia da validare) e' molto peggio del beneficio.
    if len(dropped) > len(rows) * 0.5:
        print(f"[ai-universe] scarterebbe {len(dropped)}/{len(rows)} coin: "
              f"troppe, filtro ignorato per sicurezza")
        return keep_all, {}
    if dropped:
        print(f"[ai-universe] escluse {len(dropped)}/{len(rows)} coin dal ciclo di validazione")
    return [s for s in keep_all if s not in dropped], dropped
