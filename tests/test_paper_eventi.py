"""Il paper di N3 ed E4 nel bot (bot/portafoglio/eventi.py) con le risposte di Binance finte."""
from __future__ import annotations

import pytest

from bot.portafoglio import eventi as ev
from bot.portafoglio.f5 import GIORNO_MS

ORA_MS = 3_600_000
D = 20750                                       # il giorno dell'entrata di N3 nelle prove


class _Binance:
    """Monete con il giorno di vita, il prezzo mark, le candele a 1 ora (massimi), il funding a regolamenti."""

    def __init__(self):
        self.vita = {"BTCUSDT": D - 3000}
        self.mark = {"BTCUSDT": 100_000.0}
        self.massimi = {}                       # simbolo -> {apertura dell'ora: massimo}
        self.chiusure_btc = {}                  # apertura dell'ora -> chiusura del Bitcoin
        self.tasso = {"BTCUSDT": 0.00005}
        self.passo_ore = {}                     # simbolo -> [(da ms, ore fra un regolamento e l'altro)]
        self.info = []                          # la risposta di fundingInfo
        self.adesso_ms = 0

    def moneta(self, s, vita, mark, tasso=0.0001):
        self.vita[s], self.mark[s], self.tasso[s] = vita, mark, tasso

    def _regolamenti(self, s, da):
        passi = self.passo_ore.get(s, [(0, 8)])
        t, out = (da // (8 * ORA_MS)) * 8 * ORA_MS, []
        while t <= self.adesso_ms:
            if t >= da:
                out.append({"symbol": s, "fundingTime": t, "fundingRate": str(self.tasso[s])})
            ore = [o for inizio, o in passi if t >= inizio][-1]
            t += ore * ORA_MS
        return out[:1000]

    def __call__(self, percorso, p):
        if percorso == "/fapi/v1/premiumIndex":
            return [{"symbol": s, "markPrice": str(m)} for s, m in self.mark.items()]
        if percorso == "/fapi/v1/exchangeInfo":
            return {"symbols": [{"symbol": s, "contractType": "PERPETUAL", "quoteAsset": "USDT", "status": "TRADING",
                                 "underlyingType": "COIN", "onboardDate": g * GIORNO_MS + 3600_000}
                                for s, g in self.vita.items()]}
        if percorso == "/fapi/v1/fundingInfo":
            return list(self.info)
        if percorso == "/fapi/v1/fundingRate":
            return self._regolamenti(p["symbol"], int(p["startTime"]))
        if percorso == "/fapi/v1/klines":
            s, da = p["symbol"], int(p["startTime"])
            if p["interval"] == "1d":
                g = da // GIORNO_MS
                return [[g * GIORNO_MS, 1, 1, 1, 1, 1, 0, 5e6]] if g >= self.vita.get(s, g) else []
            ore = sorted(t for t in (self.massimi.get(s) or {}) if t >= da) if s != "BTCUSDT" else \
                sorted(t for t in self.chiusure_btc if t >= da)
            if s == "BTCUSDT":
                return [[t, 0, 0, 0, self.chiusure_btc[t]] for t in ore]
            return [[t, 0, self.massimi[s][t], 0, 0] for t in ore if t <= self.adesso_ms]
        raise AssertionError(percorso)


def _paper(tmp_path, b):
    from bot.core.firebase_client import _InMemoryStore
    fb = _InMemoryStore()
    acceso = tmp_path / "acceso"
    acceso.write_text("si")
    p = ev.PaperEventi(fb, chiedi=b, file_stato=tmp_path / "stato.json", interruttore=acceso, pausa_s=0.0)
    return p, fb


def _tick(p, b, s):
    b.adesso_ms = int(s * 1000)
    p.tick(s)


def test_n3_entra_al_settimo_giorno_ed_esce_alla_protezione(tmp_path):
    b = _Binance()
    b.moneta("NUOVAUSDT", D - 7, 2.0)
    b.moneta("GIOVANEUSDT", D - 6, 3.0)
    b.moneta("VECCHIAUSDT", D - 300, 4.0)
    p, fb = _paper(tmp_path, b)
    _tick(p, b, D * 86400.0 - 3600)                        # il giorno prima, alle 23: niente entrate
    assert p.carica()["aperte"] == {}
    _tick(p, b, D * 86400.0 + 400)                         # 00:06 del giorno D
    aperte = p.carica()["aperte"]
    assert list(aperte) == [f"N3-NUOVAUSDT-{_data(D)}"]
    pos = next(iter(aperte.values()))
    assert pos["p0"] == 2.0 and pos["b0"] == 100_000.0 and pos["quota"] == pytest.approx(500.0)
    # alle 02:00 la moneta tocca +35%: si esce al +30% con l'1% di scarto, il Bitcoin alla chiusura di quell'ora
    ora = D * 24 * ORA_MS + 2 * ORA_MS
    b.massimi["NUOVAUSDT"] = {D * 24 * ORA_MS: 2.1, ora: 2.7}
    b.chiusure_btc[ora] = 101_000.0
    _tick(p, b, D * 86400.0 + 3 * 3600)
    st = p.carica()
    assert st["aperte"] == {} and st["chiuse_n"] == 1
    chiusa = fb.get_rtdb(f"/paper_eventi/chiuse/N3-NUOVAUSDT-{_data(D)}")
    atteso = ev.rendimento(2.0, 2.0 * 1.30 * 1.01, 100_000.0, 101_000.0, 0.0, 0.0)
    assert chiusa["motivo"].startswith("protezione") and chiusa["rendimento"] == pytest.approx(atteso)
    assert st["equity_realizzata"] == pytest.approx(10_000.0 + 500.0 * atteso)


def test_n3_esce_dopo_30_giorni_con_il_funding_delle_due_gambe(tmp_path):
    b = _Binance()
    b.moneta("NUOVAUSDT", D - 7, 2.0, tasso=0.0001)
    p, fb = _paper(tmp_path, b)
    _tick(p, b, D * 86400.0 - 3600)
    _tick(p, b, D * 86400.0 + 400)
    entrata_ms = p.carica()["aperte"][f"N3-NUOVAUSDT-{_data(D)}"]["entrata_ms"]
    b.mark["NUOVAUSDT"], b.mark["BTCUSDT"] = 1.5, 110_000.0
    fine = (D + 30) * 86400.0 + 400
    _tick(p, b, fine)
    chiusa = fb.get_rtdb(f"/paper_eventi/chiuse/N3-NUOVAUSDT-{_data(D)}")
    n = len([t for t in range(0, int(fine * 1000) + 1, 8 * ORA_MS) if entrata_ms < t <= int(fine * 1000)])
    atteso = ev.rendimento(2.0, 1.5, 100_000.0, 110_000.0, 0.0001 * n, 0.00005 * n)
    assert chiusa["motivo"] == "tempo" and chiusa["rendimento"] == pytest.approx(atteso)
    assert chiusa["rendimento"] > 0.25                       # la moneta scende del 25% e il Bitcoin sale del 10%


def test_e4_solo_su_un_intervallo_che_scende_con_funding_positivo(tmp_path):
    b = _Binance()
    b.moneta("CALDAUSDT", D - 400, 5.0, tasso=0.002)
    b.moneta("FREDDAUSDT", D - 400, 6.0, tasso=-0.002)
    b.moneta("GIASCESAUSDT", D - 400, 7.0, tasso=0.002)
    b.info = [{"symbol": "GIASCESAUSDT", "fundingIntervalHours": 4}]   # gia' a 4 ore al primo giro: e' la base
    p, fb = _paper(tmp_path, b)
    t0 = (D - 3) * 86400.0 + 600
    _tick(p, b, t0)
    assert p.carica()["e4_attese"] == [] and p.carica()["e4_eventi"] == []
    # un'ora e mezza dopo CALDA e FREDDA passano a 4 ore; il primo regolamento al passo nuovo e' alle 04:00 del giorno D-2
    cambio = (D - 2) * GIORNO_MS
    for s in ("CALDAUSDT", "FREDDAUSDT"):
        b.passo_ore[s] = [(0, 8), (cambio, 4)]
    b.info += [{"symbol": "CALDAUSDT", "fundingIntervalHours": 4}, {"symbol": "FREDDAUSDT", "fundingIntervalHours": 4}]
    _tick(p, b, (D - 2) * 86400.0 + 5 * 3600)
    st = p.carica()
    assert [e["simbolo"] for e in st["e4_eventi"]] == ["CALDAUSDT"]  # FREDDA ha il funding negativo: no
    assert st["e4_eventi"][0]["giorno_entrata"] == D - 1
    _tick(p, b, (D - 1) * 86400.0 + 400)                     # 00:06 del giorno dopo: entra
    assert list(p.carica()["aperte"]) == [f"E4-CALDAUSDT-{_data(D - 1)}"]
    b.mark["CALDAUSDT"] = 4.0
    _tick(p, b, (D + 6) * 86400.0 + 400)                     # 7 giorni dopo: esce
    st = p.carica()
    assert st["aperte"] == {} and st["chiuse_n"] == 1
    assert fb.get_rtdb(f"/paper_eventi/chiuse/E4-CALDAUSDT-{_data(D - 1)}")["motivo"] == "tempo"


def test_al_massimo_20_aperte(tmp_path):
    b = _Binance()
    for i in range(25):
        b.moneta(f"N{i:02d}USDT", D - 7, 1.0 + i)
    p, fb = _paper(tmp_path, b)
    _tick(p, b, D * 86400.0 - 3600)
    _tick(p, b, D * 86400.0 + 400)
    assert len(p.carica()["aperte"]) == ev.MAX_APERTE
    assert fb.get_rtdb("/paper_eventi/stato")["aperte_n3"] == ev.MAX_APERTE


def test_primo_passo_corto():
    h = ORA_MS
    assert ev.primo_passo_corto([(0, 0.001), (8 * h, 0.001), (16 * h, 0.001)]) == (None, 0)
    assert ev.primo_passo_corto([(0, 0.001), (8 * h, 0.001), (12 * h, 0.002)]) == (12 * h, 1)
    assert ev.primo_passo_corto([(0, 0.001), (8 * h, -0.001), (12 * h, 0.0)]) == (12 * h, -1)   # zero: vale il precedente


def _data(giorno):
    import time
    return time.strftime("%Y%m%d", time.gmtime(giorno * 86400))
