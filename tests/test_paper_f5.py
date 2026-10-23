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
