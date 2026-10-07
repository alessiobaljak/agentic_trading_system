# Ipotesi della campagna BTCUSDT

Ogni idea e' scritta qui PRIMA di qualunque test (Fase 1 del Passo 3). Le fonti sono tutte
pubblicate prima del 2024-01-01. Le previsioni sono scritte prima di vedere i risultati; se
sbagliate, lo dice il log. Le regole del motore, della dimensione e i costi sono quelli congelati
in `research/config/` (commissione 0,05% per lato, slippage 0,01% per lato, rischio 1% per trade,
leva massima 2, margine isolato, stop prima del target nella stessa barra).

Convenzioni di tutte le idee:
* «R» = guadagno netto diviso il rischio iniziale del trade; «PF» = profit factor dopo costi.
* Lo stop e' sempre a un multiplo dell'ATR di Wilder a 14 barre del timeframe, misurato sul close
  della barra del segnale; l'ingresso e' all'apertura della barra dopo (regola del motore).
* «Uscita a N barre» = la strategia chiede «chiudi» alla chiusura della N-esima barra con posizione
  aperta e il motore esegue all'apertura della barra successiva.
* Le direzioni long e short sono varianti separate e si giudicano separate.
* Stima dei trade: conteggio dei segnali in costruzione, NON sovrapposti, con un'occupazione
  dichiarata (barre per trade): e' un limite inferiore, perche' uno stop anticipato libera prima.

## Spiegazioni concorrenti comuni a tutte le idee (le «noiose»)

Valgono per ogni idea; ogni idea aggiunge le sue. Per ciascuna: cosa prevede e cosa la smentisce.

