"""Le regole delle idee di ipotesi.md, scritte come «Regola» per il motore.

Ogni regola precalcola i suoi indicatori sull'intera serie in modo CAUSALE (il
valore all'indice i usa solo barre <= i) e offre tre pezzi:
  * ``condizione(i)``: 'long', 'short' o None alla chiusura della barra i;
  * ``uscita(i, direzione)``: il Segnale (stop, target) come lo calcola la regola
    alla barra i, usato anche dalle entrate casuali (stessa uscita);
  * ``chiudi(i, pos)``: True se la posizione va chiusa a mercato alla barra i
    (uscita a tempo o a condizione), usato anche dalle entrate casuali.
``fabbrica(regola, direzione)`` le trasforma nella strategia che il motore chiama.
I parametri sono quelli dichiarati in ipotesi.md; chi li cambia registra una
nuova variante o una verifica di robustezza.
"""
from __future__ import annotations

from typing import Optional, Sequence

import numpy as np

from research.src.motore import Candela, Posizione, Segnale
from research.campagne.SOLUSDT.codice import campagna as cp


class Regola:
    direzioni = ("long", "short")

    def __init__(self, **p):
        self.p = p

    def precalcola(self, candele: Sequence[Candela]) -> None:
        self.o, self.h, self.l, self.c, self.v, self.ts = cp.arrays(candele)
        self.idx = {t: i for i, t in enumerate(self.ts)}
        self.n = len(candele)

    def condizione(self, i: int) -> Optional[str]:
        raise NotImplementedError

    def uscita(self, i: int, direzione: str) -> Optional[Segnale]:
        raise NotImplementedError

    def chiudi(self, i: int, pos: Posizione) -> bool:
        return False

    def barre_in_posizione(self, i: int, pos: Posizione) -> int:
        return i - self.idx[pos.ts_entrata]

    def segnale_stop_atr(self, i, direzione, atr, mult, target_mult=None, riferimento=None):
        """Stop a mult x ATR dal riferimento (la chiusura della barra i, salvo diverso).

        Lo stop si riferisce alla chiusura della barra del segnale perche' l'apertura
        della barra dopo (dove si entra) non si conosce ancora.
        """
        a = atr[i]
        if not np.isfinite(a) or a <= 0:
            return None
        rif = self.c[i] if riferimento is None else riferimento
        if direzione == "long":
            stop = rif - mult * a
            target = rif + target_mult * mult * a if target_mult else None
        else:
            stop = rif + mult * a
            target = rif - target_mult * mult * a if target_mult else None
        if stop <= 0:
            return None
        return Segnale(direzione, stop=stop, target=target)


def fabbrica(regola: Regola, direzione: Optional[str] = None, riscaldamento: int = 0) -> cp.Fabbrica:
    """Strategia per il motore: entra quando ``condizione`` da' ``direzione`` (o una qualsiasi)."""
    def f(candele: Sequence[Candela]):
        regola.precalcola(candele)

        def strategia(cand: Sequence[Candela], pos: Optional[Posizione]):
            i = len(cand) - 1
            if pos is not None:
                return "chiudi" if regola.chiudi(i, pos) else None
            if i < riscaldamento:
                return None
            d = regola.condizione(i)
            if d is None or (direzione is not None and d != direzione):
                return None
            return regola.uscita(i, d)
        return strategia
    return f


def fabbrica_casuale(regola: Regola, direzione: str, indici: Sequence[int]) -> cp.Fabbrica:
    """Entrate agli indici dati con la stessa uscita e la stessa chiusura della regola."""
    def f(candele: Sequence[Candela]):
        regola.precalcola(candele)
        return cp.fabbrica_entrate_fisse(indici, direzione, lambda cand, i: regola.uscita(i, direzione),
                                         lambda cand, pos: regola.chiudi(len(cand) - 1, pos))(candele)
    return f


