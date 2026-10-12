"""Le varianti della campagna FILUSDT, una funzione per ognuna (regole esatte registrate nel log).

Ogni funzione restituisce una ``quadro.Variante``. Le regole stanno anche in ``ipotesi.md``.
"""
from __future__ import annotations

from typing import Optional

import numpy as np

import quadro as q
from quadro import Variante


def _stop_atr(direzione: str, n_atr: int, k: float):
    def f(s):
        a = q.atr(s, n_atr)
        return s.c - k * a if direzione == "long" else s.c + k * a
    return f


# ---------------------------------------------------------------------------
# Controllo positivo degli strumenti (lezioni/metodo.md): NON e' una variante.
# ---------------------------------------------------------------------------

def controllo_positivo() -> Variante:
    """Lookahead dichiarato: entra long se la barra SUCCESSIVA chiude oltre l'1% sopra la sua apertura."""
    def ingresso(s):
        prossima_su = np.zeros(len(s.c), dtype=bool)
        prossima_su[:-1] = s.c[1:] > s.o[1:] * 1.01
        return prossima_su
    return Variante("FILUSDT-CONTROLLO", "4h", "long", ingresso, _stop_atr("long", 14, 2.0), barre_max=1,
                    descrizione="lookahead dichiarato: legge la barra dopo")


# ---------------------------------------------------------------------------
# I-01 Momento della serie storica (4h, 42 barre)
# ---------------------------------------------------------------------------

def i01(direzione: str, id_: str) -> Variante:
    def ingresso(s):
        r = q.rendimento(s.c, 42)
        return (r > 0) if direzione == "long" else (r < 0)
    return Variante(id_, "4h", direzione, ingresso, _stop_atr(direzione, 14, 2.0), barre_max=42,
                    descrizione=f"I-01 momento settimanale {direzione}")


# ---------------------------------------------------------------------------
# I-02 Rottura del canale (4h, 30 barre, uscita a canale opposto di 15 barre)
# ---------------------------------------------------------------------------

def i02(direzione: str, id_: str, n_in: int = 30, n_out: int = 15) -> Variante:
    def ingresso(s):
        if direzione == "long":
            return s.c > q.massimo_precedente(s.h, n_in)
        return s.c < q.minimo_precedente(s.l, n_in)

    def uscita(s):
        if direzione == "long":
            return s.c < q.minimo_precedente(s.l, n_out)
        return s.c > q.massimo_precedente(s.h, n_out)
    return Variante(id_, "4h", direzione, ingresso, _stop_atr(direzione, 14, 2.0), uscita=uscita,
                    descrizione=f"I-02 rottura del canale {direzione}")


# ---------------------------------------------------------------------------
# I-03 Inversione dopo movimenti estremi di 24 ore (1h)
# ---------------------------------------------------------------------------

def _z24(s):
    r1 = q.rendimento(s.c, 1)
    sd = q.dev_std_mobile(np.nan_to_num(r1, nan=0.0), 720)
    sd[:720] = np.nan
    return q.rendimento(s.c, 24) / (sd * np.sqrt(24))


def i03(direzione: str, id_: str) -> Variante:
    def ingresso(s):
        z = _z24(s)
        return (z < -2) if direzione == "long" else (z > 2)
    return Variante(id_, "1h", direzione, ingresso, _stop_atr(direzione, 24, 3.0), barre_max=24,
                    descrizione=f"I-03 inversione dopo 24 ore estreme {direzione}")


# ---------------------------------------------------------------------------
# I-04 Barre estreme con volume alto (1h)
# ---------------------------------------------------------------------------

def _sd_orari(s):
    r1 = q.rendimento(s.c, 1)
    sd = q.dev_std_mobile(np.nan_to_num(r1, nan=0.0), 720)
    sd[:720] = np.nan
    return r1, sd


def _volume_relativo(s, n):
    v = np.nan_to_num(s.v_usdt, nan=0.0)
    media_prec = np.full(v.size, np.nan)
    cs = np.cumsum(np.insert(v, 0, 0.0))
    media_prec[n:] = (cs[n:-1] - cs[:-n - 1]) / n
    return v / media_prec


def i04(direzione: str, id_: str) -> Variante:
    def ingresso(s):
        r1, sd = _sd_orari(s)
        vr = _volume_relativo(s, 168)
        estremo = (r1 < -3 * sd) if direzione == "long" else (r1 > 3 * sd)
        return estremo & (vr > 3)
    return Variante(id_, "1h", direzione, ingresso, _stop_atr(direzione, 24, 1.5), barre_max=12,
                    descrizione=f"I-04 barra estrema con volume alto {direzione}")


