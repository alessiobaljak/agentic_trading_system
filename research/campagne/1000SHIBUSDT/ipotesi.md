# Ipotesi della campagna 1000SHIBUSDT

Ogni idea è scritta qui PRIMA del suo primo test (Fase 1 e regola 6). Le varianti di
ogni idea sono tutte elencate prima del primo test di quell'idea, ognuna con il suo
motivo. Gli `id` del log si assegnano alla registrazione: qui le varianti hanno un nome
(es. «I-01 a») che la registrazione richiama.

Fonti: solo pubblicazioni anteriori al 2024-01-01 (titolo, autore, data). Nessun
risultato del gate, del registro, del paper del bot o di altre monete.

Periodo di costruzione: 2021-05-01 → 2023-03-13 (682 giorni; log, nota N003).
Costi: commissione 0,05% per lato + slippage 0,02% per lato = 0,14% del nozionale per
un giro completo, più il funding. In R il costo di un giro è 0,14% / distanza dello stop
in percentuale (per esempio 0,047 R con uno stop al 3%).

Regole comuni a tutte le varianti (scritte prima del primo test):

* segnali sulla chiusura della barra, ingresso all'apertura della barra dopo (motore);
* nessun ingresso su segnali di barre dei mesi sotto 20 milioni di USDT al giorno
  (filtro della Fase 0, `fase0_dati.md`), uguale per conteggio, test e baseline (a);
* stop calcolato sulla chiusura della barra di segnale; il motore lo rifiuta se
  l'apertura successiva è già oltre (segnale non valido);
* «ATR» è l'ATR di Wilder a 14 barre del timeframe della variante, se non detto altro;
* **tetto dello stop:** uno stop scritto «k ATR» è k ATR dalla chiusura, ma mai più lontano
  del 6% della chiusura (`stop_massimo_bot` di parametri.yaml: oltre, il bot non può
  eseguire il trade). Aggiunto prima di qualunque test di un'idea, dopo aver letto in Fase 0
  l'ATR mediano per timeframe (4h: 3,0%; 1d: 8,0%): senza tetto gli stop a 3 ATR su 4 ore
  (circa 9%) e a 2 ATR su 1 giorno (circa 16%) renderebbero il candidato non eseguibile dal
  bot. Il tetto vale anche per la (a) e la (b), che usano lo stesso calcolo del segnale;
* «σ a N barre» è la deviazione standard dei rendimenti di chiusura delle N barre
  precedenti, esclusa la barra di segnale.

## Le spiegazioni noiose, comuni a tutte le idee

Ogni idea qui sotto ripete per sé almeno dieci spiegazioni concorrenti. Sei sono sempre
le stesse; per non riscriverle uguali, qui c'è la loro forma generale, e in ogni idea
c'è la previsione specifica.

* **N1 Effetto casuale.** Prevede: R medio entro il rumore della (b) (`t` contro la (b)
  sotto la soglia), percentile fra le simulazioni non estremo. Smentita: battere
  nettamente la (b).
* **N2 Volatilità.** La condizione sceglie barre di volatilità alta o bassa; con stop in
  ATR e uscita a tempo l'R dipende dalla volatilità dopo l'ingresso. Prevede: la (b),
  che entra dove il segnale è valido con lo stesso calcolo dello stop, dà lo stesso R;
  l'effetto sparisce confrontando con la (b). Smentita: netta contro la (b).
* **N3 Trend di fondo.** Nel periodo di costruzione 1000SHIBUSDT è salita molto nel 2021
  e scesa nel 2022: una variante long o short può guadagnare solo per la direzione.
  Prevede: la (a) e la (b), nella stessa direzione, guadagnano quanto il candidato;
  l'R per anno segue il buy and hold. Smentita: netta contro la (a) e la (b), e R
  positivo anche nell'anno in cui il buy and hold della stessa direzione perde.
* **N4 Artefatto dei dati.** Buchi del mark, barre tolte dall'allineamento, candele
  anomale (prezzi errati) creano segnali falsi. Prevede: i trade migliori cadono vicino
  ai buchi o su candele anomale; togliendo i 3 migliori l'R crolla. Smentita: R senza i
  3 migliori ancora sopra la (b) e nessun legame con i buchi (`fase0_dati.md`).
