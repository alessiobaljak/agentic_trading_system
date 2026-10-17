"""I QUASI-PASSAGGI ALL'AI — apprendimento sulla RICERCA, non su una strategia.

Backlog B3, chiuso il 21 set 2026. Ogni giro della discovery produce ~40
quasi-passaggi: candidate fermate da UNA sola condizione, e di poco. Il 68%
muore su «ritorno totale», giro dopo giro. Finora si contavano i morti; nessuno
chiedeva perche'. Sono l'informazione piu' preziosa che un giro produce, perche'
dicono DOVE nello spazio delle strategie c'e' qualcosa che manca poco.

Qui i quasi-passaggi — con le loro feature, la coin, il criterio che li ha
fermati e di quanto — vengono dati al modello, che risponde con uno SCHEMA
(cosa hanno in comune) e con consigli per le proposte del giro stesso. I
consigli entrano nel contesto di `propose`; le proposte passano comunque dal
validatore e dal gate come tutte le altre.

L'AI NON DECIDE NIENTE: legge e suggerisce. Best-effort in ogni punto: un
giro di discovery non deve poter fallire perche' il modello non risponde.
"""
from __future__ import annotations

import time
from typing import Optional

from bot.ai.client import ask_json, available
from bot.config import settings

SYSTEM = """Sei un analista quantitativo. Ti do le strategie candidate che hanno
QUASI superato un gate di validazione walk-forward su crypto futures (una sola
condizione mancata, di poco), con le feature che usano, la coin, il criterio che
le ha fermate e lo scarto. Non conosci i dati di mercato: ragiona solo su cio'
che vedi.

Rispondi ESCLUSIVAMENTE con JSON:
{"schema": "cosa hanno in comune, 2-3 frasi concrete (feature, coin, criterio)",
 "ipotesi": ["fino a 3 ipotesi sul PERCHE' si fermano li'"],
 "consigli": "1-3 frasi operative per chi deve proporre nuove strategie in questo giro"}
Niente numeri inventati: se una cosa non si vede nei dati, dillo."""


# UN'AUTOPSIA PER TIMEFRAME (1 ott 2026, backlog K7). La passata a 1 ora gira
# PRIMA del giro a 15 minuti nello stesso timer, e fino al 30 set le due
# scrivevano lo stesso documento `gate_autopsy/discover`: il giro a 15 minuti
# leggeva i quasi-passaggi della passata a 1 ora credendoli suoi, e il prompt
# diceva comunque «Timeframe: 15m» (ops 0345, 0372). Ora il timeframe del bot
# resta su `discover` (lo leggono gate_progress, supervisore, istantanea) e
# ogni altro timeframe ha il suo `discover_<tf>`; il documento porta `interval`.
def doc_autopsia(interval: Optional[str] = None) -> str:
    """L'id del documento `gate_autopsy` della discovery per `interval`."""
    tf = str(interval or settings.ORCHESTRATOR_TIMEFRAME)
    return "discover" if tf == settings.ORCHESTRATOR_TIMEFRAME else f"discover_{tf}"


def e_del_timeframe(doc: Optional[dict], interval: Optional[str] = None) -> bool:
    """True se l'autopsia `doc` e' quella di `interval`. Un documento senza
    `interval` (scritto prima del 1 ott 2026) vale solo per il timeframe del bot,
    l'unico che poteva essere suo: e' l'ultima volta che succede, al primo giro
    col codice nuovo il documento porta il campo."""
    tf = str(interval or settings.ORCHESTRATOR_TIMEFRAME)
    if not isinstance(doc, dict):
        return False
    if doc.get("interval") is None:
        return tf == settings.ORCHESTRATOR_TIMEFRAME
    return str(doc.get("interval")) == tf


