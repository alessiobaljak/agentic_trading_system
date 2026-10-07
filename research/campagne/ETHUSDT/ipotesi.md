# Ipotesi della campagna ETHUSDT

Scritte PRIMA di qualunque test e prima di aver guardato i prezzi di ETHUSDT (lo
scarico dei dati era in corso mentre questo file nasceva; nessun numero di mercato
è stato letto). Ogni idea ha una fonte pubblicata prima del 2024-01-01; nessuna
viene dal gate, dal registro o dal paper del bot. Le stime dei trade (Fase 1,
punto 7) si aggiungono in fondo a ogni idea quando i dati di costruzione sono
caricati, e si registrano nel log prima del test.

Esito atteso dichiarato prima di cominciare: nessuna strategia valida trovata per
questa moneta. Con dodici idee di sette famiglie diverse e un'asticella di
Benjamini-Hochberg al 10 %, l'esito più probabile è che nessun candidato passi.

## Regole comuni a tutte le idee (fissate ora, non si cambiano)

**Serie.** Segnali e stop sul last price; liquidazione sul mark price; funding
storico a ogni settlement. Costi del protocollo per ETHUSDT: commissione 0,05 % per
lato, slippage 0,01 % per lato (fascia della scheda), poi costi doppi.

**Dimensione.** Regole del bot (`config/regole_dimensione.md`): rischio 1 % del
capitale per trade sulla distanza dallo stop, leva massima 2, margine isolato, tasso
di mantenimento 2,5 %, capitale 1.000. Stop oltre il 6 % del prezzo: si conta e si
dichiara (nel bot renderebbe il setup non tradabile), non si impone.

**Uscita comune.** Ogni idea dichiara la propria, scelta fra questi mattoni, prima
del test: stop a `k` volte l'ATR a 14 barre del timeframe del segnale (`k` = 2 per
default; la robustezza prova 1,5 e 3); durata massima `H` barre, poi chiusura
all'apertura della barra dopo; eventuale uscita su segnale contrario; eventuale
target a `rr` volte la distanza dello stop. L'entrata casuale «con la stessa uscita»
usa esattamente gli stessi mattoni con gli stessi numeri.

**Baseline (sezione 8).** (a) stesso effetto senza condizione: ingresso a ogni barra
libera, stessa direzione e stessa uscita; (b) entrate casuali: 200 strategie con
`entrate_casuali` (stesso numero di trade, stessa distanza media, stessa uscita), si
riporta il percentile dell'R medio del candidato e la differenza «netta» (2 errori
standard, bootstrap a blocchi) rispetto alla strategia casuale mediana; (c) buy and
hold e il suo opposto. «Nettamente» = oltre 2 errori standard. Blocco del bootstrap
= trade che cadono nella durata massima di una posizione, e comunque almeno un
giorno.

**Timeframe.** Scelto per ogni idea dal meccanismo, prima del test. I timeframe
adiacenti servono solo a verificare (Fase 4), mai a scegliere.

**Direzione.** Long e short sono varianti separate e si contano separate sul budget.

### Le spiegazioni concorrenti «noiose», comuni a tutte le idee

Valgono per ogni idea qui sotto, in aggiunta a quelle specifiche. Per ciascuna:
cosa prevede e cosa la smentirebbe.

| n. | Spiegazione | Previsione se è vera | Cosa la smentisce |
|---|---|---|---|
| C1 | È casuale: con 30 varianti qualcosa sembra funzionare per forza | il candidato non supera il 90° percentile delle entrate casuali; non regge in validazione | percentile alto in costruzione E p-value sotto l'asticella in validazione |
| C2 | È il trend di fondo: ETH è salita dal 2020 al 2021, qualunque long «funziona» | il long batte, lo short perde; il long NON batte l'entrata casuale long; sparisce nel 2022 | il candidato batte le entrate casuali nella stessa direzione e tiene in anni di segno diverso |
| C3 | È solo il mercato: ETH segue BTC | la stessa regola applicata ai rendimenti di BTC spiega il risultato; il vantaggio sparisce nei giorni in cui BTC è ferma | il vantaggio resta condizionando sulla parte di rendimento di ETH non spiegata da BTC |
| C4 | È volatilità: i trade vinti sono quelli nei periodi agitati, e la vol si prevede | il vantaggio in R sparisce a parità di volatilità; l'R medio è dovuto a pochi trade grandi | il risultato regge togliendo il 5 % dei trade migliori e a bande di volatilità separate |
| C5 | Artefatto dei dati: candela a cavallo, buchi, duplicati, ombra errata | il risultato cambia con la regola intra-barra opposta o con il ritardo di una barra crolla a zero | la regola opposta cambia poco, il ritardo peggiora gradualmente |
| C6 | Effetto costi: il vantaggio lordo c'è ma è dell'ordine dei costi | sopravvive a costi semplici, muore a costi doppi | regge a costi doppi |
| C7 | Dipendenza fra trade: trade sovrapposti o dello stesso giorno contati come indipendenti | l'errore standard a blocchi è molto più largo di quello ingenuo; la differenza non è più netta | la differenza resta netta con il bootstrap a blocchi |
| C8 | Lookahead nascosto: l'indicatore usa la barra in corso | il test del ritardo di una barra azzera il risultato | peggioramento graduale col ritardo |
| C9 | Funding: il risultato viene dal funding incassato dagli short (o pagato dai long), non dal prezzo | il pnl lordo di prezzo è circa zero; il funding fa la differenza | il vantaggio resta sul pnl di prezzo senza funding |
| C10 | Un solo periodo: tutto il vantaggio sta in 1-2 mesi (marzo 2020, maggio 2021, novembre 2022) | il rendimento per anno è positivo in un anno solo | vantaggio presente in almeno due anni su tre, e senza i 2 mesi migliori |