* **N5 Effetto costi.** Il vantaggio lordo esiste ma i costi lo mangiano (soprattutto
  sulle candele corte). Prevede: R medio lordo positivo, netto non positivo. Smentita:
  R netto positivo, e a costi doppi ancora sopra la (b) (Fase 4).
* **N6 È solo il mercato.** 1000SHIBUSDT segue BTC: il segnale è un modo indiretto di
  stare long o short sul mercato crypto quando sale o scende. Prevede: lo stesso
  segnale calcolato su BTCUSDT dà trade nello stesso verso nelle stesse barre, e il
  rendimento di BTC durante i trade spiega quello della moneta. Smentita: R positivo
  anche nei trade in cui BTC va contro, o differenza fra moneta e BTC positiva.

---

## Controllo positivo degli strumenti (non è un'idea, non consuma budget)

Strategia che legge DI PROPOSITO la barra successiva (lookahead dichiarato): alla
chiusura della barra i entra long se la barra i + 1 chiuderà sopra la sua apertura;
stop a 2 ATR sotto la chiusura della barra i; esce con «chiudi» alla chiusura della
barra d'ingresso (cioè all'apertura della barra i + 2). Timeframe 4h, solo long. Deve
battere nettamente la (b) (che entra a caso con la stessa uscita) e crollare con il
ritardo di una barra (con il ritardo l'ingresso cade nella barra i + 2, che la
strategia non conosce). Si registra come nota prima e dopo (lezioni/metodo.md).

---

## I-01 Momento della serie (time-series momentum)

1. **Fonte.** Tobias J. Moskowitz, Yao Hua Ooi, Lasse Heje Pedersen, «Time Series
   Momentum», Journal of Financial Economics 104(2), maggio 2012. Per le crypto: Yukun
   Liu, Aleh Tsyvinski, «Risks and Returns of Cryptocurrency», NBER Working Paper 24877,
   agosto 2018 (poi Review of Financial Studies 2021): il rendimento della settimana
   passata predice quello delle settimane successive.
2. **Affermazione verificabile.** Su 1000SHIBUSDT, se il rendimento degli ultimi 7
   giorni è positivo, il rendimento dei 3 giorni successivi è in media più alto di quello
   di un ingresso a caso nella stessa direzione con la stessa uscita (e viceversa per gli
   short). Falsificabile: R medio non sopra la (b).
3. **Sotto-domande.** Vale di più dopo movimenti grandi (oltre 20% in 7 giorni) che dopo
   quelli piccoli? Dipende dalla volatilità (in alta volatilità il momento si inverte
   più spesso)? Chi opera: investitori al dettaglio che inseguono il prezzo (attenzione,
   paura di restare fuori) e fondi di tendenza; la sotto-reazione lenta alle notizie e il
   gregge spingono nella stessa direzione per giorni. Tempo: l'effetto nella fonte è
   settimanale, quindi si guarda un orizzonte di giorni, non di ore.
4. **Spiegazioni concorrenti (11).** N1-N6 come sopra; in più: N7 *momento solo del
   2021*: l'effetto esiste solo nella fase di mania (maggio-ottobre 2021) e non dopo;
   N8 *code*: pochi rialzi enormi (ottobre 2021) fanno tutto; N9 *funding*: i long nei
   rialzi pagano funding alto che mangia il vantaggio; N10 *rimbalzo dopo i crolli*: gli
   short dopo 7 giorni negativi perdono perché i crolli rimbalzano (inversione a breve);
   N11 *sovrapposizione dei segnali*: lo stesso movimento produce trade consecutivi, che
   non sono indipendenti (lo copre il blocco del bootstrap).
5. **Previsioni e smentite.** N3: R per anno del long positivo solo nel 2021 (smentita:
   positivo anche nel 2022); N6: lo stesso segnale su BTC indica la stessa direzione nella
   maggior parte dei trade (smentita: differenza positiva rispetto a BTC); N7: R medio
   2021 alto, 2022-2023 nullo; N8: R senza i 3 migliori sotto la (b); N9: funding medio
   per trade oltre 0,05 R; N10: per lo short R medio negativo con molte uscite a stop;
   N1, N2, N4, N5, N11: come nella sezione comune.
