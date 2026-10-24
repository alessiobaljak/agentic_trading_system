"""Programma 9 (METODO.md, sezione 3): l'esplorazione sul 2022-2023. Ogni ingrediente da solo (cinque fasce per giorno) e ogni
coppia (tre fasce per tre), sui rendimenti a 1, 3 e 7 giorni meno la media dell'universo. Legge solo `esplorazione.pkl`.

Uso: python3 -m research.programma9.esplora
"""
from __future__ import annotations

import itertools
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma9.dati import DATI, ORIZZONTI

QUI = Path(__file__).parent
RIS = QUI / "esplorazione"
MERCATO = ("btc_r7", "btc_r30", "mercato_f7")          # uguali per tutte le monete del giorno: fasce nel tempo
MIN_GIORNI = 200


def fasce(df: pd.DataFrame, col: str, n: int) -> pd.Series:
    """Fasce 0..n-1: per le monete il rango nel giorno, per il mercato il rango nel tempo."""
    if col in MERCATO:
        v = df.groupby("giorno")[col].first()
        q = pd.qcut(v.rank(method="first"), n, labels=False)
        return df["giorno"].map(q)
    r = df.groupby("giorno")[col].rank(pct=True)
    return np.minimum((r * n).fillna(-1).astype(int), n - 1).where(r.notna())


def misura(df: pd.DataFrame, maschera: pd.Series, h: int) -> dict:
    """Media per giorno del rendimento in piu' delle monete nella casella; t fra i giorni (un giorno ogni h, niente sovrapposizioni)."""
    d = df.loc[maschera & df[f"y{h}"].notna(), ["giorno", f"y{h}"]]
    m = d.groupby("giorno")[f"y{h}"].mean()
    m = m[(m.index - m.index.min()) % h == 0]
    if len(m) < MIN_GIORNI / h:
        return {"giorni": int(len(m)), "media": np.nan, "t": np.nan, "monete_al_giorno": np.nan}
    return {"giorni": int(len(m)), "media": float(m.mean()), "t": float(m.mean() / (m.std(ddof=1) / np.sqrt(len(m)))),
            "monete_al_giorno": float(d.groupby("giorno").size().mean())}


def esegui(log=print) -> dict:
    df = pd.read_pickle(DATI / "esplorazione.pkl")
    ingredienti = [c for c in df.columns if c not in ("giorno", "simbolo") and not c.startswith("y")]
    log(f"[p9 esplora] {len(df)} righe, {df['giorno'].nunique()} giorni, {len(ingredienti)} ingredienti")
    f5 = {c: fasce(df, c, 5) for c in ingredienti}
    f3 = {c: fasce(df, c, 3) for c in ingredienti}
    singoli, coppie = [], []
    for h in ORIZZONTI:
        for c in ingredienti:
            for q in range(5):
                singoli.append({"ingrediente": c, "fascia": q, "h": h, **misura(df, f5[c] == q, h)})
        sing3 = {(c, q): misura(df, f3[c] == q, h)["media"] for c in ingredienti for q in range(3)}
        for a, b in itertools.combinations(ingredienti, 2):
            if a in MERCATO and b in MERCATO:
                continue
            for qa in range(3):
                for qb in range(3):
                    m = misura(df, (f3[a] == qa) & (f3[b] == qb), h)
                    sa, sb = sing3[(a, qa)], sing3[(b, qb)]
                    migliore = max([x for x in (sa, sb) if np.isfinite(x)], key=lambda x: abs(x), default=np.nan)
                    coppie.append({"a": a, "fascia_a": qa, "b": b, "fascia_b": qb, "h": h, **m,
                                   "solo_a": sa, "solo_b": sb,
                                   "aggiunta": (m["media"] - migliore) if np.isfinite(m["media"]) and np.isfinite(migliore) and
                                   np.sign(m["media"]) == np.sign(migliore) else np.nan})
    RIS.mkdir(exist_ok=True)
    s, c = pd.DataFrame(singoli), pd.DataFrame(coppie)
    s.to_csv(RIS / "singoli.csv", index=False)
    c.to_csv(RIS / "coppie.csv", index=False)
    s["at"], c["at"] = s["t"].abs(), c["t"].abs()
    righe = ["# Programma 9 — esplorazione sul 2022-2023 (descrittiva: niente qui è una prova)", "",
             f"{len(df)} righe moneta-giorno, {df['giorno'].nunique()} giorni, {len(ingredienti)} ingredienti; caselle delle coppie "
             f"{len(c)}, dei singoli {len(s)}. Media = rendimento in più della moneta rispetto alla media dell'universo, a h giorni; t fra "
             "i giorni senza sovrapposizioni.", "", "## Gli ingredienti da soli (le 25 fasce con il t più alto)", "",
             "| ingrediente | fascia (0 = più basso) | h | media | t | giorni |", "|---|---|---|---|---|---|"]
    for _, x in s.sort_values("at", ascending=False).head(25).iterrows():
        righe.append(f"| {x['ingrediente']} | {x['fascia']} | {x['h']} | {100 * x['media']:+.2f}% | {x['t']:.1f} | {x['giorni']} |")
    righe += ["", "## Le coppie (le 40 caselle con il t più alto e un'aggiunta rispetto agli ingredienti da soli)", "",
              "| a (fascia) | b (fascia) | h | media | t | solo a | solo b | aggiunta | monete al giorno |", "|---|---|---|---|---|---|---|---|---|"]
    buone = c[c["aggiunta"].abs() > 0].sort_values("at", ascending=False).head(40)
    for _, x in buone.iterrows():
        righe.append(f"| {x['a']} ({x['fascia_a']}) | {x['b']} ({x['fascia_b']}) | {x['h']} | {100 * x['media']:+.2f}% | {x['t']:.1f} | "
                     f"{100 * x['solo_a']:+.2f}% | {100 * x['solo_b']:+.2f}% | {100 * x['aggiunta']:+.2f}% | {x['monete_al_giorno']:.1f} |")
    testo = "\n".join(righe) + "\n"
    (QUI / "ESPLORAZIONE.md").write_text(testo, encoding="utf-8")
    log(testo)
    return {"singoli": len(s), "coppie": len(c)}


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("ESPLORA FINITA", flush=True)