---

## Famiglia A — Tendenza

### I-01 Momento di serie temporale (time-series momentum)

**Fonte.** «Time Series Momentum», Tobias J. Moskowitz, Yao Hua Ooi, Lasse H.
Pedersen, *Journal of Financial Economics* 104(2), 2012. Per le crypto: «Risks and
Returns of Cryptocurrency», Yukun Liu e Aleh Tsyvinski, *Review of Financial Studies*
34(6), 2021 (versione NBER 2018), che documenta un momento a 1-4 settimane su Bitcoin.

**Affermazione verificabile.** Il segno del rendimento di ETHUSDT negli ultimi 7
giorni predice il segno del rendimento nelle 4 ore successive: entrare nel verso del
rendimento passato dà un R medio superiore a quello di entrate casuali con la stessa
uscita.

**Sotto-domande.** Vale solo per movimenti grandi (oltre una soglia in deviazioni
standard) o anche piccoli? Vale anche nel 2022 (ribasso) o solo nel 2020-21? Chi
muove il prezzo: flussi lenti di investitori che arrivano in ritardo sulle notizie
(la spiegazione dei fonti) o leva che si accumula? Quanto dura l'effetto: ore o
giorni?

**Spiegazioni concorrenti specifiche** (oltre a C1-C10): (S1) *è solo il trend
2020-21*: previsione, il long vince e lo short perde ovunque; smentita, il momento
short vince nel 2022. (S2) *è il momento di BTC*, non di ETH: previsione, il
rendimento passato di BTC predice ETH meglio di quello di ETH stessa; smentita, il
segnale di ETH resta predittivo a parità di segnale BTC. (S3) *è autocorrelazione
spuria da candele mancanti*: smentita dalla conta dei buchi e dal ritardo.

**Ipotesi completa.** ETHUSDT, candele 4h. Lookback 42 barre (7 giorni). Long se il
rendimento a 42 barre è positivo e la posizione è piatta; short se negativo. Uscita:
segnale contrario (il segno cambia), oppure stop a 2 ATR(14), oppure H = 42 barre.
Timeframe 4h perché il meccanismo (flussi lenti, orizzonte 1-4 settimane) non chiede
candele più fini e a 4h i costi sono piccoli rispetto al movimento. Varianti: long,
short.

**Previsione.** Long: R medio fra 0 e +0,10, profit factor 1,0-1,15, forte nel 2020-21
e nullo nel 2022; non batte nettamente le entrate casuali long. Short: R medio
intorno a zero o negativo, con il 2022 positivo.

### I-02 Rottura del canale (trading range breakout)

**Fonte.** «Simple Technical Trading Rules and the Stochastic Properties of Stock
Returns», William Brock, Josef Lakonishok, Blake LeBaron, *Journal of Finance* 47(5),
1992 (regola «trading range break»). Per le crypto: «Technical trading rules in the
cryptocurrency market», Klaus Grobys, Shaker Ahmed, Niranjan Sapkota, *Finance
Research Letters* 32, 2020.

**Affermazione verificabile.** Una chiusura sopra il massimo delle ultimi 30 barre
da 4h (5 giorni) è seguita da un rendimento positivo in eccesso rispetto a entrate
casuali; una chiusura sotto il minimo, da uno negativo.

**Sotto-domande.** Le rotture con volume alto sono diverse? Quante sono false
rotture (rientro nel canale entro 6 barre)? La rottura funziona meglio dopo un
periodo stretto (collegamento con I-11)?

**Spiegazioni concorrenti specifiche.** (S1) *le rotture sono il momento in cui la
vol esplode*: previsione, l'R medio è dovuto a pochi trade grandi (C4). (S2) *sono
gli stop degli altri*: previsione, il movimento dopo la rottura dura poche barre
poi torna; smentita, il vantaggio resta con H = 30 barre. (S3) *è il trend 2020-21*
(C2).