# ---------------------------------------------------------------------------
# I-01 momentum di serie temporale: cambio di segno del rendimento su N barre
# ---------------------------------------------------------------------------
class Momentum(Regola):
    """p: n (barre del rendimento), atr_n, stop_mult."""

    def precalcola(self, candele):
        super().precalcola(candele)
        n = self.p["n"]
        self.rend = np.full(self.n, np.nan)
        self.rend[n:] = self.c[n:] / self.c[:-n] - 1
        self.atr = cp.atr(self.h, self.l, self.c, self.p["atr_n"])

    def condizione(self, i):
        if i < 1 or not np.isfinite(self.rend[i]) or not np.isfinite(self.rend[i - 1]):
            return None
        if self.rend[i] > 0 and self.rend[i - 1] <= 0:
            return "long"
        if self.rend[i] < 0 and self.rend[i - 1] >= 0:
            return "short"
        return None

    def uscita(self, i, direzione):
        return self.segnale_stop_atr(i, direzione, self.atr, self.p["stop_mult"])

    def chiudi(self, i, pos):
        r = self.rend[i]
        return np.isfinite(r) and ((pos.direzione == "long" and r < 0) or (pos.direzione == "short" and r > 0))


# ---------------------------------------------------------------------------
# I-02 funding estremo: contrario
# ---------------------------------------------------------------------------
class FundingEstremo(Regola):
    """p: finestra (settlement), percentile, soglia (tasso assoluto), atr_n, stop_mult, barre_uscita, funding (lista (ts, tasso))."""

    def precalcola(self, candele):
        super().precalcola(candele)
        fund = sorted(self.p["funding"])
        fts = np.array([t for t, _ in fund]); fr = np.array([r for _, r in fund])
        fin, perc, soglia = self.p["finestra"], self.p["percentile"], self.p["soglia"]
        # per ogni barra: l'ultimo settlement con ts <= close_ts della barra
        close_ts = self.ts + (self.ts[1] - self.ts[0]) - 1
        pos = np.searchsorted(fts, close_ts, side="right") - 1
        self.seg = np.zeros(self.n, dtype=int)
        ultimo_usato = -1
        for i in range(self.n):
            k = pos[i]
            if k < fin or k == ultimo_usato:
                continue
            # il settlement k deve cadere DENTRO questa barra (non in una precedente gia' usata)
            if fts[k] < self.ts[i]:
                continue
            ultimo_usato = k
            storia = fr[k - fin:k]
            if fr[k] >= np.percentile(storia, perc) and fr[k] >= soglia:
                self.seg[i] = -1
            elif fr[k] <= np.percentile(storia, 100 - perc) and fr[k] <= -soglia:
                self.seg[i] = 1
        self.atr = cp.atr(self.h, self.l, self.c, self.p["atr_n"])

    def condizione(self, i):
        return {1: "long", -1: "short"}.get(int(self.seg[i]))

    def uscita(self, i, direzione):
        return self.segnale_stop_atr(i, direzione, self.atr, self.p["stop_mult"])

    def chiudi(self, i, pos):
        return self.barre_in_posizione(i, pos) >= self.p["barre_uscita"]


# ---------------------------------------------------------------------------
# I-03 sessione americana (1h): segnale alla chiusura dell'ora `ora_segnale`, chiusura all'ora `ora_uscita`
# ---------------------------------------------------------------------------
class Sessione(Regola):
    """p: ora_segnale, ora_uscita, atr_n, stop_mult, direzione, solo_feriali."""
    def precalcola(self, candele):
        super().precalcola(candele)
        self.ore = cp.ora_utc(self.ts)
        self.gs = cp.giorno_settimana(self.ts)
        self.atr = cp.atr(self.h, self.l, self.c, self.p["atr_n"])

    def condizione(self, i):
        if self.ore[i] != self.p["ora_segnale"]:
            return None
        if self.p.get("solo_feriali") and self.gs[i] >= 5:
            return None
        return self.p["direzione"]

    def uscita(self, i, direzione):
        return self.segnale_stop_atr(i, direzione, self.atr, self.p["stop_mult"])

    def chiudi(self, i, pos):
        # chiudi alla chiusura della barra prima di ora_uscita (l'uscita avviene all'apertura dopo)
        return self.ore[i] == (self.p["ora_uscita"] - 1) % 24 or self.barre_in_posizione(i, pos) >= 24


