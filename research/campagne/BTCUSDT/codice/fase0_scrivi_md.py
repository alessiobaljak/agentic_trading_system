"""Scrive fase0_dati.md dall'analisi (fase0_analisi.json) e dalle impronte (impronte.json)."""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from log import aggiungi  # noqa: E402

QUI = Path(__file__).resolve().parent
A = json.loads((QUI / "fase0_analisi.json").read_text())
IMPRONTE = json.loads((QUI.parents[2] / "data" / "insample" / "BTCUSDT" / "impronte.json").read_text())

def mln(x): return f"{x/1e6:,.0f}".replace(",", ".")
righe = []
w = righe.append
w("# Fase 0 — I dati di BTCUSDT (in-sample, 2020-01-01 → 2023-12-31)\n")
w("Scritto dalla sessione di campagna il 2026-10-07. Tutto cio' che c'e' qui viene dai file")
w("scaricati in `research/data/insample/BTCUSDT/` (fuori da git) e dall'analisi in")
w("`codice/fase0_analisi.py` (esito salvato in `codice/fase0_analisi.json`). Nessun dato oltre il")
w("2023-12-31 e' stato richiesto, scaricato o elencato.\n")
w("## Periodi\n")
w("| Periodo | Da | A | Giorni |\n|---|---|---|---|")
w("| In-sample | 2020-01-01 | 2023-12-31 | 1.461 |")
w("| Costruzione (70%) | 2020-01-01 | 2022-10-19 | 1.023 |")
w("| Validazione (30%) | 2022-10-20 | 2023-12-31 | 438 |\n")
w("Le date sono state calcolate e registrate nel log (voce `BTCUSDT-F0-01`) PRIMA di caricare i prezzi.")
w("I mesi settembre-dicembre 2019 (listing 2019-09-08) restano fuori: l'archivio mensile parte da")
w("gennaio 2020 (decisione 5 del Passo 0). Storia utile: 4 anni, sopra i 2 richiesti.\n")
w("## Cosa e' stato scaricato\n")
w("Fonte: data.binance.vision, file mensili `futures/um`, 48 mesi per serie, ognuno con il CHECKSUM")
w("remoto verificato (nessun CHECKSUM mancante).\n")
w("| Serie | Uso | File | Barre attese | Barre presenti |\n|---|---|---|---|---|")
s = A["serie"]
w(f"| klines 15m (last price) | segnali e stop; aggregata a 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d | 48 | {s['last_15m']['attese']:,} | {s['last_15m']['presenti']:,} |".replace(",", ".").replace("30m. 1h. 2h. 4h. 6h. 8h. 12h. 1d", "30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d"))
w(f"| klines 1d (last price) | solo controllo dell'aggregazione | 48 | {s['last_1d']['attese']:,} | {s['last_1d']['presenti']:,} |".replace(",", "."))
w(f"| markPriceKlines 15m | liquidazioni | 48 | {s['mark_15m']['attese']:,} | {s['mark_15m']['presenti']:,} |".replace(",", "."))
w(f"| fundingRate | funding storico | 48 | — | {A['funding']['n_settlement']:,} settlement |".replace(",", "."))
w("")
w("## Buchi nei dati\n")
w("* **Last price 15m: nessun buco** (140.256 barre su 140.256, dal 2020-01-01 00:00 al 2023-12-31 23:45).")
w("* **Last price 1d: nessun buco** (1.461 giorni).")
w(f"* **Mark price 15m: {s['mark_15m']['attese']-s['mark_15m']['presenti']} barre mancanti in {len(s['mark_15m']['buchi'])} buchi**, tutti assenti dai file di Binance (non e' un errore di scarico):\n")
w("| Da (UTC) | A (UTC) | Barre mancanti |\n|---|---|---|")
for b in s["mark_15m"]["buchi"]:
    w(f"| {b['da']} | {b['a']} | {b['barre_mancanti']} |")