6. **Ipotesi completa e varianti.** Timeframe 4h: il segnale è settimanale e l'uscita è
   di giorni; 4 ore danno ingressi abbastanza fitti senza scendere nel rumore delle ore.
   * **I-01 a, long.** Condizione: chiusura / chiusura di 42 barre prima − 1 > 0.
     Uscita: «chiudi» dopo 18 barre (3 giorni). Stop: chiusura − 3 ATR. Nessun target.
     Riscaldamento 42 barre. Motivo dei 3 giorni: la fonte misura il rendimento delle
     settimane dopo; 3 giorni sono la parte più vicina al segnale e permettono più
     trade (con 7 giorni di tenuta al massimo 97 trade in costruzione).
   * **I-01 b, short.** Specchio: rendimento a 42 barre < 0; stop chiusura + 3 ATR; stessa
     uscita. Motivo: la fonte vale nelle due direzioni; nel 2022 il mercato è sceso.

## I-02 Ipereazione a breve e inversione

1. **Fonte.** Narasimhan Jegadeesh, «Evidence of Predictable Behavior of Security
   Returns», Journal of Finance 45(3), luglio 1990; Bruce N. Lehmann, «Fads, Martingales,
   and Market Efficiency», Quarterly Journal of Economics 105(1), febbraio 1990: i
   rendimenti estremi a breve si invertono in parte (pressione di liquidità, reazione
   eccessiva).
2. **Affermazione.** Dopo una barra da 1 ora con rendimento oltre 3 σ (σ a 168 barre),
   le 6 ore seguenti vanno in media nella direzione opposta più di un ingresso casuale
   nella stessa direzione con la stessa uscita.
3. **Sotto-domande.** L'inversione è più forte se il movimento è avvenuto con volume
   alto (liquidazioni forzate) o basso? Nelle ore di poca liquidità (notte asiatica,
   fine settimana)? Chi opera: le liquidazioni a cascata e gli ordini a mercato grandi
   spostano il prezzo oltre il valore; chi fornisce liquidità (market maker, arbitraggisti)
   lo riporta indietro in poche ore, incassando il premio. Tempo: ore.
4. **Spiegazioni concorrenti (11).** N1-N6; N7 *notizia vera*: il salto riflette
   un'informazione nuova e il prezzo continua (momento, non inversione); N8 *rimbalzo
   meccanico bid-ask*: l'inversione è solo il rimbalzo del prezzo fra denaro e lettera,
   più piccolo dei costi; N9 *cascata non finita*: le liquidazioni continuano nella barra
   dopo, lo stop scatta prima del rimbalzo; N10 *salti del mark*: il salto è sul last ma
   non sul mark (artefatto del feed); N11 *grappoli*: i salti arrivano a grappoli negli
   stessi giorni (maggio 2021, novembre 2022), pochi episodi fanno tutto.
5. **Previsioni e smentite.** N7: R negativo e uscite a stop frequenti (smentita: R sopra
   la (b)); N8: R lordo minore del costo di un giro (0,14% del nozionale) (smentita: R
   netto positivo); N9: molti stop nelle prime 2 barre; N10: i trade migliori su barre con
   differenza grande fra last e mark; N11: R per anno concentrato in un anno, senza i 3
   migliori sotto la (b); N3: il long guadagna nel 2021 e perde nel 2022 come la (a); N6:
   gli stessi salti su BTC nella stessa ora.
6. **Ipotesi e varianti.** Timeframe 1h: le liquidazioni a cascata durano minuti o ore; 1
   ora contiene il movimento e lascia il rimbalzo alle ore seguenti.
   * **I-02 a, long dopo un crollo.** Condizione: rendimento della barra < −3 σ a 168
     barre. Uscita: «chiudi» dopo 6 barre. Stop: chiusura − 2,5 ATR. Riscaldamento 168.
   * **I-02 b, short dopo un salto.** Condizione: rendimento > +3 σ. Stop chiusura + 2,5
     ATR; stessa uscita. Motivo: la fonte è simmetrica; sulle meme coin i salti in su sono
     frequenti e la fonte dice che si invertono.

## I-03 Rottura del canale (Donchian)

1. **Fonte.** Curtis M. Faith, «Way of the Turtle», McGraw-Hill, 2007 (le regole del
   «System 1» delle tartarughe di Richard Dennis: rottura del massimo di 20 periodi,
   uscita sul minimo di 10, stop a 2 N con N = ATR a 20).
