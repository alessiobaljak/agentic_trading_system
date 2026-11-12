"""Il paper di F5 nel bot (bot/portafoglio/f5.py): le regole come la ricerca e il conto del portafoglio simulato."""
from __future__ import annotations

import time

import numpy as np
import pytest

from bot.portafoglio import f5


def _pannello():
    try:
        from research.programma6 import seconda as sc
        return sc.pannello()
    except Exception:  # noqa: BLE001
        return None


def test_regole_come_la_ricerca():
    """Universo, volatilità, funding dei 7 giorni e banda: gli stessi numeri di `terza`, `ottava`, `sesta` e
    `ventiquattresima` sullo stesso pannello, per due lunedì recenti."""
    pan = _pannello()
    if pan is None:
        pytest.skip("pannello della ricerca non disponibile (dati fuori da git)")
    from research.programma6 import ottava as ot
    from research.programma6 import sesta as se
    from research.programma6 import terza as te
    from research.programma6 import ventiquattresima as vq
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    S7 = se.funding_7(pan, lun)
    W = vq.pesi_banda(np.where(np.isfinite(sig), -S7, np.nan), ps["U"], sig)
    sim = pan["simboli"]
    t0 = pan["t0"]
    ok = np.isfinite(pan["close"])
    primo = {s: int(ok[:, j].argmax()) + t0 for j, s in enumerate(sim) if ok[:, j].any()}
    for k in (len(lun) - 3, len(lun) - 2):
        m = int(ps["lunedi"][k])
        giornaliere = {}
        for j, s in enumerate(sim):
            if s not in primo:
                continue
            g = {}
            for d in range(m - 40, m + 1):
                i = d - t0
                if 0 <= i < pan["close"].shape[0] and (np.isfinite(pan["close"][i, j]) or np.isfinite(pan["open"][i, j])):
                    g[d] = (pan["open"][i, j], pan["close"][i, j], np.nan_to_num(pan["quote_volume"][i, j]))
            giornaliere[s] = g
        uni = f5.universo(giornaliere, primo, m)
        attese = {sim[j] for j in np.flatnonzero(ps["U"][k])}
        assert set(uni) == attese
        segnale, sigma = {}, {}
        for s in uni:
            j = sim.index(s)
            sigma[s] = f5.sigma_30({d: v[1] for d, v in giornaliere[s].items()}, m)
            fg = {d: float(pan["funding"][d - t0, j]) for d in range(m - 8, m)}
            segnale[s] = -f5.funding_7(fg, m) if np.isfinite(sigma[s]) else float("nan")
            assert sigma[s] == pytest.approx(sig[k, j], nan_ok=True)
            assert -segnale[s] == pytest.approx(S7[k, j]) or not np.isfinite(sigma[s])
        prima = W[k - 1]
        lunghi = {sim[j] for j in np.flatnonzero(prima > 0)}
        corti = {sim[j] for j in np.flatnonzero(prima < 0)}
        # la banda con gli stessi numeri della ricerca: la ricerca somma il funding con le somme cumulate, che alle parità
        # (molte monete al funding di base) lasciano differenze di arrotondamento che cambiano l'ordine
        esatti = {s: (-S7[k, sim.index(s)] if np.isfinite(sigma[s]) else float("nan")) for s in uni}
        pesi, _, _ = f5.pesi_banda(esatti, sigma, lunghi, corti)
        attesi = {sim[j]: W[k, j] for j in np.flatnonzero(W[k])}
        assert set(pesi) == set(attesi)
        for s, w in pesi.items():
            assert w == pytest.approx(attesi[s])