**Ipotesi completa.** ETHUSDT, 4h. Long se close > massimo delle 30 barre
precedenti (esclusa la corrente); short se close < minimo delle 30. Uscita: stop a
2 ATR(14); chiusura sotto il minimo delle 15 barre precedenti (per il long,
simmetrico per lo short); H = 60 barre. Varianti: long, short.

**Previsione.** Long: profit factor 1,0-1,2, win rate basso (35-45 %), R medio
+0,05; batte l'entrata casuale long solo se C2 è falsa. Short: profit factor sotto 1
tranne nel 2022.

## Famiglia B — Ritorno alla media

### I-03 Inversione a brevissimo termine (RSI a 2 periodi)

**Fonte.** «Fads, Martingales, and Market Efficiency», Bruce N. Lehmann, *Quarterly
Journal of Economics* 105(1), 1990 (inversione a una settimana); «Short Term Trading
Strategies That Work», Larry Connors e Cesar Alvarez, 2008 (regola RSI a 2 periodi).

**Affermazione verificabile.** Su candele da 1 ora, dopo che l'RSI a 2 periodi
scende sotto 10 il rendimento delle barre successive è positivo in eccesso
rispetto a entrate casuali long; sopra 90, negativo.

**Sotto-domande.** L'inversione è più forte quando la discesa è avvenuta a volume
basso (poca informazione) che a volume alto (notizia)? Vale di notte UTC (libro
sottile) più che di giorno? Dura 1-3 ore o di più?

**Spiegazioni concorrenti specifiche.** (S1) *spread e rimbalzo del bid-ask*: a 1h
l'effetto è dell'ordine dei costi (C6); previsione, muore a costi doppi. (S2) *è il
rimbalzo dopo le liquidazioni a cascata*: previsione, funziona solo nelle barre con
range estremo; smentita, regge escludendo le barre oltre 3 ATR. (S3) *il long
inverte, lo short no, perché il trend è su* (C2).

**Ipotesi completa.** ETHUSDT, 1h. Long se RSI(2) < 10; short se RSI(2) > 90.
Uscita: RSI(2) torna oltre 50 (per il long; sotto 50 per lo short), stop a 2 ATR(14),
H = 12 barre. Varianti: long, short.

**Previsione.** Win rate alto (60-65 %) ma R medio piccolo (0 a +0,05) e profit
factor 1,0-1,1 a costi semplici; a costi doppi profit factor sotto 1. Non passerà.

### I-04 Reazione eccessiva dopo una candela anomala

**Fonte.** «Does the Stock Market Overreact?», Werner F. M. De Bondt e Richard
Thaler, *Journal of Finance* 40(3), 1985; per le crypto: «Price overreactions in the
cryptocurrency market», Guglielmo Maria Caporale e Alex Plastun, *Journal of
Economic Studies* 46(5), 2019, che studia i giorni con rendimento anomalo e il
comportamento del giorno dopo.

**Affermazione verificabile.** Dopo una candela da 4h con rendimento oltre 2,5
deviazioni standard (misurate sulle 180 barre precedenti), la barra successiva ha
un rendimento di segno opposto in eccesso rispetto a entrate casuali.

**Sotto-domande.** L'inversione vale per le candele anomale al rialzo e al ribasso
allo stesso modo? Dipende dal volume della candela anomala? Avviene nella barra
subito dopo o in 2-3 barre?

**Spiegazioni concorrenti specifiche.** (S1) *continuazione, non inversione*: la
fonte crypto trova anche segni di momento dopo l'anomalia; previsione, lo short
dopo una candela anomala positiva perde; questa è la direzione opposta all'ipotesi
e si legge dal risultato (non diventa una nuova variante). (S2) *liquidazioni a
cascata*: la candela anomala è la liquidazione; il rimbalzo c'è solo quando il
funding era estremo prima (collegamento con I-10). (S3) *pochi eventi enormi*
(C4, C10): marzo 2020 e maggio 2021 dominano.

**Ipotesi completa.** ETHUSDT, 4h. Short se il rendimento della barra appena chiusa
è > +2,5 σ; long se < −2,5 σ. Uscita: H = 3 barre (12 ore), stop a 2 ATR(14).
Varianti: long (dopo anomalia negativa), short (dopo anomalia positiva).

**Previsione.** Long: profit factor 1,0-1,2 con R medio +0,05, dominato da pochi
eventi; short: profit factor sotto 1 (nel 2020-21 le candele anomale positive
continuano).

## Famiglia C — Valore relativo e trasmissione fra monete

### I-05 Ritardo di ETH su BTC (lead-lag)

**Fonte.** «Return and volatility spillovers among cryptocurrencies», Dimitrios
Koutmos, *Economics Letters* 173, 2018; «Virtual relationships: Short- and long-run
evidence from BitCoin and altcoin markets», Pavel Ciaian, Miroslava Rajcaniova,
d'Artis Kancs, *Journal of International Financial Markets, Institutions and Money*
52, 2018.

