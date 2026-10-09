"""Le varianti della campagna ADAUSDT. Ogni regola e' scritta qui PRIMA della sua registrazione;
le idee, le fonti e le spiegazioni concorrenti stanno in ../ipotesi.md.

Convenzioni comuni a tutte le varianti:
* segnale alla chiusura della barra i, ingresso all'apertura della barra i+1 (motore);
* stop a k ATR(14) del timeframe dalla chiusura della barra di segnale (salvo dove detto);
* indicatori causali (comune.py): il valore alla barra i usa solo le barre 0..i;
* nessun ingresso su segnali di barre di gennaio, marzo e aprile 2020 (filtro di Fase 0, in comune.py).
"""
from datetime import datetime, timezone

import numpy as np

import comune as C
from research.src.motore import Segnale


def _ora(ts):
    d = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    return d.hour, d.minute


class StopATR(C.Variante):
    """Base: stop a k ATR(14) dalla chiusura, senza target, uscita definita dalla sottoclasse."""

    def base(self, D):
        A = C.arrays(D["candele"])
        A["atr"] = C.atr(A["h"], A["l"], A["c"], 14)
        return A

    def segnale(self, i, P):
        a = P["atr"][i]
        if not np.isfinite(a) or not np.isfinite(P.get("pronto", P["c"])[i]):
            return None
        k = self.p["stop_atr"]
        if self.direzione == "long":
            return Segnale("long", P["c"][i] - k * a)
        return Segnale("short", P["c"][i] + k * a)


# I-01 Momentum a serie temporale -------------------------------------------------------------

class Momento(StopATR):
    tf = "4h"

    def prepara(self, D):
        P = self.base(D)
        P["ret"] = C.rendimento(P["c"], self.p["finestra"])
        P["pronto"] = P["ret"]
        return P

    def condizione(self, i, P):
        r = P["ret"][i]
        return bool(r > 0) if self.direzione == "long" else bool(r < 0)

    def uscita(self, i, P, barre):
        return barre >= self.p["tenuta"]


# I-02 Rottura del canale (Donchian) ------------------------------------------------------------

class Canale(StopATR):
    tf = "4h"

    def prepara(self, D):
        P = self.base(D)
        P["max_in"] = C.massimo_precedente(P["h"], self.p["ingresso"])
        P["min_in"] = C.minimo_precedente(P["l"], self.p["ingresso"])
        P["max_out"] = C.massimo_precedente(P["h"], self.p["uscita"])
        P["min_out"] = C.minimo_precedente(P["l"], self.p["uscita"])
        P["pronto"] = P["max_in"]
        return P

    def condizione(self, i, P):
        if self.direzione == "long":
            return bool(P["c"][i] > P["max_in"][i])
        return bool(P["c"][i] < P["min_in"][i])

    def uscita(self, i, P, barre):
        if self.direzione == "long":
            return bool(P["c"][i] < P["min_out"][i])
        return bool(P["c"][i] > P["max_out"][i])


# I-03 Prezzo sopra la media mobile --------------------------------------------------------------

class SopraMedia(StopATR):
    tf = "1d"

    def prepara(self, D):
        P = self.base(D)
        P["ma"] = C.sma(P["c"], self.p["media"])
        P["pronto"] = P["ma"]
        return P

    def condizione(self, i, P):
        if i < 1 or not np.isfinite(P["ma"][i - 1]):
            return False
        return bool(P["c"][i] > P["ma"][i] and P["c"][i - 1] <= P["ma"][i - 1])

    def uscita(self, i, P, barre):
        return bool(P["c"][i] < P["ma"][i])


# I-04 Reazioni eccessive giornaliere (inerzia) ------------------------------------------------

class Eccesso(StopATR):
    tf = "1d"

    def prepara(self, D):
        P = self.base(D)
        r = P["c"] / P["o"] - 1.0
        ar = np.abs(r)
        n = self.p["finestra"]
        soglia = np.full(len(r), np.nan)
        for i in range(n, len(r)):
            w = ar[i - n:i]
            soglia[i] = w.mean() + self.p["k"] * w.std(ddof=1)
        P["r"], P["soglia"] = r, soglia
        P["pronto"] = soglia
        return P

    def condizione(self, i, P):
        s = P["soglia"][i]
        if not np.isfinite(s):
            return False
        r = P["r"][i]
        return bool(r > s) if self.direzione == "long" else bool(r < -s)

    def uscita(self, i, P, barre):
        return barre >= self.p["tenuta"]