class _Finto:
    """Le risposte di Binance per 30 monete con prezzi e funding fissati."""

    def __init__(self, lunedi: int):
        self.m = lunedi
        self.prezzo = {f"C{i:02d}USDT": 10.0 + i for i in range(30)}
        self.funding = {s: 0.0001 * (i - 15) for i, s in enumerate(self.prezzo)}

    def __call__(self, percorso: str, p: dict):
        if percorso == "/fapi/v1/exchangeInfo":
            return {"symbols": [{"symbol": s, "contractType": "PERPETUAL", "quoteAsset": "USDT", "status": "TRADING",
                                 "underlyingType": "COIN", "onboardDate": (self.m - 400) * f5.GIORNO_MS}
                                for s in self.prezzo]}
        if percorso == "/fapi/v1/klines":
            s = p["symbol"]
            i = int(s[1:3])
            out = []
            for d in range(self.m - 39, self.m + 1):
                c = self.prezzo[s] * (1 + 0.01 * (i + 1) * (1 if d % 2 else -1) / 30)    # volatilità diverse
                out.append([d * f5.GIORNO_MS, c, c, c, c, 0, 0, 5e6])
            return out
        if percorso == "/fapi/v1/fundingRate":
            s = p["symbol"]
            da = int(p["startTime"])
            tempi = [t for t in range((self.m - 8) * f5.GIORNO_MS, (self.m + 9) * f5.GIORNO_MS, 8 * 3600 * 1000) if t >= da]
            return [{"fundingTime": t, "fundingRate": self.funding[s], "markPrice": self.prezzo[s]}
                    for t in tempi if t <= self.adesso_ms]
        if percorso == "/fapi/v1/premiumIndex":
            return [{"symbol": s, "markPrice": p_} for s, p_ in self.prezzo.items()]
        if percorso == "/fapi/v1/ticker/bookTicker":
            # scarto dello 0,02% (le prime monete) o dello 0,1% (le altre)
            return [{"symbol": s, "bidPrice": str(p_ * (1 - (0.0001 if int(s[1:3]) < 10 else 0.0005))),
                     "askPrice": str(p_ * (1 + (0.0001 if int(s[1:3]) < 10 else 0.0005)))} for s, p_ in self.prezzo.items()]
        if percorso == "/fapi/v1/markPriceKlines":
            # le monete pari scendono sotto il prezzo (il limite di chi compra si esegue), le dispari restano ferme
            s = p["symbol"]
            c = self.prezzo[s]
            basso = c * 0.99 if int(s[1:3]) % 2 == 0 else c
            alto = c * 1.01 if int(s[1:3]) % 2 == 0 else c
            return [[t, c, alto, basso, c, 0, t + 59_999] for t in range(int(p["startTime"]), int(p["endTime"]), 60_000)]
        raise AssertionError(percorso)


def test_paper_ribilancia_il_lunedi_e_conta_costi_e_funding(tmp_path):
    from bot.core.firebase_client import _InMemoryStore
    m = f5.lunedi_di(20750)
    finto = _Finto(m)
    fb = _InMemoryStore()
    acceso = tmp_path / "paper_f5_acceso"
    p = f5.PaperF5(fb, chiedi=finto, file_stato=tmp_path / "stato.json", interruttore=acceso, pausa_s=0.0)
    finto.adesso_ms = (m - 3) * f5.GIORNO_MS
    p.tick((m - 3) * 86400.0)                                   # spento: niente
    assert fb.get_rtdb("/paper_f5/stato") is None
    acceso.write_text("si")
    p.tick((m - 3) * 86400.0 + 600)                             # giovedì: aspetta il lunedì, ma fa la prova a secco
    assert fb.get_rtdb("/paper_f5/stato")["stato"].startswith("in attesa")
    prova = fb.get_rtdb("/paper_f5/prova")
    assert prova["universo"] == 30 and prova["long"] > 0 and prova["short"] > 0
    assert not (tmp_path / "stato.json").exists()               # la prova non opera
    p._ultimo_tentativo = 0.0
    now = m * 86400.0 + 400
    finto.adesso_ms = int(now * 1000)
    p.tick(now)
    st = p.carica()
    assert st["ultimo_lunedi"] == m and st["universo"] == 30
    pesi = st["pesi"]
    assert sum(w for w in pesi.values() if w > 0) == pytest.approx(1.0)
    assert sum(w for w in pesi.values() if w < 0) == pytest.approx(-1.0)
    assert all(pesi[s] < 0 for s in ("C29USDT", "C28USDT"))   # chi ha il funding più alto va short
    # fino al controllo dell'ora si conta lo 0,02% del limite; accanto il costo tutto a mercato
    provvisorio = sum(abs(q) * finto.prezzo[s] * f5.MAKER for s, q in st["quantita"].items())
    a_mercato = sum(abs(q) * finto.prezzo[s] * (f5.TAKER + f5.scarto(s)) for s, q in st["quantita"].items())
    assert st["equity_rif"] == pytest.approx(f5.CAPITALE - provvisorio)
    assert st["ordini"]["costo_a_mercato"] == pytest.approx(a_mercato) and len(st["ordini"]["variazioni"]) == len(st["quantita"])
    p.tick(now + 1800)                                          # l'ora non e' passata: gli ordini restano
    assert p.carica().get("ordini")
    p.tick(now + 3700)                                          # passata: le pari eseguite a limite, le dispari a mercato
    st = p.carica()
    assert "ordini" not in st
    pari = {s for s in st["quantita"] if int(s[1:3]) % 2 == 0}
    costo = sum(abs(q) * finto.prezzo[s] * (f5.MAKER if s in pari else f5.TAKER + f5.scarto(s)) for s, q in st["quantita"].items())
    assert st["equity_rif"] == pytest.approx(f5.CAPITALE - costo)
    assert st["limite_eseguite"] == len(pari) and st["limite_variazioni"] == len(st["quantita"])
    assert st["costi_a_mercato_totali"] == pytest.approx(a_mercato) and costo < a_mercato
    assert fb.get_rtdb("/paper_f5/ribilanciamenti/" + time.strftime("%Y-%m-%d", time.gmtime(m * 86400)) + "/limite")["eseguite"] == len(pari)
    # mercoledì: i prezzi salgono del 10% (neutro: long e short si compensano) e passano 6 regolamenti del funding
    for s in finto.prezzo:
        finto.prezzo[s] *= 1.10
    later = now + 2 * 86400
    finto.adesso_ms = int(later * 1000)
    p.tick(later)
    st2 = p.carica()
    pagato = sum(q * finto.prezzo[s] * finto.funding[s] * 6 for s, q in st["quantita"].items())
    assert st2["funding_totale"] == pytest.approx(pagato)
    assert pagato < 0                                            # F5 incassa: short chi paga, long chi riceve
    e = fb.get_rtdb("/paper_f5/stato")["equity"]
    atteso = st["equity_rif"] + sum(q * finto.prezzo[s] * (1 - 1 / 1.10) for s, q in st["quantita"].items()) - pagato
    assert e == pytest.approx(atteso, abs=0.01)


