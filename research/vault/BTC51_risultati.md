# Vault del protocollo 3: risultati della campagna BTC51 (Passo 5)

Scritto dal coordinamento il 17 ottobre 2026, sul branch principale, dopo l'unica esecuzione.

- **Apertura:** `APERTURA_3.md` (commit f4835d8a, 16:23 UTC), dopo la frase del proprietario «APRI IL VAULT 3».
- **Esecuzione:** una sola, `python3 research/vault/passo5_btc51.py esegui`, iniziata alle 16:24:53 UTC
  (`BTC51_giro_iniziato.json`, scritto prima di caricare i dati). Programma committato prima di scaricare i dati del
  vault. Dati: BTCUSDT perpetuo di Binance, candele last e mark a 1h e funding, dal 2024-01 al 2026-09, 33 mesi su 33
  per ogni serie, tutti con il CHECKSUM di Binance verificato. 24.096 candele orarie nel vault, nessuna mancante. Un
  giorno senza mark (2026-06-29), sostituito dal last come nel resto della serie (sezione 9.6).
- **Controlli prima dell'esecuzione:** impronte dei file del candidato uguali al Passo 3 (4 su 4), strumenti uguali al
  quarto giro del collaudo (9 su 9, sul branch principale e su quello della ricerca), specifica di V-020 nel log
  uguale a quella della validazione. Lo stesso programma ha rifatto costruzione e validazione con i numeri della
  sessione di ricerca (180 trade, +0,2227 R, p 0,01698; 80 trade, +0,1666 R).
- **Esiti completi e trade uno per uno:** `BTC51_vault.json`.

## Esito: V-020 NON supera il vault

| Condizione (sezioni 10.3 e 10.4) | Soglia | Vault | Esito |
|---|---|---|---|
| Trade | almeno 100 | 180 | sì |
| R medio dopo i costi | sopra 0 | **−0,007** | **no** |
| R medio a costi doppi | sopra 0 | −0,104 | **no** |
| Profit factor | almeno 1,10 | 0,99 | **no** |
| Asticella di Benjamini-Hochberg al 10% (un solo candidato: p ≤ 0,10) | p ≤ 0,10 | p = 0,337 | **no** |

Un candidato che fallisce resta fallito (Passo 5, punto 5). Nessuna strategia del protocollo 3 su BTC arriva al paper.

## Metriche affiancate

| Metrica | Costruzione (2020-01 → 2022-09) | Validazione (2022-10 → 2023-12) | Vault (2024-01 → 2026-09) |
|---|---|---|---|
| Trade | 180 | 80 | 180 |
| Trade al mese | 5,46 | 5,33 | 5,46 |
| R medio dopo i costi | +0,223 | +0,167 | **−0,007** |
| Profit factor | 1,46 | 1,29 | 0,99 |
| Vincenti | 48,3% | 40,0% | 36,7% |
| R medio dei vincenti / dei perdenti | — | +1,852 / −0,957 | +1,589 / −0,931 |
| Drawdown massimo | −9,0 R | −14,7 R | −21,8 R |
| R medio a costi doppi | +0,147 | +0,064 | −0,104 |
| p-value contro le entrate casuali | 0,017 | — | 0,337 |
| R medio delle entrate casuali | −0,004 | — | −0,047 (95° percentile +0,109) |
| Senza il 5% dei trade migliori (9) | +0,012 | — | −0,220 |
| Uscite per stop / per tempo | — | — | 93 (−1,081 R) / 86 (+1,147 R); 1 a fine dati |
| Trade ridotti per la leva / violazioni di liquidazione | 0 violazioni | 3 / 0 | 0 / 0 |

Fonti: costruzione e validazione da `consegna.md` e `validazione.md` della campagna (commit 1b222fb5), riprodotte
da `passo5_btc51.py riproduci`; vault da `BTC51_vault.json`.

## Cosa è cambiato rispetto a costruzione e validazione

Per semestre (R medio a trade, somma degli R, variazione del prezzo di BTC nel semestre, quota dei regolamenti del
funding sotto zero). Il semestre 2022H2 unisce l'ultimo trimestre della costruzione e il primo della validazione; il
2026H2 è solo luglio-settembre.

