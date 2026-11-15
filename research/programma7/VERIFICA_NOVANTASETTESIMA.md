# Verifica della prova 159 (`NOVANTASETTESIMA.md`, regole committate in 0a0b941) — 15 novembre 2026

Modalità verifica: nessun risultato calcolato, nessun commit, registro e regole non toccati. Ho solo scaricato i dati (permesso dal brief) e
controllato che esistano, siano interi e abbiano la forma attesa (date, colonne, buchi). Per vedere la forma ho stampato le ultime candele
di alcuni contratti: nessun rendimento calcolato.

**Esito: la prova NON è eseguibile senza interpretazioni.** Ci sono 4 ambiguità che cambiano i numeri (A1, A4, A5, A6) e le altre sono
precisazioni. Per ognuna la lettura proposta; basta un sì della sessione principale per ognuna, poi si ricommittano le regole.

## 1. I dati scaricati
Percorso (fuori da git, verificato con `git check-ignore`): `research/data/trimestrali_binance/` con `cm/` (coin-margined), `um/`
(USDT), `spot/`. Elenco con impronte sha256: `IMPRONTE_TUTTI.json` (1310 file; impronta del file elenco 66eadf6d…003fb). Ogni file è stato
confrontato con il suo `.CHECKSUM` pubblico: 1310 su 1310 uguali (un file scaricato a metà è stato riscaricato). Script usati (nella cartella
temporanea della sessione, non nel repository): scarico dai file mensili di `data.binance.vision`.

* **Coin-margined** `BTCUSD_*` e `ETHUSD_*`: tutte le 26 scadenze da `200925` a `261225`, candele a 1 giorno e a 1 ora, ogni scadenza con il
  suo file mensile. Nessun mese mancante nel mensile, quindi i file `daily` non servono.
* **USDT** `BTCUSDT_*`: da `210326` a `270326` (non «dal 2022»: esistono dal marzo 2021, vedi A6); `ETHUSDT_*` esistono ma la prova non li usa.
* **Pronti** `BTCUSDT` e `ETHUSDT` a 1 ora e a 1 giorno, da giugno 2020 a ottobre 2026, mensili (308 file). **Il pannello e `ore_di()`
  NON vanno bene come «pronti»**: sono i perpetui, non il pronti (la regola dice «già nel pannello o spot/monthly»: va scritto che si
  usa solo `spot/monthly`, vedi A9).
* **Ora di scadenza e prezzo di regolamento.** Ogni contratto finisce con una candela a 1 ora che apre alle 08:00 UTC del giorno di
  scadenza (volume zero o quasi zero, apertura = chiusura della candela precedente): **la sua chiusura è il prezzo di regolamento** ed è
  uguale alla chiusura della candela giornaliera del giorno di scadenza (verificato su 6 contratti). Quindi il file e la colonna sono:
  colonna 5 (chiusura) della candela 1 ora delle 08:00 (o della candela giornaliera di quel giorno). **La regola scrive invece «la candela delle
  07:00 UTC si approssima»: è una approssimazione inutile e peggiore**, la candela delle 08:00 esiste (A2).
* **Valore del contratto in moneta, verificato dai file**: volume in contratti (colonna 6) × valore ÷ chiusura = volume in moneta
  (colonna 8): BTC 100 dollari per contratto (170.785 contratti = 323,9 Bitcoin a 52.807), ETH 10 dollari (33.686 = 213,5 Ether a 1.575).
  Il contratto USDT è 1 Bitcoin, prezzi in USDT.
* **L'ultimo contratto non scade nel periodo**: `261225` ha dati fino al 31 ottobre; la prova si ferma al 4 ottobre (nessun dato dopo viene letto).
* **Dopo la scadenza i file continuano** con candele ferme (es. `BTCUSD_200925` e `201225` hanno 2.614 e 430 ore dopo la scadenza, a prezzo
  fisso). Vanno tagliate alla candela delle 08:00 (A2).
* **Buco nei dati dei future**: `BTCUSD_230929`, `BTCUSD_231229`, `ETHUSD_230929`, `ETHUSD_231229` non hanno candele dal 27 agosto 2023
  23:00 al 1° settembre 2023 00:00 (97 ore; il contratto è in corso). Il contratto tenuto in quei giorni è il `230929` (A7).
* **Buchi del pronti a 1 ora**: 11 buchi di 1-4 ore (giugno 2020 - marzo 2023); **nessuno cade sulle ore 08:00 e 09:00 di una scadenza**.
* **Unità del tempo**: i file del pronti dal 2025 hanno il tempo in microsecondi (16 cifre), prima in millisecondi (13); i future sempre in
  millisecondi. Va normalizzato (A9).
