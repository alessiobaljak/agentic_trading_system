"""Le varianti della campagna AVAXUSDT, una classe per idea (ipotesi.md). Regole esatte qui.

Convenzioni: i e' l'indice della barra appena chiusa; ``livelli`` calcola stop e target alla
chiusura di i (l'ingresso e' all'apertura di i+1); ``esci`` decide alla chiusura di i se
chiudere all'apertura di i+1. "Uscita dopo k barre": la posizione entra all'apertura della
barra e = i_entrata e si chiude all'apertura della barra e + k, cioe' ``esci`` vero quando
i >= e + k - 1.
"""
from __future__ import annotations

import numpy as np

from comune import (Variante, atr, btc_close, deviazione_mobile, ema, funding_ultimo, giorno_settimana,
                    massimo_mobile, minimo_mobile, ora_utc, rsi, sma, taker_buy)


def quantile_mobile(x: np.ndarray, n: int, q: float) -> np.ndarray:
    """Quantile q delle ultime n barre, barra corrente compresa (interpolazione lineare); NaN prima.
    Un valore infinito nella finestra (riscaldamento) rende il risultato NaN."""
    from numpy.lib.stride_tricks import sliding_window_view
    out = np.full(len(x), np.nan)
    if len(x) < n:
        return out
    w = sliding_window_view(x, n)
    v = np.quantile(w, q, axis=1)
    v[~np.isfinite(w).all(axis=1)] = np.nan
    out[n - 1:] = v
    return out


def _ritardo(x: np.ndarray, k: int) -> np.ndarray:
    """x spostato di k barre in avanti (valore di k barre fa); NaN all'inizio."""
    out = np.full(len(x), np.nan)
    if k < len(x):
        out[k:] = x[:-k] if k > 0 else x
    return out


class _UscitaTempo(Variante):
    """Stop in ATR dal close del segnale, nessun target, uscita dopo ``barre`` barre."""

    def _stop(self, ctx, ind, i):
        k = self.parametri.get("mult_atr", 2.0)
        a = ind["atr"][i]
        if not np.isfinite(a) or a <= 0:
            return None
        return (ctx.c[i] - k * a, None) if self.direzione == "long" else (ctx.c[i] + k * a, None)

    def livelli(self, ctx, ind, i):
        return self._stop(ctx, ind, i)

    def esci(self, ctx, ind, i, pos, e):
        return i >= e + int(self.parametri["barre"]) - 1


# --- controllo positivo: legge la barra dopo (lookahead dichiarato) -------------------------

class ControlloPositivo(_UscitaTempo):
    def indicatori(self, ctx):
        prossima_su = np.full(ctx.n, np.nan)
        prossima_su[:-1] = (ctx.c[1:] > ctx.o[1:]).astype(float)  # FUTURO, di proposito
        return {"atr": atr(ctx, int(self.parametri.get("atr_n", 14))), "futuro": prossima_su}

    def riscaldamento(self, ind):
        return int(np.flatnonzero(np.isfinite(ind["atr"]))[0])

    def condizione(self, ctx, ind, i):
        return ind["futuro"][i] == 1.0


# --- I-01 momentum di serie a 1 giorno -----------------------------------------------------

class MomentumSerie(_UscitaTempo):
    def indicatori(self, ctx):
        L = int(self.parametri["lookback"])
        return {"atr": atr(ctx, int(self.parametri.get("atr_n", 14))), "ret": ctx.c / _ritardo(ctx.c, L) - 1}

    def condizione(self, ctx, ind, i):
        r = ind["ret"][i]
        return r > 0 if self.direzione == "long" else r < 0


# --- I-02 Donchian a 4 ore ---------------------------------------------------------------

class Donchian(Variante):
    def indicatori(self, ctx):
        n_in, n_out = int(self.parametri["ingresso"]), int(self.parametri["uscita"])
        return {
            "atr": atr(ctx, int(self.parametri.get("atr", 20))),
            "max_in": _ritardo(massimo_mobile(ctx.h, n_in), 1),
            "min_in": _ritardo(minimo_mobile(ctx.l, n_in), 1),
            "max_out": _ritardo(massimo_mobile(ctx.h, n_out), 1),
            "min_out": _ritardo(minimo_mobile(ctx.l, n_out), 1),
        }

    def condizione(self, ctx, ind, i):
        if self.direzione == "long":
            return ctx.c[i] > ind["max_in"][i]
        return ctx.c[i] < ind["min_in"][i]

    def livelli(self, ctx, ind, i):
        k = self.parametri.get("mult_atr", 2.0)
        a = ind["atr"][i]
        return (ctx.c[i] - k * a, None) if self.direzione == "long" else (ctx.c[i] + k * a, None)

    def esci(self, ctx, ind, i, pos, e):
        if self.direzione == "long":
            return ctx.c[i] < ind["min_out"][i]
        return ctx.c[i] > ind["max_out"][i]


