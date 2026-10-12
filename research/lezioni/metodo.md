# Lezioni di metodo

Solo errori di metodo e trappole dei dati: mai idee, meccanismi o risultati. Si legge
all'inizio di ogni campagna. Dopo la prova di processo resta congelato fino al Passo 7.

## 2026-10-06 (Passo 0)
* La rete della sessione di lavoro può bloccare l'host dei dati: si verifica l'accesso
  PRIMA di scrivere un'ipotesi, non dopo (il 6 ott data.binance.vision e fapi.binance.com
  erano bloccati dall'ambiente).

## 2026-10-07 (prova di processo, Passo 2)

Dalle proposte delle tre campagne della prova, filtrate dal coordinamento: solo metodo e
trappole dei dati. Quelle che sono diventate regole stanno nella versione 4.4 del protocollo
(stima dei trade, «nettamente», trade minimi, budget) e qui non si ripetono.

### La sessione e il guardiano
* **Il guardiano legge la forma dei comandi, non le intenzioni.** Nella prova ha rifiutato
  comandi innocui per la loro forma: la parola `.venv` in un comando, `python3 -c`, testi con
  virgolette triple dentro un heredoc, messaggi di commit su più righe dentro `-m`, `$?`,
  `2>&1`, la cartella madre `data/insample/` (sono ammesse solo le sottocartelle della moneta e
  di BTCUSDT), la parola «bot» dentro un testo, la lettura di `src/guardiano.py`. Regole
  pratiche: file e testi si scrivono con lo strumento di scrittura dei file, mai con heredoc; il
  messaggio di commit si scrive in un file dentro `data/insample/<SIMBOLO>/` (ammessa e fuori da
  git) e si passa con `git commit -F`; i comandi restano semplici, senza redirezioni né variabili
  della shell. Con git: la storia dei commit si legge solo per la propria cartella
  (`git log -- research/campagne/<SIMBOLO>/`, senza `-p`); `fetch`, `pull` e `push` solo con il nome
  del proprio branch; `git diff` solo contro HEAD; niente merge, rebase, cherry-pick, revert. Le
  pagine web si aprono solo da siti di pubblicazioni e da Wikipedia. Un rifiuto si registra nel log
  e non si aggira.
* **Il primo push si fa nei primi minuti.** Una sessione della prova è nata senza il permesso di
  scrivere sul repository e lo ha scoperto dopo, perdendo il lavoro locale. Se il primo push
  fallisce: STOP e avvisa l'utente.
* **I test che scrivono nel log vanno in serie.** Gli `id` del log sono progressivi in un file
  solo: due lotti lanciati in parallelo possono prendere lo stesso `id`.

### I dati
* **Il mark price ha buchi che il last price non ha**, in giorni diversi da moneta a moneta
  (anche giorni interi). Il motore vuole le serie allineate barra per barra: in Fase 0 si fa
  l'intersezione delle barre di last, serie dello stop e mark, e si dichiarano le barre tolte
  (il motore conta i buchi che restano). La scelta si scrive prima di ogni test, non nel codice
  delle varianti.
* **`Candela.volume` è in moneta base, non in USDT.** Per il volume in USDT serve la colonna
  `quote_volume` dei CSV, oppure volume per chiusura (un'approssimazione, da dichiarare).
* **I dati di riferimento di BTCUSDT servono sugli stessi timeframe della moneta.** Scaricali
  tutti in Fase 0: senza, il controllo «è solo il mercato» resta vuoto proprio dove serve.
* **La fascia di slippage del 2023 può essere ottimista per gli anni prima**, quando il volume
  era più basso: guarda il volume medio per anno in Fase 0 e dichiaralo; il test a costi doppi
  copre solo in parte.
* **Un periodo tolto perché sotto la liquidità minima sposta la divisione 70/30** calcolata in
  Fase 0 dal primo mese di dati: le date di costruzione e validazione restano quelle scritte
  prima dei prezzi, e la differenza si dichiara in Fase 0.
* **Le impronte dei file sono centinaia**: stanno meglio in un file `impronte.json` accanto a
  `fase0_dati.md`, con l'impronta di quel file scritta dentro `fase0_dati.md`.

### Il metodo
* **Prima della prima variante, un controllo positivo degli strumenti.** Una strategia che legge
  di proposito la barra successiva (lookahead dichiarato), con la stessa uscita e le stesse
  baseline delle varianti vere, deve battere nettamente il caso e crollare con il ritardo di una
  barra. Costa pochi minuti e si registra come nota (non è una variante, non consuma budget): se
  non passa, nessun risultato della campagna vale.
* **Le previsioni si scrivono al netto dei costi.** Prima di scriverle calcola il costo di un
  giro (commissioni e slippage, andata e ritorno) in R, con la distanza tipica dello stop sul
  timeframe: sulle durate brevi i costi sono una parte grande del movimento.
* **In Fase 2 guarda sempre l'R per anno e l'R medio senza i 3 trade migliori**, non solo il
  totale: pochi trade estremi o un solo anno favorevole possono fare un buon totale.
* **La baseline (a) e la (b) misurano cose diverse.** Su timeframe corti la (a) è dominata dai
  costi, e un candidato la batte anche solo entrando meno spesso; il confronto che smaschera è
  la (b), con lo stesso numero di trade.
* **Una stessa fonte non dovrebbe dare più di due varianti fra le idee nuove**: due direzioni per
  due condizioni alzano la probabilità di un falso positivo dentro un'idea sola. I ritocchi della
  regola 6 sono un'altra cosa e si dichiarano con `ritocco_di`.
* **Uno stop in ATR su candele lente supera spesso il tetto di stop del 6% del bot**
  (`config/parametri.yaml`, `stop_massimo_bot`): chi disegna idee lente lo sappia prima, e scelga
  fra stop in percentuale e un'idea che il bot non può eseguire così com'è (da dichiarare).
* **Con poche decine di trade «nettamente» chiede un vantaggio grande rispetto al rumore di un
  singolo trade**: la potenza è bassa (sezione 11). Non è un motivo per cambiare criterio in
  campagna.

## Lezioni di metodo dalle campagne (Passo 7, 12 ottobre 2026)

Dalle 21 campagne della versione 4.5 (20 monete e il gruppo), filtrate dal coordinamento: solo
metodo e trappole dei dati. Le regole pratiche del 7 ottobre qui sopra restano tutte valide: molte
campagne le hanno ritrovate da sole (e qualcuna ha sbagliato lo stesso). Le proposte che sono già
diventate regole del protocollo non si ripetono: l'ingresso nell'ordine dei ritocchi delle varianti
nette con R non positivo (decisione dell'8 ottobre, regola 6; chiesta da SOLUSDT e segnalata da
ETHUSDT) e l'R medio positivo anche in validazione (correzione del 9 ottobre, Validazione punto 3;
chiesta da FILUSDT, il cui candidato 025 perdeva −0,117 R con p 0,085).

