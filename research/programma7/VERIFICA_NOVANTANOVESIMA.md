# Verifica della prova 161 (NOVANTANOVESIMA.md, commit dd1399d, 15 novembre 2026) — modalità verifica

Nessun rendimento calcolato. Regole committate (dd1399d, 17:20 UTC) prima di ogni calcolo. Letti: le regole, le regole e la verifica della
157, il rapporto della revisione, lo script del revisore (come guida). Il codice della 157 e i caricatori non sono toccati.

## Dati scaricati (solo scarico, nessun calcolo) — `novantanovesima_dati.py`
* Candele orarie del prezzo mark (`data.binance.vision/data/futures/um/monthly/markPriceKlines/{S}/1h/{S}-1h-{AAAA-MM}.zip`) e, per il
  ripiego «prezzo scambiato» delle regole, `.../futures/um/monthly/klines/{S}/1h/...`, per BTCUSDT e ETHUSDT, mesi 2021-01 .. 2026-10
  (280 file, 0 errori), in `research/data/mark_1h/` (ignorata da git). Finestra controllata: dal 3 gennaio 2021 00:00 UTC (giorno prima
  dell'inizio, serve l'apertura) al 6 ottobre 2026 escluso: 2.000+ giorni, 50.400 ore attese a moneta.
* Buchi (stessi del revisore, confermati): **mark BTC 216 ore in 9 giorni; mark ETH 72 ore in 3 giorni**; prezzo scambiato orario 0 buchi
  su tutte e due. Quindi il ripiego delle regole (prezzo scambiato) basta sempre; non serve il ripiego al giorno.
* Impronte (sha256 unico dei file nominati e letti in ordine) e conto dei buchi: `risultati_novantanovesima/impronte_mark.json`.
* Formato: zip con CSV; intestazione presente o no a seconda del mese; timestamp in microsecondi dal 2025 (gestito).

## Le parti che si eseguono senza interpretazioni
* Dati, periodo, segnale (media del funding degli N giorni D−N … D−1, sopra zero, eseguito all'apertura di D), N = 30 e 90, costi (perpetuo
  0,06% per lato, pronti 0,15% per lato), uscita finale del 4 ottobre all'apertura del 5, mark orario con ripiego sul prezzo scambiato,
  liquidazione con il massimo orario del mark e mantenimento 0,5%, esame a quattro condizioni (letture A2 della 157) più nessuna
  liquidazione, conto delle prove 326-328, Sharpe corretto con `corretto_famiglie` e il mazzo (che contiene già «157 A» e «157 B» dalla
  riga 309 di `asticella.py`: le serie «161 A» e «161 B» si passano come nuove).
* Funding regolamento per regolamento: il regolamento delle 00:00 di D+1 appartiene al giorno D (convenzione di `seconda.py:8`, come nella 157 e nel
  revisore); valore = quantità aperta × apertura oraria del mark dell'ora del regolamento; ripiego prezzo scambiato orario. Il revisore ha
  verificato 6.570 regolamenti a moneta, tutti alle 00, 08 e 16 UTC. Letto così.

## Ambiguità che possono cambiare i numeri (non calcolo; servono le risposte della sessione principale)

**A1. Il riequilibrio fra le due monete e il capitale che si compone (sezione 5).** Le regole dicono «capitale composto per moneta»,
«al rientro Q si ricalcola dal capitale della moneta di quel giorno» e «riequilibrate solo quando una delle due rientra», ma non dicono *a quanto*.
Letture possibili: (a) la moneta che rientra riparte dal **proprio** conto (nessun trasferimento); (b) riparte da **metà del totale** dei due
conti, prendendo i contanti dall'altra solo se l'altra è fuori (se è dentro non si può togliere niente senza chiuderla, e il margine in più resta nei
future per regola 3); (c) metà del totale sempre, chiudendo se serve. Lettura proposta: **(b)**. Le tre danno numeri diversi perché le monete
sono quasi sempre dentro ma non sempre insieme (BTC fuori in pochi tratti in A, ETH in pochi tratti).
Collegata: «la strategia è la media delle due monete»: lettura proposta = rendimento del patrimonio totale (somma dei due conti) da un'apertura
alla successiva, composto; non 0,5·r_BTC + 0,5·r_ETH (che equivarrebbe a riequilibrare ogni giorno gratis). Le settimane si compongono dai giorni (non si sommano come nella 157).

**A2. Il prezzo dell'apertura del perpetuo per il margine e per la base.** La 157 e il revisore usano per il margine e la base l'apertura
giornaliera del *perpetuo scambiato* (`pan["open"]`) e il mark solo dentro la giornata. Le regole (sezione 2) dicono «al prezzo mark». Lettura proposta:
per tutto il conto del future (perdita aperta, margine, valore del perpetuo, base, funding, riduzioni) si usa l'**apertura oraria del mark delle 00:00**
(ripiego: apertura oraria scambiata); a pronti l'apertura giornaliera dei prezzi già scaricati; il prezzo del perpetuo di entrata Pe = mark delle 00:00.
La differenza mark−scambiato all'apertura è piccola ma cambia i numeri della base.