# --- I-03 RSI(2) di Connors a 4 ore ------------------------------------------------------

class Rsi2(Variante):
    def indicatori(self, ctx):
        return {"atr": atr(ctx, int(self.parametri.get("atr_n", 14))), "rsi": rsi(ctx.c, 2), "sma_lunga": sma(ctx.c, int(self.parametri["media_lunga"])),
                "sma_corta": sma(ctx.c, int(self.parametri["media_corta"]))}

    def condizione(self, ctx, ind, i):
        s = self.parametri["soglia"]
        if self.direzione == "long":
            return ind["rsi"][i] < s and ctx.c[i] > ind["sma_lunga"][i]
        return ind["rsi"][i] > 100 - s and ctx.c[i] < ind["sma_lunga"][i]

    def livelli(self, ctx, ind, i):
        k = self.parametri.get("mult_atr", 3.0)
        a = ind["atr"][i]
        return (ctx.c[i] - k * a, None) if self.direzione == "long" else (ctx.c[i] + k * a, None)

    def esci(self, ctx, ind, i, pos, e):
        if self.direzione == "long":
            return ctx.c[i] > ind["sma_corta"][i]
        return ctx.c[i] < ind["sma_corta"][i]


# --- I-04 funding estremo a 8 ore --------------------------------------------------------

class Funding(_UscitaTempo):
    def indicatori(self, ctx):
        return {"atr": atr(ctx, int(self.parametri.get("atr_n", 14))), "funding": funding_ultimo(ctx)}

    def condizione(self, ctx, ind, i):
        f = ind["funding"][i]
        if self.direzione == "short":
            return f >= self.parametri["soglia"]
        return f < self.parametri["soglia"]


# --- I-05 ritardo rispetto a BTC a 1 ora -------------------------------------------------

class RitardoBtc(_UscitaTempo):
    def indicatori(self, ctx):
        b = btc_close(ctx)
        return {"atr": atr(ctx, int(self.parametri.get("atr_n", 14))), "rb": b / _ritardo(b, 1) - 1, "ra": ctx.c / _ritardo(ctx.c, 1) - 1}

    def riscaldamento(self, ind):
        return int(np.flatnonzero(np.isfinite(ind["atr"]))[0])

    def condizione(self, ctx, ind, i):
        rb, ra = ind["rb"][i], ind["ra"][i]
        if not (np.isfinite(rb) and np.isfinite(ra)):
            return False
        s, f = self.parametri["soglia_btc"], self.parametri["frazione"]
        if self.direzione == "long":
            return rb >= s and ra <= f * rb
        return rb <= -s and ra >= f * rb


# --- I-06 momento infragiornaliero a 30 minuti -------------------------------------------

class MomentoGiorno(_UscitaTempo):
    def indicatori(self, ctx):
        giorno = ctx.ts // 86_400_000
        apertura = np.full(ctx.n, np.nan)
        for i in range(ctx.n):
            if i == 0 or giorno[i] != giorno[i - 1]:
                corrente = ctx.o[i] if ctx.ts[i] % 86_400_000 == 0 else np.nan  # solo se la barra 00:00 c'e'
            apertura[i] = corrente
        minuti = (ctx.ts % 86_400_000) // 60_000
        return {"atr": atr(ctx, int(self.parametri.get("atr_n", 14))), "ret_giorno": ctx.c / apertura - 1,
                "ultima": (minuti == int(self.parametri["minuto_segnale"])).astype(float)}

    def riscaldamento(self, ind):
        return int(np.flatnonzero(np.isfinite(ind["atr"]))[0])

    def condizione(self, ctx, ind, i):
        if ind["ultima"][i] != 1.0:
            return False
        r = ind["ret_giorno"][i]
        if not np.isfinite(r):
            return False
        return r > 0 if self.direzione == "long" else r < 0


# --- I-07 lunedi' a 1 giorno -------------------------------------------------------------

