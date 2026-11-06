"""I giorni che mancano nell'archivio pubblico di Binance (research/programma6/buchi_archivio.py): seconda.candele li prende dai file
dell'interfaccia pubblica solo dove l'archivio non ha il giorno (il 28 ottobre 2026 mancava per tutte le monete)."""
import io
import zipfile

import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma6 import seconda as sc


def _riga(giorno, prezzo):
    ms = giorno * 86_400_000
    return [ms, prezzo, prezzo + 1, prezzo - 1, prezzo, 10.0, ms + 86_399_999, 1000.0, 5, 4.0, 400.0, 0]


def test_archivio_vince_e_l_interfaccia_riempie_il_buco(tmp_path, monkeypatch):
    monkeypatch.setattr(sc, "DATI", tmp_path)
    g = sc.giorno(2026, 10, 27)
    cartella = tmp_path / "XUSDT" / "giorni"
    cartella.mkdir(parents=True)
    testo = io.StringIO()
    pd.DataFrame([_riga(g, 100.0), _riga(g + 2, 102.0)]).to_csv(testo, header=False, index=False)
    with zipfile.ZipFile(cartella / "XUSDT-1d-2026-10.zip", "w") as z:
        z.writestr("XUSDT-1d-2026-10.csv", testo.getvalue())
    api = tmp_path / "XUSDT" / "giorni_api"
    api.mkdir()
    pd.DataFrame([_riga(g + 1, 101.0)], columns=m5.KLINE).to_csv(api / "XUSDT-1d-2026-10-28.csv", index=False)
    pd.DataFrame([_riga(g, 999.0)], columns=m5.KLINE).to_csv(api / "XUSDT-1d-2026-10-27.csv", index=False)
    c = sc.candele("XUSDT")
    assert list(c.index) == [g, g + 1, g + 2]
    assert c.loc[g + 1, "close"] == 101.0          # il buco riempito
    assert c.loc[g, "close"] == 100.0              # dove l'archivio c'e', vince l'archivio


def test_minuti_del_programma_5_con_il_buco_riempito(tmp_path, monkeypatch):
    monkeypatch.setattr(m5, "DATI", tmp_path)
    monkeypatch.setattr(m5, "controlla_periodo", lambda periodo, idea: None)   # qui conta solo la lettura dei file
    ms0 = int(pd.Timestamp("2026-10-27", tz="UTC").timestamp() * 1000)
    cartella = tmp_path / "XUSDT" / "klines"
    cartella.mkdir(parents=True)
    for giorno, prezzo in (("2026-10-27", 100.0), ("2026-10-29", 102.0)):
        ms = int(pd.Timestamp(giorno, tz="UTC").timestamp() * 1000)
        testo = io.StringIO()
        pd.DataFrame([[ms + 60_000 * i, prezzo, prezzo, prezzo, prezzo, 1.0, ms + 60_000 * i + 59_999, 1.0, 1, 1.0, 1.0, 0]
                      for i in range(3)]).to_csv(testo, header=False, index=False)
        with zipfile.ZipFile(cartella / f"XUSDT-1m-{giorno}.zip", "w") as z:
            z.writestr(f"XUSDT-1m-{giorno}.csv", testo.getvalue())
        (cartella / f"XUSDT-1m-{giorno}.zip.ok").write_text("ok")
    api = tmp_path / "XUSDT" / "klines_api"
    api.mkdir()
    ms = ms0 + 86_400_000
    pd.DataFrame([[ms, 101.0, 101.0, 101.0, 101.0, 1.0, ms + 59_999, 1.0, 1, 1.0, 1.0, 0],
                  [ms0, 999.0, 999.0, 999.0, 999.0, 1.0, ms0 + 59_999, 1.0, 1, 1.0, 1.0, 0]],
                 columns=m5.KLINE).to_csv(api / "XUSDT-1m-2026-10-28.csv", index=False)
    df = m5.minuti("XUSDT", "A", storia_giorni=0)
    assert df.loc[ms // 60_000, "close"] == 101.0           # il 28 ottobre dall'interfaccia
    assert df.loc[ms0 // 60_000, "close"] == 100.0          # dove l'archivio c'e', vince l'archivio