def test_banda_di_partenza_dal_paper_di_ricerca(tmp_path):
    import json
    m = f5.lunedi_di(20750)
    pr = tmp_path / "paper.json"
    p = f5.PaperF5(None, chiedi=lambda *a: None, file_stato=tmp_path / "s.json", interruttore=tmp_path / "x", pausa_s=0.0)
    p.paper_ricerca = pr
    assert p.banda_di_partenza(m) == {}                         # il file non c'e'
    import time
    prima = time.strftime("%Y-%m-%d", time.gmtime((m - 7) * 86400))
    pr.write_text(json.dumps({"adesso": {"F5": {"lunedi": prima, "long": {"AUSDT": 0.5, "BUSDT": 0.5}, "short": {"CUSDT": -1.0}}}}))
    assert p.banda_di_partenza(m) == {"lunghi": ["AUSDT", "BUSDT"], "corti": ["CUSDT"]}
    assert p.banda_di_partenza(m + 7) == {}                     # di un'altra settimana: non si usa


def test_esito_limite_come_la_ricerca():
    from research.programma6 import cinquantaseiesima as cs
    c = [[100.0, 100.5, 99.8, 100.2], [100.2, 100.4, 100.1, 101.0]]
    # compra 2 unita' a 100: il minimo 99,8 va sotto -> eseguito a limite
    assert f5.esito_limite(2.0, 100.0, c, 0.0007) == (pytest.approx(2 * 100 * f5.MAKER), True)
    # vende 2 unita' a 101: il massimo 100,5 non va sopra -> a mercato alla chiusura 101,0 (nessun movimento contro)
    costo, preso = f5.esito_limite(-2.0, 101.0, c, 0.0007)
    assert not preso and costo == pytest.approx(2 * 101 * 0.0007)
    # vende a 100,6: non eseguito, chiude a 101,0: si vende piu' in alto, il movimento e' a favore
    costo, _ = f5.esito_limite(-2.0, 100.6, c, 0.0007)
    assert costo == pytest.approx(2 * 100.6 * 0.0007 - 2 * 0.4)
    # stesso conto della ricerca (per unita' di peso)
    r, _ = cs.costo_limite(100.6, 100.5, 99.8, 101.0, False, 0.0007)
    assert costo == pytest.approx(2 * 100.6 * r)
    assert f5.esito_limite(1.0, 50.0, [], 0.0007) == (pytest.approx(50 * 0.0007), False)


def test_senza_il_regolamento_delle_00_si_aspetta(tmp_path):
    m = f5.lunedi_di(20750)
    finto = _Finto(m)
    p = f5.PaperF5(None, chiedi=finto, file_stato=tmp_path / "s.json", interruttore=tmp_path / "x", pausa_s=0.0)
    finto.adesso_ms = m * f5.GIORNO_MS - 1                      # il regolamento delle 00:00 del lunedi' non c'e' ancora
    assert p.pesi_del_lunedi(m, {}) is None
    finto.adesso_ms = m * f5.GIORNO_MS + 300_000                # pubblicato: si decide
    assert p.pesi_del_lunedi(m, {}) is not None