* **Esistenza del contratto a T + 3 mesi nell'istante T**: sì per ogni T, sia coin-margined (il contratto è quotato da 6 mesi prima della scadenza) sia
  USDT (quotato da 1 a 3 mesi prima, sempre prima di T). Eccezione di partenza in A5.

## 2. Le ambiguità e la lettura proposta

**A1. Il contratto in moneta e la copertura (da chiudere, cambia i numeri).** La regola dice «vendo il trimestrale in pari valore» e, per il
guadagno, «in dollari». Con il contratto in moneta il pari valore a dollari (contratti × 100 = moneta × prezzo a pronti) lascia un residuo
di moneta scoperta pari alla base, e il guadagno alla scadenza NON è più fisso in dollari (dipende dalla direzione): contraddice il perché
della prova. *Lettura proposta (A):* i contratti vengono dimensionati per coprire esattamente la moneta: contratti × 100 = moneta × prezzo del
future all'ingresso (nessun arrotondamento a contratto intero, capitale in scala libera). Il valore in dollari alla scadenza è allora
moneta × prezzo del future all'ingresso, noto all'ingresso. *Per B (USDT, contratto da 1 Bitcoin):* quantità uguale, ovvia.

**A2. Prezzo di regolamento.** *Proposta:* chiusura della candela a 1 ora delle 08:00 del giorno di scadenza (come sopra); la vendita del pronti
all'apertura della stessa candela del pronti (08:00). Il tempo di mezzo fra la chiusura del future (regolamento alle 08:00) e la vendita
(apertura delle 08:00) è lo stesso istante. Il valore del giorno alla scadenza usa lo stesso prezzo. Le candele del contratto dopo le 08:00 si ignorano.

**A3. Il tempo fra una scadenza e l'ingresso.** La regola dice «subito dopo si rientra» (uscita) e «alla candela che apre alle 09:00» (ingresso).
*Proposta:* l'uscita è alle 08:00 (vendita del pronti all'apertura delle 08:00, regolamento del future), l'ingresso alle 09:00; **per quell'ora si è
fuori dal mercato** (zero rischio, zero rendimento), la riserva resta ferma. Nel valore giornaliero (00:00 → 23:59) questo non cambia nulla
perché i valori sono chiusure giornaliere; il giorno della scadenza il valore a fine giorno è la posizione nuova (se entrata), con costi di
ingresso già dedotti.

**A4. «Si entra solo se la base è positiva dopo i costi»: a quale prezzo e quando (da chiudere, cambia i numeri).** La regola non dice con quali
prezzi si misura la soglia. Misurarla con l'apertura delle 09:00 e poi eseguire a quella stessa apertura usa un prezzo che non si conosce prima
dell'ordine. *Proposta:* segnale = base calcolata con le **chiusure delle candele delle 08:00** del future T+3 e del pronti (note alle 09:00),
esecuzione all'**apertura delle 09:00**; il rendimento realizzato usa i prezzi di esecuzione veri (con scarto), quindi può essere diverso dalla
base del segnale: va scritto. Giorni alla scadenza = (scadenza T+3 alle 08:00 − ingresso alle 09:00) in giorni, frazionari. Soglia: base
annualizzata > costi totali del ciclo ÷ durata in anni, dove i costi del ciclo sono quelli di A8 (non il «≈ 0,27%» scritto nella sezione
Costi, scritto prima della decisione dello 0,15% a pronti). Se non si entra: si resta fermi fino alla scadenza successiva, **il pronti è già stato
venduto e il capitale (pronti + riserva) è fermo in dollari a rendimento zero**, senza costi, e si ricontrolla **solo alla scadenza successiva** (non
ogni giorno): così dice la regola «nessuna ricerca di altre soglie».
*Se manca la candela delle 08:00 o delle 09:00 (non capita nei dati):* si salta e si scrive.

**A5. Prima scadenza e partenza dell'Ether (cambia i numeri).** Bitcoin: ingresso il 25 settembre 2020 09:00 nel `201225` (esiste dal 1° luglio 2020: ok).
La regola dice «Ether dal 25 dicembre 2020 (se il contratto prima non esiste)», ma **l'`ETHUSD_201225` esiste dal 5 agosto 2020**, quindi l'Ether
poteva entrare il 25 settembre 2020. *Proposta:* si segue la data scritta esplicitamente due volte (Ether dal 25 dicembre 2020, nel
`210326`); l'ingresso del 25 settembre 2020 dell'Ether non si fa e si scrive nel rapporto come differenza di lettura (un'eventuale variante
non è prevista). Prima del suo ingresso la quota dell'Ether (50%) resta ferma in dollari a rendimento zero (come i trimestri saltati).