**A3. Entrata: da che capitale si calcola Q e dove stanno le spese d'ingresso.** Regole: «margine = 60% del valore del perpetuo; il capitale è
Q × prezzo × 1,6». Non è detto se le spese d'ingresso (0,15% pronti, 0,06% perpetuo) stanno *dentro* il capitale o si pagano in più. Lettura proposta:
Q = capitale / (S·(1+0,0015) + 0,6·M) con S apertura a pronti e M mark delle 00:00, cioè il capitale della moneta paga pronti, spese a pronti e margine;
la commissione del perpetuo (0,06% del valore) esce dal portafoglio dei future (margine iniziale ≈ 59,94%). Con la lettura della 157 (Q = C/1,6/S, spese sopra) il conto va in contanti negativi.

**A4. Il margine all'apertura è «dopo il regolamento delle 00:00?» e la liquidazione all'apertura.** Il regolamento delle 00:00 di D è già nel margine
quando il bot controlla (accade prima). Lettura proposta: ordine all'apertura = (1) regolamento delle 00:00 sul valore della quantità tenuta;
(2) controllo di liquidazione al mark delle 00:00 (se il margine vero è sotto lo 0,5%: liquidata); (3) se il segnale è fuori: uscita; (4) se il margine
vero è sotto il 45%: riduzione fino al 60%; (5) altrimenti niente. Il revisore non fa il punto (2) all'apertura (la candela 23 lo copre quasi del tutto).

**A5. Quantità da vendere per tornare al 60% (sezione 3).** Le regole non danno la formula. Lettura proposta (stesso metodo del revisore con 0,6):
con MB = margine vero (future + perdita aperta al mark, tutto già al netto del chiuso), x = (0,6·Q·M − MB) / (S·(1−0,0015) − M·0,0006 + 0,6·M),
dove la perdita sulla parte chiusa è già dentro MB, le spese 0,15% sul pronti venduto e 0,06% sul perpetuo ridotto escono dai contanti/margine, e il
margine dopo la riduzione è esattamente il 60% del perpetuo rimasto. Quantità non arrotondate nella misura principale; x ≤ Q (se x = Q si chiude tutto).
Se si legge invece «riportare il margine al 60% *prima* delle spese», cambia di poco ma cambia.

**A6. Liquidazione e rientro (sezione 4).** Letture proposte: margine perso = tutto il portafoglio dei future della moneta (anche il funding accumulato); nessuna
tassa di liquidazione oltre; il pronti resta in mano fino all'apertura dopo, poi si **vende** (0,15%) e, se il segnale è dentro, si ricopre da capo con le spese
d'ingresso (A3) dal capitale rimasto (A1); se il segnale è fuori resta fuori. Prezzo di liquidazione = quello che porta il margine al mantenimento (come il
revisore); la perdita oltre il margine, se il mark salta, non si conta (il margine perso non scende sotto zero). Alternativa possibile: tenere il pronti e rifare solo il perpetuo
(costi diversi). Conta solo se ci sono liquidazioni; l'esame chiede zero, quindi cambia i numeri solo nel caso di fallimento.

**A7. Il controllo a 1.000 USDT con i passi veri (sezione 5).** L'archivio pubblico non ha l'exchangeInfo e da qui l'interfaccia dei contratti è bloccata:
«exchangeInfo pubblico di oggi» non si può leggere. Lettura proposta: usare i filtri già nel repository (`bot/portafoglio/filtri_conto_vero.json`: passo e minimo 0,001, valore minimo
50 e 20 USDT), da dichiarare «filtri del repository, non di oggi», pronti uguale al perpetuo (passo 0,001); quantità d'ingresso arrotondate per difetto, riduzioni
per eccesso, ordini che riducono senza minimo di valore; la soglia «sotto quale capitale la gamba del Bitcoin non si apre» richiede un prezzo: lettura proposta = l'ultimo prezzo di apertura dei dati (4 ottobre 2026) e, accanto,
il massimo del periodo. È descrittivo (non entra nell'esame) ma la decisione sul filtro (repository o macchina) la deve dare la sessione principale.

## Ambiguità che non cambiano i numeri principali (solo descrittive)
* **B1.** Scomposizione per anno (funding, base, spese, rifornimenti): in USDT su 1.000 di capitale iniziale per anno di calendario; «rifornimenti» = valore a pronti venduto per le riduzioni e
  loro numero; il verdetto usa solo l'anno del lunedì come nella 157 (A2 chiusa).
* **B2.** Correlazioni: con G1 sui giorni e le settimane comuni dei file `risultati_prima/`, con la 157 sulle sue settimane `netto`, con Bitcoin (Pearson), come nella 157.
* **B3.** «Sempre dentro» e il caso guadagno dal 2022: stesso conto con segnale sempre 1; dal 2022 = settimane dal lunedì 3 gennaio 2022, senza ricalcolare.
* **B4.** Giorni positivi / fuori / negativi: come B1 della 157.
* **B5.** Il registro delle varianti: due righe (A e B); i controlli descrittivi non sono varianti; l'esito «nessuna liquidazione» è una colonna in più nelle note.

## Esito
**Sette ambiguità (A1-A7); A1, A2, A3, A5 cambiano i numeri; A4 e A6 solo di poco; A7 la misura descrittiva.** Non calcolo. Dati del prezzo mark e dello scambiato pronti, con impronte.
Per procedere basta una riga di conferma o correzione sulle letture proposte, in particolare A1 (la più pesante).