# I-05 Momento infragiornaliero: prima mezz'ora -> ultima mezz'ora ---------------------------------

class MezzOra(StopATR):
    tf = "30m"

    def prepara(self, D):
        P = C.arrays(D["candele"])
        P["atr"] = C.atr(P["h"], P["l"], P["c"], self.p["atr_n"])
        n = len(P["c"])
        prima = np.full(n, np.nan)
        ultima_barra = np.zeros(n, dtype=bool)
        r_corrente = np.nan
        for i in range(n):
            h, m = _ora(P["ts"][i])
            if h == 0 and m == 0:
                r_corrente = P["c"][i] / P["o"][i] - 1.0  # nota alla chiusura della barra 00:00-00:30
            elif h == 0 and m == 30:
                pass
            prima[i] = r_corrente
            ultima_barra[i] = (h == 23 and m == 0)  # chiude alle 23:30: si entra nell'ultima mezz'ora
        # il rendimento della prima mezz'ora vale solo per lo stesso giorno: azzerato se il giorno manca
        giorno = P["ts"] // 86_400_000
        inizio_giorno = np.full(n, -1)
        g_cor, idx = None, -1
        for i in range(n):
            h, m = _ora(P["ts"][i])
            if h == 0 and m == 0:
                g_cor, idx = giorno[i], i
            inizio_giorno[i] = idx if g_cor == giorno[i] else -1
        prima = np.where(inizio_giorno >= 0, prima, np.nan)
        P["prima"], P["ultima"] = prima, ultima_barra
        P["pronto"] = P["atr"]
        return P

    def segnale(self, i, P):
        a = P["atr"][i]
        if not np.isfinite(a):
            return None
        k = self.p["stop_atr"]
        return Segnale("long", P["c"][i] - k * a) if self.direzione == "long" else Segnale("short", P["c"][i] + k * a)

    def condizione(self, i, P):
        if not P["ultima"][i] or not np.isfinite(P["prima"][i]):
            return False
        return bool(P["prima"][i] > 0) if self.direzione == "long" else bool(P["prima"][i] < 0)

    def uscita(self, i, P, barre):
        return barre >= 1


# I-06 BTC guida, ADA segue ------------------------------------------------------------------------

class Segue(StopATR):
    tf = "1h"

    def prepara(self, D):
        P = self.base(D)
        b = D["btc_close"]
        rb = np.full(len(b), np.nan)
        rb[1:] = b[1:] / b[:-1] - 1.0
        ra = np.full(len(b), np.nan)
        ra[1:] = P["c"][1:] / P["c"][:-1] - 1.0
        P["rb"], P["ra"] = rb, ra
        P["sb"] = C.std_mobile(np.nan_to_num(rb), self.p["finestra"])
        P["pronto"] = P["sb"]
        return P

    def condizione(self, i, P):
        rb, ra, sb = P["rb"][i], P["ra"][i], P["sb"][i]
        if not (np.isfinite(rb) and np.isfinite(ra) and np.isfinite(sb)):
            return False
        k = self.p["k"]
        if self.direzione == "long":
            return bool(rb > k * sb and ra < rb)
        return bool(rb < -k * sb and ra > rb)

    def uscita(self, i, P, barre):
        return barre >= self.p["tenuta"]


# I-07 Funding affollato --------------------------------------------------------------------------