def test_g1_decide_ogni_giorno(tmp_path):
    from bot.core.firebase_client import _InMemoryStore
    m = f5.lunedi_di(20750)
    finto = _Finto(m)
    fb = _InMemoryStore()
    acceso = tmp_path / "paper_g1_acceso"
    acceso.write_text("si")
    p = f5.PaperG1(fb, chiedi=finto, file_stato=tmp_path / "g1.json", interruttore=acceso, pausa_s=0.0)
    # martedi' alle 10:00, senza stato: non parte (la prima decisione si prende vicino alle 00:00), fa la prova a secco
    now = (m + 1) * 86400.0 + 36000
    finto.adesso_ms = int(now * 1000)
    p.tick(now)
    assert not (tmp_path / "g1.json").exists() and fb.get_rtdb("/paper_g1/prova")["universo"] == 30
    assert fb.get_rtdb("/paper_f5/stato") is None                # scrive solo nel suo ramo
    # mercoledi' alle 00:06: parte
    p._ultimo_tentativo = 0.0
    now = (m + 2) * 86400.0 + 360
    finto.adesso_ms = int(now * 1000)
    p.tick(now)
    st = p.carica()
    assert st["ultimo_lunedi"] == m + 2 and st["universo"] == 30 and st["ordini"]["variazioni"]
    # giovedi' alle 00:06: decide di nuovo (prima chiude gli ordini limite di ieri)
    p._ultimo_tentativo = 0.0
    now = (m + 3) * 86400.0 + 360
    finto.adesso_ms = int(now * 1000)
    p.tick(now)
    st2 = p.carica()
    assert st2["ultimo_lunedi"] == m + 3 and st2["limite_variazioni"] == len(st["ordini"]["variazioni"])
    assert fb.get_rtdb("/paper_g1/ribilanciamenti/" + time.strftime("%Y-%m-%d", time.gmtime((m + 2) * 86400)))["universo"] == 30
    rib = fb.get_rtdb("/paper_g1/ribilanciamenti/" + time.strftime("%Y-%m-%d", time.gmtime((m + 2) * 86400)))
    assert rib["funding_medio_7"] is not None and abs(rib["funding_medio_7"]) < 0.1      # il funding medio dell'universo (idea 45)
    # il diario per la dashboard (3 nov 2026): le entrate e le uscite del ribilancio, e il valore e le posizioni del giorno
    assert rib["entrate"] == rib["long"] + rib["short"] and rib["uscite"] == 0          # il primo ribilancio parte da zero
    oggi = fb.get_rtdb("/paper_g1/diario/" + time.strftime("%Y-%m-%d", time.gmtime(now)))
    assert oggi["equity"] > 0 and oggi["long"] + oggi["short"] > 0
    assert fb.get_rtdb("/paper_g1/prova")["funding_medio_7"] is not None
    scarto = fb.get_rtdb("/misure/scarto/" + time.strftime("%Y-%m-%d", time.gmtime(now)))
    assert len(scarto["per_moneta"]) == 30 and set(scarto["fasce"]) == {"1-10", "11-50"}
    assert all(v == pytest.approx(0.0002) or v == pytest.approx(0.001) for v in scarto["per_moneta"].values())


def test_g11_segnale_fresco_come_la_ricerca():
    m = 20750
    # A: funding basso sui 7 giorni e ieri; B: in mezzo; C: alto sui 7 giorni ma basso ieri
    f = {"A": {d: -0.001 for d in range(m - 7, m)}, "B": {d: 0.0001 for d in range(m - 7, m)},
         "C": {**{d: 0.002 for d in range(m - 7, m - 1)}, m - 1: -0.002}, "D": None}
    p = f5.PaperG11(None, chiedi=lambda *a: None, file_stato="/tmp/non_usato.json", interruttore="/tmp/non_esiste", pausa_s=0.0)
    s = p.segnali(f, m)
    # ranghi di −funding_7: A +0,5, B 0, C −0,5; di −funding di ieri: A 0, B −0,5, C +0,5 -> A 0,25, B −0,25, C 0
    assert s["A"] == pytest.approx(0.25) and s["B"] == pytest.approx(-0.25) and s["C"] == pytest.approx(0.0)
    assert np.isnan(s["D"])
    assert f5.PaperG1(None, chiedi=lambda *a: None).segnali(f, m)["C"] == pytest.approx(-0.010)   # G1: −funding dei 7 giorni (6 × 0,2% − 0,2%)


def test_monete_in_chiusura_fuori_dall_universo(tmp_path, monkeypatch):
    m = f5.lunedi_di(20750)
    finto = _Finto(m)
    vero = finto.__call__

    def chiedi(percorso, p):
        r = vero(percorso, p)
        if percorso == "/fapi/v1/exchangeInfo":
            for x in r["symbols"]:
                if x["symbol"] == "C29USDT":
                    x["deliveryDate"] = (m + 3) * f5.GIORNO_MS
        return r
    monkeypatch.setattr(f5.time, "time", lambda: m * 86400.0 + 400)
    finto.adesso_ms = m * f5.GIORNO_MS + 400_000
    p = f5.PaperF5(None, chiedi=chiedi, file_stato=tmp_path / "s.json", interruttore=tmp_path / "x", pausa_s=0.0)
    pesi, lunghi, corti, n = p.pesi_del_lunedi(m, {})
    assert n == 29 and "C29USDT" not in pesi


