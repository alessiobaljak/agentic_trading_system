"""ANALISTA POST-MORTEM — legge il vissuto e dice cosa non torna.

E' il ruolo che in questi giorni abbiamo svolto a mano: mettere accanto la
promessa del gate e il risultato del paper, e capire DOVE si rompono. I difetti
trovati cosi' (la coda che non si ripete, il freno di deriva che non scattava, il
PF misurato con una scala diversa da quella eseguita) non erano visibili in
nessuna singola metrica: si vedevano solo confrontando piu' pezzi insieme. E'
esattamente il lavoro che un modello sa fare e una soglia no.

COSA NON FA: non tocca il registro, non apre/chiude posizioni, non cambia
parametri. Scrive un documento e basta. Ogni sua ipotesi e' un SOSPETTO da
verificare col gate o con uno script — mai un'azione.

L'input e' un DIGEST AGGREGATO, non i trade grezzi: qualche decina di righe di
numeri gia' calcolati. Serve a tenere il contesto piccolo e, soprattutto, a non
far "leggere il caso" al modello su 100 righe di rumore.
"""
from __future__ import annotations

import time
from collections import Counter, defaultdict
from statistics import median
from typing import Optional

from bot.ai.client import ask_json, available

SYSTEM = """\
Sei l'analista quantitativo di un sistema di trading crypto in paper trading.
Ricevi un digest aggregato: cosa il backtest (GATE 1) aveva promesso e cosa il
paper ha davvero prodotto.

Il tuo compito e' trovare DOVE promessa e realta' divergono, e proporre ipotesi
verificabili. Non devi incoraggiare ne' allarmare: devi essere utile.

Principi:
- Distingui sempre "campione troppo piccolo" da "segnale reale". Con pochi trade
  la risposta corretta e' "non si puo' dire": dirlo e' un'analisi valida.
- Preferisci una causa misurabile a una narrativa. "La coda >=3R e' meta' di
  quella del gate" vale piu' di "il mercato e' cambiato".
- Ogni ipotesi deve indicare COME si falsifica: quale numero guardare, quale
  confronto fare, quale soglia la smentirebbe.
- Se i dati non supportano nessuna conclusione, dillo e fermati.

Rispondi ESCLUSIVAMENTE con JSON:
{
  "verdetto": "una frase sullo stato di salute complessivo",
  "fiducia": "alta" | "media" | "bassa",
  "osservazioni": [
    {"titolo": "...", "evidenza": "i numeri che la sostengono",
     "quanto_e_solido": "cosa lo renderebbe piu' o meno certo"}
  ],
  "ipotesi": [
    {"ipotesi": "...", "come_verificarla": "il controllo concreto da fare",
     "cosa_la_smentirebbe": "..."}
  ],
  "cosa_non_si_puo_dire": ["domande a cui i dati NON rispondono"]
}"""


def _pct(part: int, tot: int) -> str:
    return f"{part / tot * 100:.0f}%" if tot else "—"


