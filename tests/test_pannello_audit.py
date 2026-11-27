"""Il pannello del programma 6 dopo l'audit del 26 novembre 2026 (research/programma6/seconda.py, funding_api.py,
tipi_contratto.py, paper/aggiorna.py):

* motore-1: il funding dopo l'ultimo file mensile viene dall'interfaccia pubblica di Binance (``funding_api/``), l'archivio vince
  dove c'e', l'ultimo giorno del mese prende il regolamento delle 00:00 del giorno dopo e i giorni ancora senza il dato vero si
  segnano (``funding_stimato``); ``applica_stima`` lascia il funding vero dove c'e';
* motore-2: i giorni di un contratto che non e' una moneta (tipo ufficiale di exchangeInfo) si tolgono dal suo onboardDate in poi;
* motore-4: un simbolo rilanciato (LITUSDT il 23 dicembre 2025) diventa un contratto nuovo, e il controllo dei dati segnala le
  aperture lontane piu' del 20% dalla chiusura prima.
"""
import io
import json
import zipfile
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("numba")

from research.programma6 import funding_api as fa  # noqa: E402
from research.programma6 import seconda as sc  # noqa: E402
from research.programma6 import tipi_contratto as tc  # noqa: E402
from research.programma6.paper import aggiorna as ag  # noqa: E402

G = 86_400_000


def _ms(a, m, g, ora=0):
    return int(datetime(a, m, g, ora, tzinfo=timezone.utc).timestamp() * 1000)


def _candele(dati, simbolo, giorni, prezzi, volumi):
    """Un file di candele giornaliere (senza intestazione, come i file vecchi dell'archivio)."""
    righe = [[g * G, p, p, p, p, 1.0, g * G + G - 1, v, 5, 1.0, v / 2, 0] for g, p, v in zip(giorni, prezzi, volumi)]
    cartella = dati / simbolo / "giorni"
    cartella.mkdir(parents=True, exist_ok=True)
    testo = io.StringIO()
    pd.DataFrame(righe).to_csv(testo, header=False, index=False)
    with zipfile.ZipFile(cartella / f"{simbolo}-1d-{sc.data(giorni[0])}.zip", "w") as z:
        z.writestr(f"{simbolo}-1d-{sc.data(giorni[0])}.csv", testo.getvalue())


def _funding_archivio(dati, simbolo, mese, righe):
    cartella = dati / simbolo / "funding"
    cartella.mkdir(parents=True, exist_ok=True)
    testo = "calc_time,funding_interval_hours,last_funding_rate\n" + "\n".join(f"{ts},8,{x}" for ts, x in righe)
    with zipfile.ZipFile(cartella / f"{simbolo}-fundingRate-{mese}.zip", "w") as z:
        z.writestr(f"{simbolo}-fundingRate-{mese}.csv", testo)


def _funding_api(dati, simbolo, righe, fino_ms):
    fa.salva(dati / simbolo / fa.CARTELLA, simbolo,
             [{"fundingTime": ts, "fundingRate": f"{x:.8f}", "markPrice": "1.0"} for ts, x in righe], fino_ms)


def _ottobre(da_giorno=20):
    """I regolamenti di ottobre 2026 alle 00, 08 e 16 dal ``da_giorno``: 0,0001 alle 00, 0,0002 alle 08, 0,0003 alle 16."""
    return [(_ms(2026, 10, g, h) + 3, {0: 0.0001, 8: 0.0002, 16: 0.0003}[h]) for g in range(da_giorno, 32) for h in (0, 8, 16)]


@pytest.fixture
def dati(tmp_path, monkeypatch):
    monkeypatch.setattr(sc, "DATI", tmp_path)
    monkeypatch.setattr(sc, "PANNELLO", tmp_path / "pannello.pkl")
    return tmp_path


# ---------------------------------------------------------------------------
# motore-1: il funding vero dell'interfaccia
# ---------------------------------------------------------------------------

def test_archivio_vince_e_l_interfaccia_chiude_il_31_ottobre(dati):
    _funding_archivio(dati, "XUSDT", "2026-10", _ottobre())
    # l'interfaccia ripete il regolamento delle 16 del 31 ottobre (3 ms dopo, un altro tasso: vince l'archivio), poi le 00:00 del
    # 1° novembre (del 31 ottobre) e le 08 del 1° novembre
    _funding_api(dati, "XUSDT", [(_ms(2026, 10, 31, 16) + 6, 0.009), (_ms(2026, 11, 1, 0) + 1, 0.0004),
                                 (_ms(2026, 11, 1, 8), 0.0005)], _ms(2026, 11, 1, 10))
    g31 = sc.giorno(2026, 10, 31)
    f = sc.funding_giorni("XUSDT")
    assert f[g31] == pytest.approx(0.0002 + 0.0003 + 0.0004)        # il giorno intero, con le 00:00 del 1° novembre
    assert f[g31 + 1] == pytest.approx(0.0005)
    solo = sc.funding_giorni("XUSDT", api=False)
    assert solo[g31] == pytest.approx(0.0002 + 0.0003) and (g31 + 1) not in solo.index


