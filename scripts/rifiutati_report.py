"""I SEGNALI RIFIUTATI AVREBBERO VINTO? — voce ops `rifiutati` (26 set 2026, J6).

Per ogni classe di motivo (cooldown, tetto per coin, peso sotto soglia,
posizione aperta, esplorative al tetto, veto di regime, margine, rischio
direzionale, stop troppo largo) stampa: quanti segnali, quanti valutati sulle
candele vere, R medio, % di vincenti, mfe mediana. Poi il confronto con i trade
APERTI dello stesso periodo (collection `trades`), in R.

LO STESSO PERIODO (1 ott 2026, J6). Gli aperti si prendono dall'istante del
PRIMO RIFIUTATO REGISTRATO nella finestra, contando l'ora d'INGRESSO del trade.
Fino al 30 set si prendevano tutti i trade USCITI negli ultimi 30 giorni: i
rifiutati si registrano solo dal 26 set, gli aperti partivano dal 16 set, e
dentro c'erano anche i giorni del difetto della sessione (fino al 26 set
−77,93 USDT, dal 27 +10,19, ops 0371). Per quattro mattine (ops 0329, 0350,
0370, 0398) il report ha scritto «posizione aperta: si puo' RITARARE» per
questo, non per i rifiutati. La riga APERTI dice da quando conta.

LA REGOLA, scritta prima di vedere i numeri: un freno si ritara SOLO se per un
motivo i rifiutati hanno R medio maggiore degli aperti con almeno 30 casi
valutati (`--min-casi`). Sotto i 30 e' un dato che non c'e' ancora, non un
verdetto. E anche sopra, questo report PROPONE: la modifica al freno passa dal
gate come tutte le altre. Il 1 ott la regola NON cambia: si applica davvero
«lo stesso periodo» che gia' prometteva. Accanto a ogni verdetto si stampa il
margine (2 errori standard della differenza) SOLO COME INFORMAZIONE: non entra
nel verdetto.

L'R DEGLI APERTI (1 ott 2026) e' quello di `bot.learning.drift.r_multiplo`, lo
stesso dei «conti in R» di scripts/trade_stats.py: netto (pnl) e lordo
(`gross_pnl_usdt`), tutti e due sul rischio all'ingresso con lo stop originale.
Chi non ha lo stop originale o la size resta fuori dall'R ed e' contato.

DUE AVVERTENZE che il report ripete in fondo: i rifiutati sono prezzo puro
(niente fee, slippage, funding), gli aperti netti sono NETTI di costi — a
parita' di tragitto i rifiutati sembrano ~0,1-0,2 R migliori (per questo si
stampa anche il lordo); e i rifiutati sono simulati sulla candela, gli aperti
eseguiti al mark.

Sola lettura, nessuna lettura in piu' di prima (la cache dei trade e una query
sui rifiutati). Senza Firebase (in locale, nei test) gira sullo store in
memoria: tutto vuoto, ed esce con 0.

Uso (sul VPS):
    .venv/bin/python -m scripts.rifiutati_report
    .venv/bin/python -m scripts.rifiutati_report --giorni 14 --min-casi 30
"""
from __future__ import annotations

import argparse
import math
import time
from datetime import datetime, timezone
from statistics import mean, median, stdev
from typing import Optional

from bot.core.firebase_client import get_firebase
from bot.core.tempo import fuso
from bot.learning import drift, rifiutati
from bot.learning.trade_logger import TradeLogger

#: casi valutati minimi perche' un confronto per motivo conti come un verdetto
MIN_CASI = 30


def _f(v) -> Optional[float]:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if f == f else None


