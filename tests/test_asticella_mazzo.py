"""Il mazzo dello Sharpe corretto per famiglie (`research/programma6/asticella.py`) contro il registro (backlog P34, 12 novembre 2026;
revisione `audits/reports/2026-11-12-MAZZO_ASTICELLA.md`).

* ogni prova dalla 49 in poi entra con tante varianti quante ne conta il registro: come serie (`serie_nuove`) o come gruppo a se'
  senza serie (`senza_serie`); le differenze ammesse sono scritte in `asticella.DIFFERENZE_DAL_REGISTRO` con il perche';
* ogni cartella di risultati con una serie o degli eventi e' letta dal mazzo, o scritta in `asticella.FUORI_DAL_MAZZO`;
* le prove a eventi usano le stesse operazioni che il registro dice (stesso filtro della loro regola).
Elenco intero in `research/programma6/MAZZO_ASTICELLA.md`."""
import re
from pathlib import Path

import pandas as pd

from research.programma6 import asticella as ast
from research.src.registro import leggi

RICERCA = Path(ast.__file__).resolve().parents[1]
PREFISSI = ("settimane", "eventi", "operazioni", "giorni", "picchi", "mesi")
P6_DALLA_49 = ("quarantanovesima", "cinquantesima", "cinquantunesima", "cinquantaduesima", "cinquantatreesima",
               "cinquantaquattresima", "cinquantacinquesima", "cinquantaseiesima")

# Operazioni usate, come le scrive il registro (colonna dei risultati). Non ci sono: 90 e 91 (il registro dice 326 e 604, i file
# rifatti dopo ne hanno 327 e 630: registro da aggiornare) e 104 (il registro da' solo il periodo che decide, 523).
EVENTI_DAL_REGISTRO = {"75 G16": 3494, "76 G17": 393, "78 G19": 11638, "81 P9C": 409, "82 P9C lunga": 2389, "83 P9D": 461,
                       "96 G22": 46, "98 G23": 67, "99 G24": 445, "103 LV": 200, "105 CB": 104, "107 G13C": 77, "113 N3G": 87,
                       "115 BL": 65, "126 GT": 167, "128 BP": 818, "129 IM": 80, "130 TE": 116, "133 QO": 23969,
                       "134 PM": 668, "136 NT": 3483, "140 QH": 63, "141 FS": 3896, "146 AT": 28}


def _conto_del_registro() -> dict:
    """Varianti contate per prova (colonna «varianti nel conto»): le conferme e le prove senza conto valgono 0, «1 a eventi + 1
    portafoglio» vale 1 (l'unico modo che torna con la riga «Totale nel conto»)."""
    out = {}
    for n, celle in leggi()["prove"].items():
        c = re.sub(r"\s+", " ", celle[1])
        if n >= 49:
            out[n] = 0 if (c.startswith("conferma") or c == "—" or "di conferma" in c) else int(re.findall(r"\d+", c)[0])
    return out


def _cartelle_con_serie() -> list:
    cartelle = [RICERCA / "programma6" / f"risultati_{n}" for n in P6_DALLA_49]
    for p in ("programma7", "programma8", "programma9"):
        cartelle += sorted((RICERCA / p).glob("risultati_*"))
    return [c for c in cartelle if c.is_dir() and any(f.is_file() and f.name.startswith(PREFISSI) for f in c.iterdir())]


def test_ogni_prova_del_registro_e_nel_mazzo_con_le_sue_varianti():
    per_prova = {}
    for nome in list(ast.serie_nuove()) + [n for n, _ in ast.senza_serie()]:
        k = int(nome.split()[0])
        per_prova[k] = per_prova.get(k, 0) + 1
    diverse = {n: (r, per_prova.get(n, 0)) for n, r in _conto_del_registro().items()
               if r != per_prova.get(n, 0) and n not in ast.DIFFERENZE_DAL_REGISTRO}
    assert not diverse, f"prova: (varianti nel registro, nel mazzo); aggiungerle o scriverle in DIFFERENZE_DAL_REGISTRO: {diverse}"


def test_ogni_cartella_con_una_serie_salvata_e_letta(monkeypatch):
    letti = set()
    vero = pd.read_csv

    def spia(f, *a, **k):
        letti.add(Path(f).resolve().parent)
        return vero(f, *a, **k)

    monkeypatch.setattr(pd, "read_csv", spia)
    serie = ast.serie_nuove()
    ast.senza_serie()
    mancano = [str(c.relative_to(RICERCA)) for c in _cartelle_con_serie()
               if c.resolve() not in letti and str(c.relative_to(RICERCA)) not in ast.FUORI_DAL_MAZZO]
    assert not mancano, f"cartelle con una serie salvata ma fuori dal mazzo (aggiungerle o scriverle in FUORI_DAL_MAZZO): {mancano}"
    assert len(serie) >= 176, len(serie)                    # 12 novembre: 176 serie dalla 49 in poi, piu' 28 varianti senza serie


def test_le_prove_a_eventi_usano_le_operazioni_del_registro():
    serie = ast.serie_nuove()
    diverse = {n: (atteso, serie[n].attrs.get("eventi")) for n, atteso in EVENTI_DAL_REGISTRO.items()
               if n not in serie or serie[n].attrs.get("eventi") != atteso}
    assert not diverse, f"prova: (operazioni nel registro, nel mazzo): {diverse}"


def test_senza_serie_conta_come_gruppi_a_se():
    s = dict(ast.senza_serie())
    assert sum(n.startswith("108 ") for n in s) == 18 and sum(n.startswith("111 ") for n in s) == 8
    assert "110 CC" in s and "151 WE" in s
    _, soli = ast.mazzo()
    assert len(soli) == 18 + len(s)                        # le prove 1 e 2B (18) piu' queste