**Affermazione verificabile.** Su candele da 1 ora, se nell'ultima barra BTC è
salita oltre una soglia e ETH è salita meno di BTC, la barra successiva di ETH ha un
rendimento positivo in eccesso (ETH «recupera»); simmetrico al ribasso.

**Sotto-domande.** Il recupero avviene entro 1 ora o entro 4? È più forte quando il
divario è grande? Vale nelle ore di scambi sottili? Si è ridotto nel tempo (gli
arbitraggisti lo chiudono)?

**Spiegazioni concorrenti specifiche.** (S1) *è il momento di BTC, non il ritardo*
(C3): previsione, il segnale funziona anche quando ETH ha già seguito BTC; smentita,
funziona solo quando il divario è ampio. (S2) *il divario è spread e rumore
microstrutturale* (C6). (S3) *l'effetto era del 2020 ed è sparito* (C10).

**Ipotesi completa.** ETHUSDT, 1h, con BTCUSDT 1h come riferimento. Long se il
rendimento di BTC nell'ultima barra è > +0,75 % e il rendimento di ETH è inferiore a
quello di BTC di almeno 0,25 punti percentuali; short simmetrico. Uscita: H = 4
barre, stop a 2 ATR(14). Varianti: long, short.

**Previsione.** R medio +0,02 a +0,08 lordo in entrambe le direzioni, win rate
52-55 %, profit factor 1,0-1,1; a costi doppi quasi nullo. Il ritardo esisteva nel
2020 e si è ridotto: rendimento per anno decrescente.

### I-06 Ritorno alla media del rapporto ETH/BTC (pairs trading)

**Fonte.** «Pairs Trading: Performance of a Relative-Value Arbitrage Rule», Evan
Gatev, William N. Goetzmann, K. Geert Rouwenhorst, *Review of Financial Studies*
19(3), 2006.

**Affermazione verificabile.** Quando il logaritmo del rapporto ETH/BTC si scosta
di oltre 2 deviazioni standard dalla sua media mobile a 120 barre da 4h (20
giorni), ETH tende a rientrare: short ETH se il rapporto è alto, long se basso, con
rendimento in eccesso rispetto a entrate casuali.

**Sotto-domande.** Il rientro avviene per un movimento di ETH o di BTC (noi operiamo
solo ETH)? Lo scostamento persiste nei periodi in cui ETH ha una storia propria
(estate 2020 DeFi, 2021, settembre 2022 Merge)? Quanto dura il rientro?

**Spiegazioni concorrenti specifiche.** (S1) *il rapporto ha un trend proprio, non
una media*: previsione, gli scostamenti al rialzo continuano (ETH sale più di BTC
per mesi) e lo short perde. (S2) *il rientro avviene via BTC*: ETH resta ferma e BTC
si muove; previsione, l'R di ETH è nullo anche se il rapporto rientra. (S3) *è
l'inversione a breve di ETH* (I-03) travestita.

**Ipotesi completa.** ETHUSDT, 4h, con BTCUSDT 4h come riferimento. z = (log(ETH/BTC)
− media 120 barre) / dev. standard 120 barre. Short se z > 2; long se z < −2. Uscita:
z torna a 0 (attraversa la media), stop a 2 ATR(14), H = 60 barre. Varianti: long,
short.

**Previsione.** Win rate 55-60 %, profit factor 1,0-1,15, con perdite grandi nei
periodi di trend del rapporto; R medio +0,03.

### I-07 Momento relativo ETH contro BTC (cross-sectional momentum)

**Fonte.** «Common Risk Factors in Cryptocurrency», Yukun Liu, Aleh Tsyvinski, Xi
Wu, *Journal of Finance* 77(2), 2022 (fattore momento fra monete, formazione 1-4
settimane, tenuta 1 settimana); «Returns to Buying Winners and Selling Losers:
Implications for Stock Market Efficiency», Narasimhan Jegadeesh e Sheridan Titman,
*Journal of Finance* 48(1), 1993.

**Affermazione verificabile.** Se nelle ultime 2 settimane ETH ha reso più di BTC,
nella settimana successiva ETH rende più di entrate casuali long; se ha reso meno,
short ETH batte entrate casuali short.

**Sotto-domande.** L'effetto sta nel rendimento assoluto di ETH o solo nel
relativo? Vale con tenuta di una settimana o si esaurisce prima? È diverso nei
periodi di «stagione delle alt»?

**Spiegazioni concorrenti specifiche.** (S1) *è il momento assoluto di ETH* (I-01)
con un altro nome: previsione, i segnali coincidono per oltre l'80 % delle
settimane. (S2) *è una sola stagione* (C10): tutto il guadagno fra gennaio e maggio
2021. (S3) *il relativo inverte, non continua*, a 2 settimane: lo short dopo
sottoperformance perde.