def test_g1n_beta_e_scalatura_come_la_ricerca():
    """`beta_delle_monete` e `scala_neutra` del bot danno gli stessi numeri di `programma7.ventiquattresima` su un pannello sintetico."""
    from research.programma7 import ventiquattresima as f5n
    rng = np.random.default_rng(7)
    T, S = 130, 12
    simboli = [f"M{j}USDT" for j in range(S)]
    mercato = rng.normal(0, 0.03, T)
    beta_vero = rng.uniform(0.3, 1.8, S)
    r = mercato[:, None] * beta_vero[None, :] + rng.normal(0, 0.02, (T, S))
    close = 100 * np.cumprod(1 + r, axis=0)
    close[:T - 30, 3] = np.nan                                   # una moneta con 29 rendimenti nei 90 giorni: beta 1 nella ricerca e nel bot
    pan = {"close": close, "simboli": simboli, "t0": 20000}
    m = 20000 + T - 1                                            # il giorno di decisione: i rendimenti fino a m-1
    U = np.ones((1, S), bool)
    U[0, 5] = False                                              # una moneta fuori dall'universo
    attesi = f5n.beta_delle_monete(pan, U, np.array([m - pan["t0"]]))[0]
    uni = [s for j, s in enumerate(simboli) if U[0, j]]
    chiusure = {s: {pan["t0"] + i: float(close[i, j]) for i in range(T) if np.isfinite(close[i, j])} for j, s in enumerate(simboli)}
    beta = f5.beta_delle_monete(chiusure, uni, m)
    for j, s in enumerate(simboli):
        if U[0, j]:
            assert beta[s] == pytest.approx(attesi[j], abs=1e-9), s
    assert beta[simboli[3]] == 1.0                               # meno di 45 giorni: 1
    # la scalatura: stessi a, b della ricerca
    W = np.zeros((1, S))
    W[0, [0, 1, 2]] = [0.5, 0.3, 0.2]
    W[0, [6, 7, 8, 9]] = [-0.4, -0.3, -0.2, -0.1]
    WN, a, b, bl, bs = f5n.scala_neutra(W, np.array([[attesi[j] for j in range(S)]]))
    pesi = {s: float(W[0, j]) for j, s in enumerate(simboli) if W[0, j] != 0}
    pesi_n, a2, b2, bl2, bs2 = f5.scala_neutra(pesi, beta)
    assert (a2, b2, bl2, bs2) == pytest.approx((a[0], b[0], bl[0], bs[0]), abs=1e-9)
    for j, s in enumerate(simboli):
        assert pesi_n.get(s, 0.0) == pytest.approx(WN[0, j], abs=1e-9)
    # un lato solo: niente scalatura
    assert f5.scala_neutra({"A": 0.5, "B": 0.5}, {"A": 1.2, "B": 0.8})[1:3] == (1.0, 1.0)


def test_g1n_scala_i_pesi_di_g1(tmp_path, monkeypatch):
    """PaperG1N prende i pesi di G1 e li scala con il beta; la neutralita' finisce nel record del ribilancio."""
    m = 20800
    simboli = ["AUSDT", "BUSDT", "CUSDT", "DUSDT"]
    rng = np.random.default_rng(1)
    mercato = rng.normal(0, 0.03, 100)
    betas = {"AUSDT": 1.6, "BUSDT": 1.4, "CUSDT": 0.6, "DUSDT": 0.4}
    giornaliere = {}
    for s in simboli:
        c = 100 * np.cumprod(1 + betas[s] * mercato + rng.normal(0, 0.001, 100))
        giornaliere[s] = {m - 100 + i: (float(c[i]), float(c[i]), 1e7) for i in range(100)}
    p = f5.PaperG1N(None, chiedi=lambda *a: None, file_stato=tmp_path / "g1n.json", interruttore=tmp_path / "no", pausa_s=0.0)
    pesi_g1 = {"AUSDT": 0.5, "BUSDT": 0.5, "CUSDT": -0.5, "DUSDT": -0.5}

    def finto(self, m_, st):
        self._ultimo_universo = list(simboli)
        self._ultime_giornaliere = giornaliere
        return dict(pesi_g1), {"AUSDT", "BUSDT"}, {"CUSDT", "DUSDT"}, 4
    monkeypatch.setattr(f5.PaperG1, "pesi_del_lunedi", finto)
    pesi, lunghi, corti, n = p.pesi_del_lunedi(m, {})
    # il lato long ha beta alto (1,5) e lo short basso (0,5): il long si riduce (a = 2·0,5/2 = 0,5), lo short cresce (b = 1,5)
    assert p._neutralita["a"] == pytest.approx(0.5, abs=0.05) and p._neutralita["b"] == pytest.approx(1.5, abs=0.05)
    assert pesi["AUSDT"] == pytest.approx(0.5 * p._neutralita["a"], abs=1e-4)      # a e b nel record sono arrotondati a 4 decimali
    assert pesi["CUSDT"] == pytest.approx(-0.5 * p._neutralita["b"], abs=1e-4)
    assert sum(w * betas[s] for s, w in pesi.items()) == pytest.approx(0.0, abs=0.1)
    assert p.RAMO == "/paper_g1n" and p.giorno_di_decisione(m) == m