### I dati e l'allineamento

* **Il primo mese della scheda quasi mai è pieno: la costruzione utile è più corta di quella
  calcolata.** La scheda dice «primo mese 2020-01» ma i file cominciano dopo: XRPUSDT dal 6 gennaio,
  LTCUSDT dal 9, ETCUSDT dal 16, LINKUSDT dal 17 (il listing), ADAUSDT con il last solo dal 31
  gennaio; 1000SHIBUSDT dal 10 maggio 2021 (673 giorni invece di 682), MASKUSDT dal 26-27 agosto 2021
  (592 invece di 618), DYDXUSDT dal 9-10 settembre 2021, FTMUSDT da fine settembre 2020. Le date di
  costruzione e validazione restano quelle scritte prima dei prezzi; in Fase 0 si guarda la prima
  barra vera, si dichiara, e si sa che il minimo di 70 trade è più duro. La prima candela
  giornaliera è parziale. [XRP, LTC, LINK, ADA, ETC, 1000SHIB, DYDX, MASK, FTM]
* **Il mark manca per giorni interi, spesso negli stessi giorni su monete diverse**, e vanno elencati
  tutti in Fase 0, anche quelli che cadono in validazione. Il 2 ottobre 2022 e il 24 febbraio 2023
  mancano su ETHUSDT, LINKUSDT, FILUSDT, ETCUSDT, GALAUSDT e AVAXUSDT; il 31 luglio 2022 su LINKUSDT,
  GALAUSDT e AVAXUSDT; luglio 2021 su LINKUSDT (1 e 24-27) e AVAXUSDT. FILUSDT ha buchi anche nel last,
  in giorni diversi dal mark (last: 26-28 febbraio e 1-2 aprile 2022). Nel vault un giorno di mark
  mancante nel giugno 2026 ha lasciato il 96,7% delle barre allineate su tutte e tre le monete.
  Due conseguenze pratiche: le regole che misurano «da N barre fa» attraversano i buchi senza
  accorgersene (da dichiarare, FILUSDT lo ha fatto per tre idee); una posizione che attraversa un
  buco lungo gonfia la durata media dei trade, che entra nella distanza minima degli ingressi della
  (b) (AVAXUSDT: una posizione di mezz'ora che attraversa quattro giorni senza mark vale 192 barre).
  [ETH, LINK, FIL, ETC, GALA, AVAX]
* **I mesi sotto la liquidità minima accorciano la costruzione più di quanto dicano le date, e
  tolgono i trade alle idee lente.** DOGEUSDT: tutto il 2020 sotto i 20 milioni al giorno, la
  costruzione utile scende da 895 a 711 giorni e 8 dei 14 scarti sono a 1 giorno o 4 ore. TRBUSDT: 7
  mesi su 28 sotto soglia, metà delle idee a 4h-1d finisce sotto i 70 trade. FTMUSDT: quattro mesi
  illiquidi, trade solo in due anni, e la verifica di stabilità conta su due anni soli. MATICUSDT:
  ingressi possibili solo dal 1° febbraio 2021. Regola pratica: guardare i mesi illiquidi in Fase 0
  prima di scegliere i timeframe delle idee, e stimare a mente la frequenza dei segnali (BCHUSDT: con
  1.022 giorni di costruzione una regola giornaliera che entra meno di una volta ogni 15 giorni non
  arriva a 70; quattro idee giornaliere su sei scartate al primo tentativo, 23-67 trade). La conta
  vera si fa una volta sola, sulle regole registrate. [DOGE, TRB, FTM, MATIC, BCH]
* **Lo slippage della scheda (calcolato sul 2023) è ottimista per gli anni prima, e il test a
  costi doppi non sempre arriva alla fascia vera.** BCHUSDT: nel 2020 e nel 2022 il volume stava
  nella fascia dello 0,05% per lato contro lo 0,02% della scheda, e i costi doppi (0,04%) restano
  sotto. TRBUSDT: 0,02% per lato in scheda contro una fascia dello 0,10% nel 2020-2021. ETHUSDT: nel
  2020 il volume era un decimo di quello del 2023 (0,72 miliardi al giorno). AVAXUSDT: autunno 2020 e
  giugno-luglio 2021 sotto i 20 milioni. Da dichiarare in Fase 0 con il costo di un giro per anno
  (vedi anche le proposte in fondo). [BCH, TRB, ETH, AVAX]
* **Una cache delle serie va legata alla versione del caricatore.** La correzione del funding
  dell'8 ottobre (orario al secondo) non arrivava ai test di SOLUSDT perché la cache locale si
  ricostruiva solo se mancava: 2.083 settlement su 3.688 avevano ancora i millisecondi, e un esito
  (SOLUSDT-015 contro la (b)) cambiava da netto a non netto. Soluzione usata: la cache porta
  l'impronta di `src/dati.py` e si rifà quando cambia. L'origine del problema: il funding nei file
  di Binance arriva con qualche millisecondo di ritardo (BTCUSDT: fino a 47 ms in 2.233 settlement su
  4.383), corretto in `src/dati.py` (commit 2fedf41, CHANGELOG dell'8 ottobre). [SOL, BTC]
* **Lo scarico dei file mensili con CHECKSUM dura 20-30 minuti per circa 1.200 file e può
  interrompersi** (rete). Lo script deve riprovare mese per mese e scrivere su file, man mano,
  l'elenco dei CHECKSUM mancanti: uno scarico interrotto in background perde quell'elenco e non lo si
  può leggere (DYDXUSDT non ha mai letto l'elenco dei file accettati senza CHECKSUM remoto). Lo
  scarico di tutti i timeframe di BTCUSDT da solo supera i 10 minuti. [DOGE, 1000SHIB, ETC, DYDX, LINK]
* **La quota di volume comprato a mercato (`taker_buy_volume`, decima colonna dei file klines) c'è
  in tutti i mesi 2020-2023, ma le candele del motore non la portano**: va letta a parte. Su un
  perpetuo il segno da solo non è bilanciato: su DYDXUSDT la quota è sotto 0,5 in quasi tutti i
  giorni (257 contro 54 fra gli ingressi possibili). [ETH, DYDX]
* **Una ricerca web può mostrare informazioni dopo il 2023 sulla moneta** (MATICUSDT: titolo e
  riassunto di un articolo del 2024). Si scrive nel log cosa si è visto e si toglie l'idea
  collegata. Fra i siti: le pagine di istituti come cesifo.org non sono ammesse, la stessa scheda
  si trova su ideas.repec.org. [MATIC, LINK]

### Stop, costi e tetto del bot

* **Uno stop agganciato a un livello di prezzo (apertura del giorno, estremo della barra, minimo di
  un intervallo, una media) falsa il confronto con la (a) e la (b).** Le baseline entrano anche dove
  il livello è vicinissimo all'ingresso: il costo fisso di un giro diviso un rischio minuscolo dà R
  molto negativi, e una variante che entra solo dove lo stop è largo le batte «nettamente» senza
  alcun potere di direzione. È la trappola più ripetuta delle campagne: BTCUSDT (b) a −0,83 e −0,31 R
  per una variante con R +0,15, e V11 che passa da t 3,01 a 1,01 con lo stop fisso al 2%; LTCUSDT con
  t fra 1,1 e 2,0 su otto varianti senza alcuna direzione, e la 027 (stessa regola, stop fisso) da
  1,95 a 0,01; BCHUSDT (b) a −0,19 R contro −0,05 delle altre varianti orarie; ADAUSDT 6 volte su 6,
  con 5 varianti poi cadute ai costi doppi; FILUSDT-025 (b) −0,31 in costruzione e −0,39 in
  validazione contro −0,04 con uno stop normale, e t 1,38 contro ingressi casuali con stop di
  distanza normale; AVAXUSDT con metà delle barre a segnale non valido e la (a) facilissima da
  battere. Il test del ritardo ha lo stesso difetto quando lo stop si calcola dalla barra del segnale
  (BTCUSDT: il controllo positivo col ritardo dava ancora t 8,4). Regola pratica da subito: chi
  disegna una variante con lo stop su un livello lo sa prima, e la (b) resta il confronto che conta;
  la verifica con lo stop a distanza fissa, registrata prima, è il controllo che smaschera (vedi le
  proposte in fondo). [BTC, LTC, BCH, ADA, FIL, AVAX]
* **Un filtro che sceglie le barre volatili abbassa i costi in R, e la (b) normale non lo sa.** Con
  stop in ATR, una condizione che entra dove lo stop è largo paga meno costi per trade della (b): il
  segno è che il t contro la (b) CRESCE a costi doppi mentre l'R medio scende sotto zero
  (1000SHIBUSDT: 2,08 → 2,56 e 2,15 → 2,48). La prova utile è la (b) ristretta alle stesse barre del
  filtro (BNBUSDT-043, `vieta_extra` in `codice/comune.py`; ADAUSDT: la (b) rifatta solo dove valgono
  i filtri ha dato t 0,63 a un candidato che aveva superato tutte le verifiche della Fase 4). Da
  guardare sempre il costo medio in R del candidato e della (b). [1000SHIB, BNB, ADA]
* **Il costo di un giro in R si calcola prima di scegliere il timeframe, e il vantaggio lordo deve
  valere almeno il doppio.** Numeri misurati con stop a 2-3 ATR: 30 minuti circa 0,05 R (SOLUSDT),
  0,06 (AVAXUSDT), 0,065 (1000SHIBUSDT), 0,067 (ETHUSDT), 0,08 (ETCUSDT), 0,10 (DOGEUSDT, TRBUSDT),
  0,14 (BNBUSDT); 1 ora 0,05-0,10 R (GALAUSDT, MASKUSDT), 0,07 (FILUSDT con stop al 3%, GRUPPO);
  4 ore 0,034 R e 1 giorno 0,012 R (GRUPPO, mediana fra 80 monete). Una variante che batte il caso di
  0,06 R può avere R dopo i costi quasi zero e cadere ai costi doppi (GALAUSDT); un lordo sotto
  0,13-0,15 R a 30 minuti-1 ora non regge (1000SHIBUSDT, FILUSDT). Allargare lo stop non cambia il
  rapporto fra costi e movimento (GRUPPO). Conviene calcolare il guadagno lordo in punti base contro
  il costo del giro già in Fase 3, prima dei ritocchi (ETCUSDT). [SOL, AVAX, 1000SHIB, ETH, ETC,
  DOGE, TRB, BNB, GALA, MASK, FIL, GRUPPO]
* **Il tetto del 6% del bot rende fisso lo stop di quasi tutte le idee da 4 ore in su, e va limitato
  prima dei test.** ATR giornaliero mediano: MATICUSDT 10%, 1000SHIBUSDT 8% (3% a 4 ore), TRBUSDT
  13,4% (4,9% a 4 ore: 2 ATR supera il 6% già a 4h), FTMUSDT stop in ATR giornalieri del 30% e oltre
  (con violazioni del margine); ETCUSDT stop oltre il 6% in 3 trade su 4 a 4h; GALAUSDT 2 ATR a 4 ore
  tocca il tetto in 69 trade su 109 (e a 1 ora in 78 su 325); GRUPPO 3 ATR a 1d vale circa il 31%.
  Le R di queste idee dipendono dalla durata della tenuta più che dall'ingresso. In più, il tetto
  calcolato sulla chiusura del segnale, misurato dal riempimento vero (apertura dopo più slippage),
  supera di poco il 6% in una parte dei trade e il controllo del bot potrebbe rifiutarli
  (XRPUSDT, 1000SHIBUSDT): o si fissa il tetto un po' sotto (5,9%) o si misura dal prezzo
  d'ingresso atteso, deciso prima. [MATIC, 1000SHIB, TRB, FTM, ETC, GALA, GRUPPO, XRP]

### Baseline, potenza dell'esame e lettura dei risultati

* **La (a) non è «entrare sempre».** Con un'uscita «dopo una barra» la (a) entra una barra sì e una
  no (alla chiusura della barra in cui è ancora in posizione non può emettere un segnale): il suo
  numero di trade va letto sapendolo (LINKUSDT). Con uscita a tempo su 30 minuti fa decine di migliaia
  di trade; il bootstrap regge (16 GB di memoria) ma il tempo cresce. La (b) con molti trade costruisce
  una tabella barre × trade: a 1 ora con 24.500 barre e 1.600 trade circa 300 MB, a 15 minuti con
  migliaia di trade più GB. Si può fare, ma va saputo prima. [LINK, ETH]
* **La distribuzione dei `t` di tutte le varianti è il controllo d'insieme della Fase 5.** Se media e
  deviazione sono quelle della prova a placebo (circa 0 e 0,8), l'insieme non si distingue dal rumore
  anche se qualche variante sembra «vicina»: BCHUSDT 30 t con media 0,11 e deviazione 0,96; TRBUSDT
  come il placebo; ETHUSDT 2 varianti nette su 30 contro 0,7 attese per caso, probabilità del 14,8%
  di vederne almeno 2 (`codice/fase5.py`). [TRB, BCH, ETH]
* **Nella robustezza, metà dei parametri può non toccare la condizione d'ingresso** (finestre di
  stima, periodo dell'ATR, numero minimo di valori): quei casi «reggono» per costruzione e vanno letti
  a parte (DYDXUSDT). E i parametri interagiscono: spostare di −20% una finestra di 365 giorni (a 292)
  con un minimo fisso di 300 valori dà zero trade (BTCUSDT); si prevede quando si scrivono i
  parametri. [DYDX, BTC]
* **L'R medio senza i 3 trade migliori va riportato anche in validazione, non solo in costruzione.**
  ADAUSDT-037: in validazione +0,624 R su 82 trade, ma +0,014 senza i 3 migliori; nel vault −0,164
  (`vault/risultati.md`). «Nettamente» e l'asticella sono test sulla media e non lo vedono. Il
  drawdown di validazione si calcola dai rendimenti dei trade in percentuale del capitale
  all'ingresso, non da «1000 più la somma dei pnl»: il capitale all'inizio della validazione non è
  1000 (SOLUSDT). [ADA, SOL]
* **Una stabilità per anno con un anno solo utile non dice niente.** Una soglia che conta trade rari
  può mettere quasi tutti i trade in un anno: supera la verifica alla lettera (un solo anno con
  almeno 10 trade) e poi fa 5 trade in 14 mesi di validazione (XRPUSDT-V21r3: 84 trade su 97 nel 2020).
  Vedi le proposte in fondo. [XRP]
* **I test dello scettico che hanno smontato di più, da registrare prima e fare in Fase 5:**
  togliere dall'ipotesi la parte che porta il meccanismo (DYDXUSDT: senza la condizione «DYDX è
  rimasta indietro» il risultato non cambiava, contava solo l'ora forte di BTC); la stessa regola
  alle altre ore e la stessa ora senza la condizione, per le regole legate all'orologio (SOLUSDT:
  alle 11:30 t −1,52; 1000SHIBUSDT: a mezzogiorno t −1,09; ETCUSDT lo propone come placebo); la (b)
  solo dove valgono i filtri (ADAUSDT, sopra); lo stop a distanza fissa (BTCUSDT, LTCUSDT, FILUSDT).
  [DYDX, SOL, 1000SHIB, ETC, ADA, BTC, LTC, FIL]
* **Il controllo positivo va fatto in entrambe le direzioni, sui timeframe usati e con l'uscita più
  corta della campagna.** BCHUSDT: il primo copriva solo il long a 1h, il secondo (short su 1d e 4h)
  ha confermato. GRUPPO: con tenuta di 7 giorni non batteva nettamente la (a) di gruppo (t 1,96,
  soglia 2,07) perché l'errore della (a) con tenute lunghe è grande (0,070 R); con uscita a 1 giorno
  passa (t 24,45 contro la (b)). Col ritardo di una barra il controllo positivo non va a zero quando
  lo stop si calcola dalla barra di segnale (BNBUSDT t circa 4, AVAXUSDT 3,3 su 4.598 trade, DYDXUSDT
  2,48 contro 46,9 senza ritardo, GALAUSDT 3,7): «crolla» si legge come rapporto, e si guarda anche
  l'R medio, che deve diventare non positivo. [BCH, GRUPPO, BNB, AVAX, DYDX, GALA]
* **Nell'esame di gruppo decide quasi sempre il pavimento delle sfasate.** Molte varianti stanno al
  99-100° percentile delle simulazioni casuali indipendenti e non battono il pavimento, perché i loro
  trade cadono negli stessi giorni su tutte le monete (effetto grappolo fino a 33, fino a 112 uscite
  in un giorno). Le idee con ingressi sincronizzati (calendario, rotture nei rialzi comuni, crolli
  comuni) hanno pochi blocchi. Allentare una condizione aumenta i blocchi più di quanto riduca l'R
  fino a un punto (t 0,91 → 1,44 → 1,80 → 1,89 in I-19), poi si appiattisce. [GRUPPO]

### Il test del ritardo e il controllo di causalità

* **Il ritardo di una barra boccia per costruzione le regole legate a un'ora del giorno, e non
  distingue un lookahead da un effetto breve.** Una regola che entra alle 23:30 per l'ultima
  mezz'ora, ritardata di una barra, entra alle 00:00: il test misura un'altra strategia (SOLUSDT,
  AVAXUSDT, ADAUSDT, ETCUSDT); su FILUSDT sette candidati con la fascia 20-24 UTC sono caduti così.
  Un effetto vero di poche ore crolla con un'ora di ritardo quanto un errore di codice (MATICUSDT;
  BNBUSDT: il rimbalzo vive nella prima ora; AVAXUSDT V-14: t sceso a 0,494 volte, serviva 0,5, e la
  ricerca dell'errore non ha trovato nulla). Tutte le campagne hanno seguito la regola com'è; chi ha
  trovato un crollo ha cercato l'errore. Quello che aiuta in pochi minuti a distinguere i due casi:
  la **prova per troncamento** (condizione e segnale ricalcolati sulla serie tagliata alla barra del
  segnale, o a un terzo e due terzi, e confrontati con la serie intera: trova ogni indicatore che
  guarda avanti negli array precalcolati, e segnala subito la strategia di controllo con lookahead
  dichiarato; SOLUSDT, MATICUSDT, AVAXUSDT, TRBUSDT `codice/controllo_causalita.py`, GALAUSDT), e
  l'elenco scritto dei dati esterni che la variante legge oltre alle barre chiuse del motore (serie
  completa, BTC, funding, altre colonne): se nessuno, il lookahead non è possibile (ETHUSDT-N014).
  Cosa fare quando il controllo è pulito e il t è comunque crollato lo decide il proprietario (vedi
  in fondo). [SOL, AVAX, ADA, ETC, FIL, MATIC, BNB, ETH, TRB, GALA]

### Ritocchi e budget

* **L'ordine dei ritocchi per `t` concentra tutti i ritocchi su una o due famiglie, e il candidato
  che ne esce è il migliore di 5-7 tentativi sugli stessi dati.** È il comportamento della regola,
  non un errore delle campagne, ma va letto così ogni volta che un candidato viene da ritocchi.
  SOLUSDT: 5 ritocchi su 8 alla famiglia di 015, 4 candidati, uno solo in validazione. LTCUSDT: 5
  ritocchi della 014 anche dopo che la 027 l'aveva smontata (stop fisso, t 0,01). FILUSDT: 8 ritocchi
  su 8 alla stessa idea. DYDXUSDT: 5 alla 013 e 5 alla 014, poi il budget è finito. ETCUSDT: 5 su 7 a
  una famiglia netta contro il caso ma in perdita dopo i costi. 1000SHIBUSDT: 2 ritocchi su 5
  sprecati in scarti sotto i 70 trade. BTCUSDT: 5 ritocchi di V19 (R lordo +0,045 contro costi di
  0,12 R) l'hanno resa «netta» (t fino a 3,58) senza mai rendere l'R robusto ai costi doppi.
  MASKUSDT, DOGEUSDT, MATICUSDT, ADAUSDT, GRUPPO: stessa forma. In tutti i casi la Fase 4 (costi doppi,
  ritardo) o la validazione hanno fermato il candidato: sono il freno che serve, e vanno fatte prima
  di ogni entusiasmo. Proposte di cambiamento in fondo. [SOL, LTC, FIL, DYDX, ETC, 1000SHIB, BTC,
  MASK, DOGE, MATIC, ADA, GRUPPO]
* **Prima di un ritocco con un filtro, guardare la distribuzione della grandezza che si taglia e
  chiedersi se il filtro è già implicito nell'ingresso.** Un'uscita a 12 barre su trade con durata
  mediana 4 non tocca quasi nulla e brucia una variante (BNBUSDT-N019); il filtro «sotto la media a 50
  ore» sulla rottura short ha tolto 13 trade su 327 perché l'ingresso lo implicava (BCHUSDT); un filtro
  che toglie un terzo dei trade porta facilmente sotto 70 con 85-101 trade di partenza, e lo scarto
  consuma un ritocco della famiglia (SOLUSDT, 1000SHIBUSDT). Si ragiona, non si conta: la conta si fa
  una volta sola. [BNB, BCH, SOL, 1000SHIB]
* **Tutte le varianti di un'idea si scrivono e si contano prima del primo test dell'idea, e non si
  aggiungono varianti mentre i test girano.** Contare tutte le varianti subito dice quali idee non
  arrivano a 70 trade, e l'allentamento di una soglia scritto prima del primo test è ancora una
  variante dell'idea nuova; scritto dopo aver visto la variante gemella non lo è più (FTMUSDT, caso
  I-04). GALAUSDT: una variante allentata scritta subito dopo aver lanciato i test in background è
  arrivata 8 secondi dopo il primo risultato della sua idea ed è stata ritirata. [MATIC, FTM, GALA]
