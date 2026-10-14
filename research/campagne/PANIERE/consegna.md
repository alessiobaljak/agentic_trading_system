# Consegna della campagna PANIERE (seconda edizione, versione 5.0)

**Esito: nessuna strategia valida trovata per il paniere**, dopo aver usato tutto il budget (18 varianti e 12 ritocchi
su 12). Due varianti sono diventate candidate in costruzione e sono cadute tutte e due in Fase 4. Nessuna
validazione è stata fatta e nessun candidato è «validato».

Tutti i numeri vengono dal log (`log.jsonl`, voci PANIERE-001 .. PANIERE-090) e dai file di `lavoro/`; ogni esame è
di `research/src/gruppo.py` con `timeframe="1d"` e il terreno della seconda edizione (ordine limite) costruito dallo
strumento (`opzioni.terreno` nei risultati). Periodo: costruzione fino al 2023-01-16, 80 monete più BTCUSDT.

## Le tre idee, in breve

| Idea | Varianti esaminate | Scarti (sotto 700 trade) | t contro la (b) più alto | Esito |
|---|---|---|---|---|
| A, tendenza | 4 (A1-20 long e short, A2 long e short) | 2 (A1-55 long e short) | 1,00 (A1-20 long, 7 blocchi) | morta a questo orizzonte |
| B, momentum fra monete | 3 (B2 short, B3 long, B3 short) | 3 (B1 long e short, B2 long) | 0,46 (B3 short) | morta |
| C, ritardo dopo Bitcoin | 4 + 11 ritocchi (+1 ritocco scartato) | 2 (C1-2 short, C2-1,5 short) | 3,24 (PANIERE-040) | due candidati, caduti in Fase 4 |

Ogni variante con il suo `t` contro la (b) e il numero di blocchi (decisione del proprietario del 14 ottobre):

| Id | Variante | Trade | R medio | t (b) / soglia | t (a) | Blocchi | Monete senza ingressi (b) |
|---|---|---|---|---|---|---|---|
| 016 | A1-20 long | 727 | +0,477 (senza i 30 migliori −0,069) | 1,00 / 2,52 | 0,70 | 7 | nessuna |
| 017 | A1-20 short | 789 | +0,006 | 0,01 / 2,87 | 0,22 | 5 | nessuna |
| 020 | A2 long | 1.283 | +0,096 | 0,21 / 3,31 | 0,34 | 4 | nessuna |
| 021 | A2 short | 1.633 | −0,056 | −0,51 / 2,87 | −0,26 | 5 | KLAYUSDT, LPTUSDT (0,7%) |
| 025 | B2 short | 730 | −0,045 | 0,12 / 2,25 | 0,21 | 12 | nessuna |
| 026 | B3 long | 819 | −0,045 | −1,44 / 2,52 | −0,57 | 7 | nessuna |
| 027 | B3 short | 846 | −0,020 | 0,46 / 2,37 | 0,37 | 9 | nessuna |
| 028 | C1-1,5 long | 1.297 | +0,157 | 1,69 / 2,25 | 1,43 | 12 | nessuna |
| 029 | C1-1,5 short | 743 | −0,033 | −0,07 / 2,32 | −0,01 | 10 | nessuna |
| 030 | C1-2 long | 870 | +0,267 | **2,48 / 2,25** | 2,17 | 12 | nessuna |
| 032 | C2-1,5 long | 803 | +0,168 | 2,14 / 2,18 | 1,71 | 16 | nessuna |
| 036 | 030 + regime di Bitcoin, k 1,5 | 845 | +0,238 | 1,94 / 2,25 | 1,78 | 12 | nessuna |
| 037 | 030, uscita a 10 giorni | 793 | +0,234 | 1,69 / 2,28 | 1,15 | 11 | nessuna |
| 038 | 030, uscita a 3 giorni | 951 | +0,173 | 2,13 / 2,23 | 1,85 | 13 | nessuna |
| 039 | 032, uscita a 3 giorni | 886 | +0,132 | **2,38 / 2,17** | 1,84 | 17 | nessuna |
| 040 | 039 con k 1,25 | 1.363 | +0,130 | **3,24 / 2,11** | **2,19 / 2,11** | 25 | nessuna |
| 041 | 032 con k 1,25 | 1.230 | +0,163 | **2,83 / 2,11** | 1,92 | 24 | nessuna |
| 042 | 028 con k 1,25 | 1.963 | +0,144 | 2,05 / 2,16 | 1,54 | 18 | nessuna |
| 043 | 042, uscita a 3 giorni | 2.327 | +0,135 | **3,20 / 2,18** | **2,20 / 2,18** | 16 | nessuna |
| 044 | 042 + regime di Bitcoin | 1.233 | +0,214 | 2,28 / 2,28 | 1,93 | 11 | nessuna |
| 045 | 029 con k 1,25 | 915 | +0,015 | 0,44 / 2,37 | 0,41 | 9 | nessuna |
| 047 | 045 con k 1,0 + regime | 766 | +0,096 | 1,25 / 2,43 | 1,10 | 8 | nessuna |

