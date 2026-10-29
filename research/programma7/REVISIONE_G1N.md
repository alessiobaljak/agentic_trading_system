# Programma 7 — la revisione indipendente di G1N (29 ottobre 2026)

G1N è G1 (il funding fra monete deciso ogni giorno, prova 57) con i due lati scalati ogni giorno perché la somma dei beta stimati
sui 90 giorni prima sia zero (prova 88, `VENTISEIESIMA.md`). Il coordinamento la propone per i soldi veri perché, sul passato,
«ha la stessa resa di G1 con la discesa massima da −28,8% a −23,1%, e il merito è della neutralità (il 120/80 fa peggio)»
(`docs/backlog.md`, P26; riga 88 di `research/REGISTRO.md`).

Revisore separato: non ho scritto né la prova né il bot e non li ho toccati. Ho riscritto da zero G1 e G1N dalle regole scritte
(universo, segnale, banda, pesi, beta, scalatura, conto), prendendo dalla ricerca solo il caricamento dei dati. Gli script e i
risultati sono in `research/programma7/revisione_g1n/`:

| file | cosa fa |
|---|---|
| `nucleo.py` | G1 e G1N riscritte da zero (regole di `PRIMA.md`, `VENTIQUATTRESIMA.md`, `VENTISEIESIMA.md`) |
| `analisi.py` → `risultati.json` | il ricalcolo, i controlli (TRX, tetti, ritardi, ricampionamento, liquidità, banda che parte vuota) |
| `parita_bot.py` → `parita_bot.json` | il pannello tagliato al giorno della decisione; le funzioni del bot contro la ricerca sui dati veri |
| `inclinazione_causale.py` → `inclinazione_causale.json` | il controllo giusto per la neutralità: un'inclinazione fissa scelta solo col passato |
| `soldi_veri.py` → `soldi_veri.json` | dimensione degli ordini, rialzi dentro il giorno del lato venduto |
| `corretto_oggi.py` → `corretto_oggi.json` | lo Sharpe corretto di G1N e G1 con il mazzo delle prove di oggi (funzione della ricerca) |

Uso: `python3 -m research.programma7.revisione_g1n.analisi` (circa 4 minuti; le candele a 1 ora si leggono la prima volta), e così
gli altri. Periodo: dal 4 gennaio 2021 al 4 ottobre 2026, come la prova.

## In breve

* **I conti sono giusti.** Nessun dato futuro (controllo meccanico), il bot calcola le stesse cose della ricerca (controllo sui dati
  veri), e il mio ricalcolo da zero ridà i numeri: G1N Sharpe 1,92, discesa −23,1%; G1 1,97, discesa −28,8%.
* **Ma il motivo per preferire G1N a G1 non regge.** Il guadagno sulla discesa massima viene da un solo episodio (novembre 2023 –
  marzo 2024) e nel ricampionamento c'è solo nel 62% dei casi; nella discesa più recente (maggio-agosto 2026) G1N fa peggio di G1
  (−20,6% contro −17,9%), e dal 2025 G1N è sotto G1 (Sharpe 1,94 contro 2,42).
* **Il controllo 120/80 era quello sbagliato.** In media G1N pesa il lato long 1,04 e lo short 0,96, non 1,2 e 0,8. Un lato long
  più pesante del 4% circa, quasi fisso e scelto solo con il passato, fa **Sharpe 2,01 con la discesa −24,7%**: meglio di G1N nello
  Sharpe e quasi uguale nella discesa. La stima del beta di ogni giorno non aggiunge niente di misurabile.
* **Lo Sharpe corretto di G1N è 0,83** (0,835 con il mazzo di oggi): sotto lo 0,90 della regola del proprietario del 24 ottobre.
* **Concentrazione**: senza TRX il vantaggio di G1N sulla discesa scende da 5,6 a 1,4 punti; senza le 5 monete che rendono di più
  sparisce (0,7 punti). Il lato short arriva a 5 monete sole nei giorni di funding uguale per molte monete, con una moneta piccola
  (BLZ) al 47,8% del capitale.

## 1. Sguardo nel futuro

**Verificato.**