* **Le idee nuove «trovate dopo» e le idee scelte come contrario di un fallimento si dichiarano.**
  Con 30 unità e 14 idee da due varianti, le idee scritte dopo aver visto i primi risultati prendono
  le ultime unità: va scritto in `ipotesi.md` che sono state scritte dopo e perché non nascono da
  quei risultati (ETHUSDT I-15...I-18). Un'idea scelta come il contrario di un fallimento non è un
  vantaggio solo per questo: ETHUSDT-034 (dal fallimento sistematico di I-13) è venuta vicina al caso
  (t 1,17), perché il fallimento veniva in parte dallo stop; LINKUSDT V24 e LTCUSDT I-11 dichiarano la
  stessa scelta. [ETH, LINK, LTC]
* **Un conteggio di 0 trade si controlla prima di registrarlo come scarto.** Una media mobile
  calcolata con la somma cumulata propaga un NaN iniziale a tutta la serie: la condizione non è mai
  vera e la variante sembra uno scarto legittimo (BNBUSDT-N013). Nella strategia il segnale (con il
  riscaldamento) va valutato prima della condizione, altrimenti una finestra di barre fallisce alle
  prime barre e `conta_trade` si interrompe (MASKUSDT). [BNB, MASK]

### Il guardiano e i comandi rifiutati