2. **Affermazione.** Su 1000SHIBUSDT a 4 ore, una chiusura sopra il massimo delle 20
   barre precedenti è seguita da un movimento nella stessa direzione più lungo di quanto
   dia un ingresso a caso con la stessa uscita (uscita sul minimo di 10 barre).
3. **Sotto-domande.** Funziona solo nelle tendenze lunghe (pochi trade grandi, molti
   piccoli persi)? Dopo periodi di compressione? Chi opera: ordini di stop sopra i massimi
   recenti e seguaci di tendenza che entrano sulla rottura; poi il gregge. Tempo: giorni.
4. **Spiegazioni concorrenti (11).** N1-N6; N7 *falsi segnali in laterale*: nel 2022-2023
   il prezzo oscilla e le rotture falliscono; N8 *un solo trend*: ottobre 2021 fa tutto;
   N9 *stop troppo stretti*: 2 N su 4 ore viene preso dal rumore prima della tendenza; N10
   *ritardo dell'ingresso*: entrando all'apertura dopo la rottura si compra già caro; N11
   *liquidazioni degli short sopra i massimi* (squeeze breve, poi inversione).
5. **Previsioni e smentite.** N7: R medio 2022 negativo, vittorie rare; N8: senza i 3
   migliori R sotto la (b); N9: quota di stop alta (oltre 60%); N10: il test con ritardo
   peggiora poco (sarebbe il contrario se l'ingresso contasse); N11: i trade migliori
   durano poche barre; N3, N6 come comune.
6. **Ipotesi e varianti.** Timeframe 4h: è la candela più corta su cui un canale di 20
   barre copre più di 3 giorni, cioè movimenti di tendenza e non di rumore orario; a 1d
   i trade sarebbero troppo pochi in 682 giorni.
   * **I-03 a, long.** Condizione: chiusura > massimo degli high delle 20 barre precedenti.
     Uscita: «chiudi» quando la chiusura < minimo dei low delle 10 barre precedenti. Stop:
     chiusura − 2 ATR a 20 barre. Riscaldamento 21.
   * **I-03 b, short.** Specchio: chiusura < minimo dei low delle 20 precedenti; uscita su
     chiusura > massimo degli high delle 10 precedenti; stop + 2 ATR a 20.

## I-04 Affollamento misurato dal funding

1. **Fonte.** Maik Schmeling, Andreas Schrimpf, Karamfil Todorov, «Crypto Carry», BIS
   Working Papers n. 1087, aprile 2023: un carry (funding, base dei futures) alto segnala
   domanda di leva dei long speculativi e precede rendimenti più bassi e crolli
   (liquidazioni).
2. **Affermazione.** Quando l'ultimo funding a 8 ore di 1000SHIBUSDT è almeno 0,03% (tre
   volte il valore standard dello 0,01%), i 3 giorni seguenti rendono meno di un ingresso
   casuale: uno short guadagna più della (b). Quando il funding è negativo (gli short
   pagano), i 3 giorni seguenti rendono di più: un long guadagna più della (b).
3. **Sotto-domande.** L'effetto vale per livelli estremi o anche moderati? Dura ore o
   giorni? Chi opera: i long a leva al dettaglio pagano per restare esposti; quando il
   prezzo esita, le loro liquidazioni spingono giù. Con funding negativo gli short
   affollati vengono liquidati sui rialzi (squeeze).
4. **Spiegazioni concorrenti (11).** N1-N6; N7 *il funding segue il prezzo*: il funding è
   alto perché il prezzo è salito, e la variante è solo un'inversione dopo un rialzo
   (I-02 travestita); N8 *il funding alto accompagna la mania e la mania continua* (lo
   short perde); N9 *pochi episodi*: tutti i funding alti sono nel 2021, un regime solo;
   N10 *incasso del funding*: lo short guadagna solo il funding incassato, non dal prezzo;
   N11 *funding negativo in un mercato che scende*: il long dopo funding negativo compra
   la caduta del 2022 e perde.
5. **Previsioni e smentite.** N7: il segnale coincide con rendimenti a 7 giorni molto
   positivi (smentita: R sopra la (b), che entra a caso fra le barre valide, e il
   confronto con I-01); N8: lo short perde nel 2021; N9: trade concentrati in pochi mesi
   (smentita: R positivo in più episodi); N10: R lordo di prezzo nullo e funding incassato
   positivo; N11: il long perde nel 2022.
