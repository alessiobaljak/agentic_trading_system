# Prova 162 — Il funding fra il perpetuo in USDT e quello in USDC della stessa moneta (idea 147)

Regole scritte il 18 novembre 2026 (giro delle 08:17) dallo strategy-scout, **prima di ogni calcolo**: nessun dato di funding o di prezzo
dei contratti in USDC è stato guardato (solo un controllo che i file mensili esistano: risposta 200 o 404). La prova la esegue
strategy-researcher (prima in modalità verifica), il giudizio lo dà backtest-auditor. Il numero 162 è libero (ultima nel registro: 161).
Non spegne e non sostituisce niente.

## Il perché forte
* **Dato mai usato.** Binance quota per le monete maggiori due perpetui sulla stessa moneta: quello in USDT e quello in USDC
  (BTCUSDT e BTCUSDC, ETH, BNB, SOL, XRP, DOGE e altre). Nel registro `--cerca USDC` = 0, `--cerca "due perpetui"` = 0, `--cerca "stesso
  sottostante"` = 0: **mai provato**. Non è il funding coperto (prove 157, 160, 161: pronti contro perpetuo), non è la base dei
  trimestrali (159), non è il funding fra borse (135, 137: Hyperliquid, un'altra borsa e un'altra garanzia). Qui la borsa è la stessa,
  il sottostante è lo stesso, il margine è nel conto di Binance.
* **Ragione economica.** Ogni perpetuo ha il suo funding, calcolato sul **suo** premio rispetto all'indice. Chi tiene posizioni in USDC
  è un'altra platea (altre garanzie, altri mercati di riferimento, altri incentivi sulle commissioni) e il premio del suo contratto
  può restare sopra o sotto quello del contratto in USDT per giorni. La stessa moneta quindi paga funding diversi: si vende il contratto
  che paga di più e si compra quello che paga meno, senza rischio sul prezzo della moneta (le due gambe si annullano). È un guadagno
  da «chi paga per una posizione affollata», **regolare** (richiesta del proprietario del 15 novembre: guadagni giorno per giorno) e
  non un indicatore sul prezzo. Studio di riferimento per il meccanismo (premio del perpetuo e funding come prezzo del bisogno di leva): He, Manela,
  Ross e von Wachter, «Fundamentals of perpetual futures», 2022-2024 (arXiv 2212.06888). Lo studio non misura la coppia USDT/USDC:
  il fatto che la differenza duri è **da misurare**, non si assume.
