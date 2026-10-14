# Campagna del paniere (seconda edizione del protocollo) — regole della sessione

> **In vigore dal 2026-10-14 06:56 UTC** (preso con `date -u` subito prima del commit che apre la campagna; è l'istante che
> il controllo della sezione 9 del protocollo usa per `research/campagna/PANIERE`). Testo scritto dal coordinamento al
> Passo 0 della seconda edizione e completato il 14 ottobre 2026 dopo il «procedi» del proprietario (05:00 UTC circa).

Testo scritto dal coordinamento al Passo 0 della seconda edizione (`research/PROTOCOLLO_2.md`, approvata dal
proprietario il 13 ottobre 2026). In sola lettura per la sessione di campagna, come `monete.csv`, le `schede/` e
`via_libera_validazione.md` (guardiano, `_PROTETTI_FILE`).

## 1. Che cosa vale

* Il testo in vigore è `research/PROTOCOLLO_2.md` (versione 5.0), con tutto ciò che la sua sezione 0 tiene in
  vigore della 4.5 (`research/PROTOCOLLO.md`) e delle regole della campagna di gruppo
  (`research/campagne/GRUPPO/regole.md`). Dove i tre testi dicono cose diverse vale, nell'ordine: PROTOCOLLO_2,
  poi le regole del gruppo, poi la 4.5. **La sessione di campagna NON legge `PROTOCOLLO_2.md`** (il guardiano
  glielo nega: contiene, nella sezione 8, i risultati del vault della prima edizione): tutto ciò che le serve di
  quel testo (le sezioni 3, 4, 5 e 7 e le correzioni) è ricopiato parola per parola nella sezione 7 di questo file,
  che per lei vale come l'originale.
* La sessione lavora con il marcatore `{"tipo": "campagna", "simbolo": "PANIERE"}`, sul branch
  `research/campagna/PANIERE`, nella cartella `research/campagne/PANIERE/`. Il guardiano la tratta come la campagna
  di gruppo (sezione 12 delle regole del gruppo): dati in-sample delle sole 80 monete di `monete.csv` (e di BTCUSDT),
  la propria cartella, `research/src`, `research/config` in sola lettura.

## 2. Le monete, i dati, i periodi

* Le 80 monete sono quelle di `monete.csv` (identico, byte per byte, a quello del gruppo: stessa impronta approvata
  nel guardiano); le `schede/` dicono per ognuna il primo mese di dati e la fascia di scarto per lato, tutto vero al
  31 dicembre 2023.
* I dati sono le candele giornaliere (`klines/1d`, `markPriceKlines/1d`) e il funding, dal primo mese della scheda al
  2023-12-31, per le 80 monete e per BTCUSDT: il coordinamento li ha scaricati e verificati al Passo 0 e ha scritto
  in `impronte_1d.json` il SHA-256 di ogni file (9.406 file, `{simbolo: {nome relativo: impronta}}`, i nomi come
  li dà `dati.calcola_impronte`). I dati non sono in git: **la sessione li riscarica** in `research/data/insample/<S>/`
  (Fase 0 del gruppo, sezione 2 delle sue regole, punti 2, 4, 5 e 9: solo con `research/src/dati.py`, per esempio
  `dati.scarica_periodo(simbolo, tipo, timeframe, 2020-01-01, 2023-12-31, radice=...)` per `klines` 1d,
  `markPriceKlines` 1d e `fundingRate`; nessun altro timeframe, nessuna data oltre il 2023-12-31) e, prima di qualunque
  calcolo, confronta ogni moneta con `dati.verifica_impronte(simbolo, radice, impronte_1d[simbolo])`: un file
  registrato che manca o ha un'impronta diversa è STOP (si scrive all'utente; nessuna moneta esce). Il file
  `fase0_dati.md` della sessione riporta per moneta mesi presenti, buchi, barre tolte dall'allineamento e mesi sotto
  la liquidità, come per il gruppo; non serve riscrivere le impronte: valgono quelle di `impronte_1d.json`.