* **L'uscita dei comandi lanciati in background non si può leggere: sta in una cartella temporanea
  fuori dai percorsi ammessi.** L'hanno scoperto, ognuna con un rifiuto, 19 campagne su 21 (tutte
  tranne SOLUSDT e GRUPPO): costa un rifiuto a campagna e va messo in cima alle regole pratiche. Cosa
  ha funzionato: ogni script lungo scrive da solo il proprio esito e il proprio avanzamento in
  `data/insample/<SIMBOLO>/` (ammessa e fuori da git) o nel log, e la sessione legge solo lì; per
  aspettare la fine si usa un piccolo script Python nella cartella del codice che aspetta una parola
  in quel file (DOGEUSDT, TRBUSDT `codice/attendi.py`, GALAUSDT, BNBUSDT), oppure si lancia in primo
  piano con un timeout lungo (LINKUSDT). Lo strumento di monitoraggio continuo, lo strumento Workflow
  e i sotto-agenti non sono ammessi (XRP, DOGE, BNB, TRB, SOL, ETC). Un comando in background parte
  dalla cartella della sessione, non da quella dell'ultimo `cd`: il `cd` va nello stesso comando
  (FTMUSDT). [tutte tranne SOL e GRUPPO]
* **Il messaggio di commit con `-m` che contiene l'indirizzo della sessione (o qualunque indirizzo
  web) viene rifiutato: sempre `git commit -F` con il messaggio in un file.** Era già scritto il 7
  ottobre, e sette campagne l'hanno sbagliato lo stesso (BNB, LTC, LINK, DYDX, MASK, FTM, GRUPPO): va
  in cima. E il file del messaggio si scrive subito prima di ogni commit, nello stesso passo: due
  commit di FILUSDT hanno il titolo del commit precedente. [BNB, LTC, LINK, DYDX, MASK, FTM, GRUPPO, FIL]
