# DYDXUSDT — ipotesi (Fase 1)

Scritto PRIMA di qualunque test. Ogni idea ha la sua fonte (pubblicata prima del 2024-01-01), la
riformulazione falsificabile, le sotto-domande, almeno 10 spiegazioni concorrenti con la loro
previsione e cosa le smentirebbe, l'ipotesi completa e tutte le varianti con il loro motivo.
Il codice delle varianti è in `codice/varianti.py`, quello comune in `codice/comune.py`.

## Regole comuni a tutte le varianti (fissate prima del primo test)

* Moneta DYDXUSDT, contratto perpetuo USDS-M. Costruzione 2021-09-01 → 2023-04-19 (596 giorni),
  validazione 2023-04-20 → 2023-12-31 (log, voce DYDXUSDT-N001).
* Segnale alla chiusura di una barra, ingresso all'apertura della barra dopo (motore, sezione 7).
* Stop sul last; liquidazione sul mark; funding storico vero; commissione 0,05% e slippage 0,02% per
  lato (fascia della scheda); rischio 1% del capitale, leva massima 2, margine isolated.
* Salvo dove detto, lo stop è a k volte l'ATR di Wilder a 14 barre dal close della barra del
  segnale, senza target, e l'uscita è a tempo: dopo H barre chiuse in posizione la posizione si chiude
  all'apertura della barra seguente. Lo stop serve a definire il rischio (R) e a proteggere; l'ipotesi
  riguarda il rendimento nel periodo di tenuta.
* Filtro di liquidità della Fase 0 (mesi sotto 20 milioni di USDT al giorno): uguale per tutte.
* Riscaldamento: il segnale (stop) non si calcola prima che gli indicatori della condizione siano
  pronti, così la (a) e la (b) partono dalla prima barra in cui la variante può entrare.
* Costo di un giro (commissione + slippage, andata e ritorno) = 0,14% del prezzo. In R vale
  0,14% / distanza dello stop; le distanze tipiche per timeframe sono in `fase0_dati.md` (ATR mediano):
  le previsioni sono scritte al netto dei costi.
* Il bot oggi: stop oltre il 6% non tradabile (`stop_massimo_bot`), indicatori dal vivo solo fino a 1h,
  orizzonte 96 barre. Le varianti a 4h, 8h e 1d, e quelle con stop oltre il 6%, richiederebbero
  un'aggiunta al bot: si dichiara in consegna, non si cambia la regola per questo.
* Regola 8: so a grandi linee come sono andati i mercati dopo il 2023. Nessuna idea qui è scelta per
  quello: le idee vengono dalle fonti, e dove la fonte lo permette si provano entrambe le direzioni
  con regole speculari, per non scegliere la direzione con quello che so.

---

## I-01 — Momento della serie su candele giornaliere

**Fonte.** Yukun Liu e Aleh Tsyvinski, «Risks and Returns of Cryptocurrency», The Review of Financial
Studies 34(6), 2021 (prima versione NBER Working Paper 24877, agosto 2018). Riferimento generale:
Tobias J. Moskowitz, Yao Hua Ooi e Lasse Heje Pedersen, «Time Series Momentum», Journal of Financial
Economics 104(2), 2012.

**Affermazione verificabile.** Su una crypto, il rendimento dell'ultima settimana predice con lo stesso
segno il rendimento dei giorni successivi: dopo una settimana in salita, i 3 giorni seguenti hanno in
media un rendimento più alto (in R, dopo i costi) di 3 giorni presi a caso; dopo una settimana in discesa,
più basso. Falsificata se i trade long dopo settimane positive (o short dopo settimane negative) non
battono nettamente l'entrata casuale con la stessa uscita.

**Sotto-domande.** Vale con movimenti di qualunque dimensione o solo con quelli grandi? In quale
regime di volatilità? Chi sta comprando: investitori che inseguono il prezzo (attenzione, notizie
lente a diffondersi, ingressi di capitali). Perché dovrebbe continuare: sotto-reazione all'informazione e
inseguimento del trend. Quando: Liu e Tsyvinski lo trovano a 1-4 settimane sul mercato crypto nel suo
insieme; su una moneta sola e su 3 giorni l'effetto, se c'è, è più piccolo e più rumoroso.

**Spiegazioni concorrenti (previsione → cosa la smentirebbe).**
1. Effetto casuale. → La variante non batte la (b); il `t` contro la (b) è vicino a 0. Smentita da un
   `t` netto e stabile negli anni.
2. Trend di fondo della moneta (il prezzo di DYDX scende per gran parte del 2022). → La (b) long ha R
   medio negativo quanto la variante; long e short si comportano come la (b) della loro direzione.
   Smentita se la variante batte la (b) della sua stessa direzione.
3. È solo il mercato (DYDX segue BTC). → Il vantaggio sparisce se si guarda il momento di BTC invece
   di quello di DYDX; il buy and hold dà lo stesso segno. Smentita se il vantaggio regge anche negli anni
   in cui BTC va nella direzione opposta.
4. Volatilità: dopo settimane forti la volatilità è alta, gli stop a 2 ATR scattano di più. → Molti
   esiti a stop; R medio dominato dagli stop. Smentita se gli esiti a tempo portano il guadagno.
