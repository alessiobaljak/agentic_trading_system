# Prova 159 — La base dei future trimestrali di Bitcoin ed Ether come rendimento fisso (comprare e vendere il trimestrale fino alla scadenza)

Regole scritte il 15 novembre 2026 dallo strategy-scout, **prima di ogni calcolo**: nessun prezzo guardato, solo un controllo che i file
pubblici esistano. La prova la esegue strategy-researcher, il giudizio lo dà backtest-auditor. Numero 159 (ultima nel registro: 156; la 157,
funding coperto sul perpetuo, e la 158 sono di altri agenti). **Non è l'idea 139** (base come segnale per scegliere monete, scartata per i
pochi casi): qui la base è un rendimento che si incassa tenendo fino alla scadenza.

## Il perché forte
* **Ragione economica.** Chi vuole salire con la leva paga un premio per avere il future più caro del pronti; chi vende il future e compra il
  pronti incassa quel premio e, alla scadenza, il prezzo del future torna uguale al pronti per costruzione (consegna in contanti al prezzo
  medio dell'indice). Il rendimento è **noto al momento dell'ingresso** e non dipende dalla direzione del Bitcoin. Fonte: Schmeling,
  Schrimpf e Todorov, «Crypto carry», BIS Working Paper 1087 (2023): il premio dei future sulle crypto è stato in media alto (due cifre
  l'anno nel 2020-2022) e **crollato dopo il 2022**; è un premio per la domanda di leva, non gratuito.
* **Differenza dalle prove fatte.** Il funding dei perpetui (G1, F5, la 157) è un tasso variabile pagato ogni 8 ore; la base del trimestrale è
  fissata all'ingresso. Non c'è rischio di funding che si gira. `--cerca trimestral` = 0; le voci vicine sono la 97 (CC, perpetuo coperto con
  il pronti) e l'idea 139 (scartata come segnale).
* **Dato mai usato.** I future con scadenza in dollari-moneta (coin-margined) di Binance dal 2020; i future in USDT con scadenza dal 2022.
  Gratuiti su `data.binance.vision`.
* **Avviso onesto sui numeri attesi.** Nel 2024 la base annua è stata a occhio intorno al 10-15%, nel 2025 e 2026 molto più bassa (5-8%, nei
  periodi calmi 3-5%), cioè poco sopra i titoli di stato. Con costi di ingresso e di rotazione di circa 0,2-0,3% a trimestre il netto atteso
  è **3-8% l'anno su capitale pieno**, forse meno nel 2025-2026; un rendimento regolare ma piccolo. Rischio vero: (1) chiamata di margine
  sulla gamba corta nei rialzi forti (la perdita sul future è coperta dal guadagno sul pronti, ma solo se il margine si può rimettere in
  tempo: per questo si tiene una riserva); (2) rischio della borsa (tutto sta su Binance); (3) la base può diventare negativa, e allora non
  si entra. Non è un guadagno ogni giorno: si vede ogni giorno solo come valore del contratto, il grosso arriva alla scadenza.

## Dati (tutti gratuiti, `https://data.binance.vision/data/`)
* Candele a 1 giorno e a 1 ora dei future con scadenza: **coin-margined** `futures/cm/monthly/klines/BTCUSD_YYMMDD/1d/` e `ETHUSD_YYMMDD`
  (contratti dal 2020: BTCUSD_200925, ETHUSD_201225; controllo di esistenza fatto il 15 novembre: file di 2020, 2023 e 2026 presenti) e
  **in USDT** `futures/um/monthly/klines/BTCUSDT_YYMMDD` (dal 2022; presenti 2022-2023). Scadenze: ultimo venerdì di marzo, giugno,
  settembre, dicembre, alle 08:00 UTC. Se un mese manca nel mensile si usano i file giornalieri (`daily`); se mancano, si scrive e si salta.
* Pronti: candele a 1 ora e a 1 giorno di BTCUSDT e ETHUSDT (già nel pannello del repository o `spot/monthly/klines`).
* Prezzo di consegna: la chiusura dell'ultima candela del contratto (il prezzo di regolamento è la media dell'indice nell'ultima ora; con la
  candela a 1 ora delle 07:00 UTC si approssima, dichiarato).
* Nota: si leggono solo i prezzi delle candele dei future con scadenza, che sono pubblici e non sono funding; nessun costo di prestito è
  nei dati, si usa quello fissato qui sotto.

## L'operazione (fissata)
* Universo: Bitcoin ed Ether, 50% e 50% del capitale, con le serie tenute separate e poi sommate.
* **Ingresso**: dopo ogni scadenza T (alle 08:00 UTC, appena regolato il contratto) si sceglie il contratto con scadenza **T + 3 mesi**
  (il trimestrale successivo) e si entra alla **candela a 1 ora che apre alle 09:00 UTC** (esecuzione all'apertura dopo il segnale; il
  segnale, la scadenza, è noto da prima): compro a pronti, vendo il trimestrale in pari valore. Prima scadenza: 25 settembre 2020 per il
  Bitcoin, 25 dicembre 2020 per l'Ether (se il contratto prima non esiste).
* **Soglia**: si entra **solo se la base annualizzata all'ingresso** = (prezzo future / prezzo pronti − 1) × 365 / giorni alla scadenza è
  **sopra lo 0%** al netto dei costi (cioè sopra la somma dei costi sotto divisa sulla durata). Altrimenti si resta fermi fino alla scadenza
  successiva (nessuna ricerca di altre soglie). Si scrive la quota di trimestri saltati.
* **Uscita**: si tiene fino alla scadenza (nessuna uscita anticipata). Il future si chiude da solo al prezzo di consegna; il pronti si
  vende alla candela a 1 ora delle 08:00 UTC con il prezzo di apertura, e subito dopo si rientra sul trimestrale successivo.
* Rendimento: in dollari, **capitale = 1 di pronti + 0,25 di riserva in USDT per il margine, a rendimento zero** (versione prudente, scritta
  per avere il numero sul capitale vero). Si calcola anche il rendimento sul solo pronti (descrittivo).
* Valore del giorno: ogni giorno alle 00:00 UTC pronti (chiusura) meno future (chiusura) in dollari, per misurare la discesa massima
  del contratto in corsa (la perdita sul valore di mercato prima della scadenza).

## Costi (del programma 7 più il costo a pronti di Binance)
* Pronti: commissione 0,10% a mercato (0,075% con BNB) a pronti, scritto qui **0,10%** per prudenza; ordine limite 0,10% uguale (a pronti la
  commissione è la stessa); scarto 0,01% su BTC e su ETH (BTC, ETH e SOL: 0,01%). *Da confermare dal proprietario: il costo a pronti è
  quello standard di Binance, non è nei valori del 7 novembre.*
* Future con scadenza: 0,05% a mercato, 0,02% con ordine limite per l'apertura (si usa il limite per un'ora a 0,02%, poi a mercato, come
  la prova 155), scarto 0,01%.