# ---------------------------------------------------------------------------
# I-04 fine settimana (4h): ritraccio del lunedi' o segno puro
# ---------------------------------------------------------------------------
class FineSettimana(Regola):
    """p: modo ('ritraccio' o 'segno'), atr_n, stop_mult, soglia_atr, barre_uscita, direzione (solo per 'segno')."""
    def precalcola(self, candele):
        super().precalcola(candele)
        self.ore = cp.ora_utc(self.ts)
        self.gs = cp.giorno_settimana(self.ts)
        self.atr = cp.atr(self.h, self.l, self.c, self.p["atr_n"])

    def condizione(self, i):
        modo = self.p["modo"]
        if modo == "segno":
            # segnale alla chiusura dell'ultima barra di venerdi' (20:00-24:00): ingresso sabato 00:00
            if self.gs[i] == 4 and self.ore[i] == 20:
                return self.p["direzione"]
            return None
        # ritraccio: segnale alla chiusura dell'ultima barra di domenica (20:00-24:00)
        if not (self.gs[i] == 6 and self.ore[i] == 20):
            return None
        # movimento del fine settimana: dalla chiusura di venerdi' (ultima barra con gs==4) alla chiusura di ora
        j = i
        while j >= 0 and self.gs[j] != 4:
            j -= 1
        if j < 0 or not np.isfinite(self.atr[i]):
            return None
        mossa = self.c[i] - self.c[j]
        if mossa > self.p["soglia_atr"] * self.atr[i]:
            return "short"
        if mossa < -self.p["soglia_atr"] * self.atr[i]:
            return "long"
        return None

    def uscita(self, i, direzione):
        return self.segnale_stop_atr(i, direzione, self.atr, self.p["stop_mult"])

    def chiudi(self, i, pos):
        return self.barre_in_posizione(i, pos) >= self.p["barre_uscita"]


# ---------------------------------------------------------------------------
# I-05 continuazione dopo barra estrema; I-06 ritorno dopo barra estrema con conferma
# ---------------------------------------------------------------------------
class BarraEstrema(Regola):
    """p: finestra, soglia_sigma, modo ('continuazione' o 'ritorno'), atr_n, stop_mult, barre_uscita, target (bool, solo ritorno)."""
    def precalcola(self, candele):
        super().precalcola(candele)
        r = np.zeros(self.n); r[1:] = self.c[1:] / self.c[:-1] - 1
        self.r = r
        self.sigma = np.full(self.n, np.nan)
        f = self.p["finestra"]
        # deviazione dei rendimenti delle f barre PRECEDENTI (escluso i)
        for i in range(f + 1, self.n):
            self.sigma[i] = r[i - f:i].std()
        self.atr = cp.atr(self.h, self.l, self.c, self.p["atr_n"])

    def shock(self, i):
        s = self.sigma[i]
        if not np.isfinite(s) or s <= 0:
            return 0
        z = self.r[i] / s
        if z >= self.p["soglia_sigma"]:
            return 1
        if z <= -self.p["soglia_sigma"]:
            return -1
        return 0

    def condizione(self, i):
        if self.p["modo"] == "continuazione":
            s = self.shock(i)
            return {1: "long", -1: "short"}.get(s)
        # ritorno: shock alla barra i-1 e barra i di segno opposto
        if i < 1:
            return None
        s = self.shock(i - 1)
        if s == 1 and self.r[i] < 0:
            return "short"
        if s == -1 and self.r[i] > 0:
            return "long"
        return None

    def uscita(self, i, direzione):
        if self.p["modo"] == "continuazione":
            return self.segnale_stop_atr(i, direzione, self.atr, self.p["stop_mult"])
        a = self.atr[i]
        if not np.isfinite(a) or a <= 0:
            return None
        if direzione == "long":
            stop = min(self.l[i - 1], self.l[i]) - self.p["stop_mult"] * a
            target = (self.o[i - 1] + self.c[i - 1]) / 2 if self.p.get("target") else None
            if target is not None and target <= self.c[i]:
                target = None
        else:
            stop = max(self.h[i - 1], self.h[i]) + self.p["stop_mult"] * a
            target = (self.o[i - 1] + self.c[i - 1]) / 2 if self.p.get("target") else None
            if target is not None and target >= self.c[i]:
                target = None
        if stop <= 0:
            return None
        return Segnale(direzione, stop=stop, target=target)

    def chiudi(self, i, pos):
        return self.barre_in_posizione(i, pos) >= self.p["barre_uscita"]