# ---- il conto del funding (12 novembre 2026): le ipotesi del confronto con il demo, gate2/reports/2026-11-12-G1-funding-commissioni.md ----
ORA_MS = 3_600_000
G = 20750 * f5.GIORNO_MS                        # 2026-10-24 00:00 UTC


class _Funding:
    """Solo `/fapi/v1/fundingRate`: i regolamenti di ogni moneta, ognuno visibile da quando Binance lo pubblica (``ritardo_ms``)."""

    def __init__(self):
        self.righe, self.adesso_ms = {}, 0

    def regola(self, s, t, tasso, mark=10.0, ritardo_ms=0):
        self.righe.setdefault(s, []).append((t, tasso, mark, t + ritardo_ms))

    def __call__(self, percorso, p):
        assert percorso == "/fapi/v1/fundingRate"
        return [{"fundingTime": t, "fundingRate": r, "markPrice": str(mk)} for t, r, mk, pub in sorted(self.righe.get(p["symbol"], []))
                if t >= int(p["startTime"]) and pub <= self.adesso_ms][: int(p["limit"])]


def _paper_del_funding(tmp_path, classe=f5.PaperF5, fb=None):
    finto = _Funding()
    return classe(fb, chiedi=finto, file_stato=tmp_path / "s.json", interruttore=tmp_path / "x", pausa_s=0.0), finto


def _stato_del_funding(quantita, base_ms):
    return {"quantita": dict(quantita), "prezzi_rif": {s: 10.0 for s in quantita}, "funding_fino_ms": base_ms,
            "funding_dal_rif": 0.0, "funding_totale": 0.0, "equity_rif": f5.CAPITALE}


def _conta(p, finto, st, adesso_ms):
    finto.adesso_ms = adesso_ms
    p._funding_regolati(st, {}, adesso_ms / 1000)


@pytest.mark.parametrize("ms_di_b", [0, -3])
def test_funding_a_un_regolamento_pubblicato_dopo_quello_di_un_altra_moneta_non_si_perde(tmp_path, ms_di_b):
    """Ipotesi (a): alle 08:05 Binance ha pubblicato le 08:00 di A ma non ancora quelle di B (stessa ora in millisecondi, o qualche
    millisecondo prima). Prima si leggeva dal massimo di tutte le monete e B si perdeva; ora ogni moneta dal suo punto."""
    p, finto = _paper_del_funding(tmp_path)
    st = _stato_del_funding({"AUSDT": -100.0, "BUSDT": -100.0}, G + 5 * 60_000)
    finto.regola("AUSDT", G + 8 * ORA_MS, 0.001)
    finto.regola("BUSDT", G + 8 * ORA_MS + ms_di_b, 0.001, ritardo_ms=10 * 60_000)
    _conta(p, finto, st, G + 8 * ORA_MS + 5 * 60_000)
    assert st["funding_totale"] == pytest.approx(-1.0)          # A: −100 × 10 × 0,001 (lo short incassa)
    _conta(p, finto, st, G + 9 * ORA_MS + 5 * 60_000)
    assert st["funding_totale"] == pytest.approx(-2.0)


