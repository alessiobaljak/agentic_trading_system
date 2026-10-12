"""Ricalcolo dopo la correzione del caricatore del funding (CHANGELOG 2026-10-08).

Uso: python research/campagne/ETHUSDT/codice/ricalcolo.py

Riesegue, con lo stesso codice della campagna (comune.conta, comune.valuta, le regole
di verifiche.py), gli stessi parametri e gli stessi semi, ogni calcolo gia' registrato
nel log che usa il funding:
* il controllo positivo ETHUSDT-C01 (senza ritardo e con il ritardo di una barra);
* il conteggio dei trade delle 34 varianti contate (30 registrate e 4 scarti);
* il giro di Fase 2 delle 30 varianti testate;
* le 6 verifiche della Fase 4 di ETHUSDT-026 (I-14a).

Non scrive nel log: ogni esito va in data/insample/ETHUSDT/lavoro/ricalcolo/<chiave>.json,
e l'avanzamento in lavoro/ricalcolo/avanzamento.txt. Le voci ``correzione`` le scrive
correzioni.py, dopo, confrontando con le voci originali. Un esito gia' su disco non si rifa'.
"""

import json
import math
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune  # noqa: E402
import controllo_positivo  # noqa: E402
import idee  # noqa: E402
import registro  # noqa: E402
import verifiche  # noqa: E402
from registra import parametri_completi  # noqa: E402

CARTELLA = comune.LAVORO / "ricalcolo"
AVANZAMENTO = CARTELLA / "avanzamento.txt"
CANDIDATO = "I-14a"


def nomi_contati():
    return [v["variante_ipotesi"] for v in registro.voci()
            if v["tipo"] in ("registrazione", "scarto") and v.get("tipo_test", "variante") == "variante"
            and v.get("variante_ipotesi") in idee.VARIANTI]


def nomi_testati():
    return [v["variante_ipotesi"] for v in registro.voci()
            if v["tipo"] == "registrazione" and v.get("tipo_test") == "variante"]


