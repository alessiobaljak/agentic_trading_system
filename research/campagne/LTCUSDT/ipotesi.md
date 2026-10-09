# LTCUSDT — Ipotesi (Fase 1)

Ogni idea si scrive qui, con tutte le sue varianti, PRIMA del primo test di quell'idea (regola 6).
Il codice delle varianti è in `codice/varianti.py`; il quadro comune (dati, filtro di liquidità,
baseline) in `codice/quadro.py`.

## Fatti comuni a tutte le varianti

* Periodo di costruzione: 2020-01-01 → 2022-10-18 (dati veri dal 2020-01-09): comprende il rialzo
  del 2021 e il ribasso del 2022 (il buy and hold per anno si riporta in ogni risultato).
* Costi di un giro (andata e ritorno), contati come taker: commissione 0,05% + slippage 0,02% per
  lato = 0,14% del nozionale. In R il costo è 0,14% / distanza dello stop: con stop al 6% è circa
  0,023 R, al 3% circa 0,047 R, al 2% 0,07 R, all'1% 0,14 R. Il tetto di leva 2 riduce i trade con stop
  sotto lo 0,5% (il rischio vero scende sotto l'1%).
* Funding (Fase 0): media per settlement a 8 ore 0,023% nel 2020, 0,037% nel 2021, 0,003% nel 2022.
  Un long tenuto 7 giorni nel 2021 paga in media 21 × 0,037% ≈ 0,77% del nozionale: con stop al 6% è
  circa 0,13 R. Uno short lo incassa.
* Lo stop massimo che il bot accetta è il 6% (`stop_massimo_bot`): ogni variante qui ha lo stop
  entro il 6%, salvo dove è scritto.
* Spiegazioni concorrenti comuni (valgono per ogni idea e non si ripetono per esteso): le scrivo
  qui una volta con previsione e smentita, e in ogni idea elenco quelle specifiche. Il numero di
  spiegazioni concorrenti di un'idea conta le comuni più le specifiche.

| # | Spiegazione comune | Cosa prevede | Cosa la smentisce |
|---|---|---|---|
| C1 | Effetto casuale | `t` contro la (b) sotto la soglia; R per anno di segno variabile | batte nettamente la (b) e l'R supera la (b) in più anni |
| C2 | Trend di fondo della moneta | i long vincono solo negli anni in salita (2020-21), gli short solo nel 2022; la (b), che entra a caso nella stessa direzione, fa lo stesso | batte la (b), che ha lo stesso trend |
| C3 | «È solo il mercato»: LTC segue BTC | la stessa regola calcolata su BTCUSDT dà gli stessi ingressi e lo stesso esito; i trade vincenti coincidono con mosse di BTC | la regola su LTC batte la (b) anche dove BTC non si muove, o la stessa regola su BTC non funziona |
| C4 | Volatilità: in fasi agitate stop e movimenti sono più grandi e l'R cambia scala | i guadagni stanno nei mesi più volatili; la (b) negli stessi mesi farebbe uguale | R positivo anche nei mesi calmi; batte la (b), che vive la stessa volatilità |
| C5 | Artefatto dei dati (buchi del 2022, barre tolte, prime ore del contratto) | trade vincenti a cavallo dei buchi o nelle prime barre | nessun trade importante vicino ai buchi |
| C6 | Effetto costi: lordo positivo, netto zero | R lordo positivo ma netto vicino a zero o negativo; a costi doppi negativo | R netto positivo anche a costi doppi |
| C7 | Funding: il guadagno viene dal funding, non dal prezzo | `funding_medio_r` grande rispetto all'R medio | R positivo senza il funding (R medio molto più grande del funding medio in R) |
| C8 | Pochi trade estremi | R medio senza i 3 migliori sotto la (b) | R senza i 3 migliori ancora sopra la (b) |
| C9 | Un solo regime (la bolla del 2021, o il crollo del 2022) | R sopra la (b) in un solo anno | R sopra la (b) in più della metà degli anni con almeno 10 trade |
| C10 | Errore di calcolo o lookahead | crollo col ritardo di una barra | il `t` col ritardo resta positivo e almeno metà |

---

## I-01 — Momentum di serie temporale settimanale

**Fonte.** Yukun Liu e Aleh Tsyvinski, «Risks and Returns of Cryptocurrency», NBER Working Paper
24877, agosto 2018 (poi Review of Financial Studies 34(6), 2021). Base generale: Tobias Moskowitz,
Yao Hua Ooi e Lasse Heje Pedersen, «Time Series Momentum», Journal of Financial Economics 104(2),
2012. Liu e Tsyvinski riportano un forte momentum di serie temporale nelle criptovalute: i
rendimenti della settimana passata prevedono quelli delle settimane successive.

**Affermazione verificabile.** Su LTCUSDT, dopo una settimana (7 giorni) con rendimento positivo,
il rendimento dei 7 giorni successivi è in media più alto di quello di 7 giorni presi a caso nella
stessa direzione; simmetricamente dopo una settimana negativa per lo short. Falsificata se l'R medio
non supera nettamente la (b).

**Sotto-domande.** Vale in tutte le fasi o solo nei trend forti (2021)? Conta la dimensione del
rendimento passato? Chi muove il prezzo: investitori che inseguono i rendimenti recenti (attenzione,
flussi di nuovi entranti), reazione lenta alle notizie; in crypto anche la leva che si accumula nei
trend. In quanto tempo: la fonte parla di 1-4 settimane.

**Spiegazioni concorrenti specifiche** (oltre a C1-C10):

| # | Spiegazione | Cosa prevede | Cosa la smentisce |
|---|---|---|---|
| S1 | Il momentum c'è solo in BTC (moneta guida), LTC lo eredita in ritardo e in modo rumoroso | la stessa regola su BTC rende di più e i trade di LTC vincono solo quando BTC era in trend | LTC batte la (b) anche nelle settimane in cui BTC è piatto |
| S2 | Lo stop al 6% taglia i trend prima che paghino | molti stop, R medio negativo anche quando il rendimento a 7 giorni dopo l'ingresso è positivo | pochi stop sui trade vincenti |
| S3 | Per i long il funding del 2021 mangia il vantaggio | `funding_medio_r` dei long vicino a 0,1 R | funding medio piccolo rispetto all'R |

Spiegazioni concorrenti per questa idea: 13.

**Ipotesi completa.** LTCUSDT, momentum di serie temporale settimanale, candele 1d (il meccanismo è
a settimane: una candela giornaliera basta e un timeframe più corto aggiungerebbe solo rumore).
Posizioni di 7 giorni.

**Varianti** (scritte tutte prima del primo test):

* **LTCUSDT-001** — 1d, long. Ingresso alla chiusura del giorno i se close[i] / close[i-7] − 1 > 0;
  si entra all'apertura del giorno dopo. Uscita: dopo 7 barre in posizione (all'apertura dell'ottava).
  Stop: 6% sotto il close del giorno di segnale (il massimo del bot: un trend settimanale su LTC ha
  oscillazioni giornaliere del 4-6%, uno stop più stretto misurerebbe il rumore). Nessun target.
  Motivo: è la regola della fonte, nella sua forma più semplice (segno del rendimento a una settimana,
  tenuta di una settimana).
* **LTCUSDT-002** — 1d, short. Specchio: ingresso se close[i] / close[i-7] − 1 < 0; uscita dopo 7 barre;
  stop 6% sopra il close del giorno di segnale. Motivo: la fonte trova il momentum in entrambe le
  direzioni; lo short incassa il funding positivo.

**Previsioni (al netto dei costi).** Costi 0,023 R a giro; funding per i long circa −0,05/−0,1 R nel
2020-21. Long: profit factor fra 0,9 e 1,3, R medio fra −0,05 e +0,15; non batte nettamente la (b)
(potenza bassa con circa 100 trade). Short: profit factor fra 0,8 e 1,2, R medio fra −0,1 e +0,1;
non batte nettamente la (b).

---

## I-02 — Breakout di canale (sistema delle «tartarughe»)

**Fonte.** Curtis Faith, «Way of the Turtle: The Secret Methods that Turned Ordinary People into
Legendary Traders», McGraw-Hill, 2007 (regole del «Sistema 1»: ingresso sul massimo dei 20 periodi
precedenti, uscita sul minimo dei 10 periodi precedenti, stop a 2 N con N la media del true range a
20 periodi).

**Affermazione verificabile.** Quando il close di LTCUSDT supera il massimo dei 20 periodi precedenti,
il prezzo nei giorni successivi continua nella direzione del breakout più spesso e di più di quanto
farebbe un ingresso a caso con la stessa uscita (simmetrico per il minimo).

**Sotto-domande.** Vale solo con volatilità che si espande? Chi sta comprando: trend follower e
sistemi che usano gli stessi livelli, stop degli short posti sopra i massimi recenti (che diventano
acquisti a mercato). Quando: nei periodi successivi al breakout, la fonte tiene la posizione finché
non c'è un breakout opposto di 10 periodi.

**Spiegazioni concorrenti specifiche:**

| # | Spiegazione | Cosa prevede | Cosa la smentisce |
|---|---|---|---|
| S1 | Falsi breakout dominano in un mercato laterale (2022) | molti piccoli stop, R per anno negativo nel 2022 | R positivo anche nel 2022 |
| S2 | Il guadagno viene da pochissimi trend lunghi | R senza i 3 migliori negativo | R senza i 3 migliori positivo |
| S3 | Il tetto del 6% allo stop cambia il sistema (stop più stretti di 2 N) | molti stop al 6% nei periodi agitati | stop quasi sempre a 2 N sotto il 6% |

Spiegazioni concorrenti per questa idea: 13.

**Ipotesi completa.** LTCUSDT, breakout di canale a 20 periodi con uscita sul canale opposto a 10
periodi, candele 4h. Timeframe: la fonte è giornaliera, ma un breakout dei 20 giorni su una sola
moneta in meno di tre anni è un evento raro; il meccanismo (ordini e sistemi che reagiscono al
superamento del massimo recente) non dipende dalla durata della candela, e a 4 ore i 20 periodi sono
poco più di 3 giorni, l'orizzonte dei breakout di breve. Scelta fatta prima di contare.

**Varianti:**

* **LTCUSDT-003** — 4h, long. Ingresso alla chiusura della barra i se close[i] > massimo degli high
  delle 20 barre precedenti (i-20 … i-1). Uscita («chiudi») alla chiusura della barra in cui
  close < minimo dei low delle 10 barre precedenti. Stop: 2 × media del true range a 20 barre sotto il
  close di segnale, ma al massimo il 6% (tetto del bot). Nessun target.
* **LTCUSDT-004** — 4h, short. Specchio: close[i] < minimo dei low delle 20 barre precedenti; uscita
  quando close > massimo degli high delle 10 barre precedenti; stop 2 × ATR20 sopra, al massimo 6%.

**Previsioni.** Stop tipico 2 × ATR a 4h ≈ 3-5%, costi circa 0,03-0,05 R a giro. Long: profit factor
fra 0,9 e 1,3; short: fra 0,8 e 1,2. Nessuna delle due batte nettamente la (b) (i breakout sono
seguiti spesso da ritorni nel canale; il vantaggio, se c'è, sta in pochi trend lunghi).

---

## I-03 — Ritorno verso la media dopo eccessi di breve (RSI a 2 periodi)

**Fonte.** Larry Connors e Cesar Alvarez, «Short Term Trading Strategies That Work», TradingMarkets
Publishing, 2008: comprare quando l'RSI a 2 periodi scende sotto 5-10 con il prezzo sopra la media a
200 periodi; uscire quando il close torna sopra la media a 5 periodi.

**Affermazione verificabile.** In una tendenza di fondo positiva (close sopra la media a 200 barre),
dopo due barre di forte calo (RSI a 2 periodi sotto 10) LTCUSDT rimbalza nelle barre successive più
di quanto faccia un ingresso a caso con la stessa uscita. Specchio per lo short in tendenza negativa.

**Sotto-domande.** Vale solo quando il calo è grande in assoluto o anche per piccoli cali in fasi
calme? Chi opera: venditori impazienti (liquidazioni di leva, panico) e compratori che forniscono
liquidità e chiedono un premio; in una tendenza positiva i compratori sono più pronti. Tempi: il
rimbalzo atteso è di poche barre.

**Spiegazioni concorrenti specifiche:**

| # | Spiegazione | Cosa prevede | Cosa la smentisce |
|---|---|---|---|
| S1 | In crypto i cali di breve continuano (momentum intragiornaliero, cascate di liquidazioni) | lo stop scatta spesso subito dopo l'ingresso | pochi stop nelle prime barre |
| S2 | Il rimbalzo è troppo piccolo rispetto ai costi | R lordo positivo, netto vicino a zero | R netto positivo con margine |
| S3 | Il filtro della media lunga fa tutto: comprare a caso in tendenza positiva rende uguale | la (a), che compra a ogni barra sopra la media, rende come la variante | batte nettamente la (a) |

Spiegazioni concorrenti per questa idea: 13.

**Ipotesi completa.** LTCUSDT, ritorno verso la media di breve dentro una tendenza, candele 4h. La
fonte è giornaliera (azioni, 5 sedute a settimana); su un mercato che gira 24 ore su 24 e con pochi
anni di storia, la candela da 4 ore conserva l'idea (due candele di eccesso, rimbalzo in poche
candele) con un numero di eventi sufficiente. Il filtro della tendenza è una condizione d'ingresso
dell'ipotesi, non un filtro aggiunto: la (a) entra a ogni barra libera senza RSI né media lunga.

**Varianti:**

* **LTCUSDT-005** — 4h, long. Ingresso alla chiusura della barra i se close[i] > media semplice dei
  close a 200 barre e RSI(2) di Wilder < 10. Uscita («chiudi») alla chiusura della prima barra con
  close > media semplice a 5 barre. Stop: 6% sotto il close di segnale (la fonte non usa stop; il 6%
  è quello del bot e fa da protezione dai crolli). Nessun target.
* **LTCUSDT-006** — 4h, short. Specchio: close < media a 200 barre e RSI(2) > 90; uscita alla prima
  chiusura sotto la media a 5 barre; stop 6% sopra.

**Previsioni.** Le posizioni durano poche barre e lo stop al 6% è lontano: costo circa 0,023 R a
giro ma R per trade piccoli (movimenti dell'1-3% → 0,2-0,5 R). Long: profit factor fra 0,9 e 1,4,
R medio fra −0,05 e +0,1; short: fra 0,8 e 1,2. Nessuna batte nettamente la (b).

---

## I-04 — Inversione dopo shock di prezzo con volume alto

**Fonte.** John Y. Campbell, Sanford J. Grossman e Jiang Wang, «Trading Volume and Serial
Correlation in Stock Returns», Quarterly Journal of Economics 108(4), novembre 1993: i movimenti di
prezzo accompagnati da volume alto tendono a invertirsi, perché riflettono domanda di liquidità di
operatori non informati, assorbita da chi fornisce liquidità solo in cambio di un rendimento atteso.

**Affermazione verificabile.** Dopo una barra oraria di LTCUSDT con rendimento molto negativo
(sotto −2,5 deviazioni standard dei rendimenti orari della settimana precedente) e volume molto
alto (oltre 3 volte la mediana della settimana precedente), il prezzo nelle 12 ore successive sale
più di quanto farebbe dopo un ingresso a caso con la stessa uscita. Specchio per gli shock positivi.

**Sotto-domande.** L'inversione è più forte quando lo shock è una cascata di liquidazioni (forte
volume, nessuna notizia)? È più debole quando lo shock segue BTC (notizia di mercato)? Chi opera:
liquidazioni forzate di posizioni a leva e stop a catena da un lato, market maker e arbitraggisti
dall'altro. Tempi: il ritorno atteso è in poche ore.

**Spiegazioni concorrenti specifiche:**

| # | Spiegazione | Cosa prevede | Cosa la smentisce |
|---|---|---|---|
| S1 | Lo shock è informazione (notizia): il prezzo non torna indietro | stop frequenti, R negativo; nessuna differenza fra shock con e senza BTC | R positivo e più alto quando BTC non si muove |
| S2 | Rimbalzo meccanico dentro lo spread/ombra della stessa barra, già finito alla chiusura | il rimbalzo è nella barra di segnale, non dopo: R nullo | R positivo dalla barra successiva |
| S3 | Gli shock arrivano a grappoli (giornate di crollo): un solo episodio fa il risultato | pochi giorni con molti trade fanno l'R medio | R positivo togliendo i giorni con più trade (blocco del bootstrap) |

Spiegazioni concorrenti per questa idea: 13.

**Ipotesi completa.** LTCUSDT, inversione dopo shock orari con volume alto, candele 1h (lo shock e il
suo assorbimento sono di ore; la settimana di riferimento sono 168 barre). Posizioni di 12 ore.

**Varianti:**

* **LTCUSDT-007** — 1h, long. Ingresso alla chiusura della barra i se il rendimento close-to-close
  della barra è < −2,5 × deviazione standard dei rendimenti orari delle 168 barre precedenti (i-168 …
  i-1) e il volume (in moneta base) della barra è > 3 × la mediana dei volumi delle 168 barre
  precedenti. Uscita: dopo 12 barre in posizione. Stop: 2 × media del true range a 24 barre sotto il
  close di segnale, al massimo 6%. Nessun target.
* **LTCUSDT-008** — 1h, short. Specchio: rendimento > +2,5 deviazioni standard e volume > 3 × mediana;
  uscita dopo 12 barre; stop 2 × ATR24 sopra, al massimo 6%.

**Previsioni.** Stop tipico 2 × ATR orario ≈ 1,5-3%: costi 0,05-0,1 R a giro. Long: profit factor
fra 0,9 e 1,4, R medio fra −0,1 e +0,15; short: fra 0,8 e 1,2. Nessuna batte nettamente la (b).

---

## I-05 — Affollamento della leva misurato dal funding

**Fonte.** Maik Schmeling, Andreas Schrimpf e Karamfil Todorov, «Crypto Carry», BIS Working Papers
n. 1087, marzo 2023. Il carry delle crypto (premio dei futures e funding dei perpetui) è alto quando
la domanda di esposizione a leva degli investitori che inseguono il trend è alta; un carry alto
precede una probabilità maggiore di liquidazioni e crolli.

**Affermazione verificabile.** Quando il funding di LTCUSDT resta alto per un giorno (media degli
ultimi 3 settlement noti ≥ 0,05% per 8 ore, cinque volte il livello base dello 0,01%), nei 3 giorni
successivi uno short rende più di uno short preso a caso con la stessa uscita (prezzo che scende più
il funding incassato). Specchio: con funding negativo per un giorno (short affollati) un long rende
più di un long a caso.

**Sotto-domande.** Conta la durata dell'affollamento o il livello? Chi opera: long a leva che pagano
per restare in posizione, arbitraggisti che vendono il perpetuo e comprano il sottostante; quando il
prezzo scende le liquidazioni dei long a leva lo spingono più giù. Tempi: liquidazioni nei giorni
successivi, la fonte guarda orizzonti di giorni e settimane.

**Spiegazioni concorrenti specifiche:**

| # | Spiegazione | Cosa prevede | Cosa la smentisce |
|---|---|---|---|
| S1 | Funding alto = trend forte che continua (il funding segue il prezzo) | gli short perdono più della (b) nel 2021 | gli short battono la (b) anche nel 2021 |
| S2 | Il guadagno dello short è solo il funding incassato | R medio ≈ funding medio incassato in R | R medio molto più grande del funding |
| S3 | Gli episodi di funding alto sono pochi e a grappoli (un paio di mesi del 2021) | pochi blocchi indipendenti, risultato da uno o due episodi | R positivo in più episodi distinti |

Spiegazioni concorrenti per questa idea: 13.

**Ipotesi completa.** LTCUSDT, contrarian sull'affollamento della leva, candele 8h (allineate ai
settlement delle 00, 08 e 16 UTC: il segnale nasce a ogni settlement). Alla chiusura della barra i
si usano solo i settlement con istante ≤ chiusura della barra (quello che cade esattamente alla fine
della barra non si usa: prudenza sul momento in cui il tasso diventa noto). Posizioni di 3 giorni
(9 barre).