# ---------------------------------------------------------------------------
# I-05 RSI(2) nel trend (4h)
# ---------------------------------------------------------------------------

def i05(direzione: str, id_: str) -> Variante:
    def ingresso(s):
        m200, r2 = q.sma(s.c, 200), q.rsi(s.c, 2)
        if direzione == "long":
            return (s.c > m200) & (r2 < 10)
        return (s.c < m200) & (r2 > 90)

    def uscita(s):
        m5 = q.sma(s.c, 5)
        return (s.c > m5) if direzione == "long" else (s.c < m5)
    return Variante(id_, "4h", direzione, ingresso, _stop_atr(direzione, 14, 1.5), uscita=uscita,
                    descrizione=f"I-05 RSI(2) nel trend {direzione}")


# ---------------------------------------------------------------------------
# I-06 Funding (8h)
# ---------------------------------------------------------------------------

def funding_medio_ultimi(s, n=3):
    """Media degli ultimi n settlement con istante <= chiusura della barra (noti alla chiusura)."""
    ts_f = np.array([t for t, _ in s.funding], dtype=np.int64)
    tassi = np.array([r for _, r in s.funding])
    out = np.full(len(s.c), np.nan)
    for i, ct in enumerate(s.close_ts):
        k = int(np.searchsorted(ts_f, ct, side="right"))
        if k >= n:
            out[i] = tassi[k - n:k].mean()
    return out


def i06(direzione: str, id_: str) -> Variante:
    def ingresso(s):
        f = funding_medio_ultimi(s, 3)
        return (f > 0.0003) if direzione == "short" else (f < -0.0001)
    return Variante(id_, "8h", direzione, ingresso, _stop_atr(direzione, 14, 1.0), barre_max=9,
                    descrizione=f"I-06 funding {direzione}")


# ---------------------------------------------------------------------------
# I-07 Lunedi' (1d)
# ---------------------------------------------------------------------------

def i07(id_: str) -> Variante:
    def ingresso(s):
        return q.giorno_settimana(s) == 6  # la candela della domenica: si entra all'apertura del lunedi'

    def stop(s):
        return s.c * 0.94
    return Variante(id_, "1d", "long", ingresso, stop, barre_max=1, descrizione="I-07 lunedi' long")


# ---------------------------------------------------------------------------
# I-08 Ritardo rispetto a BTC (1h)
# ---------------------------------------------------------------------------

def i08(direzione: str, id_: str, soglia: float = 0.02, barre_rend: int = 4, barre_max: int = 8,
        n_atr: int = 24, k_atr: float = 1.5, tf: str = "1h") -> Variante:
    def ingresso(s):
        rb, rf = q.rendimento(s.btc_c, barre_rend), q.rendimento(s.c, barre_rend)
        if direzione == "long":
            return (rb > soglia) & (rf < rb)
        return (rb < -soglia) & (rf > rb)
    return Variante(id_, tf, direzione, ingresso, _stop_atr(direzione, n_atr, k_atr), barre_max=barre_max,
                    descrizione=f"I-08 ritardo rispetto a BTC {direzione}")


# ---------------------------------------------------------------------------
# I-09 Compressione e rottura delle bande (4h)
# ---------------------------------------------------------------------------

def i09(direzione: str, id_: str) -> Variante:
    def bande(s):
        m = q.sma(s.c, 20)
        sd = q.dev_std_mobile(s.c, 20)
        return m, m + 2 * sd, m - 2 * sd

    def ingresso(s):
        m, su, giu = bande(s)
        amp = (su - giu) / m
        n = len(s.c)
        compressa = np.zeros(n, dtype=bool)
        for i in range(120 + 19, n):
            rif = amp[i - 120:i]
            compressa[i] = amp[i] < np.nanpercentile(rif, 20)
        recente = np.zeros(n, dtype=bool)
        for i in range(5, n):
            recente[i] = compressa[i - 5:i].any()
        if direzione == "long":
            return recente & (s.c > su)
        return recente & (s.c < giu)

    def uscita(s):
        m = q.sma(s.c, 20)
        return (s.c < m) if direzione == "long" else (s.c > m)
    return Variante(id_, "4h", direzione, ingresso, _stop_atr(direzione, 14, 1.5), uscita=uscita,
                    descrizione=f"I-09 compressione e rottura {direzione}")