* Periodi (sezione 6 di PROTOCOLLO_2): costruzione fino al 2023-01-16 compreso, validazione dal 2023-01-17 al
  2023-12-31 (`dati.periodi_gruppo` sulle schede); il vault e il paper non sono di questa sessione.
* Il timeframe dei segnali è «1d» e basta.

## 3. Le idee e il budget

* Le tre idee, le 18 varianti e i ritocchi (3 per famiglia, 12 in tutto) sono quelli della sezione 5 di PROTOCOLLO_2:
  si registrano in `ipotesi.md` e nel log prima del primo test, con la previsione, e non si inventano idee nuove.
* Esecuzione: ingresso con ordine limite alla chiusura della candela di segnale, valido una candela, condizione
  «attraversato», maker 0,02%, scarto zero (`motore.Parametri`: `ingresso="limite"`,
  `limite_validita_barre=1`, `commissione_maker_per_lato=0.0002`); uscite a mercato con lo scarto della fascia della
  scheda; stop 2,5 ATR(20); uscita a tempo 60 barre; rischio 1%, leva 2, isolated. I numeri sono in
  `research/config/parametri_2.yaml` (approvato dal proprietario il 14 ottobre 2026, stato `congelato`) e non si
  cambiano.
* Ogni variante si riporta con il suo `t` contro la (b) e il numero di blocchi, anche quando non è «netta»: a
  barre giornaliere una posizione lunga fa pochi blocchi e un vantaggio può non risultare «netto» per quello
  (decisione del proprietario del 14 ottobre, sezione 6).

## 4. L'esame

* Lo esegue solo `research/src/gruppo.py` (`esame_di_gruppo`, `conta_trade_di_gruppo`, `controllo_positivo`) con
  `timeframe="1d"`, come per il gruppo: trade sommati, blocco, baseline (a) e (b) per moneta (semi 1000·j + s),
  strategie sfasate, «nettamente», candidato. I numeri dell'esame sono quelli del blocco `gruppo` di
  `research/config/parametri.yaml` (trade minimi 700 in costruzione, 300 in validazione; budget e ritocchi di
  PROTOCOLLO_2 prevalgono su quelli del blocco).
* **Le monete su cui gli ingressi casuali della (b) non entrano** (correzione 3 di PROTOCOLLO_2, 14 ottobre 2026,
  copiata nella sezione 7): restano fuori dalla combinazione della (b) come una moneta senza trade della (a) resta
  fuori dalla (a); la variante è non valutabile contro la (b) se portano più del 10% dei trade del candidato.
  L'esame le riporta (`baseline_b`: `monete_senza_ingressi`, `trade_candidato_senza_ingressi`,
  `quota_trade_candidato_senza_ingressi`; per moneta `b_ingressi_entrano`), e la sessione le scrive nel log della
  variante, quante e quali. Non si fa nulla per evitarle (niente monete tolte a mano, niente ritocchi per questo).
* Il modulo della variante segue il contratto della docstring di `gruppo.py`; la serie di paniere per le idee B e
  C (`research/src/paniere.py`) va calcolata nel modulo dalle candele che `gruppo.py` passa (BTCUSDT compreso),
  mai da file letti dal modulo.
* La prova a placebo a barre giornaliere (`research/taratura/placebo_paniere/`) e il controllo positivo devono essere
  passati PRIMA della prima variante: li fa il coordinamento e scrive l'esito qui sotto, sezione 6.

## 5. Log, consegna, cosa non si fa

* Log in `log.jsonl` (formato della sezione 6 della 4.5), solo in aggiunta. Consegna come nella sezione 8 delle
  regole del gruppo.
* Non si legge nulla delle campagne della prima edizione (nemmeno `campagne/GRUPPO/`, tranne i file che il
  guardiano ammette), né `research/confronto/`, `research/vault/`, `docs/`, il bot.
* Nessun dato oltre il 2023-12-31: il caricatore lo rifiuta (marcatore `vault/APERTURA_2.md`, che questa sessione
  non crea mai).