* **Altre forme rifiutate, in aggiunta a quelle del 7 ottobre** (tutte aggirabili con lo strumento
  di modifica dei file e con script che accettano più argomenti):
  `sed -i` con un testo fra apici o barre (letto come percorso: SOL, XRP, LINK, DYDX, ETC, TRB, DOGE,
  FTM); `awk` e gli asterischi nella shell (FTM); i percorsi relativi con `..`, `find .`, `cd` nella
  cartella della campagna o nella cartella madre `research/` seguito da percorsi relativi, `git -C
  <radice>` (BTC, XRP, DOGE, MATIC, AVAX, FIL, FTM): si usano percorsi assoluti dalla radice, senza
  `cd` né `-C`; `$`, `$?`, `$(...)` e i cicli `for`/`until` con variabili della shell, anche solo per
  aspettare (SOL, TRB, GALA, FIL); `grep` con un'espressione regolare complessa, con il motivo
  `'^--$'`, o con la parola `research` da sola, e le ricerche con schemi che contengono `/`
  (ADA, 1000SHIB, ETC, GRUPPO: meglio uno script di riassunto o lo strumento di ricerca); più comandi
  git uniti con `&&` e una pipe, `git push ... | tail`, `git diff HEAD --stat` senza percorso, `git
  show` (MATIC, SOL, AVAX); `ls` della cartella madre `campagne/` o `data/insample/`, e Glob senza
  percorso (LINK, ETC, XRP); nominare un file fuori dai percorsi ammessi anche senza leggerlo, per
  esempio `ls requirements*.txt` (ETC). [SOL, XRP, LINK, DYDX, ETC, TRB, DOGE, FTM, BTC, MATIC, AVAX,
  FIL, GALA, ADA, 1000SHIB, GRUPPO]