def test_pannello_con_il_funding_vero_e_i_giorni_stimati_segnati(dati):
    g0, g31 = sc.giorno(2026, 10, 20), sc.giorno(2026, 10, 31)
    giorni = list(range(g0, sc.giorno(2026, 11, 5) + 1))
    _candele(dati, "XUSDT", giorni, [1.0] * len(giorni), [5e6] * len(giorni))
    _funding_archivio(dati, "XUSDT", "2026-10", _ottobre())
    # senza l'interfaccia: il 31 ottobre e' a meta' (segnato), novembre con la media dei giorni coperti prima (segnato)
    pan = sc.costruisci_pannello(["XUSDT"], log=lambda x: None, tipi={})
    t = lambda g: g - pan["t0"]  # noqa: E731
    assert pan["funding_stimato"][t(g31), 0] and pan["funding_stimato"][t(g31 + 1):, 0].all()
    assert not pan["funding_stimato"][:t(g31), 0].any()
    assert pan["funding"][t(g31 + 2), 0] == pytest.approx(0.0006, rel=0.2)
    # con l'interfaccia completa fino al 3 novembre alle 09: veri il 31 ottobre, l'1 e il 2; dal 3 ancora stimati
    api = [(_ms(2026, 11, d, h), 0.001 * d) for d in (1, 2, 3) for h in (0, 8, 16)] + [(_ms(2026, 11, 4, 0), 0.0)]
    _funding_api(dati, "XUSDT", api[:7], _ms(2026, 11, 3, 9))
    pan = sc.costruisci_pannello(["XUSDT"], log=lambda x: None, tipi={})
    assert pan["funding"][t(g31), 0] == pytest.approx(0.0002 + 0.0003 + 0.001)
    assert pan["funding"][t(g31 + 1), 0] == pytest.approx(0.001 * 2 + 0.002)
    assert pan["funding"][t(g31 + 2), 0] == pytest.approx(0.002 * 2 + 0.003)
    assert not pan["funding_stimato"][:t(g31 + 3), 0].any()
    assert pan["funding_stimato"][t(g31 + 3):, 0].all()              # il 3 novembre ha solo le 08 scaricate: non e' completo


def test_applica_stima_lascia_il_funding_vero_e_stima_solo_i_giorni_segnati(dati, monkeypatch):
    g0 = sc.giorno(2026, 11, 1)
    pan = {"t0": g0, "simboli": ["XUSDT"], "close": np.ones((4, 1)), "quote_volume": np.full((4, 1), 5e6),
           "funding": np.array([[0.001], [0.002], [0.0007], [0.0007]]),
           "funding_stimato": np.array([[False], [False], [True], [True]])}
    ore = np.arange(g0 * 24, (g0 + 4) * 24)
    monkeypatch.setattr(ag, "premio_ore", lambda s: pd.Series(0.0001, index=ore))
    stimati = ag.applica_stima(pan)
    assert pan["funding"][:2, 0].tolist() == [0.001, 0.002]          # prima: stimati anche questi (dopo l'ultimo file mensile)
    assert pan["funding"][2:, 0] == pytest.approx([0.0003, 0.0003])
    assert stimati == {"XUSDT": sc.data(g0 + 2)}


def test_applica_stima_su_un_pannello_vecchio_rifa_il_funding_dai_file(dati, monkeypatch):
    g0, g31 = sc.giorno(2026, 10, 20), sc.giorno(2026, 10, 31)
    giorni = list(range(g0, sc.giorno(2026, 11, 3) + 1))
    _candele(dati, "XUSDT", giorni, [1.0] * len(giorni), [5e6] * len(giorni))
    _funding_archivio(dati, "XUSDT", "2026-10", _ottobre())
    _funding_api(dati, "XUSDT", [(_ms(2026, 11, 1, h), 0.001) for h in (0, 8, 16)] + [(_ms(2026, 11, 2, 0), 0.001)],
                 _ms(2026, 11, 2, 1))
    pan = sc.costruisci_pannello(["XUSDT"], log=lambda x: None, tipi={})
    vecchio = {k: pan[k] for k in ("t0", "simboli", "open", "high", "low", "close", "quote_volume")}
    vecchio["funding"] = np.full_like(pan["funding"], 0.0007)        # come un pannello salvato prima: senza la maschera
    ore = np.arange(g0 * 24, (g0 + len(giorni)) * 24)
    monkeypatch.setattr(ag, "premio_ore", lambda s: pd.Series(0.0001, index=ore))
    ag.applica_stima(vecchio)
    t = lambda g: g - pan["t0"]  # noqa: E731
    assert vecchio["funding"][t(g31), 0] == pytest.approx(0.0002 + 0.0003 + 0.001)
    assert vecchio["funding"][t(g31 + 1), 0] == pytest.approx(0.003)
    assert vecchio["funding"][t(g31 + 2):, 0] == pytest.approx(0.0003)   # dal 2 novembre: la stima dal premio


def test_il_paper_conta_i_giorni_ancora_senza_il_dato_vero():
    t0 = ag.INIZIO_GIORNI - 2
    M = np.zeros((6, 3), bool)
    M[0, 0] = True                                                   # prima del periodo P: non conta
    M[4, 1] = M[5, 1] = M[5, 2] = True
    sf = ag.stato_funding({"t0": t0, "funding_stimato": M})
    assert sf == {"giorni_moneta": 3, "monete": 2, "giorni": [sc.data(t0 + 4), sc.data(t0 + 5)]}


