# Candidato MASKUSDT-029 — short dopo un'impennata oraria, senza funding negativo

Famiglia MASKUSDT-006 (idea I-03, ritorno dopo una barra estrema; fonti: Jegadeesh 1990,
Lehmann 1990). Secondo ritocco della famiglia (028 → 029). Codice: `codice/registro_ritocchi.py`
(classe `R2`), con `codice/varianti_idee.py` (`I03S`), `codice/varianti_base.py`
(`VarianteATR`) e `codice/quadro.py` (caricamento, filtro di liquidità, strategia).

## Regole

* **Moneta e timeframe:** MASKUSDT, candele da 1 ora (last price), segnali alla chiusura.
* **Direzione:** solo short.
* **Ingresso:** alla chiusura della barra i, se
  1. il rendimento logaritmico della barra, ln(close_i / close_{i-1}), è maggiore di 3 volte la
     deviazione standard (ddof 1) dei rendimenti logaritmici orari delle 168 barre precedenti
     (esclusa la barra i);
  2. l'ultimo tasso di funding regolato con istante entro la chiusura della barra i è ≥ 0;
  3. la barra non è in un mese sotto 20 milioni di USDT di volume medio giornaliero (in
     costruzione: settembre 2022);
  4. non c'è una posizione aperta.
  Entrata short all'apertura della barra i+1.
* **Stop:** close_i + 2 × ATR di Wilder a 14 barre (1 ora), misurato alla barra i; scatta sul last.
* **Target:** close_i − 4 × ATR (2 volte la distanza dello stop).
* **Uscita a tempo:** alla chiusura della 12ª barra dall'ingresso (barra d'ingresso contata come
  1) si chiude all'apertura della barra dopo. Stop prima del target nella stessa barra.
* **Dimensione e leva (regole del bot, `config/regole_dimensione.md`):** rischio 1% del capitale
  sulla distanza dello stop; leva massima 2; margine isolato; nessun trade ridotto in costruzione;
  nessuna violazione della distanza dalla liquidazione.
* **Costi:** commissione 0,05% e slippage 0,05% per lato; funding vero ai settlement.

## Motivo economico

Un'impennata di un'ora oltre 3 deviazioni su una moneta di media capitalizzazione è spesso
liquidità che si esaurisce (acquisti a mercato concentrati, pump, chiusure forzate): il prezzo
rientra nelle ore seguenti. Quando il funding è negativo, gli short erano affollati prima
dell'impennata e la loro chiusura forzata può continuare: è il caso escluso dal filtro (nato
dallo studio dei fallimenti, nota MASKUSDT-N007, ai limiti del rumore).

## Limiti noti

* Lo stop di 2 ATR a 1 ora supera il 6% del bot in 32 trade su 86: il bot non lo esegue così
  com'è. La versione con stop 1,5 ATR (MASKUSDT-032) non batte nettamente la (b) in costruzione.
* Il filtro del funding e l'uscita a 12 barre vengono da ritocchi guardando la costruzione.
* A 30 minuti l'effetto quasi sparisce (R medio −0,03); a 2 ore i trade sono troppo pochi.