* **pytest, numpy, scipy e pyyaml possono mancare nella macchina della sessione**: si installano con
  pip prima dei test del guardiano, senza leggere i file del bot (ETH-N001, DOGE, ETC). [ETH, DOGE, ETC]

### Tempo, sessioni e cosa scrivere nel log

* **Uno script che per ogni variante conta, registra e poi testa, in serie, è lo strumento giusto
  per i lotti.** Nessun conteggio resta fuori dal log, una variante già contata non si riconta, è
  impossibile testare prima di registrare, gli id restano progressivi, e se si interrompe dopo la
  registrazione riprende dal test (ETHUSDT `codice/registra.py` e `codice/lotto.py`, LINKUSDT,
  GALAUSDT, GRUPPO, MATICUSDT). Prima di contare, una prova del codice senza numeri: le quattro
  fabbriche (variante, (a), casuale, segnale) girano su un pezzo di dati e stampano solo «ok» o
  l'errore (ETHUSDT `codice/prova_codice.py`). Uno script di riassunto per leggere i JSON degli esiti
  toglie la tentazione di `python -c` (ETHUSDT). GALAUSDT ha fatto girare tre processi in parallelo
  con gli id assegnati prima e un blocco di file sulla scrittura del log, senza sovrapposizioni: è
  una via, ma la regola del 7 ottobre (lotti in serie) resta la più semplice. Gli indicatori calcolati
  una volta su tutta la serie (causali) e letti per indice rendono le 200 simulazioni della (b)
  veloci anche a 30 minuti (FTMUSDT). [ETH, LINK, GALA, GRUPPO, MATIC, FTM]