def stop_originale(t: dict) -> Optional[float]:
    """Lo stop ORIGINALE del trade aperto (quello che definisce R): `orig_stop`
    se c'e', altrimenti ricostruito da `post_mortem.stop_pct`, altrimenti
    `stop_price` (che pero' e' spesso gia' a break-even: R stretto). Stessa
    scala di priorita' di scripts/mfe_report.stop_originale.

    1 ott 2026: l'R del report non passa piu' da qui ma da `drift.r_multiplo`
    (lo stesso dei conti in R, senza il ripiego su `stop_price`). Resta per chi
    la importa."""
    entry = _f(t.get("entry_price"))
    if not entry or entry <= 0:
        return None
    if _f(t.get("orig_stop")):
        return _f(t.get("orig_stop"))
    pm = t.get("post_mortem") or {}
    sp = _f(pm.get("stop_pct")) if isinstance(pm, dict) else None
    if sp and sp > 0:
        # `post_mortem.stop_pct` e' una FRAZIONE del prezzo (0,021 = 2,1%:
        # bot/risk/setup_check.analizza_setup). Fino al 27 set qui si divideva
        # ancora per 100: stop 100 volte piu' vicino, R degli aperti 100 volte piu'
        # grande (R medio −6,80 invece di −0,17, ops 0289). Un valore >= 1 non
        # puo' essere una frazione (stop al 100%): lo si legge come percentuale.
        frac = sp if sp < 1 else sp / 100.0
        long = str(t.get("direction", "")).lower().endswith("long")
        return entry * (1 - frac) if long else entry * (1 + frac)
    return _f(t.get("stop_price"))


def r_aperto(t: dict) -> Optional[float]:
    """R NETTO di un trade aperto: pnl in USDT diviso il rischio all'ingresso
    (|entry - stop originale| x quantita'). None se manca un pezzo.

    1 ott 2026: e' `drift.r_multiplo`, lo stesso R dei conti in R di
    scripts/trade_stats.py (ops 0388), cosi' i due report danno lo stesso
    numero per gli stessi trade."""
    return drift.r_multiplo(t)


def r_lordo(t: dict) -> Optional[float]:
    """R LORDO (1 ott 2026): `gross_pnl_usdt` sullo stesso rischio dell'R netto,
    come la riga «lordo» dei conti in R di scripts/trade_stats.py. None se il
    trade non porta il lordo o il rischio non si sa."""
    lordo = _f(t.get("gross_pnl_usdt"))
    stop = drift.stop_originale(t)
    entry, size = _f(t.get("entry_price")), _f(t.get("size"))
    if lordo is None or stop is None or entry is None or not size:
        return None
    rischio = abs(entry - stop) * size
    return lordo / rischio if rischio > 0 else None


def ora_ingresso(t: dict) -> Optional[float]:
    """L'epoch dell'INGRESSO del trade: `entry_ts`, altrimenti `entry_time`
    (ISO; senza fuso = UTC). None se non si legge (1 ott 2026)."""
    ts = _f(t.get("entry_ts"))
    if ts is not None:
        return ts
    raw = t.get("entry_time")
    if not raw:
        return None
    try:
        d = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.timestamp()


def ora_italiana(ts: float) -> str:
    """`26/09/2026 13:30` in ora italiana (bot/core/tempo.py)."""
    return datetime.fromtimestamp(float(ts), tz=fuso()).strftime("%d/%m/%Y %H:%M")


def aperti_del_periodo(trades: list, dal_ts: Optional[float]) -> dict:
    """I trade aperti da confrontare coi rifiutati (1 ott 2026): solo quelli
    ENTRATI da `dal_ts` (il primo rifiutato registrato), esplorativi esclusi.
    Senza `dal_ts` (nessun rifiutato) non c'e' un periodo comune: lista vuota.
    Torna la lista e quanti sono rimasti fuori, per motivo. Pura."""
    dentro, prima, senza_ora, esplorativi = [], 0, 0, 0
    for t in trades or []:
        if not isinstance(t, dict):
            continue
        # gli esplorativi non entrano nel confronto: size a un quarto e coppie
        # non validate, sarebbero un altro gruppo (F1bis)
        if t.get("esplorativa"):
            esplorativi += 1
            continue
        if dal_ts is None:
            continue
        ts = ora_ingresso(t)
        if ts is None:
            senza_ora += 1
        elif ts < dal_ts:
            prima += 1
        else:
            dentro.append(t)
    return {"trades": dentro, "dal_ts": dal_ts, "entrati_prima": prima,
            "senza_ora": senza_ora, "esplorativi": esplorativi}


