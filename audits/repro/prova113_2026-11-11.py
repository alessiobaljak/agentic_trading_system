"""Audit della prova 113 (N3G, `research/programma7/CINQUANTUNESIMA.md`), 11 novembre 2026.

Non esegue il `main` di nessuna prova e non scrive fuori da `audits/` (catalogo, voce 11): importa le funzioni e scrive
l'esito in `audits/repro/prova113_2026-11-11_esito.json`.

Parti (argomento a riga di comando):
  riproduci  rifà la 113 dal file degli eventi committato (stesso codice, stesso seme) e confronta con `esame.json`
  etichette  le 87 monete «gratis» con il titolo dell'annuncio; i candidati mancati (annunci fuori finestra, in altri file)
  copertura  quanti annunci «gratis» per anno ci sono nel file delle quotazioni
  rifai32    rifà gli eventi della prova 32 con `esecuzione.ore_di` di oggi (dopo la correzione del 25 ottobre), senza
             scaricare niente, e li confronta con `eventi_N3B.csv`
  riuso      simboli riusati: pause di volume zero o di candele mancanti fra la prima candela e la fine della tenuta
  funding    giorni della tenuta senza funding vero; il giorno d'uscita contato intero
  scarica <cartella>           i file mensili orari che mancano in research/data/p6h, in una cartella temporanea
  rifai32_tutti <cartella>     tutti gli eventi della 32 con le ore complete (scrive prova113_rifai32_tutti.csv)
  rifai32_21ottobre <cartella> le ore tagliate al 30 settembre 2026 (come il 21 ottobre; MARSCOIN non riprodotto)
  corretta   l'esame della 113 sul file, sul file più i 19 eventi persi, sugli eventi rifatti; finestra ±10% e ±20%
  dettagli   ore mancanti, «senza uscita» con la liquidazione, concentrazione, clima, strati più fini (per capire)
  stop <cartella>              uscita a +24/+27/+33/+36% (per capire)
Uso: PYTHONPATH=<radice> python3 audits/repro/prova113_2026-11-11.py <parte> [cartella]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import annunci as an
from research.programma6 import esecuzione as es
from research.programma6 import seconda as sc
from research.programma6 import trentaduesima as t32
from research.programma6 import trentesima as tr
from research.programma7 import cinquantunesima as c51

RADICE = Path(__file__).resolve().parents[2]
QUI = Path(__file__).parent
ESITO = QUI / "prova113_2026-11-11_esito.json"
EVENTI32 = RADICE / "research/programma6/risultati_trentaduesima/eventi_N3B.csv"
ESAME113 = RADICE / "research/programma7/risultati_cinquantunesima/esame.json"


def salva(chiave: str, valore) -> None:
    d = json.loads(ESITO.read_text()) if ESITO.exists() else {}
    d[chiave] = valore
    ESITO.write_text(json.dumps(d, ensure_ascii=False, indent=1, default=str))


def esame113(ev: pd.DataFrame, pan_simboli, seme: int = c51.SEME, n: int = c51.MESCOLATE) -> dict:
    """Lo stesso calcolo di `cinquantunesima.esegui`, senza scrivere file."""
    d = c51.etichetta(ev, c51.gratis(pan_simboli))
    obs = c51.differenza(d)
    perm = c51.mescola(d, n=n, seme=seme)
    p = float((np.sum(perm >= obs) + 1) / (len(perm) + 1))
    g, o = d[d["gratis"]], d[~d["gratis"]]
    ex = tr.esame(g, "r")
    return {"eventi": len(d), "gratis": int(len(g)), "altre": int(len(o)), "differenza": float(obs), "p_differenza": p,
            "differenza_senza_uscita": float(c51.differenza(d, "r_senza")),
            "media_gratis": float(g["r"].mean()), "media_altre": float(o["r"].mean()),
            "gratis_da_sole_p": ex["boot"]["p"], "gratis_prima_meta": ex["prima_meta"], "gratis_seconda_meta": ex["seconda_meta"],
            "gratis_senza_5": ex["senza_5_migliori"], "esame_gratis": ex["esito"],
            "per_anno_gratis": {a: [int(len(x)), float(x["r"].mean())] for a, x in g.groupby(g["data"].str[:4])},
            "per_tipo": {t: [int(len(x)), float(x["r"].mean())] for t, x in g.groupby("tipo")},
            "trimestri": int(sum(1 for _, q in d.groupby("trimestre") if 0 < q["gratis"].sum() < len(q))),
            "passa_regole": bool(p <= 0.01 and ex["esito"] == "VALIDA")}, d


def riproduci() -> None:
    pan = sc.pannello()
    ev = pd.read_csv(EVENTI32)
    out, d = esame113(ev, pan["simboli"])
    ref = json.loads(ESAME113.read_text())
    conf = {k: (out[k], ref[k]) for k in ("eventi", "gratis", "altre", "differenza", "p_differenza", "differenza_senza_uscita",
                                          "media_gratis", "media_altre")}
    conf["gratis_da_sole_p"] = (out["gratis_da_sole_p"], ref["esame_gratis"]["boot"]["p"])
    uguale = all(abs(float(a) - float(b)) < 1e-12 for a, b in conf.values())
    # stabilità della p rispetto al seme (per capire, non per decidere)
    semi = {s: esame113(ev, pan["simboli"], seme=s)[0]["p_differenza"] for s in (1, 7, 42, 2027)}
    salva("riproduci", {"confronto": conf, "identico": uguale, "p_con_altri_semi": semi})
    print("identico:", uguale)
    for k, v in conf.items():
        print(f"  {k}: rifatto {v[0]} / file {v[1]}")
    print("p con altri semi:", semi)


def _annunci_tutti() -> list:
    out = []
    for f in sorted((RADICE / "research/data/annunci").glob("*.json")):
        try:
            x = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(x, list):
            out += [dict(a, file=f.name) for a in x if isinstance(a, dict) and "titolo" in a]
    return out


def etichette() -> None:
    pan = sc.pannello()
    ev = pd.read_csv(EVENTI32)
    g = c51.gratis(pan["simboli"])
    d = c51.etichetta(ev, g)
    quot = json.loads(c51.QUOTAZIONI.read_text(encoding="utf-8"))
    # per ogni gratis: l'annuncio scelto (primo nella finestra), quanti giorni prima dell'entrata, le sigle del titolo
    righe = []
    for _, r in d[d["gratis"]].iterrows():
        ann = [x for x in quot if c51.GRATIS.search(x["titolo"]) and "Launchpad" not in x["titolo"]
               and any(an.perpetuo(s, pan["simboli"]) == r["simbolo"] for s in re.findall(r"\(([A-Z0-9]{1,15})\)", x["titolo"]))
               and 0 <= r["g_ent"] - x["ms"] / 86_400_000 <= c51.FINESTRA]
        righe.append({"data": r["data"], "simbolo": r["simbolo"], "tipo": r["tipo"], "r": round(float(r["r"]), 4),
                      "giorni_prima": [round(r["g_ent"] - x["ms"] / 86_400_000, 1) for x in ann],
                      "titoli": [x["titolo"][:140] for x in ann]})
    # sigle con più parentesi nel titolo (possibile abbinamento sbagliato)
    multi = [x for x in righe if any(len(re.findall(r"\(([A-Z0-9]{1,15})\)", t)) > 1 for t in x["titoli"])]
    # tipi diversi per lo stesso evento (es. Launchpool e HODLer): il codice prende il primo dell'elenco
    tipi_misti = [x for x in righe if len({c51.GRATIS.search(t).group(1).lower() for t in x["titoli"]}) > 1]
    # mancati: un annuncio «gratis» (in qualunque file degli annunci) che nomina il perpetuo dell'evento, ma fuori finestra
    # o in un altro file
    tutti = _annunci_tutti()
    per_perp: dict = {}
    for x in tutti:
        m = c51.GRATIS.search(x["titolo"])
        if not m:
            continue
        for s in re.findall(r"\(([A-Z0-9]{1,15})\)", x["titolo"]):
            p = an.perpetuo(s, pan["simboli"])
            if p:
                per_perp.setdefault(p, []).append((x["ms"] / 86_400_000, x["titolo"][:140], x["file"], "Launchpad" in x["titolo"]))
    mancati = []
    for _, r in d[~d["gratis"]].iterrows():
        for ms, t, f, lp in per_perp.get(r["simbolo"], []):
            mancati.append({"data": r["data"], "simbolo": r["simbolo"], "giorni_prima": round(r["g_ent"] - ms, 1), "file": f,
                            "launchpad": lp, "titolo": t, "r": round(float(r["r"]), 4)})
    # titoli «gratis» senza sigla fra parentesi (non abbinabili)
    senza_sigla = [x["titolo"][:140] for x in tutti if c51.GRATIS.search(x["titolo"]) and "Launchpad" not in x["titolo"]
                   and not re.findall(r"\(([A-Z0-9]{1,15})\)", x["titolo"])]
    salva("etichette", {"gratis": righe, "titoli_con_piu_sigle": multi, "tipi_misti": tipi_misti, "mancati": mancati,
                        "titoli_gratis_senza_sigla": senza_sigla[:200], "n_titoli_gratis_senza_sigla": len(senza_sigla),
                        "file_annunci": sorted({x["file"] for x in tutti})})
    print("gratis:", len(righe), "con più sigle:", len(multi), "tipi misti:", len(tipi_misti))
    print("annunci «gratis» sullo stesso perpetuo per eventi etichettati «altre»:", len(mancati))
    print("titoli gratis senza sigla:", len(senza_sigla))


def copertura() -> None:
    quot = json.loads(c51.QUOTAZIONI.read_text(encoding="utf-8"))
    anni: dict = {}
    for x in quot:
        a = pd.Timestamp(x["ms"], unit="ms").year
        anni.setdefault(a, [0, 0])
        anni[a][0] += 1
        if c51.GRATIS.search(x["titolo"]) and "Launchpad" not in x["titolo"]:
            anni[a][1] += 1
    prima, ultima = min(x["ms"] for x in quot), max(x["ms"] for x in quot)
    # i buchi più lunghi fra due annunci consecutivi
    ms = sorted(x["ms"] for x in quot)
    salti = sorted(((ms[i + 1] - ms[i]) / 86_400_000, pd.Timestamp(ms[i], unit="ms").date().isoformat())
                   for i in range(len(ms) - 1))[-8:]
    out = {"annunci": len(quot), "dal": pd.Timestamp(prima, unit="ms").isoformat(), "al": pd.Timestamp(ultima, unit="ms").isoformat(),
           "per_anno_annunci_e_gratis": {str(k): v for k, v in sorted(anni.items())},
           "salti_piu_lunghi_giorni": [(round(a, 1), b) for a, b in salti]}
    salva("copertura", out)
    print(json.dumps(out, ensure_ascii=False))


def rifai32() -> None:
    """Il ciclo di `trentaduesima.esegui` senza scaricare e senza scrivere; candele con `es.ore_di` di oggi."""
    pan = sc.pannello()
    ok = np.isfinite(pan["close"])
    primo = ok.argmax(axis=0) + pan["t0"]
    V = np.nan_to_num(pan["quote_volume"])
    cand = [(s, int(primo[j])) for j, s in enumerate(pan["simboli"])
            if s != "BTCUSDT" and ok[:, j].any() and t32.DA <= primo[j] <= t32.A]
    jb = pan["simboli"].index("BTCUSDT")
    giorni = np.arange(pan["close"].shape[0]) + pan["t0"]
    fb = pd.Series(pan["funding"][:, jb], index=giorni)
    cb = t32.ore("BTCUSDT")
    righe, senza_ore, vol0 = [], [], []
    for s, g0 in cand:
        j = pan["simboli"].index(s)
        e = g0 + tr.ETA
        if V[e - 1 - pan["t0"], j] <= 0:
            vol0.append(s)
            continue
        c = t32.ore(s)
        if c.empty or e * 24 not in c.index:
            senza_ore.append((s, sc.data(e), "vuote" if c.empty else f"dal {sc.data(int(c.index.min()) // 24)}"))
            continue
        f = pd.Series(pan["funding"][:, j], index=giorni)
        con, senza = tr.operazione(c, cb, f, fb, e, True), tr.operazione(c, cb, f, fb, e, False)
        if con and senza:
            righe.append({"data": sc.data(e), "annuncio": int((e + 3) // 7), "simbolo": s, "r": con["r"], "fermata": con["fermata"],
                          "giorni": con["giorni"], "r_senza": senza["r"],
                          "nan_ingresso": bool(not np.isfinite(c.loc[e * 24, "open"]))})
    nuovo = pd.DataFrame(righe)
    nuovo.to_csv(QUI / "prova113_eventi32_rifatti.csv", index=False)
    vecchio = pd.read_csv(EVENTI32)
    m = vecchio.merge(nuovo, on=["simbolo", "data"], how="outer", suffixes=("_file", "_oggi"), indicator=True)
    solo_file = m[m["_merge"] == "left_only"][["data", "simbolo", "r_file"]]
    solo_oggi = m[m["_merge"] == "right_only"][["data", "simbolo", "r_oggi", "r_senza_oggi"]]
    tutti = m[m["_merge"] == "both"].copy()
    tutti["dr"] = tutti["r_oggi"] - tutti["r_file"]
    tutti["drs"] = tutti["r_senza_oggi"] - tutti["r_senza_file"]
    diversi = tutti[(tutti["dr"].abs() > 1e-9) | (tutti["drs"].abs() > 1e-9)]
    out = {"candidati": len(cand), "volume_zero_prima": vol0, "senza_ore_oggi": senza_ore, "eventi_oggi": len(nuovo),
           "eventi_file": len(vecchio), "solo_nel_file": solo_file.to_dict("records"), "solo_oggi": solo_oggi.to_dict("records"),
           "comuni": len(tutti), "comuni_diversi": len(diversi),
           "diversi": diversi[["data", "simbolo", "r_file", "r_oggi", "r_senza_file", "r_senza_oggi", "fermata_file", "fermata_oggi"]]
           .sort_values("data").to_dict("records"),
           "nan_ingresso": nuovo.loc[nuovo["nan_ingresso"], ["data", "simbolo"]].to_dict("records") if len(nuovo) else []}
    salva("rifai32", out)
    print(f"candidati {len(cand)}, eventi oggi {len(nuovo)}, nel file {len(vecchio)}; solo nel file {len(solo_file)}, "
          f"solo oggi {len(solo_oggi)}, comuni diversi {len(diversi)}; senza ore oggi {len(senza_ore)}; volume zero {len(vol0)}")


def riuso() -> None:
    """Per ogni evento: pause (giorni senza candela o a volume zero, almeno 7 di fila) fra la prima candela e la fine della tenuta,
    e dopo (il simbolo è stato riaperto: la moneta nuova non è fra gli eventi)."""
    pan = sc.pannello()
    ev = pd.read_csv(EVENTI32)
    t0 = pan["t0"]
    C, V = pan["close"], pan["quote_volume"]
    righe = []
    for _, r in ev.iterrows():
        j = pan["simboli"].index(r["simbolo"])
        ok = np.isfinite(C[:, j])
        primo = int(ok.argmax())
        e = sc.giorno(*map(int, r["data"].split("-"))) - t0
        fine = e + tr.GIORNI + 1
        v = np.nan_to_num(V[:, j])
        vuoto = ~(v > 0)
        pause, corsa, inizio = [], 0, None
        ultimo = int(np.flatnonzero(ok)[-1])
        for k in range(primo, ultimo + 1):
            if vuoto[k]:
                if corsa == 0:
                    inizio = k
                corsa += 1
            else:
                if corsa >= 7:
                    pause.append((sc.data(inizio + t0), corsa))
                corsa = 0
        nella_tenuta = [p for p in pause if sc.giorno(*map(int, p[0].split("-"))) - t0 < fine]
        if pause:
            righe.append({"simbolo": r["simbolo"], "data": r["data"], "prima_candela": sc.data(primo + t0),
                          "pause": pause, "pausa_prima_della_fine_tenuta": bool(nella_tenuta),
                          "ultima_candela": sc.data(ultimo + t0)})
    salva("riuso", {"eventi_con_pause": righe, "n": len(righe),
                    "n_pausa_entro_la_tenuta": sum(1 for x in righe if x["pausa_prima_della_fine_tenuta"])})
    print("eventi con pause di almeno 7 giorni:", len(righe), "di cui entro la tenuta:",
          sum(1 for x in righe if x["pausa_prima_della_fine_tenuta"]))
    for x in righe[:40]:
        print(" ", x["simbolo"], x["data"], "prima", x["prima_candela"], "pause", x["pause"][:3], "ultima", x["ultima_candela"])




def funding() -> None:
    """Per ogni evento del file: giorni della tenuta (dal giorno d'entrata al giorno d'uscita, come `trentesima.operazione`) senza
    dato vero di funding (il pannello mette 0 o la media dei 90 giorni prima), e quanto pesa il giorno d'uscita contato per intero
    quando l'uscita è alle 00:00 (uscita dopo 30 giorni)."""
    pan = sc.pannello()
    ev = pd.read_csv(EVENTI32)
    t0, jb = pan["t0"], pan["simboli"].index("BTCUSDT")
    F = pan["funding"]
    vero_btc = sc.funding_giorni("BTCUSDT")
    righe = []
    for _, r in ev.iterrows():
        j = pan["simboli"].index(r["simbolo"])
        e = sc.giorno(*map(int, r["data"].split("-")))
        gu = int((e * 24 + round(r["giorni"] * 24)) // 24)
        vero = sc.funding_giorni(r["simbolo"])
        giorni = range(e, gu + 1)
        manca = [g for g in giorni if g not in vero.index]
        manca_b = [g for g in giorni if g not in vero_btc.index]
        stimati = [g for g in manca if abs(F[g - t0, j]) > 0]
        diff = float(sum(F[g - t0, j] - vero.get(g, 0.0) for g in giorni))
        uscita_00 = (not r["fermata"]) and abs(r["giorni"] - round(r["giorni"])) < 1e-9
        extra = float(F[gu - t0, j] - F[gu - t0, jb]) if uscita_00 else 0.0
        righe.append({"data": r["data"], "simbolo": r["simbolo"], "giorni_tenuta": len(giorni), "senza_dato_vero": len(manca),
                      "stimati": len(stimati), "btc_senza_dato": len(manca_b), "differenza_somma": diff, "giorno_uscita_in_piu": extra})
    d = pd.DataFrame(righe)
    d.to_csv(QUI / "prova113_funding.csv", index=False)
    out = {"eventi_con_giorni_senza_dato_vero": int((d["senza_dato_vero"] > 0).sum()),
           "giorni_senza_dato_vero": int(d["senza_dato_vero"].sum()), "giorni_stimati": int(d["stimati"].sum()),
           "eventi_con_giorni_stimati": d.loc[d["stimati"] > 0, ["data", "simbolo", "stimati", "differenza_somma"]].to_dict("records"),
           "btc_giorni_senza_dato": int(d["btc_senza_dato"].sum()),
           "giorno_uscita_in_piu_media": float(d["giorno_uscita_in_piu"].mean()),
           "giorno_uscita_in_piu_eventi": int((d["giorno_uscita_in_piu"] != 0).sum()),
           "primi_giorni_senza_dato": d.loc[d["senza_dato_vero"] > 0, ["data", "simbolo", "senza_dato_vero", "stimati"]]
           .head(40).to_dict("records")}
    salva("funding", out)
    print({k: v for k, v in out.items() if not isinstance(v, list)})
    print("eventi con giorni stimati:", len(out["eventi_con_giorni_stimati"]))


def corretta() -> None:
    """L'esame della 113 (stesso codice, stesso seme) su tre insiemi di eventi:
    (a) il file della prova 32 così com'è; (b) il file più i 19 eventi persi per la lettura oraria sbagliata (le altre righe come
    nel file); (c) gli eventi rifatti con i dati di oggi (19 eventi in più, tenute di settembre 2026 complete, funding vero di
    ottobre). Per capire: finestra dell'annuncio a ±10% e ±20%, senza le 5 gratis migliori, per anno."""
    pan = sc.pannello()
    file = pd.read_csv(EVENTI32)
    oggi = pd.read_csv(QUI / "prova113_rifai32_tutti.csv")
    chiave = ["simbolo", "data"]
    nuovi = oggi.merge(file[chiave], on=chiave, how="left", indicator=True)
    nuovi = nuovi[nuovi["_merge"] == "left_only"].drop(columns="_merge")
    b = pd.concat([file, nuovi[file.columns]], ignore_index=True)
    insiemi = {"a_file": file, "b_file_piu_19": b, "c_rifatti_oggi": oggi[file.columns]}
    out = {}
    for nome, ev in insiemi.items():
        r, d = esame113(ev, pan["simboli"])
        g = d[d["gratis"]]
        senza5 = d.drop(g["r"].sort_values(ascending=False).index[:5])
        r["differenza_senza_5_gratis_migliori"] = float(c51.differenza(senza5))
        per_trim = []
        for q, x in d.groupby("trimestre"):
            if 0 < x["gratis"].sum() < len(x):
                per_trim.append((q, int(x["gratis"].sum()), int((~x["gratis"]).sum()),
                                 round(float(x.loc[x["gratis"], "r"].mean() - x.loc[~x["gratis"], "r"].mean()), 4)))
        r["per_trimestre"] = per_trim
        r["trimestri_positivi"] = sum(1 for x in per_trim if x[3] > 0)
        out[nome] = r
    # sensibilità della finestra dell'annuncio (60 giorni) sugli eventi rifatti oggi
    sens = {}
    for fin in (48, 54, 66, 72):
        vecchia = c51.FINESTRA
        c51.FINESTRA = fin
        try:
            r, _ = esame113(oggi[file.columns], pan["simboli"])
        finally:
            c51.FINESTRA = vecchia
        sens[fin] = {k: r[k] for k in ("gratis", "differenza", "p_differenza", "media_gratis", "media_altre", "gratis_da_sole_p")}
    out["finestra"] = sens
    salva("corretta", out)
    for nome, r in out.items():
        if nome == "finestra":
            continue
        print(f"{nome}: eventi {r['eventi']}, gratis {r['gratis']} ({100 * r['media_gratis']:+.2f}%), altre {r['altre']} "
              f"({100 * r['media_altre']:+.2f}%), differenza {100 * r['differenza']:+.2f} p {r['p_differenza']:.4f}; "
              f"gratis da sole p {r['gratis_da_sole_p']:.4f}, metà {100 * r['gratis_prima_meta']:+.1f}/{100 * r['gratis_seconda_meta']:+.1f}, "
              f"senza 5 {100 * r['gratis_senza_5']:+.1f}; differenza senza le 5 gratis migliori {100 * r['differenza_senza_5_gratis_migliori']:+.2f}; "
              f"trimestri {r['trimestri']} (positivi {r['trimestri_positivi']}); passa {r['passa_regole']}")
    for fin, r in sens.items():
        print(f"finestra {fin}: gratis {r['gratis']}, differenza {100 * r['differenza']:+.2f}, p {r['p_differenza']:.4f}")


def dettagli() -> None:
    """Per capire (non cambia l'esame scritto): ore mancanti, perdite oltre il 100% senza l'uscita, concentrazione, clima di mercato,
    mescolamento dentro il mese invece che dentro il trimestre, annunci del giorno d'entrata (sguardo nel futuro, non ammesso)."""
    pan = sc.pannello()
    oggi = pd.read_csv(QUI / "prova113_rifai32_tutti.csv")
    cols = ["data", "annuncio", "simbolo", "r", "fermata", "giorni", "r_senza"]
    r0, d = esame113(oggi[cols], pan["simboli"])
    d = d.merge(oggi[["data", "simbolo", "ore_mancanti"]], on=["data", "simbolo"])
    out = {"ore_mancanti": d.loc[d["ore_mancanti"] > 0, ["data", "simbolo", "gratis", "ore_mancanti", "fermata", "r"]].to_dict("records")}
    # senza l'uscita: con leva 1 la vendita allo scoperto si chiude per liquidazione prima di perdere il 100%
    cap = d.copy()
    cap["r_senza"] = cap["r_senza"].clip(lower=-1.0)
    out["senza_uscita_sotto_meno_100"] = {"gratis": int(((d["r_senza"] < -1) & d["gratis"]).sum()),
                                          "altre": int(((d["r_senza"] < -1) & ~d["gratis"]).sum())}
    out["senza_uscita_differenza"] = {"come_nel_file": float(c51.differenza(d, "r_senza")),
                                      "perdita_fermata_a_meno_100": float(c51.differenza(cap, "r_senza")),
                                      "media_gratis_cap": float(cap.loc[cap["gratis"], "r_senza"].mean()),
                                      "media_altre_cap": float(cap.loc[~cap["gratis"], "r_senza"].mean())}
    g = d.loc[d["gratis"], "r"]
    out["concentrazione"] = {"quota_5_migliori_gratis": float(g.sort_values(ascending=False).iloc[:5].sum() / g.sum()),
                             "r_min": float(d["r"].min()), "r_max": float(d["r"].max())}
    # clima di mercato: rendimento del Bitcoin nei 90 giorni prima dell'entrata (rialzo > +10%, ribasso < -10%, laterale)
    jb = pan["simboli"].index("BTCUSDT")
    C = pan["close"][:, jb]
    def clima(x):
        e = sc.giorno(*map(int, x.split("-"))) - pan["t0"]
        v = C[e - 1] / C[e - 91] - 1
        return "rialzo" if v > 0.10 else "ribasso" if v < -0.10 else "laterale"
    d["clima"] = d["data"].map(clima)
    out["clima"] = {k: {"gratis": [int(x["gratis"].sum()), float(x.loc[x["gratis"], "r"].mean()) if x["gratis"].any() else None],
                        "altre": [int((~x["gratis"]).sum()), float(x.loc[~x["gratis"], "r"].mean())]}
                    for k, x in d.groupby("clima")}
    # mescolamento dentro il mese (strati più fini; la regola usa il trimestre)
    dm = d.copy()
    dm["trimestre"] = dm["data"].str[:7]
    obs = c51.differenza(dm)
    perm = c51.mescola(dm)
    out["dentro_il_mese"] = {"differenza": float(obs), "p": float((np.sum(perm >= obs) + 1) / (len(perm) + 1)),
                             "mesi_con_tutti_e_due": int(sum(1 for _, q in dm.groupby("trimestre") if 0 < q["gratis"].sum() < len(q))),
                             "gratis_nei_mesi_confrontabili": int(sum(q["gratis"].sum() for _, q in dm.groupby("trimestre")
                                                                      if 0 < q["gratis"].sum() < len(q)))}
    # dentro la settimana d'entrata (il gruppo del bootstrap)
    dw = d.copy()
    dw["trimestre"] = dw["annuncio"].astype(str)
    obs = c51.differenza(dw)
    perm = c51.mescola(dw)
    out["dentro_la_settimana"] = {"differenza": float(obs), "p": float((np.sum(perm >= obs) + 1) / (len(perm) + 1)),
                                  "gratis_nelle_settimane_confrontabili": int(sum(q["gratis"].sum() for _, q in dw.groupby("trimestre")
                                                                                  if 0 < q["gratis"].sum() < len(q)))}
    # annunci pubblicati il giorno d'entrata dopo le 00:00 (sguardo nel futuro: solo per dire quanto pesa, non ammesso)
    gg = c51.gratis(pan["simboli"])
    dd = oggi[cols].copy()
    dd["g_ent"] = dd["data"].map(lambda x: sc.giorno(*map(int, x.split("-"))))
    extra = [(s, x) for s, x in zip(dd["simbolo"], dd["data"]) if any(-1 < ge - m < 0 for m, _ in gg.get(s, [])
                                                                      for ge in [sc.giorno(*map(int, x.split("-")))])]
    out["annunci_nel_giorno_d_entrata_dopo_le_00"] = extra
    salva("dettagli", out)
    print(json.dumps({k: v for k, v in out.items()}, ensure_ascii=False, default=str)[:3000])


# ---------------------------------------------------------------------------------------------------------------------------
# Parte aggiunta: le candele orarie che mancano in questa copia, scaricate dall'archivio pubblico di Binance in una cartella
# temporanea fuori dal repository (argomento: la cartella). Non si scrive in `research/data/`.
# ---------------------------------------------------------------------------------------------------------------------------

def _lettore(cartella: Path, fino_a_ora: int | None = None):
    """`quarta.ore` che legge sia `research/data/p6h` sia la cartella scaricata; con ``fino_a_ora`` taglia le ore da lì in poi
    (per rifare la prova com'era il 21 ottobre, quando il file mensile di ottobre 2026 non esisteva)."""
    from research.programma5.strumenti import motore5 as m5
    from research.programma6 import quarta as qa

    def ore(simbolo: str) -> pd.DataFrame:
        file = sorted((qa.DATI / simbolo / "ore").glob("*.zip"))
        nomi = {p.name for p in file}
        file += sorted(p for p in (cartella / simbolo / "ore").glob("*.zip") if p.name not in nomi and p.stat().st_size > 1000)
        if not file:
            return pd.DataFrame()
        df = pd.concat([m5._csv_da_zip(p, m5.KLINE) for p in file], ignore_index=True)
        df["ora"] = m5._ms(df["open_time"]) // 3_600_000
        df = df.drop_duplicates("ora", keep="last").set_index("ora").sort_index()
        df = df[["open", "high", "low", "close"]].astype(float)
        if fino_a_ora is not None:
            df = df[df.index < fino_a_ora]
        return df.reindex(np.arange(df.index.min(), df.index.max() + 1))
    return ore


def scarica(cartella: str) -> None:
    import subprocess
    from concurrent.futures import ThreadPoolExecutor
    from research.programma6 import quarta as qa
    cart = Path(cartella)
    pan = sc.pannello()
    ok = np.isfinite(pan["close"])
    primo = ok.argmax(axis=0) + pan["t0"]
    cand = [(s, int(primo[j])) for j, s in enumerate(pan["simboli"])
            if s != "BTCUSDT" and ok[:, j].any() and t32.DA <= primo[j] <= t32.A]
    lavori = []
    for s, g0 in cand + [("BTCUSDT", t32.DA - tr.ETA)]:
        mesi = t32._mesi(g0 + tr.ETA) if s != "BTCUSDT" else sorted({sc.data(g)[:7] for g in range(t32.DA, t32.A + 45)})
        for m in mesi:
            nome = f"{s}-1h-{m}.zip"
            if (qa.DATI / s / "ore" / nome).exists() or (cart / s / "ore" / nome).exists():
                continue
            lavori.append((s, m, nome))

    def uno(x):
        s, m, nome = x
        d = cart / s / "ore"
        d.mkdir(parents=True, exist_ok=True)
        url = f"https://data.binance.vision/data/futures/um/monthly/klines/{s}/1h/{nome}"
        r = subprocess.run(["curl", "-sS", "-o", str(d / nome), "-w", "%{http_code}", url], capture_output=True, text=True, timeout=120)
        if r.stdout.strip() != "200":
            (d / nome).unlink(missing_ok=True)
        return r.stdout.strip()
    with ThreadPoolExecutor(max_workers=16) as ex:
        codici = list(ex.map(uno, lavori))
    print("file da scaricare", len(lavori), "esiti", {c: codici.count(c) for c in set(codici)})


def rifai32_tutti(cartella: str, fino_a_ora: int | None = None, chiave: str = "rifai32_tutti") -> pd.DataFrame:
    from research.programma6 import quarta as qa
    vecchio_ore = qa.ore
    qa.ore = _lettore(Path(cartella), fino_a_ora)
    try:
        pan = sc.pannello()
        ok = np.isfinite(pan["close"])
        primo = ok.argmax(axis=0) + pan["t0"]
        V = np.nan_to_num(pan["quote_volume"])
        cand = [(s, int(primo[j])) for j, s in enumerate(pan["simboli"])
                if s != "BTCUSDT" and ok[:, j].any() and t32.DA <= primo[j] <= t32.A]
        jb = pan["simboli"].index("BTCUSDT")
        giorni = np.arange(pan["close"].shape[0]) + pan["t0"]
        fb = pd.Series(pan["funding"][:, jb], index=giorni)
        cb = t32.ore("BTCUSDT")
        righe, senza = [], []
        for s, g0 in cand:
            j = pan["simboli"].index(s)
            e = g0 + tr.ETA
            if V[e - 1 - pan["t0"], j] <= 0:
                continue
            c = t32.ore(s)
            if c.empty or e * 24 not in c.index:
                senza.append(s)
                continue
            f = pd.Series(pan["funding"][:, j], index=giorni)
            con, sz = tr.operazione(c, cb, f, fb, e, True), tr.operazione(c, cb, f, fb, e, False)
            if con and sz:
                tratto = c[(c.index >= e * 24) & (c.index < (e + tr.GIORNI) * 24)]
                h_stop = int(e * 24 + con["giorni"] * 24) if con["fermata"] else None
                p0 = float(c.loc[e * 24, "open"])
                righe.append({"data": sc.data(e), "annuncio": int((e + 3) // 7), "simbolo": s, "r": con["r"],
                              "fermata": con["fermata"], "giorni": con["giorni"], "r_senza": sz["r"],
                              "ore_mancanti": int(tratto["open"].isna().sum()),
                              "apertura_ora_stop_su_p0": float(c.loc[h_stop, "open"] / p0) if h_stop is not None else np.nan})
        df = pd.DataFrame(righe)
    finally:
        qa.ore = vecchio_ore
    df.to_csv(QUI / f"prova113_{chiave}.csv", index=False)
    vecchio = pd.read_csv(EVENTI32)
    m = vecchio.merge(df, on=["simbolo", "data"], how="outer", suffixes=("_file", "_oggi"), indicator=True)
    comuni = m[m["_merge"] == "both"].copy()
    comuni["dr"] = comuni["r_oggi"] - comuni["r_file"]
    comuni["drs"] = comuni["r_senza_oggi"] - comuni["r_senza_file"]
    div = comuni[(comuni["dr"].abs() > 1e-9) | (comuni["drs"].abs() > 1e-9)]
    out = {"eventi": len(df), "senza_ore": senza, "solo_nel_file": m.loc[m["_merge"] == "left_only", ["data", "simbolo"]].to_dict("records"),
           "solo_oggi": m.loc[m["_merge"] == "right_only", ["data", "simbolo", "r_oggi"]].to_dict("records"),
           "comuni": len(comuni), "comuni_diversi": len(div),
           "diversi": div[["data", "simbolo", "r_file", "r_oggi", "r_senza_file", "r_senza_oggi", "giorni_file", "giorni_oggi"]]
           .to_dict("records"),
           "eventi_con_ore_mancanti": int((df["ore_mancanti"] > 0).sum()), "ore_mancanti_totali": int(df["ore_mancanti"].sum()),
           "stop_con_apertura_oltre_1_31": df.loc[df["apertura_ora_stop_su_p0"] > 1.31, ["data", "simbolo", "apertura_ora_stop_su_p0"]]
           .to_dict("records")}
    salva(chiave, out)
    print(f"{chiave}: eventi {len(df)}; solo nel file {len(out['solo_nel_file'])}; solo oggi {len(out['solo_oggi'])}; "
          f"comuni {len(comuni)}, diversi {len(div)}; eventi con ore mancanti {out['eventi_con_ore_mancanti']}; "
          f"stop con apertura oltre +31% {len(out['stop_con_apertura_oltre_1_31'])}")
    return df


if __name__ == "__main__":
    parte = sys.argv[1]
    if parte == "scarica":
        scarica(sys.argv[2])
    elif parte == "rifai32_tutti":
        rifai32_tutti(sys.argv[2])
    elif parte == "stop":                       # sensibilità della soglia d'uscita (+30% ± 10% e ± 20%), per capire
        pan = sc.pannello()
        ris = {}
        for s in (0.24, 0.27, 0.33, 0.36):
            tr.STOP = s
            ev = rifai32_tutti(sys.argv[2], chiave=f"stop_{int(s * 100)}")
            r, _ = esame113(ev[["data", "annuncio", "simbolo", "r", "fermata", "giorni", "r_senza"]], pan["simboli"])
            ris[s] = {k: r[k] for k in ("eventi", "gratis", "media_gratis", "media_altre", "differenza", "p_differenza",
                                        "gratis_da_sole_p")}
            print(s, ris[s], flush=True)
        tr.STOP = 0.30
        salva("stop", ris)
    elif parte == "rifai32_21ottobre":          # le ore fino al 30 settembre 2026 compreso, come il 21 ottobre
        rifai32_tutti(sys.argv[2], fino_a_ora=sc.giorno(2026, 10, 1) * 24, chiave="rifai32_21ottobre")
    else:
        {"riproduci": riproduci, "etichette": etichette, "copertura": copertura, "rifai32": rifai32, "riuso": riuso,
         "funding": funding, "corretta": corretta,
         "dettagli": dettagli}[parte]()