# ---------------------------------------------------------------------------
# I-10 Giorni di volume molto alto (1d)
# ---------------------------------------------------------------------------

def i10(id_: str) -> Variante:
    def ingresso(s):
        v = s.v_usdt
        out = np.zeros(len(v), dtype=bool)
        for i in range(49, len(v)):
            finestra = np.sort(v[i - 49:i + 1])
            out[i] = v[i] >= finestra[-5]
        return out
    return Variante(id_, "1d", "long", ingresso, _stop_atr("long", 14, 1.0), barre_max=3,
                    descrizione="I-10 volume alto long")


# ---------------------------------------------------------------------------
# I-11 Squilibrio degli ordini aggressivi (1h)
# ---------------------------------------------------------------------------

def _z_squilibrio(s):
    tb = q.acquisti_taker_usdt(s)
    v = s.v_usdt
    netto = np.nan_to_num(2 * tb - v, nan=0.0)
    vv = np.nan_to_num(v, nan=0.0)
    cs_n = np.cumsum(np.insert(netto, 0, 0.0))
    cs_v = np.cumsum(np.insert(vv, 0, 0.0))
    S = np.full(len(v), np.nan)
    S[23:] = (cs_n[24:] - cs_n[:-24]) / (cs_v[24:] - cs_v[:-24])
    z = np.full(len(v), np.nan)
    for i in range(24 + 720, len(v)):
        rif = S[i - 720:i]
        z[i] = (S[i] - rif.mean()) / rif.std(ddof=1)
    return z


def i11(direzione: str, id_: str) -> Variante:
    def ingresso(s):
        z = _z_squilibrio(s)
        return (z > 2) if direzione == "long" else (z < -2)
    return Variante(id_, "1h", direzione, ingresso, _stop_atr(direzione, 24, 1.5), barre_max=24,
                    descrizione=f"I-11 squilibrio degli ordini {direzione}")


# ---------------------------------------------------------------------------
# I-12 Stagionalita' della fascia di 4 ore (4h)
# ---------------------------------------------------------------------------

