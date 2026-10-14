# Protocollo di ricerca, seconda edizione (versione 5.0) — BOZZA per il proprietario

> **Stato: TESTO IN VIGORE.** Bozza del 13 ottobre 2026 scritta dopo il sì del proprietario «procedi con tutto»;
> **approvata dal proprietario il 13 ottobre 2026 alle 19:34 UTC** (messaggio in chat: «approvo la seconda edizione,
> 3 idee e anche più varianti, dal 16 gennaio 2023 va bene»), con due modifiche chieste da lui e scritte qui
> prima di qualunque dato: **tre idee** invece di due (la terza è l'idea C della sezione 5) e **più varianti**
> (18 invece di 10, con 3 ritocchi per famiglia). Le sue due domande (il paper viene dopo il vault? la sessione
> unica è una moneta o tutte?) hanno la risposta nelle sezioni 9 e 11. Da qui il testo non cambia più: le
> correzioni seguono la regola della prima edizione (una voce nuova nel log, mai una riga cancellata). Il
> Passo 0 (sezione 10) parte dal 13 ottobre sera e finisce con uno STOP: la campagna non inizia senza
> l'approvazione di `parametri_2.yaml`.

## 0. Come usare questo file

Questo testo NON sostituisce `research/PROTOCOLLO.md` (versione 4.5, in vigore dal 9 ottobre 2026): lo
specializza. Tutto ciò che non è scritto qui vale come nella 4.5 e nelle regole della campagna di gruppo
(`research/campagne/GRUPPO/regole.md`). In particolare restano in vigore senza cambiamenti:

* della 4.5: la sezione 2 (sicurezza, guardiano, `DRY_RUN`, segreti), la sezione 4 (regole non negoziabili:
  prima scrivi poi testi, log solo in aggiunta, previsioni dichiarate, ipotesi ferme, indipendenza, niente
  conoscenza del vault, backtest uguale al bot), la sezione 6 (formato del log), la sezione 7 (motore), la
  sezione 8 (statistica), le sezioni 10, 11 e 12 (memoria, limiti, stile);
* delle regole del gruppo: la sezione 2 (i dati, con il filtro di liquidità), la sezione 5 (l'esame di gruppo:
  trade sommati, blocco, baseline (a) e (b), strategie sfasate, «nettamente», candidato), la sezione 7
  (validazione e asticella), la sezione 9 (il vault di gruppo), la sezione 11 (la prova a placebo), la sezione
  12 (la sessione) e la sezione 13 (gli strumenti), con gli adattamenti al giorno scritti qui.

Chi legge questo file sta scrivendo o eseguendo la seconda edizione. Il proprietario legge solo le sezioni 1, 2
e 13 (le domande aperte); il resto è per chi esegue.

## 1. Perché una seconda edizione (i fatti, con le fonti)

1. **La prima edizione ha trovato zero strategie, e lo ha fatto bene.** 630 varianti su 20 monete più 30 nel
   gruppo di 80: 45 candidate in costruzione, 7 in validazione, 3 al vault, 0 passate, contro 0,02 attese per
   puro caso (`research/confronto/risultati.md`). La prova a placebo dice che l'esame non lascia passare il
   rumore: 0 «nette» su 85 in costruzione, 2 su 93 sotto p 0,10 in validazione, dove il caso ne darebbe 9
   (`research/taratura/placebo_gruppo/risultati.md`).
2. **Gli effetti veri esistono ma sono più piccoli del costo di un giro.** L'ultima mezz'ora del giorno UTC
   rende 0,04-0,08 R lordi a trade in 6 campagne; il ritardo delle monete dopo un'ora forte di Bitcoin 0,04-0,09
   R nel gruppo (t 2,06 contro soglia 2,16). I costi a 15 minuti-1 ora valgono 0,05-0,14 R per giro
   (`research/confronto/risultati.md`).
3. **Gli ordini limite tagliano i costi di un terzo, non li azzerano.** Sulle nove strategie delle campagne il
   costo medio scende da 0,062 a 0,039 R a trade; l'ordine alla chiusura si esegue nel 98% dei casi, ma i trade
   saltati (2,4%) sono i migliori, R medio +0,68 (`research/esperimenti/ordini_limite/risultati.md`, sezione
   7). Esito «conviene poco».
4. **Il paper e il gate dicono la stessa cosa dal lato dell'esecuzione.** Nel paper il trade medio prima dei
   costi fa −0,015 R e i costi 0,095 R (ops 0596 e 0607, 12 ottobre); il gate passa lo 0,29% delle prove e le
   passate fanno −0,06 R a trade (ops 0601 e 0604). La ricerca automatica del gate è stata fermata il 13 ottobre
   (`ops/gate_fermo`).

Conclusione: sul terreno delle candele da 15 minuti a un'ora, con regole sui prezzi, un vantaggio netto dei costi
non c'è, o è troppo piccolo per essere misurato e pagato. La struttura dell'esame regge: cambia il terreno, non
l'esame.

## 2. Cosa cambia e cosa resta (la tabella che il proprietario approva)

| Cosa | Prima edizione (4.5) | Seconda edizione (5.0) | Perché |
|---|---|---|---|
| Candela dei segnali | da 15 minuti a 1 giorno, in pratica 15m-1h | **1 giorno (UTC)**, e basta | i costi a ore valgono quanto gli effetti; a giorni il costo per trade scende a circa 0,01 R (sezione 3.2) |
| Durata delle posizioni | ore | **da 2 giorni a 60 giorni** (uscita a tempo a 60 barre) | è l'orizzonte in cui tendenza e momentum sono documentati (sezione 5) |
| Unità di prova | una moneta per campagna, 20 campagne | **il paniere delle 80 monete del gruppo**, una campagna sola | una moneta a barre giornaliere dà 20-40 trade l'anno: non bastano (sezione 4) |
| Idee | 30 varianti per moneta, idee e ritocchi | **3 idee con fonte, al massimo 18 varianti, 3 ritocchi per famiglia e 12 in tutto** (numeri chiesti dal proprietario il 13 ott) | con 630 prove passa solo il rumore fortunato; con poche idee la soglia resta onesta |
| Ingresso | a mercato all'apertura della barra dopo | **ordine limite** alla chiusura della candela di segnale, valido un giorno, con la correzione 1 della prova | prova del 13 ottobre: regola misurata, costi −36% |
| Uscite | a mercato | a mercato (stop, segnale, tempo) | le uscite a limite non convengono (prova del 13 ottobre, variante c) |
| Costruzione / validazione | 70/30 per moneta | **taglio comune al 2023-01-16** (come il gruppo) | un taglio per data vale per tutte le monete insieme |
| Vault | 2024-01-01 → 2026-09-30, una apertura | **lo stesso periodo, una apertura per tutte le candidate insieme, con tre condizioni** (sezione 8) | il vault è stato aperto l'11 ottobre per tre strategie: va dichiarato, non rifatto |
| Esame finale | il paper «solo se l'utente lo chiede» | **il paper è l'esame finale, obbligatorio, con la regola scritta prima** (sezione 9); viene DOPO il vault, come ultimo passo | l'unico dato mai visto è il futuro |
| Sessioni | una per moneta, con guardiano | **una sola sessione di campagna che lavora su TUTTE le 80 monete insieme** (il paniere), branch `research/campagna/PANIERE`, guardiano come il gruppo | come la campagna di gruppo del 10-11 ottobre |

## 3. Il terreno: orizzonte, costi, esecuzione

### 3.1 Candele, decisioni, ordini
* I segnali si calcolano sulle **candele giornaliere UTC** (last price), chiuse. La decisione è alla chiusura del
  giorno `t` (00:00 UTC del giorno `t+1`).
* **Ingresso**: ordine limite al prezzo `P` = chiusura del giorno `t`, valido per il solo giorno `t+1`; eseguito se
  il minimo del giorno `t+1` è strettamente sotto `P` (long; simmetrico per lo short), riempito **a `P`** anche se
  il giorno apre oltre (correzione 1 della prova: un ordine nel libro esegue al suo prezzo); altrimenti il
  segnale è **saltato** e si conta. Commissione maker 0,02%, scarto zero. È la regola della prova del 13 ottobre
  (`research/esperimenti/ordini_limite/regole.md`, sezione 4) e quella che il bot esegue in paper dallo stesso
  giorno.
* **Uscite**: a mercato. Lo stop sulla serie last con la regola «stop prima» del motore; l'uscita «a segnale»
  all'apertura del giorno dopo; l'uscita a tempo dopo 60 barre. Commissione taker 0,05% più lo scarto della
  fascia della moneta (`scheda_moneta.md`, parametri del gruppo). Funding come oggi.
* Una posizione alla volta per moneta, come nel motore.

### 3.2 Il costo atteso per trade (stima, da misurare al Passo 0)
Per giro: 0,02% + 0,05% + scarto 0,01-0,10% = 0,08-0,17% del nozionale. Con lo stop iniziale a 2,5 ATR(20)
giornalieri, sulle monete del paniere la distanza dello stop è di norma fra il 6% e il 12% (stima: va misurata
al Passo 0 sui dati 2020-2023 e scritta in `parametri_2.yaml`); il nozionale vale quindi 8-16 volte il rischio e
il costo per trade **0,007-0,027 R**. Contro 0,05-0,14 R della prima edizione. Il numero vero lo dà la misura.

### 3.3 Dimensione, leva, esposizione
* Rischio per trade 1% del capitale, leva massima 2, margine isolated, regole di dimensione del bot
  (`research/config/parametri.yaml`, `regole_dimensione_bot`): invariate.
* Lo stop a multipli di ATR fa da solo la **pesatura per la volatilità**: una moneta più volatile ha una size
  più piccola (è la regola di dimensione del bot, non un'idea in più).
* Il **tetto di esposizione per verso** (nel bot: 3% del capitale a rischio nello stesso verso,
  `MAX_DIRECTIONAL_RISK_PCT`) nella ricerca si misura e si riporta (posizioni aperte insieme, rischio per verso
  per giorno), non si applica: l'esame esegue le monete una per una, come il gruppo. Nel paper vale.

### 3.4 Il funding a barre giornaliere (approssimazione dichiarata)
Il funding si regola ogni 8 ore; con barre di un giorno due settlement su tre cadono dentro la barra. Il motore
addebita ogni settlement sull'apertura della candela mark che lo contiene (sezione 7 della 4.5). Al Passo 0 si
misura la differenza fra il funding a barre di 1 giorno e quello a barre di 8 ore sugli stessi trade (BTCUSDT
2020-2023) e la si scrive: se supera 0,005 R per trade in media, si usano barre di 8 ore con i segnali calcolati
sulle chiusure giornaliere. Decisione al Passo 0, prima di qualunque variante.

## 4. Il paniere, non una moneta

* Le monete sono le **80 della campagna di gruppo** (`research/campagne/GRUPPO/monete.csv`), scelte il 10
  ottobre con i dati di prima del 2024 e il filtro di liquidità della sezione 2 delle regole del gruppo (20
  milioni di USDT al giorno, mese per mese), più BTCUSDT come serie di riferimento. Nessuna moneta si aggiunge o
  si toglie guardando i risultati.
* Perché non una moneta: a barre giornaliere una strategia di tendenza fa 5-15 trade l'anno per moneta; in
  quattro anni 20-60, meno dei 74-426 che avevano le campagne della prima edizione, e quelle non bastavano a
  distinguere 0,05 R dal caso. Il paniere ne dà 2.000-5.000 sommati, con la correzione per l'effetto grappolo
  (sezione 5, punto 9 delle regole del gruppo: nella prova a placebo 80 monete valevano circa 12 indipendenti).
  Per le idee trasversali (sezione 5, idea B) il paniere è l'idea stessa.
* Le monete che muoiono nel vault: sezione 10 delle regole del gruppo, invariata.

## 5. Le idee (scritte prima, con fonte, con il perché dovrebbero durare)

Tre idee (il proprietario ne ha chieste tre il 13 ottobre). Non se ne aggiungono durante la campagna: una quarta
idea richiede una fonte pubblica a questo orizzonte e un sì del proprietario PRIMA di iniziare. Ogni variante
qui sotto è una riga del budget (regola 6 della 4.5); le varianti si registrano in `ipotesi.md` prima del primo
test, con la previsione. Il budget è di **18 varianti** (6 per idea) più al massimo **3 ritocchi per famiglia e
12 in tutto**, decisi solo guardando la costruzione: al massimo 30 test.

### Idea A — Tendenza (time-series momentum, trend following)
* **Fonte.** Moskowitz, Ooi e Pedersen, «Time Series Momentum», Journal of Financial Economics 2012; Hurst, Ooi e
  Pedersen, «A Century of Evidence on Trend-Following Investing», Journal of Portfolio Management 2017; in
  cripto Liu e Tsyvinski, «Risks and Returns of Cryptocurrency», Review of Financial Studies 2021 (momentum a
  1-4 settimane).
* **Perché dovrebbe durare.** Le informazioni si diffondono lentamente e chi è in posizione segue il gregge: il
  prezzo continua per settimane dopo una rottura. È un premio documentato su cento anni e su ogni classe di
  attivi, con periodi lunghi in cui non paga. In cripto può essersi consumato dopo il 2021: è proprio ciò che
  l'esame deve dire.
* **Varianti (6).**
  * A1, rottura: long alla chiusura sopra il massimo degli ultimi N giorni, short sotto il minimo; N ∈ {20, 55}.
    Uscita a segnale: chiusura sotto il minimo (long) o sopra il massimo (short) degli ultimi N/2 giorni.
    → A1-20 long, A1-20 short, A1-55 long, A1-55 short.
  * A2, segno del rendimento: long se il rendimento degli ultimi 60 giorni è positivo e la chiusura è sopra la
    media semplice a 100 giorni; short simmetrico. Uscita a segnale quando una delle due condizioni cade.
    → A2 long, A2 short.
  * Per tutte: stop iniziale a 2,5 ATR(20) dalla chiusura di segnale; nessun target; uscita a tempo 60 barre;
    ingresso a limite (sezione 3.1). Niente trailing: le uscite sono quelle scritte, e basta.
* **Previsione di famiglia (scritta prima).** Se in costruzione nessuna variante batte nettamente la (b) di
  gruppo con R netto > 0, l'idea è morta a questo orizzonte e non si ritocca oltre il budget.

### Idea B — Momentum trasversale fra monete (le più forti contro le più deboli)
* **Fonte.** Liu, Tsyvinski e Wu, «Common Risk Factors in Cryptocurrency», Journal of Finance 2022: un modello a
  tre fattori (mercato, dimensione, momentum) con il momentum sui rendimenti delle 1-4 settimane precedenti;
  Jegadeesh e Titman 1993 per l'effetto in azioni.
* **Perché dovrebbe durare.** Sottoreazione alle notizie e flussi che inseguono i vincitori della settimana. È
  una scommessa RELATIVA: compra le forti e vende le deboli, quindi la direzione del mercato (il 2024 in salita,
  il 2025 in discesa) pesa meno sul risultato, e l'effetto grappolo fra le monete è più piccolo.
* **Varianti (6).** Ogni lunedì alle 00:00 UTC si ordinano le monete del paniere con dati (almeno 90 giorni di
  storia e mese liquido) per il rendimento delle ultime 4 settimane (B1) o 2 settimane (B2). Long le prime 10,
  short le ultime 10; si tiene fino al lunedì dopo, quando si riordina: una posizione resta aperta se la moneta
  è ancora nelle sue 10, altrimenti esce a segnale. B3 come B1 ma con le prime e le ultime 20 (metà del paniere
  in posizione: dice se l'effetto sta nelle code o è diffuso). Stop iniziale 2,5 ATR(20); uscita a tempo 60
  barre; ingresso a limite. → B1 long, B1 short, B2 long, B2 short, B3 long, B3 short. Per il motore (una
  moneta alla volta) la classifica è una serie esterna per moneta, calcolata dal paniere con sole chiusure fino
  al giorno `t` (`dati.serie_paniere`, Passo 0).
* **Previsione di famiglia (scritta prima).** Stessa regola dell'idea A.

### Idea C — Il ritardo delle monete dopo un giorno forte di Bitcoin (la terza, chiesta dal proprietario)
* **Fonte.** Ciaian, Rajcaniova e Kancs, «Virtual relationships: Short- and long-run evidence from BitCoin and
  altcoin markets», Journal of International Financial Markets, Institutions and Money 2018 (nel breve periodo
  Bitcoin guida le altre monete); e il risultato della campagna di gruppo del 10-11 ottobre: il ritardo delle
  monete dopo un'ora forte di Bitcoin rende +0,04-0,09 R lordi a 1 ora, t 2,06 contro soglia 2,16
  (`research/confronto/risultati.md`). A barre giornaliere non è mai stato provato.
* **Perché dovrebbe durare.** Bitcoin è dove arrivano prima i flussi e le notizie; le altre monete seguono con
  ritardo perché meno liquide e meno seguite. Rischio dichiarato: a un giorno il ritardo può essere già stato
  assorbito (a 1 ora c'era e non pagava i costi; a 1 giorno i costi sono dieci volte più piccoli, ma l'effetto
  può essere sparito).
* **Varianti (6).** Un «giorno forte» di Bitcoin è un giorno UTC con rendimento oltre `k` deviazioni standard dei
  suoi rendimenti giornalieri degli ultimi 60 giorni, `k` ∈ {1,5; 2}. Alla chiusura di quel giorno: long le
  monete del paniere con rendimento del giorno inferiore a quello di Bitcoin (C1: tutte le monete in ritardo;
  C2: solo le 20 più in ritardo); short simmetrico dopo un giorno forte negativo. Uscita a segnale dopo 5
  giorni (è la regola dell'idea: il ritardo si recupera in pochi giorni o non si recupera); stop 2,5 ATR(20);
  ingresso a limite. → C1-1,5 long, C1-1,5 short, C1-2 long, C1-2 short, C2-1,5 long, C2-1,5 short. La
  deviazione standard e il rendimento di Bitcoin vengono dalla serie di riferimento BTCUSDT (chiusure fino al
  giorno `t`).
* **Previsione di famiglia (scritta prima).** Stessa regola delle idee A e B.

Non sono idee, e non entrano nel budget: la pesatura per la volatilità (è lo stop ATR, sezione 3.3) e il tetto per
verso (sezione 3.3, si misura). «Tre idee sono poche» è una scelta: con 630 varianti la prima edizione ha dovuto
alzare la soglia a t 3,96 e ha passato solo rumore fortunato.

## 6. Dati e periodi

| Cosa | Valore |
|---|---|
| Serie | klines 1d, markPriceKlines 1d, fundingRate per le 80 monete e BTCUSDT, da `data.binance.vision`, con le impronte come nelle campagne |
| In-sample | dal primo giorno con dati di ogni moneta (mai prima del 2020-01-01) al 2023-12-31 |
| Costruzione | fino al 2023-01-16 compreso (taglio comune, come il gruppo) |
| Validazione | dal 2023-01-17 al 2023-12-31 |
| Vault | dal 2024-01-01 al 2026-09-30, uguale per tutte le monete, aperto una volta per tutte le candidate insieme (sezione 8) |
| Paper | dal giorno in cui il bot esegue la candidata, per 6 mesi o 150 trade sommati (sezione 9) |

Il caricatore dei dati rifiuta ogni data dopo il 2023-12-31 finché non esiste il marcatore della seconda edizione,
`research/vault/APERTURA_2.md`, che si crea solo dopo che il proprietario ha scritto in chat esattamente
«APRI IL VAULT 2» (Passo 0, punto 5). Il marcatore della prima edizione (`vault/APERTURA.md`, branch di
coordinamento) non vale per la seconda.

## 7. L'esame (quello della campagna di gruppo, a barre giornaliere)

1. **Costruzione e validazione**: la sezione 5 delle regole del gruppo, invariata: trade sommati in ordine fisso,
   blocco, baseline (a) (stessa uscita a ogni barra libera) e (b) (entrate casuali con semi 1000·j), strategie
   sfasate, «nettamente» con il pavimento delle sfasate, candidato = batte nettamente (a) e (b) con R medio
   netto > 0. Minimi di trade sommati: costruzione 300, validazione 100, vault 300 (sezione 4 e 9 delle regole del
   gruppo). Asticella: Benjamini-Hochberg al 10% sulle candidate in validazione (sezione 7 del gruppo).
2. **La prova a placebo si rifà a barre giornaliere** prima della prima variante (sezione 11 delle regole del
   gruppo, almeno 100 strategie finte senza vantaggio, stesso esame): a un giorno le barre sono poche e il
   blocco è grande; la prova dice se l'esame regge anche così. Se non regge, STOP e si corregge l'esame prima
   di qualunque idea.
3. **Il controllo positivo** (sezione 5, punto 10 delle regole del gruppo) a barre giornaliere, prima della prima
   variante.
4. **Le varianti dell'idea B** usano una serie di paniere: il controllo di causalità del Passo 0 verifica che la
   classifica del giorno `t` usi solo chiusure fino a `t`.

## 8. Il vault (2024-01-01 → 2026-09-30) e le tre condizioni

Il vault resta il periodo chiuso storico, perché prova un'idea in minuti su tre regimi diversi (2024 in salita,
2025 in discesa, 2026 misto). È stato aperto una volta, l'11 ottobre 2026, per tre strategie intraday della
prima edizione. Per la seconda edizione vale con tre condizioni, scritte qui prima di qualunque dato:

1. **Contaminazione dichiarata.** Si sa, e si scrive in testa a `ipotesi.md` della campagna: i risultati per anno
   di BTCUSDT-V10, BNBUSDT-045 e ADAUSDT-037 nel vault (profit factor 1,067, 0,55 e 0,79; R per anno;
   `research/vault/risultati.md`), i singoli trade di BNBUSDT-045 nel vault (`research/vault/BNBUSDT-045_vault.json`),
   il buy and hold per anno 2024-2026 di BTC, BNB e ADA (BTC +121% nel 2024; ADA −61% nel 2025 e −26% nel 2026), le
   1.000 entrate casuali di quelle tre, e quello che chiunque sa dell'andamento del 2024-2026. Nessun altro dato
   del vault è stato letto da una campagna.
2. **Nessuna idea nasce o si ritocca guardando il vault.** Le idee e le varianti della sezione 5 sono fissate in
   questo testo prima di qualunque dato; il guardiano blocca i dati dal 2024 in poi nella sessione di campagna;
   ogni variante si registra nel log prima del test (regole della 4.5). Le due idee vengono dalla letteratura e
   dal conto dei costi, non dai risultati dell'11 ottobre: lo dice la sezione 1.
3. **Una apertura sola, per tutte le candidate insieme**, con il criterio del vault di gruppo (sezione 9 delle
   regole del gruppo: profit factor dopo i costi almeno 1,10, almeno 300 trade sommati, risultato totale positivo,
   R medio sopra il 90° percentile delle sfasate del vault, tasso del caso riportato). Il giudizio è RELATIVO alle
   entrate casuali e alle sfasate con la stessa uscita: sapere che il 2024 è salito non aiuta una candidata a
   passare, perché anche le entrate a caso del 2024 salgono. Si riporta anche l'R per anno (2024, 2025, 2026):
   informazione, non condizione.

Il limite, detto prima: nessun periodo del passato è davvero chiuso, perché il passato lo conosciamo. Il
protocollo chiude l'USO del dato, non il dato. L'unico dato vergine è il futuro: per questo c'è la sezione 9.

## 9. Il paper come esame finale (regola scritta prima)

**La sequenza, per rispondere alla domanda del proprietario del 13 ottobre:** costruzione (fino al 2023-01-16) →
validazione (2023-01-17 → 2023-12-31) → vault (2024-01-01 → 2026-09-30, aperto una volta per tutte le candidate
insieme) → **paper**, che viene DOPO il vault ed è l'ultimo esame: ci arrivano solo le candidate che hanno
passato il vault. Sei mesi o 150 trade sommati, quello che arriva prima, con la regola qui sotto; poi decide il
proprietario.

1. **Chi va in paper.** Ogni candidata che passa il vault (al massimo una per idea: la migliore per t contro la
   (b) in validazione), eseguita dal bot sul paniere con le regole di questo protocollo: candele giornaliere,
   ordine limite d'ingresso, stop a 2,5 ATR(20), uscita a segnale e a tempo, rischio 1%, leva 2, tetto per
   verso 3%, in `DRY_RUN`. Il bot deve saper eseguire la strategia come codice (Passo 0, punto 7): se non può,
   si costruisce prima e si prova sui dati del vault che il paper riproduca il motore (parità, come per le
   campagne).
2. **Durata.** Fino a 150 trade sommati o 6 mesi dall'avvio, quello che arriva prima. Nessun ritocco durante il
   paper. I report sono quelli che il proprietario chiede (i report del mattino restano fermi fino a nuovo
   ordine).
3. **Passa se, alla scadenza, valgono tutte insieme:**
   * R medio netto > 0 sui trade del paper (costi reali dell'esecuzione simulata: maker, taker, scarto, funding);
   * batte nettamente la baseline (b) calcolata sullo stesso periodo con le candele vere (entrate casuali con la
     stessa uscita, 200 simulazioni, semi fissi), con l'esame di gruppo (sezione 5 delle regole del gruppo);
   * tasso di esecuzione degli ordini limite almeno 70% e costo medio per trade non oltre 1,5 volte quello del
     modello del vault (è la misura dell'esecuzione: se l'esecuzione vera costa il doppio, il vantaggio del
     vault non c'è più);
   * drawdown mai oltre 1,5 volte il massimo del vault (regola `paper_soglia_conferma` della 4.5).
4. **Bocciata altrimenti.** Un'idea bocciata in paper si chiude: niente seconda prova con ritocchi sul periodo del
   paper, che da quel momento è un dato visto.
5. **Dopo un «passa»** decide il proprietario. Il denaro vero non parte mai da solo: `DRY_RUN` resta `true` finché
   il proprietario non lo chiede esplicitamente, ripetutamente e consapevolmente (CLAUDE.md).

## 10. Il Passo 0 della seconda edizione (strumenti e fatti, prima della sessione)

Lo fa il coordinamento (la sessione che ha scritto questo testo), **sul branch principale**: con una campagna
sola non c'è niente da tenere nascosto fra campagne, e il principale è ciò che la macchina e la dashboard
leggono; la sessione di campagna lavorerà nel suo branch `research/campagna/PANIERE`. Finisce con una tabella e
uno STOP: niente parte senza l'approvazione di `research/config/parametri_2.yaml`. Dal 13 ottobre sera.

1. **Dati 1d**: scarico e impronte per le 80 monete e BTCUSDT (klines 1d, markPriceKlines 1d, fundingRate),
   2020-2023; verifica delle impronte; nessuna data oltre il 2023-12-31.
2. **Motore a barre giornaliere**: test del motore con candele di un giorno (ordine limite, stop, uscita a tempo
   in barre, funding con settlement dentro la barra); la misura della sezione 3.4 (1d contro 8h su BTCUSDT) e la
   decisione che ne segue.
3. **Serie di paniere** (`dati.serie_paniere`): classifica giornaliera delle monete per rendimento a N giorni,
   con il controllo di causalità (solo chiusure fino al giorno `t`) e i suoi test.
4. **Strumenti di gruppo a 1d**: `gruppo.py` con timeframe «1d»; la prova a placebo a 1d e il controllo
   positivo (sezione 7), con i loro risultati scritti PRIMA della prima variante.
5. **Il caricatore e il vault**: sul branch principale esiste `research/vault/APERTURA.md` (il vault della prima
   edizione, aperto l'11 ottobre), quindi oggi il caricatore accetterebbe date oltre il 2023-12-31. Il Passo 0 lo
   richiude per la seconda edizione: il caricatore accetta date oltre il 2023-12-31 SOLO se esiste
   `research/vault/APERTURA_2.md`, che si crea solo dopo la frase «APRI IL VAULT 2»; il marcatore della prima
   edizione non vale più. Il guardiano della sessione `PANIERE` ammette i dati delle 80 monete e di BTCUSDT a 1d,
   come per il gruppo.
6. **I parametri** in `research/config/parametri_2.yaml`: tutto ciò che qui è un numero (ATR, N, decili, 60
   barre, minimi di trade, costi, fasce), più la distanza media dello stop misurata al punto 2 e il costo
   atteso per trade che ne deriva. Approvati dal proprietario, poi congelati.
7. **Il bot**: cosa gli manca per eseguire una strategia di paniere a barre giornaliere come codice (oggi
   esegue combinazioni di indicatori a 15 minuti-1 ora; gli ingressi a limite ci sono dal 13 ottobre). Si decide
   qui cosa costruire; si costruisce solo se una candidata passa il vault (sezione 9, punto 1).

## 11. La sessione di campagna

«Sessione unica» vuol dire UNA sessione di lavoro che studia TUTTE le 80 monete insieme, come paniere: non una
moneta sola. Nella prima edizione c'erano 20 sessioni, una per moneta, ognuna cieca alle altre; qui l'unità di
prova è il paniere (sezione 4), i trade di tutte le monete si sommano nell'esame (sezione 7), e quindi serve una
sessione sola, come la campagna di gruppo del 10-11 ottobre. Risposta alla domanda del proprietario del 13
ottobre: monete multiple, tutte e 80, in una sessione.

Una sessione sola, `research/campagna/PANIERE`, aperta dal coordinamento con il messaggio di apertura approvato,
modello `claude-opus-5-5` e ultracode attivo (regola del proprietario dell'8 ottobre), guardiano con marcatore
`campagna PANIERE`, percorsi ammessi come per il gruppo (sezione 12 delle regole del gruppo), controllo ogni ora
dal coordinamento, domande girate subito al proprietario. Il budget della sezione 5 si usa per intero o si
dichiara l'avanzo (regola 6 della 4.5). Log in `research/campagne/PANIERE/log.jsonl`, formato della sezione 6
della 4.5.

## 12. Tempi (stime, servono solo ad annunciare i calcoli lunghi) e limiti

* Passo 0: uno o due giorni di lavoro di sessione (lo scarico dei dati 1d è leggero: 81 monete × 48 mesi × 3
  serie). Campagna: uno o due giorni (18 varianti più i ritocchi, con 80 monete ciascuna; la (b) e le sfasate a
  1d sono veloci). Vault: minuti. Paper: 3-6 mesi.
* Limiti dichiarati, oltre a quelli della sezione 11 della 4.5 e della sezione 15 delle regole del gruppo: il
  vault non è vergine (sezione 8); le idee sono tre per scelta; a un giorno i trade per moneta sono pochi e la
  potenza viene dal paniere e dalla correzione per grappolo; tendenza e momentum sono documentati fino al
  2021-2022 e possono essersi consumati; il funding a barre giornaliere è un'approssimazione misurata; le 80
  monete sono quelle liquide nel 2023 (le regole del gruppo trattano quelle che muoiono); i costi del vault sono
  stime per fascia, i costi del paper sono stime del simulatore del bot, non riempimenti veri.

## 13. Le domande al proprietario e le sue risposte (13 ottobre 2026, 19:34 UTC)

1. Approvi il testo? → **«approvo la seconda edizione»**.
2. Due idee e dieci varianti bastano? → **«3 idee e anche più varianti»**: aggiunta l'idea C (sezione 5), budget a
   18 varianti e 3 ritocchi per famiglia (12 in tutto).
3. Il taglio costruzione/validazione al 2023-01-16? → **«va bene»**.
4. Sei mesi (o 150 trade) di paper come esame finale? → domanda: «è sempre dopo il vault?». Sì: il paper è l'ultimo
   passo, dopo il vault (sezione 9, in testa). Se la risposta cambia la sua decisione, lo dice prima della fine
   del Passo 0.
5. La sessione unica? → domanda: «moneta unica o multiple?». Multiple: una sessione sola che lavora su tutte le
   80 monete insieme (sezione 11). Modello e ultracode come per le campagne precedenti, salvo diversa indicazione
   prima dell'apertura.

## Appendice — differenze dalla 4.5 in una riga ciascuna

Candela 1d invece di 15m-1h; posizioni da giorni a settimane; il paniere invece della moneta; tre idee e 18
varianti invece di 30 varianti per moneta; ingresso a limite; vault dichiarato e aperto una volta per tutte le candidate; il paper
come esame finale obbligatorio con la regola scritta prima; una sola sessione di campagna; il Passo 0 misura il
costo per trade e il funding a 1d prima di qualunque variante.

## Correzioni al testo dopo l'approvazione (solo in aggiunta, mai una riga cancellata)

1. **13 ott 2026, 20:40 UTC — minimi di trade sommati (sezione 7, punto 1).** Il testo cita «costruzione 300,
   validazione 100, vault 300» come se fossero quelli delle regole del gruppo: non lo sono. Le regole del gruppo
   (`parametri.yaml`, blocco `gruppo.trade_minimi`) dicono **costruzione 700, validazione 300, vault 300**, e
   sono questi che valgono anche per la seconda edizione: nessun motivo per abbassarli (a barre giornaliere il
   paniere dà 1.500-2.500 trade sommati in costruzione per le idee A e B, stima da verificare al Passo 0). Trovata
   rileggendo il testo prima del Passo 0, prima di qualunque dato.
2. **13 ott 2026, 20:45 UTC — il vault è richiuso (sezione 10, punto 5): fatto.** `research/src/dati.py` accetta
   date oltre il 2023-12-31 solo con `research/vault/APERTURA_2.md`; `APERTURA.md` dell'11 ottobre non apre più;
   il guardiano guarda lo stesso marcatore. Test in `research/src/tests/test_dati.py`.
3. **14 ott 2026, 05:05 UTC — lo STOP del Passo 0 è sciolto: le quattro decisioni del proprietario («procedi»).**
   Il rapporto del Passo 0 (`research/passo0_2/rapporto.md`, sezione «Lo STOP») chiedeva quattro cose; il
   proprietario ha risposto «procedi» il 14 ottobre alle 05:00 UTC circa (le 07:00 in Italia), cioè sì a tutte come proposte:
   1. `research/config/parametri_2.yaml` è approvato così com'era (stato `congelato`, `approvazione_parametri`
      scritta nel file).
   2. **La potenza dell'esame a un giorno: strada (a), l'esame resta com'è** (sezione 7, punto 1). A barre
      giornaliere passano solo vantaggi grandi o idee con posizioni brevi (più blocchi): è il prezzo di non farsi
      ingannare (la prova a placebo dà 0 falsi positivi su 47). In più: una variante «non netta» per pochi blocchi
      si riporta sempre con il suo `t` contro la (b) e il numero di blocchi, così si vede.
   3. **Le monete su cui gli ingressi casuali della (b) non entrano** (sezione 7, punto 1, che eredita la sezione 5,
      punto 4, delle regole del gruppo: «la variante è non valutabile se su una moneta gli ingressi non entrano»).
      Nella seconda edizione vale questa regola, scritta qui PRIMA della modifica agli strumenti e prima di
      qualunque variante: una moneta j con n_j > 0 su cui `simula_baseline_casuale` non riesce a piazzare gli
      n_j ingressi casuali («impossibile piazzare», `statistica.entrate_casuali_per_semi`) **resta fuori dalla
      combinazione della (b) di gruppo**, esattamente come una moneta con 0 trade della (a) resta fuori dalla
      (a): le M(s) si calcolano sulle altre monete con i pesi n_j del candidato (come già succede nelle
      simulazioni in cui una moneta non ha trade), la sua b_j non esiste. L'R medio del candidato, il blocco, la
      (a) e le strategie sfasate restano su TUTTI i trade. L'esame riporta le monete lasciate fuori (quante e
      quali) e la quota dei trade del candidato che portano; **la variante è non valutabile contro la (b) se
      quelle monete portano più del 10% dei trade del candidato** (la stessa frazione della (a),
      `statistica.QUOTA_MASSIMA_FUORI_DALLA_A`, confronto esatto sugli interi: 10 · trade lasciati fuori > N),
      oltre ai motivi di prima (una moneta con meno di 2 simulazioni con trade, meno di 2 M(s)). Lo calcola solo
      `statistica.baseline_casuale_di_gruppo`. Senza monete lasciate fuori i numeri sono quelli di prima, bit per
      bit: la prova a placebo a 1 ora e i risultati della campagna di gruppo non cambiano. Dopo la modifica la
      prova a placebo a 1d e il controllo positivo si rifanno con gli strumenti nuovi, e l'esito si scrive nelle
      regole della campagna PANIERE prima dell'apertura.
   4. **Il funding a giorni** (long su Bitcoin: +0,23 R a trade nel 2020-2023): nessuna decisione; resta dentro il
      motore e dentro l'esame, da ricordare quando si leggono i risultati.
4. **14 ott 2026, 05:05 UTC — la dichiarazione di contaminazione (sezione 8, condizione 1) senza trasmetterla.** La
   sessione di campagna non legge `research/PROTOCOLLO_2.md` (il guardiano glielo nega: la sezione 8 contiene i
   risultati del vault della prima edizione e l'andamento del 2024-2026). In testa a `ipotesi.md` la sessione
   scrive quindi una frase di rimando, dettata dalle regole della campagna (`research/campagne/PANIERE/regole.md`),
   che dichiara la contaminazione senza ricopiare i numeri: così resta dichiarata senza passare alla sessione che
   sceglie i ritocchi. Le idee, le varianti e il terreno che la sessione deve conoscere (sezioni 3, 5 e 7) sono
   ricopiati nelle regole della campagna, in sola lettura, parola per parola.