def test_il_rapporto_del_paper_dice_il_funding_senza_dato_vero_e_il_controllo_dei_dati():
    vuoto = {"long": {}, "short": {}, "lunedi": "2026-11-23"}
    r = {"dati_fino_al": "2026-11-23", "funding_stimato_dal": None, "candidate": {},
         "adesso": {"F3": vuoto, "F5": vuoto, "K1": vuoto, "M1": vuoto, "F2": {"lunedi": "2026-11-23", "long": [], "short": []},
                    "C1": {"lunedi": "2026-11-16", "long": [], "short": []}, "A1": {"giorno": "2026-11-23", "pesi": {}}},
         "funding_senza_dato_vero": {"giorni_moneta": 0, "monete": 0, "giorni": []},
         "controllo_dati": {"aperture_lontane": [{"simbolo": "AERGOUSDT", "giorno": "2025-04-16", "variazione": 3.9175},
                                                 {"simbolo": "KNCUSDT", "giorno": "2022-03-01", "variazione": 0.3126}],
                            "non_monete_tolte": 71, "rilanci": {"LITUSDT": "2025-12-23"}}}
    testo = ag.rapporto(r)
    assert "**Funding senza il dato vero** (né dall'archivio mensile né dall'interfaccia pubblica di Binance) nel periodo P: " \
           "0 giorni-moneta, 0 monete." in testo
    assert "2 aperture lontane più del 20% dalla chiusura prima in tutto il pannello (le ultime: KNCUSDT 2022-03-01 +31%, " \
           "AERGOUSDT 2025-04-16 +392%); contratti che non sono monete tolti dal loro onboardDate: 71; simboli rilanciati tenuti " \
           "separati: LITUSDT dal 2025-12-23." in testo


def test_scarico_una_richiesta_dal_regolamento_dopo_l_ultimo(dati):
    chieste, pause = [], []

    def chiedi(params):
        chieste.append(params)
        return [{"fundingTime": params["startTime"] + 5 + 8 * 3_600_000 * k, "fundingRate": "0.0001", "markPrice": "1"}
                for k in range(3)]
    adesso = _ms(2026, 11, 27, 9)
    righe, fino = fa.scarica_moneta("XUSDT", 123, adesso, chiedi=chiedi, pausa=pause.append)
    assert chieste == [{"symbol": "XUSDT", "startTime": 123, "limit": 1000}] and not pause
    assert len(righe) == 3 and fino == adesso - fa.MARGINE_MS


def test_scarico_pagina_piena_429_418_ed_errori():
    pause = []
    pagine = [[{"fundingTime": 10 + k, "fundingRate": "0"} for k in range(fa.LIMITE)], [{"fundingTime": 5000, "fundingRate": "0"}]]
    chieste = []

    def chiedi(params):
        chieste.append(params["startTime"])
        return pagine[len(chieste) - 1]
    righe, fino = fa.scarica_moneta("X", 10, 10**12, chiedi=chiedi, pausa=pause.append)
    assert chieste == [10, 10 + fa.LIMITE] and len(righe) == fa.LIMITE + 1 and pause == [fa.PAUSA]
    risposte = [429, [{"fundingTime": 7, "fundingRate": "0"}]]
    righe, _ = fa.scarica_moneta("X", 0, 10**12, chiedi=lambda p: risposte.pop(0), pausa=pause.append)
    assert len(righe) == 1 and pause[-1] == 60
    assert fa.scarica_moneta("X", 0, 10**12, chiedi=lambda p: 400, pausa=pause.append) == ([], None)
    with pytest.raises(fa.Bloccato):
        fa.scarica_moneta("X", 0, 10**12, chiedi=lambda p: 418, pausa=pause.append)
    with pytest.raises(fa.Bloccato):                                  # ancora 429 dopo un minuto: non si aspetta per ogni moneta
        fa.scarica_moneta("X", 0, 10**12, chiedi=lambda p: 429, pausa=pause.append)


def test_lo_scarico_si_ferma_dopo_cinque_errori_di_fila(dati, monkeypatch):
    monkeypatch.setattr(fa, "da_scaricare", lambda *a, **k: {f"M{i}USDT": 0 for i in range(9)})
    chieste = []
    monkeypatch.setattr(fa, "scarica_moneta", lambda s, dal, adesso: (chieste.append(s), ([], None))[1])
    monkeypatch.setattr(fa.time, "sleep", lambda x: None)
    esito = fa.main([])
    assert len(chieste) == fa.ERRORI_DI_FILA == len(esito["errori"]) and esito["bloccato"] and esito["scritte"] == 0


def test_salva_unisce_in_un_file_che_dice_fin_dove_e_completo(dati):
    c = dati / "XUSDT" / fa.CARTELLA
    _funding_api(dati, "XUSDT", [(_ms(2026, 11, 1, 0), 0.001)], _ms(2026, 11, 1, 3))
    _funding_api(dati, "XUSDT", [(_ms(2026, 11, 1, 8), 0.002), (_ms(2026, 11, 1, 0), 0.001)], _ms(2026, 11, 1, 9) + 61_000)
    assert [p.name for p in c.glob("*.csv")] == ["XUSDT-fundingRate-api-fino-2026-11-01T0901.csv"]
    df, fino = fa.leggi(c)
    assert df["ts"].tolist() == [_ms(2026, 11, 1, 0), _ms(2026, 11, 1, 8)] and fino == _ms(2026, 11, 1, 9) + 60_000
    assert fa.ultimo_giorno_completo(fino) == sc.giorno(2026, 10, 31)