(046, ritocco dello short con il regime, scarto con 641 trade.) In grassetto i confronti netti.

## I due candidati e perché sono caduti

Regole complete in `candidati/PANIERE-040/regole.md` e `candidati/PANIERE-043/regole.md`. Tutti e due long, 1 giorno,
dopo un giorno forte al rialzo di Bitcoin (oltre 1,25 deviazioni standard dei 60 giorni precedenti): PANIERE-040 le
20 monete più in ritardo, PANIERE-043 tutte le monete in ritardo; stop 2,5 ATR(20), uscita dopo 3 barre, ingresso a
limite, rischio 1%, leva 2, isolated.

| Verifica (Fase 4) | PANIERE-040 | PANIERE-043 |
|---|---|---|
| Costi doppi | superata (t 3,17, R +0,109) | superata (t 3,18, R +0,114) |
| Ritardo di una barra | **non superata**: t 1,58, 0,49 volte | **non superata**: t 1,08, 0,34 volte |
| Robustezza ±20% | superata (16 casi su 16 netti) | superata (11 su 12 netti) |
| Timeframe adiacenti | non applicabile (solo 1d) | non applicabile |
| Stabilità per anno | superata (2020, 2021, 2022 sopra la b) | superata |
| Estremi (trade, giorni, monete) | superati (+0,080 / +0,083 / +0,117) | superati (+0,099 / +0,083 / +0,124) |
| Liquidazione | **6 violazioni** | **8 violazioni** |
| Regola intra-barra opposta | nessuna differenza | nessuna differenza |

* Metriche di costruzione: PANIERE-040 1.363 trade, R +0,130, 25 blocchi, effetto grappolo 6,8, al massimo 43
  posizioni aperte insieme (tutte long) e 28 uscite in un giorno, moneta più presente TRXUSDT 3,4%, 55 monete su 60
  sopra la propria b. PANIERE-043 2.327 trade, R +0,135, 16 blocchi, grappolo 12,8, al massimo 70 posizioni insieme,
  70 uscite in un giorno, moneta più presente EOSUSDT 2,6%, 72 su 76 sopra la propria b. Trade ridotti per il tetto
  di leva: 0.
* **Liquidazione**: stop a 2,5 ATR(20) fra il 79% e il 95% del prezzo dopo crolli (UNFIUSDT maggio 2021, GTCUSDT
  dicembre 2021, KNCUSDT, PEOPLEUSDT, WAVESUSDT maggio 2022, BELUSDT e BLZUSDT giugno 2022), oltre 0,8 volte la
  distanza della liquidazione. È una conseguenza del terreno (stop in ATR giornalieri senza tetto), non della
  condizione d'ingresso: lo dico al proprietario perché vale per qualunque variante di questo terreno.