* **In testa a `ipotesi.md`**, prima di qualunque ipotesi, la sessione scrive questa frase, così com'è (è la
  dichiarazione di contaminazione della sezione 8 di PROTOCOLLO_2, condizione 1, fatta senza ricopiare i numeri:
  correzione 4): «Contaminazione dichiarata dal coordinamento (PROTOCOLLO_2, sezione 8, condizione 1): tre
  strategie intraday della prima edizione sono state giudicate nel vault 2024-2026 l'11 ottobre 2026; questa
  sessione non ha letto quei risultati né alcun dato dal 2024-01-01, e le idee e le varianti qui sotto sono
  quelle fissate nel testo prima di qualunque dato.»

## 6. Esiti scritti dal coordinamento prima dell'apertura

Scritti il 13 ottobre 2026 (22:10 UTC) dal coordinamento, a Passo 0 finito.

* **Prova a placebo a barre giornaliere** (`research/taratura/placebo_paniere/risultati.md`, 96 esami, commit
  e98d0fec): **l'esame di gruppo regge**. 47 placebo valutabili per periodo (minimo 40); «nette» in costruzione 0 su
  47 (soglia 3%); p sotto 0,10 in validazione 0 su 47 (soglia 13%); code M3 0,35% e 0,58%; 1 scarto, 1 non
  valutabile. In validazione 3 placebo su 47 (6,4%) hanno l'R medio sopra il 90° percentile delle proprie sfasate
  (atteso circa 10%): l'esame a un giorno è, se mai, severo. Due correzioni scritte prima di qualunque esito
  (regole della prova, sezione 7): parametri da manuale più corti per il giorno e durata massima di 60 barre.
* **Controllo positivo a 1d** (`research/passo0_2/controllo_positivo_1d.json` e `..._sottoinsieme.json`, regola
  «rottura» con uscita ATR e tetto di 60 barre, ingressi che guardano avanti): **non passa nella forma delle regole
  del gruppo**, per due motivi che la sessione deve sapere. (1) Sulle 80 monete la baseline (b) non si costruisce:
  la strategia che guarda avanti è in posizione quasi sempre e su 13 monete (long) e 16 (short) con la serie
  giornaliera più corta «gli ingressi casuali non entrano» (serve lo stesso numero di ingressi distanziati della
  durata media, e le barre non bastano). (2) Sulle monete restanti (67 long, 64 short): short, senza ritardo R medio
  +0,29, t 2,42 contro la (b) con 7 blocchi (non «netto»: la soglia con 6 gradi è 2,6), con il ritardo t −0,67 (il
  ritardo cancella il vantaggio: condizione passata); long, la (b) non entra ancora su una moneta (ROSEUSDT), con
  il ritardo t −0,35. **Lezione per la campagna:** a barre giornaliere una variante che resta in posizione a lungo
  ha pochi blocchi (il blocco è la posizione più lunga: 60 barre = 5% della costruzione) e un pavimento alto; con
  pochi blocchi anche un vantaggio di +0,3 R a trade non è «netto». E una variante con molti trade su una moneta
  dalla storia corta può non essere valutabile perché la (b) non entra. La sessione lo riporta variante per
  variante; il proprietario ha deciso allo STOP cosa fare di queste due cose (vedi `research/passo0_2/rapporto.md`).
* **Impronte degli strumenti al termine del Passo 0** (quelle della prova a placebo, `regole.md` della prova,
  sezione 6): `research/src/motore.py` 2adb94e1…, `research/src/dati.py` 4f0d4779…, `research/src/statistica.py`
  ca027d26…, `research/src/gruppo.py` 6875b12f…, `research/config/parametri.yaml` 7f530082…. Il via libera alla
  validazione (`via_libera_validazione.md`) lo scrive il coordinamento con le impronte complete al momento giusto.
* **Le decisioni del proprietario allo STOP del Passo 0** (14 ottobre 2026, 05:00 UTC circa: «procedi»,
  PROTOCOLLO_2, correzione 3): (1) `parametri_2.yaml` approvato e congelato; (2) l'esame resta com'è, e ogni
  variante si riporta con `t` e numero di blocchi (sezione 3); (3) le monete su cui la (b) non entra restano fuori
  dalla (b) con la regola del 10% (sezione 4); (4) il funding a giorni resta dentro motore ed esame (long su
  Bitcoin tenuto 25 giorni nel 2020-2023: +0,23 R a trade in media, 24 trade della misura del Passo 0). Con la
  regola (3) `statistica.py` e `gruppo.py` sono cambiati (14 ottobre): le impronte buone sono quelle dei
  ricontrolli qui sotto, non più quelle del punto precedente.