def statistiche_aperti(trades: list[dict]) -> dict:
    """n, R netto medio, quota vincenti, mfe mediana dei trade aperti (quelli
    con R calcolabile; `senza_r` dice quanti sono rimasti fuori). Dal 1 ott 2026
    anche la deviazione standard dell'R netto (`pnl_r_dev`, per il margine) e
    l'R LORDO medio (`lordo_r_medio`) sui `lordo_n` trade che portano il lordo."""
    rs, lordi, mfes, senza = [], [], [], 0
    for t in trades:
        r = r_aperto(t)
        if r is None:
            senza += 1
            continue
        rs.append(r)
        lo = r_lordo(t)
        if lo is not None:
            lordi.append(lo)
        m = _f(t.get("mfe_r"))
        if m is not None:
            mfes.append(m)
    return {
        "n": len(rs), "senza_r": senza,
        "pnl_r_medio": round(mean(rs), 3) if rs else None,
        "pnl_r_dev": round(stdev(rs), 4) if len(rs) >= 2 else None,
        "lordo_n": len(lordi),
        "lordo_r_medio": round(mean(lordi), 3) if lordi else None,
        "quota_vincenti": round(sum(1 for r in rs if r > 0) / len(rs), 3) if rs else None,
        "mfe_r_mediana": round(median(mfes), 3) if mfes else None,
    }


def margine(rif: dict, aperti: dict) -> Optional[float]:
    """2 errori standard della differenza fra le due medie, contando ogni caso
    indipendente: 2 x sqrt(s1^2/n1 + s2^2/n2). None se un lato ha meno di 2
    casi. SOLO INFORMAZIONE (1 ott 2026): non entra nel verdetto. E' il margine
    trade per trade: nelle giornate nere perdono tutti insieme, quindi il
    margine vero e' probabilmente piu' largo (backlog H5)."""
    s1, n1 = rif.get("pnl_r_dev"), rif.get("valutati") or 0
    s2, n2 = aperti.get("pnl_r_dev"), aperti.get("n") or 0
    if s1 is None or s2 is None or n1 < 2 or n2 < 2:
        return None
    return 2.0 * math.sqrt(s1 ** 2 / n1 + s2 ** 2 / n2)


def _margine_testo(rif: dict, aperti: dict) -> str:
    p, a = rif.get("pnl_r_medio"), aperti.get("pnl_r_medio")
    mg = margine(rif, aperti)
    if p is None or a is None or mg is None:
        return " [margine: non calcolabile]"
    return f" [differenza {p - a:+.2f} ± {mg:.2f}, solo informazione]"


def verdetto(per_motivo: dict, aperti: dict, min_casi: int = MIN_CASI) -> list[str]:
    """Una riga per motivo: «ritarare» solo con >= min_casi valutati E R medio
    dei rifiutati > R medio degli aperti (gli aperti DELLO STESSO PERIODO: chi
    chiama li passa gia' filtrati, `aperti_del_periodo`). Il margine si
    aggiunge in coda come informazione, il verdetto non lo guarda. Pura."""
    righe = []
    r_ap = aperti.get("pnl_r_medio")
    for m, r in sorted(per_motivo.items(), key=lambda kv: -kv[1]["n"]):
        v, p = r["valutati"], r.get("pnl_r_medio")
        if v < min_casi or p is None:
            righe.append(f"  {m:<22} {v:>3}/{min_casi} valutati: campione insufficiente, nessun verdetto")
        elif r_ap is None:
            righe.append(f"  {m:<22} R {p:+.2f} ma senza aperti da confrontare: nessun verdetto")
        elif p > r_ap:
            righe.append(f"  {m:<22} R {p:+.2f} > aperti {r_ap:+.2f} su {v} casi: "
                         f"il freno si puo' RITARARE (proposta per il gate)"
                         + _margine_testo(r, aperti))
        else:
            righe.append(f"  {m:<22} R {p:+.2f} <= aperti {r_ap:+.2f} su {v} casi: il freno tiene"
                         + _margine_testo(r, aperti))
    return righe


def _fmt(v, spec: str = "+.2f") -> str:
    return "   —" if v is None else format(v, spec)