**A6. Variante B (cambia i numeri).** La regola dice «dal 2022» ma i contratti USDT esistono dal marzo 2021, e non dice se B usa il 100% o il 50% del
capitale (A è 50/50 con l'Ether). *Proposta:* B = 100% del capitale sul solo Bitcoin USDT; primo ingresso alla prima scadenza T del 2022
(25 marzo 2022, 09:00, nel `220624`); stesso periodo finale, stessi costi, stessa soglia. Margine: vedi A8. Il Sharpe corretto e «ogni anno
positivo» di B si contano dal 2022 (il 2022 è un anno parziale).

**A7. Valore del giorno (punto 4 del brief, da chiudere).** La regola dice «pronti (chiusura) meno future (chiusura) in dollari», che per il contratto
in moneta non è la differenza dei due prezzi. *Proposta, a base di mercato ogni giorno (non solo alla scadenza):*
* **A (moneta):** moneta Q (a pronti); contratti corti N con N × 100 = Q × F_ingresso; valore in dollari del giorno d =
  S_d × [Q + N × 100 × (1/F_d − 1/F_ingresso)], con S_d e F_d chiusure giornaliere (23:59:59 UTC del giorno d: l'«ora 00:00» della regola è la
  chiusura del giorno prima; si etichetta il giorno d con la sua chiusura, come nelle serie settimanali del programma 6). Alla scadenza il valore
  tende a Q × F_ingresso. Il guadagno è in USDT/dollari perché Q è convertito in dollari a S_d.
* **B (USDT):** valore = Q × S_d − Q × (F_d − F_ingresso), cioè pronti più guadagno del future corto.
* Capitale = Q × S_ingresso (pronti, con i costi di acquisto) + 0,25 × Q × S_ingresso in USDT ferma. Il rendimento giornaliero = variazione del
  valore ÷ capitale all'inizio del trimestre (non ricalcolato ogni giorno), poi composto da una settimana all'altra solo dopo il rinnovo.
* **Buco di agosto 2023** nei future (A, B non ha il buco): si usa l'ultima chiusura nota (carico in avanti) e si contano i giorni riempiti
  nel rapporto; per il valore del giorno fa fede il giornaliero se esiste, altrimenti l'ultima chiusura oraria. Controllo: verificare se il file giornaliero
  ha i 5 giorni; se manca anche quello, carico in avanti.
* Giorno dell'ingresso: il rendimento di quel giorno parte dall'apertura delle 09:00 (costi di ingresso inclusi); giorno dell'uscita: fino al
  regolamento e alla vendita dello 08:00, costi di uscita inclusi.
* Giorni fermi (trimestre saltato, Ether prima del 2020-12-25): rendimento zero, contati nelle settimane.

**A8. Riserva del 25% e costi (da chiudere).** La regola dice «riserva in USDT per il margine, a rendimento zero» ma non quando si attinge né cosa
succede se non basta. *Proposta, senza nessun meccanismo di rabbocco nella simulazione* (la riserva conta solo nel denominatore del capitale):
* **A (margine in moneta):** il margine è la moneta a pronti stessa, con leva 1: la liquidazione richiederebbe che il prezzo raddoppi circa; la
  riserva in USDT non serve di norma. Controllo descrittivo: il massimo del future in ogni contratto contro il prezzo di ingresso (se supera +90%, segnalare).
* **B (margine in USDT):** il margine iniziale è la sola riserva (25% del nozionale = leva 4); il pronti NON conta come margine. Liquidazione
  teorica se il rialzo massimo (massimo orario del future) rispetto all'ingresso supera circa il 24-25% (si usa 25% meno il margine di
  mantenimento 0,4%, quindi 24,6%). Se succede: la prova **registra l'evento** e la posizione viene chiusa al prezzo di liquidazione con perdita
  piena della riserva, il pronti resta e si vende a scadenza... *ma la regola non lo dice: da decidere.* Proposta più semplice e prudente:
  l'evento si segnala come «riserva insufficiente» e il rendimento non lo simula (sarebbe un'invenzione); si riporta quante volte, in quale
  trimestre, e di quanto la riserva sarebbe mancata (controllo descrittivo già scritto «quanto margine sarebbe servito nel peggior giorno»).
  *Attenzione:* il motore ufficiale (costi, scarto, liquidazione) è per i perpetui e non per i future con scadenza: **non esiste un motore
  da usare**, quindi lo scrive la prova stessa e lo dichiara.