def build_digest(trades: list[dict], pairs: dict, drift: dict,
                 calibration: dict, equity: float | None = None) -> str:
    """Digest fattuale del vissuto. Solo numeri gia' calcolati, niente prosa."""
    L: list[str] = []
    n = len(trades)
    if not n:
        return "Nessun trade chiuso."

    pnls = [float(t.get("pnl", 0) or 0) for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]
    gross_w, gross_l = sum(wins), -sum(losses)
    L.append(f"TRADE CHIUSI: {n} · vinti {len(wins)} ({_pct(len(wins), n)}) "
             f"· PnL {sum(pnls):+.2f} · PF {gross_w / gross_l if gross_l else 0:.3f}")
    if wins and losses:
        L.append(f"  vincita media {gross_w / len(wins):+.2f} · perdita media "
                 f"{-gross_l / len(losses):+.2f} · rapporto "
                 f"{(gross_w / len(wins)) / (gross_l / len(losses)):.2f}x")
    if equity:
        L.append(f"  equity attuale {equity:.2f}")

    # uscite: dice se si esce per stop, per gradino o per orologio
    by_reason: dict = defaultdict(lambda: [0, 0.0])
    for t, p in zip(trades, pnls):
        r = by_reason[str(t.get("exit_reason", "?"))]
        r[0] += 1
        r[1] += p
    L.append("USCITE:")
    for reason, (c, p) in sorted(by_reason.items(), key=lambda kv: -kv[1][0]):
        L.append(f"  {reason}: {c} ({_pct(c, n)}) · PnL {p:+.2f} · media {p / c:+.2f}")

    # mfe: la misura di DOVE arriva il prezzo, la piu' informativa che abbiamo
    mfes = [float(t["mfe_r"]) for t in trades if t.get("mfe_r") is not None]
    if mfes:
        reach = " · ".join(f">={r:g}R {_pct(sum(1 for v in mfes if v >= r), len(mfes))}"
                           for r in (0.5, 1.0, 1.5, 2.0, 3.0, 5.0))
        L.append(f"ESCURSIONE FAVOREVOLE (mfe_r, {len(mfes)} trade): "
                 f"mediana {median(mfes):.2f}R · {reach}")
        L.append("  [mfe_r = quanto lontano e' andato il prezzo a favore, in unita' di R"
                 " (R = distanza dallo stop). Sotto scale-out il profitto viene dai"
                 " trade che superano i gradini alti.]")

    stages = Counter(int(t.get("scale_stage_reached", 0) or 0) for t in trades)
    L.append("GRADINI DI TP RAGGIUNTI: " + " · ".join(
        f"{k} TP: {v} ({_pct(v, n)})" for k, v in sorted(stages.items())))

    # promessa del gate contro vissuto, per coppia (solo quelle con abbastanza trade)
    per_pair: dict = defaultdict(list)
    for t, p in zip(trades, pnls):
        per_pair[f"{t.get('symbol')}|{t.get('strategy')}"].append(p)
    rows = sorted(per_pair.items(), key=lambda kv: -len(kv[1]))[:12]
    L.append("PROMESSA DEL GATE vs VISSUTO (coppie piu' operate):")
    orphans = 0
    for key, ps in rows:
        exp = float((pairs.get(key) or {}).get("last_pf", 0) or 0)
        g, l = sum(x for x in ps if x > 0), -sum(x for x in ps if x < 0)
        live = g / l if l else (999.0 if g else 0.0)
        # "atteso 0.00" sarebbe una bugia: il gate non promette mai zero. Zero vuol
        # dire che la coppia NON e' (piu') nel registro — purgata, scaduta per
        # freshness, o il registro e' stato ricostruito dopo quei trade. Dirlo
        # esplicitamente evita che l'analisi legga un artefatto come un dato.
        if exp <= 0:
            orphans += 1
            promise = "NESSUNA PROMESSA (coppia non presente nel registro attuale)"
        else:
            promise = f"atteso {exp:.2f}"
        L.append(f"  {key}: {len(ps)} trade · PF vissuto {live:.2f} vs {promise}"
                 f" · PnL {sum(ps):+.2f}")
    in_reg = sum(1 for k in per_pair if float((pairs.get(k) or {}).get("last_pf", 0) or 0) > 0)
    L.append(f"  [coppie operate presenti nel registro attuale: {in_reg}/{len(per_pair)}"
             f" · registro: {len(pairs)} coppie]")
    if orphans and in_reg == 0:
        L.append("  [ATTENZIONE: nessuna coppia operata risulta nel registro. I trade"
                 " sono precedenti a una ricostruzione/purga: il confronto"
                 " promessa-vs-vissuto NON e' possibile su questi dati.]")

    if drift:
        gl = drift.get("global") or {}
        if gl:
            L.append(f"RILEVATORE DI DERIVA (globale): {gl.get('verdict')} · "
                     f"{gl.get('trades')} trade · PF vissuto {gl.get('live_pf')} vs "
                     f"atteso {gl.get('expected_pf')} · {gl.get('reason', '')}")
    if calibration:
        L.append(f"CALIBRAZIONE CONFIDENZA: verdetto {calibration.get('verdict')} · "
                 f"correlazione {calibration.get('correlation')} · "
                 f"{calibration.get('trades')} trade")
    return "\n".join(L)


def analyze(trades: list[dict], pairs: dict, drift: dict | None = None,
            calibration: dict | None = None,
            equity: float | None = None) -> Optional[dict]:
    """Ritorna il report dell'analista, o None se l'AI non e' disponibile."""
    if not available() or not trades:
        return None
    digest = build_digest(trades, pairs or {}, drift or {}, calibration or {}, equity)
    out = ask_json(SYSTEM, digest, max_tokens=3000, label="ai-analyst")
    if not isinstance(out, dict):
        return None
    # il documento porta con se' il digest su cui e' stato prodotto: senza, una
    # conclusione letta domani non e' piu' verificabile contro i dati di oggi.
    out["digest"] = digest
    out["generated_at"] = time.time()
    out["n_trades"] = len(trades)
    return out