# ---------------------------------------------------------------------------
# I-07 rottura di canale (Donchian / Turtle)
# ---------------------------------------------------------------------------
class Canale(Regola):
    """p: n_ingresso, n_uscita, atr_n, stop_mult."""
    def precalcola(self, candele):
        super().precalcola(candele)
        self.max_in = cp.massimo_precedente(self.h, self.p["n_ingresso"])
        self.min_in = cp.minimo_precedente(self.l, self.p["n_ingresso"])
        self.max_out = cp.massimo_precedente(self.h, self.p["n_uscita"])
        self.min_out = cp.minimo_precedente(self.l, self.p["n_uscita"])
        self.atr = cp.atr(self.h, self.l, self.c, self.p["atr_n"])

    def condizione(self, i):
        if not np.isfinite(self.max_in[i]):
            return None
        if self.c[i] > self.max_in[i]:
            return "long"
        if self.c[i] < self.min_in[i]:
            return "short"
        return None

    def uscita(self, i, direzione):
        return self.segnale_stop_atr(i, direzione, self.atr, self.p["stop_mult"])

    def chiudi(self, i, pos):
        if not np.isfinite(self.min_out[i]):
            return False
        if pos.direzione == "long":
            return self.c[i] < self.min_out[i]
        return self.c[i] > self.max_out[i]


# ---------------------------------------------------------------------------
# I-08 bande di Bollinger: ritorno alla media
# ---------------------------------------------------------------------------
class Bollinger(Regola):
    """p: n, k, atr_n, stop_mult, barre_uscita."""
    def precalcola(self, candele):
        super().precalcola(candele)
        self.media = cp.media_mobile(self.c, self.p["n"])
        self.dev = cp.deviazione_mobile(self.c, self.p["n"])
        self.atr = cp.atr(self.h, self.l, self.c, self.p["atr_n"])

    def condizione(self, i):
        if not np.isfinite(self.media[i]):
            return None
        k = self.p["k"]
        if self.c[i] < self.media[i] - k * self.dev[i]:
            return "long"
        if self.c[i] > self.media[i] + k * self.dev[i]:
            return "short"
        return None

    def uscita(self, i, direzione):
        a = self.atr[i]
        if not np.isfinite(a) or a <= 0:
            return None
        if direzione == "long":
            stop = self.l[i] - self.p["stop_mult"] * a
            target = self.media[i]
            if target <= self.c[i]:
                return None
        else:
            stop = self.h[i] + self.p["stop_mult"] * a
            target = self.media[i]
            if target >= self.c[i]:
                return None
        if stop <= 0:
            return None
        return Segnale(direzione, stop=stop, target=target)

    def chiudi(self, i, pos):
        return self.barre_in_posizione(i, pos) >= self.p["barre_uscita"]