* **Ricontrolli con gli strumenti nuovi** (prova a placebo a 1d e controllo positivo a 1d rifatti dopo la
  correzione 3): esito e impronte li scrive il coordinamento qui sotto prima dell'apertura della sessione.
  * **Controllo positivo a 1d con la regola nuova** (`research/passo0_2/controllo_positivo_1d_regola3.json`, 14
    ottobre, stessa regola «rottura» con uscita ATR e tetto di 60 barre, ingressi che guardano avanti, 80 monete):
    **non passa**, e la sessione deve sapere perché. Senza ritardo le monete su cui la (b) non entra portano il
    12,0% dei trade (long: 13 monete, 424 su 3.535) e il 13,3% (short: 16 monete, 457 su 3.427), oltre il 10%:
    confronto con la (b) non valutabile. Con il ritardo di una barra la (b) si costruisce (3 e 6 monete fuori, 1,1% e
    3,7% dei trade) e il `t` è −0,28 (long) e −0,55 (short): il vantaggio sparisce come deve. Contro la (a), senza
    ritardo, `t` 1,47 e 1,46 con 7 blocchi (R medio +0,37 e +0,27 a trade contro +0,04 e −0,08 della (a), effetto
    grappolo 39 e 30): non «netto», ed è la stessa lezione del 13 ottobre: con posizioni fino a 60 barre i blocchi
    sono 7 e un vantaggio anche di +0,3 R a trade non risulta netto. **Per la sessione:** il controllo positivo
    che farai con il tuo modulo (regole del gruppo, sezione 5, punto 10) a barre giornaliere può non passare per
    questi due motivi, non per un errore degli strumenti; riportalo com'è (t, blocchi, monete senza ingressi e
    loro quota) e scrivilo all'utente senza fermarti, salvo un errore vero (eccezione, numeri assurdi, con il
    ritardo un `t` che non scende).
  * **Prova a placebo a 1d rifatta con gli strumenti nuovi** (`research/taratura/placebo_paniere/risultati.md`, 14
    ottobre, 06:56 UTC, commit c9bb86ad; i 96 esiti del 13 ottobre sono in `lancio_13ott/`): **regge**, con i 96
    esami identici bit per bit a quelli del 13 ottobre (nessuna placebo aveva monete senza ingressi, come atteso):
    47 valutabili per periodo, 0 «nette» su 47 in costruzione, 0 su 47 con p sotto 0,10 in validazione, code M3
    0,35% e 0,58%.
  * **Impronte degli strumenti buone per questa campagna** (sezione 6 delle regole della prova a placebo, rilancio
    del 14 ottobre; sono quelle che il via libera alla validazione dovrà ritrovare):
    * `7f530082d7d5119d9e12e99a0bbe44548f9671c9b28aa70f77f97d6c2b4edfa7`  `research/config/parametri.yaml`
    * `1a5c36e48386b3705b462da9cd402c772e8521863d6230e105e9c4d79c0d5ad5`  `research/src/dati.py`
    * `1072203ce9014601d9dd55bbf3f58efdaa38a9f1b187b80b3d77f6881f90f990`  `research/src/gruppo.py`
    * `2adb94e11196e9af4dcc9f2b07ac42ad6a8cfda1399b5171f019585c8f5f78f6`  `research/src/motore.py`
    * `e42edc0082ff0e52b8d1e1a65493f912c98fd7fbf083bf53dbe0d742ef95b7a1`  `research/src/statistica.py`

## 7. Copia parola per parola delle sezioni 3, 4, 5 e 7 di `research/PROTOCOLLO_2.md` e delle sue correzioni

