"""Registra e testa le varianti del catalogo, scrivendo il log (sezione 6 del protocollo).

Uso:
  python -m research.campagne.GALAUSDT.codice.lancia registra <ID> [<ID> ...]
      conta i trade con conta_trade (una volta sola) e scrive la registrazione, oppure lo scarto
      se sotto i 70 trade minimi di costruzione;
  python -m research.campagne.GALAUSDT.codice.lancia testa <ID>
      esegue il test di costruzione di una variante gia' registrata e scrive il risultato.
L'avanzamento e i dettagli vanno in research/data/insample/GALAUSDT/uscite/ (fuori da git).
"""

from __future__ import annotations

import fcntl
import json
import math
import sys
import time

from research.campagne.GALAUSDT.codice import comune, registro
from research.campagne.GALAUSDT.codice.catalogo import CATALOGO, crea_variante

USCITE = comune.CARTELLA_DATI / "uscite"
TRADE_MINIMI = 70


def _con_blocco(funzione):
    USCITE.mkdir(parents=True, exist_ok=True)
    with open(USCITE / ".blocco", "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            return funzione()
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def voci_log():
    if not registro.LOG.exists():
        return []
    return [json.loads(r) for r in registro.LOG.read_text(encoding="utf-8").splitlines() if r.strip()]


def registra(vid: str) -> None:
    voce = CATALOGO[vid]
    if any(v.get("id") == vid and v.get("tipo") in ("registrazione", "scarto") for v in voci_log()):
        print(vid, "gia' registrata o scartata: non si riconta")
        return
    var = crea_variante(vid)
    conteggio = comune.conta(var)

    def scrivi():
        base = {
            "id": vid, "idea": voce["idea"], "famiglia": voce.get("famiglia", vid),
            "ritocco_di": voce.get("ritocco_di"), "fonte": voce["fonte"], "meccanismo": voce["meccanismo"],
            "timeframe": var.tf, "direzione": var.direzione, "classe": var.__class__.__name__,
            "parametri": var.p, "regole": voce["regole"], "periodo": "costruzione",
            "previsione": voce["previsione"], "criterio_successo": voce.get("criterio_successo", CRITERIO),
            "trade_stimati": conteggio["trade"], "conteggio": conteggio,
        }
        if voce.get("ritocco_di"):
            base["cosa_cambia"] = voce.get("cosa_cambia")
        if conteggio["trade"] < TRADE_MINIMI:
            base.update({"tipo": "scarto", "tipo_test": "variante",
                         "motivo": f"trade stimati {conteggio['trade']} sotto il minimo di costruzione {TRADE_MINIMI}"})
        else:
            base.update({"tipo": "registrazione", "tipo_test": "variante",
                         "variante_n": registro.ultimo_id_variante() + 1})
        return registro.aggiungi(base)

    scritta = _con_blocco(scrivi)
    print(vid, scritta["tipo"], "trade stimati", conteggio["trade"], scritta.get("variante_n"))


CRITERIO = ("candidato se batte nettamente la (a) e la (b) con contro_baseline e R medio dopo i costi > 0, "
            "sui dati di costruzione")


def testa(vid: str) -> None:
    voci = voci_log()
    reg = [v for v in voci if v.get("id") == vid and v.get("tipo") == "registrazione"]
    if not reg:
        raise SystemExit(f"{vid}: nessuna registrazione nel log: prima si registra")
    if any(v.get("id") == vid and v.get("tipo") == "risultato" for v in voci):
        raise SystemExit(f"{vid}: risultato gia' scritto")
    var = crea_variante(vid)
    t0 = time.time()
    ris = comune.valuta(var, "costruzione")
    minuti = (time.time() - t0) / 60
    m = ris["metriche"]
    if m.get("trade") != reg[0]["trade_stimati"]:
        print("ATTENZIONE: trade del test diversi dalla stima", m.get("trade"), reg[0]["trade_stimati"])
    prev = reg[0]["previsione"]
    corretta = None
    if isinstance(prev, dict) and "r_medio_min" in prev and "r_medio" in m:
        corretta = bool(prev["r_medio_min"] <= m["r_medio"] <= prev["r_medio_max"])
    dettagli = {k: v for k, v in ris.items() if k != "trades_r"}

    def scrivi():
        return registro.aggiungi({
            "id": vid, "tipo": "risultato", "periodo": "costruzione",
            "metriche": m, "blocco": ris.get("blocco"),
            "baseline_a": ris.get("baseline_a"), "baseline_b": ris.get("baseline_b"),
            "percentile_caso": ris.get("percentile_caso"),
            "buy_and_hold_per_anno": ris.get("buy_and_hold_per_anno"),
            "valutabile": ris.get("valutabile"), "batte_a_e_b": ris.get("batte_a_e_b"),
            "candidato": ris.get("candidato"), "previsione_corretta": corretta,
            "minuti_di_calcolo": round(minuti, 2),
        })

    _con_blocco(scrivi)
    USCITE.mkdir(parents=True, exist_ok=True)
    (USCITE / f"{vid}.json").write_text(json.dumps(registro._pulisci(ris), indent=1), encoding="utf-8")
    ba, bb = ris.get("baseline_a", {}), ris.get("baseline_b", {})
    print(vid, "trade", m.get("trade"), "R", round(m.get("r_medio", float("nan")), 4),
          "t_a", ba.get("t"), "t_b", bb.get("t"), "candidato", ris.get("candidato"))


if __name__ == "__main__":
    comando, ids = sys.argv[1], sys.argv[2:]
    for vid in ids:
        if comando == "registra":
            registra(vid)
        elif comando == "testa":
            testa(vid)
        else:
            raise SystemExit("comando: registra | testa")
