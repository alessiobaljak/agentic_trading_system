"""Le varianti di ipotesi.md con i loro parametri dichiarati, in un solo posto.

``VARIANTI[nome] = (idea, timeframe, direzione, costruttore della regola, durata attesa in barre)``.
La durata attesa serve SOLO alla stima dei trade (sezione 8), non al test.
"""
from datetime import date

from research.campagne.SOLUSDT.codice import campagna as cp
from research.campagne.SOLUSDT.codice import strategie as st


def _funding(periodo):
    return cp.carica("1h", periodo)[2]


def _btc(tf, periodo):
    return cp.carica_riferimento(tf, periodo)


def regola(nome, periodo=cp.COSTRUZIONE):
    idea, tf, direzione, costruttore, _ = VARIANTI[nome]
    return costruttore(periodo)


VARIANTI = {
    # I-01 momentum 4h
    "I-01-4h-long": ("I-01", "4h", "long", lambda per: st.Momentum(n=30, atr_n=14, stop_mult=2.0), 20),
    "I-01-4h-short": ("I-01", "4h", "short", lambda per: st.Momentum(n=30, atr_n=14, stop_mult=2.0), 20),
    # I-02 funding estremo 1h
    "I-02-1h-short": ("I-02", "1h", "short", lambda per: st.FundingEstremo(finestra=90, percentile=95, soglia=0.0003, atr_n=24, stop_mult=2.0, barre_uscita=24, funding=_funding(per)), 24),
    "I-02-1h-long": ("I-02", "1h", "long", lambda per: st.FundingEstremo(finestra=90, percentile=95, soglia=0.0003, atr_n=24, stop_mult=2.0, barre_uscita=24, funding=_funding(per)), 24),
    # I-03 sessione americana 1h
    "I-03-1h-long": ("I-03", "1h", "long", lambda per: st.Sessione(ora_segnale=12, ora_uscita=21, atr_n=24, stop_mult=3.0, direzione="long", solo_feriali=True), 8),
    # I-04 fine settimana 4h
    "I-04-4h-long": ("I-04", "4h", "long", lambda per: st.FineSettimana(modo="ritraccio", atr_n=42, stop_mult=2.0, soglia_atr=1.0, barre_uscita=6), 6),
    "I-04-4h-short": ("I-04", "4h", "short", lambda per: st.FineSettimana(modo="ritraccio", atr_n=42, stop_mult=2.0, soglia_atr=1.0, barre_uscita=6), 6),
    "I-04-4h-segno-long": ("I-04", "4h", "long", lambda per: st.FineSettimana(modo="segno", atr_n=42, stop_mult=2.0, soglia_atr=0.0, barre_uscita=12, direzione="long"), 12),
    # I-05 continuazione dopo barra estrema 1h
    "I-05-1h-long": ("I-05", "1h", "long", lambda per: st.BarraEstrema(finestra=100, soglia_sigma=3.0, modo="continuazione", atr_n=24, stop_mult=1.5, barre_uscita=12), 12),
    "I-05-1h-short": ("I-05", "1h", "short", lambda per: st.BarraEstrema(finestra=100, soglia_sigma=3.0, modo="continuazione", atr_n=24, stop_mult=1.5, barre_uscita=12), 12),
    # I-06 ritorno dopo barra estrema 1h
    "I-06-1h-long": ("I-06", "1h", "long", lambda per: st.BarraEstrema(finestra=100, soglia_sigma=3.0, modo="ritorno", atr_n=24, stop_mult=1.5, barre_uscita=24, target=True), 24),
    "I-06-1h-short": ("I-06", "1h", "short", lambda per: st.BarraEstrema(finestra=100, soglia_sigma=3.0, modo="ritorno", atr_n=24, stop_mult=1.5, barre_uscita=24, target=True), 24),
    # I-07 canale 4h
    "I-07-4h-long": ("I-07", "4h", "long", lambda per: st.Canale(n_ingresso=20, n_uscita=10, atr_n=20, stop_mult=2.0), 15),
    "I-07-4h-short": ("I-07", "4h", "short", lambda per: st.Canale(n_ingresso=20, n_uscita=10, atr_n=20, stop_mult=2.0), 15),
    # I-07 canale 1h (il 4h e' sotto il minimo di trade: scarto registrato nel log)
    "I-07-1h-long": ("I-07", "1h", "long", lambda per: st.Canale(n_ingresso=20, n_uscita=10, atr_n=20, stop_mult=2.0), 18),
    "I-07-1h-short": ("I-07", "1h", "short", lambda per: st.Canale(n_ingresso=20, n_uscita=10, atr_n=20, stop_mult=2.0), 19),
    # I-06 ritorno a 2,5 sigma (il 3 sigma e' sotto il minimo: scarto registrato nel log)
    "I-06-1h-short-2.5s": ("I-06", "1h", "short", lambda per: st.BarraEstrema(finestra=100, soglia_sigma=2.5, modo="ritorno", atr_n=24, stop_mult=1.5, barre_uscita=24, target=True), 24),
    # I-08 Bollinger 1h
    "I-08-1h-long": ("I-08", "1h", "long", lambda per: st.Bollinger(n=20, k=2.0, atr_n=20, stop_mult=1.5, barre_uscita=24), 24),
    "I-08-1h-short": ("I-08", "1h", "short", lambda per: st.Bollinger(n=20, k=2.0, atr_n=20, stop_mult=1.5, barre_uscita=24), 24),
    # I-09 ritracciamento 1h
    "I-09-1h-long": ("I-09", "1h", "long", lambda per: st.Ritracciamento(n_lunga=200, n_corta=20, atr_n=20, stop_mult=2.0, target_mult=2.0, barre_uscita=48), 48),
    "I-09-1h-short": ("I-09", "1h", "short", lambda per: st.Ritracciamento(n_lunga=200, n_corta=20, atr_n=20, stop_mult=2.0, target_mult=2.0, barre_uscita=48), 48),
    # I-10 ritardo da BTC 1h
    "I-10-1h-long": ("I-10", "1h", "long", lambda per: st.RitardoBtc(btc=_btc("1h", per), n_rend=4, finestra=100, soglia_sigma=2.0, rapporto_max=1.0, atr_n=24, stop_mult=1.5, barre_uscita=4), 4),
    "I-10-1h-short": ("I-10", "1h", "short", lambda per: st.RitardoBtc(btc=_btc("1h", per), n_rend=4, finestra=100, soglia_sigma=2.0, rapporto_max=1.0, atr_n=24, stop_mult=1.5, barre_uscita=4), 4),
    # I-11 volume alto 4h
    "I-11-4h-long": ("I-11", "4h", "long", lambda per: st.VolumeAlto(n_media=50, mult=3.0, atr_n=20, stop_mult=2.0, barre_uscita=18), 18),
    # I-12 compressione 1h
    "I-12-1h-long": ("I-12", "1h", "long", lambda per: st.Compressione(n=20, k=2.0, n_minimo=100, atr_n=20, stop_mult=2.0, target_mult=3.0, barre_uscita=48), 48),
    "I-12-1h-short": ("I-12", "1h", "short", lambda per: st.Compressione(n=20, k=2.0, n_minimo=100, atr_n=20, stop_mult=2.0, target_mult=3.0, barre_uscita=48), 48),
}