**Varianti:**

* **LTCUSDT-009** — 8h, short. Ingresso se la media degli ultimi 3 settlement noti è ≥ 0,0005.
  Uscita dopo 9 barre. Stop 6% sopra il close di segnale. Nessun target.
  *Se `conta_trade` dà meno di 70 trade* (scarto, nessun test), la sostituisce **LTCUSDT-009b**:
  uguale con soglia 0,0003 (tre volte il livello base), scritta ora, prima di qualunque test di
  questa idea.
* **LTCUSDT-010** — 8h, long. Ingresso se la media degli ultimi 3 settlement noti è < 0 (short
  affollati). Uscita dopo 9 barre. Stop 6% sotto il close di segnale.

**Previsioni.** Costi 0,023 R a giro; lo short incassa funding (con 0,05% per 9 settlement circa
0,07 R). Short: profit factor fra 0,8 e 1,3, R medio fra −0,15 e +0,15; long: fra 0,8 e 1,3. Nessuna
batte nettamente la (b) (episodi a grappoli: pochi blocchi).

---

## I-06 — Ordini concentrati intorno ai numeri tondi

**Fonte.** Carol L. Osler, «Currency Orders and Exchange Rate Dynamics: An Explanation for the
Predictive Success of Technical Analysis», Journal of Finance 58(5), ottobre 2003. Gli ordini di
stop sono concentrati appena oltre i numeri tondi (stop di acquisto appena sopra, di vendita appena
sotto), gli ordini di presa di profitto sui numeri tondi: quando il prezzo attraversa un numero
tondo, gli stop scattano a catena e il movimento accelera nella stessa direzione.