Copiate dal coordinamento il 14 ottobre 2026 (dopo la correzione 4) dal testo in vigore sul branch principale, senza
cambiare una parola (solo i titoli sono abbassati di un livello, per non confonderli con le sezioni di questo
file): per la sessione di campagna valgono come l'originale (sezione 1). I rimandi a «sezione N» dentro
la copia sono alle sezioni di PROTOCOLLO_2 (le sezioni 1, 2, 6, 8-13 non sono qui: non servono alla sessione, e la
8 contiene ciò che la sessione non deve leggere). Nella copia della sezione 7, punto 1, i minimi «300, 100, 300» sono
corretti dalla correzione 1 in **700, 300, 300**.

---

### 3. Il terreno: orizzonte, costi, esecuzione

#### 3.1 Candele, decisioni, ordini
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

#### 3.2 Il costo atteso per trade (stima, da misurare al Passo 0)
Per giro: 0,02% + 0,05% + scarto 0,01-0,10% = 0,08-0,17% del nozionale. Con lo stop iniziale a 2,5 ATR(20)
giornalieri, sulle monete del paniere la distanza dello stop è di norma fra il 6% e il 12% (stima: va misurata
al Passo 0 sui dati 2020-2023 e scritta in `parametri_2.yaml`); il nozionale vale quindi 8-16 volte il rischio e
il costo per trade **0,007-0,027 R**. Contro 0,05-0,14 R della prima edizione. Il numero vero lo dà la misura.

#### 3.3 Dimensione, leva, esposizione
* Rischio per trade 1% del capitale, leva massima 2, margine isolated, regole di dimensione del bot
  (`research/config/parametri.yaml`, `regole_dimensione_bot`): invariate.