| Semestre | Trade | R medio | Somma R | BTC | Funding sotto zero |
|---|---|---|---|---|---|
| 2020H1 | 42 | +0,402 | +16,9 | +27% | 20% |
| 2020H2 | 17 | −0,022 | −0,4 | +217% | 9% |
| 2021H1 | 10 | +0,211 | +2,1 | +21% | 6% |
| 2021H2 | 20 | +0,544 | +10,9 | +32% | 9% |
| 2022H1 | 65 | +0,040 | +2,6 | −57% | 26% |
| 2022H2 | 54 | +0,288 | +15,5 | −17% | 18% |
| 2023H1 | 20 | +0,517 | +10,3 | +84% | 7% |
| 2023H2 | 32 | −0,141 | −4,5 | +39% | 13% |
| **2024H1** | 7 | +0,527 | +3,7 | +48% | 3% |
| **2024H2** | 26 | +0,279 | +7,3 | +49% | 14% |
| **2025H1** | 39 | +0,087 | +3,4 | +15% | 16% |
| **2025H2** | 24 | −0,129 | −3,1 | −18% | 10% |
| **2026H1** | 80 | −0,166 | −13,3 | −33% | 38% |
| **2026H2** | 4 | +0,172 | +0,7 | +43% | 2% |

Fonti: trade dall'esecuzione unica del vault e da `riproduci` (costruzione e validazione); prezzo di BTC dalle
candele last a 1h (apertura della prima candela, chiusura dell'ultima); funding dai file `fundingRate` di Binance
(regolamenti sotto zero sul totale del semestre).

Quello che si vede (osservato):

1. **Il 2024 somiglia alla costruzione** (33 trade, +10,9 R). Il vantaggio sparisce dal 2025 e nel primo semestre del
   2026 si rovescia: 80 trade in sei mesi, il 44% di tutti quelli del vault, a −0,166 R.
2. **Il primo semestre del 2026 è il semestre con il funding più spesso sotto zero di tutto il periodo 2020-2026**
   (38% dei regolamenti, contro un massimo del 26% nella costruzione), con BTC a −33%.
3. **Già nella costruzione il semestre peggiore per la logica era un mercato in forte discesa** con molto funding
   negativo: 2022H1, 65 trade a +0,040 con BTC a −57%. La validazione finiva con un semestre negativo (2023H2,
   −0,141), che nella consegna compariva solo dentro la media del 2023 (+0,112).
4. **I guadagni dipendevano da pochi trade grandi** (limite 1 della consegna): senza i 9 migliori il vault scende a
   −0,220 R a trade. Le uscite a tempo guadagnano in media più di quanto perdono gli stop (+1,147 contro −1,081), ma
   gli stop sono di più (93 contro 86) e i vincenti scendono al 36,7%.

Lettura (inferita, non dimostrata): il meccanismo ipotizzato era «funding negativo = folla di short che deve
ricoprirsi». Nei mercati in discesa lunga il funding resta negativo a lungo e il segnale scatta molto più spesso, ma
lì sembra misurare la tendenza al ribasso, non una folla da spremere: il long a 24 ore perde. Con un solo vault non si
può dire di più; un'idea nuova su questo (per esempio escludere i mercati in discesa) sarebbe una variante nuova, senza
vault, giudicabile solo da un paper nuovo (Passo 8, punto 7).

## La previsione scritta prima dell'apertura (consegna, sezione 6)

| Previsione | Detto prima | Osservato |
|---|---|---|
| Trade nei 33 mesi | circa 175 (da 110 a 230) | 180: dentro |
| R medio a trade | +0,08 (da −0,10 a +0,20) | −0,007: dentro l'intervallo, sotto il centro |
| Probabilità di superare il vault | circa 1 su 4 | non superato |

## Prossimo passo (STOP)

Il Passo 5 finisce con lo STOP: decide il proprietario. Il protocollo prevede ancora:

- **Passo 6** (prova su altre monete): «ogni candidato entrato nel vault» gira senza modifiche sul vault di 9 altre
  monete. Serve solo a capire se l'idea vale altrove; non cambia l'esito del vault.
- **Passo 9** (chiusura): `lezioni.md` della campagna e aggiornamento di `STATO.md`.

Il Passo 8 (paper) non si fa: nessun candidato ha superato il vault.