**Affermazione verificabile.** Quando il close orario di LTCUSDT attraversa verso l'alto un numero
tondo, nelle 6 ore successive il prezzo sale più di quanto farebbe dopo un ingresso long a caso con
la stessa uscita; specchio per l'attraversamento verso il basso.

**Sotto-domande.** Quali numeri sono «tondi» per chi opera su LTC? Più forte sui livelli più tondi
(100, 200) che su quelli intermedi? Chi opera: trader al dettaglio con stop e ordini su livelli
tondi; i loro stop sono ordini a mercato. Tempi: la cascata di stop è veloce, ore.

**Spiegazioni concorrenti specifiche:**

| # | Spiegazione | Cosa prevede | Cosa la smentisce |
|---|---|---|---|
| S1 | I numeri tondi di LTC non sono speciali: l'attraversamento è solo un movimento in corso (momentum orario generico) | stesso risultato con livelli spostati di mezzo intervallo | — (verifica possibile solo come ritocco) |
| S2 | Gli ordini di presa di profitto sul livello fanno tornare indietro il prezzo (inversione, non continuazione) | molti stop subito dopo l'ingresso | pochi stop nelle prime barre |
| S3 | Attraversamenti ripetuti avanti e indietro in fasi laterali | molti trade a grappoli sullo stesso livello in pochi giorni, R negativo | R positivo anche togliendo i trade ripetuti |

