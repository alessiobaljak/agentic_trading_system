# Collaudo del metodo, protocollo 4: esiti

## Esito: il metodo passa il collaudo (primo giro, 17 ottobre 2026)

| Prova | Soglia | Esito |
|---|---|---|
| A — varianti finte su LINKUSDT senza vantaggio: oltre la Fase 2 | al massimo 5 su 100 | **0 su 100** |
| A — p-value sotto 0,10 | al massimo 15 su 100 | **14 su 100** |
| A, punto 6 — battono il caso su almeno 7 monete di controllo su 9 | STOP oltre 17 su 100 | **12 su 100** (attese circa 9 con monete indipendenti); 1 supera la verifica 12 intera |
| B — vantaggio inserito, B1 (long, a mercato) | con P = 0 al massimo 3 su 30 oltre la Fase 2; con almeno 0,35 R almeno l'80% | **0 su 30**; **29 su 29** (100%) |
| B — B2 (short) | come sopra | **0 su 30**; **29 su 29** (100%) |
| B — B3 (limit) | come sopra | **0 su 30**; **30 su 30** (100%) |
| B, punto 6 — verifica 12 con il vantaggio inserito sulle 9 monete di controllo, P = 1,2 | almeno 8 prove su 10 per regola | **B1 10 su 10, B2 10 su 10** (anche con P = 0,6: 10 su 10 e 10 su 10) |
| C — parita' con il bot | dopo il vault, prima del paper (D5) | non eseguita (il bot non sa eseguire il catalogo) |

Dal 20:49:34 al 21:54:38 UTC, con **Python 3.13.16, numpy 2.5.3 e scipy 1.18.1**: le versioni della macchina delle
sessioni di ricerca, lette dalla sessione di prova `session_01WAjzJ2qP6vT3KsYghVfYbf` alle 20:51 UTC. Esiti grezzi in
`esiti/giro1/` (`prova_a.jsonl`, `prova_a_estrazioni.jsonl`, `prova_b.jsonl`, `prova_b12.jsonl`), riepilogo calcolato in
`esiti/giro1/riepilogo.json` (`riepilogo.py 1`). Regole di dettaglio: `regole.md`, committato prima del calcolo
(commit 1a0dfd64, 20:47:55 UTC).

## Prova A (13bis.2), i numeri

- 501 varianti finte estratte (seme 2026), 400 scartate perche' sotto 150 trade stimati, 1 senza entrate casuali
  possibili (la numero 309, a 15 minuti: 565 trade, mentre una strategia che entra appena e' libera ne fa 311), sostituita
  con l'estrazione successiva: 100 con la Fase 2 completa.
- Timeframe delle 100: 15m 42, 30m 23, 1h 22, 2h 10, 8h 2, 4h 1. Su LINKUSDT, con 32,5 mesi di costruzione, quasi
  nessuna variante su candele lunghe arriva a 150 trade.
- p-value per decimi (da 0-0,1 a 0,9-1): 14, 9, 8, 10, 17, 8, 7, 7, 8, 12; il piu' piccolo 0,002. R medio delle 100
  varianti −0,067, delle loro entrate casuali −0,074 (i costi).
- Verifica 12 (punto 6), quante monete su 9 battono il caso: 1 → 2 varianti, 2 → 7, 3 → 15, 4 → 24, 5 → 24, 6 → 16,
  7 → 9, 8 → 3, 9 → 0. Supera la verifica 12 intera una sola variante (la numero 330, 30 minuti, long: 8 monete su 9,
  media +0,105 R), che non supera la Fase 2 (su LINKUSDT R medio +0,125, sotto 0,2, e p 0,20): la verifica 12 da sola non
  basta, e nel protocollo viene dopo la Fase 2 e le altre verifiche.

## Prova B (13bis.3), i numeri

| Regola | R medio netto con P = 0 / 0,6 / 1,2 | Senza vantaggio oltre la Fase 2 | Con almeno 0,35 R oltre la Fase 2 | Zona 0,2-0,35 R: superano / attese | Entrate casuali: salita media |
|---|---|---|---|---|---|
| B1 | −0,035 / +0,179 / +0,430 | 0 su 30 | 29 su 29 | 10 / 10 | −0,005 R |
| B2 | −0,065 / +0,167 / +0,429 | 0 su 30 | 29 su 29 | 10 / 10 | +0,006 R |
| B3 | −0,008 / +0,231 / +0,477 | 0 su 30 | 30 su 30 | 22 / 22 | −0,030 R |

Segnali inseriti uguali a quelli trovati in tutte le prove; la riserva con P = 1,8 non e' servita (con P = 1,2 almeno 29
serie su 30 arrivano a 0,35 R per ogni regola); le entrate casuali non guadagnano dal vantaggio inserito (salita sotto
0,05 R per tutte e tre).