def test_da_scaricare_dall_ultimo_regolamento_e_solo_monete_vive(dati):
    oggi = datetime(2026, 11, 27, tzinfo=timezone.utc)
    giorni = list(range(sc.giorno(2026, 10, 20), sc.giorno(2026, 11, 20)))
    for s in ("XUSDT", "NUOVAUSDT", "AZIONEUSDT"):
        _candele(dati, s, giorni, [1.0] * len(giorni), [5e6] * len(giorni))
    _candele(dati, "MORTAUSDT", list(range(sc.giorno(2024, 1, 1), sc.giorno(2024, 2, 1))), [1.0] * 31, [5e6] * 31)
    _funding_archivio(dati, "XUSDT", "2026-10", _ottobre())
    _funding_archivio(dati, "MORTAUSDT", "2024-01", [(_ms(2024, 1, 5), 0.0001)])
    tipi = {"AZIONEUSDT": {"contractType": "TRADIFI_PERPETUAL", "underlyingType": "EQUITY", "onboardDate": _ms(2026, 10, 20)}}
    piano = fa.da_scaricare(dati, tipi=tipi, oggi=oggi)
    assert piano == {"XUSDT": _ms(2026, 10, 31, 16) + 3 + 1, "NUOVAUSDT": _ms(2026, 10, 20)}
    _funding_api(dati, "XUSDT", [(_ms(2026, 11, 1, 0) + 2, 0.001)], _ms(2026, 11, 1, 3))
    assert fa.da_scaricare(dati, tipi=tipi, oggi=oggi)["XUSDT"] == _ms(2026, 11, 1, 0) + 3


# ---------------------------------------------------------------------------
# motore-2: i contratti che non sono monete
# ---------------------------------------------------------------------------

def test_tipi_come_il_bot():
    assert tc.e_moneta({"contractType": "PERPETUAL", "underlyingType": "COIN"})
    assert tc.e_moneta({"contractType": "PERPETUAL"})
    assert not tc.e_moneta({"contractType": "TRADIFI_PERPETUAL", "underlyingType": "EQUITY"})
    assert not tc.e_moneta({"contractType": "PERPETUAL", "underlyingType": "PREMARKET"})
    assert not tc.e_moneta({"contractType": "PERPETUAL", "underlyingType": "COIN", "underlyingSubType": ["TradFi"]})
    info = {"symbols": [{"symbol": "BEUSDT", "quoteAsset": "USDT", "contractType": "TRADIFI_PERPETUAL",
                         "underlyingType": "EQUITY", "onboardDate": 1, "status": "TRADING"},
                        {"symbol": "BTCUSDC", "quoteAsset": "USDC", "contractType": "PERPETUAL"}]}
    nuovi = tc.tipi(info)
    assert nuovi == {"BEUSDT": {"underlyingType": "EQUITY", "contractType": "TRADIFI_PERPETUAL", "onboardDate": 1}}
    assert set(tc.unisci({"VECCHIAUSDT": {"contractType": "PERPETUAL"}}, nuovi)) == {"BEUSDT", "VECCHIAUSDT"}


def test_tipi_scritti_e_riletti(tmp_path):
    f = tmp_path / "tipi.json"
    tc.scrivi({"AUSDT": {"contractType": "PERPETUAL", "onboardDate": 5}, "BUSDT": {"underlyingType": "EQUITY"}}, f, "2026-11-27")
    assert tc.leggi(f) == {"AUSDT": {"contractType": "PERPETUAL", "onboardDate": 5}, "BUSDT": {"underlyingType": "EQUITY"}}
    assert json.loads(f.read_text())["aggiornato"] == "2026-11-27"
    assert tc.leggi(tmp_path / "manca.json") == {}


def test_contratti_non_monete_tolti_dal_loro_onboard_restano_le_vecchie_monete(dati):
    giorni = list(range(sc.giorno(2026, 9, 1), sc.giorno(2026, 11, 1)))
    onb = sc.giorno(2026, 10, 21)
    # MDTUSDT: una moneta fino al 12 ottobre, poi l'azione Medtronic dal 21 ottobre; BEUSDT: solo un'azione; XUSDT: una moneta
    mdt = [g for g in giorni if g <= sc.giorno(2026, 10, 12) or g >= onb]
    _candele(dati, "MDTUSDT", mdt, [0.06 if g < onb else 95.0 for g in mdt], [5e6] * len(mdt))
    _candele(dati, "BEUSDT", [g for g in giorni if g >= onb], [40.0] * len([g for g in giorni if g >= onb]),
             [5e6] * len([g for g in giorni if g >= onb]))
    _candele(dati, "XUSDT", giorni, [1.0] * len(giorni), [5e6] * len(giorni))
    azione = {"contractType": "TRADIFI_PERPETUAL", "underlyingType": "EQUITY", "onboardDate": onb * G + 3_600_000}
    tipi = {"MDTUSDT": azione, "BEUSDT": azione, "XUSDT": {"contractType": "PERPETUAL", "underlyingType": "COIN",
                                                         "onboardDate": giorni[0] * G}}
    pan = sc.costruisci_pannello(["BEUSDT", "MDTUSDT", "XUSDT"], log=lambda x: None, tipi=tipi)
    assert pan["simboli"] == ["MDTUSDT", "XUSDT"]
    j = pan["simboli"].index("MDTUSDT")
    ok = np.flatnonzero(np.isfinite(pan["close"][:, j])) + pan["t0"]
    assert ok.min() == giorni[0] and ok.max() == sc.giorno(2026, 10, 12)
    assert pan["non_monete"] == {"BEUSDT": "2026-10-21", "MDTUSDT": "2026-10-21"}


# ---------------------------------------------------------------------------
# motore-4: un simbolo rilanciato e il controllo delle aperture
# ---------------------------------------------------------------------------

