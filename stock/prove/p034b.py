"""Controllo dopo le prove 27, 28, 32 e 34: un paniere di aziende piccole a pesi uguali rende meno dell'IWM di per sé?

    python -m stock.prove.p034b           # servono le chiavi di Alpaca: gira su GitHub (azioni-ricerca)

**Non è una prova** (non sceglie titoli migliori di altri e non entra nel conto delle prove): misura la base contro cui le quattro prove
sulle piccole si sono confrontate. Ogni fine mese, tutti i titoli ammessi con i filtri delle prove (fuori dall'S&P 500, chiusura da 5
dollari, mediana di 2 milioni di dollari scambiati nelle 20 sedute prima, non fondi), tenuti un mese da chiusura a chiusura:

* A — i titoli di FINRA (l'universo della prova 32, dal 2018), a pesi uguali, a pesi per dollari scambiati, e senza i nomi con
  «Acquisition» (le società vuote in attesa di una fusione si chiamano quasi tutte così);
* B — le aziende con un comunicato sui risultati nel mese (l'universo della prova 34, dal 2016), a pesi uguali e per dollari;
* la quota di nomi con «Acquisition» fra i 50 scelti dalla prova 32 (la spiegazione che lì era scritta «non verificata»).

Sul solo periodo di ricerca (fino al 31 dicembre 2024). Scrive `P034b_risultati.md`.
"""
from __future__ import annotations

import math
from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from stock.dati import alpaca, archivio, controlli
from stock.prove.p001 import QUI
from stock.prove.p003 import prepara_titolo
from stock.prove.p027 import DOLLARI_MINIMI, PREZZO_MINIMO, SEDUTE_DOLLARI, scarica
from stock.prove.p028 import decisioni as fine_mese
from stock.prove.p028 import ritorno
from stock.prove import p032, p034
from stock.strategie import tono

FINO = date(2024, 12, 31)
FONDO = "IWM"
TIPI = {"raw": "1Day_allora", "az": "azioni_allora", "asof": "-"}


def t_di(x) -> float:
    x = np.asarray(x, float)
    return float(x.mean() / x.std(ddof=1) * math.sqrt(len(x))) if len(x) > 2 else float("nan")


def vuota(nome: str) -> bool:
    return "acquisition" in nome.lower()