Spiegazioni concorrenti per questa idea: 13.

**Ipotesi completa.** LTCUSDT, continuazione dopo l'attraversamento di un numero tondo, candele 1h.
Numeri tondi: multipli di 5 USDT quando il prezzo è sotto 100, multipli di 10 USDT da 100 in su
(intervalli fra il 5% e il 10% del prezzo: livelli che si vedono sul grafico e su cui si mettono
ordini). Posizioni di 6 ore.

**Varianti:**

* **LTCUSDT-011** — 1h, long. Ingresso alla chiusura della barra i se esiste un numero tondo L con
  close[i-1] < L ≤ close[i]. Uscita dopo 6 barre. Stop 2 × ATR24 sotto il close di segnale, al
  massimo 6%. Nessun target.
* **LTCUSDT-012** — 1h, short. Specchio: close[i-1] > L ≥ close[i]. Uscita dopo 6 barre. Stop 2 × ATR24
  sopra, al massimo 6%.

**Previsioni.** Stop tipico 1,5-3%, costi 0,05-0,1 R a giro. Long e short: profit factor fra 0,8 e
1,2, R medio fra −0,15 e +0,1; nessuna batte nettamente la (b).

---

## I-07 — Breakout del range d'apertura della giornata

**Fonte.** Toby Crabel, «Day Trading with Short Term Price Patterns and Opening Range Breakout»,
Traders Press, 1990: l'uscita del prezzo dal range dei primi momenti della seduta indica la direzione
della giornata.