* Lo stop a multipli di ATR fa da solo la **pesatura per la volatilità**: una moneta più volatile ha una size
  più piccola (è la regola di dimensione del bot, non un'idea in più).
* Il **tetto di esposizione per verso** (nel bot: 3% del capitale a rischio nello stesso verso,
  `MAX_DIRECTIONAL_RISK_PCT`) nella ricerca si misura e si riporta (posizioni aperte insieme, rischio per verso
  per giorno), non si applica: l'esame esegue le monete una per una, come il gruppo. Nel paper vale.

#### 3.4 Il funding a barre giornaliere (approssimazione dichiarata)
Il funding si regola ogni 8 ore; con barre di un giorno due settlement su tre cadono dentro la barra. Il motore
addebita ogni settlement sull'apertura della candela mark che lo contiene (sezione 7 della 4.5). Al Passo 0 si
misura la differenza fra il funding a barre di 1 giorno e quello a barre di 8 ore sugli stessi trade (BTCUSDT
2020-2023) e la si scrive: se supera 0,005 R per trade in media, si usano barre di 8 ore con i segnali calcolati
sulle chiusure giornaliere. Decisione al Passo 0, prima di qualunque variante.

### 4. Il paniere, non una moneta

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

### 5. Le idee (scritte prima, con fonte, con il perché dovrebbero durare)

Tre idee (il proprietario ne ha chieste tre il 13 ottobre). Non se ne aggiungono durante la campagna: una quarta
idea richiede una fonte pubblica a questo orizzonte e un sì del proprietario PRIMA di iniziare. Ogni variante
qui sotto è una riga del budget (regola 6 della 4.5); le varianti si registrano in `ipotesi.md` prima del primo
test, con la previsione. Il budget è di **18 varianti** (6 per idea) più al massimo **3 ritocchi per famiglia e
12 in tutto**, decisi solo guardando la costruzione: al massimo 30 test.

#### Idea A — Tendenza (time-series momentum, trend following)
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

#### Idea B — Momentum trasversale fra monete (le più forti contro le più deboli)
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

#### Idea C — Il ritardo delle monete dopo un giorno forte di Bitcoin (la terza, chiesta dal proprietario)
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

### 7. L'esame (quello della campagna di gruppo, a barre giornaliere)

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

### Correzioni al testo dopo l'approvazione (solo in aggiunta, mai una riga cancellata)

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

5. **14 ott 2026, 09:15 UTC — la serie di paniere arriva alla variante (sezione 5, idea B e variante C2; sezione 10,
   punto 3): scelta (a) del proprietario.** Alla fine della Fase 0 la sessione di campagna ha fatto notare che le
   funzioni della variante ricevono da `gruppo.py` solo le candele della propria moneta e di BTCUSDT: la classifica
   del paniere (idea B) e «le 20 monete più in ritardo» (C2) non si possono calcolare. Il Passo 0, punto 3, aveva
   costruito la serie (`paniere.py`) senza il passaggio alla variante. Domanda girata al proprietario alle 09:00 UTC
   («(a) estendere gruppo.py e rifare il placebo, oppure (b) lavorare solo su A e C1»); risposta «a» alle 09:05 UTC.
   Cosa cambia, scritto prima del rilancio della prova: (1) il contesto della variante ha `ctx.paniere_chiuse_entro(ts)`,
   le righe GIORNALIERE del paniere (un giorno UTC per riga: `ts`, `close_ts`, `chiusure` = {simbolo: chiusura last 1d}
   di tutte le monete dell'esame e di BTCUSDT con la candela quel giorno, `sotto_liquidita` = le monete il cui mese è
   sotto la soglia), limitate alla chiusura dell'ultima barra ricevuta come le candele di BTCUSDT (mai una riga del
   futuro), costruite una volta per esame nel processo principale dalle stesse serie 1d della Fase 0 e incluse
   nell'impronta dei dati di ogni pezzo; (2) il contesto ha `ctx.simbolo`, il simbolo della moneta del pezzo, che
   serve SOLO a trovare la propria moneta nel paniere: resta vietata una regola che tratta una moneta diversamente
   dalle altre per nome (la regola della sezione 3, punto 3, delle regole del gruppo, «niente strategie fra monete»,
   è superata per la seconda edizione dalla sezione 5 di questo testo, che le idee B e C sono); (3) il modulo della
   variante può importare `research.src.paniere`, che ha tre funzioni «dell'ultimo giorno» sulle righe
   (`rendimenti_ultimo_giorno`, `classifica_ultimo_giorno` con la stessa regola di parità di `classifica`,
   `giorno_forte_ultimo` con la deviazione dei 60 giorni precedenti), con i test che le confrontano con le funzioni
   sulle matrici intere; (4) **il terreno d'ingresso negli strumenti** (seconda nota della sessione, 09:14 UTC: gli
   strumenti costruivano i parametri del motore con l'ingresso a mercato della prima edizione): `gruppo.py` costruisce
   da solo i `Parametri` del motore con l'ordine limite della sezione 3.1 (alla chiusura della candela di segnale,
   valido una candela, condizione «attraversato», maker 0,02%, scarto zero all'ingresso; uscite a mercato con lo
   scarto della scheda), letti da `research/config/parametri_2.yaml` congelato (`terreno_seconda_edizione`), e li
   riporta nelle opzioni dell'esame (quindi nella sua impronta). In una sessione di campagna il terreno lo decide il
   marcatore (PANIERE: seconda edizione) e la sessione non può chiederne un altro; fuori campagna lo sceglie chi
   chiama (la prova a placebo del paniere e il vault passano «seconda_edizione»). Per una variante che non usa il
   paniere e con il terreno della prima edizione i numeri dell'esame non cambiano (test). **La prova a placebo a 1d si
   rifà con gli strumenti nuovi e con il terreno della seconda edizione** prima che la sessione registri la prima
   variante: con l'ordine limite i riempimenti cambiano, quindi i numeri NON saranno quelli del 13 ottobre (atteso,
   scritto prima: cambiano i trade, deve reggere lo stesso l'esame, con le soglie delle regole della prova); e il
   controllo positivo si rifà con lo stesso terreno. La correzione entra nel branch della campagna al suo STOP
   (regole del gruppo, sezione 11, punto 6). Nessuna variante è stata esaminata prima della correzione: la sessione
   si è fermata alla Fase 0 per questo.

## 8. Correzioni (solo in aggiunta, scritte dal coordinamento; dove dicono cose diverse dalle sezioni sopra, valgono loro)

### Correzione 1 — come la variante riceve la serie di paniere (14 ottobre 2026, dopo la scelta (a) del proprietario)