def _ribilancia_con(p, st, pesi, now):
    """Il ribilancio vero (`PaperF5.ribilancia`) con pesi e prezzi dati (niente universo da Binance)."""
    p.pesi_del_lunedi = lambda m, s: (pesi, {k for k, w in pesi.items() if w > 0}, {k for k, w in pesi.items() if w < 0}, len(pesi))
    p._prezzi_mark = lambda: {"AUSDT": 10.0, "BUSDT": 10.0, "CUSDT": 10.0}
    p.salva(st)
    return p.ribilancia(int(now // 86400), now, p.carica())


def test_funding_b_il_regolamento_delle_00_pubblicato_dopo_il_ribilancio_si_conta_con_le_quantita_di_prima(tmp_path):
    """Ipotesi (b): al ribilancio delle 00:06 i regolamenti delle 00:00 di A e B non sono ancora pubblicati (D il suo sì). Prima il
    punto letto diventava l'ora del ribilancio e A e B si perdevano; ora restano in sospeso e si contano quando arrivano, con la
    quantità che avevano alle 00:00 (A resta con una quantità diversa, B esce dal portafoglio), una volta sola; le posizioni nuove
    contano dalle 00:06."""
    p, finto = _paper_del_funding(tmp_path)
    st = _stato_del_funding({"AUSDT": -100.0, "BUSDT": -100.0, "DUSDT": -100.0}, G - 16 * ORA_MS + 5 * 60_000)
    finto.regola("AUSDT", G, 0.001, ritardo_ms=7 * 60_000)
    finto.regola("BUSDT", G, 0.002, ritardo_ms=8 * 60_000)
    finto.regola("DUSDT", G, 0.001)
    finto.adesso_ms = G + 6 * 60_000
    st = _ribilancia_con(p, st, {"AUSDT": -0.05, "CUSDT": 0.03}, (G + 6 * 60_000) / 1000)
    assert st["funding_totale"] == pytest.approx(-1.0) and set(st["quantita"]) == {"AUSDT", "CUSDT"}
    assert {s: v[0]["q"] for s, v in st["funding_sospesi"].items()} == {"AUSDT": -100.0, "BUSDT": -100.0}
    q_a, q_c = st["quantita"]["AUSDT"], st["quantita"]["CUSDT"]
    assert q_a == pytest.approx(-0.05 * (f5.CAPITALE + 1.0) / 10, rel=1e-3)
    _conta(p, finto, st, G + ORA_MS + 6 * 60_000)                 # A e B pubblicati alle 00:07 e 00:08, con −100
    assert st["funding_totale"] == pytest.approx(-1.0 - 1.0 - 2.0)
    for s, tasso in (("AUSDT", 0.001), ("BUSDT", 0.001), ("CUSDT", -0.001)):
        finto.regola(s, G + 8 * ORA_MS, tasso)
    for h in (2, 3, 9, 10):
        _conta(p, finto, st, G + h * ORA_MS + 6 * 60_000)
    atteso = -4.0 + q_a * 10 * 0.001 + q_c * 10 * -0.001          # B non c'è più: le sue 08:00 non contano
    assert st["funding_totale"] == pytest.approx(atteso) and "funding_sospesi" not in st


def test_funding_b_il_sospeso_scade_e_non_conta_un_regolamento_dopo_il_ribilancio(tmp_path):
    """Un regolamento in sospeso che non arriva entro ``FUNDING_IN_SOSPESO_MS`` non si aspetta più; un regolamento dopo l'ora del
    ribilancio non si conta mai con la quantità di prima."""
    p, finto = _paper_del_funding(tmp_path)
    st = _stato_del_funding({"BUSDT": -100.0}, G - 16 * ORA_MS)
    finto.adesso_ms = G + 6 * 60_000
    st = _ribilancia_con(p, st, {"AUSDT": -0.05, "CUSDT": 0.03}, (G + 6 * 60_000) / 1000)
    finto.regola("BUSDT", G + ORA_MS, 0.002)                     # B a un'ora: le 01:00 sono dopo il ribilancio
    _conta(p, finto, st, G + ORA_MS + 6 * 60_000)
    assert st["funding_totale"] == 0.0 and "funding_sospesi" not in st    # pubblicato uno dopo: il sospeso finisce
    st = _stato_del_funding({"BUSDT": -100.0}, G - 16 * ORA_MS)
    finto.righe.clear()
    finto.adesso_ms = G + 6 * 60_000
    st = _ribilancia_con(p, st, {"AUSDT": -0.05}, (G + 6 * 60_000) / 1000)
    _conta(p, finto, st, G + 6 * 60_000 + f5.FUNDING_IN_SOSPESO_MS + 1)
    assert "funding_sospesi" not in st


def test_funding_c_niente_doppioni_e_monete_a_intervallo_di_un_ora_o_quattro(tmp_path):
    """Ipotesi (c): ogni regolamento una volta sola, anche con valutazioni ravvicinate e monete a 1 e 4 ore (passava anche prima)."""
    p, finto = _paper_del_funding(tmp_path)
    st = _stato_del_funding({"AUSDT": -100.0, "HUSDT": 100.0, "QUSDT": -100.0}, G + 5 * 60_000)
    for h in range(1, 25):
        finto.regola("HUSDT", G + h * ORA_MS, -0.0005)            # a un'ora: il long incassa
    for h in (4, 8, 12, 16, 20, 24):
        finto.regola("QUSDT", G + h * ORA_MS, 0.001)
    for h in (8, 16, 24):
        finto.regola("AUSDT", G + h * ORA_MS, 0.0001)
    for minuti in range(65, 25 * 60, 37):                         # valutazioni ogni 37 minuti
        _conta(p, finto, st, G + minuti * 60_000)
    atteso = -(24 * 100 * 10 * 0.0005) - (6 * 100 * 10 * 0.001) - (3 * 100 * 10 * 0.0001)
    assert st["funding_totale"] == pytest.approx(atteso)


def test_funding_di_g1_su_firebase_per_regolamento_e_moneta(tmp_path):
    """Il funding del paper di G1 per regolamento (`/paper_g1/funding/{data}/{ora}`): incassato (+) o pagato (−), il numero di
    monete, le 10 più grandi; riscritto quando arriva una moneta in ritardo. Gli altri paper non lo scrivono."""
    from bot.core.firebase_client import _InMemoryStore
    fb = _InMemoryStore()
    p, finto = _paper_del_funding(tmp_path, f5.PaperG1, fb)
    monete = {f"M{i:02d}USDT": -100.0 for i in range(12)}
    st = _stato_del_funding(monete, G + 5 * 60_000)
    for i, s in enumerate(monete):
        finto.regola(s, G + 8 * ORA_MS, 0.0001 * (i + 1), ritardo_ms=(20 * 60_000 if i == 11 else 0))
    _conta(p, finto, st, G + 8 * ORA_MS + 5 * 60_000)
    r = fb.get_rtdb("/paper_g1/funding/2026-10-24/08:00")
    assert r["monete"] == 11 and r["incassato"] == pytest.approx(sum(100 * 10 * 0.0001 * (i + 1) for i in range(11)))
    assert len(r["maggiori"]) == 10 and "M00USDT" not in r["maggiori"] and r["maggiori"]["M10USDT"] == pytest.approx(1.1)
    _conta(p, finto, st, G + 9 * ORA_MS + 5 * 60_000)             # M11 pubblicata in ritardo: il regolamento si riscrive
    r = fb.get_rtdb("/paper_g1/funding/2026-10-24/08:00")
    assert r["monete"] == 12 and r["incassato"] == pytest.approx(-st["funding_totale"]) and "M01USDT" not in r["maggiori"]
    _conta(p, finto, st, G + 8 * ORA_MS + f5.FUNDING_PER_REGOLAMENTO_MS + 60_000)
    assert st["funding_regolamenti"] == {}                        # nello stato solo le ultime 26 ore
    for classe in (f5.PaperF5, f5.PaperG11, f5.PaperG1N):
        assert classe.PUBBLICA_FUNDING is False
        altro = _InMemoryStore()
        q, finto2 = _paper_del_funding(tmp_path, classe, altro)
        st2 = _stato_del_funding({"AUSDT": -100.0}, G)
        finto2.regola("AUSDT", G + 8 * ORA_MS, 0.001)
        _conta(q, finto2, st2, G + 9 * ORA_MS)
        assert st2["funding_totale"] == pytest.approx(-1.0) and altro.get_rtdb(f"{classe.RAMO}/funding") is None
        assert "funding_regolamenti" not in st2


VIETATI_DA_FIREBASE = set(".$#[]/")


def chiavi_vietate(x, dove=""):
    """Le chiavi (a ogni livello) che Firebase rifiuta: `salva` dei paper scrive lo stato intero in `/<ramo>/stato_interno`."""
    if isinstance(x, dict):
        out = [f"{dove}/{k}" for k in x if not isinstance(k, str) or VIETATI_DA_FIREBASE & set(k) or not k]
        for k, v in x.items():
            out += chiavi_vietate(v, f"{dove}/{k}")
        return out
    if isinstance(x, (list, tuple)):
        return [y for v in x for y in chiavi_vietate(v, dove)]
    return []


def test_lo_stato_dei_paper_non_ha_chiavi_che_firebase_rifiuta(tmp_path):
    """Revisione del 12 novembre 2026, problema 82: con il funding per regolamento, i sospesi e i punti letti, lo stato del paper
    di G1 (quello salvato in `/paper_g1/stato_interno`) non ha chiavi con `. $ # [ ] /`; il percorso pubblicato sì ha la data e l'ora."""
    from bot.core.firebase_client import _InMemoryStore
    fb = _InMemoryStore()
    p, finto = _paper_del_funding(tmp_path, f5.PaperG1, fb)
    p.MISURA_SCARTI = False
    st = _stato_del_funding({"AUSDT": -100.0, "BUSDT": -100.0}, G - 16 * ORA_MS + 5 * 60_000)
    finto.regola("AUSDT", G, 0.001)
    finto.regola("BUSDT", G, 0.002, ritardo_ms=8 * 60_000)
    finto.adesso_ms = G + 6 * 60_000
    st = _ribilancia_con(p, st, {"AUSDT": -0.05, "CUSDT": 0.03}, (G + 6 * 60_000) / 1000)
    finto.regola("AUSDT", G + 8 * ORA_MS, 0.001)
    finto.regola("CUSDT", G + 8 * ORA_MS, 0.001, ritardo_ms=30 * 60_000)
    for h in (1, 8):
        _conta(p, finto, st, G + h * ORA_MS + 6 * 60_000)
    p.salva(st)
    salvato = fb.get_rtdb("/paper_g1/stato_interno")
    assert salvato["funding_regolamenti"] and salvato["funding_visti"] == {"AUSDT": G + 8 * ORA_MS}
    assert chiavi_vietate(salvato) == [] and chiavi_vietate(p.carica()) == []
    assert set(salvato["funding_regolamenti"]) == {"2026-10-24T00:00", "2026-10-24T08:00"}
    assert fb.get_rtdb("/paper_g1/funding/2026-10-24/00:00")["monete"] == 2
    assert chiavi_vietate({"a/b": 1}) == ["/a/b"] and chiavi_vietate({"x": [{"y.z": 1}]}) == ["/x/y.z"]