**Affermazione verificabile.** Quando, dopo le 04:00 UTC, un close orario di LTCUSDT supera il
massimo delle prime quattro ore della giornata UTC (00:00-03:59), il prezzo a fine giornata è più
alto di quanto farebbe dopo un ingresso long a caso con la stessa uscita; specchio per il minimo.

**Sotto-domande.** In crypto la giornata «apre» davvero alle 00:00 UTC? (È l'apertura della candela
giornaliera di Binance, su cui molti calcolano i livelli.) Le prime quattro ore sono la mattina
asiatica; l'uscita dal range avviene spesso all'arrivo di Europa e Stati Uniti, con più volume. Chi
opera: sistemi intraday sui livelli della giornata, stop sopra/sotto il range. Tempi: entro la
giornata.

**Spiegazioni concorrenti specifiche:**

| # | Spiegazione | Cosa prevede | Cosa la smentisce |
|---|---|---|---|
| S1 | In un mercato 24 ore su 24 l'apertura UTC non ha un ruolo: è un breakout qualunque | stesso risultato con range di un altro orario | — (solo come ritocco) |
| S2 | I costi su un movimento intragiornaliero mangiano tutto | R lordo positivo, netto negativo | R netto positivo |
| S3 | I breakout falliscono e tornano nel range (stop al minimo del range) | stop frequenti | pochi stop |