La sezione 4 dice che la serie di paniere per le idee B e C «va calcolata nel modulo dalle candele che `gruppo.py`
passa». Alla Fase 0 la sessione ha fatto notare che `gruppo.py` passava solo le candele della propria moneta e di
BTCUSDT: non bastano. Il proprietario ha scelto di estendere lo strumento (correzione 5 di PROTOCOLLO_2, copiata
qui sotto nella sezione 7 alla voce «Correzioni al testo»). Da questa correzione in poi, in `research/src/gruppo.py`
(contratto nella docstring, punto 3):

* `ctx.paniere_chiuse_entro(ts)` dà le righe giornaliere del paniere viste fino a `ts` e mai oltre la chiusura
  dell'ultima barra ricevuta: ogni riga ha `ts` (apertura del giorno UTC), `close_ts`, `chiusure` (il dizionario
  {simbolo: chiusura last 1d} delle 80 monete e di BTCUSDT che hanno la candela quel giorno, in sola lettura) e
  `sotto_liquidita` (le monete il cui mese è sotto la soglia di liquidità quel giorno). Un giorno per riga, tutti i
  giorni del calendario dal primo giorno di dati della moneta più antica alla fine del periodo. A barre giornaliere
  la riga del giorno `t` ha lo stesso `close_ts` della candela di `t`: alla chiusura di `t` la variante la vede.
* `ctx.simbolo` è il simbolo della moneta del pezzo. Serve SOLO a trovare la propria moneta nella classifica: una
  regola che tratta una moneta diversamente dalle altre per nome resta vietata (regole del gruppo, sezione 3, punto
  3, che per il resto è superata dalle idee B e C della seconda edizione).
* Il modulo della variante può importare `research.src.paniere`, che ha tre funzioni per le righe del paniere, da
  chiamare alla chiusura di ogni barra: `classifica_ultimo_giorno(righe, n_giorni, storia_minima=0)` → ({simbolo:
  rango}, n_monete), rango 1 = rendimento a `n_giorni` più alto, parità alfabetica, BTCUSDT escluso, fuori le monete
  sotto la liquidità nel giorno e, con `storia_minima`, quelle senza una chiusura `storia_minima` giorni prima;
  `rendimenti_ultimo_giorno` (lo stesso senza la classifica); `giorno_forte_ultimo(chiusure, k, n=60, minimo=40)`
  → +1, −1 o 0 per l'ultimo giorno di una sequenza di chiusure (per esempio quelle di BTCUSDT da
  `ctx.btc_chiuse_entro`), con la deviazione standard dei `n` rendimenti precedenti. I loro test le confrontano con
  le funzioni sulle matrici intere (`research/src/tests/test_paniere.py`).
* Per l'idea B «ogni lunedì alle 00:00 UTC» è la chiusura della candela di domenica: la classifica si legge alla
  chiusura della barra della domenica (riga del paniere di quel giorno) e l'ordine limite vale per il lunedì.
* Le righe del paniere stanno nell'impronta dei dati di ogni pezzo e si riportano nel risultato (`paniere`: giorni,
  monete, estremi, impronta).
* **Il terreno d'ingresso lo costruisce `gruppo.py`** (seconda nota della sessione, 09:14 UTC): con il marcatore
  PANIERE ogni esame (`conta_trade_di_gruppo`, `esame_di_gruppo`, `controllo_positivo`) usa da solo i `Parametri` del
  motore con l'ordine limite della sezione 3 (letti da `research/config/parametri_2.yaml`: ingresso a limite alla
  chiusura della candela di segnale, valido una candela, condizione «attraversato», maker 0,02%, scarto zero
  all'ingresso; uscite a mercato con lo scarto della scheda; stop, uscita a segnale e a tempo restano nel modulo
  della variante) e li riporta in `opzioni.terreno`; l'argomento `terreno` delle funzioni non va passato (se diverso
  da quello del marcatore è rifiutato). La sessione non costruisce mai `Parametri` da sola. La prova a placebo a
  barre giornaliere e il controllo positivo sono stati rifatti con gli strumenti nuovi e con questo terreno prima
  dell'apertura della Fase 2: esito e impronte nella sezione 6.
