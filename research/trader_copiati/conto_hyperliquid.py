"""Il conto della copia dei trader migliori di Hyperliquid (HYPERLIQUID.md, sezione 2), dalle posizioni raccolte in `hyperliquid/`.

A ogni giro della raccolta (ogni 4 ore) il portafoglio copiato è la media dei 20 conti della settimana del peso di ogni moneta (valore
della posizione con il segno diviso il valore del conto), abbinato ai perpetui di Binance e scalato a un'esposizione totale non oltre 2.
I pesi entrano all'apertura dell'ora dopo il giro e si tengono fino all'entrata del giro dopo, sui prezzi orari di Binance (file
giornalieri dell'archivio pubblico, che escono il giorno dopo), con il costo a mercato sui cambi di peso e il funding di Binance.

Dal 5 novembre 2026 anche i due gruppi dell'aggiunta di HYPERLIQUID.md: gli stessi conti con ognuno a esposizione uguale, e le
«balene» (i 20 conti piu' grandi).

Dal 27 novembre 2026 (audit del 26 novembre) anche la misura del giudice delle balene (GIUDICE_BALENE.md, regole 10-11 e nota del 27
novembre): i tre conti copiati (a) «costanti», (b) tutti i giudicabili, (c) «mercato» e «caso», con le posizioni lette sia da
`posizioni_*.jsonl.gz` (i conti scelti) sia da `liquidazioni_*.jsonl.gz` (i 600 conti della mappa); `misura_giudice` non fa niente finché
non c'è un giudizio in `giudice_balene/giudizi/`.

Uso: python3 -m research.trader_copiati.conto_hyperliquid
"""
from __future__ import annotations

import gzip
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

QUI = Path(__file__).parent
ARCHIVIO = QUI / "hyperliquid"
ESPOSIZIONE_MAX = 2.0
GIUDICE = QUI / "giudice_balene"                       # il foglio del lunedì, i giudizi (giudizi/AAAA-MM-GG.json) e la misura
G1_SETTIMANE = QUI.parent.parent / "gate2" / "exports"  # ricalcolo_g1_ricerca_AAAA-MM-GG.json del confronto settimanale (regola 11)


def simbolo_binance(moneta: str, simboli: set) -> str | None:
    if moneta.startswith("k") and moneta[1:].isupper():
        cand = (f"1000{moneta[1:]}USDT",)
    else:
        cand = (f"{moneta}USDT", f"1000{moneta}USDT")
    return next((s for s in cand if s in simboli), None)


# I gruppi (HYPERLIQUID.md): il nome, il prefisso dei file della scelta, se ogni conto va portato a esposizione 2 prima della media
# (aggiunta del 5 novembre) e da quale giro si conta
GRUPPI = {
    "migliori del mese": ("scelti_", False, ""),
    "migliori del mese, a esposizione uguale": ("scelti_", True, "2026-11-05 08:40"),
    "balene (i 20 conti più grandi)": ("scelti_balene_", False, "2026-11-05 08:40"),
}


def _scelti(prefisso: str) -> dict:
    """{data della scelta: indirizzi} per un prefisso (``scelti_`` non prende i file delle balene)."""
    out = {}
    for f in sorted(ARCHIVIO.glob(f"{prefisso}*.json")):
        resto = f.stem[len(prefisso):]
        if len(resto) == 10 and resto[4] == "-":
            out[resto] = {c["indirizzo"] for c in json.loads(f.read_text())["conti"]}
    return out


