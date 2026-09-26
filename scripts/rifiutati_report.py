"""I SEGNALI RIFIUTATI AVREBBERO VINTO? — voce ops `rifiutati` (26 set 2026, J6).

Per ogni classe di motivo (cooldown, tetto per coin, peso sotto soglia,
posizione aperta, esplorative al tetto, veto di regime, margine, rischio
direzionale, stop troppo largo) stampa: quanti segnali, quanti valutati sulle
candele vere, R medio, % di vincenti, mfe mediana. Poi il confronto con i trade
APERTI dello stesso periodo (collection `trades`), in R.

LA REGOLA, scritta prima di vedere i numeri: un freno si ritara SOLO se per un
motivo i rifiutati hanno R medio maggiore degli aperti con almeno 30 casi
valutati (`--min-casi`). Sotto i 30 e' un dato che non c'e' ancora, non un
verdetto. E anche sopra, questo report PROPONE: la modifica al freno passa dal
gate come tutte le altre.

DUE AVVERTENZE che il report ripete in fondo: i rifiutati sono prezzo puro
(niente fee, slippage, funding), gli aperti sono NETTI di costi — a parita' di
tragitto i rifiutati sembrano ~0,1-0,2 R migliori; e i rifiutati sono simulati
sulla candela, gli aperti eseguiti al mark.

Sola lettura. Senza Firebase (in locale, nei test) gira sullo store in memoria:
tutto vuoto, ed esce con 0.

Uso (sul VPS):
    .venv/bin/python -m scripts.rifiutati_report
    .venv/bin/python -m scripts.rifiutati_report --giorni 14 --min-casi 30
"""
from __future__ import annotations

import argparse
import time
from datetime import datetime, timezone
from statistics import mean, median
from typing import Optional

from bot.core.firebase_client import get_firebase
from bot.learning import rifiutati
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
    scala di priorita' di scripts/mfe_report.stop_originale."""
    entry = _f(t.get("entry_price"))
    if not entry or entry <= 0:
        return None
    if _f(t.get("orig_stop")):
        return _f(t.get("orig_stop"))
    pm = t.get("post_mortem") or {}
    sp = _f(pm.get("stop_pct")) if isinstance(pm, dict) else None
    if sp and sp > 0:
        long = str(t.get("direction", "")).lower().endswith("long")
        return entry * (1 - sp / 100.0) if long else entry * (1 + sp / 100.0)
    return _f(t.get("stop_price"))


def r_aperto(t: dict) -> Optional[float]:
    """R NETTO di un trade aperto: pnl in USDT diviso il rischio all'ingresso
    (|entry - stop originale| x quantita'). None se manca un pezzo."""
    entry, stop, size, pnl = (_f(t.get("entry_price")), stop_originale(t),
                              _f(t.get("size")), _f(t.get("pnl")))
    if entry is None or stop is None or not size or pnl is None:
        return None
    rischio = abs(entry - stop) * abs(size)
    if rischio <= 0:
        return None
    return pnl / rischio


def statistiche_aperti(trades: list[dict]) -> dict:
    """n, R medio, quota vincenti, mfe mediana dei trade aperti (quelli con R
    calcolabile; `senza_r` dice quanti sono rimasti fuori)."""
    rs, mfes, senza = [], [], 0
    for t in trades:
        r = r_aperto(t)
        if r is None:
            senza += 1
            continue
        rs.append(r)
        m = _f(t.get("mfe_r"))
        if m is not None:
            mfes.append(m)
    return {
        "n": len(rs), "senza_r": senza,
        "pnl_r_medio": round(mean(rs), 3) if rs else None,
        "quota_vincenti": round(sum(1 for r in rs if r > 0) / len(rs), 3) if rs else None,
        "mfe_r_mediana": round(median(mfes), 3) if mfes else None,
    }


def verdetto(per_motivo: dict, aperti: dict, min_casi: int = MIN_CASI) -> list[str]:
    """Una riga per motivo: «ritarare» solo con >= min_casi valutati E R medio
    dei rifiutati > R medio degli aperti. Pura, per i test."""
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
                         f"il freno si puo' RITARARE (proposta per il gate)")
        else:
            righe.append(f"  {m:<22} R {p:+.2f} <= aperti {r_ap:+.2f} su {v} casi: il freno tiene")
    return righe


def _fmt(v, spec: str = "+.2f") -> str:
    return "   —" if v is None else format(v, spec)


def stampa(r: dict, aperti: dict, min_casi: int) -> None:
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
    qv = aperti["quota_vincenti"]
    vinc_ap = "—" if qv is None else f"{qv * 100:.0f}%"
    print(f"\nAPERTI nello stesso periodo: {aperti['n']} trade con R calcolabile "
          f"({aperti['senza_r']} senza) · R medio {_fmt(aperti['pnl_r_medio'])} · "
          f"vincenti {vinc_ap} · mfe mediana {_fmt(aperti['mfe_r_mediana'], '.2f')}")
    print(f"\nREGOLA: un freno si ritara solo se per un motivo i rifiutati hanno R medio > "
          f"aperti con >= {min_casi} casi valutati.")
    print("VERDETTO PER MOTIVO:")
    if pm:
        for riga in verdetto(pm, aperti, min_casi):
            print(riga)
    else:
        print("  niente da giudicare.")
    print("\nAVVERTENZE: i rifiutati sono prezzo puro (niente fee, slippage, funding) e "
          "simulati sulla candela;\ngli aperti sono netti di costi ed eseguiti al mark: a "
          "parita' di tragitto i rifiutati sembrano ~0,1-0,2 R migliori.")


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--giorni", type=int, default=30, help="finestra in giorni (default 30)")
    ap.add_argument("--min-casi", type=int, default=MIN_CASI,
                    help=f"casi valutati minimi per un verdetto (default {MIN_CASI})")
    args = ap.parse_args(argv)
    now = time.time()
    fb = get_firebase()
    r = rifiutati.riassunto(fb, giorni=args.giorni, now=now)
    try:
        trades = TradeLogger(fb).all_since(now - args.giorni * 86400) or []
    except Exception as exc:  # noqa: BLE001
        print(f"[rifiutati] trade non letti ({exc})")
        trades = []
    # gli esplorativi non entrano nel confronto: size a un quarto e coppie non
    # validate, sarebbero un altro gruppo (F1bis)
    aperti = statistiche_aperti([t for t in trades if isinstance(t, dict) and not t.get("esplorativa")])
    stampa(r, aperti, args.min_casi)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