6. **Ipotesi e varianti.** Timeframe 4h: il funding cambia ogni 8 ore e l'effetto nella
   fonte è di giorni; 4 ore permettono di entrare entro metà intervallo.
   * **I-04 a, short con funding alto.** Condizione: ultimo funding noto ≥ 0,0003.
     Uscita dopo 18 barre (3 giorni). Stop chiusura + 3 ATR. Riscaldamento 14.
   * **I-04 b, long con funding negativo.** Condizione: ultimo funding < 0. Uscita dopo 18
     barre. Stop chiusura − 3 ATR.

## I-05 Premio del volume alto

1. **Fonte.** Simon Gervais, Ron Kaniel, Dan H. Mingelgrin, «The High-Volume Return
   Premium», Journal of Finance 56(3), giugno 2001: i titoli con volume insolitamente alto
   in un giorno o una settimana rendono di più nel periodo seguente (la visibilità attira
   nuovi compratori).
2. **Affermazione.** Quando il volume in USDT delle ultime 24 ore supera il doppio della
   media giornaliera dei 50 giorni precedenti, i 3 giorni seguenti rendono più di un
   ingresso long casuale con la stessa uscita.
3. **Sotto-domande.** Vale anche se il giorno di volume alto è stato di ribasso? Chi
   opera: l'attenzione porta nuovi compratori al dettaglio (sulle meme coin l'attenzione
   è il motore del prezzo); i venditori allo scoperto sono vincolati. Tempo: giorni.
4. **Spiegazioni concorrenti (10).** N1-N6; N7 *il volume alto è la cima*: il volume
   esplode al culmine della mania e poi il prezzo crolla (lo dice anche I-06); N8 *volume
   del ribasso*: i giorni di volume alto del 2022 sono vendite forzate (crolli di LUNA, FTX)
   e il long compra prima di altro ribasso; N9 *momento*: il volume alto segue rialzi e il
   vantaggio è il momento (I-01); N10 *volatilità*: dopo il volume alto la volatilità sale e
   con stop in ATR l'R non cambia.
5. **Previsioni e smentite.** N7: R negativo nei trade del 2021; N8: R negativo quando il
   giorno del segnale è di ribasso; N9: R simile a I-01 a negli stessi giorni; N10: R
   entro la (b).
6. **Ipotesi e varianti.** Timeframe 4h (finestra di 24 ore = 6 barre, media su 300 barre).
   * **I-05 a, long.** Condizione: somma del volume in USDT delle ultime 6 barre ≥ 2 × (somma
     del volume delle 300 barre precedenti / 50). Uscita dopo 18 barre. Stop chiusura − 3
     ATR. Riscaldamento 306. Una sola variante: la fonte predice solo un rialzo.

## I-06 Gonfia e sgonfia (pump-and-dump)

1. **Fonte.** Josh Kamps, Bennett Kleinberg, «To the moon: defining and detecting
   cryptocurrency pump-and-dumps», Crime Science 7, 2018; Tao Li, Donghwa Shin, Baolian
   Wang, «Cryptocurrency Pump-and-Dump Schemes», SSRN, 2018: i rialzi improvvisi con
   volume anomalo sono spesso gonfiati e il prezzo torna indietro nelle ore dopo.
2. **Affermazione.** Dopo una barra da 15 minuti con rendimento ≥ +4% e volume in USDT ≥ 5
   volte la media delle 96 barre precedenti (24 ore), le 4 ore seguenti scendono più di un
   ingresso short casuale con la stessa uscita.
3. **Sotto-domande.** Dipende dall'ora (i gruppi organizzati scelgono orari fissi)? Dalla
   grandezza del salto? Chi opera: chi ha organizzato il rialzo vende ai ritardatari; il
   prezzo torna dove era. Tempo: minuti-ore.
4. **Spiegazioni concorrenti (10).** N1-N6; N7 *notizie vere* (quotazioni, annunci di
   Elon Musk, nuove borse): il prezzo non torna; N8 *squeeze degli short*: il salto è una
   liquidazione degli short e continua; N9 *grappoli di mania*: tutti i segnali nel maggio
   e ottobre 2021; N10 *è I-02 b*: il volume non aggiunge nulla al salto da solo.
5. **Previsioni e smentite.** N7, N8: R negativo con stop frequenti; N9: R per mese
   concentrato; N10: confronto con I-02 b (stessa direzione, candele diverse).