**Ipotesi completa.** ETHUSDT, 1d, con BTCUSDT 1d come riferimento. Ogni lunedì alla
chiusura della candela della domenica: se il rendimento di ETH a 14 giorni meno
quello di BTC è positivo, long; se negativo, short. Ingresso all'apertura del
lunedì, uscita H = 7 barre (la domenica successiva), stop a 2 ATR(14) giornaliero
(che supererà spesso il 6 % del bot: si dichiara). Varianti: long, short.

**Previsione.** Circa 140 trade in costruzione, metà per direzione (sotto il minimo
per direzione: probabilmente «non si sa» a meno che le due direzioni si giudichino
insieme; si dichiara). Profit factor 1,0-1,2.

## Famiglia D — Calendario

### I-08 Inversione del fine settimana

**Fonte.** «Bitcoin time-of-day, day-of-week and month-of-year effects in returns
and trading volume», Dirk G. Baur, Daniel Cahill, Keith Godfrey, Zhangxin (Frank)
Liu, *Finance Research Letters* 31, 2019 (volumi e volatilità più bassi nel fine
settimana); «Seasonality in cryptocurrencies», Lars Kaiser, *Finance Research
Letters* 31, 2019 (effetti di calendario deboli e instabili). Meccanismo di
inversione da liquidità sottile: Lehmann 1990 (vedi I-03).

**Affermazione verificabile.** Il rendimento del lunedì ha segno opposto a quello
del fine settimana (sabato + domenica): con mercati sottili il fine settimana esagera
e il lunedì, al ritorno della liquidità, corregge.

**Sotto-domande.** Vale solo per fine settimana con movimento grande (> 1 σ)? La
correzione avviene nelle prime ore UTC del lunedì (Asia) o con l'apertura
europea/americana? Vale nel 2022?

**Spiegazioni concorrenti specifiche.** (S1) *Kaiser ha ragione: non c'è nulla*
(C1). (S2) *il lunedì continua, non inverte* (il fine settimana anticipa flussi
reali): previsione, R medio negativo. (S3) *dipende da pochi lunedì* (C10).

**Ipotesi completa.** ETHUSDT, 1d. Alla chiusura della candela della domenica: se
il rendimento sabato+domenica è > +1 %, short; se < −1 %, long. Ingresso
all'apertura del lunedì, uscita H = 1 barra (chiusura del lunedì, cioè apertura di
martedì), stop a 2 ATR(14) giornaliero. Varianti: long, short.

**Previsione.** Circa 100 fine settimana oltre soglia in costruzione, divisi fra le
due direzioni: sotto il minimo per direzione. R medio intorno a zero; profit
factor 0,9-1,1.

### I-09 Momento intragiornaliero (la prima ora predice l'ultima)

**Fonte.** «Market intraday momentum», Lei Gao, Yufeng Han, Sophia Zhengzi Li,
Guofu Zhou, *Journal of Financial Economics* 129(2), 2018: il rendimento della
prima mezz'ora predice quello dell'ultima mezz'ora del giorno, per effetto dei
flussi degli operatori che aggiustano le posizioni a fine giornata.

**Affermazione verificabile.** Il rendimento dell'ora 00:00-01:00 UTC di ETHUSDT
predice il segno del rendimento dell'ora 23:00-24:00 UTC dello stesso giorno UTC.
Nei perpetui il giorno UTC è segnato dal settlement del funding a 00:00 e dalla
chiusura della candela giornaliera.

**Sotto-domande.** Esiste un «giorno» nelle crypto? Il settlement delle 00:00 crea
flussi di chiusura? Vale di più nei giorni con prima ora grande?

**Spiegazioni concorrenti specifiche.** (S1) *non c'è giornata nelle crypto*:
previsione, R medio zero (C1). (S2) *è il momento a 1 giorno* (I-01 corto):
previsione, usare il rendimento 00:00-23:00 predice meglio della sola prima ora.
(S3) *costi* (C6): un trade di 1 ora con 0,12 % di costi su un'ora che si muove
dello 0,5 %.

**Ipotesi completa.** ETHUSDT, 1h. Alla chiusura della barra 22:00-23:00 UTC: long se
il rendimento della barra 00:00-01:00 dello stesso giorno è > +0,3 %, short se
< −0,3 %. Ingresso all'apertura di 23:00, uscita H = 1 barra (apertura di 00:00),
stop a 2 ATR(14). Varianti: long, short.

**Previsione.** Non batterà i costi: profit factor 0,9-1,05, R medio 0 a −0,03.

## Famiglia E — Funding e posizionamento

### I-10 Funding estremo come segnale contrario (carry affollato)

**Fonte.** «Fundamentals of Perpetual Futures», Songrun He, Asaf Manela, Omri Ross,
Victor von Wachter, 2022 (manoscritto, arXiv 2212.06888); «Crypto carry», Maik
Schmeling, Andreas Schrimpf, Karamfil Todorov, BIS Working Paper n. 1087, 2023
(il carry dei perpetui è alto quando la domanda di leva long è affollata e prevede
rendimenti più bassi).