* **Ritardo**: il lookahead non è possibile per costruzione (le funzioni leggono solo dati chiusi da `ctx`, il
  controllo positivo dello stesso modulo crolla col ritardo come deve); inferito: una parte del recupero arriva già il
  giorno dell'ingresso (+0,08 R alla prima chiusura), e un giorno di ritardo la perde.
* **Sono il migliore di più tentativi**: 5 e 8 tentativi nell'idea C, la stessa coppia di modifiche (soglia 1,25 e
  uscita a 3 barre); battono la (a) per 0,08 e 0,02 sopra la soglia.

## Cosa abbiamo capito (osservato, sui dati 2020 – 16 gennaio 2023)

* Dopo un giorno forte al rialzo di Bitcoin le altre monete salgono nei giorni dopo: comprarle tutte dà +0,075 R a
  trade (t 1,97, PANIERE-089); comprare solo quelle rimaste indietro quasi raddoppia (+0,135, t 3,20). Il ritardo
  conta per circa metà; l'altra metà è il mercato che continua. Lato short (dopo un giorno forte al ribasso) niente.
* Il vantaggio è concentrato in pochi giorni (36-63 giorni di segnale in tre anni) e dipende da cosa fa Bitcoin dopo
  (+0,39 R se sale nei 5 giorni dopo, −0,10 se scende: non prevedibile all'ingresso).
* La tendenza (idea A) e il momentum fra monete (idea B) non battono il caso a questo orizzonte; molte loro varianti
  non arrivano nemmeno a 700 trade sommati con l'ordine limite.
* L'ordine limite toglie trade: 7 varianti su 18 sotto i 700.

## Rischi e limiti da riportare

* Potenza: con uscite fino a 60 barre i blocchi sono 4-7 e la soglia 2,5-3,3; solo le varianti brevi (idea C)
  hanno abbastanza blocchi per essere giudicate.
* Le serie di costruzione finiscono il 16 gennaio 2023, a metà di un rialzo: i trade usciti a «fine dati» (48-57 per
  variante C long) hanno R medio +1,1-1,5 e i due giorni migliori di PANIERE-040 e PANIERE-043 sono il 15-16 gennaio.
* ICPUSDT senza funding da maggio 2021 ad agosto 2022 (la fonte non ha i file): long un po' favoriti lì.
* Lo stop dei candidati (circa 22% del prezzo in mediana) è oltre il tetto del 6% del bot: così com'è il bot non
  potrebbe eseguirli.
* Sopravvivenza (monete vive e liquide nel 2023) e mercato comune: come nelle regole del gruppo, sezione 15.

## Trade attesi in paper, vault e trasferimento

Non applicabile: nessun candidato.

## Misure di processo (dal log, `codice/misure.py`, `lavoro/misure.json`)

* Dalla prima all'ultima voce: 6,97 ore (14 ottobre 2026, 07:13 – 14:11 UTC); pause 4,69 ore (due STOP per gli
  strumenti: lettura delle regole del gruppo; paniere e ordine limite mancanti in `gruppo.py`); senza le pause 2,28 ore.
* Minuti per idea dalla prima registrazione all'ultimo risultato: A 7,2; B 5,5; C 35,5 (con i ritocchi).
* Spiegazioni concorrenti scritte in `ipotesi.md`: A 12, B 11, C 12.
* Varianti esaminate 22 (11 idee nuove, 11 ritocchi); scarti 8 (7 idee nuove, 1 ritocco); famiglie ritoccate 4.
* Candidati in Fase 2: da idee nuove 0, da ritocchi 2 (PANIERE-040, PANIERE-043).
* Varianti nette contro (a) e (b) con R medio non positivo: 0.
* Minuti di calcolo per variante (registrazione → risultato): 1,6-1,7.
* Rifiuti del guardiano: 5 (PANIERE-002 e 003 risolti dalla correzione del coordinamento; tre errori miei di forma:
  `git log` fuori dalla cartella, `sed -i`, `2>&1`).
