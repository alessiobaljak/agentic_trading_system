"""Programma 6, cinquantesima prova (CINQUANTESIMA.md): F5 identica sulle monete 101-150, scarto 0,10%, esame delle
conferme (`settima.esito`).

Uso: python3 -m research.programma6.cinquantesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import settima as st
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq
from research.programma6.motore import TAKER

QUI = Path(__file__).parent
RIS = QUI / "risultati_cinquantesima"


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, da=100, a=150, indicatori_si=False)
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    ct = np.where(np.isfinite(sig), -se.funding_7(pan, lun), np.nan)
    W = vq.pesi_banda(ct, ps["U"], sig)
    df = te.conto(W, ps["R"], ps["F"], np.full(len(ps["simboli"]), TAKER + st.SCARTO))
    df.index = ps["lunedi"]
    df["dal_funding"] = -df["funding"]
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "settimane_F5_101_150.csv.gz")
    d = df[(df.index >= se.INIZIO) & (df["monete"] > 0)]
    date = pd.to_datetime(d.index.to_numpy() * 86400, unit="s")
    c = {"settimane_operate": int(len(d)), "dal": sc.data(int(d.index.min())) if len(d) else "",
         "intero": te.numeri_settimana(d["netto"]), "boot": sc.bootstrap_blocchi(d["netto"].to_numpy(), blocco=4),
         "costi_doppi": float(d["netto_doppio"].mean()), "dal_funding_annuo": float(d["dal_funding"].mean() * 52),
         "dal_prezzo_annuo": float(d["lordo"].mean() * 52), "spese_annue": float(d["spese"].mean() * 52),
         "giro_medio": float(d["giro"].mean()),
         "per_anno": {int(a): {"settimane": int((date.year == a).sum()), "annuo": float(d["netto"][date.year == a].mean() * 52)}
                      for a in sorted(set(date.year))}}
    u = d[d.index >= sc.ULTIMO_ANNO]
    c["ultimo_anno"] = float(u["netto"].mean() * 52) if len(u) else float("nan")
    c["senza_5_migliori"] = float(d["netto"].sort_values(ascending=False).iloc[5:].mean())
    f5 = pd.read_csv(QUI / "risultati_ventiquattresima" / "settimane_F5.csv.gz", index_col=0)["netto"]
    comuni = d.index.intersection(f5.index)
    c["correlazione_F5_cento"] = float(np.corrcoef(d.loc[comuni, "netto"], f5.loc[comuni])[0, 1])
    c["esito"] = st.esito(c)
    (RIS / "esame.json").write_text(json.dumps(c, ensure_ascii=False, indent=1), encoding="utf-8")
    i, b = c["intero"], c["boot"]
    testo = "\n".join([
        "# Programma 6 — risultati della cinquantesima prova (F5 sulle monete 101-150, conferma)", "",
        "Regole in `CINQUANTESIMA.md` (scritte prima).", "",
        f"* {c['settimane_operate']} settimane operate dal {c['dal']}: Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% l'anno, "
        f"volatilità {100 * i['volatilita']:.1f}%, discesa {100 * i['discesa_max']:.1f}%.",
        f"* Media settimanale {100 * b['media']:+.3f}% (intervallo {100 * b['basso']:+.3f}; {100 * b['alto']:+.3f}, p {b['p']:.4f}).",
        f"* Dal funding {100 * c['dal_funding_annuo']:+.1f}% l'anno, dal prezzo {100 * c['dal_prezzo_annuo']:+.1f}%, spese "
        f"{100 * c['spese_annue']:.1f}% (giro medio {c['giro_medio']:.2f}); a costi doppi {100 * 52 * c['costi_doppi']:+.1f}% l'anno.",
        "* Per anno: " + ", ".join(f"{a} {100 * v['annuo']:+.1f}%" for a, v in c["per_anno"].items())
        + f"; ultimo anno {100 * c['ultimo_anno']:+.1f}%; senza le 5 settimane migliori {100 * c['senza_5_migliori']:+.3f}% a settimana.",
        f"* Correlazione con F5 sulle 100: {c['correlazione_F5_cento']:.2f}.", "",
        f"**Esito: {c['esito']}**"]) + "\n"
    (QUI / "RISULTATI_CINQUANTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return c


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("CINQUANTESIMA FINITA", flush=True)