class Affollamento(StopATR):
    tf = "8h"

    def prepara(self, D):
        P = self.base(D)
        f = sorted(D["funding"])
        ts_f = np.array([t for t, _ in f], dtype=np.int64)
        r_f = np.array([r for _, r in f])
        close_ts = np.array([c.close_ts for c in D["candele"]], dtype=np.int64)
        n = len(close_ts)
        ultimo = np.full(n, np.nan)
        quantile = np.full(n, np.nan)
        m = self.p["storia"]
        q = self.p["quantile"]
        for i in range(n):
            k = np.searchsorted(ts_f, close_ts[i], side="right") - 1  # ultimo settlement entro la chiusura
            if k >= m:
                ultimo[i] = r_f[k]
                quantile[i] = np.quantile(r_f[k - m:k], q)
        P["f"], P["q"] = ultimo, quantile
        P["pronto"] = quantile
        return P

    def condizione(self, i, P):
        f, q = P["f"][i], P["q"][i]
        if not (np.isfinite(f) and np.isfinite(q)):
            return False
        if self.direzione == "short":
            return bool(f > self.p["minimo"] and f >= q)
        return bool(f < self.p["massimo"] and f <= q)

    def uscita(self, i, P, barre):
        return barre >= self.p["tenuta"]


# I-08 Compressione della volatilita' (Bollinger, «squeeze») -----------------------------------

class Compressione(StopATR):
    tf = "4h"

    def prepara(self, D):
        P = self.base(D)
        n = self.p["bande"]
        mid = C.sma(P["c"], n)
        sd = C.std_mobile(P["c"], n)
        bw = 4 * sd / mid
        lun = self.p["storia"]
        sq = np.zeros(len(bw), dtype=bool)
        for i in range(lun, len(bw)):
            if np.isfinite(bw[i]) and np.all(np.isfinite(bw[i - lun:i])):
                sq[i] = bw[i] <= bw[i - lun:i].min()
        rec = np.zeros(len(bw), dtype=bool)
        w = self.p["recente"]
        for i in range(len(bw)):
            rec[i] = sq[max(0, i - w):i + 1].any()
        P["mid"], P["up"], P["dn"], P["rec"] = mid, mid + 2 * sd, mid - 2 * sd, rec
        P["pronto"] = mid
        return P

    def condizione(self, i, P):
        if not P["rec"][i]:
            return False
        if self.direzione == "long":
            return bool(P["c"][i] > P["up"][i])
        return bool(P["c"][i] < P["dn"][i])

    def uscita(self, i, P, barre):
        if self.direzione == "long":
            return bool(P["c"][i] < P["mid"][i])
        return bool(P["c"][i] > P["mid"][i])


# I-09 RSI(2) in trend (Connors) -------------------------------------------------------------------

class Ritracciamento(StopATR):
    def __init__(self, tf, **p):
        super().__init__(**p)
        self.tf = tf

    def prepara(self, D):
        P = self.base(D)
        P["lenta"] = C.sma(P["c"], self.p["trend"])
        P["veloce"] = C.sma(P["c"], self.p["uscita_media"])
        P["rsi"] = C.rsi(P["c"], self.p["rsi_n"])
        P["pronto"] = P["lenta"]
        return P

    def condizione(self, i, P):
        r, ma = P["rsi"][i], P["lenta"][i]
        if not (np.isfinite(r) and np.isfinite(ma)):
            return False
        return bool(P["c"][i] > ma and r < self.p["soglia"])

    def uscita(self, i, P, barre):
        return bool(P["c"][i] > P["veloce"][i])


# I-10 Premio dei volumi alti --------------------------------------------------------------------

class VolumeAlto(StopATR):
    def __init__(self, tf, **p):
        super().__init__(**p)
        self.tf = tf

    def prepara(self, D):
        P = self.base(D)
        vol = D["volume_usdt"]
        r = P["c"] / P["o"] - 1.0
        n, m = self.p["finestra_volume"], self.p["finestra_ritorni"]
        qv = np.full(len(vol), np.nan)
        sr = np.full(len(vol), np.nan)
        for i in range(max(n, m), len(vol)):
            qv[i] = np.quantile(vol[i - n:i], self.p["quantile"])
            sr[i] = r[i - m:i].std(ddof=1)
        P["vol"], P["qv"], P["r"], P["sr"] = vol, qv, r, sr
        P["pronto"] = qv
        return P

    def condizione(self, i, P):
        if not (np.isfinite(P["qv"][i]) and np.isfinite(P["sr"][i])):
            return False
        return bool(P["vol"][i] > P["qv"][i] and abs(P["r"][i]) < self.p["k_ritorno"] * P["sr"][i])

    def uscita(self, i, P, barre):
        return barre >= self.p["tenuta"]