**Affermazione verificabile.** Quando il tasso di funding dell'ultimo settlement è
sopra il 90° percentile dei 90 settlement precedenti (30 giorni), il rendimento di
ETH fino al settlement successivo è negativo in eccesso rispetto a entrate casuali
short (i long affollati pagano e si sgonfiano); sotto il 10° percentile, positivo.

**Sotto-domande.** L'effetto sta nel prezzo o solo nel funding incassato (C9)?
Dura 8 ore o più? È più forte dopo più settlement estremi di fila? L'intervallo
del funding è sempre di 8 ore nel periodo (si verifica in Fase 0)?

**Spiegazioni concorrenti specifiche.** (S1) *il funding alto accompagna il trend,
che continua*: previsione, lo short perde nel 2020-21. (S2) *è solo il funding
incassato* (C9): il pnl di prezzo è nullo. (S3) *il percentile mobile insegue il
regime*: in un trend lungo quasi ogni settlement è «estremo».

**Ipotesi completa.** ETHUSDT, 8h (candele allineate ai settlement 00:00, 08:00,
16:00 UTC). Alla chiusura della barra 8h: short se il tasso del settlement appena
pagato è sopra il 90° percentile mobile; long se sotto il 10°. Uscita: H = 1 barra
(il settlement dopo), stop a 2 ATR(14) a 8h. Varianti: short (funding alto), long
(funding basso); terza variante solo se le prime due passano le baseline: H = 3
barre.

**Previsione.** Short: profit factor 1,0-1,2 con il contributo del funding
incassato; sul solo prezzo circa 1,0. Long: pochi segnali (il funding negativo è
raro), forse sotto i 100 trade.

## Famiglia F — Volatilità

### I-11 Compressione della volatilità e rottura (squeeze)

**Fonte.** «Bollinger on Bollinger Bands», John Bollinger, McGraw-Hill, 2001 (lo
«squeeze»: bande strette precedono movimenti ampi); «Street Smarts», Laurence A.
Connors e Linda Bradford Raschke, 1995 (rapporto di volatilità storica a 6/100
giorni sotto 0,5).

**Affermazione verificabile.** Quando la volatilità realizzata a 30 barre da 4h è
sotto la metà di quella a 180 barre, la prima chiusura fuori dal range delle 30
barre è seguita da un movimento nello stesso verso con rendimento in eccesso
rispetto a entrate casuali e rispetto alle rotture senza compressione (I-02).

**Sotto-domande.** La direzione della rottura è prevedibile o solo l'ampiezza? La
compressione precede davvero l'espansione (è una previsione sulla volatilità, non
sul segno)? Quante rotture dopo compressione sono false?

**Spiegazioni concorrenti specifiche.** (S1) *la compressione predice la vol, non
la direzione*: previsione, win rate 50 % ma R grandi in valore assoluto nei due
sensi; profit factor circa 1. (S2) *è I-02 con meno trade*: previsione, R medio
uguale a I-02. (S3) *pochi eventi* (C1).

**Ipotesi completa.** ETHUSDT, 4h. Condizione: dev. standard dei rendimenti a 30
barre / dev. standard a 180 barre < 0,5. Long se, con la condizione vera nella barra
precedente, close > massimo delle 30 barre; short se < minimo. Uscita: stop a 2
ATR(14), target a 2 volte la distanza dello stop, H = 30 barre. Varianti: long,
short.

**Previsione.** Meno di 100 trade per direzione in costruzione: probabile scarto
per stima dei trade, o «non si sa».

## Famiglia G — Volume

### I-12 Premio del volume alto

**Fonte.** «The High-Volume Return Premium», Simon Gervais, Ron Kaniel, Dan H.
Mingelgrin, *Journal of Finance* 56(3), 2001: un titolo con volume insolitamente
alto attira attenzione e nei giorni successivi rende di più (ipotesi della
visibilità); «Market Statistics and Technical Analysis: The Role of Volume»,
Lawrence Blume, David Easley, Maureen O'Hara, *Journal of Finance* 49(1), 1994.

**Affermazione verificabile.** Dopo una candela da 12h con volume in USDT nel 10 %
più alto delle 100 barre precedenti, le 6 barre successive (3 giorni) hanno
rendimento positivo in eccesso rispetto a entrate casuali long, qualunque sia il
segno della candela.

**Sotto-domande.** Vale sia per candele di volume al rialzo che al ribasso? Su
una moneta già seguitissima l'attenzione marginale conta? Il volume alto nelle
crypto è liquidazione (ribasso) più che attenzione?

