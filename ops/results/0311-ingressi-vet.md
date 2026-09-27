# 0311-ingressi-vet.req

_eseguito: 2026-09-27 13:15 UTC_

**richiesta:** `ingressi-vet`
**eseguito:** `.venv/bin/python -m scripts.ingressi_report --coppia VETUSDT/gen_6d06dca0 --dettaglio`
**esito:** codice 0 in 121.0s

```
[firebase] connesso (Firestore + RTDB)
==========================================================================
INGRESSI DEL PAPER, TRADE PER TRADE: dove il motore non entra, e perche'
==========================================================================
PAPER: 126 trade chiusi su 62 coppie · rigirate 1 · tolleranza 2 barre · deadline 720s

── VETUSDT|gen_6d06dca0 · 3 trade · 15m · scala 2/4/6 · BE si · keep globale
[backtest] cache ESTESA di 149 candele (invece di riscaricarne 166133) (VETUSDT 15m)
[backtest] dati da cache: 166133 candele (VETUSDT 15m)
  motore: 228 trade sulla storia intera, 1 dal primo trade del paper · cooldown 4 barre
  #1  18 Sep 03:45 UTC  short entry 0.007585  pnl -3.24 USDT (stop_loss)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore bull_trending / paper bull_trending
  #2  19 Sep 04:00 UTC  short entry 0.008292  pnl -5.51 USDT (stop_loss)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore high_uncertainty / paper high_uncertainty
  #3  23 Sep 03:30 UTC  short entry 0.009713  pnl +3.38 USDT (trailing_stop)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore bull_trending / paper bull_trending
  DETTAGLIO VETUSDT|gen_6d06dca0
    spec: rsi_extreme low=20.0 high=75.0 AND session hour_from=8 hour_to=16 · timeframe 15m · solo entrambi · mercato no · 1h no · volume_mult 0 · min_adx 0
    spec nel registro: genitore — · ipotesi — · record coppia: pass 4 · sostituita_da — · genitore —
    #1 18 Sep 03:45 UTC short entry 0.007585 pnl -3.24 · classe REGOLA_NON_SCATTA · IGNOTO
       regola sul trade: — → non registrata
       motore k-2 18 Sep 03:15 close 0.007493: rsi_extreme L=no S=no (low=20 high=75 rsi=69.3) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta: fermano rsi_extreme)
       motore k-1 18 Sep 03:30 close 0.007549: rsi_extreme L=no S=no (low=20 high=75 rsi=74.33) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta: fermano rsi_extreme)
       motore k+0 18 Sep 03:45 close 0.00758: rsi_extreme L=no S=si (low=20 high=75 rsi=76.62) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta)
       motore k+1 18 Sep 04:00 close 0.007529: rsi_extreme L=no S=no (low=20 high=75 rsi=66.18) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta: fermano rsi_extreme)
       paper (prezzo d'ingresso 0.007585): rsi_extreme L=no S=si (low=20 high=75 rsi=76.62) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta)
       paper (chiusura 0.00758): rsi_extreme L=no S=si (low=20 high=75 rsi=76.62) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta)
       indicatori motore/paper: uguali (entro 5%)
       DIAGNOSI: sui valori scritti dal paper la regola NON scatta col prezzo d'ingresso: frenano session — NB: il prezzo su cui il bot ha deciso (vivo) non e' sul trade, `entry_price` porta lo slippage: se la feature che frena guarda il prezzo, vale la riga «prezzo di decisione ≈»; se guarda un indicatore, i valori registrati non sono quelli su cui il bot ha deciso
    #2 19 Sep 04:00 UTC short entry 0.008292 pnl -5.51 · classe REGOLA_NON_SCATTA · IGNOTO
       regola sul trade: — → non registrata
       motore k-2 19 Sep 03:30 close 0.007856: rsi_extreme L=no S=no (low=20 high=75 rsi=49.09) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta: fermano rsi_extreme)
       motore k-1 19 Sep 03:45 close 0.007891: rsi_extreme L=no S=no (low=20 high=75 rsi=52.93) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta: fermano rsi_extreme)
       motore k+0 19 Sep 04:00 close 0.00828: rsi_extreme L=no S=si (low=20 high=75 rsi=75.26) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta)
       motore k+1 19 Sep 04:15 close 0.008245: rsi_extreme L=no S=no (low=20 high=75 rsi=71.95) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta: fermano rsi_extreme)
       paper (prezzo d'ingresso 0.008292): rsi_extreme L=no S=si (low=20 high=75 rsi=75.26) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta)
       paper (chiusura 0.00828): rsi_extreme L=no S=si (low=20 high=75 rsi=75.26) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta)
       indicatori motore/paper: uguali (entro 5%)
       DIAGNOSI: sui valori scritti dal paper la regola NON scatta col prezzo d'ingresso: frenano session — NB: il prezzo su cui il bot ha deciso (vivo) non e' sul trade, `entry_price` porta lo slippage: se la feature che frena guarda il prezzo, vale la riga «prezzo di decisione ≈»; se guarda un indicatore, i valori registrati non sono quelli su cui il bot ha deciso
    #3 23 Sep 03:30 UTC short entry 0.009713 pnl +3.38 · classe REGOLA_NON_SCATTA · IGNOTO
       regola sul trade: — → non registrata
       motore k-2 23 Sep 03:00 close 0.009584: rsi_extreme L=no S=no (low=20 high=75 rsi=70.59) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta: fermano rsi_extreme)
       motore k-1 23 Sep 03:15 close 0.009614: rsi_extreme L=no S=no (low=20 high=75 rsi=72.33) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta: fermano rsi_extreme)
       motore k+0 23 Sep 03:30 close 0.009729: rsi_extreme L=no S=si (low=20 high=75 rsi=77.76) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta)
       motore k+1 23 Sep 03:45 close 0.009636: rsi_extreme L=no S=no (low=20 high=75 rsi=66.41) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta: fermano rsi_extreme)
       paper (prezzo d'ingresso 0.009713): rsi_extreme L=no S=si (low=20 high=75 rsi=77.76) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta)
       paper (chiusura 0.009729): rsi_extreme L=no S=si (low=20 high=75 rsi=77.76) | session L=si S=no (hour_from=8 hour_to=16 ora_utc=13) | => nessun segnale (nessuna direzione netta)
       indicatori motore/paper: uguali (entro 5%)
       DIAGNOSI: sui valori scritti dal paper la regola NON scatta col prezzo d'ingresso: frenano session — NB: il prezzo su cui il bot ha deciso (vivo) non e' sul trade, `entry_price` porta lo slippage: se la feature che frena guarda il prezzo, vale la riga «prezzo di decisione ≈»; se guarda un indicatore, i valori registrati non sono quelli su cui il bot ha deciso
  ABBINATI 0/3 · «come il bot» (da 200 barre prima del paper): 0/3 abbinati, 0 trade del motore
  [119s]

==========================================================================
RIASSUNTO
==========================================================================
  trade classificati: 3 · abbinati 0 (0%) · «come il bot» 0%
  per classe:
    REGOLA_NON_SCATTA        3
  REGOLA_NON_SCATTA per sotto-motivo:
    IGNOTO                   3
  per coppia (abbinati/trade):
    VETUSDT|gen_6d06dca0                0/3   (  0%) · come il bot 0/3
  coppie con piu' non abbinati: VETUSDT|gen_6d06dca0 (3)

LETTURA: 0/3 ingressi abbinati (0%): la regola non scatta e i dati non spiegano perche' (3 su 3 non abbinati) — da guardare a mano.
  NB: i trade del motore sono simulati sulla storia intera, senza holdout; «stop» del
      motore e' dedotto (il SimTrade non porta il motivo). Questo comando misura e basta.
[ingressi] finito in 119s

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