Spiegazioni concorrenti per questa idea: 13.

**Ipotesi completa.** LTCUSDT, breakout del range delle prime 4 ore UTC, candele 1h, al massimo un
trade al giorno, chiusura a fine giornata.

**Varianti:**

* **LTCUSDT-013** — 1h, long. Range = massimo e minimo delle barre 00:00, 01:00, 02:00, 03:00 UTC
  della stessa giornata. Ingresso alla chiusura della prima barra della giornata, fra quella delle
  04:00 e quella delle 20:00 comprese, con close > massimo del range (al massimo un ingresso al
  giorno: se nella giornata c'è già stato un segnale, niente). Stop: al minimo del range (al massimo
  6% sotto il close di segnale). Uscita: alla chiusura della barra delle 23:00 (si esce all'apertura
  delle 00:00).
* **LTCUSDT-014** — 1h, short. Specchio: close < minimo del range; stop al massimo del range (al
  massimo 6%); stessa uscita.

**Previsioni.** Stop tipico 2-4% (range di 4 ore più il tratto fino al breakout), costi 0,04-0,07 R.
Long e short: profit factor fra 0,8 e 1,2; nessuna batte nettamente la (b).

---

## I-08 — Effetto del giorno della settimana (lunedì)

**Fonte.** Guglielmo Maria Caporale e Alex Plastun, «The day of the week effect in the
cryptocurrency market», Finance Research Letters 31, dicembre 2019: per BTC rendimenti anomali
(più alti) il lunedì.