* **Costi del ciclo** (per trimestre, per gamba): pronti 0,15% per lato (decisione del 15 novembre) × 2 = 0,30%; future in apertura: ordine limite a
  0,02% (si assume eseguito perché per un ordine di vendita sull'apertura il massimo della candela è sempre ≥ apertura, vedi `nucleo.spese_limite`
  con `oltre=0`) più scarto 0,01% = 0,03%; uscita del future a scadenza: 0 (come scritto). Totale ≈ 0,33%, non 0,27%.
  La commissione di consegna di Binance non è nella regola: zero. Il costo dello 0,15% sul pronti all'ingresso e all'uscita si applica **a ogni
  rotazione** (vendita dello 08:00 e riacquisto delle 09:00), come scritto; non si tiene il pronti da una scadenza all'altra (sarebbe una variante).

**A9. Dati del pronti.** Solo `spot/monthly/klines` (BTCUSDT, ETHUSDT, 1 ora e 1 giorno), tempo normalizzato a millisecondi, non il pannello dei perpetui.
Il prezzo di apertura/chiusura a pronti per le 08:00/09:00 viene da lì; il pronti non ha buchi in quelle ore alle scadenze.

**A10. Fine del periodo.** `FINE = giorno(2026,10,5)` in `prima.py` (esclusivo) corrisponde a «4 ottobre compreso». Il contratto aperto al 4 ottobre
(`BTCUSD_261225` o `ETHUSD_261225`, e per B `BTCUSDT_261225`) si valuta al valore di mercato del 4 ottobre; il «chiuso a mercato» descrittivo
si calcola a parte con i costi (0,15% pronti + 0,05% future + scarto), non entra nell'esame.

**A11. Lo Sharpe corretto («159 A» e «159 B»).**
* `corretto_famiglie(nuove={"159 A": serie, "159 B": serie}, candidate={"159 A": {...}, "159 B": {...}})`. Le serie sono settimanali nette, come
  il programma 6 (settimane dal 4 gennaio 2021 al 5 ottobre 2026, `periodo()`): **i trimestri del 2020 (25 settembre - 31 dicembre) restano fuori dallo Sharpe
  corretto**, ma contano per «ogni anno positivo» (anno parziale, come scritto). Per «settimane intere»: stessa definizione di settimana delle
  altre prove (lunedì-lunedì, da verificare nel formato dei file `settimane_*.csv.gz`); i settimane fermi valgono zero.
* `serie_programma7()` ha l'elenco fisso dei nomi: le serie «159 A» e «159 B» si passano in `nuove=`, ma **la sessione principale deve poi aggiungerle
  a `serie_nuove()` o `serie_programma7()` (non è un compito della prova)**, altrimenti il mazzo dei prossimi calcoli non le conta.
* Le famiglie le decide la correlazione (`gruppi`, `TAGLIO`): «1 famiglia e 2 prove» è una previsione, non una regola; se A e B non sono nello stesso
  gruppo, il conteggio per famiglie sale di 2. Si riporta il numero vero.
* **Il conto del registro**: `python3 -m research.src.registro --riepilogo` dice già «conto delle prove: 324» con ultima prova 159. La regola scrive
  «da 320 a 322», il brief «da 322 a 324». *Proposta:* nelle formule si usa il numero di famiglie del mazzo (non il conto delle prove); il conto 324 è di
  competenza della sessione principale e il rapporto lo cita senza modificarlo. Da confermare che 324 comprende già le 2 prove di questa.
* Rendimento sulle sole serie settimanali: la volatilità è piccola (valore di mercato quasi costante); lo Sharpe sarà alto per costruzione. Nel
  rapporto si scrivono anche rendimento annuo netto, quota dei trimestri saltati e la media 2024-2026 contro il 4% della regola.

**A12. Cose già chiare e da non toccare.** Universo: Bitcoin ed Ether 50% e 50% (A), serie separate poi sommate; 2 varianti al massimo; costo a pronti
0,15% (decisione di 15 novembre); funding zero; nessun'altra soglia. I controlli di stress (10 maggio 2021, 9-12 novembre 2022, 10 ottobre 2025)
leggono la base dalle chiusure giornaliere dei file scaricati: nessuna ambiguità. La correlazione con G1, F5, K2, M7 è descrittiva (`gruppi`).

## 3. Cosa serve per partire
Un sì (o una correzione) su A1, A4, A5, A6, A7, A8 e A11; le altre si considerano chiuse con la lettura proposta se nessuno obietta.
Appena le regole sono ricommittate, i dati sono pronti in `research/data/trimestrali_binance/` e il registro delle varianti sarà `research/trials/novantasettesima.csv`.