def main():
    fini, membri = fine_mese()
    nomi = alpaca.nomi_dei_titoli()
    # A: l'universo della prova 32
    vs = p032.vendite_scoperto()
    regolamenti = sorted(vs)
    giorni_a = [g for g in fini if p032.PRIMA <= g <= FINO]
    valida = {g: p032.data_valida(regolamenti, g) for g in giorni_a}
    cand_a = sorted({s for g in giorni_a[:-1] for s in vs[valida[g]] if s not in membri[g]} - {FONDO})
    # B: l'universo della prova 34
    ev = p034.comunicati()
    ev = ev[ev["sic"] != p034.VUOTE]
    cand_b = sorted(set(ev["simbolo"]) - {FONDO})
    tutti = sorted(set(cand_a) | set(cand_b))
    scarica(tutti + [FONDO], TIPI["raw"], TIPI["az"], TIPI["asof"])
    fondi = {s for s in tutti if tono.e_un_fondo(nomi.get(s, ""))}
    chiusure, dollari = {}, {}
    for s in tutti:
        df = archivio.carica(s, TIPI["raw"])
        if s in fondi or df is None or len(df) <= SEDUTE_DOLLARI:
            continue
        i = pd.Index(controlli.date_ny(df.index))
        chiusure[s] = pd.Series(df["close"].to_numpy(), index=i)
        dollari[s] = pd.Series((df["close"] * df["volume"]).to_numpy(), index=i)

    def mediana_dollari(s: str, g: date) -> float | None:
        c = chiusure.get(s)
        if c is None or g not in c.index or c.loc[g] < PREZZO_MINIMO:
            return None
        v = dollari[s].loc[:g].iloc[:-1].iloc[-SEDUTE_DOLLARI:]
        m = float(v.median()) if len(v) == SEDUTE_DOLLARI else 0.0
        return m if m >= DOLLARI_MINIMI else None
    _, rett_f, _ = prepara_titolo(FONDO, FINO, TIPI["raw"], TIPI["az"])
    calendario = sorted(rett_f.index)
    amm_a = {g: {s: m for s in vs[valida[g]] if s not in membri[g] and (m := mediana_dollari(s, g))} for g in giorni_a[:-1]}
    giorni_b = [g for g in fini if p034.PRIMA <= g <= FINO]
    amm_b = {}
    eventi = []
    for s, d in zip(ev["simbolo"], ev["deposito"]):
        x = p034.intorno(calendario, d)
        if x and s in chiusure and s not in p034.membri_al(x[0], fini, membri) and mediana_dollari(s, x[0]):
            eventi.append((s, x[1], 0.0))
    for k, g in enumerate(giorni_b[:-1]):
        prima = giorni_b[k - 1] if k else date(2015, 12, 31)
        amm_b[g] = {s: m for s in p034.del_mese(eventi, prima, g) if (m := mediana_dollari(s, g))}
    rett, rotti = {}, 0
    for s in sorted(set().union(*[set(v) for v in amm_a.values()], *[set(v) for v in amm_b.values()])):
        try:
            _, rett[s], _ = prepara_titolo(s, FINO, TIPI["raw"], TIPI["az"])
        except Exception:  # noqa: BLE001 — titolo con i dati rotti: si conta e resta fuori
            rotti += 1

    def panieri(amm: dict, giorni: list[date]) -> dict[str, list[tuple[date, float]]]:
        out = {"pesi uguali": [], "pesi per dollari": [], "senza «Acquisition»": [], "mediana dei titoli": []}
        for k, g0 in enumerate(giorni[:-1]):
            g1 = giorni[k + 1]
            if g0 not in rett_f.index:
                continue
            f = ritorno(rett_f, g0, g1)
            r = {s: ritorno(rett[s], g0, g1) for s in amm.get(g0, {}) if s in rett and g0 in rett[s].index}
            if len(r) < 25:
                continue
            w = np.array([amm[g0][s] for s in r])
            v = np.array(list(r.values()))
            senza = [x for s, x in r.items() if not vuota(nomi.get(s, ""))]
            out["pesi uguali"].append((g0, float(v.mean()) - f))
            out["pesi per dollari"].append((g0, float((w * v).sum() / w.sum()) - f))
            out["senza «Acquisition»"].append((g0, float(np.mean(senza)) - f))
            out["mediana dei titoli"].append((g0, float(np.median(v)) - f))
        return out
    righe = []
    for nome, amm, giorni in (("A — i titoli di FINRA (prova 32)", amm_a, giorni_a), ("B — chi ha un comunicato nel mese (prova 34)", amm_b, giorni_b)):
        for variante, serie in panieri(amm, giorni).items():
            x = np.array([v for _, v in serie])
            anni = pd.Series(x, index=[g.year for g, _ in serie]).groupby(level=0).sum()
            righe.append(f"| {nome} | {variante} | {len(x)} | **{x.mean():+.2%}** | {t_di(x):.2f} | {np.median(x):+.2%} | "
                         f"{(x > 0).mean():.0%} | " + " ".join(f"{y}: {v:+.0%}" for y, v in anni.items()) + " |")
    # le società vuote: quanti nomi con «Acquisition» fra gli ammessi e fra i 50 scelti dalla prova 32
    quota_amm = {}
    quota_scelti = {}
    for g in giorni_a[:-1]:
        a = [s for s in amm_a[g] if s in rett]
        scelti = p032.scegli(vs[valida[g]], set(a))
        quota_amm.setdefault(g.year, []).append(np.mean([vuota(nomi.get(s, "")) for s in a]) if a else 0.0)
        quota_scelti.setdefault(g.year, []).append(np.mean([vuota(nomi.get(s, "")) for s in scelti]) if scelti else 0.0)
    q = " | ".join(f"{y}: {np.mean(quota_amm[y]):.0%} / {np.mean(quota_scelti[y]):.0%}" for y in sorted(quota_amm))
    testo = ["# Controllo dopo le prove sulle piccole — il paniere di base contro l'IWM", "",
             f"Calcolato da `python -m stock.prove.p034b` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC. **Non è una prova**: misura la base "
             "contro cui si sono confrontate le prove 27, 28, 32 e 34 (non entra nel conto). Ogni fine mese tutti i titoli ammessi con i "
             "filtri delle prove, tenuti un mese da chiusura a chiusura, meno l'IWM negli stessi giorni; solo il periodo di ricerca, "
             f"fino al 31 dicembre 2024. Titoli con i dati rotti {rotti}; fondi esclusi {len(fondi)}.", "",
             "| Paniere | Come | Mesi | Medio meno IWM al mese | t | Mediana | Mesi sopra l'IWM | Somma per anno |",
             "|---|---|---|---|---|---|---|---|", *righe, "",
             "**Nomi con «Acquisition» (società vuote in attesa di una fusione), media per anno: fra gli ammessi della prova 32 / fra i 50 "
             f"scelti dalla prova 32:** {q}.", "",
             "Il nome viene dall'elenco di oggi di Alpaca: una società vuota che si è già fusa può avere oggi un altro nome, quindi le quote "
             "sono un minimo."]
    (QUI / "P034b_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[-12:]))


if __name__ == "__main__":
    main()
