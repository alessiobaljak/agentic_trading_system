"""Il mazzo dello Sharpe corretto per famiglie (`research/programma6/asticella.py`, `serie_nuove`) deve contenere ogni prova dalla 49
in poi che ha salvato una serie settimanale o un file di eventi (backlog P34, 12 novembre 2026: il mazzo si era fermato alla prova
102). Una prova lasciata fuori apposta va scritta in `asticella.FUORI_DAL_MAZZO` con il perche' (elenco in
`research/programma6/MAZZO_ASTICELLA.md`)."""
from pathlib import Path

import pandas as pd

from research.programma6 import asticella as ast

RICERCA = Path(ast.__file__).resolve().parents[1]
PREFISSI = ("settimane", "eventi", "operazioni", "giorni", "picchi")
P6_DALLA_49 = ("quarantanovesima", "cinquantesima", "cinquantunesima", "cinquantaduesima", "cinquantatreesima",
               "cinquantaquattresima", "cinquantacinquesima", "cinquantaseiesima")


def _cartelle_con_serie() -> list:
    cartelle = [RICERCA / "programma6" / f"risultati_{n}" for n in P6_DALLA_49]
    for p in ("programma7", "programma8", "programma9"):
        cartelle += sorted((RICERCA / p).glob("risultati_*"))
    return [c for c in cartelle if c.is_dir() and any(f.is_file() and f.name.startswith(PREFISSI) for f in c.iterdir())]


def test_ogni_prova_con_una_serie_salvata_e_nel_mazzo(monkeypatch):
    letti = set()
    vero = pd.read_csv

    def spia(f, *a, **k):
        letti.add(Path(f).resolve().parent)
        return vero(f, *a, **k)

    monkeypatch.setattr(pd, "read_csv", spia)
    serie = ast.serie_nuove()
    mancano = [str(c.relative_to(RICERCA)) for c in _cartelle_con_serie()
               if c.resolve() not in letti and str(c.relative_to(RICERCA)) not in ast.FUORI_DAL_MAZZO]
    assert not mancano, f"cartelle con una serie salvata ma fuori dal mazzo (aggiungerle o scriverle in FUORI_DAL_MAZZO): {mancano}"
    assert len(serie) >= 178, len(serie)                    # 12 novembre: 178 serie dalla 49 in poi (267 con le prove fino alla 48)
    for n in ("50 F5 101-150", "96 G22", "103 LV", "112 LQ", "133 QO", "148 B", "149 BTCUSDT_4h_A", "152 V1", "152 V3"):
        assert n in serie and serie[n].abs().sum() > 0, n