def _lit(dati):
    """LITUSDT come nell'archivio: scambi fino al 31 gennaio 2025, poi 325 giorni a volume zero col prezzo fermo a 0,592, e il
    contratto nuovo dal 23 dicembre 2025 a 3,734."""
    vivi = list(range(sc.giorno(2025, 1, 1), sc.giorno(2025, 2, 1)))
    morti = list(range(sc.giorno(2025, 2, 1), sc.giorno(2025, 12, 23)))
    nuovi = list(range(sc.giorno(2025, 12, 23), sc.giorno(2026, 1, 20)))
    _candele(dati, "LITUSDT", vivi + morti + nuovi, [0.6] * len(vivi) + [0.592] * len(morti) + [3.734] * len(nuovi),
             [2e6] * len(vivi) + [0.0] * len(morti) + [9e6] * len(nuovi))
    return {"LITUSDT": {"contractType": "PERPETUAL", "underlyingType": "COIN", "onboardDate": _ms(2025, 12, 23, 9)}}


def test_lit_rilanciato_diventa_un_contratto_nuovo(dati):
    pan = sc.costruisci_pannello(["LITUSDT"], log=lambda x: None, tipi=_lit(dati), separa_rilanci=True)
    assert pan["simboli"] == ["LITUSDT", "LITUSDT_prima_del_2025-12-23"] and pan["rilanci"] == {"LITUSDT": "2025-12-23"}
    nuovo, vecchio = (np.isfinite(pan["close"][:, j]) for j in (0, 1))
    assert np.flatnonzero(nuovo)[0] + pan["t0"] == sc.giorno(2025, 12, 23)   # i 200 giorni di vita contano da qui
    assert np.flatnonzero(vecchio)[-1] + pan["t0"] == sc.giorno(2025, 12, 22)
    r = sc.rendimenti(pan)
    assert r[sc.giorno(2025, 12, 22) - pan["t0"], 1] == 0.0 and np.abs(r).max() < 0.02   # niente salto finto del +531%
    assert sc.aperture_lontane(pan) == []


def test_senza_il_tipo_il_salto_si_vede_nel_controllo_dei_dati(dati):
    _lit(dati)
    pan = sc.costruisci_pannello(["LITUSDT"], log=lambda x: None, tipi={}, separa_rilanci=True)
    assert pan["simboli"] == ["LITUSDT"] and pan["rilanci"] == {} and pan["rilanci_non_separati"] == {}
    al = sc.aperture_lontane(pan)
    assert len(al) == 1 and al[0]["simbolo"] == "LITUSDT" and al[0]["giorno"] == "2025-12-23"
    assert al[0]["variazione"] == pytest.approx(3.734 / 0.592 - 1, abs=1e-4)


def test_onboard_dopo_la_prima_candela_senza_giorni_morti_non_e_un_rilancio(dati):
    giorni = list(range(sc.giorno(2025, 1, 1), sc.giorno(2025, 3, 1)))
    _candele(dati, "YUSDT", giorni, [1.0] * len(giorni), [5e6 if g != giorni[30] else 0.0 for g in giorni])
    tipi = {"YUSDT": {"contractType": "PERPETUAL", "underlyingType": "COIN", "onboardDate": giorni[35] * G}}
    pan = sc.costruisci_pannello(["YUSDT"], log=lambda x: None, tipi=tipi, separa_rilanci=True)
    assert pan["simboli"] == ["YUSDT"] and np.isfinite(pan["close"][:, 0]).sum() == len(giorni)


# ritocco del 27 novembre 2026 (controllo indipendente dell'audit): le colonne <SIMBOLO>_prima_del_<giorno> si leggevano per nome
# in scarico_metrics e undicesima.pannello_metrics (1.430 richieste a vuoto, pkl vuoti, KeyError 'oi_valore_fine', paper fermo).
# Secondo ritocco: quei lettori ed esecuzione.ore_di passano da simbolo_base e scarico_metrics scrive il file di ogni colonna
# vecchia (per quattordicesima._taker_ls, che legge per nome); la separazione e' accesa.

def test_la_separazione_e_accesa_coi_lettori_del_paper_che_usano_simbolo_base(dati):
    """Il pannello come lo costruisce il paper separa LIT, e i lettori per nome del giro del mattino passano da simbolo_base."""
    from research.programma6 import esecuzione as es
    from research.programma6 import scarico_metrics as smx
    from research.programma6 import undicesima as un
    assert sc.SEPARA_RILANCI is True
    pan = sc.costruisci_pannello(["LITUSDT"], log=lambda x: None, tipi=_lit(dati))
    assert pan["simboli"] == ["LITUSDT", "LITUSDT_prima_del_2025-12-23"] and pan["rilanci_non_separati"] == {}
    for f in (smx.giorni_che_servono, smx.colonne_vecchie, un.pannello_metrics, es.ore_di):
        assert "simbolo_base" in f.__code__.co_names, f.__name__
    assert "colonne_vecchie" in smx.main.__code__.co_names


def test_spenta_i_rilanci_restano_uniti_e_si_dicono(dati):
    pan = sc.costruisci_pannello(["LITUSDT"], log=lambda x: None, tipi=_lit(dati), separa_rilanci=False)
    assert pan["simboli"] == ["LITUSDT"] and not any(sc.SUFFISSO_VECCHIO in s for s in pan["simboli"])
    assert pan["rilanci"] == {} and pan["rilanci_non_separati"] == {"LITUSDT": "2025-12-23"}
    assert [x["giorno"] for x in sc.aperture_lontane(pan)] == ["2025-12-23"]      # il salto resta segnalato


