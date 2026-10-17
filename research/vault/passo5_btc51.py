"""Passo 5 del protocollo 3 (vault) per la campagna BTC51, eseguito dal coordinamento sul branch principale.

    python3 research/vault/passo5_btc51.py verifica
        impronte degli strumenti (quarto giro del collaudo) e dei file del candidato (validazione.md sul branch
        della ricerca), specifica di V-020 nel log uguale a quella della validazione. Nessun dato del vault.

    python3 research/vault/passo5_btc51.py riproduci
        rifa' costruzione (con entrate casuali e p-value) e validazione di V-020 con questo programma e controlla
        che i numeri siano quelli della sessione di ricerca (180 trade, +0,223 R, p 0,017; 80 trade, +0,167 R).
        Nessun dato del vault: serve a sapere che il vault girera' con la stessa catena.

    python3 research/vault/passo5_btc51.py scarica
        scarica in research/data/vault/BTCUSDT le candele last e mark a 1h e il funding dal 2024-01 al 2026-09,
        con il CHECKSUM di Binance. Rifiuta senza vault/APERTURA_3.md (il caricatore).

    python3 research/vault/passo5_btc51.py esegui
        UNA sola esecuzione di V-020 sul vault (decisioni dal 2024-01-01 00:00 al 2026-09-30 23:00 UTC), a costi
        normali e doppi, con le entrate casuali (1.000 simulazioni, seme 2026) e l'asticella di Benjamini-Hochberg
        al 10%. Prima di caricare i dati scrive BTC51_giro_iniziato.json: se esiste gia', si rifiuta.

SCELTA dichiarata (come in validazione): la serie si carica dal 2020-01-01, cosi' l'ATR(14) dello stop arriva gia'
calcolato al 2024-01-01; le decisioni si prendono solo alle chiusure delle candele del vault e nessun dato oltre il
2026-09-30 si usa.

I file del candidato si leggono dal branch della ricerca (``git show <commit>:<percorso>``) al commit della consegna.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

RADICE_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RADICE_REPO))

import numpy as np  # noqa: E402

from research.src import dati  # noqa: E402
from research.src import catalogo3 as cat  # noqa: E402
from research.src import motore3 as mot  # noqa: E402
from research.src import statistica3 as st  # noqa: E402

CARTELLA = Path(__file__).resolve().parent
#: il commit della consegna (Passo 4) sul branch della ricerca
COMMIT_CONSEGNA = "1b222fb5dbf10b002b06f5101ac55716a4cdfc33"
CAMPAGNA = "research/campagne/BTC51"
FILE_CANDIDATO = ["candidati/V-020/regole.md", "codice/lotto_2.json", "codice/lotto.py", "codice/registro.py"]
IMPRONTE_COLLAUDO = RADICE_REPO / "research" / "collaudo_3" / "esiti" / "giro4" / "impronte.json"
GIRO_INIZIATO = CARTELLA / "BTC51_giro_iniziato.json"
ESITO = CARTELLA / "BTC51_vault.json"
SIMBOLO = "BTCUSDT"
TIMEFRAME = "1h"
INIZIO_SERIE = date(2020, 1, 1)


def _git_show(percorso: str) -> bytes:
    return subprocess.run(["git", "-C", str(RADICE_REPO), "show", f"{COMMIT_CONSEGNA}:{percorso}"],
                          check=True, capture_output=True).stdout


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _ora(ms: int) -> str:
    return datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def _pulisci(x):
    if isinstance(x, dict):
        return {str(k): _pulisci(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_pulisci(v) for v in x]
    if isinstance(x, (np.floating, float)):
        v = float(x)
        return None if math.isnan(v) else ("inf" if math.isinf(v) else v)
    if isinstance(x, np.integer):
        return int(x)
    return x


def specifica() -> dict:
    voci = [json.loads(r) for r in _git_show(f"{CAMPAGNA}/log.jsonl").decode("utf-8").splitlines() if r.strip()]
    reg = [x for x in voci if x.get("id") == "V-020" and x.get("tipo") == "registrazione"]
    val = [x for x in voci if x.get("id") == "V-020-VAL" and x.get("tipo") == "registrazione"]
    if len(reg) != 1 or len(val) != 1:
        raise SystemExit(f"registrazioni di V-020 nel log: {len(reg)} di costruzione, {len(val)} di validazione")
    spec = cat.normalizza(reg[0]["specifica"])
    if spec != cat.normalizza(val[0]["specifica"]):
        raise SystemExit("la specifica di V-020 nel log e' diversa da quella della validazione")
    return spec


def verifica() -> dict:
    esito = {"commit_consegna": COMMIT_CONSEGNA}
    attese = json.loads(IMPRONTE_COLLAUDO.read_text(encoding="utf-8"))
    strumenti = {f: _sha((RADICE_REPO / f).read_bytes()) == h for f, h in attese.items()}
    strumenti_ricerca = {f: _sha(_git_show(f)) == h for f, h in attese.items()}
    testo = _git_show(f"{CAMPAGNA}/validazione.md").decode("utf-8")
    congelate = {f: h for f, h in re.findall(r"`([^`]+)`: `([0-9a-f]{64})`", testo)}
    congelate.update({f: h for f, h in re.findall(r"\| `([^`]+)` \| `([0-9a-f]{64})` \|", testo)})
    candidato = {f: {"attesa": congelate.get(f), "trovata": _sha(_git_show(f"{CAMPAGNA}/{f}"))} for f in FILE_CANDIDATO}
    esito["strumenti_uguali_al_collaudo"] = strumenti
    esito["strumenti_uguali_sul_branch_della_ricerca"] = strumenti_ricerca
    esito["candidato"] = candidato
    esito["specifica"] = specifica()
    esito["tutto_uguale"] = (all(strumenti.values()) and all(strumenti_ricerca.values())
                             and all(v["attesa"] == v["trovata"] for v in candidato.values()))
    return esito


def _esegui_periodo(s, spec, a: int, b: int, con_casuali: bool) -> dict:
    c = cat.compila(spec, s)
    ris = mot.esegui(c, mot.Regole(), mot.COSTI_NORMALI, a, b)
    m = mot.metriche(ris, s)
    md = mot.metriche(mot.esegui(c, mot.Regole(), mot.COSTI_DOPPI, a, b), s)
    out = {"periodo_candele": [_ora(s.ts[a]), _ora(s.ts[b])], "candele": b - a + 1, "metriche": m,
           "metriche_costi_doppi": md, "risultato": ris}
    if con_casuali and m["trade"] > 0:
        cas = st.entrate_casuali(c, m["trade"], a, b, mot.Regole(), mot.COSTI_NORMALI, st.N_SIMULAZIONI, st.SEME,
                                 larghezze_candidato=[st.larghezza_stop(t) for t in ris.trade])
        out["p_value"] = st.p_value(m["r_medio"], cas["valori"], st.N_SIMULAZIONI)
        out["casuali"] = {k: v for k, v in cas.items() if k != "valori"}
        out["media_casuali"] = float(np.mean(cas["valori"]))
        out["valori_casuali"] = [float(v) for v in cas["valori"]]
    return out


def _indice(ts, giorno: date) -> int:
    return int(np.searchsorted(np.asarray(ts), dati.ms_da_data(giorno)))


def riproduci() -> dict:
    spec = specifica()
    s = dati.serie_3(SIMBOLO, TIMEFRAME, INIZIO_SERIE, dati.FINE_IN_SAMPLE)
    fine_costr = _indice(s.ts, dati.INIZIO_VALIDAZIONE_3) - 1
    costr = _esegui_periodo(s, spec, 0, fine_costr, con_casuali=True)
    val = _esegui_periodo(s, spec, fine_costr + 1, len(s.ts) - 1, con_casuali=False)
    return {"costruzione": {"periodo": costr["periodo_candele"], "trade": costr["metriche"]["trade"],
                            "r_medio": costr["metriche"]["r_medio"], "p_value": costr["p_value"],
                            "r_costi_doppi": costr["metriche_costi_doppi"]["r_medio"]},
            "validazione": {"periodo": val["periodo_candele"], "trade": val["metriche"]["trade"],
                            "r_medio": val["metriche"]["r_medio"],
                            "profit_factor": val["metriche"]["profit_factor"],
                            "r_costi_doppi": val["metriche_costi_doppi"]["r_medio"]}}


def scarica() -> dict:
    dati.azzera_checksum_mancanti()
    fatti = {}
    for tipo, tf in (("klines", TIMEFRAME), ("markPriceKlines", TIMEFRAME), ("fundingRate", None)):
        p = dati.scarica_periodo(SIMBOLO, tipo, tf, dati.INIZIO_VAULT, dati.FINE_VAULT, verifica_checksum=True)
        fatti[f"{tipo}/{tf}"] = {"mesi": len(p), "primo": p[0].name if p else None, "ultimo": p[-1].name if p else None,
                                 "impronte": {x.name: _sha(x.read_bytes()) for x in p}}
    fatti["checksum_mancanti"] = sorted(getattr(dati, "CHECKSUM_MANCANTI", []))
    return fatti


def esegui() -> dict:
    if GIRO_INIZIATO.exists() or ESITO.exists():
        raise SystemExit("il vault di BTC51 e' gia' stato eseguito: si esegue una volta sola")
    if not dati.vault_aperto():
        raise SystemExit("manca research/vault/APERTURA_3.md")
    v = verifica()
    if not v["tutto_uguale"]:
        raise SystemExit(f"impronte diverse: {json.dumps(v, ensure_ascii=False)}")
    spec = v["specifica"]
    GIRO_INIZIATO.write_text(json.dumps({"iniziato": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                         "verifica": v}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    s, conteggi = dati.serie_3_con_conteggi(SIMBOLO, TIMEFRAME, INIZIO_SERIE, dati.FINE_VAULT)
    a = _indice(s.ts, dati.INIZIO_VAULT)
    b = len(s.ts) - 1
    r = _esegui_periodo(s, spec, a, b, con_casuali=True)
    m, md = r["metriche"], r["metriche_costi_doppi"]
    esiti = st.supera_vault(m, md)
    p = r.get("p_value")
    asticella = st.asticella_vault([p])[0] if p is not None else False
    esiti["asticella_benjamini_hochberg"] = bool(asticella)
    esiti["supera"] = bool(esiti["supera_senza_asticella"] and asticella)
    ris = r.pop("risultato")
    r["conteggi_serie"] = conteggi
    r["esiti"] = esiti
    r["trade"] = [{"ingresso": _ora(t.ts_ingresso), "uscita": _ora(t.ts_uscita), "motivo": t.motivo,
                   "r": round(t.r, 4)} for t in ris.trade]
    r["finito"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ESITO.write_text(json.dumps(_pulisci(r), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return {k: r[k] for k in ("periodo_candele", "candele", "p_value", "media_casuali", "esiti")} | {
        "trade": m["trade"], "trade_al_mese": m["trade_al_mese"], "r_medio": m["r_medio"],
        "profit_factor": m["profit_factor"], "vincenti": m["vincenti"], "drawdown": m["drawdown_max_r"],
        "r_costi_doppi": md["r_medio"], "r_per_anno": m["r_per_anno"], "motivi": m.get("motivi"),
        "ridotti": m.get("ridotti"), "violazioni_liquidazione": m.get("violazioni_liquidazione")}


if __name__ == "__main__":
    comando = {"verifica": verifica, "riproduci": riproduci, "scarica": scarica, "esegui": esegui}[sys.argv[1]]
    print(json.dumps(_pulisci(comando()), indent=1, ensure_ascii=False))