**Spiegazioni concorrenti specifiche.** (S1) *il volume alto è una cascata di
liquidazioni e il rialzo dopo è il rimbalzo di I-04*: previsione, il vantaggio sta
tutto nelle candele di volume negative. (S2) *è il trend* (C2). (S3) *volume in
USDT contaminato da wash trading o da cambi di tick*: artefatto (C5).

**Ipotesi completa.** ETHUSDT, 12h. Long se il volume in USDT della barra chiusa è
sopra il 90° percentile delle 100 barre precedenti. Uscita: H = 6 barre, stop a 2
ATR(14). Variante: long. Lo short non ha meccanismo nella fonte: non si prova.

**Previsione.** Profit factor 1,0-1,15 dominato dal 2020-21; non batte l'entrata
casuale long.

---

## Scarti dichiarati prima di cominciare (non consumano budget)

* **Cicli di mesi e halving** (candele settimanali o più lunghe): fuori dai
  timeframe ammessi (regola 10).
* **Scadenze mensili delle opzioni** (ultimo venerdì del mese, 08:00 UTC; «Stock
  price clustering on option expiration dates», Ni, Pearson, Poteshman, *Journal
  of Financial Economics* 2005): 33 scadenze in costruzione, molto sotto i 100
  trade; e il meccanismo (pinning) predice meno volatilità, non una direzione.
* **Eventi singoli di ETH** (il passaggio al proof-of-stake di settembre 2022):
  un evento solo, nessun conteggio possibile.

## Stime dei trade (si compilano con i dati di costruzione, prima di ogni registrazione)

Vedi il log: ogni registrazione porta `trade_stimati`, contati sui soli segnali dei
dati di costruzione con la regola di non sovrapposizione (un segnale si conta solo
se dista dal precedente contato almeno la durata massima H della posizione).

*Correzione del 7 ottobre (voce ETHUSDT-C001 del log):* per le idee con uscita su
segnale si usa una seconda stima che simula solo entrate e uscite da segnale; la
regola qui sopra resta per le altre. La modifica è avvenuta dopo aver visto i
conteggi dei segnali, mai un rendimento.

---

## Secondo lotto di idee (scritto il 7 ottobre 2026 mentre il primo lotto girava, prima di vederne i risultati)

Il primo lotto ha lasciato 14 varianti scartate per pochi trade e 9 in test: 21 varianti
di budget libere. Il proprietario chiede di spendere il budget su famiglie diverse. Le
quattro idee qui sotto usano dati che il primo lotto non toccava (flusso degli ordini,
prezzo mark, apertura del giorno, ora del giorno). Regole comuni, baseline e spiegazioni
concorrenti C1-C10 come sopra.

## Famiglia H — Flusso degli ordini

### I-13 Squilibrio degli ordini a mercato (compratori aggressivi contro venditori aggressivi)

**Fonte.** «Order imbalance, liquidity, and market returns», Tarun Chordia, Richard Roll,
Avanidhar Subrahmanyam, *Journal of Financial Economics* 65(1), 2002: lo squilibrio fra
acquisti e vendite aggressive è legato ai rendimenti e quello passato predice, debolmente,
quelli futuri (pressione di inventario dei market maker che si scarica con ritardo).

**Affermazione verificabile.** Su candele da 1 ora, se nelle ultime 4 ore la quota di
volume in USDT scambiato da compratori aggressivi (campo taker_buy_quote_volume di Binance)
supera il 58 %, le 2 ore successive hanno rendimento positivo in eccesso rispetto a entrate
casuali; sotto il 42 %, negativo.

**Sotto-domande.** Lo squilibrio continua (pressione) o inverte (inventario che si
scarica)? Conta di più a volume alto? Il campo di Binance misura davvero gli aggressori
(sì, per costruzione: è il lato che prende liquidità)?

**Spiegazioni concorrenti specifiche.** (S1) *lo squilibrio è già nel prezzo*: il
rendimento delle 4 ore spiega tutto e lo squilibrio non aggiunge nulla. (S2) *inversione,
non continuazione*: R medio negativo. (S3) *scambi fittizi o automi che alternano*:
artefatto (C5).

**Ipotesi completa.** ETHUSDT, 1h. Quota compratori aggressivi a 4 barre = somma
taker_buy_quote / somma quote_volume. Long se > 0,58; short se < 0,42. Uscita: H = 2
barre, stop a 2 ATR(14). Varianti: long, short.

**Previsione.** R medio +0,01 a +0,04 lordo, profit factor 1,0-1,05: sotto i costi doppi.
Non batte le baseline.

## Famiglia I — Base del perpetuo

### I-14 Premio del perpetuo sul prezzo mark

