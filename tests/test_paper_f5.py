"""Il paper di F5 nel bot (bot/portafoglio/f5.py): le regole come la ricerca e il conto del portafoglio simulato."""
from __future__ import annotations

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
    costo = sum(abs(q) * finto.prezzo[s] * (f5.TAKER + f5.scarto(s)) for s, q in st["quantita"].items())
    assert st["equity_rif"] == pytest.approx(f5.CAPITALE - costo)
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
