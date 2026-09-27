# 0310-ingressi-orca.req

_eseguito: 2026-09-27 13:13 UTC_

**richiesta:** `ingressi-orca`
**eseguito:** `.venv/bin/python -m scripts.ingressi_report --coppia ORCAUSDT/gen_6d06dca0 --dettaglio`
**esito:** codice 0 in 48.3s

```
[firebase] connesso (Firestore + RTDB)
==========================================================================
INGRESSI DEL PAPER, TRADE PER TRADE: dove il motore non entra, e perche'
==========================================================================
PAPER: 126 trade chiusi su 62 coppie · rigirate 1 · tolleranza 2 barre · deadline 720s

── ORCAUSDT|gen_6d06dca0 · 3 trade · 15m · scala 1.5/3/5 · BE si · keep globale
[backtest] cache ESTESA di 149 candele (invece di riscaricarne 63353) (ORCAUSDT 15m)
[backtest] dati da cache: 63353 candele (ORCAUSDT 15m)
  motore: 93 trade sulla storia intera, 0 dal primo trade del paper · cooldown 4 barre
  #1  18 Sep 03:30 UTC  short entry 1.42  pnl -3.02 USDT (stop_loss)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore bull_trending / paper bull_trending
  #2  20 Sep 16:30 UTC  short entry 1.438  pnl -2.99 USDT (stop_loss)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore bear_trending / paper bear_trending
  #3  27 Sep 07:30 UTC  short entry 1.694  pnl -1.43 USDT (stop_loss)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore sideways / paper sideways
  DETTAGLIO ORCAUSDT|gen_6d06dca0
    spec: rsi_extreme low=20.0 high=75.0 AND session hour_from=8 hour_to=16 · timeframe 15m · solo entrambi · mercato no · 1h no · volume_mult 0 · min_adx 0
    spec nel registro: genitore — · ipotesi — · record coppia: pass 4 · sostituita_da — · genitore —
    #1 18 Sep 03:30 UTC short entry 1.42 pnl -3.02 · classe REGOLA_NON_SCATTA · IGNOTO
       regola sul trade: — → non registrata
       motore k-2 18 Sep 03:00 close 1.402: rsi_extreme L=no S=no (low=20 high=75 rsi=68.18) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta: fermano rsi_extreme)
       motore k-1 18 Sep 03:15 close 1.41: rsi_extreme L=no S=no (low=20 high=75 rsi=72.69) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta: fermano rsi_extreme)
       motore k+0 18 Sep 03:30 close 1.419: rsi_extreme L=no S=si (low=20 high=75 rsi=76.69) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta)
       motore k+1 18 Sep 03:45 close 1.418: rsi_extreme L=no S=si (low=20 high=75 rsi=75.37) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta)
       paper (prezzo d'ingresso 1.42): rsi_extreme L=no S=si (low=20 high=75 rsi=76.69) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta)
       paper (chiusura 1.419): rsi_extreme L=no S=si (low=20 high=75 rsi=76.69) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta)
       indicatori motore/paper: uguali (entro 5%)
       DIAGNOSI: sui valori scritti dal paper la regola NON scatta col prezzo d'ingresso: frenano session — NB: il prezzo su cui il bot ha deciso (vivo) non e' sul trade, `entry_price` porta lo slippage: se la feature che frena guarda il prezzo, vale la riga «prezzo di decisione ≈»; se guarda un indicatore, i valori registrati non sono quelli su cui il bot ha deciso
    #2 20 Sep 16:30 UTC short entry 1.438 pnl -2.99 · classe REGOLA_NON_SCATTA · IGNOTO
       regola sul trade: — → non registrata
       motore k-2 20 Sep 16:00 close 1.42: rsi_extreme L=no S=no (low=20 high=75 rsi=67.9) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta: fermano rsi_extreme)
       motore k-1 20 Sep 16:15 close 1.425: rsi_extreme L=no S=no (low=20 high=75 rsi=71.28) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta: fermano rsi_extreme)
       motore k+0 20 Sep 16:30 close 1.438: rsi_extreme L=no S=si (low=20 high=75 rsi=77.81) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta)
       motore k+1 20 Sep 16:45 close 1.438: rsi_extreme L=no S=si (low=20 high=75 rsi=77.81) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta)
       paper (prezzo d'ingresso 1.438): rsi_extreme L=no S=si (low=20 high=75 rsi=77.81) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta)
       paper (chiusura 1.438): rsi_extreme L=no S=si (low=20 high=75 rsi=77.81) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta)
       indicatori motore/paper: uguali (entro 5%)
       DIAGNOSI: sui valori scritti dal paper la regola NON scatta col prezzo d'ingresso: frenano session — NB: il prezzo su cui il bot ha deciso (vivo) non e' sul trade, `entry_price` porta lo slippage: se la feature che frena guarda il prezzo, vale la riga «prezzo di decisione ≈»; se guarda un indicatore, i valori registrati non sono quelli su cui il bot ha deciso
    #3 27 Sep 07:30 UTC short entry 1.694 pnl -1.43 · classe REGOLA_NON_SCATTA · IGNOTO
       regola sul trade: [gen] rsi_extreme low=20.0 high=75.0 AND session hour_from=8 hour_to=16 → coincide con la spec
       feats_at_entry: stoch_k=96.55 atr_pct=0.0056 dist_ema=0.0215 hour=7 bb_pos=1.123 adx=75.51 vol_ratio=2.095 stop_pct=0.0139 r1=1.5 rsi=79.12 market_up=1
       motore k-2 27 Sep 07:00 close 1.673: rsi_extreme L=no S=no (low=20 high=75 rsi=70.46) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta: fermano rsi_extreme)
       motore k-1 27 Sep 07:15 close 1.68: rsi_extreme L=no S=no (low=20 high=75 rsi=73.75) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta: fermano rsi_extreme)
       motore k+0 27 Sep 07:30 close 1.695: rsi_extreme L=no S=si (low=20 high=75 rsi=79.12) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta)
       motore k+1 27 Sep 07:45 close 1.716: rsi_extreme L=no S=si (low=20 high=75 rsi=84.04) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta)
       paper (prezzo d'ingresso 1.694): rsi_extreme L=no S=si (low=20 high=75 rsi=79.12) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta)
       paper (chiusura 1.695): rsi_extreme L=no S=si (low=20 high=75 rsi=79.12) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta)
       paper (prezzo di decisione ≈1.694, da feats.dist_ema): rsi_extreme L=no S=si (low=20 high=75 rsi=79.12) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta)
       indicatori motore/paper: uguali (entro 5%)
       DIAGNOSI: sui valori scritti dal paper la regola NON scatta col prezzo d'ingresso: frenano session — NB: il prezzo su cui il bot ha deciso (vivo) non e' sul trade, `entry_price` porta lo slippage: se la feature che frena guarda il prezzo, vale la riga «prezzo di decisione ≈»; se guarda un indicatore, i valori registrati non sono quelli su cui il bot ha deciso
  ABBINATI 0/3 · «come il bot» (da 200 barre prima del paper): 0/3 abbinati, 0 trade del motore
  [47s]

==========================================================================
RIASSUNTO
==========================================================================
  trade classificati: 3 · abbinati 0 (0%) · «come il bot» 0%
  per classe:
    REGOLA_NON_SCATTA        3
  REGOLA_NON_SCATTA per sotto-motivo:
    IGNOTO                   3
  per coppia (abbinati/trade):
    ORCAUSDT|gen_6d06dca0               0/3   (  0%) · come il bot 0/3
  coppie con piu' non abbinati: ORCAUSDT|gen_6d06dca0 (3)

LETTURA: 0/3 ingressi abbinati (0%): la regola non scatta e i dati non spiegano perche' (3 su 3 non abbinati) — da guardare a mano.
  NB: i trade del motore sono simulati sulla storia intera, senza holdout; «stop» del
      motore e' dedotto (il SimTrade non porta il motivo). Questo comando misura e basta.
[ingressi] finito in 47s

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