* **Avviso onesto.** Il funding delle due gambe segue in gran parte lo stesso indice, la differenza può essere di pochi centesimi di punto
  base per ciclo e le spese per cambiare lato (quattro gambe) sono alte: probabile che il lordo sia piccolo (pochi punti l'anno) e che
  il netto sia vicino a zero. Probabilità medio-bassa, ma il t può essere alto perché la serie è poco rumorosa (come nel coperto, t 8). Si prova perché
  è l'unico guadagno senza rischio di prezzo che non avevamo misurato su Binance.

## Dati e periodo (verificati il 18 novembre 2026 solo come esistenza dei file)
* Funding mensile: `https://data.binance.vision/data/futures/um/monthly/fundingRate/<SIMBOLO>/<SIMBOLO>-fundingRate-AAAA-MM.zip` per i
  simboli in USDC e in USDT. Candele giornaliere: `.../monthly/klines/<SIMBOLO>/1d/<SIMBOLO>-1d-AAAA-MM.zip` (apertura alle 00:00 UTC).
  **Verificato**: BTC, ETH, BNB, SOL, XRP e DOGE in USDC hanno file dal **gennaio 2024** (404 per dicembre 2023 e prima), fino a ottobre 2026.
  Per le altre monete in USDC si prova lo stesso indirizzo; l'universo è quello che risponde 200.
* **Universo**: le monete che hanno **tutti e due** i perpetui, in USDT e in USDC, con almeno 30 giorni interi di storia in USDC prima del
  giorno della decisione. Si esclude il perpetuo su azioni (tipo ufficiale di Binance, backlog P32). Elenco e primo giorno di ogni moneta
  scritti nel rapporto.
* **Periodo**: dal primo giorno con 30 giorni di storia (circa il 31 gennaio 2024) al **31 ottobre 2026** (ultimo mese intero del funding
  dell'archivio; niente funding stimato, vedi `INDEX.md`). Anni: 2024, 2025 pieni, 2026 parziale (10 mesi); tutti e tre contano per
  «ogni anno positivo». Sono meno di 3 anni: lo si scrive e il giudizio ne tiene conto.

## Il segnale (fissato qui)
Per ogni moneta, alla decisione del giorno D (00:00 UTC) si usano i funding **già pagati prima di D** (ultimo = quello delle 16:00 UTC del
giorno D−1). Differenza d = media **per giorno** (somma dei funding pagati nel giorno dal contratto in USDT meno la somma di quelli del
contratto in USDC) sulle ultime L giornate intere. Per giorno e non per ciclo perché i due contratti possono pagare a intervalli diversi
(1, 4 o 8 ore; correzione della sessione principale prima del commit, 18 novembre).
* Se d > +θ: **vendere il perpetuo in USDT e comprare quello in USDC**. Se d < −θ: il contrario. Se |d| ≤ θ: moneta ferma (nessuna posizione).
* Tutte le monete non ferme hanno lo stesso valore nominale per gamba (pesi uguali, 1 diviso il numero di monete non ferme, al massimo 1 di
  valore nominale per gamba in totale). Capitale = valore nominale di una gamba (margine al 50% per gamba, nessuna leva sopra il 2x; il
  rendimento è sul capitale). Il controllo del margine è nella sezione «Chiusura della verifica», punto 11 (margine in comune).
* Rendimento giornaliero di una moneta = (rendimento dell'apertura D all'apertura D+1 della gamba comprata meno quello della venduta) +
  funding vero di **tutte** le scadenze del giorno D di ciascun contratto: Σ f(venduto) − Σ f(comprato), con f il tasso pubblicato (chi è
venduto incassa f quando è positivo, chi è comprato lo paga) − spese. Nota: sul conto la gamba in USDC richiede la modalità con più
garanzie di Binance (gli USDT valgono come margine); nel calcolo il capitale è uno solo. Gli
  eventuali buchi del archivio (`programma6/buchi_archivio.py`) si saltano e si scrivono.
* Esecuzione: ordini all'apertura del giorno D, **a mercato** (conservativo): 0,05% per gamba più scarto 0,01% su BTC, ETH, SOL e 0,02% sulle
  altre. Un cambio di lato o una chiusura costano due gambe in chiusura e, se si riapre, due in apertura. Con ordine limite (0,02%) si calcola **solo
  come controllo descrittivo**, non come variante. Nessuna spesa se la posizione resta uguale (pesi uguali: si riequilibra solo
  quando cambia il numero di monete non ferme, e si paga solo sul valore scambiato).

## Varianti (fissate, solo 2)
* **A (lenta)**: L = 30 giorni, θ = 0,006% al giorno (circa 2,2% l'anno; lo 0,002% per ciclo di 8 ore scritto dallo scout), decisione
  solo il primo giorno di ogni mese.
* **B (veloce)**: L = 7 giorni, θ = 0,015% al giorno (circa 5,5% l'anno; lo 0,005% per ciclo di 8 ore), decisione solo il lunedì.
Nessuna soglia, finestra o frequenza diversa dopo i risultati. Perché solo due: la differenza sta fra «persistente da un mese» e «da una
settimana»; le soglie corrispondono a circa 2,2% e 5,5% l'anno (un cambio di lato costa circa 0,24-0,28%, più di θ × i giorni di tenuta:
la verifica lo ha notato; la soglia non si cambia). Conta **2 prove**
(le due serie hanno probabilmente correlazione alta: la famiglia è una, `corretto_famiglie` nel conto).
**Controlli descrittivi, non varianti** (si scrivono, non si scelgono): media di d per anno e per moneta; quota di giorni con la stessa
segnalazione del mese dopo (persistenza); distribuzione della differenza fra i prezzi dei due contratti (il rischio di base); numero di
cambi di lato; rendimento con ordine limite; rendimento senza la moneta migliore.

## Chiusura della verifica (18 novembre 2026, sessione principale, prima di ogni calcolo)
Dalla verifica di strategy-researcher (`VERIFICA_CENTESIMA.md`, 14 punti). **Dove il testo sopra dice diversamente, vale questa sezione.**
1. **Universo**: l'elenco fisso dei 40 simboli in USDC dell'archivio con il rispettivo in USDT, scritto in `VERIFICA_CENTESIMA.md` con il
   primo mese; si copia nel rapporto con il primo giorno utile di ogni moneta. Nessuna moneta si aggiunge o si toglie dopo.
2. **Storia**: si conta in giorni UTC interi con la candela giornaliera **e** almeno un funding pubblicato, per **tutti e due** i contratti.
3. **Inizio**: una moneta entra alla prima decisione della variante con almeno **30** giorni interi di storia (per tutte e due le
   varianti, come scritto nell'universo); la serie di ogni variante parte dal primo giorno con almeno una moneta non ferma; i giorni
   senza posizione valgono 0 e restano nella serie.
4. **Fine**: l'ultimo giorno D è il **30 ottobre 2026** (il 31 non ha l'apertura del giorno dopo nell'archivio mensile).
5. **Funding nel segnale**: il giorno di un pagamento è la data UTC del suo orario; nel segnale della decisione D entrano i pagamenti delle
   giornate D−L … D−1, cioè con orario da D−L 00:00 compreso a D 00:00 **escluso**. Solo i file mensili dell'archivio, mai il pannello.
6. **Giorni senza funding**: se in una delle L giornate un contratto non ha nessun pagamento, la moneta è ferma a quella decisione; i casi
   si contano e si scrivono.
7. **Funding nel rendimento**: la posizione tenuta dall'apertura di D all'apertura di D+1 riceve o paga i pagamenti con orario **dopo** D 00:00
   e **fino a** D+1 00:00 compreso (il pagamento delle 00:00 va alla posizione che c'era a quell'istante, come nel motore di G1: chi apre
   alle 00:00 di D non conta il pagamento delle 00:00 di D; chi chiude all'apertura di D lo conta).
8. **Pesi**: il rendimento si calcola a pesi costanti 1/N fra due decisioni (riequilibrio giornaliero implicito a costo zero: è un limite e
   si scrive nel rapporto); le spese si pagano solo il giorno della decisione.
9. **Spese**: spesa del giorno di decisione = somma su ogni gamba di (0,05% + scarto 0,01% su BTC, ETH, SOL o 0,02% sulle altre, uguale per
   USDT e USDC) × |peso nuovo con segno − peso vecchio con segno|; un cambio di lato è chiusura più apertura delle due gambe; quando cambia N
   si scambia la differenza dei pesi sulle gambe delle monete che restano. Lo scarto uguale per il USDC, meno liquido, è ottimista: si scrive
   come limite.
10. **Contratto che finisce** (MATIC, IP e simili): se un contratto non ha più candele o funding, la posizione si chiude all'ultima apertura
    disponibile con le spese di chiusura e la moneta esce; il caso si scrive.
11. **Margine (decisione della sessione principale)**: le due gambe stanno nello stesso portafoglio dei future di Binance con il **margine in
    comune** (modalità con più garanzie, come il margine unico che il bot usa già sul demo): un profitto su una gamba copre la perdita
    sull'altra. A ogni ora, con le quantità fisse dalla decisione e i prezzi del punto 12: equity del conto = capitale + profitto o perdita
    di prezzo di tutte le gambe + funding e spese già maturati. Il giorno è **a rischio** se in una qualunque ora l'equity scende sotto il
    **10% del capitale**; **liquidato** se scende sotto il mantenimento, 0,5% del valore delle gambe (come nella 161). Solo come descrizione,
    non nell'esame: la regola per gamba isolata della verifica (margine 50% del valore iniziale ± la sola gamba, «a rischio» sotto il 10% del
    valore corrente), la base massima fra i due prezzi e la leva massima.
12. **Prezzi per il margine**: il prezzo mark a 1 ora di ogni contratto; dove manca un'ora, il prezzo scambiato a 1 ora dello stesso contratto;
    mai le candele giornaliere. Le ore mancanti si contano.
13. **Dati**: è autorizzato un solo script nuovo, `programma7/centesima_dati.py` (sul modello di `novantanovesima_dati.py`), che scarica da
    `data.binance.vision` fundingRate, candele 1d e 1h e mark a 1 ora dei 40 simboli in USDC e dei corrispondenti in USDT, con impronte e
    buchi in `risultati_centesima/`; i dati in `research/data/` (non committati).
14. **Esame**: per ciascuna variante la serie settimanale netta (somma dei netti giornalieri per settimana da lunedì); tutte e due le varianti
    in `nuove` di `corretto_famiglie`; i numeri dell'esame sono quelli di `numeri_settimana` sulla serie dopo `periodo()` (tagliata al 5
    ottobre 2026); Sharpe su 365 giorni e numeri fino al 30 ottobre solo come descrizione. Ogni variante si giudica da sola: la prova è
    promettente se almeno una variante supera tutto l'esame. Netto annuo su capitale = media giornaliera netta (giorni fermi compresi) × 365,
    capitale = valore nominale di una gamba; per anno la stessa media nel sotto-periodo («ogni anno positivo» = media del sotto-periodo > 0).

## L'esame (regole approvate dal proprietario il 9 e l'11 novembre)
Passa se: netto dopo i costi positivo; **ogni anno positivo** (2024, 2025, 2026 parziale); t almeno 3; Sharpe corretto almeno 0,80 con il
conto per famiglie (`corretto_famiglie` in `programma6/asticella.py`, esempio `audits/repro/prova28_2026-11-11.py` voce 11); **nessun
giorno in cui il margine di una gamba sarebbe stato a rischio** con la regola scritta sopra. In più: la serie si mette accanto a G1
(correlazione e miscela 80/20 solo come numero descrittivo, senza ritocchi). Se il rendimento netto è sotto il 3% l'anno su capitale,
anche con Sharpe alto è **non promosso per poco valore** (si scrive: troppo piccolo per muovere un conto).

## Cosa si consegna
`research/programma7/RISULTATI_CENTESIMA.md`, serie giornaliere in `research/programma7/risultati_centesima/`, script
`research/programma7/centesima.py`, varianti in `research/trials/centesima.csv`, la serie scaricata in `research/data/` (non committata),
a schermo al massimo 20 righe.

## Testo della riga di coda (sezione 5 del registro)
147. **Il funding fra il perpetuo in USDT e quello in USDC della stessa moneta** (strategy-scout, 18 novembre): vendere il contratto che paga di
più e comprare quello che paga meno, senza rischio sul prezzo; mai provato (`--cerca USDC` = 0); dati gratuiti di Binance dal gennaio 2024;
regole in `programma7/CENTESIMA.md` → prova 162. Probabilità medio-bassa (lordo piccolo, spese di quattro gambe).

## Testo della riga del registro
| 162 | CU: il funding fra il perpetuo in USDT e quello in USDC della stessa moneta (idea 147, strategy-scout del 18 novembre): vendere il contratto che paga di più e comprare quello che paga meno, pesi uguali, a mercato, decisione mensile con 30 giorni di storia e soglia 0,002% per ciclo (A) o settimanale con 7 giorni e 0,005% (B), dal gennaio 2024 al 31 ottobre 2026; esame + margine mai a rischio + netto almeno 3% l'anno (`programma7/CENTESIMA.md`); dati mai usati |
