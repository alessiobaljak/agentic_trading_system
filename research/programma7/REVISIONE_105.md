# Revisione separata della prova 105 (l'effetto Coinbase) — 25 ottobre 2026

Revisore separato (un agente indipendente, senza le conclusioni del coordinamento), dalle 12:50 alle 13:05 UTC. Script e tabelle in
`revisione_105/` (scritti per essere eseguiti da `/tmp/revisore105/`: i percorsi vanno adattati).

* **Nessuno sguardo al futuro**: la prima ora di scambi su Coinbase cade sempre il giorno L (11-22 UTC); l'entrata a L+1 è dopo.
* **Stessa moneta**: chiusura del primo giorno su Coinbase e perpetuo Binance nello stesso giorno, rapporto 0,99-1,07 in 104 casi su 105.
* **Errore di lettura dei dati** (il più grave): `programma6/esecuzione.ore_di` ignorava i file mensili per 14 monete le cui barre
  cominciano a settembre 2023: 14 eventi spariti senza dirlo (91 invece di 105). Corretto nel codice comune il 25 ottobre.
* **Simboli riusati**: PUMP fino al 9 luglio 2025 era un altro token; il perpetuo vero aveva 5 giorni il giorno L (la regola chiede 30).
* **Eventi che non sono quotazioni nuove** (dentro la regola scritta, riportati a parte): BAT, MANA, CVC (già quotate in USDC dal
  2018-2019), NOM (nuovo nome di OMNI), MON, MEGA, SENT (giorno di nascita del token, perpetuo di pre-mercato), SOL (data dubbia).
* **Robustezza**: senza il 2025 p 0,12; senza i 10 migliori +1,36% (p 0,23); dall'ottobre 2025 +0,41% su 21 eventi.
* **Il controllo è giusto**; contro le altre monete dello stesso giorno, quelle di età simile o con la salita più simile, l'eccesso è
  +5,4-6,0 punti con p < 0,001: nel passato l'effetto c'era.
* **Giudizio: non regge** come strategia validata (corretti i dati: p 0,010 con tutti gli eventi, 0,016 togliendo PUMP); da tenere in coda.

## Misura in avanti a tavolino (idea 75): le quotazioni nuove su Coinbase dopo il 25 ottobre 2026

La stessa regola della prova 105, senza cambiarla, sui soli eventi nuovi (monete con il perpetuo di Binance da almeno 30 giorni che
cominciano a scambiare contro il dollaro su Coinbase). Si rifà il conto quando gli eventi nuovi sono almeno 30.

| Controllo (UTC) | Monete nuove su Coinbase con il perpetuo di Binance |
|---|---|
| 2026-10-26 16:23 | nessuna (rispetto all'elenco del 25 ottobre) |
| 2026-10-26 20:20 | nessuna |
| 2026-10-27 00:21 | nessuna |
| 2026-10-27 04:20 | nessuna |
| 2026-10-27 08:26 | nessuna |
| 2026-10-27 12:36 | nessuna |