# ---------------------------------------------------------------------------
# I-09 ritracciamento nella tendenza (medie mobili)
# ---------------------------------------------------------------------------
class Ritracciamento(Regola):
    """p: n_lunga, n_corta, atr_n, stop_mult, target_mult, barre_uscita."""
    def precalcola(self, candele):
        super().precalcola(candele)
        self.lunga = cp.media_mobile(self.c, self.p["n_lunga"])
        self.corta = cp.media_mobile(self.c, self.p["n_corta"])
        self.atr = cp.atr(self.h, self.l, self.c, self.p["atr_n"])

    def condizione(self, i):
        if not np.isfinite(self.lunga[i]):
            return None
        if self.c[i] > self.lunga[i] and self.l[i] < self.corta[i] and self.c[i] > self.corta[i]:
            return "long"
        if self.c[i] < self.lunga[i] and self.h[i] > self.corta[i] and self.c[i] < self.corta[i]:
            return "short"
        return None

    def in_tendenza(self, i):
        """Per la baseline condizionata: 'long' se sopra la media lunga, 'short' se sotto."""
        if not np.isfinite(self.lunga[i]):
            return None
        return "long" if self.c[i] > self.lunga[i] else "short"

    def uscita(self, i, direzione):
        a = self.atr[i]
        if not np.isfinite(a) or a <= 0:
            return None
        if direzione == "long":
            stop = self.l[i] - self.p["stop_mult"] * a
            dist = self.c[i] - stop
            target = self.c[i] + self.p["target_mult"] * dist
        else:
            stop = self.h[i] + self.p["stop_mult"] * a
            dist = stop - self.c[i]
            target = self.c[i] - self.p["target_mult"] * dist
        if stop <= 0 or dist <= 0:
            return None
        return Segnale(direzione, stop=stop, target=target)

    def chiudi(self, i, pos):
        return self.barre_in_posizione(i, pos) >= self.p["barre_uscita"]


# ---------------------------------------------------------------------------
# I-10 ritardo di SOL rispetto a BTC
# ---------------------------------------------------------------------------
class RitardoBtc(Regola):
    """p: btc (candele BTCUSDT stesso timeframe), n_rend, finestra, soglia_sigma, rapporto_max, atr_n, stop_mult, barre_uscita."""
    def precalcola(self, candele):
        super().precalcola(candele)
        btc = {c.ts: c.close for c in self.p["btc"]}
        cb = np.array([btc.get(t, np.nan) for t in self.ts])
        # riempi i buchi di BTC con l'ultimo valore noto (causale)
        for i in range(1, self.n):
            if not np.isfinite(cb[i]):
                cb[i] = cb[i - 1]
        n = self.p["n_rend"]
        self.rb = np.full(self.n, np.nan); self.rs = np.full(self.n, np.nan)
        self.rb[n:] = cb[n:] / cb[:-n] - 1
        self.rs[n:] = self.c[n:] / self.c[:-n] - 1
        f = self.p["finestra"]
        self.sig = np.full(self.n, np.nan)
        for i in range(n + f, self.n):
            self.sig[i] = np.nanstd(self.rb[i - f:i])
        self.atr = cp.atr(self.h, self.l, self.c, self.p["atr_n"])

    def condizione(self, i):
        s = self.sig[i]
        if not np.isfinite(s) or s <= 0 or not np.isfinite(self.rs[i]):
            return None
        z = self.rb[i] / s
        if z >= self.p["soglia_sigma"] and self.rs[i] < self.p["rapporto_max"] * self.rb[i]:
            return "long"
        if z <= -self.p["soglia_sigma"] and self.rs[i] > self.p["rapporto_max"] * self.rb[i]:
            return "short"
        return None

    def uscita(self, i, direzione):
        return self.segnale_stop_atr(i, direzione, self.atr, self.p["stop_mult"])

    def chiudi(self, i, pos):
        return self.barre_in_posizione(i, pos) >= self.p["barre_uscita"]


# ---------------------------------------------------------------------------
# I-11 premio del volume alto
# ---------------------------------------------------------------------------
class VolumeAlto(Regola):
    """p: n_media, mult, atr_n, stop_mult, barre_uscita."""
    def precalcola(self, candele):
        super().precalcola(candele)
        self.vm = np.full(self.n, np.nan)
        n = self.p["n_media"]
        for i in range(n, self.n):
            self.vm[i] = self.v[i - n:i].mean()
        self.atr = cp.atr(self.h, self.l, self.c, self.p["atr_n"])

    def condizione(self, i):
        if not np.isfinite(self.vm[i]) or self.vm[i] <= 0:
            return None
        return "long" if self.v[i] > self.p["mult"] * self.vm[i] else None

    def uscita(self, i, direzione):
        return self.segnale_stop_atr(i, direzione, self.atr, self.p["stop_mult"])

    def chiudi(self, i, pos):
        return self.barre_in_posizione(i, pos) >= self.p["barre_uscita"]