**Fonte.** «BitMEX bitcoin derivatives: Price discovery, informational efficiency, and
hedging effectiveness», Carol Alexander, Jaehyuk Choi, Heungju Park, Sungbin Park,
*Journal of Futures Markets* 40(1), 2020 (il perpetuo guida il prezzo spot ma il suo premio
sull'indice rientra); He, Manela, Ross, von Wachter 2022 (vedi I-10): il funding ancora
il perpetuo all'indice.

**Affermazione verificabile.** Su candele da 1 ora, quando il rapporto fra chiusura last
e chiusura mark meno 1 (il premio del perpetuo) supera il 90° percentile delle 720 barre
precedenti (30 giorni), le barre successive hanno rendimento negativo in eccesso (il
premio rientra); sotto il 10°, positivo.

**Sotto-domande.** Il rientro è del last verso il mark o del mark verso il last? Il
premio estremo coincide con le candele anomale (I-04)? Dura un'ora o meno?

**Spiegazioni concorrenti specifiche.** (S1) *il premio estremo è un picco di una barra e
rientra dentro la stessa barra*: a 1h non resta nulla. (S2) *è I-04 travestita*. (S3) *il
mark è una media del premio, quindi il «premio» misura il momento a brevissimo*:
previsione, segno uguale a I-03.

**Ipotesi completa.** ETHUSDT, 1h. premio = close_last / close_mark − 1. Short se premio
> 90° percentile mobile (720 barre precedenti); long se < 10°. Uscita: H = 4 barre, stop
a 2 ATR(14). Varianti: short, long.

**Previsione.** R medio +0,02 a +0,06 lordo in entrambe le direzioni; profit factor
1,0-1,1; muore a costi doppi.

## Famiglia J — Rottura del range d'apertura

### I-15 Rottura del range d'apertura del giorno UTC

**Fonte.** «Day Trading with Short Term Price Patterns and Opening Range Breakout», Toby
Crabel, 1990: il primo movimento del giorno oltre una frazione del range medio tende a
continuare fino alla chiusura.

**Affermazione verificabile.** Su candele da 1 ora, la prima chiusura del giorno UTC
sopra l'apertura del giorno più 0,5 volte l'ATR giornaliero (14 giorni precedenti) è
seguita, fino alla fine del giorno, da un rendimento positivo in eccesso rispetto a
entrate casuali con la stessa uscita; simmetrico al ribasso.

**Sotto-domande.** Nelle crypto l'apertura a 00:00 UTC è un riferimento che qualcuno
guarda (settlement del funding, candela giornaliera)? La continuazione dura ore o si
esaurisce? Vale di più nei giorni con range stretto il giorno prima (I-11)?

**Spiegazioni concorrenti specifiche.** (S1) *è il momento intragiornaliero* (I-09 e
I-01 a poche barre). (S2) *falsa rottura e inversione*: R medio negativo. (S3) *il
risultato sta nei giorni di trend 2020-21* (C2, C10).

**Ipotesi completa.** ETHUSDT, 1h, con l'ATR a 14 giorni calcolato sulle candele
giornaliere precedenti. Long alla prima chiusura oraria > apertura del giorno + 0,5
ATR giornaliero; short alla prima < apertura − 0,5 ATR giornaliero; un solo ingresso al
giorno. Uscita: alla chiusura della barra delle 23:00 (cioè all'apertura delle 00:00),
stop a 2 ATR(14) orario, H = 24 barre. Varianti: long, short.

**Previsione.** Profit factor 1,0-1,1, R medio 0 a +0,05; non netto rispetto alle
entrate casuali long nel 2020-21.

## Famiglia K — Sessione del giorno

### I-16 Ore americane e ore asiatiche

**Fonte.** Baur, Cahill, Godfrey, Liu, *Finance Research Letters* 31, 2019 (effetti
dell'ora del giorno nei rendimenti e nei volumi di Bitcoin, legati agli orari dei mercati
tradizionali).

**Affermazione verificabile.** Le ore della sessione azionaria americana (13:00-21:00
UTC) hanno rendimento medio positivo in eccesso rispetto a entrate casuali long con la
stessa durata; le ore asiatiche (00:00-08:00 UTC) negativo (short in eccesso).

**Sotto-domande.** L'effetto è dei flussi istituzionali americani del 2020-22
(correlazione con le azioni) o un artefatto del trend? Cambia con l'ora legale (13:30
contro 14:30 UTC)?

**Spiegazioni concorrenti specifiche.** (S1) *è il trend 2020-21 distribuito sulle ore*
(C2): la baseline a ogni barra long lo rivela. (S2) *Kaiser: niente di stabile* (C1). (S3)
*effetto dell'ora legale*: si verifica spezzando per stagione.

**Ipotesi completa.** ETHUSDT, 1h. Variante long: alla chiusura della barra delle 12:00
(che chiude alle 13:00) long, uscita H = 8 barre (apertura delle 21:00), stop a 2 ATR(14).
Variante short: alla chiusura della barra delle 23:00 short, uscita H = 8 (apertura delle
08:00), stop a 2 ATR(14).

**Previsione.** Entrambe sotto i costi: profit factor 0,95-1,05, R medio circa 0; nessuna
batte nettamente le entrate casuali.
