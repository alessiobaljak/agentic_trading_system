# Verifica della prova 162 (CENTESIMA.md, commit 08190b1) — 18 novembre 2026

Modalità verifica: nessun calcolo, nessun dato di funding o prezzo aperto. Controllata solo l'ESISTENZA dei file con l'elenco delle
chiavi dell'archivio pubblico (`data.binance.vision`, elenco dei nomi dei file, mai il contenuto). Regole committate (08190b1).

## Esito
**Non eseguibile così com'è**: 14 punti da chiudere (sotto). Il lato dei dati è a posto: tutti i 40 perpetui in USDC hanno il
funding mensile, le candele giornaliere e **anche le candele a un'ora del prezzo mark** (`markPriceKlines/<SIMBOLO>/1h`, 40 su 40).

## Universo: monete con tutti e due i perpetui (primo mese di funding = primo mese delle candele giornaliere in USDC)
40 monete in USDC, tutte con il corrispondente in USDT (che parte sempre prima o nello stesso mese). Nessun contratto su azioni.
Il primo mese è il mese del primo file: il primo giorno vero sta dentro il file (non aperto), quindi il primo giorno utile (30 giorni
interi) è da calcolare dalle candele.
- Gennaio 2024: BNB, BTC, DOGE, ETH, SOL, XRP
- Febbraio 2024: LINK, ORDI, SUI
- Marzo 2024: 1000PEPE, 1000SHIB, AVAX, WLD
- Aprile 2024: ARB, BCH, BOME, FIL, LTC, MATIC, NEAR, NEO, TIA, WIF
- Maggio 2024: 1000BONK, ENA, ETHFI
- Luglio 2024: CRV
- Marzo 2025: ADA, HBAR, IP, KAITO, PNUT, TRUMP
- Giugno 2025: AAVE, UNI
- Luglio 2025: PENGU; Agosto 2025: BIO; Settembre 2025: WLFI; Novembre 2025: ZEC; Luglio 2026: DATAIP
Fine dei file: tutte a ottobre 2026 tranne tre eccezioni.
- MATIC: funding in USDC fino a gennaio 2026, candele giornaliere in USDC e in USDT solo fino a settembre 2024.
- IP: funding fino a giugno 2026 (sia USDC sia USDT), candele giornaliere fino a ottobre 2026.
- DATAIP: solo 4 mesi (entra circa ad agosto 2026).
Nessun buco di mesi nei file elencati (numero di file = mesi dal primo all'ultimo).

## Ambiguità e correzioni proposte
1. **Universo, elenco**: «l'universo è quello che risponde 200» non dice come si ottiene l'elenco. Correzione: «L'universo è l'elenco dei 40 simboli
   in USDC dell'archivio con il rispettivo in USDT (elenco scritto nel rapporto con il primo mese e il primo giorno utile); l'elenco si fissa una volta,
   prima del calcolo.»
2. **«30 giorni interi di storia»**: non dice di che cosa (candele o funding, di una gamba o di tutte e due). Correzione: «La storia si conta in
   giorni UTC interi con la candela giornaliera E almeno un funding pubblicato, per entrambi i contratti.»
3. **Primo giorno utile e inizio della serie**: «circa il 31 gennaio 2024» vale solo per la variante B se fosse giornaliera; A decide solo il
   primo del mese (BTC: 1° febbraio 2024), B solo il lunedì (5 febbraio 2024). Correzione: «Una moneta entra alla prima decisione della variante con
   almeno 30 giorni interi di storia; la serie di ogni variante parte dal primo giorno con almeno una moneta non ferma; i giorni senza posizione
   valgono 0 e restano nella serie (Sharpe e t su 365 giorni di calendario).»
4. **Fine del periodo**: il giorno D = 31 ottobre ha bisogno dell'apertura del 1° novembre, che l'archivio mensile non ha. Correzione: «L'ultimo giorno
   D è il 30 ottobre 2026; il 31 ottobre non entra (niente apertura del giorno dopo).»
5. **Il «giorno» del funding e l'«ultimo pagato = 16:00 di D−1»**: vale solo per intervalli da 8 ore (con 4 o 1 ora l'ultimo è alle 20:00 o 23:00).
   Correzione: «Il giorno di un funding è la data UTC del suo orario di pagamento (00:00 compreso nel giorno che inizia); nel segnale entrano i pagamenti con
   orario strettamente prima delle 00:00 di D.» Per entrambi i contratti si usano gli stessi file mensili dell'archivio (non il pannello, che dopo il
   31 ottobre mette una stima).
6. **Buchi e giorni senza funding**: non è detto che cosa fa il segnale se in una delle L giornate manca ogni pagamento di un contratto.
   Correzione: «Se in una delle L giornate un contratto non ha nessun pagamento, la moneta è ferma quel giorno; il numero di casi si scrive.»
7. **Funding del pagamento delle 00:00 il giorno dell'ordine**: l'ordine è alle 00:00 di D e il pagamento delle 00:00 di D è «del giorno D»: non è chiaro
   se chi apre in quell'istante lo incassa (sarebbe ottimista). Correzione: «Il pagamento delle 00:00 si conta solo per la posizione già aperta il giorno
   prima; nel giorno di apertura si contano i pagamenti dopo le 00:00; nel giorno di chiusura quello delle 00:00 non si conta.»
