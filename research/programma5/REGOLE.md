# Programma 5: le regole

Scritte dal coordinamento il 18 ottobre 2026 (sera), dopo la delega del proprietario: «non continuare a chiedermi le
autorizzazioni, procedi ad oltranza fino a che non avrai trovate delle strategie profittevoli che devono valere le crypto
ad oggi in corso [...] scrivimi solo quando avrai trovate diverse strategie che si possono applicare a diverse crypto
anche se ci volessero dei giorni». Valgono per tutte le idee del programma. Lo stato e la coda delle idee sono in
`STATO.md`.

## 1. Cosa cerchiamo

**Strategie di trading attivo, anche scalping sulla volatilità**, che:
1. guadagnano **dopo costi realistici** e anche **a costi doppi**;
2. reggono su **più monete** (almeno 3 per strategia);
3. reggono su **dati recenti** (2024-2026) e, appena ce ne sono abbastanza, sui dati nuovi (da ottobre 2026);
4. hanno un **perché** (chi perde dall'altra parte, e perché dovrebbe continuare a perdere).

Il programma finisce, e il coordinamento scrive al proprietario, quando **almeno 3 strategie** di idee diverse superano
tutto l'esame (sezione 5). Prima, nessun messaggio; eccezioni: un problema che blocca il lavoro (macchina giù, disco
pieno, accesso negato) o una delle regole che non si negoziano in gioco.

## 2. Le monete

Dodici perpetui USDT-M liquidi, quotati oggi e con storia dal 2020-2021: **BTC, ETH, SOL, XRP, BNB, DOGE, ADA, LINK, AVAX,
LTC, DOT, TRX** (tutti `…USDT`). Un'idea può usarne meno (per esempio se il dato che le serve manca), mai di più senza
scriverlo prima.

## 3. I dati

Archivio pubblico di Binance (`data.binance.vision`), con il controllo del CHECKSUM, in `research/data/p5/` (fuori da git;
le impronte in `research/programma5/scarico_*.json`):
* candele da 1 minuto (prezzo di scambio), da cui si fanno 5, 15 e 60 minuti;
* il file `metrics` ogni 5 minuti (interesse aperto, rapporti long/short, rapporto fra acquisti e vendite aggressive): c'è
  da settembre 2020 per BTC e da dicembre 2021 per le altre; righe doppie e fuori ordine si tolgono e si riordinano;
  l'orario si tratta come **fine** dei 5 minuti (prudente: niente dati futuri); il file del giorno si considera noto solo
  dal giorno dopo per il paper (ritardo di pubblicazione), ma nello storico vale al suo orario;
* il funding a ogni regolamento, con il suo intervallo vero.

## 4. I periodi

| Periodo | Date | Uso |
|---|---|---|
| **C** costruzione | dall'inizio dei dati al 2022-12-31 | si disegna l'idea e si fissano i valori |
| **V** validazione | 2023-01-01 → 2023-12-31 | una volta per idea, con la regola congelata |
| **R** recente | 2024-01-01 → 2026-09-30 | una volta per idea, dopo V; già aperto per altre idee su alcune monete e conosciuto dal modello: si dichiara |
| **A** in avanti | dal 2026-10-01 ai dati più nuovi | si riporta; diventa la prova nel paper |

* **L'ordine non si cambia**: prima C, poi V, poi R. Un'idea si congela (regola completa con tutti i valori, impronta
  SHA-256 del file) **prima** di aprire V; non si tocca dopo. Un'idea che cade in V o in R è **bruciata**; una versione
  modificata è un'idea nuova, con la sua scheda.
* Al massimo **3 varianti** per idea, tutte congelate insieme; vale la migliore solo se supera l'esame tenendo conto delle
  3 (soglia divisa per 3).

## 5. L'esame

**I costi** (per lato): commissione 0,05% a mercato, 0,02% con ordine limite; scarto di prezzo 0,01% per BTC, ETH, SOL e
0,02% per le altre; **nelle esplosioni** (movimento di 5 minuti oltre 8 volte il tipico) lo scarto si raddoppia, perché il
libro degli ordini si svuota. Il funding si paga o si incassa a ogni regolamento attraversato. Ogni risultato si riporta
anche **a costi doppi**.

**Il confronto con il caso**: le stesse uscite, applicate a ingressi presi a caso sulle stesse monete e negli stessi mesi,
tanti quanti i trade della strategia (20 ripetizioni).

**L'incertezza**: bootstrap a blocchi di giorni di calendario (i trade di monete diverse nello stesso giorno si
ricampionano insieme), 2.000 ricampionamenti, seme 2026.

**Un'idea supera l'esame se, in ordine:**
1. **C**: guadagno medio a trade dopo i costi positivo, con l'intervallo al 95% sopra zero, e maggiore del caso;
2. **V**: guadagno medio dopo i costi positivo con p a una coda ≤ **0,005** (diviso per il numero di varianti), e positivo
   a costi doppi;
3. **R**: guadagno medio dopo i costi positivo sul periodo, con l'intervallo al 95% sopra zero; positivo in almeno 2 dei
   3 anni (2024, 2025, 2026 fino a settembre); positivo a costi doppi;
4. **Monete**: nel periodo R, positivo su almeno il **60%** delle monete con almeno 20 trade, e almeno 3 monete;
5. **Frequenza**: almeno 100 trade in R su tutte le monete (una strategia che non opera non serve).

Con fino a 50 idee nel programma, la soglia di V (0,5%) dà in media meno di 0,25 idee false oltre V; il passaggio su R
(un altro periodo, più anni, più monete) le riduce ancora. **Il periodo A** si riporta sempre, ma non decide finché ha meno
di 100 trade.

## 6. Come si lavora

* Ogni idea ha una scheda `idee/I-NNN/scheda.md` con: meccanismo, fonte se c'è, regola, valori, varianti; si committa
  **prima** di calcolare su C. I numeri su C si scrivono in `idee/I-NNN/C.md`; la regola congelata in
  `idee/I-NNN/congelata.md` con l'impronta, **prima** di V; poi `V.md`, `R.md`, `A.md`.
* Ogni esito va in `STATO.md` (registro delle idee), anche quando l'idea è bruciata, con il motivo: è la memoria del
  programma.
* Gli strumenti sono in `research/programma5/strumenti/`, con i loro test; un difetto trovato si corregge, si scrive, e
  le idee già calcolate con lo strumento sbagliato si rifanno.
* Il coordinamento lavora a turni (si risveglia da solo) e lascia sempre lo stato in `STATO.md`, così un turno nuovo
  riparte da lì.
* Il bot non si tocca durante la ricerca. Le strategie che superano l'esame entrano nel paper solo con il servizio
  separato (`docs/proposta_ripartenza.md`, sezione 4), dopo.
