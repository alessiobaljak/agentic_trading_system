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

## 6bis. L'esplorazione su C (aggiunta il 18 ottobre 2026, prima di calcolarla)

Le prime tre idee calcolate (I-005, I-006, I-007) sono cadute in C con un guadagno lordo vicino a zero: provare un'idea
alla volta è lento e spreca il periodo C, che serve proprio a cercare. Da qui:

* Si può **esplorare il periodo C** con una griglia di segnali scritta e committata **prima** del calcolo
  (`esplorazione/E-NNN/piano.md`): famiglie di segnali, valori, orizzonti, e i **criteri di promozione** a idea.
* Si registra **tutto** quello che la griglia calcola (`esplorazione/E-NNN/risultati.md`), non solo i segnali promossi,
  con il numero di celle provate.
* L'esplorazione **non apre mai V, R o A**: lavora solo su C (il guardiano lo impone, `motore5.controlla_periodo`).
* Un segnale promosso diventa un'idea con la sua scheda (al massimo 3 varianti, vicine al segnale), il calcolo su C con il
  motore a minuti del programma (costi, caso, bootstrap), e poi l'esame di sempre: congelata, V una volta con la soglia
  divisa per le varianti, R una volta. La soglia di V **non cambia**: è V, non C, a dire se un segnale trovato
  cercando è vero.

## 6ter. La soglia di V e le idee parenti di un V positivo (aggiunta il 18 ottobre 2026, ore 16:20 UTC)

**Cosa è successo.** Dopo le prime 16 idee: I-010 (rimbalzo dopo i crolli di qualche ora) e I-016 (reti d'acquisto
sotto il prezzo) hanno su V un netto positivo in **tutte e sei** le varianti, dopo i costi e a costi doppi, su 9-11 monete
su 12; ma p è 0,0018 (I-010c, soglia 0,0017) e 0,040-0,047 (I-016). **Restano bruciate**: la regola valeva quando le ho
calcolate. Il numero però mostra un difetto del disegno: nel 2023 i crolli sono pochi (I-010c: 74 trade in 27 giorni) e un
guadagno vero di +0,5-0,8% a trade non può arrivare a p 0,0017 in un anno solo; e dopo V c'è comunque R, che è un'altra
prova indipendente. Con V a 0,005 e R insieme, la probabilità che un'idea falsa passi tutto è dell'ordine di 0,005 × 0,02
= 0,0001: su 50 idee, 0,005 false attese, a prezzo di scartare quasi tutte le vere.

**Da qui, per le idee con la scheda scritta da adesso in poi** (le idee fino a I-016 tengono il loro esito):

1. **V**: netto positivo con p a una coda ≤ **0,05 diviso il numero di varianti**, e positivo a costi doppi. Con R dopo
   (intervallo sopra zero, 2 anni su 3, 60% delle monete, costi doppi), la probabilità che un'idea falsa passi tutte e due
   è circa 0,017 × 0,02 ≈ 0,0003: su 50 idee, meno di 0,02 false attese.
2. **R**, in più: il netto resta positivo **togliendo il giorno migliore** (il giorno di calendario con la somma dei netti
   più alta). Il motivo: il periodo R il modello lo conosce in parte (per esempio i grandi crolli del 2024 e del 2025), e
   un'idea non deve reggersi su un giorno solo.
3. **Le idee parenti di un V positivo.** Se un'idea entra sugli stessi eventi (stesso fenomeno, stesso lato) di un'idea che
   su V ha già dato un netto positivo, V per lei non è più una prova: lo conosco. Allora V è **costruzione** e la prova è
   **R da solo**, con la soglia severa: p a una coda ≤ **0,005 diviso il numero di varianti** su R, più tutte le condizioni
   di R (punto 2 compreso). Prima di aprire V si congela tutto: le varianti candidate, la regola meccanica che sceglie le 3
   da portare su R, e la prova su R.
4. Un'idea parente di un V **non positivo** può usare V come prova: saperlo va contro di lei, non a favore.