def stampa(r: dict, aperti: dict, min_casi: int, periodo: Optional[dict] = None) -> None:
    dal = datetime.fromtimestamp(r["dal"], tz=timezone.utc).strftime("%Y-%m-%d")
    print(f"SEGNALI RIFIUTATI — ultimi {r['giorni']} giorni (dal {dal} UTC): "
          f"{r['totale']} registrati")
    pm = r["per_motivo"]
    if not pm:
        print("  nessun segnale rifiutato registrato: l'ombra e' vuota (bot fermo, "
              "o riavviato senza il codice del 26 set).")
    else:
        print(f"  {'motivo':<22} {'segnali':>7} {'valutati':>8} {'attesa':>6} {'scaduti':>7} "
              f"{'R medio':>8} {'vincenti':>8} {'mfe med':>8}  esiti")
        for m, x in sorted(pm.items(), key=lambda kv: -kv[1]["n"]):
            esiti = ", ".join(f"{k} {v}" for k, v in sorted(x["esiti"].items(), key=lambda kv: -kv[1]))
            vinc = "   —" if x["quota_vincenti"] is None else f"{x['quota_vincenti'] * 100:4.0f}%"
            print(f"  {m:<22} {x['n']:>7} {x['valutati']:>8} {x['in_attesa']:>6} {x['scaduti']:>7} "
                  f"{_fmt(x['pnl_r_medio']):>8} {vinc:>8} {_fmt(x['mfe_r_mediana'], '.2f'):>8}  {esiti}")
    periodo = periodo or {}
    dal_ts = periodo.get("dal_ts", r.get("primo_ts"))
    if dal_ts is None:
        print("\nAPERTI: nessun rifiutato registrato, quindi nessun periodo comune: "
              "nessun confronto.")
    else:
        qv = aperti["quota_vincenti"]
        vinc_ap = "—" if qv is None else f"{qv * 100:.0f}%"
        print(f"\nAPERTI dal {ora_italiana(dal_ts)} ora italiana (primo rifiutato registrato), "
              f"per ora d'ingresso: {aperti['n']} trade con R ({aperti['senza_r']} senza R) · "
              f"R netto medio {_fmt(aperti['pnl_r_medio'])} · "
              f"R lordo medio {_fmt(aperti.get('lordo_r_medio'))} "
              f"(su {aperti.get('lordo_n', 0)} col lordo) · "
              f"vincenti {vinc_ap} · mfe mediana {_fmt(aperti['mfe_r_mediana'], '.2f')}")
        print(f"  fuori dal confronto: {periodo.get('entrati_prima', 0)} entrati prima e usciti dopo, "
              f"{periodo.get('senza_ora', 0)} senza ora d'ingresso, "
              f"{periodo.get('esplorativi', 0)} esplorativi")
    print(f"\nREGOLA: un freno si ritara solo se per un motivo i rifiutati hanno R medio > "
          f"aperti (R netto, stesso periodo) con >= {min_casi} casi valutati.")
    print("MARGINE: 2 errori standard della differenza, caso per caso; solo informazione, "
          "non entra nel verdetto.")
    print("VERDETTO PER MOTIVO:")
    if pm:
        for riga in verdetto(pm, aperti, min_casi):
            print(riga)
    else:
        print("  niente da giudicare.")
    print("\nAVVERTENZE: i rifiutati sono prezzo puro (niente fee, slippage, funding) e "
          "simulati sulla candela;\ngli aperti sono netti di costi ed eseguiti al mark: a "
          "parita' di tragitto i rifiutati sembrano ~0,1-0,2 R migliori (vedi R lordo).")


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--giorni", type=int, default=30, help="finestra in giorni (default 30)")
    ap.add_argument("--min-casi", type=int, default=MIN_CASI,
                    help=f"casi valutati minimi per un verdetto (default {MIN_CASI})")
    args = ap.parse_args(argv)
    now = time.time()
    fb = get_firebase()
    r = rifiutati.riassunto(fb, giorni=args.giorni, now=now)
    primo = r.get("primo_ts")
    trades: list = []
    if primo is not None:
        # 1 ott 2026: un trade entrato dopo il primo rifiutato e' anche uscito
        # dopo, quindi basta chiedere alla cache i trade usciti da li' e poi
        # filtrare per ora d'INGRESSO (aperti_del_periodo). Stessa cache di
        # prima: nessuna lettura in piu'.
        try:
            trades = TradeLogger(fb).all_since(primo) or []
        except Exception as exc:  # noqa: BLE001
            print(f"[rifiutati] trade non letti ({exc})")
            trades = []
    periodo = aperti_del_periodo(trades, primo)
    aperti = statistiche_aperti(periodo["trades"])
    stampa(r, aperti, args.min_casi, periodo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
