"""Prova dei moduli delle varianti su prezzi SINTETICI (passeggiata casuale): solo il contratto, mai risultati.

Per ogni modulo e parametri: la variante gira con motore.esegui su una serie inventata; crea_casuale con le
barre di segnale dei suoi trade deve rifare gli stessi trade (il controllo di gruppo.py); crea_a e crea_segnale
devono girare. Stampa solo «ok» o l'errore, e il numero dei trade sulla serie inventata (non e' una stima).
Uso: python3 -u prova_moduli.py
"""
import importlib.util
import json
import random
import sys
from bisect import bisect_right
from pathlib import Path

from comune import CARTELLA_GRUPPO  # noqa: F401  (mette la radice del progetto nel path)
from research.src import motore
from research.src.motore import Candela, StoriaChiusa

MS_GIORNO = 86_400_000


def serie_inventata(n, seme, ms=MS_GIORNO):
    rnd = random.Random(seme)
    t0 = 1577836800000  # 2020-01-01
    prezzo, candele = 100.0, []
    for i in range(n):
        o = prezzo
        c = o * (1 + rnd.gauss(0, 0.04))
        h = max(o, c) * (1 + abs(rnd.gauss(0, 0.02)))
        l = min(o, c) * (1 - abs(rnd.gauss(0, 0.02)))
        candele.append(Candela(t0 + i * ms, o, h, l, c, rnd.uniform(1e5, 1e6) * (3 if rnd.random() < 0.05 else 1),
                               t0 + (i + 1) * ms - 1))
        prezzo = c
    return candele


class Ctx:
    def __init__(self, ms, btc, funding, orologio):
        self.timeframe = "x"
        self.ms_per_barra = ms
        self._btc, self._f, self._o = btc, funding, orologio

    def btc_chiuse_entro(self, ts):
        lim = min(ts, self._o[0]) if self._o[0] is not None else -1
        k = bisect_right([c.close_ts for c in self._btc], lim)
        return StoriaChiusa(self._btc, k)

    def funding_regolato_entro(self, ts):
        lim = min(ts, self._o[0]) if self._o[0] is not None else -1
        k = bisect_right([t for t, _ in self._f], lim)
        return StoriaChiusa(self._f, k)


def avvolgi(strategia, orologio):
    def f(storia, pos):
        orologio[0] = storia[-1].close_ts
        return strategia(storia, pos)
    return f


def prova(percorso, p, ms=MS_GIORNO):
    spec = importlib.util.spec_from_file_location("variante", percorso)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    candele = serie_inventata(1200, 1, ms)
    btc = serie_inventata(1200, 2, ms)
    rnd = random.Random(3)
    funding = [(candele[0].ts + i * 8 * 3_600_000, rnd.gauss(0.0001, 0.0008)) for i in range(len(candele) * 3)]
    orologio = [None]
    ctx = Ctx(ms, btc, funding, orologio)
    par = motore.Parametri()
    r = motore.esegui(candele, None, candele, funding, avvolgi(mod.crea_variante(ctx, p)(), orologio), par)
    segnali = []
    for t in r.trades:
        i = [c.ts for c in candele].index(t.ts_entrata)
        segnali.append(i - 1)
    orologio[0] = None
    r2 = motore.esegui(candele, None, candele, funding, avvolgi(mod.crea_casuale(ctx, p)(frozenset(segnali)), orologio), par)
    uguali = [(a.ts_entrata, a.ts_uscita, a.r) for a in r.trades] == [(b.ts_entrata, b.ts_uscita, b.r) for b in r2.trades]
    orologio[0] = None
    ra = motore.esegui(candele, None, candele, funding, avvolgi(mod.crea_a(ctx, p)(), orologio), par)
    orologio[0] = None
    vietate = motore.barre_vietate_segnale_non_valido(candele, mod.crea_segnale(ctx, p), par)
    return {"trade_variante": len(r.trades), "casuale_uguale": uguali, "trade_a": len(ra.trades),
            "intervalli_vietati": len(vietate)}


if __name__ == "__main__":
    casi = json.loads(Path(sys.argv[1]).read_text()) if len(sys.argv) > 1 else []
    for modulo, p, ms in casi:
        try:
            esito = prova(CARTELLA_GRUPPO / "codice" / modulo, p, ms)
            print("ok" if esito["casuale_uguale"] else "DIVERSO", modulo, json.dumps(p), esito, flush=True)
        except Exception as e:  # noqa: BLE001
            print("ERRORE", modulo, json.dumps(p), type(e).__name__, e, flush=True)