# I-11 Numeri tondi (Osler) ----------------------------------------------------------------------

class NumeriTondi(StopATR):
    tf = "1h"

    def prepara(self, D):
        P = self.base(D)
        c = P["c"]
        n = len(c)
        su = np.zeros(n, dtype=bool)
        giu = np.zeros(n, dtype=bool)
        for i in range(1, n):
            passo = 0.5 * 10 ** np.floor(np.log10(c[i - 1]))
            a, b = np.floor(c[i - 1] / passo), np.floor(c[i] / passo)
            su[i] = b > a
            giu[i] = b < a
        P["su"], P["giu"] = su, giu
        return P

    def condizione(self, i, P):
        return bool(P["su"][i]) if self.direzione == "long" else bool(P["giu"][i])

    def uscita(self, i, P, barre):
        return barre >= self.p["tenuta"]


# I-12 Ritorno del residuo rispetto a BTC (Avellaneda e Lee) ---------------------------------------

class Residuo(StopATR):
    tf = "1h"

    def prepara(self, D):
        P = self.base(D)
        la, lb = np.log(P["c"]), np.log(D["btc_close"])
        ra = np.diff(la, prepend=np.nan)
        rb = np.diff(lb, prepend=np.nan)
        n, w = self.p["finestra_beta"], self.p["finestra_somma"]
        N = len(ra)
        e = np.full(N, np.nan)
        sig = np.full(N, np.nan)
        for i in range(n + 1, N):
            xa, xb = ra[i - n + 1:i + 1], rb[i - n + 1:i + 1]
            ok = np.isfinite(xa) & np.isfinite(xb)
            if ok.sum() < n // 2:
                continue
            beta = np.cov(xa[ok], xb[ok])[0, 1] / np.var(xb[ok], ddof=1)
            res = xa[ok] - beta * xb[ok]
            e[i] = ra[i] - beta * rb[i] if np.isfinite(ra[i]) and np.isfinite(rb[i]) else 0.0
            sig[i] = res.std(ddof=1) * np.sqrt(w)
        somma = np.full(N, np.nan)
        for i in range(w, N):
            blocco = e[i - w + 1:i + 1]
            if np.all(np.isfinite(blocco)):
                somma[i] = blocco.sum()
        P["s"] = somma / sig
        P["pronto"] = P["s"]
        return P

    def condizione(self, i, P):
        s = P["s"][i]
        if not np.isfinite(s):
            return False
        return bool(s < -self.p["ingresso"]) if self.direzione == "long" else bool(s > self.p["ingresso"])

    def uscita(self, i, P, barre):
        s = P["s"][i]
        if barre >= self.p["tenuta"]:
            return True
        if not np.isfinite(s):
            return False
        return bool(s > -self.p["rientro"]) if self.direzione == "long" else bool(s < self.p["rientro"])

    def segnale(self, i, P):
        if not np.isfinite(P["s"][i]):
            return None
        return StopATR.segnale(self, i, P)


# I-13 Rottura dell'intervallo d'apertura (Crabel) -------------------------------------------------

