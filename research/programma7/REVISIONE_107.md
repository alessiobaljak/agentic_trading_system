# Revisione separata della prova 107 (i perpetui annunciati in chiusura) — 25 ottobre 2026

Revisore separato (un agente indipendente), dalle 20:25 alle 20:42 UTC. Script e tabelle in `revisione_107/` (scritti per essere eseguiti
da `/tmp/revisore107/`: i percorsi vanno adattati). Rifatta la prova: stessi 77 eventi, stesso risultato (+7,89%, p 0,028).

* **Ora dell'annuncio vera**: nell'ora dell'annuncio il volume sale di 33 volte (mediana) e la moneta perde il 2,3% sul Bitcoin.
* **Ora di chiusura sbagliata in 18 eventi su 77**: sei annunci hanno due date per contratti diversi e il codice usava la più tarda
  (`quarantacinquesima.py`, `chiusura = max(dopo)`); per quei 18 l'uscita cadeva 23 ore dopo la chiusura vera, su candele senza scambi.
* **OMG**: la chiusura è stata rinviata (dicembre 2024, poi di nuovo): contato come chiusura, +31,9%. Rinviate anche AKRO e BLZ (2022).
* **Dieci contratti mancanti** (sigla scritta in altro modo negli annunci del 2022, più MEMEFI): con loro 87 eventi, **+4,85% a evento,
  p 0,116**, senza i 5 migliori +0,86%; il 2022 vale −14,7% su 12 eventi. AERGO manca perché l'archivio non ha il file mensile.
* **Con le chiusure giuste** (OMG tenuto): +7,40%, p 0,036; senza l'uscita a +30% +11,80% (p 0,0036, ma con perdite da −62%, −73%, −79%).
* **Contro le altre monete negli stessi giorni** (220-540 monete, volume o andamento simile): +6-7 punti, p 0,003-0,007: l'effetto della
  chiusura è vero, non è il calo generale delle monete piccole.
* **Robustezza**: 77 eventi in 26 settimane; contando una volta ogni settimana +4,1%, t 0,81; senza i 10 migliori −0,05%; ottobre 2026
  tre eventi su tre perdenti (−29,5%).
* **Funding**: lo short in media incassa (+0,95% a evento); il conto a giorni interi è prudente in media ma rumoroso sul singolo evento.
* **Si può fare dal vivo?** Fino al settembre 2026 sì (nuove posizioni vietate solo da 30 minuti prima della chiusura). Ma **l'annuncio
  del 21 ottobre 2026 (PTB, MITO) vieta i nuovi ordini agli utenti normali dal minuto della pubblicazione**: se diventa la regola, su
  Binance la strategia non si può più fare. Il costo d'entrata vero è circa 0,5-1% (nei primi minuti), non 0,1%.
* **Giudizio: misurare in avanti con riserve** (chiusura per contratto, rinvii, controllo che all'uscita ci siano scambi, costi d'entrata
  più alti, e a ogni annuncio verificare se Binance lascia aprire posizioni).

**Decisione del coordinamento**: non va nel paper. La regola scritta non passa e con i dati completi passa ancora meno (p 0,116); e dal
21 ottobre Binance blocca i nuovi ordini dal momento dell'annuncio. Resta una **osservazione da seguire**: a ogni nuovo annuncio di
chiusura si guarda se gli utenti possono ancora aprire posizioni; se per tre annunci di fila sì, si scrive una prova nuova con i dati
corretti e i costi veri, da misurare in avanti.

## Osservazione in avanti: Binance lascia ancora aprire posizioni dopo l'annuncio?

| Controllo (UTC) | Annunci di chiusura nuovi | Nuove posizioni vietate da | Conta per «tre di fila» |
|---|---|---|---|
| 2026-10-21 09:30 (PTB, MITO) | 1 | dal minuto della pubblicazione (gli utenti normali); i market maker da 30 minuti prima | no |
| 2026-10-26 04:20 | nessuno dopo il 21 ottobre | — | — |
| 2026-10-26 12:43 | nessuno dopo il 21 ottobre | — | — |
| 2026-10-26 16:23 | nessuno dopo il 21 ottobre | — | — |
| 2026-10-26 20:20 | nessuno dopo il 21 ottobre | — | — |
| 2026-10-27 00:21 | nessuno dopo il 21 ottobre | — | — |
| 2026-10-27 04:20 | nessuno dopo il 21 ottobre | — | — |
| 2026-10-27 08:26 | nessuno dopo il 21 ottobre | — | — |
| 2026-10-27 12:36 | nessuno dopo il 21 ottobre | — | — |
| 2026-10-27 16:21 | nessuno dopo il 21 ottobre | — | — |
| 2026-10-27 20:21 | nessuno dopo il 21 ottobre | — | — |
| 2026-10-28 00:21 | nessuno dopo il 21 ottobre | — | — |
| 2026-10-28 04:20 | nessuno dopo il 21 ottobre | — | — |
| 2026-10-28 08:19 | nessuno dopo il 21 ottobre | — | — |
