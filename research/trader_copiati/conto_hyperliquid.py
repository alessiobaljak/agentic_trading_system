"""Il conto della copia dei trader migliori di Hyperliquid (HYPERLIQUID.md, sezione 2), dalle posizioni raccolte in `hyperliquid/`.

A ogni giro della raccolta (ogni 4 ore) il portafoglio copiato è la media dei 20 conti della settimana del peso di ogni moneta (valore
della posizione con il segno diviso il valore del conto), abbinato ai perpetui di Binance e scalato a un'esposizione totale non oltre 2.
I pesi entrano all'apertura dell'ora dopo il giro e si tengono fino all'entrata del giro dopo, sui prezzi orari di Binance (file
giornalieri dell'archivio pubblico, che escono il giorno dopo), con il costo a mercato sui cambi di peso e il funding di Binance.

Dal 5 novembre 2026 anche i due gruppi dell'aggiunta di HYPERLIQUID.md: gli stessi conti con ognuno a esposizione uguale, e le
«balene» (i 20 conti piu' grandi).

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
    return out


if __name__ == "__main__":
    esegui()