* **Gli id delle note si generano o si controllano prima di scrivere.** Uno script di note con id
  fissi, rilanciato dopo un errore, scriverebbe due volte lo stesso id (ETCUSDT, evitato a mano con
  una voce di correzione). Due campi con lo stesso nome (`errore_standard` dell'esito di
  `contro_baseline` e quello del dizionario della (b)) si perdono se si uniscono i dizionari: nomi
  diversi (MASKUSDT). [ETC, MASK]
* **L'orario delle voci del log si prende dall'orologio della macchina dentro lo script che scrive
  la voce**, mai a memoria (GRUPPO-013, una correzione per questo). Le durate lette dal campo `data`
  hanno un limite: XRPUSDT ha registrato 40 minuti dalla prima all'ultima voce per il lavoro svolto;
  le misure di processo vanno lette sapendolo. [GRUPPO, XRP]
* **Nella registrazione della validazione si scrive anche la previsione numerica**: BTCUSDT l'ha
  dimenticata (N018) e il formato della registrazione dovrebbe chiederla. [BTC]

### Proposte che toccano una regola del protocollo o richiedono una decisione del proprietario

Elencate, non decise. Per ognuna: cosa cambierebbe, chi la propone, il numero che la sostiene.

1. **Verifica obbligatoria con lo stop a distanza fissa per ogni candidato con lo stop su un livello
   di prezzo** (nuova verifica della Fase 4, registrata prima, per candidato e baseline), oppure una
   (b) con la stessa distribuzione della distanza dello stop, oppure vietare alla (b) le barre in cui
   la distanza dello stop è sotto un minimo scritto prima, o riportare l'R medio in percentuale del
   prezzo accanto alla (b). [BTC, LTC, ADA, FIL] Numeri: BTCUSDT V11 t 3,01 → 1,01; LTCUSDT 027 t 1,95 →
   0,01; ADAUSDT 6 su 6; FILUSDT-025 t 1,38 con stop normale, validazione −0,117 R.