## 7. La fase 2: cercare sui dati recenti (aggiunta il 18 ottobre 2026, ore 16:45 UTC, prima di ogni calcolo della fase)

**Perché.** I-020 (lo scalping a limite nelle code delle candele) su C rendeva +0,19-0,32% a trade con t fino a 7, nel
2023 +0,02-0,15%, nel 2024-2026 zero: il vantaggio si è chiuso anno dopo anno. Lo stesso dicono l'autopsia delle strategie
vecchie (il vantaggio cala quando il mercato cambia) e le idee di tendenza, che su V facevano quanto il mercato. Cercare
sul 2020-2022 trova cose vere allora; il proprietario chiede strategie che **valgano oggi**. Da qui una seconda fase,
con le stesse regole di metodo (scheda prima del calcolo, regola congelata con le impronte, un periodo di prova aperto una
volta, tutto registrato), ma con i periodi spostati sul recente.

**I periodi della fase 2**

| Periodo | Date | Uso |
|---|---|---|
| **C2** costruzione | 2024-01-01 → 2025-06-30 | esplorazioni (6bis) e disegno delle idee |
| **V2** prova | 2025-07-01 → 2026-09-30 | una volta per idea, con la regola congelata |
| **A** in avanti | dal 2026-10-01 | si riporta; poi la prova nel paper |

Dichiarato: questi anni il modello li conosce in parte (i grandi movimenti del 2024 e del 2025); per questo la prova chiede
anche il risultato **senza il giorno migliore** e in tutte e due le metà di V2. I fenomeni già provati su R (il rimbalzo
dopo i crolli di I-017 e lo scalping a limite di I-020, sulle 12 monete) su V2 si provano **solo sulle monete nuove**.

**Le monete della fase 2**: le 12 del programma più **12 nuove**, scelte con una regola meccanica scritta qui prima di
guardare: fra i perpetui USDT-M dell'archivio di Binance con candele da 1 minuto mensili dal settembre 2023 o prima (100
giorni di storia prima di C2) e un file giornaliero di ottobre 2026 (cioè ancora quotati oggi), esclusi le 12 già usate e
i perpetui di monete stabili (USDC, FDUSD, TUSD, BUSD, USDP, DAI), le 12 con il **volume in USDT più alto nel settembre
2026** (dalle candele giornaliere). La lista e i volumi in `universo_fase2.json`.

**L'esame della fase 2** (idee J-NNN, al massimo 3 varianti, giudicate insieme):
1. **C2**: netto dopo i costi con l'intervallo al 95% sopra zero e maggiore del caso;
2. **V2**, una volta: netto con l'intervallo al 95% sopra zero e **p a una coda ≤ 0,005 / numero delle varianti**
   (bootstrap a blocchi di giorni, 10.000 ricampionamenti); positivo a costi doppi; positivo togliendo il giorno migliore;
   positivo in **tutte e due le metà** (2025-07-01 → 2025-12-31 e 2026-01-01 → 2026-09-30); positivo su almeno il **60%**
   delle monete con almeno 20 trade (almeno 5 monete); almeno **200** trade.
3. **A** si riporta sempre; una strategia che supera V2 entra nella prova del paper solo con il servizio separato, dopo.

Con fino a 30 idee nella fase 2, la soglia di V2 dà in media meno di 0,05 idee false oltre l'esame. Le idee della fase 1
restano col loro esito.

## 7bis. L'universo esteso: le 100 monete più scambiate (aggiunta il 18 ottobre 2026, ore 17:20 UTC, prima di guardare)

Il proprietario, il 18 ottobre 2026 alle 17:15 UTC circa: «va bene che hai iniziato con le 12 più scambiate oggi ma poi
devi analizzare l'intero universo o almeno le top 100 su binance future... scrivimi solo quando avrei le strategie come ti
dicevo questo non è un lavoro di velocità, se ci vogliono giorni va bene».