**Affermazione verificabile.** Il rendimento di LTCUSDT dall'apertura del lunedì (00:00 UTC)
all'apertura del martedì è in media più alto di quello di un giorno preso a caso tenuto long con la
stessa uscita.

**Sotto-domande.** Il lunedì sconta le notizie del fine settimana e il ritorno dei flussi
istituzionali (mercati tradizionali chiusi nel fine settimana)? Vale per una moneta diversa da BTC?

**Spiegazioni concorrenti specifiche:**

| # | Spiegazione | Cosa prevede | Cosa la smentisce |
|---|---|---|---|
| S1 | L'effetto è di BTC e LTC lo segue solo in parte | lunedì di LTC positivi solo quando BTC sale | — (contesto con BTC) |
| S2 | Ricerca su più giorni della settimana: il lunedì è uscito per caso nella fonte | nessun effetto su LTC | effetto netto su LTC |

Spiegazioni concorrenti per questa idea: 12.

**Ipotesi completa.** LTCUSDT, long il lunedì, candele 1d.

**Variante:**

* **LTCUSDT-015** — 1d, long. Ingresso alla chiusura della barra giornaliera della domenica
  (si entra all'apertura del lunedì). Uscita dopo 1 barra (all'apertura del martedì). Stop 6% sotto
  il close di segnale. Nessun target.

**Previsioni.** Costi 0,023 R; R per trade = rendimento del giorno / 6%. Profit factor fra 0,8 e 1,3,
R medio fra −0,05 e +0,1; non batte nettamente la (b).

---

## I-09 — Compressione della volatilità e breakout (lo «squeeze» delle bande di Bollinger)

**Fonte.** John Bollinger, «Bollinger on Bollinger Bands», McGraw-Hill, 2001: una larghezza delle
bande ai minimi di lungo periodo (lo «squeeze») precede un'espansione della volatilità; l'uscita del
prezzo da una banda dopo lo squeeze indica la direzione del movimento.

**Affermazione verificabile.** Dopo una fase in cui la larghezza delle bande (20 periodi, 2 deviazioni
standard) di LTCUSDT a 4 ore è fra le più basse delle ultime 120 barre, un close sopra la banda
superiore è seguito da un rialzo più ampio di quello di un long preso a caso con la stessa uscita;
specchio sotto la banda inferiore.

**Sotto-domande.** L'espansione arriva sempre, ma la direzione si indovina dal primo breakout? Chi
opera: la compressione accumula ordini e stop vicini al prezzo; l'espansione li fa scattare. Tempi:
giorni (decine di barre a 4 ore).

**Spiegazioni concorrenti specifiche:**

| # | Spiegazione | Cosa prevede | Cosa la smentisce |
|---|---|---|---|
| S1 | L'espansione c'è ma la direzione è casuale (primo breakout falso) | molti stop alla media centrale, R vicino a zero | R positivo e pochi stop |
| S2 | Lo stop alla media centrale è troppo vicino: rumore | stop frequenti nelle prime barre | pochi stop iniziali |
| S3 | È un breakout come I-02, senza informazione in più dalla compressione | stesso R della variante di I-02 | R più alto della I-02 nella stessa direzione |

Spiegazioni concorrenti per questa idea: 13.