w("")
w("**Regola adottata (dichiarata qui e nel log, voce `BTCUSDT-F0-03`):** le barre mark mancanti si")
w("riempiono con la barra last dello stesso istante, prima dell'aggregazione (`codice/dati_btc.py`,")
w("`riempi_mark_con_last`). Motivi: il mark serve solo alla liquidazione, che con leva massima 2 e")
w("margine di mantenimento 2,5% dista circa il 47% dall'ingresso; lo scarto fra close mark e close")
w(f"last e' mediano {A['scarto_mark_last_close']['mediana']*100:.4f}%, 99° percentile {A['scarto_mark_last_close']['p99']*100:.3f}%, massimo {A['scarto_mark_last_close']['max']*100:.2f}%.")
w("Lo stop scatta sulla serie last (`serie_stop` approvata), quindi il riempimento non tocca gli stop.")
w("Il motore di `src/` non e' stato modificato: il riempimento e' nel codice della campagna.\n")
w("## Controllo dell'aggregazione\n")
w(f"Le candele 1d aggregate dalle 15m coincidono con le 1d native di Binance su open, high, low e close")
w(f"in tutti i {A['aggregazione_1d']['giorni_nativi']} giorni. Il volume differisce in {A['aggregazione_1d']['n_differenze']} giorni")
w("(2023-08-16: aggregato 280.543 contro nativo 272.023; 2023-11-10: 267.169 contro 299.374, in moneta base):")
w("sono incoerenze dei file di Binance, non dell'aggregazione, e il volume non entra in nessuna regola")
w("di prezzo. Si dichiara e basta.\n")
w("## Sospensioni e cambi di contratto\n")
w("Nessun cambio di contratto per BTCUSDT (nessuna cucitura). Nessuna sospensione visibile nella serie")
w("last (nessun buco). I buchi del mark price coincidono con giorni interi e sembrano file di archivio")
w("mancanti, non sospensioni del mercato.\n")
w("## Funding\n")
f = A["funding"]
w(f"* Disponibile dal {f['primo']} al {f['ultimo']} UTC: {f['n_settlement']:,} settlement.".replace(",", "."))
w("* Intervallo: **8 ore per tutto il periodo** (dichiarato dai file e osservato: 4.382 distanze su 4.382 pari a 8 ore).")
w(f"* Tasso: mediana {f['tasso']['mediana']*100:.4f}%, medio {f['tasso']['medio']*100:.4f}%, min {f['tasso']['min']*100:.2f}%, max {f['tasso']['max']*100:.2f}% per settlement.")
w("* Medio per anno e quota di settlement positivi (long paga):\n")
w("| Anno | Tasso medio per settlement | Quota positivi |\n|---|---|---|")
for a in f["medio_per_anno"]:
    w(f"| {a} | {f['medio_per_anno'][a]*100:.4f}% | {f['quota_positivi_per_anno'][a]*100:.0f}% |")
w("")
w("## Volume e liquidita'\n")
v = A["volume_usdt_giorno"]
w("Stima del volume giornaliero in USDT = volume in moneta base × close del giorno (la candela del")
w("motore non porta il quote volume; l'approssimazione basta per la soglia).\n")
w("| Anno | Volume medio al giorno (milioni USDT) | Giorno minimo (milioni USDT) |\n|---|---|---|")
for a in v["medio_per_anno"]:
    w(f"| {a} | {mln(v['medio_per_anno'][a])} | {mln(v['minimo_per_anno'][a])} |")
w("")
w(f"Giorni sotto la soglia di 20 milioni di USDT: **{len(v['giorni_sotto_soglia'])}**. Nessun periodo da escludere dai test.")
w("Fascia di slippage: 0,01% per lato (scheda, volume medio 2023 sopra 1 miliardo); anche il 2020, l'anno")
w("piu' sottile, sta sopra 1 miliardo in media.\n")
w("## Prezzo per anno (descrizione dei dati, non un risultato)\n")
w("| Anno | Primo open | Ultimo close | Minimo | Massimo |\n|---|---|---|---|---|")
for a, p in A["prezzo_per_anno"].items():
    w(f"| {a} | {p['primo_open']:,.0f} | {p['ultimo_close']:,.0f} | {p['min']:,.0f} | {p['max']:,.0f} |".replace(",", "."))
w("")
w("## Impronte SHA-256 dei file scaricati\n")
w("Da qui in poi queste sono la verita' della campagna: a ogni sessione i file si riscaricano e")
w("`dati.verifica_impronte` li confronta; una differenza e' uno STOP.\n")
w("| File | SHA-256 |\n|---|---|")
for nome, h in IMPRONTE.items():
    w(f"| `{nome}` | `{h}` |")
w("")
(QUI.parent / "fase0_dati.md").write_text("\n".join(righe), encoding="utf-8")
aggiungi({
    "id": "BTCUSDT-F0-03", "tipo": "nota", "fase": "0",
    "oggetto": "regola per le barre mark mancanti e chiusura della Fase 0",
    "mark_15m_mancanti": s["mark_15m"]["attese"] - s["mark_15m"]["presenti"],
    "buchi_mark": s["mark_15m"]["buchi"],
    "regola": "barra mark mancante = barra last dello stesso istante, prima dell'aggregazione (codice/dati_btc.py); il motore in src/ non cambia",
    "perche": "il mark serve solo alla liquidazione (a leva 2 dista ~47%); scarto mediano mark/last 0,007%; lo stop scatta sul last",
    "last_15m": "completa, 140256/140256",
    "funding": "8 ore per tutto il periodo, 4383 settlement",
    "liquidita": "nessun giorno sotto 20 milioni USDT; nessun periodo escluso",
    "storia_utile_anni": 4,
    "esito_fase_0": "la moneta ha campagna: storia 4 anni >= 2",
    "impronte": "192 file, elencate in fase0_dati.md",
})
print("scritto fase0_dati.md")
