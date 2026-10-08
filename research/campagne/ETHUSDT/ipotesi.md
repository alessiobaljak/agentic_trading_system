# ETHUSDT — Ipotesi (Fase 1)

Scritto l'8 ottobre 2026, PRIMA di qualunque conteggio o test delle idee qui sotto. Ogni
idea ha la sua fonte, pubblicata prima del 2024-01-01 (verificata il giorno stesso su
pagine di editori, archivi universitari e banche centrali). Nessuna idea viene dal gate,
dal registro delle strategie, dal paper del bot o da altre monete. Le varianti di ogni
idea sono tutte qui, ognuna con il suo motivo, prima del primo test di quell'idea
(regola 6). Al massimo due varianti per fonte (`lezioni/metodo.md`).

Regola 8: nessuna di queste idee e' scelta perche' si sa che ha funzionato dopo il 2023.
Chi scrive (un modello) ha una conoscenza generale dei mercati crypto fino al 2026; le idee
vengono dalla letteratura citata e le famiglie di meccanismo sono scelte per essere
diverse fra loro, non per come sono andate.

## Convenzioni comuni a tutte le varianti

* Segnale alla chiusura di una barra (solo barre chiuse), ingresso all'apertura della
  barra dopo, una posizione alla volta (motore della sezione 7).
* "Stop a k ATR, al massimo 6%": distanza dello stop = min(k x ATR(14), 6% della chiusura
  del segnale), dalla chiusura del segnale. Il 6% e' il tetto di stop del bot
  (`stop_massimo_bot`): con il tetto la variante resta eseguibile dal bot.
* "Stop al 6%" (timeframe di 1 giorno): distanza fissa del 6%. Su ETH nel periodo di
  costruzione l'ATR(14) giornaliero mediano e' il 6,96% (`codice/costi_in_r.py`): uno stop
  in ATR supererebbe sempre il tetto del bot.
