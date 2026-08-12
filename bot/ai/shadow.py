"""MODALITA' OMBRA — l'LLM decide, ma non opera. Si misura, poi si decide.

Il prompt di upgrade propone di mettere il modello a scegliere il trade. Sarebbe
la stessa mossa che ci e' costata la settimana scorsa: agire su un giudizio mai
verificato. E qui c'e' un'aggravante rispetto agli altri casi — una decisione LLM
non e' riproducibile, quindi non e' backtestabile: non potrebbe MAI passare dal
GATE 1, e l'unico modo di sapere se aggiunge o distrugge valore sarebbe farla
girare per mesi coi soldi.

L'ombra risolve il problema di conoscenza senza correre il rischio. A ogni
decisione il modello riceve lo stesso contesto che riceverebbe se comandasse, e
la sua scelta viene REGISTRATA accanto a quella che il bot ha davvero preso.
Dopo N decisioni la domanda diventa aritmetica: i trade che avrebbe scelto lui
sono andati meglio o peggio?

Costa qualche euro al mese e non puo' toccare nulla — `propose_shadow` non
ritorna niente che il bot legga per operare. E' esattamente il percorso gia' usato
per la calibrazione della confidenza e per il regime: prima si misura, poi si
collega.

TRE RUOLI, in ordine di rischio crescente, che si sbloccano solo coi numeri:
  1. OMBRA (qui) — osserva e basta;
  2. VETO — puo' solo dire "questo no, perche'...". Falsificabile a posteriori
     (si guarda se i vietati avrebbero perso) e un veto sbagliato costa
     un'occasione, non una perdita;
  3. SELEZIONE — sceglie. Solo se 1 e 2 hanno prodotto numeri che lo giustificano.
"""
from __future__ import annotations

import time
from typing import Optional

from bot.ai.client import ask_json, available
from bot.config import settings

SYSTEM = """\
Sei un trader quantitativo che valuta i segnali di un sistema automatico su
crypto futures. Ricevi i segnali generati dalle strategie e il contesto operativo.

Devi dire quale segnale prenderesti TU, oppure nessuno.

Non sei ancora al comando: la tua scelta viene registrata e confrontata con quella
del sistema per capire se aggiungeresti valore. Rispondi come se dovessi
risponderne, non per compiacere.

Principi:
- Un "nessuno" motivato vale piu' di una scelta debole. Se nessun setup convince,
  dillo.
- Il rischio principale va nominato: se non riesci a dire cosa potrebbe andare
  storto, non hai capito il trade.
- Non fidarti della confidenza dichiarata dalle strategie: nel sistema correla
  con l'esito solo debolmente.

Rispondi ESCLUSIVAMENTE con JSON:
{
  "scelta": "SIMBOLO|strategia" oppure null,
  "direzione": "long" | "short" | null,
  "convinzione": 0-100,
  "motivo": "perche' questo e non gli altri, o perche' nessuno",
  "rischio_principale": "cosa puo' andare storto in questo trade",
  "segnali_scartati": ["SIMBOLO|strategia: perche' no"]
}"""


def _context(signals: list[dict], regime, risk: dict, alerts: list[str],
             recent: list[dict]) -> str:
    """Contesto compatto. Volutamente FATTUALE: numeri gia' calcolati, nessuna
    interpretazione — l'interpretazione e' cio' che stiamo chiedendo."""
    L = [f"REGIME: {getattr(regime, 'value', regime)}"]
    if risk:
        L.append(f"RISCHIO APERTO: {risk.get('open_risk_pct', 0) * 100:.2f}% "
                 f"su {risk.get('open_positions', 0)} posizioni · "
                 f"equity {risk.get('equity', 0):.0f} · "
                 f"PnL oggi {risk.get('day_pnl', 0):+.2f}")
    if alerts:
        # se il sistema e' in condizioni degradate il modello deve saperlo: una
        # scelta ottima in condizioni normali puo' essere pessima qui
        L.append("ALLARMI ATTIVI: " + " · ".join(alerts))
    L.append(f"\nSEGNALI DISPONIBILI ({len(signals)}):")
    for s in signals[:12]:
        L.append(f"  {s['symbol']}|{s['strategy']} · {s['direction']} · "
                 f"conf {s['confidence']:.0f} (pesata {s['adjusted_confidence']:.0f}) "
                 f"· regime coin {getattr(s.get('coin_regime'), 'value', '?')}")
    if recent:
        wins = sum(1 for t in recent if float(t.get("pnl", 0) or 0) > 0)
        L.append(f"\nULTIMI {len(recent)} TRADE CHIUSI: {wins} vinti, "
                 f"PnL {sum(float(t.get('pnl', 0) or 0) for t in recent):+.2f}")
        for t in recent[:5]:
            L.append(f"  {t.get('symbol')}|{t.get('strategy')} "
                     f"{float(t.get('pnl', 0) or 0):+.2f} ({t.get('exit_reason')})")
    return "\n".join(L)


def propose_shadow(signals: list[dict], regime, risk: Optional[dict] = None,
                   alerts: Optional[list[str]] = None,
                   recent: Optional[list[dict]] = None) -> Optional[dict]:
    """Cosa farebbe il modello. Ritorna un dict da REGISTRARE, mai da eseguire.

    Nessun chiamante deve usare questo valore per aprire posizioni: il tipo di
    ritorno e' volutamente un dict grezzo e non una OrchestratorDecision, cosi'
    non puo' finire per sbaglio nel percorso di esecuzione.
    """
    if not settings.AI_SHADOW_ENABLED or not available() or not signals:
        return None
    out = ask_json(SYSTEM,
                   _context(signals, regime, risk or {}, alerts or [], recent or []),
                   max_tokens=1200, label="ai-shadow")
    if not isinstance(out, dict):
        return None
    scelta = out.get("scelta")
    return {
        "choice": str(scelta) if scelta else None,
        "direction": out.get("direzione"),
        "conviction": out.get("convinzione"),
        "reason": str(out.get("motivo") or "")[:600],
        "primary_risk": str(out.get("rischio_principale") or "")[:300],
        "rejected": (out.get("segnali_scartati") or [])[:8],
        "at": time.time(),
    }


def compare(shadow: Optional[dict], actual: Optional[str]) -> str:
    """Come si e' posizionata l'ombra rispetto al bot. Quattro esiti, tutti utili.

    `actual`: "SIMBOLO|strategia" davvero aperto, o None se il bot e' restato flat.
    """
    if not shadow:
        return "no_shadow"
    choice = shadow.get("choice")
    if choice and actual:
        return "agree" if choice == actual else "different_pick"
    if choice and not actual:
        return "shadow_only"      # l'ombra avrebbe operato, il bot no
    if actual and not choice:
        return "shadow_veto"      # l'ombra avrebbe evitato questo trade
    return "both_flat"