6. **Ipotesi e varianti.** Timeframe 15m: un gonfia-e-sgonfia dura minuti; a 1 ora il
   salto e la discesa finirebbero nella stessa barra.
   * **I-06 a, short.** Condizione sopra. Uscita dopo 16 barre (4 ore). Stop chiusura + 2
     ATR. Riscaldamento 96. Una sola variante: la fonte descrive solo la discesa dopo il
     salto.

## I-07 Effetto del lunedì

1. **Fonte.** Guglielmo Maria Caporale, Alex Plastun, «The day of the week effect in the
   cryptocurrency market», Finance Research Letters 31, dicembre 2019: per bitcoin
   rendimenti anormalmente alti il lunedì.
2. **Affermazione.** Su 1000SHIBUSDT un long tenuto dal lunedì 00:00 UTC al martedì 00:00
   UTC rende più di un long casuale di un giorno.
3. **Sotto-domande.** Vale nei periodi di ribasso? Dipende dal fine settimana precedente?
   Chi opera: il ritorno degli operatori istituzionali e dei flussi dei giorni lavorativi
   dopo il fine settimana più sottile.
4. **Spiegazioni concorrenti (10).** N1-N6; N7 *data mining della fonte*: con 7 giorni e
   molte monete un giorno risulta per caso (previsione: niente effetto); N8 *è un effetto
   di bitcoin*: se c'è, SHIB lo ha tramite BTC (N6); N9 *volatilità del lunedì*: il lunedì
   è più volatile e con stop in ATR l'R non cambia; N10 *gap del fine settimana*: il
   movimento del lunedì inverte quello del fine settimana (inversione, non giorno).
5. **Previsioni e smentite.** N7: R entro la (b); N8: BTC il lunedì ha lo stesso segno nei
   trade migliori; N9: R entro la (b); N10: R correlato negativamente al rendimento del
   fine settimana.
6. **Ipotesi e varianti.** Timeframe 1d: l'effetto è sul giorno intero.
   * **I-07 a, long.** Condizione: la barra di segnale è la domenica (UTC). Uscita: «chiudi»
     dopo 1 barra. Stop chiusura − 2 ATR (giornaliero). Riscaldamento 14. Una sola
     variante: la fonte riporta l'anomalia del lunedì in su.

## I-08 Momento interno al giorno

1. **Fonte.** Lei Gao, Yufeng Han, Sophia Zhengzi Li, Guofu Zhou, «Market intraday
   momentum», Journal of Financial Economics 129(2), agosto 2018; per bitcoin: Dehua Shen,
   Andrew Urquhart, Pengfei Wang, «Bitcoin intraday time series momentum», The Financial
   Review 57(2), 2022: il rendimento della prima mezz'ora predice quello dell'ultima.
2. **Affermazione.** Il segno del rendimento della prima mezz'ora del giorno UTC (00:00-00:30)
   predice il segno del rendimento dell'ultima mezz'ora (23:30-24:00) dello stesso giorno.
3. **Sotto-domande.** Più forte nei giorni di volatilità alta? Chi opera: ribilanciamenti e
   coperture di fine giornata (per le crypto la chiusura UTC è quella dei contratti e
   degli indici giornalieri), informati che entrano presto e ritardatari che seguono.
4. **Spiegazioni concorrenti (10).** N1-N6; N7 *costi*: il movimento di mezz'ora è dello
   stesso ordine dei costi (sezione 11, costi a orizzonte corto); N8 *funding a mezzanotte*:
   il settlement delle 00:00 sposta il prezzo nell'ultima mezz'ora indipendentemente dalla
   prima; N9 *è il trend*: nei giorni in rialzo entrambe le mezz'ore salgono; N10 *bitcoin*:
   l'effetto è di BTC e passa a SHIB.
5. **Previsioni e smentite.** N7: R lordo positivo ma netto negativo; N8: l'ultima mezz'ora
   ha un rendimento medio di segno fisso (indipendente dalla prima); N9: R positivo solo
   nei giorni di trend forte; N10: BTC stesso segno.
6. **Ipotesi e varianti.** Timeframe 30m, come la fonte.
   * **I-08 a, long.** Condizione: barra di segnale = 23:00-23:30 UTC e rendimento della barra
     00:00-00:30 dello stesso giorno > 0. Ingresso 23:30, «chiudi» dopo 1 barra. Stop
     chiusura − 2 ATR (30m). Riscaldamento 48.
   * **I-08 b, short.** Rendimento della prima mezz'ora < 0; stop + 2 ATR. Stessa uscita.