def _riga(n: dict, specs: dict) -> str:
    key = str(n.get("key", ""))
    sym, gid = (key.split("|", 1) + [""])[:2]
    sp = specs.get(gid) if isinstance(specs, dict) else None
    feats = "?"
    if isinstance(sp, dict):
        parti = []
        for f in sp.get("features") or []:
            k = f.get("kind")
            extra = ",".join(f"{a}={b}" for a, b in sorted(f.items()) if a != "kind")
            parti.append(f"{k}({extra})" if extra else str(k))
        feats = "+".join(parti) or "?"
        feats += f" adx>={sp.get('min_adx', 0)} atr={sp.get('atr_mult_stop')}"
    sf = n.get("shortfall")
    sf_txt = f"{float(sf):.3f}" if isinstance(sf, (int, float)) else "?"
    if n.get("numeri") == "holdout":
        # caduta sull'HOLDOUT (1 ott 2026, K7): soglia vera e numeri dell'holdout,
        # non piu' «scarto 0,000» coi numeri delle finestre che aveva superato
        return (f"- {sym} · {feats} · fermata sull'holdout ({n.get('criterio') or '?'}, "
                f"scarto {sf_txt}) · PF dell'holdout {n.get('pf', '?')} · "
                f"{n.get('trades', '?')} trade dell'holdout · PF senza i migliori "
                f"{n.get('pf_ex_top', '?')}")
    return (f"- {sym} · {feats} · fermata su {n.get('binding', '?')} "
            f"(scarto {sf_txt}) · PF {n.get('pf', '?')} · {n.get('trades', '?')} trade")


def analizza(fb, max_righe: int = 40, interval: Optional[str] = None) -> Optional[dict]:
    """Legge l'autopsia del giro precedente DELLO STESSO timeframe
    (`gate_autopsy/discover` per il timeframe del bot, `discover_<tf>` per gli
    altri: 1 ott 2026, K7), interroga il modello, salva l'esito in
    `ai_hypotheses/autopsia` e lo ritorna. None se non c'e' niente da leggere,
    se l'autopsia e' di un altro timeframe o se l'AI non e' disponibile."""
    if not available():
        return None
    tf = str(interval or settings.ORCHESTRATOR_TIMEFRAME)
    try:
        doc = fb.get_doc("gate_autopsy", doc_autopsia(tf)) or {}
        specs = (fb.get_doc("discovered_strategies", "specs") or {}).get("specs") or {}
        if isinstance(specs, str):
            from bot.core.firebase_client import decode_pairs
            specs = decode_pairs(specs)
    except Exception:  # noqa: BLE001
        return None
    if not e_del_timeframe(doc, tf):
        return None
    near = list(doc.get("near_misses") or [])[:max_righe]
    if not near:
        return None
    binding = doc.get("binding") or {}
    testa = ", ".join(f"{k}: {v}" for k, v in list(binding.items())[:5])
    user = (f"Ultimo giro: {doc.get('passed', '?')} passate su {doc.get('evaluated', '?')} "
            f"valutate. Criteri che fermano di piu': {testa or 'n/d'}.\n"
            f"Timeframe: {tf}.\n\n"
            f"I {len(near)} quasi-passaggi:\n" + "\n".join(_riga(n, specs) for n in near))
    out = ask_json(SYSTEM, user, max_tokens=1200, label="ai-autopsia")
    if not isinstance(out, dict) or not out.get("schema"):
        return None
    esito = {"at": time.time(), "n_quasi": len(near), "interval": tf,
             "schema": str(out.get("schema", ""))[:1200],
             "ipotesi": [str(x)[:400] for x in (out.get("ipotesi") or [])][:3],
             "consigli": str(out.get("consigli", ""))[:800]}
    try:
        fb.set_doc("ai_hypotheses", "autopsia", esito)
    except Exception as exc:  # noqa: BLE001
        print(f"[ai-autopsia] esito non salvato ({str(exc)[:80]})")
    return esito


def contesto_per_le_proposte(esito: Optional[dict]) -> str:
    """Il testo da accodare al contesto di `propose`: schema + consigli."""
    if not esito:
        return ""
    return (f"ANALISI DEI QUASI-PASSAGGI DEL GIRO PRECEDENTE ({esito.get('n_quasi')} "
            f"candidate fermate da una sola condizione):\n{esito.get('schema', '')}\n"
            f"Consigli: {esito.get('consigli', '')}")