def _t_fascia_successiva(s, n_oss=30):
    """t dei rendimenti delle ultime n_oss barre della fascia (ora del giorno) della barra successiva.

    La fascia e' lunga quanto la barra: 6 fasce al giorno a 4 ore, 12 a 2 ore, 4 a 6 ore.
    """
    durata = q.MS[s.tf]
    n_fasce = 86_400_000 // durata
    fascia = (s.ts // durata) % n_fasce
    rend = s.c / s.o - 1.0
    storia = {f: [] for f in range(n_fasce)}
    t = np.full(len(s.c), np.nan)
    for i in range(len(s.c)):
        storia[int(fascia[i])].append(rend[i])
        prossima = (int(fascia[i]) + 1) % n_fasce
        h = storia[prossima]
        if len(h) >= n_oss:
            x = np.array(h[-n_oss:])
            sd = x.std(ddof=1)
            t[i] = x.mean() / (sd / np.sqrt(n_oss)) if sd > 0 else np.nan
    return t


def i12(direzione: str, id_: str, n_oss: int = 30, soglia_t: float = 1.5, k_atr: float = 1.5,
        n_atr: int = 14, barre_max: int = 1, tf: str = "4h") -> Variante:
    def ingresso(s):
        t = _t_fascia_successiva(s, n_oss)
        return (t > soglia_t) if direzione == "long" else (t < -soglia_t)
    return Variante(id_, tf, direzione, ingresso, _stop_atr(direzione, n_atr, k_atr), barre_max=barre_max,
                    descrizione=f"I-12 stagionalita' della fascia {direzione}")


# ---------------------------------------------------------------------------
# I-13 Rottura di volatilita' dall'apertura del giorno (1h)
# ---------------------------------------------------------------------------

def _giorno_apertura_escursione(s):
    giorno = s.ts // 86_400_000
    n = len(s.c)
    apertura = np.full(n, np.nan)
    escursione_prec = np.full(n, np.nan)
    alto, basso, ap = {}, {}, {}
    for i in range(n):
        d = int(giorno[i])
        if d not in ap:
            ap[d] = s.o[i]
            alto[d], basso[d] = s.h[i], s.l[i]
        else:
            alto[d], basso[d] = max(alto[d], s.h[i]), min(basso[d], s.l[i])
        apertura[i] = ap[d]
        if d - 1 in alto:
            escursione_prec[i] = alto[d - 1] - basso[d - 1]
    return giorno, apertura, escursione_prec


def _ultima_barra_del_giorno(s):
    """True per la barra che chiude alla fine del giorno UTC (23 a 1h, 23:30 a 30m, 22 a 2h)."""
    return ((s.close_ts + 1) % 86_400_000) == 0


def i13(direzione: str, id_: str, k: float = 0.6, tf: str = "1h") -> Variante:
    def ingresso(s):
        giorno, ap, esc = _giorno_apertura_escursione(s)
        if direzione == "long":
            cond = s.c > ap + k * esc
        else:
            cond = s.c < ap - k * esc
        cond = cond & ~_ultima_barra_del_giorno(s)
        prima = np.zeros(len(s.c), dtype=bool)
        visto = set()
        for i in range(len(s.c)):
            if cond[i] and int(giorno[i]) not in visto:
                prima[i] = True
                visto.add(int(giorno[i]))
        return prima

    def stop(s):
        _, ap, _ = _giorno_apertura_escursione(s)
        return ap

    def uscita(s):
        return _ultima_barra_del_giorno(s)
    return Variante(id_, tf, direzione, ingresso, stop, uscita=uscita,
                    descrizione=f"I-13 rottura di volatilita' {direzione}")


# ---------------------------------------------------------------------------
# I-14 Shock di illiquidita' (4h)
# ---------------------------------------------------------------------------

def i14(id_: str) -> Variante:
    def ingresso(s):
        r1 = np.abs(q.rendimento(s.c, 1))
        illiq = r1 / s.v_usdt
        illiq = np.nan_to_num(illiq, nan=0.0)
        cs = np.cumsum(np.insert(illiq, 0, 0.0))
        n = len(illiq)
        out = np.zeros(n, dtype=bool)
        for i in range(186, n):
            recente = (cs[i + 1] - cs[i - 5]) / 6
            prima = (cs[i - 5] - cs[i - 185]) / 180
            out[i] = prima > 0 and recente > 2 * prima
        return out
    return Variante(id_, "4h", "long", ingresso, _stop_atr("long", 14, 1.5), barre_max=18,
                    descrizione="I-14 shock di illiquidita' long")


# ---------------------------------------------------------------------------
# I-15 Momento dentro il giorno (4h, ultima fascia)
# ---------------------------------------------------------------------------

def rend_btc_dal_giorno(s, barre_dal_giorno: int = 5):
    """Rendimento di BTC dall'apertura del giorno UTC (close della barra che chiude a mezzanotte).

    A 4 ore, alla chiusura della barra 16-20 la barra che chiude a mezzanotte e' 5 barre prima;
    se in mezzo c'e' un buco della serie (ts non a distanza giusta) il valore e' NaN.
    """
    out = np.full(len(s.c), np.nan)
    k = barre_dal_giorno
    giusto = (s.ts[k:] - s.ts[:-k]) == k * q.MS[s.tf]
    out[k:] = np.where(giusto, s.btc_c[k:] / s.btc_c[:-k] - 1, np.nan)
    return out


def i15(direzione: str, id_: str, atr_pct_minimo: float = 0.0, tf: str = "4h", ora_barra_segnale: int = 16,
        barre_max: int = 1, n_atr_filtro: int = 14, n_atr_stop: int = 14, k_atr: float = 1.5,
        btc_giorno_minimo: Optional[float] = None, btc_giorno_massimo: Optional[float] = None,
        stop_massimo_pct: Optional[float] = None, vol_rel_minimo: Optional[float] = None,
        atr_pct_massimo: Optional[float] = None) -> Variante:
    def ingresso(s):
        _, ap, _ = _giorno_apertura_escursione(s)
        alle_20 = q.ora_utc(s) == ora_barra_segnale  # a 4h la barra 16-20 UTC: alla sua chiusura sono le 20
        volatile = (q.atr(s, n_atr_filtro) / s.c) > atr_pct_minimo
        if atr_pct_massimo is not None:
            volatile = volatile & ((q.atr(s, n_atr_filtro) / s.c) < atr_pct_massimo)
        base = alle_20 & volatile & ((s.c > ap) if direzione == "long" else (s.c < ap))
        if btc_giorno_minimo is not None:
            base = base & (rend_btc_dal_giorno(s) > btc_giorno_minimo)
        if btc_giorno_massimo is not None:
            base = base & (rend_btc_dal_giorno(s) < btc_giorno_massimo)
        if vol_rel_minimo is not None:
            # volume USDT della barra / media dei volumi delle 42 barre fino alla corrente (7 giorni a 4h)
            vol_rel = s.v_usdt / q.sma(np.nan_to_num(s.v_usdt), 42)
            base = base & (vol_rel > vol_rel_minimo)
        return base

    def stop(s):
        st = _stop_atr(direzione, n_atr_stop, k_atr)(s)
        if stop_massimo_pct is None:
            return st
        if direzione == "long":
            return np.maximum(st, s.c * (1 - stop_massimo_pct))
        return np.minimum(st, s.c * (1 + stop_massimo_pct))
    return Variante(id_, tf, direzione, ingresso, stop, barre_max=barre_max,
                    descrizione=f"I-15 momento dentro il giorno {direzione}")


# ---------------------------------------------------------------------------
# I-16 Incrocio del close con la media a 50 barre (4h)
# ---------------------------------------------------------------------------

def i16(direzione: str, id_: str) -> Variante:
    def ingresso(s):
        m = q.sma(s.c, 50)
        prima_c, prima_m = np.roll(s.c, 1), np.roll(m, 1)
        prima_m[0] = np.nan
        if direzione == "long":
            return (s.c > m) & (prima_c <= prima_m)
        return (s.c < m) & (prima_c >= prima_m)

    def uscita(s):
        m = q.sma(s.c, 50)
        return (s.c < m) if direzione == "long" else (s.c > m)
    return Variante(id_, "4h", direzione, ingresso, _stop_atr(direzione, 14, 1.5), uscita=uscita,
                    descrizione=f"I-16 incrocio con la media {direzione}")


TUTTE = {
    "controllo": controllo_positivo,
    "FILUSDT-001": lambda: i01("long", "FILUSDT-001"),
    "FILUSDT-002": lambda: i01("short", "FILUSDT-002"),
    "FILUSDT-003": lambda: i02("long", "FILUSDT-003"),
    "FILUSDT-004": lambda: i02("short", "FILUSDT-004"),
    "FILUSDT-005": lambda: i03("long", "FILUSDT-005"),
    "FILUSDT-006": lambda: i03("short", "FILUSDT-006"),
    "FILUSDT-007": lambda: i02("long", "FILUSDT-007", 20, 10),
    "FILUSDT-008": lambda: i02("short", "FILUSDT-008", 20, 10),
    "FILUSDT-009": lambda: i04("long", "FILUSDT-009"),
    "FILUSDT-010": lambda: i04("short", "FILUSDT-010"),
    "FILUSDT-011": lambda: i05("long", "FILUSDT-011"),
    "FILUSDT-012": lambda: i05("short", "FILUSDT-012"),
    "FILUSDT-013": lambda: i06("short", "FILUSDT-013"),
    "FILUSDT-014": lambda: i06("long", "FILUSDT-014"),
    "FILUSDT-015": lambda: i07("FILUSDT-015"),
    "FILUSDT-016": lambda: i08("long", "FILUSDT-016"),
    "FILUSDT-017": lambda: i08("short", "FILUSDT-017"),
    "FILUSDT-018": lambda: i09("long", "FILUSDT-018"),
    "FILUSDT-019": lambda: i09("short", "FILUSDT-019"),
    "FILUSDT-020": lambda: i10("FILUSDT-020"),
    "FILUSDT-021": lambda: i11("long", "FILUSDT-021"),
    "FILUSDT-022": lambda: i11("short", "FILUSDT-022"),
    "FILUSDT-023": lambda: i12("long", "FILUSDT-023"),
    "FILUSDT-024": lambda: i12("short", "FILUSDT-024"),
    "FILUSDT-025": lambda: i13("long", "FILUSDT-025"),
    "FILUSDT-026": lambda: i13("short", "FILUSDT-026"),
    "FILUSDT-027": lambda: i14("FILUSDT-027"),
    "FILUSDT-028": lambda: i15("long", "FILUSDT-028"),
    "FILUSDT-029": lambda: i15("short", "FILUSDT-029"),
    "FILUSDT-030": lambda: i16("long", "FILUSDT-030"),
    "FILUSDT-031": lambda: i16("short", "FILUSDT-031"),
    # Ritocchi (regola 6), in ordine di registrazione
    "FILUSDT-032": lambda: i15("long", "FILUSDT-032", atr_pct_minimo=0.028),
    "FILUSDT-033": lambda: i15("long", "FILUSDT-033", btc_giorno_minimo=0.005),
    "FILUSDT-034": lambda: i15("long", "FILUSDT-034", atr_pct_minimo=0.028, btc_giorno_minimo=0.005),
    "FILUSDT-035": lambda: i15("long", "FILUSDT-035", atr_pct_minimo=0.028, btc_giorno_minimo=0.024),
    "FILUSDT-036": lambda: i15("long", "FILUSDT-036", atr_pct_minimo=0.028, btc_giorno_minimo=0.005,
                               stop_massimo_pct=0.055),
    "FILUSDT-037": lambda: i15("short", "FILUSDT-037", btc_giorno_massimo=-0.005),
    "FILUSDT-038": lambda: i15("short", "FILUSDT-038", btc_giorno_massimo=-0.005, vol_rel_minimo=0.68),
    "FILUSDT-039": lambda: i15("short", "FILUSDT-039", btc_giorno_massimo=-0.005, atr_pct_massimo=0.043),
}

# Verifiche della Fase 4 per il candidato FILUSDT-016 (le regole del candidato non cambiano:
# ogni voce e' un caso di verifica, mai una variante da adottare).
_V16 = {
    "R01": dict(soglia=0.016), "R02": dict(soglia=0.024),
    "R03": dict(barre_rend=3), "R04": dict(barre_rend=5),
    "R05": dict(barre_max=6), "R06": dict(barre_max=10),
    "R07": dict(n_atr=19), "R08": dict(n_atr=29),
    "R09": dict(k_atr=1.2), "R10": dict(k_atr=1.8),
    "T30m": dict(tf="30m", barre_rend=8, barre_max=16, n_atr=48),
    "T2h": dict(tf="2h", barre_rend=2, barre_max=4, n_atr=12),
}
for _k, _p in _V16.items():
    TUTTE[f"FILUSDT-016-{_k}"] = (lambda p=_p, k=_k: i08("long", f"FILUSDT-016-{k}", **p))

# Verifiche della Fase 4 per il candidato FILUSDT-024 (I-12 short, 4h).
_V24 = {
    "R01": dict(n_oss=24), "R02": dict(n_oss=36),
    "R03": dict(soglia_t=1.2), "R04": dict(soglia_t=1.8),
    "R05": dict(k_atr=1.2), "R06": dict(k_atr=1.8),
    "R07": dict(n_atr=11), "R08": dict(n_atr=17),
    "R10": dict(barre_max=2),
    "T2h": dict(tf="2h", barre_max=2, n_atr=28),
    "T6h": dict(tf="6h", barre_max=1, n_atr=9),
}
for _k, _p in _V24.items():
    TUTTE[f"FILUSDT-024-{_k}"] = (lambda p=_p, k=_k: i12("short", f"FILUSDT-024-{k}", **p))

# Verifiche della Fase 4 per il candidato FILUSDT-025 (I-13 long, 1h).
_V25 = {"R01": dict(k=0.48), "R02": dict(k=0.72), "T30m": dict(tf="30m"), "T2h": dict(tf="2h")}
for _k, _p in _V25.items():
    TUTTE[f"FILUSDT-025-{_k}"] = (lambda p=_p, k=_k: i13("long", f"FILUSDT-025-{k}", **p))

# Verifiche della Fase 4 per il candidato FILUSDT-032 (ritocco di 028: I-15 long con filtro di volatilita').
_V32 = {
    "R01": dict(atr_pct_minimo=0.0224), "R02": dict(atr_pct_minimo=0.0336),
    "R03": dict(n_atr_filtro=11), "R04": dict(n_atr_filtro=17),
    "R05": dict(n_atr_stop=11), "R06": dict(n_atr_stop=17),
    "R07": dict(k_atr=1.2), "R08": dict(k_atr=1.8),
    "R10": dict(barre_max=2),
    "T2h": dict(tf="2h", ora_barra_segnale=18, barre_max=2, n_atr_filtro=28, n_atr_stop=28),
    "T6h": dict(tf="6h", ora_barra_segnale=12, barre_max=1, n_atr_filtro=9, n_atr_stop=9),
}
for _k, _p in _V32.items():
    TUTTE[f"FILUSDT-032-{_k}"] = (lambda p=_p, k=_k: i15("long", f"FILUSDT-032-{k}", **dict({"atr_pct_minimo": 0.028}, **p)))
