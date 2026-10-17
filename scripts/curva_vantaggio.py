"""LA CURVA DEL VANTAGGIO DEL SEGNALE (T2, 2 ott 2026) — la parte che legge.

I conti (puri, con tutte le scelte spiegate) stanno in
`bot/learning/curva_vantaggio.py`; la regola e' nel diario
(`docs/andremo_live.md`, «2 ottobre, mattina: T2»), scritta prima dei numeri.

Qui: i trade chiusi del paper (come `scripts.mfe_report`: `TradeLogger.all_since(0)`)
e le candele da 15m dalla cache del gate in SOLA LETTURA, con
`scripts.tp_aperti.carica_cache`: nessun download, nessuna scrittura, si puo'
lanciare anche col gate in corso. Una moneta che non e' in cache si salta e si conta.

Uso (sul VPS):
    .venv/bin/python -m scripts.curva_vantaggio
Gira anche in coda a `scripts.mfe_report` (chiave ops `mfe`).
"""
from __future__ import annotations

import math
import textwrap
import time

from bot.learning import curva_vantaggio as cv

REGOLA = (
    "Regola (diario, 2 ott 2026, scritta PRIMA dei numeri): per ogni trade vero del paper, "
    "la mossa del prezzo dopo 1, 4, 12 e 24 ore dall'ingresso, col segno della direzione, in "
    "«mosse tipiche di 24 ore» della moneta (calcolate sui 30 giorni PRIMA dell'ingresso). "
    "Confronto: ingressi a caso sulla stessa moneta negli stessi giorni, stessa direzione. "
    "Vantaggio = media dei segnali - media del caso; margine al 95% ricampionando le giornate. "
    "Tutte le durate dentro il margine -> «nessun vantaggio misurabile» (il lavoro sui TP si "
    "ferma, il problema e' l'ingresso o il gate: R1); qualcuna sopra -> «c'è un vantaggio» (il "
    "TP va dove la curva smette di salire, poi T1 dopo le letture del 7-14 ott); sotto -> «i "
    "segnali fanno peggio del caso», detto per primo.")

SCELTE = (
    f"Scelte: prezzo d'ingresso = chiusura dell'ultima candela da 15m gia' chiusa all'ingresso "
    f"(niente sguardo avanti); mossa tipica = mediana di |mossa di 24 ore| nei "
    f"{cv.GIORNI_NORMA} giorni prima; caso = {cv.N_CASO} ingressi per segnale, stessa moneta e "
    f"direzione, nelle {cv.FINESTRA_CASO_S // 3600} ore DOPO il segnale (non prima: la direzione e' decisa col passato), solo se il loro futuro "
    f"c'e' nei dati; margine = {cv.N_BOOT} ricampionamenti delle giornate (UTC), seme fisso. "
    f"Le colonne in % non sono normalizzate: servono solo a farsi un'idea.")


def serie_dalla_cache(segnali: list[dict], carica, timeframe: str = "15m",
                      ora: float | None = None) -> dict:
    """Una lettura di cache per moneta, con abbastanza giorni da coprire il primo
    ingresso, i 30 giorni della mossa tipica prima e 2 di margine. Una moneta che
    manca (o una lettura che solleva) vale None: il chiamante la conta."""
    if not segnali:
        return {}
    ora = time.time() if ora is None else ora
    giorni = int(math.ceil(max(0.0, ora - min(s["ts"] for s in segnali)) / 86400.0)) \
        + cv.GIORNI_NORMA + 2
    out: dict = {}
    for sym in sorted({s["symbol"] for s in segnali}):
        try:
            out[sym] = carica(sym, timeframe, giorni) or None
        except Exception:  # noqa: BLE001
            out[sym] = None
    return out


def stampa(trades: list[dict] | None, carica=None, ora: float | None = None) -> dict:
    """Stampa la sezione e ritorna i numeri (curva, esito, conti, saltati)."""
    if carica is None:
        from scripts.tp_aperti import carica_cache as carica
    t0 = time.time()
    print("\n" + "=" * 78)
    print("LA CURVA DEL VANTAGGIO DEL SEGNALE (T2)")
    print("=" * 78)
    for riga in textwrap.wrap(REGOLA, 95):
        print(riga)

    segnali, conti = cv.segnali_dai_trade(trades or [])
    altri = ", ".join(f"{k}: {v}" for k, v in sorted(conti["altri_timeframe"].items()))
    print(f"\n  trade chiusi letti: {conti['letti']} · a 15m: {conti['del_timeframe']} "
          f"(esplorativi: {conti['esplorativi']}) · altri timeframe, fuori dalla curva: "
          f"{sum(conti['altri_timeframe'].values())}" + (f" ({altri})" if altri else "")
          + (f" · senza ora/direzione/moneta: {conti['senza_dati']}" if conti["senza_dati"] else ""))

    serie = serie_dalla_cache(segnali, carica, ora=ora)
    righe, saltati = cv.misura_segnali(segnali, serie)
    curva = cv.curva(righe)
    versi = cv.per_verso(righe)
    esito = cv.verdetto(curva)

    n_salt = sum(saltati.values())
    monete_assenti = sum(1 for v in serie.values() if v is None)
    print(f"  misurati: {curva['n']} su {curva['giorni']} giornate (esplorativi fra i misurati: "
          f"{sum(1 for r in righe if r['esplorativa'])}) · saltati: {n_salt}"
          + (" (" + ", ".join(f"{k}: {v}" for k, v in sorted(saltati.items())) + ")"
             if n_salt else "")
          + (f" · monete non in cache: {monete_assenti} su {len(serie)}" if monete_assenti else ""))
    if righe:
        nc = sorted(r["n_caso"] for r in righe)
        print(f"  ingressi a caso per segnale: mediana {nc[len(nc) // 2]}, minimo {nc[0]}")
    for riga in textwrap.wrap(SCELTE, 93):
        print("  " + riga)

    if righe:
        print("\n  Vantaggio in mosse tipiche di 24 ore (decide) e in % (solo per farsi un'idea):")
        for riga in cv.righe_tabella(curva):
            print(riga)
        print("\n  Per verso (solo informativo, non decide):")
        print(cv.riga_verso("long", versi["long"]))
        print(cv.riga_verso("short", versi["short"]))
    print("\n  Parte informativa del motore (segnali delle coppie validate negli ultimi giorni): "
          "non ancora — rigirare il motore chiede di scaricare candele, questa sezione legge "
          "solo la cache.")
    print(f"  Limiti: {curva['n']} trade su {curva['giorni']} giornate di un solo mercato; le "
          f"uscite non toccano la misura (si guarda il prezzo, non il trade). Su prezzi a caso "
          f"(100 prove sintetiche, 220 segnali, 16 giorni) la regola dice «nessun vantaggio» "
          f"~75-81 volte su 100: un «vantaggio» o un «peggio» a una sola durata va letto con "
          f"questo in mente. "
          f"(calcolo: {time.time() - t0:.1f}s)")
    print(f"\nESITO (regola del 2 ott): {esito['testo']}")
    return {"curva": curva, "versi": versi, "verdetto": esito, "conti": conti,
            "saltati": saltati}


def main() -> int:
    from bot.core.firebase_client import get_firebase
    from bot.learning.trade_logger import TradeLogger

    fb = get_firebase()
    stampa(TradeLogger(fb).all_since(0.0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