2. **La (b) ristretta alle barre del filtro come verifica standard per ogni candidato con un
   filtro** (Fase 4). [BNB, ADA, 1000SHIB] Numeri: ADAUSDT t 0,63 dopo che tutte le verifiche erano
   superate; 1000SHIBUSDT t che cresce a costi doppi (2,08 → 2,56).
3. **L'ordine dei ritocchi (regola 6).** Tre varianti proposte: escludere dalla lista le varianti con R
   lordo medio sotto i costi medi in R, perché nessun filtro può recuperarle (BTC: V19 lordo +0,045
   contro costi 0,12 R, cinque ritocchi); non lasciare in testa una famiglia che un suo ritocco ha
   già smontato (LTC: 5 ritocchi della 014 dopo la 027); valutare se concentrare 5+5 ritocchi su due
   famiglie è l'uso migliore delle ultime varianti (DYDX, FIL, SOL, ETC, MASK, GRUPPO). Tutte le
   campagne dicono che la regola è stata applicata com'è.
4. **Il test del ritardo (Fase 4, verifica 6).** Affiancare al rapporto dei t un controllo diretto del
   lookahead (prova per troncamento e profilo del rendimento barra per barra) e scrivere cosa si fa
   quando il controllo è pulito e il t è comunque sotto la metà (AVAX: V-14 a 0,494, nessun errore
   trovato; SOL; MATIC; ETH-N014). Per le regole legate a un'ora del giorno: un test del lookahead
   che non sposti la fascia (per esempio entrare un'ora dopo su candele più corte), oppure dichiarare
   in partenza che il protocollo non le ammette, così non consumano budget (FIL: 7 candidati caduti
   così; ETC: dichiararlo nell'ipotesi; ADA). Oggi la regola dice «il candidato non va avanti finché
   l'errore non è trovato»: le proposte la cambiano.
5. **Stabilità temporale (Fase 4): richiedere almeno due anni con 10 trade, o dichiarare «non
   giudicabile» con un anno solo.** [XRP] Numero: 84 trade su 97 nel 2020, poi 5 trade in validazione.
6. **R medio senza i 3 migliori obbligatorio anche in validazione** (oggi è solo in Fase 2 e Fase 4).
   [ADA] Numero: +0,624 → +0,014 senza i 3 migliori; vault −0,164.
7. **Slippage per anno invece della fascia del 2023**, deciso prima delle campagne, con il costo di un
   giro per anno in Fase 0. [BCH, TRB, ETH] Numeri: BCHUSDT 0,05% contro 0,02% (i costi doppi, 0,04%,
   non arrivano); TRBUSDT 0,10% contro 0,02%.
8. **Tetto dello stop misurato dall'ingresso atteso, o fissato al 5,9%**, deciso prima dei test.
   [XRP, 1000SHIB]
9. **Il formato della registrazione di validazione chiede la previsione numerica.** [BTC] Modifica di
   formato (sezione 6), non di criterio.
10. **Prova di causalità per troncamento come prova standard quando il ritardo crolla** [SOL, MATIC,
    TRB, GALA, AVAX]: è una pratica, non un cambio di criterio, ma va scritta nel protocollo se deve
    valere per tutte (è parte del punto 4).
11. **Test paralleli con blocco del file e id assegnati prima** [GALA] contro la regola pratica del 7
    ottobre «i test che scrivono nel log vanno in serie»: non è una regola del protocollo, ma le due
    indicazioni vanno conciliate prima di lasciarle entrambe nel file.
12. **Candidato «debole» al 90-96° percentile ma non netto** (dall'archivio della prova di processo,
    BTCUSDT, proposta 3): non unita, è nell'archivio (sotto). La segnalo perché la sola campagna di
    gruppo ha visto molte varianti al 99-100° percentile non nette.

### Cosa contengono gli archivi della prova di processo (non uniti)

I branch `origin/research/archivio/campagna/{BTCUSDT,ETHUSDT,SOLUSDT}` (7 ottobre, archiviati al
Passo 2) hanno le loro `lezioni_metodo_proposte.md` e `lezioni_moneta.md`. Quasi tutte le proposte
di metodo sono già entrate nel protocollo 4.4 (stima dei trade per tipo di uscita e con occupazione
unica, «nettamente» unico, due varianti per fonte, budget e avanzo dichiarato, 200 simulazioni fisse,
impronte.json) o nella sezione del 7 ottobre qui sopra (guardiano, mark con buchi, volume in moneta
base, slippage del 2023, controllo positivo, previsioni nette, R per anno e senza i 3 migliori, lotti
in serie, BTC sugli stessi timeframe). Non sono entrate, e restano solo lì: il «candidato debole»
(BTCUSDT-archivio 3, sopra al punto 12); la lentezza del motore a 1 ora con lo slicing a ogni barra
(BTCUSDT-archivio 8: 5 minuti con 100 simulazioni, 8 a 30 minuti con 50); le idee a un ingresso a
settimana che non possono arrivare ai trade minimi per direzione, con la proposta di una variante
«entrambe le direzioni» (ETHUSDT-archivio 3); il percentile fra 200 casuali contro il bootstrap a
blocchi, da riportare entrambi (ETHUSDT-archivio 7: 4 varianti su 23 sopra il 97° percentile, nessuna
oltre 1,5 errori standard). Le lezioni sulle monete degli archivi stanno nella bozza
`lezioni_comuni_bozza.md`, in una sezione a parte, senza unirle.