* **Prova meccanica** (`parita_bot.py`, `parita_bot.json`): per 6 giorni (5 a caso e l'ultimo, 4 ottobre 2026) ho rifatto i pesi
  della ricerca su un pannello dove, dal giorno d in poi, prezzi, massimi, minimi, chiusure e volumi sono cancellati (resta solo
  l'apertura delle 00:00 di d) e il funding dei giorni di tenuta da d in poi è zero. **I pesi di G1 e G1N del giorno d sono
  identici** (differenza 0,0 in tutti e 6). Quindi i pesi del giorno d non usano niente del giorno d o dopo.
* **Beta** (`programma7/ventiquattresima.py`, righe 29-52, chiamata da `ventiseiesima.py` riga 37 con gli indici dei giorni): i
  rendimenti sono chiusura su chiusura dei giorni d−90 … d−1; la chiusura di d−1 è delle 23:59:59, cioè nota alle 00:00 di d. La media
  di mercato usa le monete dell'universo della settimana (deciso il lunedì con i dati fino alla domenica): non c'è futuro.
* **Allineamento** (letto nel codice e confermato dal ricalcolo): il rendimento del giorno d è dall'apertura di d all'apertura di d+1
  (`seconda.rendimenti`); il funding nel conto è quello pagato da chi tiene d (08:00 e 16:00 di d, 00:00 di d+1, `seconda.py` righe 5-8
  e 73-82); il segnale usa i 7 giorni di tenuta prima di d, cioè i regolamenti fino alle 00:00 di d compreso (`sesta.funding_7`). Il
  regolamento delle 00:00 è noto alle 00:00; il bot aspetta che sia pubblicato (`f5.py` righe 513-519).
* **Ritardare il beta non cambia niente** (`risultati.json`, «varianti»): con il beta di un giorno prima G1N fa 1,93 (discesa −22,8%),
  con quello di 7 giorni prima 1,94 (−21,8%). Se il beta portasse dentro qualcosa del futuro, ritardarlo farebbe peggio.

## 2. La scalatura

**Verificato** (`risultati.json`, «scalatura» e «beta_monete»):

* La formula fa quello che dice: a·βL = b·βS e a + b = 2 (esposizione lorda al 200%); con il taglio fra 0,5 e 1,5 resta a + b = 2.
* **I limiti 0,5-1,5 non scattano mai**: a va da 0,86 a 1,29 (5%-95%: 0,95-1,13), in media **a 1,043 e b 0,957**. Beta medio del lato
  long 0,90, dello short 0,98, come scritto nei risultati.
* **Beta negativi**: nessun giorno con il beta di un lato negativo; fra le monete tenute, 397 posizioni-giorno su 110.764 (0,36%) hanno
  il beta negativo. Il caso «βL + βS ≤ 0» non capita mai.
* **Pochi dati e monete nuove**: il caso non capita. L'universo vuole 200 giorni di vita, quindi ogni moneta tenuta ha i 90 giorni; il
  beta di ripiego (1) non si usa mai (0 su 110.764).
* **Il beta di una moneta è rumoroso**: fra il beta dei 90 giorni prima e quello dei 90 giorni dopo la correlazione è 0,44. La
  differenza fra i due lati invece è stabile (correlazione 0,69; −0,075 prima, −0,082 dopo): il lato long ha quasi sempre il beta un
  po' più basso dello short.

**Il controllo «peso fisso 120/80» non è quello giusto.** Doveva dire se il merito è della neutralità o del lato long più pesante; ma
G1N in media pesa 1,04/0,96, quindi il 120/80 è un'inclinazione cinque volte più forte. Con l'inclinazione della stessa misura:

| | Sharpe | l'anno | discesa (settimane) | 15 settimane peggiori di G1 |
|---|---|---|---|---|
| G1 | 1,97 | +54,3% | −28,8% | −6,03% |
| G1N (beta di ogni giorno) | 1,92 | +51,5% | −23,1% | −5,48% |
| inclinazione fissa 1,043/0,957 (la media di G1N: senno di poi, solo per capire) | 2,02 | +56,3% | −24,2% | −5,55% |
| **inclinazione causale** (a = media degli a dei giorni prima, b = 2 − a) | **2,01** | **+55,5%** | **−24,7%** | −5,66% |
| 120/80 (il controllo della prova) | 1,56 | +63,7% | −29,4% | −3,82% |

(`risultati.json` e `inclinazione_causale.json`.) Nel ricampionamento a blocchi di 8 settimane (5.000 volte, stesse settimane per le
due serie): G1N ha lo Sharpe più alto dell'inclinazione causale solo nel 14% dei casi e la discesa più bassa nel 42%. **Quindi quasi
tutto l'effetto è un lato long un po' più pesante, quasi costante; stimare il beta ogni giorno costa Sharpe e non porta una discesa
misurabilmente minore.** La frase della riga 88 «il merito è della neutralità (il 120/80 fa peggio)» non è dimostrata. Riserva: anche
l'inclinazione causale è un'idea nata dopo aver visto i risultati; qui serve solo come controllo, non come proposta.

**Neutralità misurata dopo** (`risultati.json`, «beta_realizzato»): G1 era già quasi neutra (beta settimanale verso la media delle 100
−0,02, verso il Bitcoin −0,03); G1N diventa +0,05 e +0,05. Sui giorni la neutralità riesce (G1 −0,06, G1N −0,004). Nelle settimane del
10% di mercato più forte G1 fa in media +3,2%, G1N +4,0%; in quelle del 10% più debole G1 +3,6%, G1N +1,9%: G1N scambia un po' di
guadagno nei crolli con un po' di guadagno nei rialzi.

## 3. Ricerca contro bot

**Verificato sui dati veri** (`parita_bot.py`): per 60 giorni a caso fra il 2021 e il 2026 ho dato alle funzioni pure del bot
(`universo`, `sigma_30`, `funding_7`, `pesi_banda`, `beta_delle_monete`, `scala_neutra` di `bot/portafoglio/f5.py`) gli stessi dati
della ricerca, con la banda del giorno prima della ricerca e la chiusura del giorno in corso messa apposta a un valore falso (×7).
Universo uguale in 60 giorni su 60; pesi di G1 e G1N uguali (differenza massima 6·10⁻¹⁷); beta uguali (2·10⁻¹⁵); nessuna moneta che
cambia lato. Stessa finestra (90 rendimenti, d−90 … d−1), stesso minimo (45), stessi limiti (0,5-1,5), stessa media di mercato. Il
valore falso della candela in corso non cambia niente: il bot non la usa. Anche il mio ricalcolo da zero coincide con la ricerca
(universo uguale in tutti i 2.100 giorni, pesi entro 10⁻¹⁶, `risultati.json`, «parita_con_la_ricerca»).

Le differenze che restano (nessuna è un errore di calcolo; le prime due contano per il confronto con il paper):

| # | Differenza | Bot | Ricerca | Peso |
|---|---|---|---|---|
| 1 | **La banda parte vuota** | G1N è partito il 26 ottobre senza posizioni (`f5.py` righe 603-604: `banda_di_partenza` dà {} per G1 e G1N) | banda con la storia dal 2021 | sui dati (20 partenze a caso, `risultati.json`, «banda_da_vuota»): le posizioni coincidono con quelle della ricerca dopo 12 giorni (mediana, al massimo 26); il primo giorno metà dell'esposizione è diversa (differenza lorda 1,28 su 2,00), dopo 7 giorni 0,20. **Nelle prime 2-4 settimane il paper non misura G1N com'è nella ricerca**, e G1 (partito il 24) e G1N (il 26) hanno bande diverse: il loro confronto in queste settimane misura soprattutto questo |
| 2 | **Ora della decisione** | nominale 00:05 (`f5.py` riga 54), in pratica 00:17-00:21 per G1N (`ops/results/0674`-`0677`: i paper girano uno dopo l'altro) al prezzo mark di quel momento | apertura delle 00:00 | piccolo; su F5 entrare alle 01:00 costava circa 0,01 di Sharpe (`programma6/CONTROLLO_PARITA.md`) |
| 3 | Ordine limite eseguito | se il **mark** a 1 minuto passa il livello nell'ora (`f5.py` righe 64-73, 378-384) | se il **minimo/massimo** della candela a 1 ora di scambio passa l'apertura (`programma6/cinquantaseiesima.py` righe 28-33) | il mark è più liscio del prezzo degli scambi: nel paper gli ordini «eseguiti» possono essere un po' meno |
| 4 | Universo | fuori i contratti che Binance chiude entro 8 giorni e quelli non in scambio adesso (`f5.py` righe 199-202, 341, 500); vita dalla data di quotazione | tiene le monete fino all'ultima candela; vita dalla prima candela dell'archivio | piccolo; il bot è più prudente. La media di mercato del beta usa le stesse monete ridotte (`f5.py` righe 629-631) |
| 5 | Funding dei 7 giorni | somma esatta dei regolamenti uno per uno (`f5.py` righe 123-125, 349-357) | somme giornaliere arrotondate a 12 decimali (`sesta.py` riga 32) | le parità restano parità in tutti e due; un ordine diverso è possibile solo per resti dell'ultima cifra. Il commento in cima a `f5.py` (righe 23-27) descrive ancora la ricerca di prima del 23 ottobre |
| 6 | Funding nel conto | mark del regolamento × quantità (`f5.py` righe 543-557) | peso di inizio giorno × somma del giorno | trascurabile |
| 7 | Quantità | non arrotondate al passo e al minimo di Binance (`f5.py` riga 438) | — | vedi il punto 5 (con 1.000 USDT tre ordini su quattro sarebbero sotto il minimo) |
| 8 | Conto demo | segue **G1**, non G1N (`demo_binance.py` riga 42, `FILE_G1`) | — | l'esecuzione vera di G1N non è provata da nessuna parte |

Due frasi da correggere nei testi (non nel codice): il commento di `PaperG1N` (`f5.py` righe 608-609) e il backlog dicono «con lo
stesso rendimento»: sono 2,8 punti l'anno in meno e 0,06 di Sharpe (1,91 contro 1,97 nella prova). La riga 88 del registro riporta +51,2%, −5,49%, corretto 0,84, t
4,59; il file dei risultati, rifatto il 25 ottobre con le candele orarie corrette, dice +51,3%, −5,48%, 0,83, 4,60.

## 4. I numeri

**Ricalcolo indipendente** (`risultati.json`, «sintesi»; stessi dati e stessa regola degli ordini limite della ricerca, codice mio):

| | Sharpe | l'anno | volatilità | discesa (settimane) | discesa (giorni) | a mercato | ordini limite più severi (0,05% / 0,10%) | costi tripli |
|---|---|---|---|---|---|---|---|---|
| G1 | 1,97 | +54,3% | 27,5% | −28,8% | −30,1% | 1,86 | 1,78 / 1,59 | 1,51 |
| G1N | 1,92 | +51,5% | 26,8% | −23,1% | −24,3% | 1,80 | 1,72 / 1,53 | 1,45 |

La ricerca dice G1N 1,91 e +51,3%: la differenza (0,007) viene probabilmente dal modo di far derivare i pesi nel conto delle
variazioni a limite (non verificato). Con gli ordini limite che devono passare il livello dello 0,10%, la discesa di G1N sale a
−27,6%, vicina a quella di G1 nella prova.

**Per anno** (rendimento; Sharpe fra parentesi):

| | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 (fino al 4 ottobre) |
|---|---|---|---|---|---|---|
| G1 | +109,9% (2,94) | +31,7% (1,33) | +8,2% (0,34) | +68,0% (2,29) | +72,5% (3,84) | +28,5% (1,11) |
| G1N | +124,8% (3,47) | +17,0% (0,72) | +11,6% (0,58) | +67,6% (2,26) | +57,4% (3,39) | +22,9% (0,82) |

Ogni anno positivo, ma G1N è sotto G1 in 2022, 2025 e 2026. **Dal 2025** (92 settimane, `inclinazione_causale.json`): G1 Sharpe 2,42 e
discesa −17,9%; G1N 1,94 e −20,6%; inclinazione causale 2,27 e −18,1%.

**La discesa più bassa è fortuna o no?** (`risultati.json`, «discese_peggiori» e «bootstrap_G1N_meno_G1»)

* Le discese peggiori: G1 −28,8% (dal 13 novembre 2023, fondo il 25 marzo 2024), −17,9% (dal 25 maggio 2026, fondo il 10 agosto),
  −15,1% (agosto-settembre 2021); G1N −23,1% (stesso episodio del 2023-24), **−20,6% (stesso episodio del 2026: peggio di G1)**,
  −13,5% (2021). Il guadagno di 5,6 punti viene da un episodio solo.
* Settimana peggiore: G1 −9,4%, **G1N −11,1%**. Giorno peggiore: G1 −8,5%, G1N −7,0%. Media del 5% delle settimane peggiori: G1
  −6,03%, G1N −5,78%.
* Ricampionamento a blocchi di 8 settimane (5.000 volte): la discesa di G1N è più bassa di quella di G1 nel **62%** dei casi, in media di
  0,9 punti (90% dei casi fra −5,5 e +6,5 punti); lo Sharpe di G1N è più alto nel 26% dei casi. **Il −23,1% contro −28,8% non è un
  vantaggio dimostrato.**

**Lo Sharpe corretto** (`corretto_oggi.json`, funzione della ricerca con tutte le serie di oggi, 80 gruppi): **G1N 0,835**, G1 0,860; t
4,60 e 4,73. G1N e G1 stanno nello stesso gruppo (28 prove): scegliere G1N fra le varianti di G1 non costa niente nel conto, che è la
debolezza del metodo già scritta in `REVISIONE_G11.md`. Con la regola del proprietario (da 0,90, ogni anno positiva, t sopra 3) G1N
**non passa**; oggi non passa nemmeno G1.

**Poche monete** (`risultati.json`, «concentrazione» e «varianti»):

* Il contributo (prezzo e funding, prima delle spese) viene per il 45% da cinque monete: BNB 10,7%, TRX 10,1%, DASH 9,7%, ALGO 7,7%,
  BCH 7,1%. Le peggiori: IOTA, XRP, NEAR, LINK, LUNA.
* **TRX** nella ricerca arriva al 29,3% del lato long (36,4% del capitale in G1N, il 28 agosto 2026) ed è sopra il 20% del lato in 39
  giorni. Il «quasi 50%» del paper del 27 ottobre (`docs/andremo_live.md`) è più di quanto si sia mai visto nel passato: probabilmente la
  banda partita vuota (20 long invece dei circa 27 abituali) più a alto (non verificato: non ho accesso al paper).
* Varianti (Sharpe, discesa):

| | G1 | G1N | vantaggio di G1N sulla discesa |
|---|---|---|---|
| come scritte | 1,97, −28,8% | 1,92, −23,1% | 5,6 punti |
| **senza TRX** | 1,81, −26,0% | 1,73, −24,6% | 1,4 punti |
| tetto del 20% per moneta nel lato | 1,94, −31,3% | 1,89, −25,5% | 5,9 punti |
| tetto del 10% | 1,87, −31,2% | 1,74, −25,3% | 5,9 punti |
| senza le 5 monete migliori (scelte dopo, solo per misurare) | 1,51, −29,6% | 1,49, −28,9% | 0,7 punti |

  Senza TRX G1N per anno: 2021 +124,3%, 2022 +14,9%, 2023 +4,6%, 2024 +56,0%, 2025 +61,3%, 2026 +16,0%. Senza le 5 migliori il 2023
  di G1N è +0,9%.

**Pochi giorni** (`risultati.json`, «dipendenza»): i 10 giorni migliori fanno il 27% del guadagno totale di G1N (G1 25%). Senza i 10
giorni migliori G1N fa 1,55 (G1 1,58); senza le 20 settimane migliori 0,93 (G1 1,00).

## 5. Cosa può andare storto con i soldi veri (che il paper non vede)

* **Il lato venduto è fatto di monete piccole** (`risultati.json`, «liquidita»): metà delle posizioni short (56%) sono monete fra la 51ª
  e la 100ª per volume; volume giornaliero mediano 42 milioni di USDT, il 5% più basso 12 milioni. Fino a 100.000 USDT di capitale una
  posizione è al massimo lo 0,33% del volume del giorno; con 1 milione al massimo il 3,3%; con 10 milioni il 39% delle posizioni supera
  l'1% del volume. Lo scarto dello 0,02% usato per queste monete non è mai stato misurato sui libri di allora.
* **Pochi short, uno enorme**: quando molte monete hanno lo stesso funding (il 5 febbraio 2024 63 su 100 erano al funding di base) le
  parità prendono il rango medio e lo short resta con 5 monete: quel giorno BLZ era short per il **47,8% del capitale**. Giorni con meno di
  10 short: 67 (45 nel 2021, 22 nel 2024); con 5 o meno: 8. È un rischio, non un errore: G1 ha lo stesso problema.
* **I rialzi improvvisi del lato venduto** (`soldi_veri.json`): su 56.535 posizioni short-giorno, 1.298 hanno visto il massimo del giorno
  oltre il +20% dall'apertura, 493 oltre il +30%, 138 oltre il +50% (il massimo +413%). Il giorno peggiore di una sola moneta short: XRP
  il 30 gennaio 2021, +57%, −7,9% del capitale. Se tutte le monete toccassero il massimo del giorno insieme, il conto perderebbe nel caso
  peggiore l'11,1% (30 gennaio 2021; un giorno su cento il 4,2%); nel crollo di tutte insieme al minimo il caso peggiore è −3,2%.
  Con il margine incrociato e il 200% di esposizione una perdita dell'11% in un giorno non porta alla liquidazione; con il margine
  isolato a leva 5 un rialzo di circa il 20% chiuderebbe quella posizione. Il demo imposta la leva 5 per moneta ma non il tipo di
  margine (`demo_binance.py`): quale sia sul conto non l'ho verificato.
* **Il funding è metà del guadagno**: G1N incassa il 27,1% l'anno dal funding su un netto del 51,5% (`risultati.json`); paga in 1,1%
  dei giorni, al massimo lo 0,11% in un giorno. Se Binance cambia le regole del funding (tetti, intervalli più corti nei rialzi) il
  vantaggio cambia; il paper lo vede solo dopo.
* **Ordini piccoli** (`soldi_veri.json`): 56 variazioni al giorno, mediana lo 0,22% del capitale. Sotto i 5 USDT (il minimo tipico di
  Binance): con 1.000 USDT il 76% degli ordini (20% del giro), con 5.000 il 27%, con 10.000 il 14%, con 100.000 l'1,4%. Con poco capitale
  il conto vero non può seguire i pesi; il paper non arrotonda niente.
* **Gli ordini limite sono l'ipotesi più fragile**: se il prezzo deve passare il livello dello 0,05%, G1N scende a 1,72; dello 0,10% a
  1,53, sotto il «tutto a mercato» (1,80). L'esecuzione vera di G1N non la prova nessuno (il demo fa G1).
* **Monete tolte dal listino**: nella ricerca G1N ha tenuto DODO 2 giorni, EOS 3, KEEP 5, LUNA 2 dopo l'ultima candela, a rendimento zero
  (`risultati.json`, «tolte_dal_listino_tenute»); LUNA negli ultimi giorni costa il 3,4% del capitale. Il bot esce dai contratti che
  Binance annuncia in chiusura entro 8 giorni, ma una chiusura improvvisa (come LUNA) non si anticipa.
* **Giorni estremi**: con le candele giornaliere non si vede cosa succede dentro un giorno come il 10 ottobre 2025 (vendite forzate a
  catena e chiusure forzate delle posizioni in guadagno da parte di Binance): lì una copertura long-short vera può rompersi. Non l'ho
  potuto misurare.

## 6. Cosa non ho potuto controllare

* Il paper e il demo di adesso (non ho accesso alla macchina né a Firebase): i numeri del paper vengono dal diario e dai log in `ops/`.
* Il ricalcolo usa lo stesso pannello e la stessa regola degli ordini limite della ricerca: è indipendente nel codice, non nei dati né
  nell'ipotesi di esecuzione.
* Ottobre 2026: il funding del mese nell'archivio è stimato (media dei 90 giorni), quindi non ho usato le settimane dopo il 4 ottobre.
* Lo scarto vero delle monete piccole nel 2021-2024 e il percorso dentro i giorni di crollo.

## Giudizio

**Non regge come variante da preferire a G1 per i soldi veri**: i conti sono giusti, senza dati futuri e uguali nel bot, ma la discesa
più bassa viene da un solo episodio (62% nel ricampionamento), dal 2025 G1N fa peggio di G1, un lato long più pesante del 4% quasi fisso
fa meglio (2,01 contro 1,92) senza stimare nessun beta, e lo Sharpe corretto 0,83 è sotto lo 0,90 della regola del proprietario.