def test_simbolo_base_dei_file_di_ogni_colonna():
    rilanci = {"LITUSDT": "2025-12-23"}
    assert sc.simbolo_base("LITUSDT_prima_del_2025-12-23", rilanci) == ("LITUSDT", None, sc.giorno(2025, 12, 23))
    assert sc.simbolo_base("LITUSDT_prima_del_2025-12-23") == ("LITUSDT", None, sc.giorno(2025, 12, 23))
    assert sc.simbolo_base("LITUSDT", rilanci) == ("LITUSDT", sc.giorno(2025, 12, 23), None)
    assert sc.simbolo_base("LITUSDT") == ("LITUSDT", None, None)
    assert sc.simbolo_base("BTCUSDT", rilanci) == ("BTCUSDT", None, None)


def test_rifai_funding_di_un_pannello_coi_rilanci_separati(dati):
    """rifai_funding (che ora passa da simbolo_base) da' lo stesso funding del pannello costruito, anche alle due parti di LIT."""
    tipi = _lit(dati)
    giorni = range(sc.giorno(2025, 1, 1), sc.giorno(2026, 1, 20))
    righe = [(g * G + h * 3_600_000, 0.0001) for g in giorni for h in (0, 8, 16)]
    for mese in sorted({sc.data(g)[:7] for g in giorni}):
        _funding_archivio(dati, "LITUSDT", mese, [r for r in righe if sc.data(r[0] // G)[:7] == mese])
    pan = sc.costruisci_pannello(["LITUSDT"], log=lambda x: None, tipi=tipi, separa_rilanci=True)
    F, M = pan["funding"].copy(), pan["funding_stimato"].copy()
    pan["funding"][:] = 0.0
    del pan["funding_stimato"]
    sc.rifai_funding(pan)
    assert np.array_equal(pan["funding"], F) and np.array_equal(pan["funding_stimato"], M)
    assert pan["funding"][:, 1].sum() > 0 and pan["funding"][:, 0].sum() > 0


def test_il_pannello_dice_i_giorni_tolti_in_coda(dati):
    giorni = list(range(sc.giorno(2026, 11, 1), sc.giorno(2026, 11, 20)))
    for s in ("AUSDT", "BUSDT", "CUSDT"):
        _candele(dati, s, giorni if s != "CUSDT" else giorni[:-2], [1.0] * len(giorni), [5e6] * len(giorni))
    _candele(dati, "DUSDT", giorni[:-2], [1.0] * (len(giorni) - 2), [5e6] * (len(giorni) - 2))
    righe = []
    pan = sc.costruisci_pannello(["AUSDT", "BUSDT", "CUSDT", "DUSDT"], log=righe.append, tipi={})
    assert pan["giorni_in_coda_tolti"] == ["2026-11-18", "2026-11-19"]
    assert sc.data(pan["t0"] + pan["close"].shape[0] - 1) == "2026-11-17"
    assert any("tolti 2 giorni in coda pubblicati solo in parte (2026-11-18, 2026-11-19)" in x for x in righe)


def test_il_rapporto_dice_i_giorni_tolti_in_coda_e_i_rilanci_uniti():
    vuoto = {"long": {}, "short": {}, "lunedi": "2026-11-23"}
    base = {"dati_fino_al": "2026-11-23", "funding_stimato_dal": None, "candidate": {},
            "adesso": {"F3": vuoto, "F5": vuoto, "K1": vuoto, "M1": vuoto, "F2": {"lunedi": "2026-11-23", "long": [], "short": []},
                       "C1": {"lunedi": "2026-11-16", "long": [], "short": []}, "A1": {"giorno": "2026-11-23", "pesi": {}}}}
    cd = {"aperture_lontane": [], "non_monete_tolte": 71, "rilanci": {}, "rilanci_non_separati": {"LITUSDT": "2025-12-23"},
          "giorni_in_coda_tolti": ["2026-11-24"]}
    testo = ag.rapporto({**base, "controllo_dati": cd})
    assert "simboli rilanciati tenuti separati: nessuno; simboli rilanciati ancora uniti al vecchio contratto (separazione " \
           "spenta): LITUSDT dal 2025-12-23." in testo
    assert "**Giorni in coda tolti** perché l'archivio li ha pubblicati solo in parte: 1 (2026-11-24)." in testo
    cd["giorni_in_coda_tolti"] = ["2026-11-22", "2026-11-23", "2026-11-24"]
    assert "3 (2026-11-22, 2026-11-23, 2026-11-24). **Più di 2: da controllare**" in ag.rapporto({**base, "controllo_dati": cd})


# ---------------------------------------------------------------------------
# secondo ritocco del 27 novembre 2026: i lettori dei dati sulle posizioni con i rilanci separati
# ---------------------------------------------------------------------------

VECCHIO_LIT = "LITUSDT_prima_del_2025-12-23"
RILANCIO_LIT = sc.giorno(2025, 12, 23)


def test_giorni_che_servono_chiede_la_parte_vecchia_col_simbolo_di_base(monkeypatch):
    from research.programma6 import scarico_metrics as smx
    from research.programma6 import terza as te
    t0, T = RILANCIO_LIT - 400, 450
    simboli = ["BTCUSDT", "LITUSDT", VECCHIO_LIT]
    lunedi = np.array([g for g in range(t0 + 40, t0 + T) if (g + 3) % 7 == 0], dtype=np.int64)
    U = np.zeros((len(lunedi), 3), bool)
    U[:, 0] = True
    U[lunedi < RILANCIO_LIT - 10, 2] = True                      # la vecchia LIT nell'universo fino a poco prima del rilancio
    U[-1, 1] = True                                              # la nuova nell'ultima settimana
    monkeypatch.setattr(te, "pannello_settimane", lambda pan, **k: {"lunedi": lunedi, "U": U, "simboli": simboli})
    monkeypatch.setattr(smx, "DAL", t0)
    pan = {"t0": t0, "close": np.ones((T, 3)), "simboli": simboli, "rilanci": {"LITUSDT": "2025-12-23"}}
    servono = smx.giorni_che_servono(pan)
    assert sorted(servono) == ["BTCUSDT", "LITUSDT"]             # nessun nome che l'archivio non conosce
    lit = servono["LITUSDT"]
    assert any(g < RILANCIO_LIT for g in lit) and any(g >= RILANCIO_LIT for g in lit)
    assert max(g for g in lit if g < RILANCIO_LIT) < RILANCIO_LIT - 10     # della parte vecchia solo i giorni prima del rilancio


def test_una_moneta_senza_nessun_file_non_scrive_un_pkl_vuoto(tmp_path, monkeypatch):
    from research.programma6 import scarico_metrics as smx
    monkeypatch.setattr(smx, "DATI", tmp_path)
    monkeypatch.setattr(smx, "un_giorno", lambda s, g: (g, None, None))      # come un 404 per ogni giorno
    r = smx.una_moneta("NUOVAUSDT", {smx.DAL + 1, smx.DAL + 2})
    assert r["giorni"] == 0 and not list(tmp_path.glob("*.pkl"))


def _metrics(giorni, valore):
    return pd.DataFrame({"oi_valore_fine": valore, "count_toptrader_long_short_ratio": 1.0,
                         "sum_toptrader_long_short_ratio": 1.0, "count_long_short_ratio": 1.0,
                         "sum_taker_long_short_vol_ratio": valore}, index=list(giorni))


def test_pannello_metrics_parte_vecchia_dal_simbolo_di_base_e_pkl_vuoti_saltati(tmp_path, monkeypatch):
    from research.programma6 import undicesima as un
    monkeypatch.setattr(un, "DATI_M", tmp_path)
    t0, T = RILANCIO_LIT - 20, 40
    pd.concat([_metrics(range(t0, RILANCIO_LIT), 1.0), _metrics(range(RILANCIO_LIT, t0 + T), 2.0)]).to_pickle(tmp_path / "LITUSDT.pkl")
    pd.DataFrame().to_pickle(tmp_path / "VUOTAUSDT.pkl")                     # come lo scriveva scarico_metrics prima
    pan = {"t0": t0, "close": np.ones((T, 3)), "simboli": ["LITUSDT", VECCHIO_LIT, "VUOTAUSDT"],
           "rilanci": {"LITUSDT": "2025-12-23"}}
    pm = un.pannello_metrics(pan)
    r = RILANCIO_LIT - t0
    assert np.all(pm["oi"][:r, 1] == 1.0) and np.all(np.isnan(pm["oi"][r:, 1]))      # la vecchia: solo prima del rilancio
    assert np.all(np.isnan(pm["oi"][:r, 0])) and np.all(pm["oi"][r:, 0] == 2.0)       # la nuova: solo dal rilancio
    assert np.all(np.isnan(pm["oi"][:, 2]))
    # senza rilanci (rilanci uniti, o pannello di prima) si legge come prima: tutto il file col nome della colonna
    pm1 = un.pannello_metrics({"t0": t0, "close": np.ones((T, 1)), "simboli": ["LITUSDT"]})
    assert np.all(pm1["oi"][:r, 0] == 1.0) and np.all(pm1["oi"][r:, 0] == 2.0)


def test_la_colonna_vecchia_ha_il_suo_file_e_i_lettori_per_nome_la_trovano(tmp_path, monkeypatch):
    """scarico_metrics scrive il file della colonna vecchia (il file di base fino al rilancio): quattordicesima._taker_ls, che
    legge per nome, ha per la vecchia LIT gli stessi dati di quando LIT era una colonna sola."""
    from research.programma6 import quattordicesima as q
    from research.programma6 import scarico_metrics as smx
    monkeypatch.setattr(smx, "DATI", tmp_path)
    monkeypatch.setattr(q, "DATI_M", tmp_path)
    t0, T = RILANCIO_LIT - 20, 40
    pd.concat([_metrics(range(t0, RILANCIO_LIT), 1.0), _metrics(range(RILANCIO_LIT, t0 + T), 2.0)]).to_pickle(tmp_path / "LITUSDT.pkl")
    pan = {"t0": t0, "close": np.ones((T, 3)), "simboli": ["BTCUSDT", "LITUSDT", VECCHIO_LIT],
           "rilanci": {"LITUSDT": "2025-12-23"}}
    assert smx.colonne_vecchie(pan) == [VECCHIO_LIT]
    v = pd.read_pickle(tmp_path / f"{VECCHIO_LIT}.pkl")
    assert v.index.max() == RILANCIO_LIT - 1 and len(v) == RILANCIO_LIT - t0
    tk = q._taker_ls(pan)
    r = RILANCIO_LIT - t0
    assert np.all(tk[:r, 2] == 1.0) and np.all(np.isnan(tk[r:, 2])) and np.all(np.isnan(tk[:, 0]))
    assert smx.colonne_vecchie({**pan, "simboli": ["BTCUSDT", "LITUSDT"]}) == []      # niente rilanci, niente file in piu'


def test_una_cartella_col_nome_di_una_colonna_vecchia_non_diventa_un_simbolo(dati):
    giorni = list(range(sc.giorno(2025, 1, 1), sc.giorno(2025, 2, 1)))
    _candele(dati, "XUSDT", giorni, [1.0] * len(giorni), [5e6] * len(giorni))
    _candele(dati, "XUSDT_prima_del_2025-01-20", giorni, [1.0] * len(giorni), [5e6] * len(giorni))
    pan = sc.costruisci_pannello(log=lambda x: None, tipi={})
    assert pan["simboli"] == ["XUSDT"]


def test_ore_di_parte_vecchia_dal_simbolo_di_base_fino_al_rilancio(monkeypatch):
    """esecuzione.ore_di (secondo ritocco del 27 novembre 2026): la colonna vecchia di un rilancio ha le candele a 1 ora del simbolo
    di base fino all'ultima ora prima del rilancio; prima non trovava nessun file e le sue variazioni si contavano a mercato."""
    from research.programma6 import esecuzione as es
    ore = np.arange((RILANCIO_LIT - 2) * 24, (RILANCIO_LIT + 2) * 24)
    letti = []

    def barre(s, intervallo):
        letti.append(s)
        return pd.DataFrame({"minuto": ore * 60, "open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0})

    monkeypatch.setattr(es.d6, "barre", barre)
    monkeypatch.setattr(es.qa, "ore", lambda s: pd.DataFrame())
    vecchio, nuovo = es.ore_di(VECCHIO_LIT), es.ore_di("LITUSDT")
    assert letti == ["LITUSDT", "LITUSDT"]
    assert len(vecchio) == 48 and vecchio.index.max() == RILANCIO_LIT * 24 - 1
    assert len(nuovo) == 96
    monkeypatch.setattr(es.d6, "barre", lambda s, i: pd.DataFrame())
    assert es.ore_di(VECCHIO_LIT).empty                                       # senza file: vuoto, come prima


# secondo controllo indipendente (27 novembre 2026): un perpetuo di pre-mercato su una moneta resta una moneta per la ricerca
# (paper/REGOLE.md, sezione 11: annuncio di moneta senza «TradFi» ne' «Pre-IPO»); il bot (e_moneta) resta com'e'

PREDICT = {"underlyingType": "PREMARKET", "contractType": "PERPETUAL", "underlyingSubType": ["Pre-Market"],
           "onboardDate": 1792916100000}
MOONSHOT = {"underlyingType": "PREMARKET", "contractType": "TRADIFI_PERPETUAL", "underlyingSubType": ["TradFi", "Pre-IPO"],
            "onboardDate": 1790065800000}
OURA = {"underlyingType": "PREMARKET", "contractType": "TRADIFI_PERPETUAL", "underlyingSubType": ["Pre-IPO", "TradFi"],
        "onboardDate": 1790152200000}


def test_la_ricerca_tiene_il_pre_mercato_su_una_moneta_e_toglie_il_pre_ipo():
    assert tc.e_moneta_ricerca(PREDICT) and not tc.e_moneta(PREDICT)
    assert not tc.e_moneta_ricerca(MOONSHOT) and not tc.e_moneta_ricerca(OURA)
    assert not tc.e_moneta_ricerca({"contractType": "PERPETUAL", "underlyingType": "PREMARKET", "underlyingSubType": ["Pre-IPO"]})
    assert not tc.e_moneta_ricerca({"contractType": "PERPETUAL", "underlyingType": "PREMARKET", "underlyingSubType": ["TradFi"]})
    assert not tc.e_moneta_ricerca({"contractType": "TRADIFI_PERPETUAL", "underlyingType": "EQUITY"})
    assert not tc.e_moneta_ricerca({"contractType": "CURRENT_QUARTER", "underlyingType": "COIN"})
    assert tc.e_moneta_ricerca({"contractType": "PERPETUAL", "underlyingType": "COIN"}) and tc.e_moneta_ricerca({"contractType": "PERPETUAL"})


def test_predict_resta_nel_pannello_e_nello_scarico_del_funding_moonshot_e_oura_no(dati):
    giorni = list(range(sc.giorno(2026, 10, 1), sc.giorno(2026, 11, 20)))       # dopo l'onboardDate di MOONSHOT e OURA
    for s in ("PREDICTUSDT", "MOONSHOTUSDT", "OURAUSDT", "XUSDT"):
        _candele(dati, s, giorni, [1.0] * len(giorni), [5e6] * len(giorni))
    tipi = {"PREDICTUSDT": PREDICT, "MOONSHOTUSDT": MOONSHOT, "OURAUSDT": OURA,
            "XUSDT": {"contractType": "PERPETUAL", "underlyingType": "COIN", "onboardDate": giorni[0] * G}}
    pan = sc.costruisci_pannello(log=lambda x: None, tipi=tipi)
    assert pan["simboli"] == ["PREDICTUSDT", "XUSDT"]
    assert set(pan["non_monete"]) == {"MOONSHOTUSDT", "OURAUSDT"}
    j = pan["simboli"].index("PREDICTUSDT")
    assert np.isfinite(pan["close"][:, j]).sum() == len(giorni)
    piano = fa.da_scaricare(dati, tipi=tipi, oggi=datetime(2026, 11, 27, tzinfo=timezone.utc))
    assert set(piano) == {"PREDICTUSDT", "XUSDT"}