# ---------------------------------------------------------------------------
# I-12 compressione della volatilita' e rottura
# ---------------------------------------------------------------------------
class Compressione(Regola):
    """p: n, k, n_minimo, atr_n, stop_mult, target_mult, barre_uscita."""
    def precalcola(self, candele):
        super().precalcola(candele)
        self.media = cp.media_mobile(self.c, self.p["n"])
        self.dev = cp.deviazione_mobile(self.c, self.p["n"])
        larg = 2 * self.p["k"] * self.dev / self.media
        self.larg = larg
        self.min_larg = cp.minimo_precedente(np.where(np.isfinite(larg), larg, np.inf), self.p["n_minimo"])
        self.atr = cp.atr(self.h, self.l, self.c, self.p["atr_n"])

    def condizione(self, i):
        if i < 1 or not np.isfinite(self.larg[i - 1]) or not np.isfinite(self.min_larg[i - 1]):
            return None
        if self.larg[i - 1] > self.min_larg[i - 1]:
            return None  # la barra prima non era al minimo di larghezza
        k = self.p["k"]
        if self.c[i] > self.media[i] + k * self.dev[i]:
            return "long"
        if self.c[i] < self.media[i] - k * self.dev[i]:
            return "short"
        return None

    def uscita(self, i, direzione):
        return self.segnale_stop_atr(i, direzione, self.atr, self.p["stop_mult"], target_mult=self.p["target_mult"])

    def chiudi(self, i, pos):
        return self.barre_in_posizione(i, pos) >= self.p["barre_uscita"]


# ---------------------------------------------------------------------------
# I-13 sbilanciamento degli ordini (quota di volume taker buy)
# ---------------------------------------------------------------------------
class Sbilanciamento(Regola):
    """p: taker (dict ts -> (taker_buy_volume, volume)), n_somma, finestra, percentile, atr_n, stop_mult, barre_uscita."""
    def precalcola(self, candele):
        super().precalcola(candele)
        tk = self.p["taker"]
        tb = np.array([tk.get(t, (np.nan, np.nan))[0] for t in self.ts])
        vv = np.array([tk.get(t, (np.nan, np.nan))[1] for t in self.ts])
        n = self.p["n_somma"]
        self.quota = np.full(self.n, np.nan)
        for i in range(n - 1, self.n):
            s = vv[i - n + 1:i + 1].sum()
            if np.isfinite(s) and s > 0:
                self.quota[i] = tb[i - n + 1:i + 1].sum() / s
        f, perc = self.p["finestra"], self.p["percentile"]
        self.alto = np.full(self.n, np.nan); self.basso = np.full(self.n, np.nan)
        for i in range(f + n, self.n):
            st_ = self.quota[i - f:i]
            st_ = st_[np.isfinite(st_)]
            if len(st_) >= f // 2:
                self.alto[i] = np.percentile(st_, perc); self.basso[i] = np.percentile(st_, 100 - perc)
        self.atr = cp.atr(self.h, self.l, self.c, self.p["atr_n"])

    def condizione(self, i):
        q = self.quota[i]
        if not np.isfinite(q) or not np.isfinite(self.alto[i]):
            return None
        if q > self.alto[i]:
            return "long"
        if q < self.basso[i]:
            return "short"
        return None

    def uscita(self, i, direzione):
        return self.segnale_stop_atr(i, direzione, self.atr, self.p["stop_mult"])

    def chiudi(self, i, pos):
        return self.barre_in_posizione(i, pos) >= self.p["barre_uscita"]