| # | Spiegazione | Cosa prevede | Cosa la smentirebbe |
|---|---|---|---|
| C1 | **Caso.** L'effetto e' rumore campionario | R medio del candidato dentro la distribuzione delle entrate casuali con la stessa uscita; differenza non netta (sotto 2 errori standard) | R medio sopra il 90° percentile delle entrate casuali e differenza netta dalla simulazione mediana |
| C2 | **E' solo il mercato** (buy and hold di BTC, trend di fondo del periodo) | I trade long rendono perche' BTC e' salito: l'R medio dei long non batte l'entrata casuale long con la stessa uscita; gli short perdono | Vantaggio presente anche rispetto alle entrate casuali con la stessa direzione, e nei singoli anni (2020, 2021, 2022), non solo nel totale |
| C3 | **Volatilita'.** Il segnale seleziona solo barre volatili: il rischio sale, non il vantaggio | Vinte e perse piu' grandi, R medio vicino a zero, PF vicino a 1 | R medio positivo dopo aver normalizzato per lo stop in ATR (gia' fatto: R e' per unita' di rischio) e sopra il caso |
| C4 | **Artefatto dei dati** (barre aggregate, buchi del mark, lookahead involontario) | Il risultato crolla col ritardo di una barra; cambia con la regola intra-barra opposta; dipende da pochi trade | Peggioramento graduale col ritardo; stabilita' con la regola opposta; vantaggio non concentrato in pochi trade estremi |
| C5 | **Effetto costi.** Il vantaggio lordo esiste ma e' piu' piccolo dei costi | PF sopra 1 prima dei costi e sotto 1 dopo; crolla a costi doppi | PF sopra 1,10 anche a costi doppi |
| C6 | **Dipendenza da un solo regime** (2020-21 rialzo, 2022 ribasso) | R medio positivo in un anno solo e negativo negli altri | R medio positivo in almeno due anni su tre di costruzione |

---

## I-01 — Rottura del canale di prezzo (trading range breakout)

**Fonte.** Gerritsen, Bouri, Ramezanifar, Roubaud, «The profitability of technical trading rules in
the Bitcoin market», Finance Research Letters 34, 2020 (trovano che le regole di rottura
dell'intervallo di prezzo battono il buy and hold su BTC, a differenza degli incroci di medie);
Brock, Lakonishok, LeBaron, «Simple Technical Trading Rules and the Stochastic Properties of Stock
Returns», Journal of Finance 47(5), 1992 (definizione della regola di rottura).

**Affermazione verificabile.** Dopo che il close supera il massimo delle N barre precedenti, il
prezzo continua nella stessa direzione abbastanza da pagare i costi: l'R medio dei long aperti
alla barra dopo la rottura e' positivo e nettamente superiore a quello delle entrate casuali con la
stessa uscita. Simmetrico per gli short sotto il minimo. Falsificata se l'R medio non e' positivo o
non batte le entrate casuali.

**Sotto-domande.** Vale piu' con un'ampiezza di canale lunga (trend) o corta (rumore)? Chi opera:
seguaci del trend e stop di chi era contro, che spingono nella stessa direzione per qualche giorno.
Quando: nelle ore e nei giorni subito dopo la rottura; l'effetto dovrebbe esaurirsi in pochi giorni.
Vale nei rialzi e nei ribassi? Dipende dalla volatilita' al momento della rottura?

**Spiegazioni concorrenti specifiche** (oltre C1-C6):
| # | Spiegazione | Prevede | Smentita da |
|---|---|---|---|
| S1 | Le rotture sono false piu' spesso di quanto siano vere (stop hunting) | Molti stop subito dopo l'ingresso, R medio negativo, win rate sotto 40% | win rate e R medio positivi |
| S2 | L'effetto e' tutto nei primi mesi del 2021 (un solo trend) | R positivo solo nel 2021 | R positivo in piu' anni |
| S3 | Il vantaggio dipende dalla lunghezza esatta del canale | Cambiando N di poco il risultato cambia di segno | area stabile intorno a N |
| S4 | E' la volatilita' dopo la rottura, non la direzione | baseline (a) con la stessa uscita su ogni barra da' lo stesso R | il candidato batte la baseline (a) |

**Ipotesi completa.** BTCUSDT; meccanismo: continuazione dopo la rottura del canale; timeframe
**4h** (motivo: le regole della fonte sono giornaliere con finestre di 50-200 giorni, che su 2,8 anni
di costruzione danno pochi trade; a 4 ore un canale di 30 barre copre 5 giorni, lo stesso ordine
di grandezza «di qualche giorno» del meccanismo, con molti piu' segnali); ingresso long se il close
supera il massimo delle 30 barre precedenti, short se scende sotto il minimo; stop 2 ATR(14);
uscita quando il close torna oltre il canale opposto a 15 barre (per un long: close sotto il minimo
delle 15 barre precedenti) oppure a 60 barre (10 giorni) al massimo. Direzioni separate.
Verifiche: timeframe adiacenti 2h e 8h; canali 20 e 40 barre (robustezza).

**Previsione.** Long: PF fra 0,95 e 1,20, R medio fra 0 e +0,10, ~120-180 trade; non batte
nettamente le entrate casuali long (il rialzo 2020-21 aiuta entrambi). Short: PF fra 0,80 e 1,00.
Esito piu' probabile: nessun candidato.

---

## I-02 — Momentum di serie temporale a una settimana

**Fonte.** Moskowitz, Ooi, Pedersen, «Time Series Momentum», Journal of Financial Economics 104(2),
2012 (il segno del rendimento passato predice il rendimento futuro, su molti mercati); Liu,
Tsyvinski, «Risks and Returns of Cryptocurrency», Review of Financial Studies 34(6), 2021 (per
Bitcoin il rendimento a una settimana predice positivamente il rendimento della settimana dopo).

**Affermazione verificabile.** Se il rendimento degli ultimi 7 giorni e' positivo, il rendimento
dei 7 giorni seguenti e' in media positivo e superiore a quello incondizionato; se negativo,
negativo. Falsificata se l'R medio dei long (short) aperti su questo segnale non e' positivo o non
batte le entrate casuali con la stessa uscita.

**Sotto-domande.** L'effetto e' piu' forte dopo rendimenti grandi (soglia) o basta il segno?
Chi opera: chi arriva in ritardo sulle notizie e chi insegue il trend (diffusione lenta, herding);
sul lato opposto, chi vende per limitare le perdite. Quando: entro una o due settimane. Vale
quando il mercato scende (2022)?

**Spiegazioni concorrenti specifiche**:
| # | Spiegazione | Prevede | Smentita da |
|---|---|---|---|
| S1 | E' il trend 2020-21: «positivo» era quasi sempre vero | i long rendono quanto l'entrata casuale long; gli short perdono | long sopra il caso, short non peggiori del caso short |
| S2 | L'autocorrelazione settimanale e' negativa a questa scala (reversal), non positiva | R medio negativo per entrambe le direzioni | R positivo |
| S3 | L'effetto esiste solo nei primi 1-2 giorni della settimana seguente | uscita a 7 barre diluisce; uscita a 2 barre renderebbe di piu' (da verificare solo come robustezza, non per scegliere) | R stabile fra 5 e 10 barre |
| S4 | Dipende dal giorno in cui si calcola (effetto calendario) | il risultato cambia molto spostando la finestra di un giorno | stabile |

**Ipotesi completa.** BTCUSDT; meccanismo: continuazione del rendimento settimanale; timeframe
**1d** (il meccanismo e' settimanale: la candela giornaliera e' la piu' lunga ammessa e quella della
fonte); long se close/close di 7 barre prima − 1 > 0 alla chiusura di una barra in cui non si e'
in posizione; stop 2 ATR(14); uscita a 7 barre. Short simmetrico con rendimento < 0. Direzioni
separate. Verifiche: timeframe adiacente 12h (con 14 barre); finestre 5 e 10 giorni (robustezza).

**Previsione.** Long: PF 1,00-1,25, ~110-130 trade, R medio 0 / +0,15, non nettamente sopra il
caso long. Short: PF 0,85-1,05. Esito piu' probabile: nessun candidato; il long potrebbe passare le
baseline solo grazie al 2020-21 e cadere sulla stabilita' per anno.

---

## I-03 — Momentum intragiornaliero (prima mezz'ora → ultima mezz'ora)

**Fonte.** Shen, Urquhart, Wang, «Bitcoin intraday time series momentum», Financial Review 57(2),
2022 (il rendimento della prima mezz'ora del giorno predice quello dell'ultima mezz'ora).
Gao, Han, Li, Zhou, «Intraday momentum», Journal of Financial Economics 129(2), 2018 (lo stesso
effetto sull'indice azionario, origine dell'idea).

**Affermazione verificabile.** Il segno del rendimento 00:00-00:30 UTC predice il segno del
rendimento 23:30-24:00 UTC dello stesso giorno: un trade aperto alle 23:30 nella direzione della
prima mezz'ora ha R medio positivo e batte le entrate casuali con la stessa uscita (1 barra).
Falsificata se dopo i costi l'R medio non e' positivo.

**Sotto-domande.** Per BTC, che non ha apertura e chiusura, il «giorno» e' quello UTC, in cui cadono
settlement del funding (00:00) e le chiusure giornaliere degli exchange: chi ribilancia a fine
giornata (fondi, market maker che chiudono l'inventario) spinge nella direzione del mattino. Vale
solo con una prima mezz'ora grande (soglia)? Vale nei giorni feriali e nei fine settimana?

**Spiegazioni concorrenti specifiche**:
| # | Spiegazione | Prevede | Smentita da |
|---|---|---|---|
| S1 | Costi: il movimento di mezz'ora (~0,3-0,5%) e' dell'ordine del costo di andata e ritorno (0,12%) | PF sopra 1 lordo, sotto 1 netto | PF sopra 1,10 netto |
| S2 | E' un effetto di una fase sola (2020-21) | R positivo in un anno solo | R positivo in piu' anni |
| S3 | Il giorno UTC non e' il giorno giusto (la fonte potrebbe usare un altro fuso) | nessun effetto a UTC | effetto a UTC |
| S4 | Lo stop a 2 ATR su 30 minuti scatta spesso e rovina un effetto medio piccolo | molti stop | pochi stop e R positivo |

**Ipotesi completa.** BTCUSDT; meccanismo: ribilanciamento di fine giornata nella direzione
dell'apertura; timeframe **30m** (e' la scala dell'effetto nella fonte); alla chiusura della barra
delle 23:00 (cioe' alle 23:30), se il rendimento della barra 00:00-00:30 dello stesso giorno UTC
e' > 0 long, se < 0 short; ingresso all'apertura della barra 23:30, stop 2 ATR(14), uscita a 1
barra (apertura delle 00:00). Una sola variante con le due direzioni separate nel giudizio.
Verifica: soglia |rendimento| > 0,3% (robustezza), timeframe adiacente 15m (prima e ultima
mezz'ora costruite con due barre).

**Previsione.** ~1.000 trade, PF fra 0,85 e 1,00 dopo i costi, R medio negativo. Esito piu'
probabile: effetto lordo piccolo o nullo, mangiato dai costi. Se l'R lordo (senza costi) fosse
nettamente positivo, sarebbe comunque un'informazione per lezioni_moneta.

---

## I-04 — Funding estremo come segnale di posizionamento affollato

**Fonte.** Schmeling, Schrimpf, Todorov, «Crypto Carry», BIS Working Papers n. 1087, aprile 2023
(il carry dei perpetui, cioe' il funding, e' alto quando la domanda di leva lunga e' alta, e
periodi di carry alto precedono rendimenti bassi e crolli); He, Manela, Ross, von Wachter,
«Fundamentals of Perpetual Futures», arXiv 2212.06888, dicembre 2022 (il funding ancora il perpetuo
allo spot: funding alto = perpetuo a premio = domanda netta di long).

**Affermazione verificabile.** Quando l'ultimo funding settlement e' nel decile piu' alto dei 90
giorni precedenti (270 settlement), uno short aperto al settlement seguente e tenuto per 3
settlement (24 ore) ha R medio positivo (prezzo + funding incassato) e batte le entrate casuali
short con la stessa uscita. Simmetrico: funding nel decile piu' basso → long. Falsificata se l'R
medio non e' positivo o non batte il caso.

**Sotto-domande.** Chi paga il funding alto: long a leva affollati; chi incassa: arbitraggisti
(cash and carry) che vendono il perpetuo; quando il premio e' estremo, lo sbilancio tende a
rientrare per liquidazioni dei long o per l'arbitraggio. Quanto dura: ore-giorni. Vale quando il
funding e' alto per settimane (2021) o solo nei picchi?

**Spiegazioni concorrenti specifiche**:
| # | Spiegazione | Prevede | Smentita da |
|---|---|---|---|
| S1 | Funding alto = trend forte in corso: lo short perde sul prezzo piu' di quanto incassa | R medio negativo per gli short, stop frequenti | R positivo |
| S2 | E' solo il funding incassato (carry), non il prezzo | R positivo ma piccolo; senza funding R ≈ 0 | R positivo anche sul solo prezzo (si dichiara la scomposizione) |
| S3 | Decile su 90 giorni = quasi sempre nel 2021 (regime) | trade concentrati in un anno | trade e R distribuiti su piu' anni |
| S4 | Il funding al settlement T e' noto solo a T: usarlo per entrare a T e' lookahead | il test del ritardo (ingresso a T+8h) azzera l'effetto | peggioramento graduale (qui l'ingresso usa il settlement PRECEDENTE, gia' noto da 8 ore) |

**Ipotesi completa.** BTCUSDT; meccanismo: rientro di un posizionamento affollato segnalato dal
funding; timeframe **8h** (l'intervallo del funding); segnale alla chiusura della barra 8h se
l'ultimo settlement avvenuto entro quella chiusura e' sopra il 90° percentile dei 270 settlement
precedenti → short; sotto il 10° percentile → long; stop 2 ATR(14 barre 8h); uscita a 3 barre.
Direzioni separate. Verifiche: soglie 85°/95° (robustezza), timeframe adiacenti 4h e 12h (con il
settlement letto dalla barra), costi doppi.

**Previsione.** Short: 80-150 trade, PF 0,90-1,15, R medio -0,05 / +0,10, con il funding incassato
che vale circa 0,03-0,05 R per trade. Long: meno trade (funding negativo e' raro), 40-90, forse
sotto il minimo. Esito piu' probabile: nessun candidato; se qualcosa regge, e' lo short.

---

## I-05 — Effetto giorno della settimana (lunedi')

**Fonte.** Aharon, Qadan, «Bitcoin and the day-of-the-week effect», Economic Modelling 82, 2019
(rendimenti e volatilita' di Bitcoin piu' alti il lunedi'); Baur, Cahill, Godfrey, Liu, «Bitcoin
time-of-day, day-of-week and month-of-year effects in returns and trading volume», Finance
Research Letters 31, 2019; Kaiser, «Seasonality in cryptocurrencies», Finance Research Letters 31,
2019.

**Affermazione verificabile.** Il rendimento del lunedi' (00:00-24:00 UTC) e' in media positivo e
superiore a quello di un giorno qualsiasi: un long aperto all'apertura del lunedi' e chiuso
all'apertura del martedi' ha R medio positivo e batte le entrate casuali long a 1 barra.
Falsificata se non e' positivo o non batte il caso.

**Sotto-domande.** Chi opera il lunedi': i mercati tradizionali riaprono (flussi istituzionali,
notizie accumulate nel fine settimana), gli exchange crypto hanno volume maggiore. Vale in UTC o
in un fuso americano? E' cambiato nel tempo (effetti di calendario svaniscono quando sono noti)?

**Spiegazioni concorrenti specifiche**:
| # | Spiegazione | Prevede | Smentita da |
|---|---|---|---|
| S1 | E' il trend: ogni giorno del 2020-21 rende in media positivo | lunedi' ≈ giorno medio; non batte il caso long | lunedi' batte il caso long |
| S2 | Pochi lunedi' estremi fanno la media | R mediano ≈ 0, media trainata da 3-5 trade | R mediano positivo |
| S3 | L'effetto era nel campione della fonte (2013-2018) e non c'e' piu' | R ≈ 0 in tutti gli anni | R positivo |
| S4 | Il fuso: l'effetto e' sul lunedi' americano (dalle 13:30 UTC) | nessun effetto a UTC | effetto a UTC |

**Ipotesi completa.** BTCUSDT; meccanismo: flussi di inizio settimana; timeframe **1d**; alla
chiusura della barra della domenica → long; stop 2 ATR(14); uscita a 1 barra (apertura del
martedi'). Una variante, solo long (la fonte non da' un giorno negativo abbastanza netto per uno
short motivato). Verifiche: 12h (lunedi' in due barre), costi doppi.

**Previsione.** ~145 trade, PF 0,90-1,20, R medio -0,05 / +0,10, non netto rispetto al caso.
Esito piu' probabile: nessun candidato.

---

## I-06 — Continuazione dopo un giorno anomalo

**Fonte.** Caporale, Plastun, «Price overreactions in the cryptocurrency market», Journal of
Economic Studies 46(5), 2019 (dopo un giorno di movimento anomalo, il giorno seguente il prezzo
tende a muoversi nella STESSA direzione, momentum e non contrarian, nelle crypto).

**Affermazione verificabile.** Dopo un giorno con |rendimento| sopra media + 1 deviazione standard
dei 30 giorni precedenti, il rendimento del giorno seguente ha lo stesso segno in media: un trade
nella direzione del giorno anomalo, tenuto 1 giorno, ha R medio positivo e batte le entrate
casuali. Falsificata se non e' positivo o non batte il caso.

**Sotto-domande.** Chi opera: chi reagisce in ritardo alla notizia che ha causato il giorno anomalo,
e le liquidazioni a catena (un giorno anomalo in giu' liquida long, che spingono ancora giu').
Vale piu' in giu' (liquidazioni) che in su? Dipende dalla soglia?

**Spiegazioni concorrenti specifiche**:
| # | Spiegazione | Prevede | Smentita da |
|---|---|---|---|
| S1 | Dopo un giorno anomalo c'e' solo piu' volatilita', non direzione | baseline (a) sulle stesse barre da' lo stesso R; R ≈ 0 | R positivo e sopra (a) |
| S2 | L'effetto e' asimmetrico (solo in giu', per le liquidazioni) | short positivi, long no | entrambi positivi |
| S3 | La soglia a 1 deviazione standard e' troppo bassa: include giorni normali | nessun effetto; con 2 deviazioni standard (pochi trade, non giudicabile) forse si | effetto gia' a 1 deviazione |
| S4 | Lo stop a 2 ATR dopo un giorno anomalo (ATR gonfiato) e' lontano e il rischio per trade in prezzo e' grande: R piccolo per costruzione | R medio piccolo in valore assoluto | R medio sopra 0,05 |

**Ipotesi completa.** BTCUSDT; meccanismo: continuazione dopo un movimento anomalo; timeframe
**1d** (scala della fonte); alla chiusura di un giorno con |close/close precedente − 1| > media +
1 deviazione standard dei |rendimenti| dei 30 giorni precedenti → trade nella direzione del giorno;
stop 2 ATR(14); uscita a 1 barra. Direzioni separate. Verifiche: soglia 1,5 deviazioni, 12h, costi
doppi.

**Previsione.** Long 60-90 trade (forse sotto il minimo e scartato dalla stima), short 50-80
(idem). PF 0,9-1,1. Esito piu' probabile: scarto per pochi trade o nessun candidato.

---

## Idee scartate senza consumare budget

| Id | Idea | Motivo dello scarto |
|---|---|---|
| S-01 | Deriva del prezzo nelle ore intorno al settlement del funding (i long vendono prima di pagare) | nessuna fonte pubblicata prima del 2024 con titolo, autore e data che io possa citare con certezza: senza fonte l'idea non entra |
| S-02 | Ciclo del dimezzamento (halving) e stagionalita' pluriennale | il meccanismo richiede candele oltre 1 giorno e cicli di anni: fuori dai timeframe ammessi (regola 10) |
| S-03 | Qualunque idea basata su cosa e' successo dal 2024 in poi (flussi di strumenti nuovi, eventi) | regola 8: niente conoscenza del vault |
