# BNBUSDT — consegna della campagna

Protocollo versione 4.5 (approvata il 2026-10-09 alle 12:06 UTC). Sessione di campagna del
9 ottobre 2026, branch `research/campagna/BNBUSDT`. Tutti i numeri vengono dal log
(`log.jsonl`, id indicati) e dal codice in `codice/`. Nessun candidato è «validato»: l'esito
dell'asticella è **provvisorio** e lo conferma il coordinamento al Passo 4.

## In una riga

Un candidato va al vault: **BNBUSDT-045**, un long a 1h che compra i cali bruschi (RSI a 2
periodi sotto 5) in tendenza rialzista, solo nel fine settimana UTC, ed esce al rimbalzo. Ha
superato la validazione al limite (32 trade con 30 minimi, p-value 0,031, R medio +0,047). È il
quinto ritocco di una sola famiglia, con un filtro scelto guardando i dati di costruzione: il
rischio che sia fortuna è alto e lo dico prima del vault.

## Il candidato BNBUSDT-045

### Regole (congelate: `candidati/BNBUSDT-045/regole.md`)

| | Regola |
|---|---|
| Moneta | BNBUSDT, perpetuo USDS-M |
| Timeframe | 1h, candele last price |
| Direzione | solo long |
| Ingresso | alla chiusura di una barra a 1h che apre di sabato o domenica (UTC), se chiusura > SMA(200) e RSI di Wilder a 2 periodi < 5; ingresso all'apertura della barra dopo |
| Uscita | prima chiusura sopra la SMA(5), oppure dopo 12 barre in posizione; uscita all'apertura della barra dopo |
| Stop | 2,5 ATR(14) sotto la chiusura della barra di segnale, sul last price |
| Target | nessuno |
| Filtri | nessun ingresso su segnali di maggio e giugno 2020 (sotto la liquidità minima) |
| Dimensione e leva | rischio 1% per trade, nozionale al massimo 2 volte il capitale, margine isolato, liquidazione sul mark |

**Motivo economico.** Connors e Alvarez («Short Term Trading Strategies That Work», 2008): in
tendenza rialzista un calo brusco di poche ore viene da venditori impazienti o forzati e chi
fornisce liquidità viene pagato col rimbalzo. Il filtro del fine settimana: con gli operatori
istituzionali in gran parte assenti la liquidità è più sottile e i cali sono più spesso pressione
di liquidità che informazione. Questo secondo motivo è stato scritto **dopo** aver visto i numeri
per giorno (nota BNBUSDT-N018): è una spiegazione plausibile, non una previsione fatta prima.

### Metriche, separate per periodo

| | Costruzione (2020-02-01 → 2022-10-28) | Validazione (2022-10-29 → 2023-12-31) |
|---|---|---|
| Trade | 74 (2020: 21, 2021: 34, 2022: 19) | 32 (2022: 4, 2023: 28) |
| R medio a trade, dopo i costi | +0,138 | +0,047 |
| R mediano | +0,200 | +0,111 |
| R medio per anno | 2020 +0,171; 2021 +0,184; 2022 +0,020 | 2022 −0,038; 2023 +0,059 |
| R medio senza i 3 trade migliori | +0,120 | +0,008 |
| Profit factor | 2,76 | 1,49 |
| Quota di trade vincenti | 76% | 75% |
| Uscite | 71 sul segnale, 3 stop | 29 sul segnale, 2 stop, 1 a fine dati |
| Rendimento totale (rischio 1% a trade) | +10,8% | +1,7% |
| Drawdown massimo | −1,6% | −2,3% |
| Costi medi in R (commissioni e slippage) | 0,047 | 0,079 |
| Baseline (a), stesso stop e uscita entrando a ogni barra libera | −0,047; t 4,12, netta | −0,094; t 1,94, non netta (soglia 2,32) |
| Baseline (b), 200 simulazioni a entrate casuali | −0,048; t 3,96, netta | −0,092; t 2,14, non netta (soglia 2,32) |
| Percentile fra le simulazioni casuali (indizio) | 100 | 98,5 |
| p-value contro la (b) (`contro_baseline`) | 0,0003 | **0,031** |
| Buy and hold per anno (contesto) | 2020 +49%; 2021 +1.267%; 2022 −42% | 2022 (ultimi 2 mesi) −17%; 2023 +26% |
| Correlazione fra R dei trade e BTC nella stessa finestra | 0,31 | 0,54 |
| Trade ridotti per il tetto di leva | 0 | 0 |
| Violazioni del margine dalla liquidazione | 0 | 0 |