* "Esce dopo N barre": "chiudi" alla chiusura della N-esima barra in posizione (la barra
  d'ingresso conta 1), cioe' uscita all'apertura della barra N+1.
* Le uscite per stop e target le fa il motore (stop prima del target nella stessa barra).
* Giorno = giorno UTC (le candele giornaliere di Binance).
* Costo di un giro (commissioni e slippage, andata e ritorno) = 0,12% del nozionale. In
  R, con lo stop a 2 ATR(14): 15m 0,097; 30m 0,067; 1h 0,047; 2h 0,032; 4h 0,022;
  8h 0,015 (piu' il funding). Con lo stop al 6%: 0,020 R. Le previsioni sono al netto.
* "Nettamente" e le baseline sono quelle della sezione 8 (`codice/comune.py`, `valuta`).
* Con circa 70-150 trade e R per trade con deviazione standard intorno a 1, l'errore
  dell'R medio e' circa 0,08-0,15 R: battere nettamente la (b) chiede un vantaggio di
  circa 0,2-0,3 R per trade. Per questo la previsione di quasi tutte le varianti e' «non
  batte nettamente la (b)».

Le spiegazioni concorrenti «noiose» compaiono in ogni idea (caso, volatilita', trend di
fondo, artefatto dei dati, costi, «e' solo il mercato»), adattate all'idea.

---

## I-01 — Momentum sul prezzo della settimana passata (time-series momentum)

**Fonte.** Yukun Liu e Aleh Tsyvinski, «Risks and Returns of Cryptocurrency», The Review of
Financial Studies 34(6), 2021, pp. 2689-2727 (prima versione: NBER Working Paper 24877,
agosto 2018). Trovano un forte momentum nel tempo: i rendimenti delle settimane passate
prevedono quelli della settimana dopo, per Bitcoin, Ripple ed Ethereum (piu' debole per
Ethereum). Spiegazione proposta: l'attenzione degli investitori (un rialzo attira
domanda). Base generale: Moskowitz, Ooi e Pedersen, «Time series momentum», Journal of
Financial Economics 104(2), 2012.

**Affermazione falsificabile.** Su ETHUSDT, dopo una settimana (7 giorni UTC) con
rendimento positivo, la settimana successiva ha un R medio piu' alto di quello di una
settimana presa a caso con la stessa uscita (baseline (b)); simmetricamente per le
settimane negative e lo short.

**Sotto-domande.** Vale in ogni regime o solo nei rialzi forti (2020-2021)? Dipende dalla
dimensione del rendimento passato? Chi compra dopo un rialzo: piccoli investitori che
arrivano tardi, attirati dai prezzi e dalle notizie; chi vende dopo un ribasso: chi chiude
leva e chi segue il trend. Quando: l'effetto e' su un orizzonte di 1-4 settimane.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Caso | R medio vicino alla (b), t sotto 1 | t contro la (b) oltre 2 e stabile negli anni |
| 2 | Trend di fondo: nel 2020-2021 ETH sale molto, ogni long guadagna | la variante batte la (c) ma non la (b), che entra long a caso nello stesso periodo | t contro la (b) oltre la soglia |
| 3 | E' solo il mercato: ETH segue BTC, il momentum e' di tutto il mercato | stessi risultati con il segnale preso su BTC | il segnale su ETH aggiunge oltre quello su BTC (non si testa: e' contesto) |
| 4 | Volatilita': dopo settimane forti la volatilita' e' alta, e uno stop fisso al 6% scatta piu' spesso | molti stop, R medio negativo pur con il segno giusto | pochi stop nei trade che falliscono |
| 5 | Costi: 0,02 R a giro, piccoli; il funding positivo del 2020-2021 pesa sui long tenuti 7 giorni | long peggiorato di 0,01-0,03 R dal funding | funding totale trascurabile nei risultati |
| 6 | Artefatto dei dati: chiusure giornaliere UTC arbitrarie | lo stesso con altri orari di chiusura (non provato) | — |
| 7 | Pochi trade estremi (maggio 2021, crollo di marzo 2020) fanno la media | senza i 3 trade migliori l'R medio crolla | R medio senza i 3 migliori ancora sopra la (b) |
| 8 | Un solo anno favorevole | R medio alto in un anno, negativo negli altri | R medio sopra la (b) in piu' della meta' degli anni |
| 9 | Reversione di breve: dopo una settimana forte, i primi giorni ritracciano | R medio peggiore con orizzonte corto | — |
| 10 | Attenzione degli investitori (l'ipotesi) | R medio sopra la (b) in tutti gli anni | t contro la (b) sotto 1 |
| 11 | Effetto leva: i rialzi aumentano le posizioni a leva che spingono ancora | piu' forte quando il funding e' alto | nessuna differenza col funding |

**Ipotesi completa.** ETHUSDT, momentum di una settimana, timeframe 1d (il meccanismo e'
settimanale e le chiusure giornaliere lo misurano senza rumore intragiornaliero), una
direzione per variante.

**Varianti.**
* **I-01a** — 1d, long. Ingresso: chiusura / chiusura di 7 barre prima - 1 > 0. Uscita:
  dopo 7 barre. Stop al 6%. Nessun target. Motivo: il segno del rendimento passato come in
  Moskowitz et al., orizzonte di una settimana come in Liu e Tsyvinski.
  Previsione: R medio fra -0,05 e +0,20 dopo i costi; non batte nettamente la (b) (t fra
  -0,5 e 1,5): il trend del periodo lo prende anche la (b).
* **I-01b** — 1d, short. Ingresso: rendimento di 7 barre < 0. Uscita dopo 7 barre. Stop al
  6%. Motivo: la stessa ipotesi nell'altra direzione. Previsione: R medio fra -0,25 e
  +0,05; non batte nettamente la (b).

Criterio di successo (tutte le varianti di tutte le idee): batte nettamente la (a) e la
(b) con R medio dopo i costi positivo (sezione 8, Fase 2).

---

## I-02 — Rottura del canale di Donchian (le regole delle "tartarughe")

**Fonte.** Curtis M. Faith, «Way of the Turtle: The Secret Methods that Turned Ordinary
People into Legendary Traders», McGraw-Hill, 2007. Sistema 1: entrata sulla rottura del
massimo (minimo) delle ultime 20 barre, uscita sulla rottura opposta delle ultime 10,
stop a 2 N (N = ATR a 20 barre).

**Affermazione falsificabile.** Su ETHUSDT a 4 ore, quando la chiusura supera il massimo
delle 20 barre precedenti, i trade con uscita sul minimo di 10 barre e stop a 2 ATR hanno
un R medio piu' alto della stessa uscita con entrate casuali; simmetrico per lo short.

**Sotto-domande.** Le rotture funzionano meglio dopo periodi calmi o agitati? Chi compra
sulla rottura: chi segue il trend, gli stop dei venditori sopra i massimi recenti, chi
entra sulle notizie. Quanto dura: le tartarughe tenevano settimane; a 4 ore la durata
attesa e' di pochi giorni.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Caso | t contro la (b) sotto 1 | t oltre la soglia, stabile negli anni |
| 2 | Trend di fondo (rialzo 2020-2021, ribasso 2022) | long buono solo 2020-2021, short solo 2022, come la (b) | batte la (b) anche nell'anno contrario |
| 3 | E' solo il mercato: le rotture di ETH sono rotture di BTC | — (contesto) | — |
| 4 | Volatilita': le rotture avvengono quando la volatilita' sale, e i trade casuali con la stessa uscita lo prendono uguale | stesso R della (b) | — |
| 5 | Costi: 0,02 R a giro con stop a 2 ATR; falsi segnali molti e piccoli | perdite piccole e frequenti | — |
| 6 | Artefatto: barre a 4 ore allineate a UTC | (non provato) | — |
| 7 | Pochi trade estremi (le grandi corse) fanno tutto | senza i 3 migliori la media crolla | R senza i 3 migliori sopra la (b) |
| 8 | Falsa rottura: la rottura richiama chi prende profitto e il prezzo torna indietro | R medio negativo, molti stop | — |
| 9 | Stop a cascata sopra i massimi (la variante cattura l'accelerazione) | vantaggio nei primi giorni, poi niente | — |
| 10 | Seguire il trend paga perche' i prezzi si aggiustano lentamente (l'ipotesi) | R sopra la (b) in piu' anni | t sotto 1 |
| 11 | Il tetto del 6% sullo stop taglia i trade piu' volatili e cambia la distribuzione | — | — |

**Ipotesi completa.** ETHUSDT, rottura di canale, 4h. Il sistema originale e'
giornaliero; a 1 giorno lo stop a 2 N sarebbe circa il 14% (fuori dal tetto del bot) e le
rotture sarebbero poche. A 4 ore le stesse regole in barre guardano 3-4 giorni e lo stop a
2 ATR resta sotto il 6% nel 63% delle barre (`codice/costi_in_r.py`).

**Varianti.**
* **I-02a** — 4h, long. Ingresso: chiusura > massimo dei massimi delle 20 barre precedenti
  (esclusa quella corrente). Uscita: chiusura < minimo dei minimi delle 10 barre
  precedenti. Stop a 2 ATR(20), al massimo 6%. Motivo: il Sistema 1 com'e' scritto, in
  barre. Previsione: R medio fra -0,05 e +0,15; non batte nettamente la (b).
* **I-02b** — 4h, short, specchio. Previsione: R medio fra -0,15 e +0,10; non batte
  nettamente la (b).

---

## I-03 — Prezzo sopra o sotto la media mobile di 50 giorni

**Fonte.** William Brock, Josef Lakonishok e Blake LeBaron, «Simple Technical Trading
Rules and the Stochastic Properties of Stock Returns», The Journal of Finance 47(5),
1992, pp. 1731-1764. La regola a media mobile di lunghezza variabile (1, 50): long quando
il prezzo sta sopra la media di 50 giorni, fuori (o short) quando sta sotto; i rendimenti
nei giorni "buy" erano piu' alti di quelli nei giorni "sell".

**Affermazione falsificabile.** Su ETHUSDT i periodi con chiusura sopra la media semplice
di 50 giorni hanno, per trade, un R medio piu' alto di trade casuali con la stessa uscita
(uscita quando la chiusura torna sotto la media); simmetrico per lo short.

**Sotto-domande.** L'effetto viene dalle prime barre dopo l'incrocio o da tutto il periodo
sopra la media? Chi agisce: chi segue il trend con regole simili (molto diffuse), fondi
che entrano quando il trend e' confermato. Orizzonte: settimane.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Caso | t contro la (b) sotto 1 | t oltre la soglia |
| 2 | Trend di fondo: sopra la media nei rialzi | stesso R della (b) long | batte la (b) |
| 3 | E' solo il mercato (BTC) | — (contesto) | — |
| 4 | Volatilita': i trade sopra la media hanno volatilita' diversa | — | — |
| 5 | Costi: piccoli a 1d (0,02 R), ma molti falsi incroci | perdite frequenti piccole | — |
| 6 | Artefatto della chiusura UTC | (non provato) | — |
| 7 | Pochi trade lunghi (2020-2021) fanno tutto | senza i 3 migliori crolla | R senza i 3 migliori sopra la (b) |
| 8 | Un solo anno | R alto nel 2020 o 2021, negativo nel 2022 | sopra la (b) in piu' anni |
| 9 | Lo stop al 6% (sotto 1 ATR giornaliero) chiude quasi tutti i trade per stop prima che il trend si sviluppi | molti stop, R vicino a -1 per molti trade | pochi stop |
| 10 | Aggiustamento lento all'informazione (l'ipotesi) | R sopra la (b) | t sotto 1 |
| 11 | Profezia che si autoavvera (tutti guardano la media di 50) | effetto concentrato vicino all'incrocio | — |

**Ipotesi completa.** ETHUSDT, media mobile di 50 giorni, 1d (la regola e' giornaliera
nella fonte).

**Varianti.**
* **I-03a** — 1d, long. Ingresso: chiusura > media semplice delle ultime 50 chiusure
  (compresa la corrente). Uscita: chiusura < la stessa media. Stop al 6%. Se lo stop
  scatta e la chiusura resta sopra la media, si rientra (come la regola originale, che e'
  long finche' il prezzo sta sopra). Previsione: R medio fra -0,10 e +0,30; non batte
  nettamente la (b).
* **I-03b** — 1d, short, specchio (chiusura < media; uscita chiusura > media). Previsione:
  R medio fra -0,30 e +0,10; non batte nettamente la (b).

---

## I-04 — RSI a 2 barre: eccesso di breve contro il trend lungo

**Fonte.** Larry Connors e Cesar Alvarez, «Short Term Trading Strategies That Work»,
TradingMarkets Publishing, 2009. Regola: sopra la media di 200 barre, comprare quando
l'RSI a 2 periodi scende sotto 10 (eccesso di vendita di breve), uscire quando la
chiusura torna sopra la media di 5; sotto la media di 200, lo specchio short. Senza stop
nella regola originale.

**Affermazione falsificabile.** Su ETHUSDT a 4 ore, dentro un trend lungo rialzista
(chiusura sopra la media di 200 barre), dopo un RSI(2) sotto 10 il prezzo rimbalza: l'R
medio dei trade e' piu' alto di trade casuali con la stessa uscita; simmetrico per lo
short.

**Sotto-domande.** Il rimbalzo dipende da quanto e' profondo l'eccesso? E' piu' forte
dopo cadute con volume alto (vendite forzate)? Chi fornisce liquidita': chi compra le
cadute (market maker, chi accumula), contro chi vende per paura o per chiusura di leva.
Tempo: poche barre (ore, un giorno).

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Caso | t sotto 1 | t oltre la soglia |
| 2 | Trend di fondo: in un trend rialzista ogni acquisto guadagna | come la (b) long nel 2020-2021 | batte la (b) |
| 3 | E' solo il mercato: le cadute di ETH sono cadute di BTC che rimbalza | — (contesto) | — |
| 4 | Volatilita': gli eccessi capitano quando la volatilita' sale, lo stop a ATR si allarga | — | — |
| 5 | Costi: 0,015-0,03 R a giro a 4 ore; guadagni attesi piccoli | R medio vicino a zero | — |
| 6 | Artefatto: RSI su barre UTC di 4 ore | (non provato) | — |
| 7 | Pochi trade estremi (crollo di marzo 2020, maggio 2021) | senza i 3 migliori crolla | — |
| 8 | Lo stop (che la regola originale non ha) taglia i rimbalzi tardivi | molti stop prima del rimbalzo | pochi stop |
| 9 | Liquidita' fornita a pagamento (l'ipotesi): chi compra l'eccesso guadagna un premio | R sopra la (b) in piu' anni | t sotto 1 |
| 10 | Momentum di breve: in crypto le cadute continuano (l'opposto) | R medio negativo, sotto la (b) | — |
| 11 | Il filtro della media di 200 sceglie solo i periodi di rialzo, e la (a) senza filtro e' piu' debole | batte la (a) ma non la (b) | — |

**Ipotesi completa.** ETHUSDT, ritorno verso la media dopo un eccesso di breve, 4h. La
fonte usa barre giornaliere di azioni (sessioni di 6,5 ore); ETH scambia 24 ore su 24 e
gli eccessi di liquidita' si riassorbono in ore: la barra di 4 ore e' la scala del
meccanismo qui. A 1 giorno, con la media di 200 giorni che si scalda solo a meta' 2020,
le occasioni sarebbero poche.

**Varianti.**
* **I-04a** — 4h, long. Ingresso: chiusura > media semplice di 200 chiusure e RSI(2) <
  10. Uscita: chiusura > media semplice di 5 chiusure. Stop a 3 ATR(14), al massimo 6%
  (uno stop largo, perche' la regola originale non ne ha). Previsione: R medio fra -0,05 e
  +0,15; non batte nettamente la (b).
* **I-04b** — 4h, short. Ingresso: chiusura < media di 200 e RSI(2) > 90. Uscita: chiusura
  < media di 5. Stop a 3 ATR(14), al massimo 6%. Previsione: R medio fra -0,15 e +0,10;
  non batte nettamente la (b).

---

## I-05 — Barra piu' stretta delle ultime 7 (contrazione della volatilita')

**Fonte.** Toby Crabel, «Day Trading with Short Term Price Patterns and Opening Range
Breakout», Traders Press, 1990. La barra con l'escursione piu' stretta delle ultime 7
(NR7) annuncia un'espansione dell'escursione: si entra nella direzione in cui il prezzo
esce dalla barra stretta.

**Affermazione falsificabile.** Su ETHUSDT a 4 ore, dopo una barra NR7, una chiusura oltre
il suo massimo porta a un movimento nella stessa direzione nel giorno dopo: R medio piu'
alto di trade casuali con la stessa uscita; simmetrico per lo short.

**Sotto-domande.** La contrazione e' piu' informativa se dura piu' barre? Dipende
dall'ora? Chi agisce: quando il mercato e' fermo si accumulano ordini condizionati sopra e
sotto (stop e ingressi su rottura); l'uscita li fa scattare. Tempo: ore, al massimo un
giorno.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Caso | t sotto 1 | t oltre la soglia |
| 2 | Trend di fondo | long buono nel 2020-2021 come la (b) | batte la (b) |
| 3 | E' solo il mercato | — (contesto) | — |
| 4 | Volatilita' che torna alla media: dopo una barra stretta l'escursione cresce, ma in direzione casuale | l'R della variante come la (b) | batte la (b) |
| 5 | Costi: lo stop sotto la barra stretta e' vicino, il costo in R e' alto (0,05-0,1 R) | R medio negativo per i costi | — |
| 6 | Artefatto: le barre di 4 ore spezzano le sessioni in modo arbitrario | (non provato) | — |
| 7 | Pochi trade estremi | senza i 3 migliori crolla | — |
| 8 | Stagionalita' oraria: le barre strette sono di notte (Asia), le rotture al mattino europeo | — | — |
| 9 | Ordini condizionati accumulati (l'ipotesi) | R sopra la (b) in piu' anni | t sotto 1 |
| 10 | Falsa rottura: la rottura di una barra stretta viene riassorbita | molti stop | — |

**Ipotesi completa.** ETHUSDT, rottura dopo contrazione, 4h (barre corte abbastanza da
avere molte contrazioni, lunghe abbastanza da non essere dominate dai costi).

**Varianti.**
* **I-05a** — 4h, long. Condizione: la barra precedente e' NR7 (la sua escursione
  massimo-minimo e' la piu' piccola delle 7 barre che finiscono con lei) e la barra
  corrente chiude sopra il massimo della barra NR7. Stop: il minimo della barra NR7, con
  distanza al massimo 6%. Uscita dopo 6 barre (un giorno). Previsione: R medio fra -0,10 e
  +0,10; non batte nettamente la (b).
* **I-05b** — 4h, short, specchio (chiusura sotto il minimo della barra NR7, stop sul suo
  massimo). Previsione: R medio fra -0,10 e +0,10; non batte nettamente la (b).

---

## I-06 — La prima mezz'ora del giorno prevede l'ultima

**Fonte.** Dehua Shen, Andrew Urquhart e Pengfei Wang, «Bitcoin intraday time-series
momentum», The Financial Review 57(2), 2022, pp. 319-344 (online il 26 ottobre 2021).
Su Bitcoin il rendimento della prima mezz'ora del giorno di scambio prevede quello
dell'ultima; l'effetto e' attribuito a chi fornisce liquidita'. Base: Gao, Han, Li e Zhou,
«Market intraday momentum», Journal of Financial Economics 129(2), 2018.

**Affermazione falsificabile.** Su ETHUSDT, se la mezz'ora 00:00-00:30 UTC sale, la
mezz'ora 23:30-24:00 UTC dello stesso giorno ha un R medio piu' alto di una mezz'ora
casuale con la stessa uscita; simmetrico per lo short.

**Sotto-domande.** Il giorno di scambio di una moneta che non chiude mai: la fonte lo
definisce con il volume; qui si usa il giorno UTC delle candele di Binance (scelta
dichiarata). Dipende dalla volatilita' del giorno? Chi agisce: chi ribilancia a fine
giornata nella direzione del giorno (copertura, fondi), chi fornisce liquidita' la mattina.
Tempo: una mezz'ora.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Caso | t sotto 1 | t oltre la soglia |
| 2 | Costi: 0,067 R a giro con stop a 2 ATR su 30 minuti, quanto il movimento tipico | R medio negativo intorno a -0,07 | R medio dopo costi positivo |
| 3 | Trend di fondo | — | — |
| 4 | E' solo il mercato (BTC) | — (contesto) | — |
| 5 | Volatilita': l'ultima mezz'ora ha volatilita' diversa dalle altre | R vicino a quello della (b) | — |
| 6 | Artefatto: il giorno UTC non e' il giorno di scambio della fonte | nessun effetto qui, anche se esiste altrove | — |
| 7 | Stagionalita' oraria pura (l'ultima mezz'ora sale sempre o scende sempre) | stesso R senza la condizione | batte la (a) e la (b) |
| 8 | Pochi giorni estremi | senza i 3 migliori crolla | — |
| 9 | Copertura e ribilanciamento di fine giornata (l'ipotesi) | R sopra la (b) | t sotto 1 |
| 10 | Il funding a 00:00 UTC: chi chiude prima del settlement muove l'ultima mezz'ora | effetto legato al segno del funding | — |

**Ipotesi completa.** ETHUSDT, momentum intragiornaliero, 30m (la mezz'ora e' l'unita'
della fonte).

**Varianti.**
* **I-06a** — 30m, long. Alla chiusura della barra 23:00-23:30 UTC, se la barra
  00:00-00:30 dello stesso giorno ha chiusura > apertura: long all'apertura delle 23:30.
  Uscita dopo 1 barra (alle 00:00). Stop a 2 ATR(14), al massimo 6%. Previsione: R medio
  fra -0,15 e 0,00 (i costi pesano quanto il movimento); non batte nettamente la (b).
* **I-06b** — 30m, short, specchio (prima mezz'ora con chiusura < apertura). Previsione:
  R medio fra -0,15 e 0,00; non batte nettamente la (b).

---

## I-07 — BTC si muove prima di ETH

**Fonte.** Andrew W. Lo e A. Craig MacKinlay, «When Are Contrarian Profits Due to Stock
Market Overreaction?», The Review of Financial Studies 3(2), 1990, pp. 175-205: i
rendimenti dei titoli grandi anticipano quelli dei piccoli (correlazione incrociata con
ritardo). Fonte contraria, tenuta come spiegazione concorrente: Azhar Mohamad, Imtiaz
Mohammad Sifat e Mohammad Syazwan Mohamed Shariff, «Lead-Lag relationship between
Bitcoin and Ethereum: Evidence from hourly and daily data», Research in International
Business and Finance 50, 2019, pp. 306-321 (relazione in entrambi i sensi, poco spazio
per guadagnare a breve).

**Affermazione falsificabile.** Su ETHUSDT a 1 ora, quando BTC sale di oltre l'1% in una
barra ed ETH sale meno della meta' di BTC, ETH recupera il ritardo nelle 2 barre dopo: R
medio piu' alto di trade casuali con la stessa uscita; simmetrico per le discese.

**Sotto-domande.** Quanto dura il ritardo: secondi (arbitraggio) o ore (investitori)? Vale
solo con volume alto? Chi agisce: chi tratta ETH guarda BTC come prezzo di riferimento;
fondi che comprano il "paniere" in ordine di grandezza. Tempo: entro 1-2 ore.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Caso | t sotto 1 | t oltre la soglia |
| 2 | Arbitraggio veloce: il ritardo si chiude in secondi, non in ore | nessun effetto a 1 ora | R sopra la (b) |
| 3 | Relazione in entrambi i sensi (Mohamad e altri): ETH a volte guida | effetto nullo in media | — |
| 4 | ETH che sale meno di BTC ha notizie proprie negative: il ritardo e' informazione | R negativo (ETH continua a restare indietro) | — |
| 5 | Volatilita': dopo una barra forte di BTC la volatilita' di ETH sale | stop piu' frequenti | — |
| 6 | Trend di fondo | — | — |
| 7 | Costi: 0,047 R a giro | R medio dopo costi vicino a zero | — |
| 8 | Artefatto: barre orarie di BTC ed ETH chiuse nello stesso istante, ma con prezzi dell'ultimo scambio di ogni contratto | (non provato) | — |
| 9 | Pochi eventi estremi | senza i 3 migliori crolla | — |
| 10 | Diffusione lenta dell'informazione dal grande al piccolo (l'ipotesi) | R sopra la (b) | t sotto 1 |

**Ipotesi completa.** ETHUSDT con BTCUSDT come riferimento, recupero del ritardo, 1h.

**Varianti.**
* **I-07a** — 1h, long. Condizione: nella barra appena chiusa BTC ha chiusura/apertura - 1
  > +1% ed ETH ha chiusura/apertura - 1 < meta' di quello di BTC. Uscita dopo 2 barre. Stop
  a 2 ATR(14), al massimo 6%. Previsione: R medio fra -0,10 e +0,10; non batte nettamente la
  (b).
* **I-07b** — 1h, short, specchio (BTC < -1%, ETH > meta' del rendimento di BTC).
  Previsione: R medio fra -0,10 e +0,10; non batte nettamente la (b).

---

## I-08 — Funding alto: la leva di chi insegue il rialzo

**Fonte.** Maik Schmeling, Andreas Schrimpf e Karamfil Todorov, «Crypto carry», BIS
Working Papers n. 1087, aprile 2023 (versione del 24 marzo 2023). La differenza fra futures
e spot (il "carry", che nei perpetui si paga con il funding) diventa a volte molto grande:
la spingono piccoli investitori che inseguono il trend e vogliono rialzo a leva, mentre il
capitale che fa arbitraggio e' limitato; insieme alla leva alta questo aiuta a spiegare i
crolli ricorrenti.

**Affermazione falsificabile.** Su ETHUSDT, dopo un settlement di funding oltre lo 0,05%
per 8 ore (cinque volte il tasso base dello 0,01%, circa il 55% l'anno), il prezzo nei 3
giorni seguenti ha un R medio, per uno short, piu' alto di uno short casuale con la stessa
uscita. Specchio: dopo un funding negativo (chi e' short paga), un long.

**Sotto-domande.** Conta il livello o la crescita del funding? Vale solo in fasi di
euforia? Chi agisce: i long a leva pagano il funding; quando il prezzo esita, le
liquidazioni li chiudono a catena. Tempo: giorni.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Caso | t sotto 1 | t oltre la soglia |
| 2 | Trend di fondo: il funding e' alto nei rialzi forti, che continuano | short in perdita, sotto la (b) | — |
| 3 | E' solo il mercato: il funding alto e' di tutto il mercato crypto | — (contesto) | — |
| 4 | Volatilita': funding alto in fasi volatili, stop piu' frequenti | molti stop | — |
| 5 | Costi: lo short incassa il funding alto (aiuta); 0,015 R di commissioni a giro | il funding migliora lo short di 0,02-0,05 R | — |
| 6 | Artefatto: il tasso di settlement e' quello del periodo appena finito, gia' noto al mercato | effetto gia' nel prezzo, nullo | — |
| 7 | Pochi crolli (maggio 2021, marzo 2020) fanno tutto | senza i 3 migliori crolla | — |
| 8 | Il funding misura la domanda di leva, non la sopravvalutazione (l'ipotesi e' sbagliata nel tempo breve) | nessun effetto in 3 giorni | — |
| 9 | Leva affollata che viene liquidata (l'ipotesi) | R sopra la (b), concentrato nei crolli | t sotto 1 |
| 10 | Funding negativo dopo i crolli: chi e' short e' gia' in guadagno e copre, il prezzo rimbalza | long dopo funding negativo sopra la (b) | — |

**Ipotesi completa.** ETHUSDT, leva affollata misurata dal funding, 8h (l'intervallo del
funding: ogni barra contiene un settlement).

**Varianti.**
* **I-08a** — 8h, short. Condizione: l'ultimo settlement gia' avvenuto alla chiusura della
  barra ha tasso >= 0,0005. Uscita dopo 9 barre (3 giorni). Stop a 2 ATR(14), al massimo
  6%. Previsione: R medio fra -0,20 e +0,15; non batte nettamente la (b).
* **I-08b** — 8h, long. Condizione: l'ultimo settlement ha tasso < 0. Uscita dopo 9 barre.
  Stop a 2 ATR(14), al massimo 6%. Motivo: lo stesso meccanismo dal lato opposto (chi e'
  short paga per esserlo). Previsione: R medio fra -0,15 e +0,15; non batte nettamente la
  (b).

---

## I-09 — Il lunedi'

**Fonte.** Guglielmo Maria Caporale e Alex Plastun, «The day of the week effect in the
cryptocurrency market», Finance Research Letters 31, 2019, pp. 258-269 (prima versione:
CESifo Working Paper 6716, ottobre 2017). Su Bitcoin i rendimenti del lunedi' sono
significativamente piu' alti degli altri giorni; Litecoin, Ripple e Dash non mostrano
l'effetto; le simulazioni di trading danno guadagni per lo piu' non distinguibili dal caso.

**Affermazione falsificabile.** Su ETHUSDT il lunedi' UTC ha un R medio, per un long di un
giorno, piu' alto di un giorno preso a caso con la stessa uscita.

**Sotto-domande.** ETH segue BTC: se l'effetto c'e' su BTC, passa a ETH? Viene dal ritorno
degli operatori istituzionali dopo il fine settimana? Tempo: un giorno.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Caso (la fonte stessa trova guadagni simili al caso) | t sotto 1 | t oltre la soglia |
| 2 | L'effetto e' di BTC, non di ETH (la fonte non lo trova sulle altre monete) | nessun effetto | — |
| 3 | Trend di fondo: ogni long di un giorno guadagna nel 2020-2021 | come la (b) | batte la (b) |
| 4 | E' solo il mercato | — (contesto) | — |
| 5 | Volatilita': il lunedi' e' piu' volatile (riapertura dei mercati tradizionali) | piu' stop | — |
| 6 | Costi: 0,02 R a giro con stop al 6% | piccoli | — |
| 7 | Artefatto: il lunedi' UTC comincia la domenica sera in America | (non provato) | — |
| 8 | Pochi lunedi' estremi | senza i 3 migliori crolla | — |
| 9 | Ritorno dei grandi operatori dopo il fine settimana (l'ipotesi) | R sopra la (b) in piu' anni | t sotto 1 |
| 10 | Lo stop al 6% e' meno di un ATR giornaliero e chiude i lunedi' volatili | molti stop | — |

**Ipotesi completa.** ETHUSDT, effetto del giorno della settimana, 1d.

**Varianti.**
* **I-09a** — 1d, long. Condizione: la barra appena chiusa e' la domenica UTC (si entra
  all'apertura del lunedi'). Uscita dopo 1 barra (all'apertura del martedi'). Stop al 6%.
  Unica variante: la fonte non dice nulla sugli altri giorni ne' sullo short. Previsione:
  R medio fra -0,10 e +0,15; non batte nettamente la (b).

---

## I-10 — Dopo un giorno anomalo, il prezzo continua

**Fonte.** Guglielmo Maria Caporale e Alex Plastun, «Price overreactions in the
cryptocurrency market», Journal of Economic Studies 46(5), 2019, pp. 1137-1155 (prima
versione: CESifo Working Paper 6861, gennaio 2018). Su Bitcoin, Litecoin, Ripple e Dash il
giorno dopo un giorno anomalo (rendimento oltre la media di un multiplo della deviazione
standard) ha movimenti piu' grandi del normale; nelle simulazioni comprare il rimbalzo
perde, seguire la direzione guadagna ma non oltre il caso.

**Affermazione falsificabile.** Su ETHUSDT, dopo un giorno con rendimento (chiusura /
apertura - 1) sopra la media + 1 deviazione standard dei 30 giorni prima, il giorno dopo un
long ha un R medio piu' alto di un long di un giorno a caso; specchio per i giorni anomali
negativi e lo short.

**Sotto-domande.** Conta la dimensione dell'anomalia (1, 2, 3 deviazioni)? Il volume? Chi
agisce: chi arriva tardi sulla notizia, le liquidazioni del giorno dopo. Tempo: un giorno.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Caso (la fonte trova guadagni non distinguibili dal caso) | t sotto 1 | t oltre la soglia |
| 2 | Volatilita': dopo un giorno grande il giorno dopo e' grande in entrambe le direzioni | piu' stop, R vicino alla (b) | — |
| 3 | Trend di fondo | come la (b) | batte la (b) |
| 4 | E' solo il mercato | — (contesto) | — |
| 5 | Costi: 0,02 R a giro | piccoli | — |
| 6 | Artefatto della chiusura UTC | (non provato) | — |
| 7 | Reversione: dopo l'eccesso il prezzo torna indietro (l'opposto) | R negativo, sotto la (b) | — |
| 8 | Pochi giorni estremi | senza i 3 migliori crolla | — |
| 9 | Diffusione lenta della notizia (l'ipotesi) | R sopra la (b) in piu' anni | t sotto 1 |
| 10 | Liquidazioni a catena che proseguono il giorno dopo | effetto piu' forte nei giorni negativi | — |

**Ipotesi completa.** ETHUSDT, continuazione dopo un giorno anomalo, 1d.

**Varianti.**
* **I-10a** — 1d, long. Condizione: rendimento della barra appena chiusa > 0 e > media + 1
  deviazione standard dei rendimenti delle 30 barre precedenti (esclusa la corrente).
  Uscita dopo 1 barra. Stop al 6%. Previsione: R medio fra -0,10 e +0,15; non batte
  nettamente la (b).
* **I-10b** — 1d, short. Condizione: rendimento < 0 e < media - 1 deviazione standard.
  Uscita dopo 1 barra. Stop al 6%. Previsione: R medio fra -0,15 e +0,10; non batte
  nettamente la (b).

---

## I-11 — Il passaggio di un numero tondo fa scattare gli stop

**Fonte.** Carol L. Osler, «Currency Orders and Exchange Rate Dynamics: An Explanation for
the Predictive Success of Technical Analysis», The Journal of Finance 58(5), 2003, pp.
1791-1819. Gli ordini di stop si ammassano appena oltre i numeri tondi (quelli di
acquisto appena sopra, quelli di vendita appena sotto): quando il prezzo passa un numero
tondo il movimento accelera.

**Affermazione falsificabile.** Su ETHUSDT a 1 ora, quando una chiusura passa verso l'alto
un livello tondo, le 4 barre dopo hanno un R medio piu' alto di trade casuali con la
stessa uscita; specchio verso il basso e short.

**Sotto-domande.** Quali numeri sono "tondi" per ETH: qui multipli di 100 dollari sopra
1000 e multipli di 10 sotto 1000 (scelta dichiarata, dalla convenzione dei prezzi). Conta
quanto e' tondo (1000 piu' di 1100)? Chi agisce: stop di chi e' short (sopra) e di chi e'
long (sotto), ingressi su rottura. Tempo: minuti o ore.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Caso | t sotto 1 | t oltre la soglia |
| 2 | Il passaggio di un livello e' solo una barra forte: e' momentum orario, non il livello | stesso R con livelli non tondi (non provato) | — |
| 3 | Gli stop crypto sono a percentuali, non a numeri tondi | nessun effetto | — |
| 4 | Ordini di presa di profitto al numero tondo: il prezzo torna indietro | R negativo | — |
| 5 | Volatilita' | — | — |
| 6 | Trend di fondo | come la (b) | — |
| 7 | E' solo il mercato | — (contesto) | — |
| 8 | Costi: 0,047-0,06 R a giro con stop a 1,5 ATR | R dopo costi vicino a zero | — |
| 9 | Artefatto: con prezzi sotto 1000 i livelli a 10 dollari sono molto fitti (a 150 dollari, il 7%; a 900, l'1%) | effetto diverso nel 2020 | — |
| 10 | Cascata di stop (l'ipotesi) | R sopra la (b) | t sotto 1 |

**Ipotesi completa.** ETHUSDT, livelli tondi e stop, 1h (l'effetto e' rapido; 1 ora e' la
barra piu' corta dove i costi restano sotto 0,1 R).

**Varianti.**
* **I-11a** — 1h, long. Condizione: esiste un livello tondo L con chiusura precedente < L
  <= chiusura corrente. Uscita dopo 4 barre. Stop a 1,5 ATR(14), al massimo 6%. Previsione:
  R medio fra -0,10 e +0,10; non batte nettamente la (b).
* **I-11b** — 1h, short. Condizione: chiusura precedente >= L > chiusura corrente. Uscita
  dopo 4 barre. Stop a 1,5 ATR(14), al massimo 6%. Previsione: R medio fra -0,10 e +0,10;
  non batte nettamente la (b).

---

## I-12 — Volume insolito e visibilita'

**Fonte.** Simon Gervais, Ron Kaniel e Dan H. Mingelgrin, «The High-Volume Return
Premium», The Journal of Finance 56(3), 2001, pp. 877-919. Un volume insolitamente alto in
un giorno o in una settimana precede rendimenti piu' alti nel mese dopo; un volume
insolitamente basso, rendimenti piu' bassi. Spiegazione: il volume cambia la visibilita'
del titolo e quindi la domanda.

**Affermazione falsificabile.** Su ETHUSDT, dopo un giorno con volume fra i 5 piu' alti
degli ultimi 50 giorni (il decimo superiore, come nella fonte), un long tenuto 10 giorni ha
un R medio piu' alto di un long casuale con la stessa uscita; dopo un giorno con volume fra
i 5 piu' bassi, uno short tenuto 10 giorni.

**Sotto-domande.** L'effetto dipende dal segno del rendimento del giorno? (La fonte dice
di no.) Chi agisce: nuovi investitori che notano la moneta. Tempo: settimane.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Caso | t sotto 1 | t oltre la soglia |
| 2 | Il volume alto accompagna i crolli (capitolazione) e i massimi | effetto con segno opposto secondo il rendimento del giorno | — |
| 3 | Trend di fondo: il volume cresce nei rialzi (2020-2021) | come la (b) | batte la (b) |
| 4 | E' solo il mercato | — (contesto) | — |
| 5 | Volatilita': volume alto = volatilita' alta, lo stop al 6% scatta spesso | molti stop | — |
| 6 | Costi: 0,02 R a giro, ma funding di 10 giorni sui long del 2020-2021 | -0,02/-0,05 R | — |
| 7 | Artefatto: il volume qui e' volume in ETH per chiusura (approssimazione del volume in USDT) | (dichiarato) | — |
| 8 | Il volume cresce col tempo (2020: 0,7 miliardi, 2021: 7,6): "alto rispetto a 50 giorni" capita piu' spesso nei periodi di crescita | trade concentrati nel 2020-2021 | — |
| 9 | Pochi trade estremi | senza i 3 migliori crolla | — |
| 10 | Visibilita' e domanda (l'ipotesi) | R sopra la (b) in piu' anni | t sotto 1 |

**Ipotesi completa.** ETHUSDT, volume e visibilita', 1d.

**Varianti.** Volume del giorno = volume (in ETH) per chiusura, un'approssimazione del
volume in USDT (le candele del motore non portano la colonna `quote_volume`).
* **I-12a** — 1d, long. Condizione: il volume del giorno appena chiuso e' fra i 5 piu' alti
  dei 50 giorni che finiscono con lui. Uscita dopo 10 barre. Stop al 6%. Previsione: R
  medio fra -0,20 e +0,20; non batte nettamente la (b).
* **I-12b** — 1d, short. Condizione: volume fra i 5 piu' bassi dei 50 giorni. Uscita dopo
  10 barre. Stop al 6%. Previsione: R medio fra -0,20 e +0,15; non batte nettamente la (b).

---

## I-13 — Vendite forzate: la spirale di liquidita' e il rimbalzo

**Fonte.** Markus K. Brunnermeier e Lasse Heje Pedersen, «Market Liquidity and Funding
Liquidity», The Review of Financial Studies 22(6), 2009, pp. 2201-2238. Quando chi opera a
leva perde, i margini salgono e deve vendere: le vendite forzate spingono il prezzo oltre
il valore, e la liquidita' torna dopo (il prezzo recupera).

**Affermazione falsificabile.** Su ETHUSDT a 1 ora, dopo una barra che scende di oltre 2
ATR(24) dall'apertura alla chiusura con volume oltre 3 volte la media delle 24 barre prima
(il segno delle liquidazioni a catena), nelle 6 ore dopo un long ha un R medio piu' alto di
un long casuale con la stessa uscita; specchio per i rialzi forzati (chiusura degli
short) e lo short.

**Sotto-domande.** Il rimbalzo e' piu' forte quando il funding era alto (piu' leva)? Chi
agisce: i liquidatori dell'exchange vendono a mercato; chi compra sono i market maker e chi
cerca prezzi bassi. Tempo: ore.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Caso | t sotto 1 | t oltre la soglia |
| 2 | La caduta e' informazione (notizie): il prezzo continua a scendere | R negativo | — |
| 3 | Volatilita' altissima dopo l'evento: lo stop scatta | molti stop | — |
| 4 | Trend di fondo | — | — |
| 5 | E' solo il mercato (BTC guida la caduta) | — (contesto) | — |
| 6 | Costi: stop sotto il minimo della barra, distanza grande, 0,03 R a giro | piccoli | — |
| 7 | Artefatto: il volume del motore e' in ETH, non in USDT (per un rapporto su 24 ore conta poco) | — | — |
| 8 | Pochi eventi (marzo 2020, maggio 2021) fanno tutto | senza i 3 migliori crolla | — |
| 9 | Liquidita' che torna dopo le vendite forzate (l'ipotesi) | R sopra la (b) | t sotto 1 |
| 10 | Il rimbalzo c'e' ma arriva dopo piu' di 6 ore | R vicino a zero | — |

**Ipotesi completa.** ETHUSDT, rimbalzo dopo vendite (o acquisti) forzati, 1h.

**Varianti.**
* **I-13a** — 1h, long. Condizione: chiusura - apertura < -2 x ATR(24) calcolato sulle
  barre precedenti, e volume > 3 volte la media del volume delle 24 barre precedenti.
  Uscita dopo 6 barre. Stop: minimo della barra del segnale meno 0,5 ATR, con distanza al
  massimo 6%. Previsione: R medio fra -0,10 e +0,20; non batte nettamente la (b).
* **I-13b** — 1h, short, specchio (chiusura - apertura > +2 ATR, volume > 3 volte; stop
  sopra il massimo piu' 0,5 ATR). Previsione: R medio fra -0,15 e +0,10; non batte
  nettamente la (b).

---

## I-14 — Rifiuto al massimo (minimo) del giorno prima

**Fonte.** Carol L. Osler, «Support for Resistance: Technical Analysis and Intraday
Exchange Rates», Federal Reserve Bank of New York Economic Policy Review 6(2), luglio 2000,
pp. 53-68. I livelli di supporto e resistenza indicati dagli operatori fanno invertire i
trend intragiornalieri piu' spesso del caso.

**Affermazione falsificabile.** Su ETHUSDT a 1 ora, quando una barra supera il massimo del
giorno UTC precedente ma chiude sotto di esso (rifiuto), nelle 6 ore dopo uno short ha un R
medio piu' alto di uno short casuale con la stessa uscita; specchio al minimo del giorno
prima e long.

**Sotto-domande.** Il massimo del giorno prima e' un livello che gli operatori crypto
guardano (grafici giornalieri)? Conta se e' il primo tocco del giorno? Chi agisce: chi
vende alla resistenza e chi prende profitto. Tempo: ore.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Caso | t sotto 1 | t oltre la soglia |
| 2 | Il livello e' solo un massimo recente: e' reversione di breve oraria | stesso effetto su massimi casuali (non provato) | — |
| 3 | Rotture vere: dopo il rifiuto il prezzo riprova e passa | R negativo | — |
| 4 | Trend di fondo: in un rialzo i massimi si superano | short in perdita nel 2020-2021 | — |
| 5 | E' solo il mercato | — (contesto) | — |
| 6 | Volatilita' | — | — |
| 7 | Costi: stop vicino (sopra il massimo della barra), costo 0,05-0,1 R | R dopo costi negativo | — |
| 8 | Artefatto del giorno UTC | (non provato) | — |
| 9 | Pochi trade estremi | senza i 3 migliori crolla | — |
| 10 | Ordini ammassati al livello (l'ipotesi) | R sopra la (b) in piu' anni | t sotto 1 |

**Ipotesi completa.** ETHUSDT, supporto e resistenza dal giorno prima, 1h.

**Varianti.**
* **I-14a** — 1h, short. Condizione: massimo della barra > massimo del giorno UTC
  precedente e chiusura < massimo del giorno precedente. Stop: massimo della barra piu' 0,25
  ATR(14), con distanza al massimo 6%. Uscita dopo 6 barre. Previsione: R medio fra -0,15 e
  +0,10; non batte nettamente la (b).
* **I-14b** — 1h, long, specchio (minimo della barra < minimo del giorno precedente e
  chiusura > minimo del giorno precedente; stop sotto il minimo della barra meno 0,25 ATR).
  Previsione: R medio fra -0,10 e +0,15; non batte nettamente la (b).

---

## Idee aggiunte dopo i primi test (scritte l'8 ottobre 2026, prima di contarle)

Le tre idee qui sotto sono state scritte DOPO aver visto i risultati di costruzione di
I-01 ... I-07 (lo si dichiara), e prima di qualunque conteggio o test loro. Non nascono da
quei risultati: sono meccanismi di famiglie non ancora provate (squilibrio degli ordini,
periodicita' oraria, rottura di volatilita' dentro il giorno), ognuno con la sua fonte. Il
protocollo vuole il budget usato per intero e le idee nuove con fonte prima dei ritocchi
(regola 6). Si testano solo finche' c'e' budget (30 varianti).

---

## I-15 — Lo squilibrio degli ordini del giorno prevede il giorno dopo

**Fonte.** Tarun Chordia e Avanidhar Subrahmanyam, «Order imbalance and individual stock
returns: Theory and evidence», Journal of Financial Economics 72(3), 2004, pp. 485-518.
Lo squilibrio fra acquisti e vendite avviati da chi prende liquidita' in un giorno prevede
il rendimento del giorno dopo: chi ha informazione spezza gli ordini su piu' giorni e chi fa
mercato aggiusta il prezzo con ritardo.

**Affermazione falsificabile.** Su ETHUSDT, dopo un giorno in cui la quota di volume
comprato a mercato (taker buy / volume, colonne dei file di Binance) supera la sua media
dei 30 giorni prima, un long di un giorno ha un R medio piu' alto di un long casuale con la
stessa uscita; specchio per la quota sotto la media e lo short.

**Sotto-domande.** Conta la dimensione dello squilibrio? Vale nei giorni di volume alto?
Chi agisce: chi compra a mercato con informazione o con fretta; chi fa mercato rimane
corto e alza i prezzi. Tempo: un giorno.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Caso | t sotto 1 | t oltre la soglia |
| 2 | Lo squilibrio e' solo il rendimento del giorno (si compra quando sale): e' momentum di un giorno | stesso effetto della continuazione dopo un giorno positivo | — |
| 3 | Nei futures la quota di taker buy ha un livello strutturale diverso da 0,5 | (tolto confrontando con la media dei 30 giorni) | — |
| 4 | Trend di fondo | come la (b) | batte la (b) |
| 5 | E' solo il mercato | — (contesto) | — |
| 6 | Volatilita' | — | — |
| 7 | Costi: 0,02 R a giro con stop al 6% | piccoli | — |
| 8 | Artefatto: la classificazione taker dell'exchange include ordini di liquidazione (vendite forzate a mercato) | la quota bassa segnala liquidazioni, poi rimbalzo (short in perdita) | — |
| 9 | Pochi giorni estremi | senza i 3 migliori crolla | — |
| 10 | Informazione spezzata su piu' giorni (l'ipotesi) | R sopra la (b) in piu' anni | t sotto 1 |

**Ipotesi completa.** ETHUSDT, squilibrio degli ordini, 1d.

**Varianti.** Quota del giorno = taker_buy_volume / volume della candela giornaliera last.
* **I-15a** — 1d, long. Condizione: quota del giorno appena chiuso > media delle quote dei
  30 giorni precedenti (escluso il giorno corrente). Uscita dopo 1 barra. Stop al 6%.
  Previsione: R medio fra -0,10 e +0,10; non batte nettamente la (b).
* **I-15b** — 1d, short. Condizione: quota < media dei 30 giorni precedenti. Uscita dopo 1
  barra. Stop al 6%. Previsione: R medio fra -0,10 e +0,10; non batte nettamente la (b).

---

## I-16 — La stessa ora dei giorni passati (periodicita' intragiornaliera)

**Fonte.** Steven L. Heston, Robert A. Korajczyk e Ronnie Sadka, «Intraday Patterns in the
Cross-Section of Stock Returns», The Journal of Finance 65(4), 2010, pp. 1369-1407. Il
rendimento di un titolo in una mezz'ora del giorno e' legato a quello della stessa mezz'ora
nei giorni precedenti, fino a 40 giorni: flussi di scambio che si ripetono alla stessa ora
(istituzioni, ribilanciamenti).

**Affermazione falsificabile.** Su ETHUSDT a 1 ora, l'ora del giorno con il rendimento medio
piu' alto negli ultimi 20 giorni (se positivo) ha, il giorno dopo, un R medio per un long di
un'ora piu' alto di un'ora casuale con la stessa uscita; specchio per l'ora peggiore
(media negativa) e lo short.

**Sotto-domande.** Le ore "forti" sono legate a sessioni (Asia, Europa, America) o al
funding (00, 08, 16 UTC)? Quanto sono stabili? Chi agisce: flussi ricorrenti alla stessa
ora. Tempo: un'ora.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Caso: con 24 ore la migliore delle 24 medie e' alta per caso (selezione) | R vicino alla (b) | t oltre la soglia |
| 2 | Costi: 0,047 R a giro con stop a 2 ATR, contro un movimento medio orario minimo | R medio negativo | R dopo costi positivo |
| 3 | Stagionalita' fissa (un'ora sempre forte) invece di periodicita' mobile | — | — |
| 4 | Volatilita' oraria diversa | — | — |
| 5 | Trend di fondo | — | — |
| 6 | E' solo il mercato | — (contesto) | — |
| 7 | Artefatto: il settlement del funding alle 00, 08, 16 sposta i prezzi a ore fisse | ore scelte vicine ai settlement | — |
| 8 | Pochi giorni estremi | senza i 3 migliori crolla | — |
| 9 | Flussi ricorrenti (l'ipotesi) | R sopra la (b) | t sotto 1 |
| 10 | 20 giorni sono troppo pochi per stimare la media di un'ora (rumore) | effetto nullo | — |

**Ipotesi completa.** ETHUSDT, periodicita' oraria, 1h.

**Varianti.**
* **I-16a** — 1h, long. Alla chiusura di ogni barra si guarda l'ora successiva h: se h e'
  l'ora con la media piu' alta degli ultimi 20 rendimenti (chiusura/apertura - 1) di
  ciascuna delle 24 ore, e quella media e' > 0, long all'apertura dell'ora h. Uscita dopo
  1 barra. Stop a 2 ATR(14), al massimo 6%. Previsione: R medio fra -0,12 e 0,00; non batte
  nettamente la (b).
* **I-16b** — 1h, short, specchio (l'ora con la media piu' bassa, se < 0). Previsione: R
  medio fra -0,12 e 0,00; non batte nettamente la (b).

---

## I-17 — Rottura di volatilita' dall'apertura del giorno

**Fonte.** Larry Williams, «Long-Term Secrets to Short-Term Trading», John Wiley & Sons,
1999. La rottura di volatilita': quando il prezzo si allontana dall'apertura del giorno di
una frazione dell'escursione del giorno prima, il giorno tende a chiudere in quella
direzione (espansione dell'escursione).

**Affermazione falsificabile.** Su ETHUSDT, la prima volta in un giorno UTC che una barra di
1 ora chiude sopra apertura del giorno + 0,5 x (massimo - minimo del giorno prima), un long
tenuto fino alla fine del giorno ha un R medio piu' alto di un long casuale con la stessa
uscita; specchio sotto l'apertura e short.

**Sotto-domande.** Conta l'ora della rottura? La dimensione dell'escursione di ieri? Chi
agisce: chi segue la giornata, gli stop sopra i massimi del giorno. Tempo: ore, fino alla
fine del giorno.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Caso | t sotto 1 | t oltre la soglia |
| 2 | Trend di fondo | long buono nel 2020-2021 come la (b) | batte la (b) |
| 3 | E' solo il mercato | — (contesto) | — |
| 4 | Volatilita': le rotture accadono nei giorni volatili, in entrambe le direzioni | come la (b) | — |
| 5 | Costi: stop all'apertura del giorno (distanza grande), costo sotto 0,03 R | piccoli | — |
| 6 | Artefatto del giorno UTC | (non provato) | — |
| 7 | Falsa rottura: ritorno verso l'apertura | molti stop | — |
| 8 | Pochi giorni estremi | senza i 3 migliori crolla | — |
| 9 | Espansione dell'escursione nella direzione della rottura (l'ipotesi) | R sopra la (b) | t sotto 1 |
| 10 | Momentum intragiornaliero gia' coperto da altre idee (I-06) | — | — |

**Ipotesi completa.** ETHUSDT, rottura di volatilita' intragiornaliera, 1h.

**Varianti.**
* **I-17a** — 1h, long. Condizione: barra con apertura fra le 00:00 e le 22:00 UTC; prima
  barra del giorno con chiusura > apertura del giorno + 0,5 x escursione del giorno UTC
  precedente. Uscita: "chiudi" alla chiusura della barra delle 23:00 (fine del giorno).
  Stop all'apertura del giorno, con distanza al massimo 6%. Previsione: R medio fra -0,10 e
  +0,15; non batte nettamente la (b).
* **I-17b** — 1h, short, specchio (chiusura < apertura del giorno - 0,5 x escursione di
  ieri; stop all'apertura del giorno). Previsione: R medio fra -0,15 e +0,10; non batte
  nettamente la (b).

---

## Ordine dei test

Le idee si contano e si testano nell'ordine di questo file (I-01 ... I-14), una variante
alla volta, in serie (`lezioni/metodo.md`: i test che scrivono nel log vanno in serie).
Gli `id` del log (ETHUSDT-001, ...) si assegnano alla registrazione o allo scarto;
`variante_n` cresce solo per le varianti testate. Le varianti sono 27 (13 idee con due
varianti e una con una): se tutte arrivano ai trade minimi, restano 3 unita' di budget per i
ritocchi, nell'ordine della regola 6.