## Prova B, punto 6

| Regola | P = 0,6: superano la verifica 12 | P = 1,2: superano | Monete che battono il caso, in media |
|---|---|---|---|
| B1 | 10 su 10 | 10 su 10 | 9 su 9 |
| B2 | 10 su 10 | 10 su 10 | 9 su 9 |

## Cose da sapere

1. **Prima del commit delle regole** il coordinamento ha fatto due calcoli di prova sul codice, per i tempi e per
   controllare i lanci (`regole.md`, ultima sezione): la regola B1 sulla serie 1 senza vantaggio e la prova B.6 di B1 con
   seme 1 e P = 1,2. La prova B.6 di B1, seme 1, P = 1,2 rifatta nel giro: 9 su 9, supera (come nella prova).
2. **`parametri_4.yaml`** e' cambiato durante il calcolo (le versioni, alle 21:11 UTC) e dopo (la riga dello stato,
   congelato): nessun programma del collaudo e degli strumenti lo legge (lo elenca solo `collaudo.py impronte`), quindi
   le prove non dipendono da quei cambiamenti. L'impronta qui sotto e' quella del file congelato.
3. Il generatore dei lanci (`collaudo.py`, `_lanci`) moltiplica interi a 64 bit: numpy avvisa del superamento della
   capacita' una volta per processo; il risultato e' quello voluto (aritmetica modulo 2^64 di SplitMix64).
4. Le serie senza direzione di monete diverse sono indipendenti, mentre le monete vere si muovono insieme: con monete
   vere la verifica 12 filtra un po' meno di quanto misurato qui (`PROTOCOLLO_4.md`, sezione 15).

## Impronte (valgono per tutta la ricerca, 13bis.5)

`esiti/giro1/impronte.json`:

| Strumento | SHA-256 |
|---|---|
| `research/src/catalogo3.py` | `5c72340ffb6ccdda66eac27b184250311b3e822ce18b8003126cd4b1f9640442` |
| `research/src/motore3.py` | `84d3700cb1633711bb11db31ae9555f938897a4fd3fce1a3a56452281d9cf6c3` |
| `research/src/statistica3.py` | `1e5bbd750df11ca0c1f790edcc607fc9eea492e5a5ee34746190571fc391811a` |
| `research/src/statistica4.py` | `bb29a81438e48d393d37a40ea98930ab2895fde05d4b490d633219164cd29cb9` |
| `research/src/controllo4.py` | `0e47e91e12d52a07f6c01970c8bd5db1294dcd37ecd9557daed9f5149a88bfa4` |
| `research/src/statistica.py` | `e42edc0082ff0e52b8d1e1a65493f912c98fd7fbf083bf53dbe0d742ef95b7a1` |
| `research/src/dati.py` | `4a6d0dede79c359633ef672d1d4551f50f7a94993a366262c3039a8357054502` |
| `research/src/guardiano.py` | `fa7d4a34b2cec886d69731810c713358d46dd44a65a545446a3bc62068903067` |
| `research/config/parametri_4.yaml` | `8f46a666fe8d83c8ca70294e0a0658e532bda6781428154da7fd95a4e15ff92c` |
| `research/config/bot_4.md` | `88dc419c5b223857e18bce9f214ef0f50d89b20100d6ff1ee715e763f324e1b1` |
| `research/collaudo_4/collaudo.py` | `701edfe4c04c195f385ac1a6ddbea9adf1b0880a83ed34dce56776c6423ef106` |
| `research/collaudo_4/regole.md` | `4d9dcc6d101665642f94abedf2497666716beee01455fb2314965afc8e2eaafb` |

## Approvazione

Il proprietario ha delegato l'approvazione degli esiti al coordinamento il 17 ottobre 2026 verso le 21:10 UTC
(`research/protocollo_4_note.md`, sezione 0): il collaudo e' superato senza correzioni, gli strumenti sono congelati e
il coordinamento apre la sessione di ricerca.
