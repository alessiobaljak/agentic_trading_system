"""Fase 0, punti 6 e 9 delle regole del gruppo: la tabella per moneta di fase0_dati.md, dai file 1d scaricati.

Per ogni moneta di monete.csv e per BTCUSDT, solo con le funzioni di research/src/dati.py:
* mesi presenti di last (klines/1d), mark (markPriceKlines/1d) e funding, rispetto a quelli attesi (dal primo mese
  della scheda al 2023-12), e i mesi mancanti;
* barre giornaliere di last e mark, barre tolte dall'allineamento (carica_serie_allineate, intersezione) con le loro
  date, prima barra vera (prima barra presente in entrambe le serie) e controllo della storia (prima del 2022-01-01);
* giorni mancanti nel last fra la prima e l'ultima barra;
* intervallo del funding nel tempo (intervallo_funding sulle righe del file);
* volume medio giornaliero in USDT per anno (volume_usdt_da_zip sui file 1d del last) e mesi sotto la liquidità
  minima (mesi_sotto_liquidita, la funzione unica del filtro), separati fra costruzione e validazione.

Scrive lavoro/fase0_dati.json (tutto) e fase0_dati.md (le tabelle). Nessun calcolo d'esame.
"""

import csv
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

RADICE = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE))

from research.src import dati  # noqa: E402

CARTELLA = RADICE / "research" / "campagne" / "PANIERE"
FINE = date(2023, 12, 31)
TAGLIO = date(2023, 1, 16)
LIMITE_STORIA = date(2022, 1, 1)
GIORNO = 86_400_000


def giorno(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).date().isoformat()


def intervalli_di_giorni(lista_ts):
    """[(primo, ultimo)] di giorni consecutivi, come testo."""
    blocchi = []
    for ts in sorted(lista_ts):
        if blocchi and ts - blocchi[-1][1] == GIORNO:
            blocchi[-1][1] = ts
        else:
            blocchi.append([ts, ts])
    return [giorno(a) if a == b else f"{giorno(a)}..{giorno(b)}" for a, b in blocchi]


def mesi_presenti(simbolo, tipo, intervallo, inizio):
    attesi = list(dati.mesi_del_periodo(inizio, FINE))
    presenti = [m for m in attesi if dati.percorso_mese(simbolo, tipo, intervallo, m[0], m[1]).is_file()]
    mancanti = [f"{a}-{m:02d}" for a, m in attesi if (a, m) not in presenti]
    return len(attesi), len(presenti), mancanti


def analizza(simbolo, inizio):
    r = {"inizio_scheda": inizio.isoformat()}
    for nome, tipo, intervallo in (("last", "klines", "1d"), ("mark", "markPriceKlines", "1d"),
                                   ("funding", "fundingRate", None)):
        attesi, presenti, mancanti = mesi_presenti(simbolo, tipo, intervallo, inizio)
        r[f"mesi_{nome}"] = {"attesi": attesi, "presenti": presenti, "mancanti": mancanti}
    al = dati.carica_serie_allineate(simbolo, "1d", inizio, FINE)
    last = dati.carica_candele(simbolo, "1d", inizio, FINE)
    candele = al["candele"]
    r["barre_last"] = len(last)
    r["barre_allineate"] = len(candele)
    r["tolte_last"] = intervalli_di_giorni(al["tolte_last"])
    r["tolte_mark"] = intervalli_di_giorni(al["tolte_mark"])
    r["n_tolte_last"] = al["n_tolte_last"]
    r["n_tolte_mark"] = al["n_tolte_mark"]
    r["tolte_last_in_validazione"] = sum(1 for ts in al["tolte_last"] if ts >= dati.ms_da_data(TAGLIO + timedelta(days=1)))
    r["prima_barra_last"] = giorno(last[0].ts) if last else None
    r["prima_barra_allineata"] = giorno(candele[0].ts) if candele else None
    r["ultima_barra_allineata"] = giorno(candele[-1].ts) if candele else None
    r["storia_ok"] = bool(candele) and datetime.fromtimestamp(candele[0].ts / 1000, tz=timezone.utc).date() < LIMITE_STORIA
    if last:
        ts_last = {c.ts for c in last}
        tutti = range(last[0].ts, last[-1].ts + 1, GIORNO)
        r["giorni_mancanti_last"] = intervalli_di_giorni([t for t in tutti if t not in ts_last])
    else:
        r["giorni_mancanti_last"] = []
    righe_funding = dati.carica_funding_dettaglio(simbolo, inizio, FINE)
    r["funding_settlement"] = len(righe_funding)
    r["funding_primo"] = giorno(righe_funding[0][0]) if righe_funding else None
    r["funding_intervalli"] = [[giorno(ts), ore] for ts, ore in dati.intervallo_funding(righe_funding)]
    liq = dati.liquidita_mensile(simbolo, inizio, FINE)
    per_anno = {}
    for (anno, mese), voce in liq.items():
        if voce["volume_medio_usdt"] is not None:
            per_anno.setdefault(str(anno), []).extend([voce["volume_medio_usdt"]] * voce["giorni"])
    r["volume_medio_usdt_per_anno"] = {a: round(sum(v) / len(v)) for a, v in sorted(per_anno.items())}
    sotto = dati.mesi_sotto_liquidita(simbolo, inizio, FINE)
    r["mesi_sotto_liquidita"] = [f"{a}-{m:02d}" for a, m in sotto]
    r["mesi_sotto_liquidita_costruzione"] = sum(1 for a, m in sotto if date(a, m, 1) <= TAGLIO)
    r["mesi_sotto_liquidita_validazione"] = sum(1 for a, m in sotto if (a, m) >= (2023, 1))
    r["mesi_totali"] = len(liq)
    return r


def main():
    with open(CARTELLA / "monete.csv", encoding="utf-8") as f:
        simboli = [riga["simbolo"] for riga in csv.DictReader(f)]
    schede = {s: dati.leggi_scheda_gruppo(s) for s in simboli}
    risultati = {}
    for s in simboli:
        risultati[s] = analizza(s, schede[s]["primo_mese"])
        risultati[s]["slippage_per_lato"] = schede[s]["slippage_per_lato"]
        print(s, "ok")
    risultati["BTCUSDT"] = analizza("BTCUSDT", date(2020, 1, 1))
    (CARTELLA / "lavoro" / "fase0_dati.json").write_text(
        json.dumps(risultati, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("fatto")


if __name__ == "__main__":
    main()
