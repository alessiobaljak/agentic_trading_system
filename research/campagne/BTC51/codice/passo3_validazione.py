"""Passo 3 del protocollo 3 (validazione), in due comandi separati.

    python3 research/campagne/BTC51/codice/passo3_validazione.py congela
        impronte SHA-256 dei file del candidato, confrontate con quelle del via libera
        (via_libera_validazione.md); le scrive in validazione.md. Nessun dato della validazione.

    python3 research/campagne/BTC51/codice/passo3_validazione.py esegui
        una sola esecuzione di V-020 sul periodo dal 2022-10-01 al 2023-12-31, a costi normali e doppi,
        con le condizioni della sezione 10.3; esito nel log, in risultati/V-020_validazione.json e in
        validazione.md. Si rifiuta se le impronte non coincidono o se la validazione e' gia' registrata.

SCELTA dichiarata: la serie si carica dal 2020-01-01 al 2023-12-31, e le decisioni si prendono solo alle chiusure
delle candele della validazione (dal 2022-10-01 00:00 all'ultima del 2023-12-31). Gli indicatori arrivano gia'
caldi dalla storia precedente, come per il bot dal vivo; nessun dato oltre il 2023-12-31 e nessun trade che legga
oltre la fine del periodo.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lotto  # noqa: E402
import registro  # noqa: E402

import numpy as np  # noqa: E402

from research.src import dati  # noqa: E402
from research.src import catalogo3 as cat  # noqa: E402
from research.src import motore3 as mot  # noqa: E402
from research.src import statistica3 as st  # noqa: E402

CARTELLA = Path(__file__).resolve().parent.parent
FILE = ["candidati/V-020/regole.md", "codice/lotto_2.json", "codice/lotto.py", "codice/registro.py"]
VALIDAZIONE = CARTELLA / "validazione.md"
VIA_LIBERA = CARTELLA / "via_libera_validazione.md"


def impronte() -> dict:
    return {f: hashlib.sha256((CARTELLA / f).read_bytes()).hexdigest() for f in FILE}


def attese() -> dict:
    testo = VIA_LIBERA.read_text(encoding="utf-8")
    return {f: h for f, h in re.findall(r"`([^`]+)`: `([0-9a-f]{64})`", testo)}


def confronto():
    trov, att = impronte(), attese()
    diverse = [f for f in FILE if att.get(f) != trov[f]]
    return trov, att, diverse


def congela() -> None:
    trov, att, diverse = confronto()
    righe = ["# Validazione della campagna BTC51 (Passo 3)", "",
             f"Scritto dalla sessione di ricerca il {registro.adesso()}. Via libera del coordinamento: "
             "`via_libera_validazione.md` (sì del proprietario, «sì procedi con la validazione»).", "",
             "## 1. Candidato congelato", "",
             "Candidati: **V-020** (l'unico). Impronte SHA-256 calcolate prima di caricare i dati della validazione, "
             "confrontate con quelle del via libera:", "",
             "| File | SHA-256 | Uguale al via libera |", "|---|---|---|"]
    for f in FILE:
        righe.append(f"| `{f}` | `{trov[f]}` | {'sì' if att.get(f) == trov[f] else '**NO**'} |")
    righe += ["", "Esito del confronto: " + ("**tutte uguali**." if not diverse else f"**DIVERSE: {diverse}** — STOP."), ""]
    VALIDAZIONE.write_text("\n".join(righe) + "\n", encoding="utf-8")
    registro.aggiungi({"tipo": "nota", "testo": "Passo 3, candidato congelato: impronte in validazione.md; "
                       + ("uguali al via libera" if not diverse else f"DIVERSE dal via libera: {diverse}")})
    print("IMPRONTE UGUALI" if not diverse else f"IMPRONTE DIVERSE: {diverse}")


def esegui() -> None:
    _, _, diverse = confronto()
    if diverse:
        raise SystemExit(f"impronte diverse dal via libera: {diverse}")
    if any(x.get("id") == "V-020-VAL" for x in registro.voci()):
        raise SystemExit("la validazione di V-020 e' gia' registrata: si fa una volta sola")
    reg = [x for x in registro.voci() if x.get("id") == "V-020" and x.get("tipo") == "registrazione"][0]
    spec = cat.normalizza(reg["specifica"])
    r_costr = json.loads((CARTELLA / "risultati" / "V-020.json").read_text(encoding="utf-8"))["metriche"]["r_medio"]
    registro.aggiungi({"id": "V-020-VAL", "tipo": "registrazione", "tipo_test": "validazione", "verifica_di": "V-020",
                       "specifica": spec, "periodo": "validazione, dal 2022-10-01 al 2023-12-31",
                       "r_medio_costruzione": r_costr,
                       "previsione": "R medio fra -0,1 e +0,15; probabilmente non supera la condizione della meta' "
                                     "dell'R di costruzione (0,111)",
                       "criterio_successo": "sezione 10.3, validazione"})
    s = dati.serie_3("BTCUSDT", "1h", date(2020, 1, 1), date(2023, 12, 31))
    ts = np.asarray(s.ts)
    a = int(np.searchsorted(ts, dati.ms_da_data(date(2022, 10, 1))))
    b = len(ts) - 1
    c = cat.compila(spec, s)
    ris = mot.esegui(c, mot.Regole(), mot.COSTI_NORMALI, a, b)
    m = mot.metriche(ris, s)
    rd = mot.esegui(c, mot.Regole(), mot.COSTI_DOPPI, a, b)
    md = mot.metriche(rd, s)
    esiti = st.supera_validazione(m, md, r_costr)
    periodo = [datetime.fromtimestamp(int(ts[a]) / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M"),
               datetime.fromtimestamp(int(ts[b]) / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")]
    dettaglio = {"id": "V-020", "periodo_candele": periodo, "candele": b - a + 1, "metriche": m,
                 "metriche_costi_doppi": md, "r_medio_costruzione": r_costr, "esiti": esiti,
                 "trade": [{"ingresso": datetime.fromtimestamp(t.ts_ingresso / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M"),
                            "uscita": datetime.fromtimestamp(t.ts_uscita / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M"),
                            "motivo": t.motivo, "r": round(t.r, 4)} for t in ris.trade]}
    (CARTELLA / "risultati" / "V-020_validazione.json").write_text(
        json.dumps(lotto._pulisci(dettaglio), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    sintesi = {k: m.get(k) for k in ("trade", "trade_al_mese", "r_medio", "profit_factor", "vincenti",
                                     "r_medio_vincenti", "r_medio_perdenti", "drawdown_max_r", "tempo_in_posizione",
                                     "ridotti", "violazioni_liquidazione")}
    registro.aggiungi({"id": "V-020-VAL", "tipo": "risultato", "metriche": lotto._pulisci(lotto._arrot(sintesi)),
                       "r_medio_costi_doppi": round(md["r_medio"], 3),
                       "r_per_anno": lotto._pulisci({k: round(x, 3) for k, x in m["r_per_anno"].items()}),
                       "esiti": lotto._pulisci(esiti), "esito": "supera" if esiti["supera"] else "non supera",
                       "dettaglio": "risultati/V-020_validazione.json"})
    print(json.dumps(lotto._pulisci({"periodo": periodo, "trade": m["trade"], "r_medio": m["r_medio"],
                                     "profit_factor": m["profit_factor"], "r_costi_doppi": md["r_medio"],
                                     "vincenti": m["vincenti"], "drawdown": m["drawdown_max_r"],
                                     "r_per_anno": m["r_per_anno"], "motivi": m["motivi"],
                                     "trade_al_mese": m["trade_al_mese"], "esiti": esiti})))


if __name__ == "__main__":
    {"congela": congela, "esegui": esegui}[sys.argv[1]]()