Voci del log: BNBUSDT-045 (costruzione), BNBUSDT-045-validazione.

### Verifiche della Fase 4 (sulla costruzione; nota BNBUSDT-N030)

| Verifica | Esito |
|---|---|
| Robustezza (ogni parametro ±20%, uno alla volta) | superata: 13 casi su 16 contano (3 sotto i 70 trade), t contro la (b) positivo in tutti, netta in 12 su 13 |
| Timeframe adiacenti | 2h: t +1,34 (R −0,001), positivo; 30m: 3 trade, non conta. Superata, ma a 2h il vantaggio in R non c'è |
| Costi doppi | superata: R +0,088, t 3,91 netta |
| Ritardo di una barra | superata: t 2,19 contro 3,96 (metà 1,98), R +0,048 |
| Stabilità per anno | superata: sopra la media della (b) in 2020, 2021, 2022 |
| Pochi trade estremi | superata: +0,120 senza i 3 migliori |
| Regola intra-barra opposta | nessuna differenza (nessun target) |
| Liquidazione | nessuna violazione |
| Prova dello scettico: (b) solo nelle barre del fine settimana | t 4,43, netta |

### Asticella (provvisoria)

Un solo candidato in validazione (m = 1): p-value 0,031 ≤ 0,10, quindi l'asticella di
Benjamini-Hochberg al 10% è superata; trade di validazione 32 ≥ 30. **Esito provvisorio**: lo
conferma il coordinamento al Passo 4.

### Rischi noti

1. **Scelta su sottogruppi.** Il filtro del fine settimana è il migliore di 7 gruppi per giorno
   guardati sugli stessi trade di costruzione. L'esame di costruzione non corregge per questo; la
   validazione sì, ma con un margine sottile.
2. **Pochi stop.** 3 stop su 74 in costruzione (4%) contro il 14% della regola senza filtro: con
   il 14% l'R medio scenderebbe verso +0,03.
3. **Validazione fragile.** 32 trade (due sopra il minimo), t sotto la soglia di «nettamente»;
   senza i 3 migliori l'R di validazione è +0,008. I 4 trade del 2022 hanno R medio negativo.
4. **Esecuzione nella prima ora.** I due candidati gemelli senza il filtro del fine settimana
   (BNBUSDT-043 e 044) sono caduti perché il vantaggio spariva entrando un'ora dopo. Per
   BNBUSDT-045 il ritardo regge (t 2,19), ma l'R scende da +0,138 a +0,048.
5. **Costi.** In validazione i costi pesano 0,079 R a trade, cioè più dell'R medio (+0,047).
6. **Slippage del 2020.** Il volume del 2020 era circa un decimo di quello del 2023: per i 21
   trade del 2020 lo slippage della scheda è ottimista (`fase0_dati.md`).
7. **Mercato.** La correlazione con BTC nella stessa finestra sale da 0,31 a 0,54 in validazione.

### Criterio nel vault (`criterio_vault`)

Tutte insieme, sul periodo 2024-01-01 → 2026-09-30: profit factor dopo i costi almeno 1,10;
almeno 30 trade; rendimento totale positivo; R medio sopra il 90° percentile delle entrate
casuali con la stessa uscita (stessa direzione, stesso numero di trade, stessa durata media).

### Paper

Frequenza del backtest: 74 trade in circa 33 mesi di costruzione e 32 in circa 14 mesi di
validazione, cioè circa **2,2-2,3 trade al mese**. Per arrivare a 50 trade servono circa **22
mesi**, oltre il massimo di 12 (`paper_durata_massima_mesi`): al Passo 9 l'utente dovrà decidere
se accettarlo.

### Il bot può eseguirlo?