class GiornoSettimana(_UscitaTempo):
    def indicatori(self, ctx):
        return {"atr": atr(ctx, int(self.parametri.get("atr_n", 14))), "gs": giorno_settimana(ctx).astype(float)}

    def condizione(self, ctx, ind, i):
        # la barra i e' quella del giorno prima di quello voluto (alla sua chiusura si entra)
        return int(ind["gs"][i]) == (int(self.parametri["giorno"]) - 1) % 7


# --- I-08 reazioni eccessive a 4 ore -----------------------------------------------------

class ReazioneEccessiva(_UscitaTempo):
    def indicatori(self, ctx):
        r = ctx.c / _ritardo(ctx.c, 1) - 1
        sd = _ritardo(deviazione_mobile(np.nan_to_num(r, nan=0.0), int(self.parametri["finestra"])), 1)
        sd[: int(self.parametri["finestra"]) + 1] = np.nan
        return {"atr": atr(ctx, int(self.parametri.get("atr_n", 14))), "z": r / sd}

    def condizione(self, ctx, ind, i):
        z, s = ind["z"][i], self.parametri["soglia_z"]
        return z > s if self.direzione == "long" else z < -s


class Inversione(ReazioneEccessiva):
    """I-13: dopo un salto estremo si entra CONTRO il salto."""

    def condizione(self, ctx, ind, i):
        z, s = ind["z"][i], self.parametri["soglia_z"]
        return z < -s if self.direzione == "long" else z > s


# --- I-14 squilibrio degli ordini aggressivi a 4 ore -------------------------------------

class Squilibrio(_UscitaTempo):
    def indicatori(self, ctx):
        f = int(self.parametri["finestra"])
        quota = taker_buy(ctx) / ctx.v
        q0 = np.nan_to_num(quota, nan=0.5)
        media = _ritardo(sma(q0, f), 1)
        sd = _ritardo(deviazione_mobile(q0, f), 1)
        z = (quota - media) / sd
        return {"atr": atr(ctx, int(self.parametri.get("atr_n", 14))), "z": z}

    def riscaldamento(self, ind):
        return int(np.flatnonzero(np.isfinite(ind["z"]) & np.isfinite(ind["atr"]))[0])

    def condizione(self, ctx, ind, i):
        z, s = ind["z"][i], self.parametri["soglia_z"]
        if not np.isfinite(z):
            return False
        return z > s if self.direzione == "long" else z < -s


# --- I-09 rottura della volatilita' del giorno a 1 ora -----------------------------------