8. **Pesi che si spostano fra una decisione e l'altra**: «pesi uguali» e rendimento giornaliero = pesi costanti, ma i prezzi spostano il valore delle
   gambe e la spesa di ribilanciamento giornaliero non è prevista. Correzione: «Il rendimento si calcola a pesi costanti 1/N per tutto il periodo fra due
   decisioni (riequilibrio giornaliero implicito, a costo zero: limite scritto nel rapporto); le spese si pagano solo il giorno della decisione.»
9. **Spese: cosa si scambia**: bisogna dire la formula. Correzione: «Spesa del giorno = somma, su ogni gamba, di (0,05% + scarto 0,01% su BTC/ETH/SOL o 0,02%
   sulle altre, lo stesso per USDT e USDC) × |peso nuovo − peso vecchio con segno| del valore nominale scambiato; un cambio di lato = chiusura e apertura
   delle due gambe; quando cambia il numero N delle monete non ferme si scambia la differenza dei pesi su ogni gamba delle monete che restano.»
   Nota: lo scarto di prezzo uguale per USDC e USDT è ottimistico (il USDC è meno liquido): si scrive come limite, non si cambia.
10. **Contratto che finisce (MATIC, IP) o moneta che sparisce**: nessuna regola. Correzione: «Se un contratto non ha più candele o funding, la posizione si
    chiude all'ultima apertura disponibile con le spese di chiusura e la moneta esce dall'universo; il caso si scrive.»
11. **Controllo del margine, che cosa si misura e la soglia**: manca la soglia di «a rischio» e il testo parla di «spostamento fra i due prezzi» (la base),
    che non è il rischio di liquidazione di una gamba (la gamba venduta sale con il prezzo della moneta; la perdita è compensata dall'altra gamba solo
    con i margini in comune). Correzione (soglia da scegliere dalla sessione principale: qui 10% come esempio, mantenimento 0,5% come nella 161):
    «Dalla decisione fino alla successiva, con le quantità fisse e i prezzi mark orari, per ogni gamba si calcola il margine = 50% del valore iniziale
    ± profitto/perdita da prezzo della sola gamba, senza trasferimenti fra le gambe e senza rifornimenti; il giorno è "a rischio" se in qualunque ora il
    margine di una gamba scende sotto il 10% del suo valore corrente (liquidato se sotto lo 0,5%). Si scrivono anche la base massima fra i due prezzi e
    la leva massima.» Nota: con questa regola, la variante A (un mese) è molto più esposta di B; il rendimento resta calcolato a pesi costanti, e lo si dice.
12. **Dati per il margine**: il testo dice «`mark_1h` dove c'è; altrimenti il massimo delle candele giornaliere», ma le candele a 1 ora del mark ESISTONO per
    tutti i 40 USDC (più buchi di poche ore da misurare) e le candele a 1 ora del prezzo scambiato esistono anch'esse. Il massimo giornaliero non dà
    l'istante comune delle due gambe. Correzione: «Prezzo mark a 1 ora di ogni contratto; dove manca un'ora, il prezzo scambiato a 1 ora dello stesso
    contratto (come nella 161); mai le candele giornaliere.»
13. **Caricatori e permesso di scaricare**: non esiste un caricatore ufficiale per USDC (il pannello è solo USDT). Le regole dicono «la serie scaricata
    in `research/data/`». Correzione: «È autorizzato un solo script nuovo, `programma7/centesima_dati.py` (sul modello di `novantanovesima_dati.py`), che scarica da
    `data.binance.vision`: fundingRate, klines 1d e 1h, markPriceKlines 1h dei 40 simboli in USDC e dei corrispondenti USDT, con impronte e buchi in
    `risultati_centesima/`.»
14. **L'esame, il conto per famiglie e il netto «su capitale»**: manca come si ottengono i numeri. Dal codice (`asticella.corretto_famiglie`,
    `terza.numeri_settimana`, `periodo`): la serie è settimanale netta (somma dei netti giornalieri per settimana con inizio il lunedì, come
    `_lunedi`), Sharpe su 52 settimane, t = Sharpe × √(settimane/52); `periodo()` taglia le serie al **5 ottobre 2026** e toglie le settimane ferme iniziali;
    i gruppi usano solo settimane con operazioni (almeno 52 comuni). Correzione: «Per ciascuna variante si costruisce la serie settimanale netta
    (somma dei netti giornalieri per settimana da lunedì); le due varianti vanno ENTRAMBE in `nuove` di `corretto_famiglie`; i numeri di `candidate`
    (sharpe, settimane, asimmetria, curtosi) sono quelli di `numeri_settimana` della serie dopo `periodo()`; lo Sharpe su 365 giorni e i numeri fino al
    30 ottobre si scrivono solo come descrizione. Ogni variante è giudicata per conto suo: la prova è promettente se almeno una variante supera tutto
    l'esame. Netto annuo su capitale = media giornaliera netta (giorni fermi compresi) × 365, capitale = 1 valore nominale di una gamba, sull'intero
    periodo; per anno: stessa media × 365 nel sotto-periodo ("ogni anno positivo" = media del sotto-periodo > 0).»

## Un'osservazione non bloccante
La frase «θ pari a circa 3 e 6 volte le spese di un cambio ammortizzate nel periodo di tenuta» non torna: un cambio di lato costa circa 4 × 0,06-0,07% =
0,24-0,28%, mentre θ × 30 giorni = 0,18% (A) e θ × 7 = 0,105% (B). Non cambia il calcolo; si propone di toglierla o correggerla
(«θ è circa 0,7 e 0,4 volte le spese di un cambio di lato nel periodo di tenuta») perché non faccia pensare a un margine di sicurezza che non c'è.