def scrivi(chiave, esito, secondi):
    CARTELLA.mkdir(parents=True, exist_ok=True)
    (CARTELLA / f"{chiave}.json").write_text(
        json.dumps(registro.pulisci({"chiave": chiave, "secondi": round(secondi, 1), "esito": esito}),
                   indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    with open(AVANZAMENTO, "a", encoding="utf-8") as f:
        f.write(f"{registro.adesso()} {chiave} {round(secondi, 1)} s\n")


def leggi(chiave):
    p = CARTELLA / f"{chiave}.json"
    return json.loads(p.read_text(encoding="utf-8"))["esito"] if p.is_file() else None


def lavoro(compito):
    """Un calcolo indipendente; ritorna la chiave."""
    tipo, nome, extra = compito
    chiave = f"{tipo}_{nome}" + (f"_{extra}" if extra else "")
    if (CARTELLA / f"{chiave}.json").is_file():
        return chiave
    inizio = time.time()
    if tipo == "controllo":
        V, kw, tf = controllo_positivo.VARIANTI[nome]
        p = comune.parametri(ritardo_barre=1) if extra == "ritardo" else None
        esito = comune.valuta(V, kw, tf, p, con_a=(extra != "ritardo"))
    elif tipo == "conta":
        V, kw, tf = idee.VARIANTI[nome]
        esito = comune.conta(V, kw, tf)
    elif tipo == "costruzione":
        V, kw, tf = idee.VARIANTI[nome]
        esito = comune.valuta(V, kw, tf)
    elif tipo == "verifica":
        esito = verifica_semplice(nome, extra)
    elif tipo == "robustezza":
        V, kw, tf = idee.VARIANTI[nome]
        caso = verifiche.casi_robustezza(V, kw)[int(extra)]
        conteggio = comune.conta(V, caso["kw"], tf)["trade"]
        esito = {"parametro": caso["parametro"], "valore": caso["valore"], "trade_stimati": conteggio}
        if conteggio >= comune.TRADE_MINIMI_COSTRUZIONE:
            esito["sintesi"] = verifiche.sintesi(comune.valuta(V, caso["kw"], tf, con_a=False))
    elif tipo == "adiacente":
        V, kw, tf = idee.VARIANTI[nome]
        k2 = verifiche.kw_timeframe(V, kw, tf, extra)
        conteggio = comune.conta(V, k2, extra)["trade"]
        esito = {"timeframe": extra, "parametri": k2, "trade_stimati": conteggio}
        if conteggio >= comune.TRADE_MINIMI_COSTRUZIONE:
            esito["sintesi"] = verifiche.sintesi(comune.valuta(V, k2, extra, con_a=False))
    else:
        raise ValueError(tipo)
    scrivi(chiave, esito, time.time() - inizio)
    return chiave


def verifica_semplice(nome, verifica):
    """Costi doppi, ritardo e regola intra-barra opposta: come verifiche.main, senza il log."""
    V, kw, tf = idee.VARIANTI[nome]
    if verifica == "costi_doppi":
        p = comune.parametri(moltiplicatore_costi=2.0)
    elif verifica == "ritardo":
        p = comune.parametri(ritardo_barre=1)
    elif verifica == "intrabarra_opposta":
        p = comune.parametri(riempimento_intrabarra="target_prima")
    else:
        raise ValueError(verifica)
    return verifiche.sintesi(comune.valuta(V, kw, tf, p, con_a=False))


def esiti_verifiche(nome):
    """Gli esiti delle 6 verifiche con le regole di verifiche.main, sui numeri ricalcolati."""
    V, kw, tf = idee.VARIANTI[nome]
    ris = leggi(f"costruzione_{nome}")
    t0 = float(ris["baseline_b"]["t"])
    media_b0 = float(ris["baseline_b"]["media"])
    out = {}
    s = leggi(f"verifica_{nome}_costi_doppi")
    out["costi_doppi"] = {"esito": s, "superata": bool(s["netta_b"] and s["r_medio"] > 0)}
    s = leggi(f"verifica_{nome}_ritardo")
    t1 = s["t_b"] if isinstance(s["t_b"], (int, float)) else -math.inf
    out["ritardo"] = {"esito": s, "t_senza_ritardo": t0, "superata": bool(t1 > 0 and t1 >= 0.5 * t0)}
    s = leggi(f"verifica_{nome}_intrabarra_opposta")
    out["intrabarra_opposta"] = {"esito": s, "differenza_r_medio": s["r_medio"] - float(ris["metriche"]["r_medio"]),
                                 "superata": None}
    casi = verifiche.casi_robustezza(V, kw)
    righe, contano, positivi, netti = [], 0, 0, 0
    for k in range(len(casi)):
        e = leggi(f"robustezza_{nome}_{k}")
        riga = {"parametro": e["parametro"], "valore": e["valore"], "trade_stimati": e["trade_stimati"]}
        if "sintesi" not in e:
            riga["conta"] = False
        else:
            s = e["sintesi"]
            riga.update(s)
            riga["conta"] = True
            contano += 1
            if s["valutabile_b"] and s["t_b"] > 0:
                positivi += 1
            if s["valutabile_b"] and s["netta_b"]:
                netti += 1
        righe.append(riga)
    out["robustezza"] = {"casi": righe, "casi_previsti": len(casi), "casi_che_contano": contano,
                         "t_positivo": positivi, "netti": netti,
                         "superata": bool(contano >= len(casi) / 2 and positivi == contano and netti >= contano / 2)}
    righe, ok = [], True
    for tf2 in verifiche.ADIACENTI[tf]:
        e = leggi(f"adiacente_{nome}_{tf2}")
        riga = {"timeframe": tf2, "parametri": e["parametri"], "trade_stimati": e["trade_stimati"]}
        if "sintesi" not in e:
            riga["conta"] = False
        else:
            s = e["sintesi"]
            riga.update(s)
            riga["conta"] = True
            if not (s["valutabile_b"] and s["t_b"] > 0):
                ok = False
        righe.append(riga)
    out["timeframe_adiacenti"] = {"casi": righe, "superata": ok}
    m = ris["metriche"]
    anni = [a for a, n in m["trade_per_anno"].items() if n >= 10]
    sopra = [a for a in anni if m["r_medio_per_anno"][a] > media_b0]
    stabile = len(sopra) > len(anni) / 2
    senza3 = m["r_medio_senza_3_migliori"]
    estremi = senza3 is not None and senza3 > media_b0
    liq = m.get("n_violazioni_liquidazione", 0) == 0
    out["stabilita_estremi_liquidazione"] = {
        "anni_con_10_trade": anni, "anni_sopra_media_b": sopra, "media_b": media_b0, "stabilita": stabile,
        "r_senza_3_migliori": senza3, "estremi": estremi,
        "violazioni_liquidazione": m.get("n_violazioni_liquidazione"), "liquidazione": liq,
        "superata": bool(stabile and estremi and liq)}
    return out


def main() -> None:
    V, kw, tf = idee.VARIANTI[CANDIDATO]
    compiti = [("controllo", "ETHUSDT-C01", ""), ("controllo", "ETHUSDT-C01", "ritardo")]
    compiti += [("costruzione", n, "") for n in nomi_testati()]
    compiti += [("conta", n, "") for n in nomi_contati()]
    compiti += [("verifica", CANDIDATO, v) for v in ("costi_doppi", "ritardo", "intrabarra_opposta")]
    compiti += [("robustezza", CANDIDATO, str(k)) for k in range(len(verifiche.casi_robustezza(V, kw)))]
    compiti += [("adiacente", CANDIDATO, t) for t in verifiche.ADIACENTI[tf]]
    CARTELLA.mkdir(parents=True, exist_ok=True)
    with open(AVANZAMENTO, "a", encoding="utf-8") as f:
        f.write(f"{registro.adesso()} inizio: {len(compiti)} calcoli\n")
    with ProcessPoolExecutor(max_workers=4) as pool:
        for chiave in pool.map(lavoro, compiti):
            pass
    scrivi(f"verifiche_{CANDIDATO}", esiti_verifiche(CANDIDATO), 0.0)
    with open(AVANZAMENTO, "a", encoding="utf-8") as f:
        f.write(f"{registro.adesso()} fine\n")


if __name__ == "__main__":
    main()