def giri(simboli: set, prefisso: str = "scelti_", uguale: bool = False, dal: str = "") -> pd.DataFrame:
    """Una riga per giro: l'ora del giro, i pesi copiati (scalati) e la leva media dei conti prima di scalare. I conti di un giro sono
    quelli dell'ultima scelta fatta fino a quel giorno; con ``uguale`` ogni conto con posizioni abbinate pesa a esposizione 2."""
    scelti = _scelti(prefisso)
    righe: dict = {}
    for f in sorted(ARCHIVIO.glob("posizioni_*.jsonl.gz")):
        for linea in gzip.open(f, "rt", encoding="utf-8"):
            r = json.loads(linea)
            righe.setdefault(r["ora"], []).append(r)
    out = []
    for ora, conti in sorted(righe.items()):
        prima_ = [k for k in scelti if k <= ora[:10]]
        if ora < dal or not prima_:
            continue
        t = datetime.strptime(ora, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        ammessi = scelti[max(prima_)]
        pesi: dict = {}
        leve = []
        n = 0
        for r in conti:
            if r["indirizzo"] not in ammessi or not r.get("conto"):
                continue
            n += 1
            lordo = 0.0
            del_conto: dict = {}
            for p in r["posizioni"]:
                w = (1 if p["quantita"] > 0 else -1) * float(p["valore"]) / float(r["conto"])
                lordo += abs(w)
                s = simbolo_binance(p["moneta"], simboli)
                if s:
                    del_conto[s] = del_conto.get(s, 0.0) + w
            if uguale:
                g = sum(abs(w) for w in del_conto.values())
                del_conto = {s: w * ESPOSIZIONE_MAX / g for s, w in del_conto.items()} if g > 1e-12 else {}
            for s, w in del_conto.items():
                pesi[s] = pesi.get(s, 0.0) + w
            leve.append(lordo)
        if not n:
            continue
        pesi = {s: w / n for s, w in pesi.items() if abs(w) > 1e-12}
        g = sum(abs(w) for w in pesi.values())
        if g > ESPOSIZIONE_MAX:
            pesi = {s: w * ESPOSIZIONE_MAX / g for s, w in pesi.items()}
        out.append({"ora": t, "entrata": int(t.timestamp() // 3600) + 1, "pesi": pesi, "conti": n,
                    "leva_media_conti": float(np.mean(leve)) if leve else 0.0, "esposizione": min(g, ESPOSIZIONE_MAX)})
    return pd.DataFrame(out)


def scarica_giorni(simbolo: str, dal: datetime, al: datetime) -> None:
    from research.programma6 import quarta as qa
    from research.programma6 import scarico_giorni as sg
    g = dal
    while g <= al:
        d = g.strftime("%Y-%m-%d")
        try:
            sg._scarica(f"data/futures/um/daily/klines/{simbolo}/1h/{simbolo}-1h-{d}.zip", qa.DATI / simbolo / "ore")
        except Exception:  # noqa: BLE001
            pass
        g += timedelta(days=1)


def tratti(gg: pd.DataFrame, ore: dict, costo: dict, F: np.ndarray, t0: int, jj: dict, data) -> list:
    """Il conto giro per giro (pesi tenuti dall'entrata di un giro all'entrata del dopo), fin dove ci sono i prezzi."""
    righe, prima = [], {}
    for k in range(len(gg) - 1):
        h1, h2, pesi = int(gg["entrata"].iloc[k]), int(gg["entrata"].iloc[k + 1]), gg["pesi"].iloc[k]
        lordo, manca = 0.0, False
        for s, w in pesi.items():
            o = ore[s]
            if h1 not in o.index or h2 not in o.index or not np.isfinite(o.loc[[h1, h2], "open"]).all():
                manca = True
                break
            lordo += w * (o.loc[h2, "open"] / o.loc[h1, "open"] - 1)
        if manca:
            break                                   # i prezzi di questo tratto non sono ancora nell'archivio
        spese = sum(abs(pesi.get(s, 0.0) - prima.get(s, 0.0)) * costo.get(s, 0.001) for s in set(pesi) | set(prima))
        fund = 0.0
        for s, w in pesi.items():
            for h in range(h1, h2):
                d = h // 24 - t0
                if 0 <= d < F.shape[0] and np.isfinite(F[d, jj[s]]):
                    fund += w * F[d, jj[s]] / 24
        righe.append({"dal": data(h1 // 24) + f" {h1 % 24:02d}:00", "ore": h2 - h1, "lordo": lordo, "spese": spese, "funding": fund,
                      "netto": lordo - spese - fund, "esposizione": gg["esposizione"].iloc[k],
                      "netto_lungo": float(sum(pesi.values())), "leva_media_conti": gg["leva_media_conti"].iloc[k]})
        prima = pesi
    return righe


def riassunto(gg: pd.DataFrame, righe: list) -> dict:
    d = pd.DataFrame(righe)
    out = {"giri_raccolti": int(len(gg)), "tratti_con_i_prezzi": int(len(d))}
    if len(d):
        out.update({"dal": righe[0]["dal"], "rendimento": float((1 + d["netto"]).prod() - 1), "lordo": float(d["lordo"].sum()),
                    "spese": float(d["spese"].sum()), "funding": float(d["funding"].sum()), "ore": int(d["ore"].sum()),
                    "esposizione_media": float(d["esposizione"].mean()), "netto_lungo_medio": float(d["netto_lungo"].mean()),
                    "leva_media_dei_conti": float(d["leva_media_conti"].mean())})
    return out


# ---------------------------------------------------------------------------------------------------------------------------------
# La misura del giudice delle balene (GIUDICE_BALENE.md, regole 10-11; come si conta: nota del 27 novembre 2026)
# ---------------------------------------------------------------------------------------------------------------------------------
GRUPPI_GIUDICE = {"a": ("costante",), "b": ("costante", "mercato", "caso"), "c": ("mercato", "caso")}
NOMI_GIUDICE = {"a": "(a) i «costanti»", "b": "(b) tutti i giudicabili", "c": "(c) «mercato» e «caso» (controllo)"}
CONTI_MIN_A = 5                     # regola 10: con meno di 5 «costanti» il conto (a) resta in cassa
VALIDO = timedelta(days=8)          # un giudizio vale fino a quello del lunedì dopo, al più 8 giorni dal suo lunedì (regola 9)
PANIERE = ("BTCUSDT", "ETHUSDT", "SOLUSDT")


def _ora(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)


def _lunedi(t: datetime) -> datetime:
    return (t - timedelta(days=t.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)


def posizioni_giri(archivio: Path | None = None, dal: str = "") -> dict:
    """{ora del giro: {indirizzo: (valore del conto, [(moneta, quantità, valore)])}} dai conti scelti (`posizioni_*.jsonl.gz`, tutte le
    posizioni) e dai 600 conti della mappa delle liquidazioni (`liquidazioni_*.jsonl.gz`, posizioni da 10.000 dollari in su); se un conto
    è in tutti e due nello stesso giro contano le posizioni di `posizioni_*.jsonl.gz`, come nel giudice. ``dal``: «AAAA-MM», i mesi prima
    non si leggono."""
    archivio = archivio or ARCHIVIO
    out: dict = {}
    for f in sorted(archivio.glob("posizioni_????-??.jsonl.gz")):
        if f.name[len("posizioni_"):][:7] < dal:
            continue
        for linea in gzip.open(f, "rt", encoding="utf-8"):
            if not linea.strip():
                continue
            r = json.loads(linea)
            out.setdefault(r["ora"], {})[r["indirizzo"]] = (
                float(r.get("conto") or 0), [(p["moneta"], float(p["quantita"]), float(p["valore"])) for p in r.get("posizioni") or []])
    elenchi: dict = {}
    for f in sorted(archivio.glob("liquidazioni_????-??.jsonl.gz")):
        if f.name[len("liquidazioni_"):][:7] < dal:
            continue
        for linea in gzip.open(f, "rt", encoding="utf-8"):
            if not linea.strip():
                continue
            r = json.loads(linea)
            nome = r["conti_della_settimana"]
            if nome not in elenchi:
                g = archivio / nome
                elenchi[nome] = [c["indirizzo"] for c in json.loads(g.read_text())["conti"]] if g.exists() else []
            indirizzi = elenchi[nome]
            per_conto: dict = {}
            for i, moneta, q, v, *_ in r.get("posizioni") or []:
                per_conto.setdefault(i, []).append((moneta, float(q), float(v)))
            giro = out.setdefault(r["ora"], {})
            for i, valore in enumerate(r.get("conti") or []):
                if valore is None or i >= len(indirizzi) or indirizzi[i] in giro:
                    continue
                giro[indirizzi[i]] = (float(valore), per_conto.get(i, []))
    return out


def giudizi(cartella: Path | None = None) -> list:
    """I giudizi committati (`giudice_balene/giudizi/AAAA-MM-GG.json`, formato nella nota del 27 novembre di GIUDICE_BALENE.md), in ordine
    di lunedì: il lunedì, da quando vale (``scritto_il``, ora UTC; se manca, il lunedì alle 08:00), le voci e le correzioni (ognuna conta
    dal giorno dopo la sua ora, regola 9). Il file può anche essere il solo elenco dei giudizi."""
    cartella = cartella or GIUDICE / "giudizi"
    out = []
    for f in sorted(cartella.glob("????-??-??.json")):
        x = json.loads(f.read_text())
        if isinstance(x, list):
            x = {"giudizi": x}
        lun = datetime.strptime(f.stem, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        scritto = x.get("scritto_il")
        correzioni = sorted((_ora(c["ora"]).replace(hour=0, minute=0) + timedelta(days=1), c["indirizzo"], c["voce"])
                            for c in x.get("correzioni") or [])
        out.append({"lunedi": lun, "dal": _ora(scritto) if scritto else lun + timedelta(hours=8), "ora_scritta": bool(scritto),
                    "voci": {g["indirizzo"]: g["voce"] for g in x.get("giudizi") or []}, "correzioni": correzioni})
    return out


def voci_al(giudizio: dict, t: datetime) -> dict:
    voci = dict(giudizio["voci"])
    for da, indirizzo, voce in giudizio["correzioni"]:
        if da <= t:
            voci[indirizzo] = voce
    return voci


def giudizio_del_giro(gg: list, t: datetime) -> dict | None:
    """Il giudizio che vale al giro delle ``t``: l'ultimo già scritto, se dal suo lunedì non sono passati 8 giorni (regola 9: vale fino
    al lunedì seguente; un lunedì saltato non si recupera e i tre conti restano in cassa finché non c'è un giudizio nuovo)."""
    validi = [g for g in gg if g["dal"] <= t < g["lunedi"] + VALIDO]
    return max(validi, key=lambda g: g["lunedi"]) if validi else None


def pesi_gruppo(conti_giro: dict, ammessi, simboli: set) -> tuple[dict, int, float]:
    """I pesi di un conto copiato a un giro (nota del 27 novembre): ogni conto letto con valore sopra zero e posizioni abbinate ai
    perpetui di Binance a esposizione uguale (2, come il gruppo «a esposizione uguale» di HYPERLIQUID.md), poi la media, poi il totale
    portato a esposizione 2, uguale per i tre conti copiati (regola 10). Restituisce anche quanti conti sono entrati e la loro leva media
    prima di scalare (esposizione lorda sul valore del conto)."""
    somma: dict = {}
    n, leve = 0, []
    for indirizzo in sorted(ammessi):
        x = conti_giro.get(indirizzo)
        if not x or x[0] <= 0:
            continue
        conto, posizioni = x
        n += 1
        del_conto: dict = {}
        lordo = 0.0
        for moneta, q, v in posizioni:
            w = (1 if q > 0 else -1) * abs(v) / conto
            lordo += abs(w)
            s = simbolo_binance(moneta, simboli)
            if s:
                del_conto[s] = del_conto.get(s, 0.0) + w
        leve.append(lordo)
        g = sum(abs(w) for w in del_conto.values())
        if g > 1e-12:
            for s, w in del_conto.items():
                somma[s] = somma.get(s, 0.0) + w * ESPOSIZIONE_MAX / g
    if not n:
        return {}, 0, 0.0
    pesi = {s: w / n for s, w in somma.items() if abs(w) > 1e-12}
    g = sum(abs(w) for w in pesi.values())
    pesi = {s: w * ESPOSIZIONE_MAX / g for s, w in pesi.items()} if g > 1e-12 else {}
    return pesi, n, float(np.mean(leve))


def giri_giudice(simboli: set, posizioni: dict, gg: list) -> dict:
    """Per ognuno dei tre conti copiati, una riga per giro dal primo giudizio in poi: i pesi (vuoti = in cassa, con il perché), i conti
    entrati e quelli del giudizio."""
    out: dict = {k: [] for k in GRUPPI_GIUDICE}
    for ora in sorted(posizioni):
        t = _ora(ora)
        g = giudizio_del_giro(gg, t)
        if g is None and not out["a"]:
            continue                                       # prima del primo giudizio non si conta niente
        voci = voci_al(g, t) if g else {}
        for k, ammesse in GRUPPI_GIUDICE.items():
            ammessi = {i for i, v in voci.items() if v in ammesse}
            if g is None:
                cassa = "nessun giudizio valido"
            elif k == "a" and len(ammessi) < CONTI_MIN_A:
                cassa = f"meno di {CONTI_MIN_A} «costanti»"
            elif not ammessi:
                cassa = "nessun conto nel giudizio"
            else:
                cassa = ""
            pesi, n, leva = ({}, 0, 0.0) if cassa else pesi_gruppo(posizioni[ora], ammessi, simboli)
            if not cassa and not pesi:
                cassa = "nessuna posizione abbinata"
            out[k].append({"ora": t, "entrata": int(t.timestamp() // 3600) + 1, "pesi": pesi, "conti": n,
                           "conti_del_giudizio": len(ammessi), "cassa": cassa, "lunedi": g["lunedi"].strftime("%Y-%m-%d") if g else "",
                           "leva_media_conti": leva, "esposizione": float(sum(abs(w) for w in pesi.values()))})
    return {k: pd.DataFrame(v) for k, v in out.items()}


def paniere(ore: dict, h1: int, h2: int) -> float | None:
    """Il rendimento del paniere uguale di Bitcoin, Ether e Solana (prezzi orari di Binance) dall'apertura dell'ora h1 a quella di h2."""
    rr = []
    for s in PANIERE:
        o = ore.get(s)
        if o is None or h1 not in o.index or h2 not in o.index or not np.isfinite(o.loc[[h1, h2], "open"]).all():
            return None
        rr.append(o.loc[h2, "open"] / o.loc[h1, "open"] - 1)
    return float(np.mean(rr))


def settimane_gruppo(gg: pd.DataFrame, righe: list, ore: dict) -> dict:
    """Le settimane (dal lunedì 00:00 UTC; un tratto conta nella settimana della sua entrata) di un conto copiato: netto (dopo spese e
    funding), solo comprato meno venduto (netta × paniere, senza spese), a esposizione netta zero (netto meno netta × paniere), il
    paniere, e se la settimana è completa (i prezzi arrivano fino al lunedì dopo)."""
    sett: dict = {}
    fine = None
    for k, r in enumerate(righe):
        h1, h2 = int(gg["entrata"].iloc[k]), int(gg["entrata"].iloc[k + 1])
        rp = paniere(ore, h1, h2)
        if rp is None:
            break
        fine = h2
        lun = _lunedi(datetime.fromtimestamp(h1 * 3600, tz=timezone.utc)).strftime("%Y-%m-%d")
        s = sett.setdefault(lun, {"netto": 1.0, "solo_netta": 1.0, "netta_zero": 1.0, "paniere": 1.0, "tratti": 0, "tratti_in_cassa": 0,
                                  "conti_del_giudizio": 0, "cassa": set()})
        s["netto"] *= 1 + r["netto"]
        s["solo_netta"] *= 1 + r["netto_lungo"] * rp
        s["netta_zero"] *= 1 + r["netto"] - r["netto_lungo"] * rp
        s["paniere"] *= 1 + rp
        s["tratti"] += 1
        if gg["cassa"].iloc[k]:
            s["tratti_in_cassa"] += 1
            s["cassa"].add(gg["cassa"].iloc[k])
        s["conti_del_giudizio"] = max(s["conti_del_giudizio"], int(gg["conti_del_giudizio"].iloc[k]))
    out = {}
    for lun, s in sorted(sett.items()):
        fine_sett = int((datetime.strptime(lun, "%Y-%m-%d").replace(tzinfo=timezone.utc) + timedelta(days=7)).timestamp() // 3600)
        out[lun] = {"netto": s["netto"] - 1, "solo_netta": s["solo_netta"] - 1, "netta_zero": s["netta_zero"] - 1,
                    "paniere": s["paniere"] - 1, "tratti": s["tratti"], "tratti_in_cassa": s["tratti_in_cassa"],
                    "in_cassa": s["tratti_in_cassa"] == s["tratti"], "perche_in_cassa": sorted(s["cassa"]),
                    "conti_del_giudizio": s["conti_del_giudizio"], "completa": fine is not None and fine >= fine_sett}
    return out


def g1_settimane(cartella: Path | None = None) -> dict:
    """G1 nelle stesse settimane (regola 11), dall'ultimo ricalcolo del confronto settimanale (`gate2/exports/ricalcolo_g1_ricerca_
    AAAA-MM-GG.json`): netto del giorno = lordo − spese a mercato − funding, la settimana (dal lunedì) solo con tutti e 7 i giorni."""
    cartella = cartella or G1_SETTIMANE
    ff = sorted(cartella.glob("ricalcolo_g1_ricerca_????-??-??.json"))
    if not ff:
        return {}
    per: dict = {}
    for d, v in json.loads(ff[-1].read_text()).items():
        lun = _lunedi(datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=timezone.utc)).strftime("%Y-%m-%d")
        per.setdefault(lun, []).append(float(v["lordo"]) - float(v["sp_mercato"]) - float(v["funding"]))
    return {lun: float(np.prod([1 + r for r in rr]) - 1) for lun, rr in per.items() if len(rr) == 7}


def _statistiche(xx: list) -> dict:
    x = np.array(xx, dtype=float)
    if not len(x):
        return {"settimane": 0}
    sd = float(x.std(ddof=1)) if len(x) > 1 else None
    return {"settimane": int(len(x)), "media": float(x.mean()), "dev_std": sd,
            "t": float(x.mean() / (sd / np.sqrt(len(x)))) if sd else None}


def rapporto_giudice(risultati: dict, g1: dict, gg: list) -> str:
    pc = lambda v: "—" if v is None else f"{100 * v:+.2f}%"  # noqa: E731
    righe = ["# Il giudice delle balene: la misura in avanti (regole 10-11)", "",
             "Regole: `GIUDICE_BALENE.md` (regole 10-13 e nota del 27 novembre 2026). **Nessuno giudica questi numeri prima di 8 settimane "
             "di giudizi** (regola 12: il 25 gennaio 2027). Ogni conto copiato prende i conti del giudizio in vigore al giro (scritto prima "
             "del giro, al più 8 giorni dal suo lunedì): pesi dalle posizioni al giro (conti scelti e mappa delle liquidazioni), ogni conto a "
             "esposizione uguale, il totale a esposizione 2 per tutti e tre; prezzi orari, spese (0,05% più lo scarto 0,01% su Bitcoin, Ether "
             "e Solana, 0,02% sulle altre) e funding di Binance. «Solo netta» = comprato meno venduto × paniere (Bitcoin, Ether e Solana in "
             "parti uguali, senza spese); «netta zero» = netto meno solo netta (la parte propria). G1: ultimo ricalcolo del confronto "
             "settimanale (`gate2/exports/ricalcolo_g1_ricerca_*.json`), stesse spese.", ""]
    senza_ora = [g["lunedi"].strftime("%Y-%m-%d") for g in gg if not g["ora_scritta"]]
    if senza_ora:
        righe += [f"Giudizi senza `scritto_il` (contano dal lunedì alle 08:00 UTC): {', '.join(senza_ora)}.", ""]
    settimane = sorted({s for r in risultati.values() for s in r["settimane"]})
    righe += ["| settimana dal | conti (a) / (b) / (c) | (a) | (b) | (c) | (a) − (b) | (a) netta zero | (b) netta zero | "
              "(c) netta zero | (a) solo netta | paniere | G1 | note |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for s in settimane:
        x = {k: risultati[k]["settimane"].get(s) for k in GRUPPI_GIUDICE}
        v = lambda k, c: x[k][c] if x[k] else None  # noqa: E731
        note = [f"({k}) in cassa: " + ", ".join(x[k]["perche_in_cassa"]) for k in GRUPPI_GIUDICE if x[k] and x[k]["in_cassa"]]
        if any(x[k] and not x[k]["completa"] for k in GRUPPI_GIUDICE):
            note.append("in corso")
        ab = v("a", "netto") - v("b", "netto") if x["a"] and x["b"] else None
        conti = " / ".join(str(x[k]["conti_del_giudizio"]) if x[k] else "—" for k in GRUPPI_GIUDICE)
        righe.append(f"| {s} | {conti} | {pc(v('a', 'netto'))} | {pc(v('b', 'netto'))} | {pc(v('c', 'netto'))} | {pc(ab)} | "
                     f"{pc(v('a', 'netta_zero'))} | {pc(v('b', 'netta_zero'))} | {pc(v('c', 'netta_zero'))} | {pc(v('a', 'solo_netta'))} | "
                     f"{pc(v('b', 'paniere'))} | {pc(g1.get(s))} | {'; '.join(note)} |")
    righe += ["", "Le settimane complete, una riga per conto copiato (media, deviazione standard e t delle settimane; correlazione "
              "settimanale con il paniere):"]
    for k, nome in NOMI_GIUDICE.items():
        st = risultati[k]["riassunto"]
        netto, corr = st["netto"], st.get("correlazione_paniere")
        riga = f"* **{nome}**: {netto['settimane']} " + ("settimana completa" if netto["settimane"] == 1 else "settimane complete")
        if netto["settimane"]:
            t = "—" if netto["t"] is None else f"{netto['t']:.2f}"
            c = "—" if corr is None else f"{corr:+.2f}"
            riga += (f", media {pc(netto['media'])} (dev. std {pc(netto['dev_std'])}, t {t}); a netta zero "
                     f"{pc(st['netta_zero'].get('media'))}; correlazione con il paniere {c}")
        righe.append(riga + ".")
    return "\n".join(righe) + "\n"


def misura_giudice(log=print, uscita: Path | None = None, pan: dict | None = None, ore: dict | None = None,
                   cartella_giudizi: Path | None = None, archivio: Path | None = None) -> dict:
    """La misura delle regole 10-11 di GIUDICE_BALENE.md: i tre conti copiati settimana per settimana, con il paniere e G1 accanto.
    Scrive `giudice_balene/misura.json` e `giudice_balene/MISURA.md`; senza giudizi non fa niente e non scrive niente."""
    gg = giudizi(cartella_giudizi)
    if not gg:
        return {}
    from research.programma6 import esecuzione as es
    from research.programma6 import seconda as sc
    pan = sc.pannello() if pan is None else pan
    simboli = set(pan["simboli"])
    primo = min(g["dal"] for g in gg)
    serie = giri_giudice(simboli, posizioni_giri(archivio, (primo - timedelta(days=1)).strftime("%Y-%m")), gg)
    if serie["a"].empty:
        log("[giudice] misura: nessun giro dopo il primo giudizio")
        return {}
    ore = dict(ore or {})
    usati = sorted({s for d in serie.values() for p in d["pesi"] for s in p} | set(PANIERE))
    al = datetime.now(timezone.utc) - timedelta(days=1)
    for s in usati:
        if s not in ore:
            scarica_giorni(s, serie["a"]["ora"].min().to_pydatetime(), al)
            ore[s] = es.ore_di(s)
    costo = dict(zip(pan["simboli"], sc.costi_moneta(pan["simboli"])))
    jj = {s: i for i, s in enumerate(pan["simboli"])}
    try:
        g1 = g1_settimane()
    except Exception:  # noqa: BLE001
        g1 = {}
    risultati = {}
    for k, d in serie.items():
        righe = tratti(d, ore, costo, pan["funding"], pan["t0"], jj, sc.data) if len(d) > 1 else []
        sett = settimane_gruppo(d, righe, ore)
        complete = [x for x in sett.values() if x["completa"]]
        pan_c = [x["paniere"] for x in complete]
        net_c = [x["netto"] for x in complete]
        corr = float(np.corrcoef(net_c, pan_c)[0, 1]) if len(complete) >= 3 and np.std(net_c) > 0 and np.std(pan_c) > 0 else None
        risultati[k] = {"nome": NOMI_GIUDICE[k], "settimane": sett, "tratti": righe,
                        "riassunto": {"netto": _statistiche(net_c), "netta_zero": _statistiche([x["netta_zero"] for x in complete]),
                                      "solo_netta": _statistiche([x["solo_netta"] for x in complete]), "correlazione_paniere": corr}}
    uscita = GIUDICE if uscita is None else uscita
    uscita.mkdir(parents=True, exist_ok=True)
    (uscita / "misura.json").write_text(json.dumps({"giudizi": [g["lunedi"].strftime("%Y-%m-%d") for g in gg], "g1": g1,
                                                     "gruppi": risultati}, ensure_ascii=False, indent=1, default=str))
    testo = rapporto_giudice(risultati, g1, gg)
    (uscita / "MISURA.md").write_text(testo, encoding="utf-8")
    log(f"[giudice] misura: {len(serie['a'])} giri dal primo giudizio, settimane {', '.join(sorted(risultati['b']['settimane'])) or '—'}")
    return risultati


def esegui(log=print) -> dict:
    from research.programma6 import esecuzione as es
    from research.programma6 import seconda as sc
    pan = sc.pannello()
    simboli = set(pan["simboli"])
    tutti = {nome: giri(simboli, pref, uguale, dal) for nome, (pref, uguale, dal) in GRUPPI.items()}
    tutti = {k: v for k, v in tutti.items() if not v.empty}
    if not tutti:
        log("[copia] nessun giro raccolto")
        return {}
    usati = sorted({s for gg in tutti.values() for p in gg["pesi"] for s in p})
    dal, al = min(gg["ora"].min() for gg in tutti.values()), datetime.now(timezone.utc) - timedelta(days=1)
    for s in usati:
        scarica_giorni(s, dal, al)
    ore = {s: es.ore_di(s) for s in usati}
    costo = dict(zip(pan["simboli"], sc.costi_moneta(pan["simboli"])))
    jj = {s: i for i, s in enumerate(pan["simboli"])}
    risultati = {}
    for nome, gg in tutti.items():
        righe = tratti(gg, ore, costo, pan["funding"], pan["t0"], jj, sc.data)
        risultati[nome] = {**riassunto(gg, righe), "tratti": righe}
    principale = risultati.get("migliori del mese", {})
    out = {k: v for k, v in principale.items() if k != "tratti"}
    (QUI / "hyperliquid_conto.json").write_text(json.dumps({**principale, "gruppi": risultati}, ensure_ascii=False, indent=1,
                                                          default=str))
    pc = lambda v: f"{100 * v:+.2f}%"  # noqa: E731
    testo = ["# La copia dei trader migliori di Hyperliquid: il conto in avanti", "",
             "Regole in `HYPERLIQUID.md` (sezione 2; i due gruppi in più nell'aggiunta del 5 novembre). Solo informazione: non entra nel "
             "bot (soldi finti a tavolino). «Comprato meno venduto» è la somma dei pesi con il segno (negativo = più venduto che comprato).", ""]
    for nome, r in risultati.items():
        riga = f"* **{nome}**: giri raccolti {r['giri_raccolti']}, tratti con i prezzi di Binance già pubblicati {r['tratti_con_i_prezzi']}"
        if r["tratti_con_i_prezzi"]:
            riga += (f"; **dal {r['dal']} UTC, {r['ore']} ore: {pc(r['rendimento'])}** (prezzo {pc(r['lordo'])}, spese "
                     f"{pc(-r['spese'])}, funding {pc(-r['funding'])}); esposizione media {r['esposizione_media']:.2f}, comprato meno "
                     f"venduto in media {r['netto_lungo_medio']:+.2f}; leva media dei conti {r['leva_media_dei_conti']:.2f}")
        testo.append(riga + ".")
    (QUI / "HYPERLIQUID_CONTO.md").write_text("\n".join(testo) + "\n", encoding="utf-8")
    log("\n".join(testo))
    try:                                    # la misura del giudice delle balene (GIUDICE_BALENE.md, regole 10-11): solo con un giudizio
        misura_giudice(log, pan=pan, ore=ore)
    except Exception as ex:  # noqa: BLE001
        log(f"[giudice] misura non calcolata ({ex})")
    return out


if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["--giudice"]:      # solo la misura del giudice delle balene
        misura_giudice()
    else:
        esegui()