class Apertura(C.Variante):
    tf = "15m"

    def prepara(self, D):
        P = C.arrays(D["candele"])
        n = len(P["c"])
        b = self.p["barre_intervallo"]
        alto = np.full(n, np.nan)
        basso = np.full(n, np.nan)
        fine_giorno = np.zeros(n, dtype=bool)
        ammesso = np.zeros(n, dtype=bool)
        giorno = P["ts"] // 86_400_000
        inizio = {}
        for i in range(n):
            inizio.setdefault(giorno[i], i)
        for i in range(n):
            g = giorno[i]
            j = inizio[g]
            h, m = _ora(P["ts"][i])
            fine_giorno[i] = (h == 23 and m == 45)
            # l'intervallo e' noto solo dopo la chiusura delle prime b barre del giorno, complete
            if _ora(P["ts"][j]) == (0, 0) and i >= j + b and np.all(P["ts"][j + 1:j + b] - P["ts"][j:j + b - 1] == 900_000):
                alto[i] = P["h"][j:j + b].max()
                basso[i] = P["l"][j:j + b].min()
                ammesso[i] = h < self.p["ultima_ora"]
        P.update(alto=alto, basso=basso, fine=fine_giorno, ammesso=ammesso)
        return P

    def segnale(self, i, P):
        if not np.isfinite(P["alto"][i]):
            return None
        if self.direzione == "long":
            return Segnale("long", P["basso"][i])
        return Segnale("short", P["alto"][i])

    def condizione(self, i, P):
        if not P["ammesso"][i] or i < 1 or not np.isfinite(P["alto"][i - 1]):
            return False
        if self.direzione == "long":
            return bool(P["c"][i] > P["alto"][i] and P["c"][i - 1] <= P["alto"][i])
        return bool(P["c"][i] < P["basso"][i] and P["c"][i - 1] >= P["basso"][i])

    def uscita(self, i, P, barre):
        return bool(P["fine"][i])


# ---------------------------------------------------------------------------------------------

def _mom(d):
    v = Momento(finestra=42, tenuta=42, stop_atr=3.0)
    v.direzione = d
    return v


def _can(d):
    v = Canale(ingresso=20, uscita=10, stop_atr=2.0)
    v.direzione = d
    return v


def _ecc(d):
    v = Eccesso(finestra=30, k=1.0, tenuta=1, stop_atr=2.0)
    v.direzione = d
    return v


def _mezz(d):
    v = MezzOra(atr_n=48, stop_atr=1.5)
    v.direzione = d
    return v


def _seg(d):
    v = Segue(finestra=168, k=1.5, tenuta=3, stop_atr=2.0)
    v.direzione = d
    return v


def _aff(d, **p):
    v = Affollamento(storia=90, tenuta=3, stop_atr=2.5, **p)
    v.direzione = d
    return v


def _comp(d):
    v = Compressione(bande=20, storia=120, recente=5, stop_atr=2.0)
    v.direzione = d
    return v


def _tondi(d):
    v = NumeriTondi(tenuta=12, stop_atr=1.5)
    v.direzione = d
    return v


def _res(d):
    v = Residuo(finestra_beta=720, finestra_somma=24, ingresso=2.0, rientro=0.5, tenuta=24, stop_atr=2.0)
    v.direzione = d
    return v


def _ape(d):
    v = Apertura(barre_intervallo=4, ultima_ora=20)
    v.direzione = d
    return v


VARIANTI = {
    "ADAUSDT-001": _mom("long"),
    "ADAUSDT-002": _mom("short"),
    "ADAUSDT-003": _can("long"),
    "ADAUSDT-004": _can("short"),
    "ADAUSDT-005": SopraMedia(media=20, stop_atr=3.0),
    "ADAUSDT-006": _ecc("long"),
    "ADAUSDT-007": _ecc("short"),
    "ADAUSDT-008": _mezz("long"),
    "ADAUSDT-009": _mezz("short"),
    "ADAUSDT-010": _seg("long"),
    "ADAUSDT-011": _seg("short"),
    "ADAUSDT-012": _aff("short", quantile=0.9, minimo=0.0003),
    "ADAUSDT-013": _aff("long", quantile=0.1, massimo=0.0),
    "ADAUSDT-014": _comp("long"),
    "ADAUSDT-015": _comp("short"),
    "ADAUSDT-016": Ritracciamento("1d", trend=200, uscita_media=5, rsi_n=2, soglia=5, stop_atr=3.0),
    "ADAUSDT-017": Ritracciamento("4h", trend=200, uscita_media=5, rsi_n=2, soglia=5, stop_atr=3.0),
    "ADAUSDT-018": VolumeAlto("1d", finestra_volume=50, finestra_ritorni=30, quantile=0.9, k_ritorno=1.0, tenuta=5, stop_atr=3.0),
    "ADAUSDT-019": VolumeAlto("4h", finestra_volume=300, finestra_ritorni=180, quantile=0.9, k_ritorno=1.0, tenuta=30, stop_atr=3.0),
    "ADAUSDT-020": _tondi("long"),
    "ADAUSDT-021": _tondi("short"),
    "ADAUSDT-022": _res("long"),
    "ADAUSDT-023": _res("short"),
    "ADAUSDT-024": _ape("long"),
    "ADAUSDT-025": _ape("short"),
}
for _k, _v in VARIANTI.items():
    if _k in ("ADAUSDT-005", "ADAUSDT-016", "ADAUSDT-017", "ADAUSDT-018", "ADAUSDT-019"):
        _v.direzione = "long"