**La regola** (meccanica, scritta prima di calcolare la classifica): fra i perpetui USDT-M dell'archivio di Binance con le
candele da 1 minuto mensili da **febbraio 2025 o prima** (almeno 100 giorni di storia prima di V2) e un file giornaliero di
ottobre 2026 (ancora quotati), escluse le monete stabili, le **100 con il volume in USDT più alto nel settembre 2026**
(le 12 del programma comprese nella classifica). Lista e volumi in `universo_top100.json` (`strumenti/universo.py`).

* Una moneta quotata dopo gennaio 2024 entra in C2 dal momento in cui ha la storia che le misure chiedono (σ delle 720
  ore, almeno 500): conta meno, non è esclusa.
* Le esplorazioni della fase 2 sull'universo esteso hanno i loro piani (E-111 e seguenti); quelle già scritte sulle 24
  monete (E-101, E-102, E-103) restano com'erano.
* **V2 si fa sull'universo esteso** anche per le idee nate su 24 monete: le monete in più non sono state viste su C2, e
  danno alla prova più potenza. I fenomeni già provati su R (6ter; sezione 7) restano provati solo sulle monete diverse
  dalle 12 della fase 1.
* Per scaricare meno, le monete nuove si scaricano dal settembre 2023 (`scarico.py`, opzione `--dal 2023-09`).

## 8. La fase 3: la scelta che si adatta (aggiunta il 18 ottobre 2026, ore 20:40 UTC, prima di ogni calcolo della fase)

**Perché.** Dopo circa 40 idee, il quadro è chiaro e misurato: i fenomeni ci sono, ma cambiano col tempo. Il rimbalzo dopo
i crolli c'era nel 2020-2025 e non nella seconda metà del 2025; la continuazione dopo le salite non c'era nel 2020-2022,
c'era nel 2024-2025; lo scalping nelle code si è chiuso dal 2022. Una regola fissa scelta su un periodo cade nel periodo
dopo. Un esperto non tiene una regola per sempre: guarda cosa funziona adesso e lo cambia quando smette. La fase 3 prova
proprio questo, ma in modo meccanico e senza guardare avanti: **una procedura scelta prima** che ogni mese prende, fra
tutte le celle delle esplorazioni, quelle che hanno reso nei mesi precedenti, e le usa nel mese dopo.

**Cosa si prova** (idee M-NNN, al massimo 3 varianti): la procedura, non una regola. Le celle candidate sono tutte quelle a
una moneta delle esplorazioni (`esplora_fase2.celle_moneta` ed `esplora_calendario.celle`), nei due versi, sulle 24 monete
della fase 2, dal 2020 al 2026-09-30 (periodo **W**). Ogni trade di una cella ha il suo netto dopo i costi (commissione a
mercato e scarto **doppio** su ogni lato, funding; per le celle coperte con BTC anche la gamba di BTC). A ogni inizio mese
la procedura guarda **solo i trade già chiusi** prima di quel momento, e sceglie con una regola fissata prima.

**L'esame** (una volta, sul periodo che va dal primo mese con abbastanza storia al 2026-09-30):
1. netto medio a trade dei trade scelti con l'intervallo al 95% sopra zero e **p a una coda ≤ 0,005 / varianti**
   (bootstrap a blocchi di giorni, 10.000 ricampionamenti);
2. positivo a costi doppi e togliendo il giorno migliore;
3. positivo in almeno **4 anni su 6** (2021-2026) e **positivo su V2** (2025-07 → 2026-09) da solo;
4. positivo su almeno il 60% delle monete con almeno 20 trade;
5. **la prova a placebo**: la stessa procedura sulle celle con i rendimenti spostati nel tempo a caso (ogni cella di un
   numero di mesi a caso, in cerchio) deve dare in media zero; se il placebo dà un risultato positivo la procedura ha un
   difetto e l'esame è nullo finché non è corretto.
Dichiarato: questi anni il modello li conosce in parte e conosce gli esiti delle fasi 1 e 2; la procedura però non sceglie
mai con dati del mese in cui opera, e le sue scelte (finestra, numero di celle) sono quelle comuni, fissate qui prima.
Il periodo A (dal 2026-10-01) si riporta sempre e diventa la prova nel paper.
