# Campagna di gruppo — consegna

**Esito: nessuna strategia valida trovata per il gruppo.**

Il budget di 30 varianti è stato usato per intero (20 da idee nuove con fonte, 10 ritocchi), più 6 scarti per la
stima dei trade che non consumano budget. Nessuna variante è diventata candidato in costruzione: nessuna ha battuto
nettamente sia la (a) sia la (b) di gruppo. Non c'è quindi nessun candidato da congelare né da validare, e il
periodo di validazione (dal 2023-01-17 al 2023-12-31) non è stato usato. Il log completo è `log.jsonl` (voci da
GRUPPO-001 a GRUPPO-055); le ipotesi con la Fase 1 sono in `ipotesi.md`; la Fase 0 in `fase0_dati.md`.

Stile: «osservato» = numero dell'esame (`gruppo.py`) o di uno script di lavoro, con il file; «inferito» =
conclusione dai numeri; «ipotizzato» = spiegazione non verificata.

## Come si è lavorato

* **Monete e periodi.** Le 80 monete di `monete.csv`; costruzione fino al 2023-01-16 per tutte (nota GRUPPO-006);
  storia sufficiente per 80 su 80; dati senza errori di scarico, con le impronte in `impronte/` (Fase 0: GRUPPO-007,
  GRUPPO-036, GRUPPO-039).
* **Controllo positivo degli strumenti.** Il primo (uscita a 7 giorni) non è passato (GRUPPO-009): contro la (a)
  di gruppo t 1,96 con soglia 2,07, perché l'errore della (a) di gruppo con tenute lunghe è grande (0,070 R). Su
  decisione del proprietario si è rifatto con l'uscita a 1 giorno (GRUPPO-010): passa (t contro la (b) 24,45 e
  contro la (a) 9,85 senza ritardo, -1,28 con il ritardo di una barra; GRUPPO-011).
* **Esame.** Ogni numero è di `research/src/gruppo.py` (`conta_trade_di_gruppo`, `esame_di_gruppo`); il codice
  della sessione scrive solo le strategie (`codice/i*.py`) e gli script di lavoro.

## Tutte le varianti (costruzione)

Numeri dal campo `risultato` del log (tabella prodotta da `codice/tabella_varianti.py`). Il t è quello di
`contro_baseline` con il pavimento delle sfasate; «soglia» è quella della (b).