## I-09 Bitcoin guida, la moneta segue

1. **Fonte.** Andrew W. Lo, A. Craig MacKinlay, «When Are Contrarian Profits Due to Stock
   Market Overreaction?», Review of Financial Studies 3(2), 1990 (i titoli grandi guidano i
   piccoli: gli ultimi incorporano le notizie di mercato con ritardo); per le crypto: Pavel
   Ciaian, Miroslava Rajcaniova, d'Artis Kancs, «Virtual relationships: Short- and long-run
   evidence from BitCoin and altcoin markets», Journal of International Financial Markets,
   Institutions and Money 52, 2018.
2. **Affermazione.** Dopo un'ora in cui BTC sale più di 2 σ (σ di BTC a 168 ore) e
   1000SHIBUSDT sale meno di BTC, nelle 3 ore seguenti 1000SHIBUSDT sale più di un long
   casuale con la stessa uscita (recupera il ritardo); specularmente in discesa.
3. **Sotto-domande.** Il ritardo è maggiore di notte o nel fine settimana (meno arbitraggisti)?
   Chi opera: gli arbitraggisti fra monete e i market maker aggiornano prima BTC, la liquidità
   delle monete piccole reagisce dopo.
4. **Spiegazioni concorrenti (10).** N1-N6 (N6 qui è il meccanismo stesso: va distinto dal
   semplice «BTC continua», che si controlla con il rendimento di BTC nelle 3 ore dopo); N7
   *momento di BTC*: BTC stesso continua e SHIB lo segue (allora il vantaggio è il momento di
   BTC, non il ritardo); N8 *divergenza vera*: SHIB resta indietro per motivi suoi e non
   recupera; N9 *costi*: il recupero è più piccolo del giro di costi; N10 *rumore di
   misura*: con candele orarie la differenza di 1 ora è soprattutto rumore.
5. **Previsioni e smentite.** N7: BTC nelle 3 ore dopo va nella stessa direzione quanto SHIB;
   N8: R negativo; N9: R lordo < costo; N10: R entro la (b).
6. **Ipotesi e varianti.** Timeframe 1h.
   * **I-09 a, long.** Condizione: rendimento di BTC nella barra > 2 σ_BTC(168) e rendimento
     di SHIB nella barra < rendimento di BTC. Uscita dopo 3 barre. Stop chiusura − 2,5 ATR.
     Riscaldamento 168.
   * **I-09 b, short.** Specchio: BTC < −2 σ e SHIB > rendimento di BTC; stop + 2,5 ATR.

## I-10 Compressione della volatilità e rottura delle bande

1. **Fonte.** John Bollinger, «Bollinger on Bollinger Bands», McGraw-Hill, 2001 (la
   «squeeze»: un'ampiezza delle bande ai minimi precede un'espansione, e la direzione è
   quella della prima chiusura fuori dalle bande).
2. **Affermazione.** Su 4 ore, dopo che l'ampiezza delle bande (4 σ / media, 20 barre) ha
   toccato il minimo delle 120 barre precedenti nelle ultime 6 barre, una chiusura sopra la
   banda alta è seguita da un rialzo più ampio di quanto dia un ingresso a caso.
3. **Sotto-domande.** Le compressioni lunghe danno rotture migliori? Chi opera: dopo un
   periodo quieto gli stop si accumulano vicini; la rottura li fa scattare a cascata.
4. **Spiegazioni concorrenti (10).** N1-N6; N7 *rotture false* in laterale; N8 *è I-03*:
   la rottura delle bande coincide con la rottura del canale; N9 *volatilità*: dopo la
   compressione cresce la volatilità, con stop in ATR il rapporto non cambia; N10 *uscita
   troppo rapida*: l'uscita sulla media taglia i trend.
5. **Previsioni e smentite.** N7: molte uscite in perdita, R entro la (b); N8: trade negli
   stessi giorni di I-03 con R simile; N9: R entro la (b); N10: R medio piccolo, durata breve.
