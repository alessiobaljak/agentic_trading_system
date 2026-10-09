"""Verifiche della Fase 4 su un candidato (dati di costruzione). Scrive risultati/fase4_<chiave>.json.

Uso: python fase4.py <chiave> elenco   -> stampa i casi previsti (per la registrazione)
     python fase4.py <chiave> esegui   -> esegue (le verifiche devono essere gia' registrate)

Regole (PROTOCOLLO.md, Fase 4):
* robustezza: ogni parametro numerico +-20%, uno alla volta (interi: round(0,8 x) e round(1,2 x)
  con le meta' verso l'alto; se uguale, -1 e +1); ogni caso si conta con conta_trade; sotto 70
  trade si dichiara e non conta; un caso non valutabile conta come fallito; superata se nei casi
  che contano il t contro la (b) ricalcolata resta positivo e in almeno meta' batte nettamente, e
  se contano almeno meta' dei casi previsti;
* timeframe adiacenti: parametri in barre convertiti alla stessa durata (intero piu' vicino,
  almeno 1); superata se su ognuno con i trade minimi il t contro la (b) resta positivo;
* ritardo di una barra: t contro la (b) ricalcolata col ritardo positivo e almeno meta';
* costi doppi: batte ancora nettamente la (b) a costi doppi e R medio a costi doppi positivo;
* stabilita': R medio sopra la media della (b) in piu' della meta' degli anni con almeno 10 trade;
* trade estremi: R senza i 3 migliori sopra la media della (b);
* regola intra-barra opposta: si dichiara la differenza;
* liquidazione: nessuna violazione.
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune  # noqa: E402
from varianti import VARIANTI  # noqa: E402


def arrotonda(x):
    return int(math.floor(x + 0.5))


def spostamenti_intero(v):
    giu, su = arrotonda(0.8 * v), arrotonda(1.2 * v)
    if giu == v:
        giu = v - 1
    if su == v:
        su = v + 1
    return giu, su


# Parametri numerici di ogni candidato (i booleani e le scelte, come il minuto del segnale, non si spostano)
NUMERICI = {
    "V-14": {"finestra": "int", "soglia_z": "float", "barre": "int", "mult_atr": "float", "atr_n": "int"},
    "V-12": {"barre": "int", "mult_atr": "float", "atr_n": "int"},
}
# Timeframe adiacenti con i parametri in barre convertiti alla stessa durata
ADIACENTI = {
    "V-14": [("2h", {"finestra": 360, "barre": 12, "atr_n": 28}), ("6h", {"finestra": 120, "barre": 4, "atr_n": 9})],
    # 15m: segnale alla chiusura della barra 23:15-23:30, uscita dopo 2 barre (00:00), ATR 28 barre;
    # 1h: la mezz'ora non esiste: segnale alla chiusura della barra 22:00-23:00 (ingresso 23:00), 1 barra, ATR 7
    "V-12": [("15m", {"minuto_segnale": 1395, "barre": 2, "atr_n": 28}), ("1h", {"minuto_segnale": 1320, "barre": 1, "atr_n": 7})],
}


def casi_robustezza(chiave):
    var = VARIANTI[chiave]
    casi = []
    for nome, tipo in NUMERICI[chiave].items():
        v = var.parametri.get(nome, 14 if nome == "atr_n" else None)
        if tipo == "int":
            giu, su = spostamenti_intero(int(v))
        else:
            giu, su = round(0.8 * v, 10), round(1.2 * v, 10)
        for nuovo in (giu, su):
            casi.append((f"{nome}={nuovo}", {nome: nuovo}))
    return casi


def nuova(var, tf=None, **mod):
    p = dict(var.parametri)
    p.setdefault("atr_n", 14)
    p.update(mod)
    return type(var)(var.id, tf or var.tf, var.direzione, **p)


def scrivi(msg):
    with (comune.CARTELLA_DATI / "fase4_avanzamento.txt").open("a", encoding="utf-8") as f:
        f.write(msg + "\n")


def main():
    chiave, modo = sys.argv[1], sys.argv[2]
    var = VARIANTI[chiave]
    if modo == "elenco":
        print("robustezza", casi_robustezza(chiave))
        print("adiacenti", ADIACENTI[chiave])
        return
    if modo == "conta":
        conti = {}
        for nome, mod in casi_robustezza(chiave):
            if nome != "barre=0":
                conti[nome] = comune.conta(nuova(var, **mod))["trade"]
        for tf, mod in ADIACENTI[chiave]:
            conti[tf] = comune.conta(nuova(var, tf=tf, **mod))["trade"]
        print(chiave, json.dumps(conti))
        return
    base = json.loads((comune.CARTELLA / "risultati" / f"{chiave}.json").read_text(encoding="utf-8"))
    t0 = base["baseline_b"]["t"]
    media_b = base["baseline_b"]["media"]
    out = {"candidato": var.id, "t_b_costruzione": t0, "media_b": media_b}

    # robustezza
    rob = []
    for nome, mod in casi_robustezza(chiave):
        if nome == "barre=0":
            rob.append({"caso": nome, "esito": "non costruibile: una posizione di 0 barre non esiste; dichiarato, non conta"})
            continue
        v = nuova(var, **mod)
        n = comune.conta(v)["trade"]
        if n < comune.TRADE_MIN["costruzione"]:
            rob.append({"caso": nome, "trade": n, "esito": "sotto i trade minimi: dichiarato, non conta"})
            continue
        r = comune.valuta(v, "costruzione", solo_b=True)
        b = r["baseline_b"]
        rob.append({"caso": nome, "trade": n, "r_medio": r["metriche"]["r_medio"], "t_b": b.get("t"),
                    "netta_b": b.get("netta"), "valutabile": b.get("valutabile")})
        scrivi(f"{chiave} robustezza {nome} t {b.get('t')}")
    contano = [c for c in rob if "t_b" in c]
    previsti = len(casi_robustezza(chiave))
    positivi = all(c["valutabile"] and c["t_b"] is not None and c["t_b"] > 0 for c in contano)
    nette = sum(1 for c in contano if c["valutabile"] and c["netta_b"])
    out["robustezza"] = {"casi": rob, "previsti": previsti, "contano": len(contano), "nette": nette,
                         "superata": bool(contano) and len(contano) * 2 >= previsti and positivi and nette * 2 >= len(contano)}

    # timeframe adiacenti
    adi = []
    for tf, mod in ADIACENTI[chiave]:
        v = nuova(var, tf=tf, **mod)
        n = comune.conta(v)["trade"]
        if n < comune.TRADE_MIN["costruzione"]:
            adi.append({"timeframe": tf, "trade": n, "esito": "sotto i trade minimi: dichiarato, non conta"})
            continue
        r = comune.valuta(v, "costruzione", solo_b=True)
        b = r["baseline_b"]
        adi.append({"timeframe": tf, "parametri": mod, "trade": n, "r_medio": r["metriche"]["r_medio"],
                    "t_b": b.get("t"), "netta_b": b.get("netta"), "valutabile": b.get("valutabile")})
        scrivi(f"{chiave} adiacente {tf} t {b.get('t')}")
    contano_adi = [c for c in adi if "t_b" in c]
    out["timeframe_adiacenti"] = {"casi": adi, "superata": all(c["valutabile"] and c["t_b"] > 0 for c in contano_adi)}

    # ritardo di una barra
    r = comune.valuta(var, "costruzione", parametri=comune.parametri_con(ritardo_barre=1), solo_b=True)
    tr = r["baseline_b"].get("t")
    out["ritardo"] = {"trade": r["metriche"]["trade"], "r_medio": r["metriche"]["r_medio"], "t_b": tr,
                      "media_b": r["baseline_b"].get("media"),
                      "superata": tr is not None and tr > 0 and tr >= 0.5 * t0}
    scrivi(f"{chiave} ritardo t {tr}")

    # costi doppi
    r = comune.valuta(var, "costruzione", parametri=comune.parametri_con(moltiplicatore_costi=2.0), solo_b=True)
    b = r["baseline_b"]
    out["costi_doppi"] = {"trade": r["metriche"]["trade"], "r_medio": r["metriche"]["r_medio"], "t_b": b.get("t"),
                          "media_b": b.get("media"), "netta_b": b.get("netta"),
                          "superata": bool(b.get("netta")) and r["metriche"]["r_medio"] > 0}
    scrivi(f"{chiave} costi doppi t {b.get('t')} r {r['metriche']['r_medio']}")

    # regola intra-barra opposta (si dichiara)
    r = comune.valuta(var, "costruzione", parametri=comune.parametri_con(riempimento_intrabarra="target_prima"), solo_b=True)
    out["intrabarra_opposta"] = {"r_medio": r["metriche"]["r_medio"], "differenza_r": round(r["metriche"]["r_medio"] - base["metriche"]["r_medio"], 6),
                                 "t_b": r["baseline_b"].get("t")}

    # stabilita', trade estremi, liquidazione (dal risultato di costruzione)
    m = base["metriche"]
    anni = [a for a, n in m["trade_per_anno"].items() if n >= 10]
    sopra = [a for a in anni if m["r_medio_per_anno"][a] > media_b]
    out["stabilita"] = {"anni_con_10_trade": anni, "anni_sopra_b": sopra, "superata": len(sopra) * 2 > len(anni)}
    out["trade_estremi"] = {"r_senza_3_migliori": m["r_medio_senza_3_migliori"], "media_b": media_b,
                            "superata": m["r_medio_senza_3_migliori"] > media_b}
    out["liquidazione"] = {"violazioni": m["violazioni_liquidazione"], "superata": m["violazioni_liquidazione"] == 0}
    out["tutte_superate"] = all(out[k]["superata"] for k in ("robustezza", "timeframe_adiacenti", "ritardo", "costi_doppi",
                                                              "stabilita", "trade_estremi", "liquidazione"))
    (comune.CARTELLA / "risultati" / f"fase4_{chiave}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    scrivi(f"{chiave} fine, tutte superate: {out['tutte_superate']}")


if __name__ == "__main__":
    main()