# I-14 Squilibrio degli ordini aggressivi (Chordia e Subrahmanyam) ----------------------------------

class Squilibrio(StopATR):
    tf = "1h"

    def prepara(self, D):
        P = self.base(D)
        q = C.quota_acquisti_aggressivi(D)
        v = P["v"]
        sq = np.where(np.isfinite(q), (2 * q - 1) * v, 0.0)  # acquisti - vendite aggressive, in moneta
        w, m = self.p["finestra"], self.p["storia"]
        cs = np.cumsum(np.insert(sq, 0, 0.0))
        cv = np.cumsum(np.insert(v, 0, 0.0))
        imb = np.full(len(v), np.nan)
        imb[w - 1:] = (cs[w:] - cs[:-w]) / np.maximum(cv[w:] - cv[:-w], 1e-12)
        alto = np.full(len(v), np.nan)
        basso = np.full(len(v), np.nan)
        for i in range(m + w, len(v)):
            st = imb[i - m:i]
            alto[i] = np.quantile(st, self.p["quantile"])
            basso[i] = np.quantile(st, 1 - self.p["quantile"])
        P["imb"], P["alto"], P["basso"] = imb, alto, basso
        P["pronto"] = alto
        return P

    def condizione(self, i, P):
        x = P["imb"][i]
        if not (np.isfinite(x) and np.isfinite(P["alto"][i])):
            return False
        return bool(x > P["alto"][i]) if self.direzione == "long" else bool(x < P["basso"][i])

    def uscita(self, i, P, barre):
        return barre >= self.p["tenuta"]


# I-15 Inversione di breve periodo come fornitura di liquidita' (Nagel) ----------------------------

class Inversione(StopATR):
    tf = "4h"

    def prepara(self, D):
        P = self.base(D)
        w, m = self.p["finestra"], self.p["storia"]
        r = C.rendimento(P["c"], w)
        s = np.full(len(r), np.nan)
        for i in range(m + w, len(r)):
            s[i] = r[i - m:i].std(ddof=1)
        P["r"], P["s"] = r, s
        P["pronto"] = s
        return P

    def condizione(self, i, P):
        r, s = P["r"][i], P["s"][i]
        if not (np.isfinite(r) and np.isfinite(s)):
            return False
        k = self.p["k"]
        return bool(r < -k * s) if self.direzione == "long" else bool(r > k * s)

    def uscita(self, i, P, barre):
        return barre >= self.p["tenuta"]


def _sq(d):
    v = Squilibrio(finestra=24, storia=720, quantile=0.9, tenuta=24, stop_atr=2.0)
    v.direzione = d
    return v


def _inv(d):
    v = Inversione(finestra=6, storia=360, k=2.0, tenuta=6, stop_atr=3.0)
    v.direzione = d
    return v


def _ecc2(d):
    v = Eccesso(finestra=30, k=0.5, tenuta=1, stop_atr=2.0)
    v.direzione = d
    return v


def _comp2(d):
    v = Compressione(bande=20, storia=60, recente=5, stop_atr=2.0)
    v.direzione = d
    return v


VARIANTI.update({
    "ADAUSDT-026": _sq("long"),
    "ADAUSDT-027": _sq("short"),
    "ADAUSDT-028": _inv("long"),
    "ADAUSDT-029": _inv("short"),
    "ADAUSDT-030": _ecc2("long"),
    "ADAUSDT-031": _ecc2("short"),
    "ADAUSDT-032": _comp2("long"),
    "ADAUSDT-033": _comp2("short"),
})

from registrazioni import REG  # noqa: E402,F401