| n. | id | variante | tf | dir. | ritocco di | trade | R medio dopo i costi | t contro (b) | t contro (a) | soglia | blocchi | R senza i 30 migliori | R per anno (2020/21/22/23) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | GRUPPO-012 | I-03-L | 1d | long | — | 1738 | -0,012 | -0,38 | -0,36 | 2,10 | 28 | -0,044 | -0,02 / -0,02 / -0,01 / 0,12 |
| 2 | GRUPPO-014 | I-03-S | 1d | short | — | 1405 | -0,024 | -0,37 | -0,41 | 2,14 | 20 | -0,041 | -0,13 / -0,06 / 0,02 / — |
| 3 | GRUPPO-015 | I-01-L | 1d | long | — | 3756 | 0,036 | 0,39 | 0,20 | 2,11 | 26 | -0,001 | 0,15 / 0,10 / -0,12 / 0,88 |
| 4 | GRUPPO-016 | I-01-S | 1d | short | — | 4320 | -0,022 | 0,20 | 0,19 | 2,08 | 35 | -0,034 | -0,10 / -0,07 / 0,04 / -0,49 |
| 5 | GRUPPO-017 | I-02-L | 1d | long | — | 871 | 0,110 | 0,71 | 0,55 | 2,32 | 10 | -0,033 | 0,30 / 0,21 / -0,30 / 0,48 |
| 6 | GRUPPO-018 | I-02-S | 1d | short | — | 1115 | -0,008 | 0,28 | 0,29 | 2,28 | 11 | -0,043 | -0,27 / -0,11 / 0,07 / -0,68 |
| 7 | GRUPPO-020 | I-04-S | 1d | short | — | 877 | -0,055 | -0,96 | -0,67 | 2,09 | 31 | -0,094 | -0,30 / -0,04 / 0,01 / -0,37 |
| 8 | GRUPPO-021 | I-05-S | 1d | short | — | 2096 | -0,034 | -0,27 | -0,18 | 2,09 | 31 | -0,050 | -0,02 / -0,04 / 0,17 / -0,03 |
| 9 | GRUPPO-025 | I-08-L | 1d | long | — | 7116 | -0,024 | -1,37 | -1,02 | 2,03 | 91 | -0,029 | 0,02 / -0,03 / -0,03 / 0,07 |
| 10 | GRUPPO-027 | I-11-S | 1d | short | — | 798 | -0,038 | -0,02 | 0,22 | 2,28 | 11 | -0,122 | -0,19 / -0,23 / 0,31 / -0,29 |
| 11 | GRUPPO-029 | I-12-S | 1d | short | — | 1437 | -0,072 | -0,82 | -0,85 | 2,32 | 10 | -0,089 | -0,12 / -0,06 / 0,01 / -0,67 |
| 12 | GRUPPO-030 | I-17-L | 1d | long | — | 1630 | 0,081 | 1,23 | 0,98 | 2,14 | 20 | 0,051 | -0,18 / 0,20 / -0,00 / 0,16 |
| 13 | GRUPPO-032 | I-24-L | 1d | long | — | 1760 | 0,005 | 0,37 | 0,17 | 2,11 | 25 | -0,016 | -0,01 / -0,03 / 0,03 / 0,07 |
| 14 | GRUPPO-033 | I-24-S | 1d | short | — | 1652 | -0,002 | 0,80 | 0,46 | 2,08 | 33 | -0,017 | -0,03 / 0,02 / -0,01 / -0,23 |
| 15 | GRUPPO-034 | I-26-L | 1d | long | — | 954 | 0,002 | -0,07 | -0,10 | 2,17 | 17 | -0,079 | 0,18 / 0,05 / -0,08 / — |
| 16 | GRUPPO-035 | I-26-S | 1d | short | — | 1046 | -0,093 | -1,33 | -0,69 | 2,20 | 15 | -0,122 | -0,18 / -0,13 / -0,02 / — |
| 17 | GRUPPO-037 | I-19-L | 4h | long | — | 2545 | 0,085 | 1,44 | 1,33 | 2,28 | 11 | 0,044 | 0,27 / 0,13 / -0,05 / 0,54 |
| 18 | GRUPPO-038 | I-19-S | 4h | short | — | 4328 | -0,019 | 0,70 | 0,58 | 2,06 | 43 | -0,039 | -0,11 / -0,04 / 0,06 / -0,31 |
| 19 | GRUPPO-040 | I-07-L | 1h | long | — | 8025 | -0,031 | 1,55 | 1,35 | 2,14 | 20 | -0,047 | -0,04 / -0,01 / -0,09 / 0,25 |
| 20 | GRUPPO-041 | I-07-S | 1h | short | — | 3175 | -0,056 | 0,40 | 0,36 | 2,08 | 32 | -0,081 | -0,21 / -0,08 / -0,01 / -0,12 |
| 21 | GRUPPO-044 | I-07-L-r1 | 1h | long | GRUPPO-040 | 841 | 0,024 | 1,49 | 1,45 | 2,25 | 12 | -0,043 | 0,02 / -0,01 / 0,02 / 0,60 |
| 22 | GRUPPO-045 | I-07-L-r2 | 1h | long | GRUPPO-040 | 829 | 0,029 | 1,13 | 1,19 | 2,25 | 12 | -0,062 | -0,05 / 0,02 / 0,02 / 0,85 |
| 23 | GRUPPO-046 | I-07-L-r3 | 1h | long | GRUPPO-040 | 2820 | 0,005 | 2,01 | 1,89 | 2,16 | 18 | -0,026 | -0,03 / 0,01 / -0,02 / 0,50 |
| 24 | GRUPPO-047 | I-07-L-r4 | 1h | long | GRUPPO-046 | 1558 | 0,000 | 1,61 | 1,52 | 2,14 | 20 | -0,043 | 0,00 / -0,04 / 0,04 / 0,58 |
| 25 | GRUPPO-048 | I-07-L-r5 | 1h | long | GRUPPO-046 | 2806 | 0,008 | 2,06 | 1,99 | 2,16 | 18 | -0,013 | -0,01 / 0,01 / -0,01 / 0,34 |
| 26 | GRUPPO-049 | I-19-L-r1 | 4h | long | GRUPPO-037 | 1230 | 0,089 | 0,91 | 0,88 | 2,87 | 5 | 0,032 | 0,35 / 0,20 / -0,11 / 0,52 |
| 27 | GRUPPO-050 | I-19-L-r2 | 4h | long | GRUPPO-037 | 5346 | 0,049 | 1,80 | 1,42 | 2,13 | 21 | 0,027 | 0,09 / 0,09 / -0,04 / 0,54 |
| 28 | GRUPPO-051 | I-19-L-r3 | 4h | long | GRUPPO-050 | 11062 | 0,028 | 1,89 | 1,26 | 2,07 | 38 | 0,016 | 0,01 / 0,06 / -0,04 / 0,55 |
| 29 | GRUPPO-052 | I-19-L-r4 | 4h | long | GRUPPO-051 | 10463 | 0,017 | 1,71 | 1,16 | 2,05 | 49 | 0,009 | 0,02 / 0,04 / -0,03 / 0,41 |
| 30 | GRUPPO-053 | I-19-L-r5 | 4h | long | GRUPPO-051 | 9710 | 0,029 | 1,26 | 0,89 | 2,08 | 35 | 0,002 | 0,07 / 0,09 / -0,09 / 0,93 |