* Totale per trimestre e per gamba, entrata e uscita: circa 2 × (0,10% + 0,02%) + scarti ≈ 0,27%. L'uscita del future a scadenza è gratuita.
* **Funding: zero** (i future con scadenza non pagano il funding): è il punto della prova. Il pronti non ha costo di prestito.

## Periodo
Dall'ingresso 25 settembre 2020 (Bitcoin) al 4 ottobre 2026 compreso, come `FINE` di `prima.py`; i contratti attivi alla data di fine si chiudono
a mercato al prezzo del future della candela del 4 ottobre (descrittivo, scritto a parte, fuori dal conto per l'esame). Non si guardano i
dati dopo. Il 2020 e il 2026 sono anni parziali, contano per «ogni anno positivo». L'Ether parte dal 25 dicembre 2020.

## Varianti (fissate, al massimo 2)
A: coin-margined (Bitcoin ed Ether), come sopra, dal 2020. B: la stessa operazione sulla sola scadenza in USDT del Bitcoin (dal 2022), per
vedere se il risultato cambia con un contratto diverso (stessa serie di date, stessa famiglia). Nessun'altra variante dopo i risultati.
Conta **1 famiglia di prove e 2 prove nel conto** (il conto passa da 320 a 322; la formula conta le famiglie). Controlli descrittivi,
non varianti: rendimento annualizzato della base all'ingresso per trimestre; trimestri saltati; rendimento netto per trimestre; per anno;
discesa massima sul valore di mercato; mesi positivi; la base contro il funding medio del perpetuo nello stesso trimestre (per vedere se
la base paga più del funding); la correlazione con G1, F5, K2 e M7 (`programma6/asticella.py`, `gruppi` con `TAGLIO`).

## L'esame (regole approvate dal proprietario il 9 novembre)
Passa se: netto dopo i costi positivo; **ogni anno positivo**; t almeno 3; Sharpe corretto almeno 0,80 con il conto per famiglie
(`corretto_famiglie` in `programma6/asticella.py`, esempio `audits/repro/prova28_2026-11-11.py`, voce 11). **Avviso onesto**: un rendimento
molto regolare dà uno Sharpe alto anche se piccolo, ma i rendimenti sono a trimestre e l'esame va fatto sulla serie **giornaliera** del valore
di mercato (pronti meno future più la riserva) e sulle settimane intere, non sul solo rendimento a scadenza (altrimenti lo Sharpe è
gonfiato dal prezzo fisso). Anche se l'esame passa, **la rendita è piccola**: si scrive il rendimento annuo netto sul capitale con riserva
accanto allo Sharpe; se è sotto il 4% l'anno per la media 2024-2026 lo si dice nel rapporto («regolare ma poco più dei titoli di stato»).
**Controlli sul rischio della borsa** (descrittivi): quanto margine sarebbe servito nel peggior giorno (rialzo massimo del Bitcoin in un
giorno e su 7 giorni durante un contratto: la riserva di 0,25 basta?); la serie del 12 marzo 2020 non esiste (parte dopo); la base nei
giorni del 10 maggio 2021, 9-12 novembre 2022 (caduta di una grande borsa) e del 10 ottobre 2025 (liquidazioni di massa) come stress.

## Cosa si consegna
Rapporto su file in `research/programma7/RISULTATI_NOVANTASETTESIMA.md`, serie giornaliere in `risultati_novantasettesima/`, script
`novantasettesima.py`, registro delle varianti in `research/trials/novantasettesima.csv`, a schermo al massimo 20 righe. I file scaricati
da `data.binance.vision` vanno in `research/data/` (fuori da git, con l'impronta).

## Testo della riga del registro
| 159 | BQ: la base dei future trimestrali di Bitcoin ed Ether come rendimento fisso: comprare a pronti e vendere il trimestrale successivo alla scadenza, tenere fino alla scadenza, solo se la base è positiva dopo i costi (A: coin-margined dal 2020; B: Bitcoin in USDT dal 2022), capitale con riserva di margine del 25% (`programma7/NOVANTASETTESIMA.md`); Schmeling, Schrimpf e Todorov, BIS 2023; diversa dall'idea 139 | 2 | da fare | da fare |

## Decisione della sessione principale del 15 novembre 2026, prima di ogni calcolo
Il costo a pronti vale **0,15% per lato** (0,10% di commissione più 0,05% di scarto), lo stesso della prova 97 (`TRENTACINQUESIMA.md`,
riga 27) e della prova 157: è il precedente già usato nel registro, più prudente dello 0,10% proposto sopra.