5. Effetto costi: con stop larghi i costi in R sono piccoli, ma il funding nelle fasi euforiche è alto
   per i long. → Il funding mangia il vantaggio long. Smentita se il funding totale è piccolo rispetto al
   guadagno.
6. Artefatto dei dati (buchi, barre tolte dall'allineamento). → Pochi trade con barre mancanti
   spostano il risultato. Smentita dal conteggio dei buchi nei trade.
7. Pochi trade estremi (il listing di settembre 2021, con movimenti del 100%). → Senza i 3 trade migliori
   l'R medio crolla. Smentita se senza i 3 migliori resta sopra la (b).
8. Un solo periodo (l'euforia di fine 2021). → Vantaggio solo nel 2021. Smentita se c'è in più anni.
9. Ritorno verso la media invece che continuazione a 3 giorni (l'orizzonte breve è dominato dal
   rimbalzo). → R medio sotto la (b). Smentita da un R sopra la (b).
10. Il segnale settimanale è una media mobile mascherata: entra quasi sempre nella stessa direzione del
    trend di fondo. → La quota di giorni con segnale è molto sbilanciata; la (a) e la variante coincidono
    quasi. Smentita se la variante batte nettamente la (a).
11. Dipendenza dal giorno della settimana (le settimane si misurano da ogni giorno, ma i ritorni del
    fine settimana sono diversi). → Il vantaggio viene da un solo giorno d'ingresso. Smentita se è
    distribuito sui giorni.

**Ipotesi completa.** DYDXUSDT, momento della serie a 7 giorni, candele giornaliere (il meccanismo
lavora su giorni e settimane; più corto non è il fenomeno della fonte, più lungo non arriva ai 70 trade
in 596 giorni), tenuta 3 giorni.

**Varianti.**
* `I01_long` — long se il rendimento delle ultime 7 candele giornaliere (close su close di 7 giorni
  prima) è positivo; stop 2 ATR(14) giornaliero; uscita dopo 3 barre. Motivo: la direzione della fonte.
* `I01_short` — short se lo stesso rendimento è negativo; regole speculari. Motivo: la fonte parla di
  continuazione in entrambe le direzioni; si provano separate (regola 6).

---

## I-02 — Rottura del massimo o del minimo di 50 barre

**Fonte.** William Brock, Josef Lakonishok e Blake LeBaron, «Simple Technical Trading Rules and the
Stochastic Properties of Stock Returns», The Journal of Finance 47(5), dicembre 1992 (regola «trading
range break»: comprare quando il prezzo supera il massimo precedente, vendere quando rompe il minimo).

**Affermazione verificabile.** Quando il close supera il massimo delle 50 barre precedenti, il prezzo
nelle 10 barre seguenti sale in media più che dopo un ingresso casuale (in R, dopo i costi); quando rompe
il minimo, scende di più. Falsificata se la variante non batte nettamente la (a) e la (b).

**Sotto-domande.** Vale per rotture di qualunque ampiezza? In regimi di volatilità bassa o alta?
Chi opera: chi ha ordini stop sopra le resistenze (short che chiudono, compratori di rottura), chi segue
il trend. Perché dovrebbe muovere il prezzo: gli ordini concentrati oltre il livello si eseguono a
catena. Quando: nelle ore e nei giorni dopo la rottura. Timeframe: con candele giornaliere su 596 giorni
le rotture di 50 giorni sono poche decine; 4 ore conserva il meccanismo (livelli visibili a tutti su
una scala di giorni: 50 barre sono circa 8 giorni) con abbastanza eventi.

**Spiegazioni concorrenti.**
1. Effetto casuale. → `t` contro la (b) vicino a 0. Smentita da un `t` netto stabile.
2. Trend di fondo: le rotture al ribasso sono frequenti nel 2022 perché il prezzo scende. → La variante
   short ha lo stesso R della (b) short. Smentita se batte la (b) della sua direzione.
3. È solo il mercato: le rotture di DYDX coincidono con quelle di BTC. → Il vantaggio c'è solo quando
   anche BTC rompe. Smentita se regge sulle rotture proprie di DYDX (da guardare nei fallimenti).
4. Falsi segnali in laterale: la rottura si richiude. → Molti stop nelle prime barre. Smentita se gli
   esiti a tempo dominano.
5. Volatilità: dopo una rottura la volatilità sale; lo stop a 2 ATR è sproporzionato. → R medio
   dominato dalla varianza. Smentita da un guadagno medio stabile senza i 3 migliori.
6. Ritorno verso la media sulle rotture (stop hunting: il prezzo prende gli stop e torna indietro). →
   R medio sotto la (b). Smentita da R sopra la (b).
7. Costi: rotture con barre larghe e slippage reale maggiore di quello modellato. → Il vantaggio sparisce
   a costi doppi. Smentita se regge a costi doppi.
8. Pochi eventi estremi (settembre 2021, crollo di maggio 2022, di novembre 2022). → Senza i 3 migliori
   crolla. Smentita se resta sopra la (b).
9. Un solo anno. → Il vantaggio è tutto nel 2021 o nel 2022. Smentita se c'è in più anni.
10. Artefatto dei dati: barre tolte dall'allineamento accorciano il canale. → Rotture vicino ai buchi.
    Smentita dal conteggio dei buchi.
11. Funding: le rotture al rialzo arrivano con funding alto che pesa sui long tenuti 40 ore. → Funding
    totale grande. Smentita se è piccolo.

**Ipotesi completa.** DYDXUSDT, rottura del canale di 50 barre, candele da 4 ore, tenuta 10 barre
(circa 40 ore, l'ordine dei 10 giorni della fonte riportato alla scala della barra).

**Varianti.**
* `I02_long` — long se il close supera il massimo degli high delle 50 barre precedenti; stop 2 ATR(14);
  uscita dopo 10 barre.
* `I02_short` — short se il close scende sotto il minimo dei low delle 50 barre precedenti; speculare.

---

## I-03 — Ipervenduto a 2 barre dentro il trend (ritorno verso la media)

**Fonte.** Larry Connors e Cesar Alvarez, «Short Term Trading Strategies That Work», TradingMarkets
Publishing, 2008 (regola: sopra la media a 200, RSI a 2 periodi sotto 10 → comprare; uscire quando il
close supera la media a 5). L'RSI è di J. Welles Wilder, «New Concepts in Technical Trading Systems»,
1978.

**Affermazione verificabile.** Dentro un trend positivo (close sopra la media a 200 barre), dopo due
barre di forte calo (RSI(2) sotto 10) il prezzo rimbalza: i trade long chiusi al ritorno sopra la media a
5 hanno R medio più alto dell'ingresso casuale con la stessa uscita. Speculare per lo short in trend
negativo con RSI(2) sopra 90. Falsificata se non batte nettamente la (a) e la (b).

**Sotto-domande.** Vale con cali grandi o piccoli? Con volatilità alta (liquidazioni a catena) o bassa?
Chi opera: chi fornisce liquidità ai venditori costretti o impazienti; chi compra il calo dentro il
trend. Perché il prezzo dovrebbe tornare: la pressione di vendita temporanea non porta informazione.
Quando: in poche barre. Timeframe: la fonte usa candele giornaliere su azioni; su DYDX una media a 200
giorni lascia meno di 400 giorni utili e pochi segnali; si sceglie 1 ora (media a 200 ore, circa 8
giorni), perché il crypto si muove 24 ore su 24 e i ritorni dopo eccessi di breve sono un fenomeno di
ore.

**Spiegazioni concorrenti.**
1. Effetto casuale. → `t` vicino a 0.
2. Trend di fondo: il filtro a 200 sceglie la direzione del trend, e la (b) nella stessa direzione ha
   lo stesso R. → Variante uguale alla (b). Smentita se la batte.
3. È solo il mercato: i cali di DYDX sono cali di BTC che rimbalza. → Vantaggio solo quando BTC scende
   insieme. Smentita guardando i fallimenti.
4. Volatilità: l'RSI(2) basso arriva dopo barre larghe; uno stop a 3 ATR si allarga e l'R per trade
   cambia scala. → Effetto di scala, non di direzione. Smentita se R e percentuale vanno d'accordo.
5. Asimmetria degli esiti: molti piccoli guadagni e rare grandi perdite (uscita al ritorno sulla media
   a 5, nessun target). → Win rate alto, R medio vicino a zero. Smentita da R medio netto sopra la (b).
6. Costi: a 1 ora e con uscite rapide i costi in R pesano. → Il vantaggio lordo c'è ma il netto no.
   Smentita se resta a costi doppi.
7. Continuazione invece di ritorno (liquidazioni a catena nel crypto). → R sotto la (b). Smentita da R
   sopra la (b).
8. Pochi episodi estremi. → Senza i 3 migliori crolla.
9. Un solo anno (2021 rialzista). → Vantaggio solo nel 2021.
10. Artefatto dei dati (buchi in barre di grande movimento). → Trade a cavallo dei buchi.
11. Momento della giornata: i cali avvengono a ore precise (apertura degli Stati Uniti) e il rimbalzo è
    stagionale. → Vantaggio concentrato a certe ore. Da guardare nei fallimenti.

**Ipotesi completa.** DYDXUSDT, ritorno verso la media dentro il trend, candele da 1 ora, uscita al
ritorno oltre la media a 5, stop 3 ATR(14) per definire il rischio (la fonte non usa stop).

**Varianti.**
* `I03_long` — long se close > media semplice a 200 e RSI(2) < 10; uscita quando close > media a 5;
  stop 3 ATR.
* `I03_short` — short se close < media a 200 e RSI(2) > 90; uscita quando close < media a 5; speculare.

---

## I-04 — Momento intragiornaliero: la prima mezz'ora predice l'ultima

**Fonte.** Lei Gao, Yufeng Han, Sophia Zhengzi Li e Guofu Zhou, «Market Intraday Momentum», Journal
of Financial Economics 129(2), 2018 (sull'indice S&P 500: il rendimento della prima mezz'ora predice
quello dell'ultima). Per Bitcoin, con il giorno in UTC: Dehua Shen, Andrew Urquhart e Pengfei Wang,
«Bitcoin Intraday Time Series Momentum», The Financial Review 57(2), 2022 (online 2021).

**Affermazione verificabile.** Se la prima mezz'ora del giorno UTC (00:00-00:30) chiude in salita,
l'ultima mezz'ora (23:30-24:00) ha in media un rendimento più alto di una mezz'ora presa a caso;
speculare in discesa. Falsificata se la variante non batte nettamente la (a) e la (b).

**Sotto-domande.** Vale con prime mezz'ore grandi o piccole? Nei giorni volatili? Chi opera
nell'ultima mezz'ora UTC: chi ribilancia a fine giornata, chi chiude posizioni per i conteggi giornalieri,
gli arbitraggisti che coprono a fine giornata (la fonte su azioni parla di operatori informati lenti e di
coperture). Il giorno UTC ha significato su Binance (candele giornaliere, conteggi). Quando: solo
l'ultima mezz'ora.

**Spiegazioni concorrenti.**
1. Effetto casuale. → `t` vicino a 0.
2. Trend di fondo. → Long e short come le (b) della loro direzione.
3. È solo il mercato: è il momento intragiornaliero di BTC, che DYDX segue. → (non distinguibile con
   un test su DYDX solo; si dichiara).
4. Stagionalità oraria pura: l'ultima mezz'ora UTC sale (o scende) sempre, a prescindere dalla prima.
   → Long e short hanno R di segno opposto e simmetrico rispetto alla (b) senza la condizione;
   il controllo è la (a) (ogni mezz'ora) e la differenza fra le due varianti.
5. Costi: in 30 minuti il movimento tipico è dello stesso ordine dei costi. → R lordo positivo, netto
   negativo. Smentita se a costi doppi regge.
6. Volatilità: le prime mezz'ore grandi annunciano giorni volatili, gli stop a 2 ATR scattano. →
   Esiti a stop frequenti.
7. Funding: il settlement delle 00:00 cade all'uscita (momento ambiguo, contato solo se costo). →
   Funding sistematico contro. Smentita dal funding totale.
8. Artefatto: barre mancanti alle 00:00 o alle 23:00 (manutenzioni). → Giorni saltati, non bias.
9. Pochi giorni estremi. → Senza i 3 migliori crolla.
10. Un solo anno. → Vantaggio in un anno solo.
11. Effetto del settlement delle 00:00 (chi chiude prima del funding vende nell'ultima mezz'ora quando
    il funding è positivo). → Il rendimento dell'ultima mezz'ora dipende dal funding, non dalla prima
    mezz'ora. Da guardare nei fallimenti.

**Ipotesi completa.** DYDXUSDT, momento intragiornaliero, candele da 30 minuti (la scala della fonte),
ingresso all'apertura delle 23:30 UTC, uscita all'apertura delle 00:00, stop 2 ATR(14) a 30 minuti.

**Varianti.**
* `I04_long` — long se la barra 00:00-00:30 dello stesso giorno ha close sopra l'open.
* `I04_short` — short se ha close sotto l'open.

---

## I-05 — Ritorno dopo un movimento forte con volume alto (liquidità forzata)

**Fonte.** John Y. Campbell, Sanford J. Grossman e Jiang Wang, «Trading Volume and Serial Correlation in
Stock Returns», The Quarterly Journal of Economics 108(4), novembre 1993 (i movimenti di prezzo
accompagnati da volume alto, se nati da domanda di liquidità non informata, tendono a invertirsi).

**Affermazione verificabile.** Dopo una barra oraria che scende più di 2 ATR con un volume in USDT oltre
3 volte la media delle 24 ore precedenti, le 12 ore seguenti salgono in media più di un ingresso
casuale (in R, dopo i costi); speculare dopo una salita forte con volume alto. Falsificata se la
variante non batte nettamente la (a) e la (b).

**Sotto-domande.** Vale per i movimenti con volume alto nati da liquidazioni (venditori costretti) e non
da notizie? Chi opera: le liquidazioni dei futures (ordini a mercato forzati), chi fornisce liquidità
contro di loro. Perché il prezzo dovrebbe tornare: la vendita forzata non porta informazione e chi
fornisce liquidità chiede un premio. Quando: in ore.

**Spiegazioni concorrenti.**
1. Effetto casuale. → `t` vicino a 0.
2. Notizie: i movimenti con volume alto portano informazione e continuano (Llorente, Michaely, Saar e
   Wang, 2002). → R sotto la (b). Smentita da R sopra la (b).
3. Trend di fondo. → La variante si comporta come la (b) della sua direzione.
4. È solo il mercato: i crolli di DYDX sono crolli di tutto il crypto, che rimbalza. → Il vantaggio c'è
   solo quando anche BTC crolla. Da guardare nei fallimenti.
5. Volatilità: dopo un crollo la volatilità resta alta; lo stop a 2 ATR (ATR gonfiato dalla barra) è
   largo e l'R per trade piccolo. → R vicini a zero.
6. Costi: slippage reale nei crolli molto più alto di 0,02%. → Il backtest è ottimista; a costi doppi
   cala molto.
7. Pochi eventi estremi. → Senza i 3 migliori crolla.
8. Un solo anno (il 2022 dei crolli). → Vantaggio in un anno solo.
9. Artefatto dei dati: barre con volume anomalo per errori della fonte. → Da guardare nei trade.
10. Il volume alto è un effetto di calendario (apertura degli Stati Uniti, settlement). → Eventi
    concentrati a certe ore.
11. Il mark si discosta dal last nei crolli e la liquidazione del modello scatta. → Violazioni o esiti a
    liquidazione. Smentita dal conteggio.

**Ipotesi completa.** DYDXUSDT, ritorno dopo movimento forte con volume alto, candele da 1 ora (le
liquidazioni a catena si vedono su ore), tenuta 12 barre, stop 2 ATR(14).

**Varianti.**
* `I05_long` — long se il rendimento close su close della barra è sotto −2 × ATR(14) della barra prima
  diviso il suo close, e il volume in USDT della barra supera 3 volte la media delle 24 barre precedenti.
* `I05_short` — short con rendimento sopra +2 ATR relativi e lo stesso volume; speculare.

---

## I-06 — Funding affollato

**Fonte.** Maik Schmeling, Andreas Schrimpf e Karamfil Todorov, «Crypto Carry», BIS Working Papers
n. 1087, aprile 2023 (il carry dei futures crypto è alto quando domina la domanda di leva degli
investitori che inseguono il prezzo; un carry alto annuncia liquidazioni e cadute).

**Affermazione verificabile.** Quando il funding regolato di DYDX è almeno 0,03% per 8 ore (tre volte il
livello base dello 0,01%), il prezzo nelle 24 ore seguenti scende in media più che dopo un ingresso
casuale; quando è −0,03% o meno, sale di più (posizioni corte affollate). Falsificata se la variante non
batte nettamente la (a) e la (b).

**Sotto-domande.** Vale con funding alto in trend forte o solo in laterale? Chi opera: chi è a leva
dalla parte affollata e paga il funding; chi incassa. Perché il prezzo dovrebbe muoversi contro la
folla: chiusure delle posizioni costose e liquidazioni. Quando: tra un settlement e i successivi.

**Spiegazioni concorrenti.**
1. Effetto casuale. → `t` vicino a 0.
2. Il funding alto segue il trend e il trend continua (momento). → Short dopo funding alto perde.
3. Trend di fondo. → Variante come la (b) della sua direzione.
4. È solo il mercato: il funding di DYDX è alto quando lo è su tutto il crypto. → (si guarda
   BTC nei fallimenti).
5. Il guadagno viene dal funding incassato, non dal prezzo. → `funding_totale` negativo grande e
   movimento di prezzo nullo. Si dichiara.
6. Pochi episodi (il funding estremo è raro). → Pochi trade; la stima dei trade decide.
7. Volatilità: funding estremo in giorni di grande volatilità, stop frequenti.
8. Un solo episodio lungo (settimane di funding alto). → Trade a grappolo, blocco lungo.
9. Artefatto: tassi sporadici errati nella fonte. → Da guardare nei trade.
10. Costi: con candele a 8 ore e stop a 2 ATR i costi in R sono piccoli; non è costi.
11. Il cambio di intervallo del funding (se avviene) cambia la scala del tasso. → Da controllare in
    Fase 0.

**Ipotesi completa.** DYDXUSDT, funding affollato, candele da 8 ore (allineate ai settlement delle 00,
08 e 16 UTC), tenuta 3 barre (24 ore), stop 2 ATR(14).

**Varianti.**
* `I06_short` — short se l'ultimo funding regolato entro la chiusura della barra è ≥ 0,0003.
* `I06_long` — long se è ≤ −0,0003.

---

## I-07 — Il lunedì

**Fonte.** Guglielmo Maria Caporale e Alex Plastun, «The day of the week effect in the cryptocurrency
market», Finance Research Letters 31, 2019 (rendimenti anomali positivi di Bitcoin il lunedì).

**Affermazione verificabile.** La candela giornaliera del lunedì (UTC) di DYDX ha in media un
rendimento più alto di una giornata presa a caso. Falsificata se il long del lunedì non batte nettamente
la (a) e la (b).

**Sotto-domande.** Vale nelle settimane volatili o calme? Chi opera il lunedì: il ritorno degli
operatori istituzionali e dei mercati tradizionali dopo il fine settimana, a volume basso. Perché
dovrebbe salire: flussi in entrata concentrati a inizio settimana. Quando: nel giorno.

**Spiegazioni concorrenti.**
1. Effetto casuale (con 7 giorni da scegliere, uno esce per caso). → `t` vicino a 0. La fonte stessa
   prova più giorni: rischio di scelta a posteriori nella fonte.
2. Trend di fondo. → Long del lunedì come la (b) long.
3. È solo il mercato: il lunedì di BTC. → (si dichiara).
4. Volatilità del lunedì più alta (riapertura dei mercati tradizionali): stop frequenti.
5. Costi: un trade al giorno con stop larghi, costi piccoli in R.
6. Funding: il lunedì cade su tre settlement come gli altri giorni; non è funding.
7. Pochi lunedì estremi. → Senza i 3 migliori crolla.
8. Un solo anno. → Vantaggio solo nel 2021.
9. Effetto del fine settimana: il rendimento anomalo è la domenica sera (fine della candela della
   domenica) e non il lunedì. → Da guardare nei fallimenti.
10. Artefatto: manutenzioni di Binance concentrate in certi giorni.
11. Rumore di un effetto pubblicato sui dati di altri anni (2013-2017): l'effetto può non esistere più
    dopo la pubblicazione.

**Ipotesi completa.** DYDXUSDT, lunedì, candele giornaliere, long dall'apertura alla chiusura del lunedì
UTC, stop 2 ATR(14).

**Varianti.**
* `I07_long` — long all'apertura del lunedì (segnale alla chiusura della candela della domenica), uscita
  dopo 1 barra. Una sola variante: la fonte non dà una direzione short.

---

## I-08 — BTC guida, DYDX segue

**Fonte.** Andrew W. Lo e A. Craig MacKinlay, «When Are Contrarian Profits Due to Stock Market
Overreaction?», The Review of Financial Studies 3(2), 1990 (i rendimenti dei titoli grandi precedono
quelli dei titoli piccoli: correlazione incrociata ritardata).

**Affermazione verificabile.** In un'ora in cui BTC sale più di 2 deviazioni standard dei suoi rendimenti
orari dell'ultima settimana e DYDX sale meno di BTC, le 3 ore seguenti di DYDX salgono più di un ingresso
casuale; speculare in discesa. Falsificata se la variante non batte nettamente la (a) e la (b).

**Sotto-domande.** Vale per movimenti di BTC grandi o anche medi? Chi opera: l'informazione di mercato
arriva prima su BTC (più liquido, più seguito), gli operatori sulle monete minori si adeguano con
ritardo; gli arbitraggi fra monete. Quando: entro poche ore.

**Spiegazioni concorrenti.**
1. Effetto casuale. → `t` vicino a 0.
2. Il ritardo è solo rumore di microstruttura (prezzi vecchi su DYDX nell'ultima barra), che a 1 ora
   è già sparito. → Nessun vantaggio dopo la prima barra.
3. Trend di fondo. → Come la (b) della direzione.
4. È solo il mercato: è il momento di BTC (BTC continua e DYDX lo segue con beta). → Il vantaggio
   c'è anche senza la condizione «DYDX ha seguito meno»: si dichiara, non si separa.
5. Il ritardo di DYDX è informazione propria (notizie negative su DYDX) e non si chiude. → R sotto la
   (b).
6. Volatilità: ore di BTC estreme sono ore di DYDX estreme, stop frequenti.
7. Costi: tenuta 3 ore, stop a 2 ATR orari; i costi pesano.
8. Pochi episodi estremi.
9. Un solo anno.
10. Artefatto: barre di BTC mancanti o disallineate. → Le ore senza BTC sono escluse.
11. Ritorno verso la media di BTC dopo movimenti forti: DYDX segue il ritorno. → R sotto la (b).

**Ipotesi completa.** DYDXUSDT, correlazione ritardata con BTC, candele da 1 ora, tenuta 3 barre, stop
2 ATR(14). Deviazione standard di BTC sulle 168 ore precedenti (almeno 100 valori).

**Varianti.**
* `I08_long` — long se il rendimento orario di BTC supera 2 deviazioni standard e quello di DYDX nella
  stessa ora è minore di quello di BTC.
* `I08_short` — short se il rendimento di BTC è sotto −2 deviazioni standard e quello di DYDX è maggiore.

---

## I-09 — Numeri tondi

**Fonte.** Carol L. Osler, «Currency Orders and Exchange Rate Dynamics: An Explanation for the Predictive
Success of Technical Analysis», The Journal of Finance 58(5), ottobre 2003 (gli ordini stop si
concentrano subito oltre i numeri tondi: quando il prezzo li attraversa il movimento accelera).

**Affermazione verificabile.** Quando il close orario attraversa al rialzo un numero tondo (multipli di
0,5 USDT sotto 10, multipli di 5 da 10 in su), le 4 ore seguenti salgono più di un ingresso casuale;
speculare al ribasso. Falsificata se la variante non batte nettamente la (a) e la (b).

**Sotto-domande.** Vale per tutti i numeri tondi o solo per quelli «interi»? Chi opera: chi ha ordini
stop e prese di profitto messi sui numeri tondi (persone, non algoritmi). Perché dovrebbe muovere il
prezzo: gli stop eseguiti a catena dopo l'attraversamento. Quando: subito dopo.

**Spiegazioni concorrenti.**
1. Effetto casuale. → `t` vicino a 0.
2. Le prese di profitto sui numeri tondi (la stessa fonte): il prezzo rimbalza invece di proseguire.
   → R sotto la (b).
3. Trend di fondo. → Come la (b).
4. È solo il mercato. → (si dichiara).
5. La griglia (0,5 e 5) non è quella che usano gli operatori di DYDX. → Nessun effetto.
6. Volatilità: gli attraversamenti avvengono in ore volatili.
7. Costi: tenuta 4 ore, stop a 2 ATR orari.
8. Pochi episodi estremi.
9. Un solo anno (il 2021 con prezzi sopra 10 e la griglia larga).
10. Artefatto: attraversamenti avanti e indietro nella stessa zona (laterale) gonfiano i trade.
11. È momento di breve: ogni movimento orario forte prosegue, tondo o no. → La (a) non lo
    distingue; la (b) entra a caso.

**Ipotesi completa.** DYDXUSDT, numeri tondi, candele da 1 ora, tenuta 4 barre, stop 2 ATR(14).

**Varianti.**
* `I09_long` — long se close(i−1) < L ≤ close(i) per un numero tondo L.
* `I09_short` — short se close(i−1) > L ≥ close(i).

---

## I-10 — Barra stretta e rottura

**Fonte.** Toby Crabel, «Day Trading with Short Term Price Patterns and Opening Range Breakout», Traders
Press, 1990 (la barra più stretta delle ultime 7, «NR7», precede un'espansione dell'intervallo; si opera
nella direzione della rottura).

**Affermazione verificabile.** Dopo una barra da 4 ore che ha l'intervallo high-low più stretto delle
ultime 7, se la barra seguente chiude oltre il suo massimo, le 6 barre seguenti salgono più di un ingresso
casuale (stop al minimo della barra stretta); speculare al ribasso. Falsificata se la variante non batte
nettamente la (a) e la (b).

**Sotto-domande.** Vale in trend o in laterale? Chi opera: dopo una fase di compressione, i
partecipanti che aspettavano la direzione entrano insieme. Perché: la volatilità si raggruppa e si
alterna (compressione → espansione). Quando: nelle barre successive.

**Spiegazioni concorrenti.**
1. Effetto casuale. → `t` vicino a 0.
2. L'espansione c'è ma la direzione no: la rottura del primo lato non dice dove andrà. → R vicino alla
   (b).
3. Trend di fondo. → Come la (b).
4. È solo il mercato.
5. Lo stop stretto (al minimo della barra stretta) fa crescere i costi in R. → R netto negativo per
   costi.
6. Lo stop stretto scatta spesso per rumore. → Molti stop, pochi esiti a tempo.
7. Pochi episodi estremi.
8. Un solo anno.
9. Artefatto: barre strette per buchi di dati o manutenzioni (volume quasi zero). → Da guardare.
10. Le barre strette notturne (Asia) hanno un comportamento diverso: stagionalità oraria.
11. È la rottura di un canale corto (I-02 a scala più breve). → Si dichiara.

**Ipotesi completa.** DYDXUSDT, compressione e rottura, candele da 4 ore, tenuta 6 barre, stop al
lato opposto della barra stretta.

**Varianti.**
* `I10_long` — barra i−1 la più stretta delle ultime 7 (intervallo strettamente minore delle 6
  precedenti) e close(i) > high(i−1); stop = low(i−1).
* `I10_short` — stessa barra stretta e close(i) < low(i−1); stop = high(i−1).

---

## I-11 — Squilibrio degli ordini dei taker

**Fonte.** Tarun Chordia e Avanidhar Subrahmanyam, «Order Imbalance and Individual Stock Returns:
Theory and Evidence», Journal of Financial Economics 72(3), 2004 (lo squilibrio fra acquisti e vendite
aggressive di un giorno predice con lo stesso segno il rendimento del giorno dopo, perché gli ordini
grandi si spezzano su più giorni).

**Affermazione verificabile.** Se nella candela giornaliera la quota del volume in USDT comprata dai
taker supera il 50%, il giorno dopo il prezzo sale più di un giorno preso a caso; se è sotto il 50%,
scende di più. Falsificata se la variante non batte nettamente la (a) e la (b).

**Sotto-domande.** Vale con squilibri grandi o anche piccoli? Chi opera: chi esegue un ordine grande a
pezzi, con ordini a mercato. Perché: la domanda non ancora eseguita continua il giorno dopo. Quando: il
giorno dopo.

**Spiegazioni concorrenti.**
1. Effetto casuale. → `t` vicino a 0.
2. Lo squilibrio è solo l'effetto del movimento del giorno (si compra a mercato quando sale): è momento
   di un giorno. → Il vantaggio coincide con quello del rendimento del giorno. Si dichiara.
3. Trend di fondo. → Come la (b).
4. È solo il mercato.
5. Ritorno verso la media: lo squilibrio del giorno spinge il prezzo troppo, il giorno dopo torna. → R
   sotto la (b).
6. Volatilità: squilibri forti in giorni volatili.
7. Costi: stop larghi su candele giornaliere, costi piccoli in R; non è costi.
8. Pochi giorni estremi.
9. Un solo anno.
10. Artefatto: la colonna dei taker nei file vecchi potrebbe mancare o essere diversa. → Controllo
    dei valori mancanti.
11. I market maker dei perpetui equilibrano il flusso: la quota resta vicina al 50% e il segno è rumore.

**Ipotesi completa.** DYDXUSDT, squilibrio dei taker, candele giornaliere, tenuta 1 barra, stop 2
ATR(14).

**Varianti.**
* `I11_long` — long se la quota comprata dai taker nella barra è sopra 0,5.
* `I11_short` — short se è sotto 0,5.

---

## Varianti aggiunte il 2026-10-09 alle 17:47 UTC, dopo gli scarti e prima di ogni test di queste idee

Regola 6: allentare le soglie di uno scarto per raggiungere i trade minimi, senza aver visto risultati,
è ancora una variante dell'idea nuova. Le idee I-02, I-05 e I-06 hanno avuto solo scarti (conteggi
40/54, 57/65, 30/61; voci S001-S006): nessun loro risultato è stato visto. Le spiegazioni concorrenti
restano quelle scritte sopra.

### I-02 (rottura del canale) — su candele da 1 ora

Motivo: sulle 4 ore le rotture di 50 barre sono 40 e 54. Si tiene il parametro della fonte (50 barre,
tenuta 10 barre) e si scende a 1 ora: 50 ore sono circa due giorni di livelli visibili; il meccanismo
(ordini concentrati oltre il massimo o il minimo recente) vale a ogni scala in cui i livelli sono visibili.
Stop 2 ATR(14) orario (circa il 4%, eseguibile dal bot).

* `I02h_long` — long se close > massimo degli high delle 50 barre orarie precedenti; uscita dopo 10 barre.
* `I02h_short` — short se close < minimo dei low delle 50 barre precedenti; speculare.

### I-05 (ritorno dopo movimento forte con volume alto) — soglie più larghe

Motivo: con −2 ATR e volume 3 volte la media gli eventi sono 57 e 65. Si allarga a 1,5 ATR e volume 2
volte la media delle 24 ore: resta un movimento fuori dal normale con partecipazione insolita (la
condizione di Campbell, Grossman e Wang), meno estremo.

* `I05b_long` — rendimento della barra < −1,5 × ATR(14)/close della barra prima e volume > 2 × media 24
  barre; long, uscita dopo 12 barre, stop 2 ATR.
* `I05b_short` — rendimento > +1,5 ATR relativi e lo stesso volume; short; speculare.

### I-06 (funding affollato) — soglia al livello base

Motivo: a ±0,03% i casi sono 30 e 61. La soglia si porta ai confini naturali del meccanismo del
funding di Binance: sopra lo 0,01% (il livello del solo tasso d'interesse) il premio del perpetuo è
positivo, cioè i long pagano più del livello base; sotto zero gli short pagano i long. Meno estremo, ma è
ancora «la folla paga per stare da quella parte».

* `I06b_short` — short se l'ultimo funding regolato è > 0,0001; 8h, uscita dopo 3 barre, stop 2 ATR.
* `I06b_long` — long se è < 0; speculare.

---

## I-12 — Il perpetuo caro o economico rispetto al mark

**Fonte.** Songrun He, Asaf Manela, Omri Ross e Victor von Wachter, «Fundamentals of Perpetual
Futures», arXiv 2212.06888, dicembre 2022 (lo scarto fra prezzo del perpetuo e prezzo a pronti è grande,
cambia nel tempo e si richiude: il funding e l'arbitraggio lo spingono verso zero).

**Affermazione verificabile.** Il mark price di Binance segue il prezzo dell'indice a pronti (con una media
del premio): quando il close del last è molto sopra il close del mark rispetto al solito (scarto relativo
oltre 2 deviazioni standard della sua media delle 168 ore precedenti), nelle 4 ore seguenti il last scende
più di un ingresso casuale, perché il perpetuo torna verso il prezzo a pronti; speculare quando è molto
sotto. Falsificata se la variante non batte nettamente la (a) e la (b).

**Sotto-domande.** Lo scarto si richiude muovendo il perpetuo o muovendo il pronti verso il perpetuo (in
quel caso non c'è nulla da guadagnare in direzione)? Vale con scarti grandi in giorni volatili? Chi
opera: gli arbitraggisti fra pronti e perpetuo, chi incassa il funding; chi ha spinto il perpetuo con la
leva. Quando: in ore (il funding si regola ogni 8 ore).

**Spiegazioni concorrenti.**
1. Effetto casuale. → `t` vicino a 0.
2. Lo scarto si richiude dal lato del pronti (il perpetuo guida la scoperta del prezzo): il last
   prosegue nella direzione del premio. → R sotto la (b).
3. Lo scarto last-mark è rumore di microstruttura alla chiusura della barra (un solo scambio), senza
   contenuto. → Nessun vantaggio.
4. È momento di breve: il last è sopra il mark perché è appena salito (il mark segue con ritardo per
   la media del premio). → Il segnale coincide con «la barra è salita molto»; il risultato è quello di un
   ritorno verso la media di un'ora.
5. Trend di fondo. → Come la (b) della direzione.
6. È solo il mercato. → (si dichiara).
7. Costi: tenuta 4 ore, stop 2 ATR orari (costo circa 0,03 R).
8. Pochi episodi estremi.
9. Un solo anno.
10. Artefatto: barre del mark mancanti o ricostruite (le due giornate tolte; il mark che parte prima del
    last). → Da guardare.
11. Il premio è alto per settimane (regime) e lo z-score a 168 ore lo segue in ritardo.

**Ipotesi completa.** DYDXUSDT, scarto del perpetuo dal mark, candele da 1 ora, tenuta 4 barre, stop 2
ATR(14). Scarto = close del last / close del mark − 1; z = (scarto − media delle 168 barre precedenti) /
deviazione standard delle 168 barre precedenti.

**Varianti.**
* `I12_short` — short se z > 2.
* `I12_long` — long se z < −2.