Il 2023 in costruzione sono solo i 16 giorni dal 1° al 16 gennaio: i suoi R medi sono su pochi trade.

| scarto | variante | trade stimati | motivo |
|---|---|---|---|
| GRUPPO-019 | I-04-L | 370 | trade stimati 370 sotto 700 |
| GRUPPO-022 | I-05-L | 882 | AXSUSDT ha il 10,1% dei trade stimati, oltre il 10% |
| GRUPPO-023 | I-06-L | 126 | trade stimati 126 sotto 700 |
| GRUPPO-024 | I-06-S | 143 | trade stimati 143 sotto 700 |
| GRUPPO-026 | I-10-L | 46 | trade stimati 46 sotto 700; ATOMUSDT ha il 10,9% dei trade stimati, oltre il 10% |
| GRUPPO-028 | I-12-L | 453 | trade stimati 453 sotto 700 |

## Cosa dicono i numeri

* **Osservato.** Nessuna variante batte nettamente la (b): il t più alto è 2,06 (GRUPPO-048, soglia 2,16), il
  secondo 2,01 (GRUPPO-046). Entrambi sono il terzo e il quinto ritocco della stessa famiglia, con R medio dopo i
  costi di 0,008 e 0,005 per trade.
* **Osservato.** Le due famiglie più vicine (il ritardo delle monete dopo un'ora forte di BTC, a 1 ora; il rientro
  del rendimento proprio della moneta al netto di BTC, a 4 ore) mostrano un effetto lordo positivo e stabile fra le
  varianti, ma piccolo: a 1 ora il recupero prima dei costi è circa +0,04-0,09 R per trade contro un costo di un
  giro di 0,05-0,07 R (`lavoro/fase3_*.out`); a 4 ore il rientro vale fino a +0,11 R prima dei costi ma vive
  soprattutto nei giorni di vendite generali (`lavoro/fase3_040_037.out`), dove l'esame conta molti trade come
  poche scommesse (fino a 112 uscite in un giorno, blocchi di 200-290 trade).
* **Osservato.** Il 2022 (anno di ribasso) è negativo in quasi tutte le varianti long con R medio positivo.
* **Osservato.** Molte varianti stanno al 99,5-100° percentile fra le simulazioni casuali (che entrano in modo
  indipendente su ogni moneta), ma non battono il pavimento delle sfasate, che conserva i grappoli fra monete.
* **Inferito.** Con 80 monete che si muovono insieme, i trade sommati valgono molti meno trade indipendenti
  (effetto grappolo fino a 33): la potenza dell'esame di gruppo per vantaggi di pochi centesimi di R è bassa, come
  dice regole.md, sezione 15. Un vantaggio di questa taglia, se c'è, non si distingue dal caso con questi dati.
* **Inferito.** Il confronto con la (a) di gruppo ha poca potenza con tenute di più giorni (errore della (a) 0,07 R
  con tenuta 7 nel primo controllo positivo): le idee su 1d a più giorni partivano svantaggiate (GRUPPO-011).

## Verifiche della Fase 4, validazione, asticella, vault

Non applicabili: nessun candidato. Nessun p-value di validazione, nessuna asticella (m = 0). Il criterio del vault
(regole.md, sezione 9) non si applica. Trade al mese attesi in paper: nessuno.