class RotturaGiorno(Variante):
    def indicatori(self, ctx):
        giorno = ctx.ts // 86_400_000
        n = ctx.n
        apertura = np.full(n, np.nan)
        escursione_prec = np.full(n, np.nan)
        gia_sopra = np.zeros(n)
        gia_sotto = np.zeros(n)
        fine_giorno = ((ctx.ts % 86_400_000) // 3_600_000 == 23).astype(float)
        k = self.parametri["k"]
        hi = lo = None
        hi_prec = lo_prec = None
        corrente_ap = np.nan
        visto_su = visto_giu = False
        for i in range(n):
            nuovo = i == 0 or giorno[i] != giorno[i - 1]
            if nuovo:
                if hi is not None and giorno[i] == giorno[i - 1] + 1:
                    hi_prec, lo_prec = hi, lo
                else:
                    hi_prec = lo_prec = None
                hi, lo = ctx.h[i], ctx.l[i]
                corrente_ap = ctx.o[i] if ctx.ts[i] % 86_400_000 == 0 else np.nan
                visto_su = visto_giu = False
            else:
                hi, lo = max(hi, ctx.h[i]), min(lo, ctx.l[i])
            apertura[i] = corrente_ap
            if hi_prec is not None:
                escursione_prec[i] = hi_prec - lo_prec
            # "prima chiusura oltre il livello": le barre precedenti dello stesso giorno non l'hanno fatto
            gia_sopra[i] = 1.0 if visto_su else 0.0
            gia_sotto[i] = 1.0 if visto_giu else 0.0
            if np.isfinite(apertura[i]) and np.isfinite(escursione_prec[i]):
                if ctx.c[i] > apertura[i] + k * escursione_prec[i]:
                    visto_su = True
                if ctx.c[i] < apertura[i] - k * escursione_prec[i]:
                    visto_giu = True
        return {"atr": atr(ctx, int(self.parametri.get("atr_n", 14))), "apertura": apertura, "escursione": escursione_prec,
                "gia_sopra": gia_sopra, "gia_sotto": gia_sotto, "fine_giorno": fine_giorno}

    def riscaldamento(self, ind):
        return int(np.flatnonzero(np.isfinite(ind["atr"]))[0])

    def condizione(self, ctx, ind, i):
        ap, es = ind["apertura"][i], ind["escursione"][i]
        if not (np.isfinite(ap) and np.isfinite(es)) or ind["fine_giorno"][i] == 1.0:
            return False
        k = self.parametri["k"]
        if self.direzione == "long":
            return ctx.c[i] > ap + k * es and ind["gia_sopra"][i] == 0.0
        return ctx.c[i] < ap - k * es and ind["gia_sotto"][i] == 0.0

    def livelli(self, ctx, ind, i):
        ap = ind["apertura"][i]
        if not np.isfinite(ap):
            return None
        return (ap, None)

    def esci(self, ctx, ind, i, pos, e):
        return ind["fine_giorno"][i] == 1.0


# --- I-10 compressione di Bollinger a 4 ore ----------------------------------------------

class Compressione(Variante):
    def indicatori(self, ctx):
        n, k = int(self.parametri["n"]), self.parametri["k"]
        m = sma(ctx.c, n)
        sd = deviazione_mobile(ctx.c, n)
        ampiezza = 2 * k * sd / m
        q = self.parametri.get("quantile")
        if q is None:
            minimo = minimo_mobile(np.nan_to_num(ampiezza, nan=np.inf), int(self.parametri["finestra_min"]))
        else:
            minimo = quantile_mobile(np.nan_to_num(ampiezza, nan=np.inf), int(self.parametri["finestra_min"]), q)
        compresso = np.where(np.isfinite(ampiezza) & np.isfinite(minimo), (ampiezza <= minimo).astype(float), np.nan)
        w = int(self.parametri["entro"]) + 1
        recente = massimo_mobile(np.nan_to_num(compresso, nan=0.0), w)
        recente[~np.isfinite(minimo)] = np.nan
        primo_ok = int(self.parametri["finestra_min"]) + n - 2 + w
        recente[:primo_ok] = np.nan
        return {"atr": atr(ctx, int(self.parametri.get("atr_n", 14))), "media": m, "sup": m + k * sd, "inf": m - k * sd, "recente": recente}

    def condizione(self, ctx, ind, i):
        if ind["recente"][i] != 1.0:
            return False
        return ctx.c[i] > ind["sup"][i] if self.direzione == "long" else ctx.c[i] < ind["inf"][i]

    def livelli(self, ctx, ind, i):
        k = self.parametri.get("mult_atr", 2.0)
        a = ind["atr"][i]
        return (ctx.c[i] - k * a, None) if self.direzione == "long" else (ctx.c[i] + k * a, None)

    def esci(self, ctx, ind, i, pos, e):
        return ctx.c[i] < ind["media"][i] if self.direzione == "long" else ctx.c[i] > ind["media"][i]


# --- I-11 forza relativa contro BTC a 1 giorno -------------------------------------------

class ForzaRelativa(_UscitaTempo):
    def indicatori(self, ctx):
        L = int(self.parametri["lookback"])
        rapporto = ctx.c / btc_close(ctx)
        return {"atr": atr(ctx, int(self.parametri.get("atr_n", 14))), "ret_rel": rapporto / _ritardo(rapporto, L) - 1}

    def condizione(self, ctx, ind, i):
        r = ind["ret_rel"][i]
        return r > 0 if self.direzione == "long" else r < 0


# --- I-12 volume alto a 4 ore ------------------------------------------------------------

class VolumeAlto(_UscitaTempo):
    def indicatori(self, ctx):
        f = int(self.parametri["finestra"])
        media = _ritardo(sma(ctx.v, f), 1)
        return {"atr": atr(ctx, int(self.parametri.get("atr_n", 14))), "rel": ctx.v / media}

    def condizione(self, ctx, ind, i):
        return ind["rel"][i] > self.parametri["multiplo"]


VARIANTI = {
    "V-01": MomentumSerie("AVAXUSDT-V01", "1d", "long", lookback=14, barre=3, mult_atr=2.0),
    "V-02": MomentumSerie("AVAXUSDT-V02", "1d", "short", lookback=14, barre=3, mult_atr=2.0),
    "V-03": Donchian("AVAXUSDT-V03", "4h", "long", ingresso=20, uscita=10, atr=20, mult_atr=2.0),
    "V-04": Donchian("AVAXUSDT-V04", "4h", "short", ingresso=20, uscita=10, atr=20, mult_atr=2.0),
    "V-05": Rsi2("AVAXUSDT-V05", "4h", "long", soglia=10, media_lunga=200, media_corta=5, mult_atr=3.0),
    "V-06": Rsi2("AVAXUSDT-V06", "4h", "short", soglia=10, media_lunga=200, media_corta=5, mult_atr=3.0),
    "V-07": Funding("AVAXUSDT-V07", "8h", "short", soglia=0.0003, barre=3, mult_atr=2.0),
    "V-08": Funding("AVAXUSDT-V08", "8h", "long", soglia=0.0, barre=3, mult_atr=2.0),
    "V-09": RitardoBtc("AVAXUSDT-V09", "1h", "long", soglia_btc=0.01, frazione=0.5, barre=3, mult_atr=2.0),
    "V-10": RitardoBtc("AVAXUSDT-V10", "1h", "short", soglia_btc=0.01, frazione=0.5, barre=3, mult_atr=2.0),
    "V-11": MomentoGiorno("AVAXUSDT-V11", "30m", "long", minuto_segnale=1380, barre=1, mult_atr=2.0),
    "V-12": MomentoGiorno("AVAXUSDT-V12", "30m", "short", minuto_segnale=1380, barre=1, mult_atr=2.0),
    "V-13": GiornoSettimana("AVAXUSDT-V13", "1d", "long", giorno=0, barre=1, mult_atr=2.0),
    "V-14": ReazioneEccessiva("AVAXUSDT-V14", "4h", "long", finestra=180, soglia_z=2.0, barre=6, mult_atr=2.0),
    "V-15": ReazioneEccessiva("AVAXUSDT-V15", "4h", "short", finestra=180, soglia_z=2.0, barre=6, mult_atr=2.0),
    "V-16": RotturaGiorno("AVAXUSDT-V16", "1h", "long", k=0.5),
    "V-17": RotturaGiorno("AVAXUSDT-V17", "1h", "short", k=0.5),
    "V-18": Compressione("AVAXUSDT-V18", "4h", "long", n=20, k=2.0, finestra_min=125, entro=10, mult_atr=2.0),
    "V-19": Compressione("AVAXUSDT-V19", "4h", "short", n=20, k=2.0, finestra_min=125, entro=10, mult_atr=2.0),
    "V-22": Donchian("AVAXUSDT-V22", "4h", "long", ingresso=10, uscita=5, atr=20, mult_atr=2.0),
    "V-23": Donchian("AVAXUSDT-V23", "4h", "short", ingresso=10, uscita=5, atr=20, mult_atr=2.0),
    "V-24": Compressione("AVAXUSDT-V24", "4h", "long", n=20, k=2.0, finestra_min=125, entro=10, quantile=0.2, mult_atr=2.0),
    "V-25": Compressione("AVAXUSDT-V25", "4h", "short", n=20, k=2.0, finestra_min=125, entro=10, quantile=0.2, mult_atr=2.0),
    "V-26": VolumeAlto("AVAXUSDT-V26", "4h", "long", finestra=180, multiplo=2.0, barre=6, mult_atr=2.0),
    "V-27": Inversione("AVAXUSDT-V27", "1h", "long", finestra=720, soglia_z=3.0, barre=3, mult_atr=2.0),
    "V-28": Inversione("AVAXUSDT-V28", "1h", "short", finestra=720, soglia_z=3.0, barre=3, mult_atr=2.0),
    "V-29": Squilibrio("AVAXUSDT-V29", "4h", "long", finestra=180, soglia_z=2.0, barre=6, mult_atr=2.0),
    "V-30": Squilibrio("AVAXUSDT-V30", "4h", "short", finestra=180, soglia_z=2.0, barre=6, mult_atr=2.0),
    "V-31": Compressione("AVAXUSDT-V31", "1h", "long", n=20, k=2.0, finestra_min=125, entro=10, quantile=0.2, mult_atr=2.0),
    "V-32": Compressione("AVAXUSDT-V32", "1h", "short", n=20, k=2.0, finestra_min=125, entro=10, quantile=0.2, mult_atr=2.0),
    "V-20": ForzaRelativa("AVAXUSDT-V20", "1d", "long", lookback=14, barre=3, mult_atr=2.0),
    "V-21": VolumeAlto("AVAXUSDT-V21", "4h", "long", finestra=180, multiplo=3.0, barre=6, mult_atr=2.0),
}

CONTROLLO = ControlloPositivo("AVAXUSDT-CONTROLLO", "1h", "long", barre=1, mult_atr=2.0)
