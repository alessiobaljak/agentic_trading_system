"""Le parti nuove della prova 35: i filtri, il volume relativo, la scelta, le esecuzioni al minuto, le quantità, il conto."""
from datetime import date

import numpy as np
import pandas as pd

from stock.prove import p035

G = date(2024, 3, 4)


def minuti(righe):
    t = pd.date_range("2024-03-04 14:35", periods=len(righe), freq="min", tz="UTC")
    return pd.DataFrame(righe, columns=["open", "high", "low", "close"], index=t)


def test_filtri_atr_e_volume_delle_sedute_prima():
    n = 20
    i = pd.date_range("2024-01-02", periods=n, freq="B", tz="America/New_York")
    df = pd.DataFrame({"open": 10.0, "high": 11.0, "low": 9.0, "close": 10.0, "volume": 2_000_000.0}, index=i)
    rett = pd.Series(10.0, index=pd.Index(i.date))
    d = p035.filtri(df, rett)
    assert d["passa"].iloc[:14].sum() == 0               # servono le 14 sedute prima
    assert d["passa"].iloc[14:].all()
    assert abs(d["atr"].iloc[-1] - 2.0) < 1e-9 and abs(d["adv"].iloc[-1] - 2e6) < 1e-6


def test_volume_relativo_e_scelta():
    assert p035.volume_relativo(300.0, [100.0] * 14) == 3.0
    assert p035.volume_relativo(300.0, [100.0] * 13 + [None]) is None
    rv = {f"S{i:02d}": float(i) for i in range(30)}
    s = p035.scegli(rv)
    assert len(s) == 20 and s[0] == "S29" and "S00" not in s      # sotto 1 non entra
    assert p035.scegli({"A": 0.9, "B": 1.0}) == ["B"]


def test_esegui_acquisto_che_va_alla_chiusura():
    b = minuti([[10.0, 10.05, 9.9, 10.0], [10.0, 10.3, 10.0, 10.25], [10.25, 10.6, 10.2, 10.5], [10.5, 10.9, 10.45, 10.8]])
    op = p035.esegui(b, 1, 10.2, 2.0, G, "X")          # stop a 0,2 sotto l'ingresso
    assert op.ingresso == 10.2 and not op.allo_stop and op.uscita == 10.8


def test_esegui_il_minimo_prima_della_rottura_non_conta():
    # il minuto della rottura parte sotto il livello, il minimo (9,5) è prima della rottura, la chiusura (10,25) sopra lo stop
    b = minuti([[9.8, 10.3, 9.5, 10.25], [10.25, 10.4, 10.2, 10.3]])
    op = p035.esegui(b, 1, 10.2, 2.0, G, "X")
    assert not op.allo_stop
    # se la chiusura di quel minuto è sotto lo stop (10,0), allo stop
    b = minuti([[9.8, 10.3, 9.5, 9.9], [9.9, 10.0, 9.8, 9.9]])
    op = p035.esegui(b, 1, 10.2, 2.0, G, "X")
    assert op.allo_stop and op.uscita == 10.0


def test_esegui_apertura_oltre_il_livello_e_stop_dopo_con_buco():
    b = minuti([[10.5, 10.6, 10.35, 10.4], [10.0, 10.1, 9.9, 10.0]])    # entra a 10,5; stop a 10,3; il minuto dopo apre a 10,0
    op = p035.esegui(b, 1, 10.2, 2.0, G, "X")
    assert op.ingresso == 10.5 and op.allo_stop and op.uscita == 10.0
    b = minuti([[10.5, 10.6, 10.25, 10.4]])                             # apre oltre il livello e tocca lo stop nello stesso minuto
    op = p035.esegui(b, 1, 10.2, 2.0, G, "X")
    assert op.allo_stop and abs(op.uscita - 10.3) < 1e-9


def test_esegui_vendita_e_nessuna_rottura():
    b = minuti([[10.0, 10.1, 9.7, 9.75], [9.75, 9.8, 9.5, 9.6]])
    op = p035.esegui(b, -1, 9.8, 2.0, G, "X")
    assert op.lato == -1 and op.ingresso == 9.8 and not op.allo_stop and op.uscita == 9.6
    assert p035.esegui(minuti([[10.0, 10.1, 9.9, 10.0]]), 1, 10.5, 2.0, G, "X") is None


def test_quantita_rischio_e_limite():
    assert p035.azioni(100_000, 100.0, 1.0) == 200          # 4 × 100'000 / 20 / 100 = 200 < 1'000 / 1 = 1'000
    assert p035.azioni(100_000, 10.0, 1.0) == 1000           # il rischio decide: 1'000 / 1
    assert p035.azioni(100_000, 100.0, 1.0, leva=1.0) == 50


def test_conto_senza_costi_e_con_costi():
    op = p035.Operazione(G, "X", 1, 100.0, pd.Timestamp("2024-03-04 14:40", tz="UTC"), 101.0, pd.Timestamp("2024-03-04 20:59", tz="UTC"),
                         False, 1.0)
    r = p035.conto([op], [G], 0.0, 0.0, scarto=False, commissioni=False)
    assert abs(r[G] - 200 * 1.0 / 100_000) < 1e-12
    r2 = p035.conto([op], [G], 0.001, 0.001)
    assert r2[G] < r[G]
    assert np.isfinite(r2[G])
