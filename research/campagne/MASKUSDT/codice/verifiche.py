"""Fase 4: verifiche del candidato MASKUSDT-029 sui dati di costruzione, ognuna registrata prima.

Le verifiche non cambiano le regole del candidato e non servono a sceglierne un'altra.
Criteri (PROTOCOLLO.md, Fase 4, «Quando una verifica e' superata»):
* robustezza: ogni parametro numerico +-20% uno alla volta (interi a round(0,8x) e round(1,2x),
  meta' verso l'alto; se uguale, +-1); casi sotto 70 trade dichiarati e non contati; non
  valutabile = fallito; nei casi che contano t contro la (b) positivo in tutti e netto in almeno
  meta'; se contano meno della meta' dei casi previsti, non superata;
* timeframe adiacenti (30m e 2h, parametri in barre convertiti): t contro la (b) positivo dove
  ci sono i trade minimi;
* stabilita': R medio sopra la media della (b) in piu' della meta' degli anni con almeno 10 trade;
* pochi trade estremi: senza i 3 migliori R medio sopra la media della (b);
* regola intra-barra opposta: si dichiara la differenza;
* ritardo di una barra: t contro la (b) col ritardo positivo e almeno meta' del t senza ritardo;
* liquidazione: nessuna violazione;
* costi doppi: netto contro la (b) a costi doppi e R medio a costi doppi positivo.
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import quadro  # noqa: E402
import registro  # noqa: E402
from campagna import _scrivi_esito, stampa  # noqa: E402
from registro_ritocchi import R2  # noqa: E402

CAND = "MASKUSDT-029"


def arrot(x):
    return int(math.floor(x + 0.5))


def sposta_intero(v):
    giu, su = arrot(0.8 * v), arrot(1.2 * v)
    if giu == v:
        giu = v - 1
    if su == v:
        su = v + 1
    return giu, su


def classe(**attr):
    return type("Caso", (R2,), dict(attr))


def casi_robustezza():
    out = []
    for nome, attr, val in [("dev", "dev", 3.0), ("stop_atr", "k_stop", 2.0), ("target_rapporto", "rr", 2.0)]:
        for seg, f in (("giu", 0.8), ("su", 1.2)):
            out.append((f"rob-{nome}-{seg}", {attr: round(val * f, 10)}, f"{nome} {val} -> {round(val * f, 10)}"))
    for nome, attr, val in [("finestra_dev", "finestra_dev", 168), ("uscita_barre", "barre_max", 12), ("atr_barre", "n_atr", 14)]:
        giu, su = sposta_intero(val)
        out.append((f"rob-{nome}-giu", {attr: giu}, f"{nome} {val} -> {giu}"))
        out.append((f"rob-{nome}-su", {attr: su}, f"{nome} {val} -> {su}"))
    return out


def breve(e):
    b, a = e.get("baseline_b", {}), e.get("baseline_a", {})
    m = e["metriche"]
    return {"trade": m["trade"], "r_medio": m["r_medio"], "profit_factor": m["profit_factor"],
            "r_medio_per_anno": m["r_medio_per_anno"], "trade_per_anno": m["trade_per_anno"],
            "r_medio_senza_3_migliori": m["r_medio_senza_3_migliori"], "drawdown_max": m["drawdown_max"],
            "n_violazioni_liquidazione": m["n_violazioni_liquidazione"], "n_ridotti": m["n_ridotti"],
            "stop_oltre_6pct": m["stop_oltre_6pct"], "stop_pct_mediana": m["stop_pct_mediana"],
            "t_b": b.get("t"), "soglia_b": b.get("soglia"), "netta_b": b.get("netta"), "valutabile_b": b.get("valutabile"),
            "media_b": b.get("media"), "t_a": a.get("t"), "netta_a": a.get("netta"), "valutabile": e.get("valutabile")}


def esegui(nome, cls, descr, par_kwargs=None, criterio=""):
    vid = f"{CAND}-V-{nome}"
    if any(v.get("id") == vid for v in registro.voci()):
        stampa(vid, "gia' fatta")
        return None
    par_kwargs = par_kwargs or {}
    var = cls()
    cont = quadro.conta(var, quadro.parametri(**par_kwargs))
    registro.aggiungi({"id": vid, "tipo": "registrazione", "tipo_test": "verifica", "verifica_di": CAND,
                       "verifica": descr, "timeframe": var.tf, "direzione": var.direzione,
                       "parametri_motore": par_kwargs, "periodo": "costruzione", "trade_stimati": cont["trade"],
                       "criterio_successo": criterio})
    if cont["trade"] < quadro.TRADE_MINIMI_COSTRUZIONE:
        registro.aggiungi({"id": vid, "tipo": "risultato", "sotto_minimo": True, "trade": cont["trade"],
                           "commento": "sotto i trade minimi di costruzione: si dichiara e non conta"})
        return {"sotto_minimo": True, "trade": cont["trade"]}
    e = quadro.valuta(var, **par_kwargs)
    _scrivi_esito(vid, e)
    b = breve(e)
    registro.aggiungi({"id": vid, "tipo": "risultato", "metriche_breve": b, "blocco": e.get("blocco"),
                       "baseline_b": e.get("baseline_b"), "percentile_caso": e.get("percentile_caso")})
    stampa(vid, json.dumps(registro._pulisci(b)))
    return b


def main():
    esiti = {}
    base = esegui("ripetizione", R2, "ripetizione del test del candidato (controllo che il codice dia lo stesso risultato)",
                  criterio="stesso R medio e stessi trade del risultato registrato")
    esiti["ripetizione"] = base
    crit_rob = "t contro la (b) positivo in tutti i casi che contano, netto in almeno meta'"
    for nome, attr, descr in casi_robustezza():
        esiti[nome] = esegui(nome, classe(**attr), "robustezza: " + descr, criterio=crit_rob)
    crit_tf = "t contro la (b) ricalcolata positivo"
    esiti["tf-30m"] = esegui("tf-30m", classe(tf="30m", finestra_dev=336, barre_max=24, n_atr=28),
                             "timeframe adiacente 30m (finestra 336, uscita 24 barre, ATR 28 barre)", criterio=crit_tf)
    esiti["tf-2h"] = esegui("tf-2h", classe(tf="2h", finestra_dev=84, barre_max=6, n_atr=7),
                            "timeframe adiacente 2h (finestra 84, uscita 6 barre, ATR 7 barre)", criterio=crit_tf)
    esiti["ritardo-1"] = esegui("ritardo-1", R2, "ritardo di una barra", {"ritardo_barre": 1},
                                criterio="t contro la (b) col ritardo positivo e almeno meta' del t senza ritardo")
    esiti["costi-doppi"] = esegui("costi-doppi", R2, "costi doppi", {"moltiplicatore_costi": 2.0},
                                  criterio="netto contro la (b) a costi doppi e R medio positivo")
    esiti["intrabarra-opposta"] = esegui("intrabarra-opposta", R2, "regola intra-barra opposta (target prima)",
                                         {"riempimento": "target_prima"}, criterio="si dichiara la differenza")
    p = quadro.RADICE_REPO / "research" / "data" / "insample" / "MASKUSDT" / "risultati" / "verifiche_029.json"
    p.write_text(json.dumps(registro._pulisci(esiti), indent=1))
    stampa("fine verifiche")


if __name__ == "__main__":
    main()