**Ipotesi completa.** LTCUSDT, breakout dopo compressione della volatilità, candele 4h (la fonte è
giornaliera con riferimento a «sei mesi»; a 4 ore 120 barre sono 20 giorni: la compressione relativa
alle ultime settimane, scelta per avere eventi a sufficienza; scelta fatta prima di contare).

**Varianti:**

* **LTCUSDT-016** — 4h, long. Larghezza delle bande = (banda superiore − banda inferiore) / media a
  20 barre. Squeeze alla barra i−1: la larghezza in i−1 è ≤ al 10° percentile delle larghezze delle
  120 barre precedenti (i−121 … i−2). Ingresso alla chiusura della barra i se c'è squeeze in i−1 e
  close[i] > banda superiore[i]. Stop: alla media a 20 barre (al massimo 6%). Uscita: alla chiusura
  della prima barra con close < media a 20 barre, oppure dopo 30 barre. Nessun target.
* **LTCUSDT-017** — 4h, short. Specchio: squeeze in i−1 e close[i] < banda inferiore[i]; stop alla media
  a 20 barre (al massimo 6%); uscita alla prima chiusura sopra la media, o dopo 30 barre.

**Previsioni.** Stop tipico 1,5-3% (metà della larghezza compressa), costi 0,05-0,1 R. Long e short:
profit factor fra 0,8 e 1,3; nessuna batte nettamente la (b).

---

## I-10 — Inerzia dopo un giorno anomalo

**Fonte.** Guglielmo Maria Caporale e Alex Plastun, «Price overreactions in the cryptocurrency
market», Journal of Economic Studies 46(5), 2019 (CESifo Working Paper 7280, 2018). Studiano bitcoin,
litecoin, ripple e dash: dopo un giorno anomalo il movimento del giorno dopo è più ampio, in entrambe
le direzioni, che dopo un giorno normale; una strategia d'inerzia (nella direzione del giorno
anomalo) sembra profittevole ma non si distingue dal caso, una contraria non è profittevole (riassunto
della fonte, letto il 2026-10-09 sulla pagina dell'editore).

**Affermazione verificabile.** Dopo un giorno con rendimento di LTCUSDT anomalo verso l'alto (oltre la
media più 1,5 deviazioni standard dei 30 giorni precedenti), il giorno dopo un long rende più di un
long preso a caso con la stessa uscita; specchio per i giorni anomali verso il basso.

**Sotto-domande.** Il giorno anomalo nasce da una notizia (continua) o da liquidazioni (si inverte)?
La fonte trova che l'inerzia non batte il caso: mi aspetto quindi poco; lo provo perché la fonte
include proprio LTC (fino al 2018) e la dimensione del movimento successivo è maggiore.

**Spiegazioni concorrenti specifiche:**

| # | Spiegazione | Cosa prevede | Cosa la smentisce |
|---|---|---|---|
| S1 | Il giorno dopo è solo più volatile, non orientato | R vicino a zero con dispersione alta | R positivo netto |
| S2 | Costi e stop rendono negativo ciò che è positivo lordo | R lordo positivo, netto no | R netto positivo |
| S3 | La fonte ha già detto che non batte il caso: risultato atteso nullo | t contro la (b) vicino a 0 | t oltre la soglia |

Spiegazioni concorrenti per questa idea: 13.

**Ipotesi completa.** LTCUSDT, inerzia dopo un giorno anomalo, candele 1d, posizione di un giorno.

**Varianti:**

* **LTCUSDT-018** — 1d, long. Rendimento del giorno r[i] = close[i]/close[i−1] − 1; media m e deviazione
  standard s dei rendimenti dei 30 giorni precedenti (i−30 … i−1). Ingresso se r[i] > m + 1,5 s.
  Uscita dopo 1 barra. Stop 6% sotto il close di segnale.
  *Se `conta_trade` dà meno di 70 trade* (scarto), la sostituisce **LTCUSDT-018b**: soglia m + 1,0 s,
  scritta ora.
* **LTCUSDT-019** — 1d, short. Specchio: r[i] < m − 1,5 s; uscita dopo 1 barra; stop 6% sopra.
  *Se scarto*, la sostituisce **LTCUSDT-019b**: soglia m − 1,0 s, scritta ora.

**Previsioni.** Costi 0,023 R. Profit factor fra 0,8 e 1,3, R medio fra −0,1 e +0,1; nessuna batte
nettamente la (b) (la fonte stessa non trova differenze dal caso).