Non così com'è. (1) Il bot opera solo coppie scritte dal suo gate nel registro: serve l'aggiunta
«coppia del protocollo» descritta al Passo 0 (`config/regole_dimensione.md`). (2) Il timeframe a
1h esiste fra gli indicatori dal vivo del bot e le posizioni durano al massimo 12 barre, sotto
l'orizzonte di 96 barre del bot. (3) Lo stop: in costruzione 8 trade su 74 avevano lo stop oltre
il 6% del prezzo (massimo 17,5%, nel 2020-2021), che il bot rifiuterebbe come setup non
tradabile; in validazione nessuno (mediana 2,1%, massimo 3,4%). (4) Il filtro di calendario,
RSI(2), SMA(200), SMA(5) e ATR(14) sono codice semplice da scrivere come strategia del bot.

### Previsione per il vault e il trasferimento

Vault: probabilità che passi tutte e quattro le condizioni del `criterio_vault` intorno al 25-35%
(stima mia, non un calcolo): la regola senza filtro ha un vantaggio vicino a zero, e la parte
del fine settimana è la più esposta alla fortuna. Se passa, mi aspetto un R medio fra 0 e +0,08 e
un profit factor vicino a 1,1-1,4. Trasferimento: improbabile. Il filtro del fine settimana e le
soglie vengono da BNBUSDT; su monete con più volume nel fine settimana o con costi in R più alti
(stop più stretti) mi aspetto che fallisca sulla maggior parte delle monete.

## Varianti usate e budget

* **30 varianti testate su 30**: 25 da idee nuove, 5 ritocchi (tutti nella famiglia
  BNBUSDT-005, il massimo di 5), **25 famiglie**. 15 scarti per trade minimi (non consumano
  budget), di cui 2 dovuti a un errore del codice della campagna, corretto (BNBUSDT-N013).
* Idee con fonte: 18 in 9 famiglie di meccanismi, dichiarate esaurite prima dei ritocchi (N017).
* Candidati in Fase 2: 3, tutti da ritocchi (BNBUSDT-043, 044, 045); 0 da idee nuove.
  BNBUSDT-043 e 044 scartati in Fase 4 per il ritardo di una barra (e 044 anche per i costi
  doppi); nessun errore di lookahead trovato (N023).
* In validazione: 1 candidato (BNBUSDT-045, unico sopravvissuto della sua famiglia).

## Idee provate (riepilogo; dettagli in `lezioni_moneta.md`)

Nessuna delle 25 varianti di idee nuove ha battuto nettamente la (a) o la (b). Le più vicine al
caso: RSI(2) a 1h (t 1,67), squilibrio degli ordini aggressivi long a 4h (1,50), shock di
illiquidità long a 4h (1,20), funding molto negativo long a 8h (1,16).

## Misure di processo

Ricavate dal log con `codice/misure.py` e da `ipotesi.md`.

* Durata dalla prima all'ultima voce del log: dal 2026-10-09 12:22:00 UTC al 2026-10-09 13:23:31
  UTC, **62 minuti**, senza pause (le date vengono dall'orologio della macchina). La maggior parte
  del lavoro di Fase 0 e Fase 1 (scarico, codice, fonti, ipotesi) è avvenuta fra le prime voci.
* Minuti dalla prima registrazione all'ultimo risultato, per idea (i test a 4h, 8h e 1d durano
  pochi secondi, quindi molte idee risultano sotto il minuto): I-01 0,1; I-02 0,1; I-03 24,8 (6
  varianti, 5 ritocchi); I-04 0,0; I-05 0,1; I-06 0,5; I-07 0,0; I-08 0,1; I-09 0,1; I-10 0,1;
  I-11 1,1; I-12 0,2; I-14 0,1; I-16 0,1; I-17 0,1; I-18 0,7. I-13 e I-15 non hanno varianti
  testate (solo scarti).
* Spiegazioni concorrenti scritte in `ipotesi.md`: 10 per ognuna delle 18 idee.
* Varianti diventate candidati in Fase 2: 0 da idee nuove, 3 da ritocchi.
* Varianti che hanno battuto nettamente la (a) e la (b) con R medio dopo i costi non positivo: 0.
* Rifiuti del guardiano: 6, tutti per errori miei di forma dei comandi, registrati e non aggirati
  (N002, N005, N010, N012, N014, N029).