## Se il bot potrebbe eseguire queste regole

Domanda senza oggetto (nessun candidato). In generale (ipotesi.md, convenzioni): le varianti su 1d con stop a 3 ATR
hanno stop di circa il 31%, oltre il tetto del 6% del bot; il bot ha indicatori dal vivo solo fino a 1 ora e limiti
di portafoglio che cambierebbero una strategia su 80 monete (regole.md, sezione 15).

## Previsione per vault e trasferimento

Nessuna: non c'è un candidato del gruppo da portare al vault.

## Limiti (protocollo sezione 11 e regole.md sezione 15)

* Potenza bassa per vantaggi piccoli e trade a grappoli: «nessuna strategia valida» non vuol dire «nessun
  vantaggio»; vuol dire che con 30 varianti e questo esame nessun vantaggio si distingue dal caso.
* I ritocchi si sono concentrati su due famiglie (5 ciascuna, il massimo), come vuole l'ordine della regola 6: i
  loro t più alti sono il massimo di 5 tentativi e vanno letti con questo sconto.
* Il controllo positivo è passato con l'uscita a 1 giorno (decisione del proprietario); con l'uscita a 7 giorni non
  passava per la poca potenza della (a) di gruppo.
* Sopravvivenza: le monete sono quelle liquide nel 2023 e quotate prima del 2022.
* Funding: ICPUSDT senza file di funding per 16 mesi (2021-05 a 2022-08): lì nessun funding addebitato.
* Il guardiano giudica le azioni, non gli script; le letture della sessione sono state solo nei percorsi ammessi.

## Misure di processo

Da `codice/misure.py` (`lavoro/misure.out`), sul log fino alla voce GRUPPO-053; le voci successive sono la Fase 5
e la chiusura.

* Durata dalla prima all'ultima voce: 869 minuti (2026-10-10 17:17 → 2026-10-11 07:46 UTC); pause dichiarate 666
  minuti (attesa dell'ambiente, attesa delle risposte dell'utente); senza pause 203 minuti.
* Varianti: 30 (20 da idee nuove, 10 ritocchi), 20 famiglie, 6 scarti. Ritocchi solo dopo la nota delle idee
  esaurite (GRUPPO-042).
* Per idea, minuti dalla registrazione della prima variante all'ultimo risultato, varianti e spiegazioni
  concorrenti scritte in `ipotesi.md`: I-01 7 min, 2 varianti, 11 spiegazioni; I-02 6, 2, 11; I-03 2, 2, 11; I-04
  5, 1 (più uno scarto), 11; I-05 4, 1 (più uno scarto), 11; I-07 88, 7 (5 ritocchi), 11; I-08 3, 1, 11; I-11 2, 1,
  11; I-12 2, 1 (più uno scarto), 11; I-17 1, 1, 11; I-19 120, 7 (5 ritocchi), 11; I-24 3, 2, 11; I-26 2, 2, 11;
  idee solo con scarti: I-06 (11 spiegazioni), I-10 (11). (I minuti delle idee su 1d sono brevi perché le varianti
  giravano in lotti: registrazione e test di seguito, risultati scritti dopo il lotto.)
* Varianti diventate candidati in Fase 2: 0 da idee nuove, 0 da ritocchi.
* Varianti che hanno battuto nettamente la (a) e la (b) con R medio dopo i costi non positivo: 0.
* Minuti di calcolo per variante (esame di costruzione): circa 0,5-0,8 a 1d, 3,1-3,4 a 4h, 11,2-11,6 a 1h; sotto le
  stime della sezione 14 di regole.md per 1d e 4h, alla soglia alta per 1h (5-11 minuti).
* Previsioni (campo `previsione_corretta` delle 30 voci di risultato): giuste 21, sbagliate 9 (per lo più di poco,
  sull'R, sul t o sul numero di trade); i motivi sono nelle voci di risultato. I due controlli positivi non contano.
* Rifiuti del guardiano, tutti per errori di forma miei e nessuno aggirato: 9 (3 in GRUPPO-002, 2 in GRUPPO-004, 1
  in GRUPPO-005, 1 in GRUPPO-036, 1 nella registrazione GRUPPO-012, 1 nella registrazione GRUPPO-045).
* Una correzione nel log (GRUPPO-013): una data scritta a memoria invece che con l'orologio della macchina.