6. **Ipotesi e varianti.** Timeframe 4h.
   * **I-10 a, long.** Condizione: compressione (sopra) e chiusura > media 20 + 2 σ 20.
     Uscita: «chiudi» quando la chiusura < media 20. Stop chiusura − 2 ATR. Riscaldamento 140.
   * **I-10 b, short.** Chiusura < media 20 − 2 σ 20; uscita su chiusura > media 20; stop +2 ATR.

## I-11 Ritorno alla media in tendenza (RSI a 2)

1. **Fonte.** Larry Connors, Cesar Alvarez, «Short Term Trading Strategies That Work»,
   TradingMarkets Publishing, 2008: comprare cali di breve (RSI a 2 periodi sotto 10)
   quando il prezzo è sopra la media a 200, uscire sopra la media a 5.
2. **Affermazione.** Su 4 ore, con chiusura sopra la media a 200 barre e RSI(2) < 10, il
   prezzo risale sopra la media a 5 più spesso e con R medio più alto di un long casuale con
   la stessa uscita.
3. **Sotto-domande.** Vale solo nelle tendenze sane? Chi opera: prese di profitto di breve
   dentro una tendenza; i compratori della tendenza rientrano sul calo.
4. **Spiegazioni concorrenti (10).** N1-N6; N7 *coltello che cade*: nel 2022 il filtro
   della media lascia passare l'inizio dei crolli; N8 *R asimmetrico*: molte piccole
   vincite e poche perdite grandi (lo stop) danno un R medio vicino a zero; N9 *costi*:
   rimbalzi piccoli rispetto ai costi; N10 *è I-02 a*: stesso meccanismo d'inversione su
   un'altra scala.
5. **Previsioni e smentite.** N7: perdite concentrate nel 2022; N8: win rate alto ma R
   medio ≤ 0; N9: R lordo < costo; N10: trade negli stessi giorni di I-02 a.
6. **Ipotesi e varianti.** Timeframe 4h (la fonte usa il giornaliero; a 1d i trade in
   682 giorni sarebbero troppo pochi: la regola resta la stessa sulle candele da 4 ore).
   * **I-11 a, long.** Condizione: chiusura > media 200 e RSI(2) < 10. Uscita: chiusura >
     media 5. Stop chiusura − 3 ATR. Riscaldamento 200.
   * **I-11 b, short.** Chiusura < media 200 e RSI(2) > 90; uscita: chiusura < media 5;
     stop + 3 ATR.

## I-12 Squilibrio fra compratori e venditori aggressivi

1. **Fonte.** Tarun Chordia, Avanidhar Subrahmanyam, «Order imbalance and individual
   stock returns: Theory and evidence», Journal of Financial Economics 72(3), giugno 2004:
   lo squilibrio degli ordini di un giorno predice positivamente il rendimento del giorno
   dopo (i market maker smaltiscono l'inventario a poco a poco).
2. **Affermazione.** Quando la quota di volume aggressivo in acquisto (colonna
   taker_buy_quote_volume dei file klines) delle ultime 24 ore supera il 90° percentile
   dei 30 giorni precedenti, le 24 ore seguenti salgono più di un long casuale con la
   stessa uscita; sotto il 10° percentile, scendono più di uno short casuale.
3. **Sotto-domande.** Lo squilibrio conta di più quando il prezzo non si è ancora mosso?
   Chi opera: chi ha informazione compra a mercato per giorni; i market maker spostano il
   prezzo gradualmente.
4. **Spiegazioni concorrenti (10).** N1-N6; N7 *è il momento*: lo squilibrio accompagna il
   rialzo appena avvenuto (I-01); N8 *inversione*: compratori esausti, il prezzo torna; N9
   *misura del feed*: la colonna aggressiva è distorta dai robot di arbitraggio; N10
   *volatilità*: lo squilibrio estremo coincide con volatilità alta.
5. **Previsioni e smentite.** N7: R simile a I-01 a negli stessi giorni; N8: R negativo; N9:
   R entro la (b); N10: R entro la (b).
6. **Ipotesi e varianti.** Timeframe 1h (24 barre = 1 giorno, 720 barre = 30 giorni).
   * **I-12 a, long.** Condizione: quota aggressiva in acquisto a 24 barre > 90° percentile
     delle quote a 24 barre delle 720 barre precedenti. Uscita dopo 24 barre. Stop chiusura
     − 3 ATR. Riscaldamento 744.
   * **I-12 b, short.** Quota < 10° percentile. Stop + 3 ATR. Stessa uscita.
