# Programma 6 — quarta prova: il rimbalzo dopo i crolli, sulle monete mai usate

Scritto il 19 ottobre 2026, dopo le prime tre prove del programma 6 e **prima di scaricare i dati e di qualunque
calcolo** di questa. Vale `SECONDA.md` per i dati giornalieri, l'universo al tempo giusto e gli esclusi, dove qui non si
dice altro.

## 1. Perché questa

1. Le prime tre prove (indicatori di tendenza sulla singola moneta e fra monete, `RISULTATI*.md`) arrivano al massimo a
   uno Sharpe di 0,5 dal 2021; dopo 24 prove lo Sharpe corretto chiede circa **1,5** (stima dal calcolo della soglia con la
   dispersione degli Sharpe delle prove: circa 0,76 di soglia attesa per caso più l'incertezza di 4-6 anni). Altre prove
   di indicatori sugli stessi anni alzano solo la soglia.
2. La strategia più vicina all'esame in tutto il lavoro è nel programma 5: **I-017c4**, il long dopo un crollo di 4 ore
   (`research/programma5/idee/I-017/`): sul periodo R (2024-01 → 2026-09) **+2,198% netto a trade**, 211 trade, intervallo
   +0,564; +3,858, positiva in ogni anno, su 12 monete su 12, a costi doppi (+2,027%) e senza il giorno migliore
   (+1,772%); non passò per la soglia (p 0,0037 contro 0,0017), alzata dalle molte idee provate. È anche quello che il
   proprietario chiama scalping sulla volatilità (`docs/backlog.md`, P13).
3. Quella regola è stata misurata solo sulle 12 monete del programma 5. **Le monete mai usate** da nessuna prova di
   questo tipo sono la conferma più pulita senza aspettare: stessa regola, congelata, su monete diverse.

**Monete mai usate**: tutte quelle dell'archivio (sezione 3 di `SECONDA.md`, esclusi compresi), **tolte** le 100 di
`research/programma5/universo_top100.json`, le 12 di `research/programma5/universo_fase2.json` e le 12 del programma 5
(`MONETE`): su quelle il programma 5 ha fatto esplorazioni a ore, anche sui crolli. Le monete del vecchio gate
(`research/data/insample/`) restano dentro: il gate non ha mai misurato questa regola.

## 2. La regola (quella congelata di I-017c4, senza cambiare niente)

* Candele da **1 ora** (archivio pubblico di Binance, `klines/1h`, con il CHECKSUM).
* `lc` = logaritmo della chiusura; σ = deviazione standard dei rendimenti orari di `lc` sulle 720 ore prima (almeno 500);
  `z4` = (lc_t − lc_{t−4}) / (σ_{t−4} · √4).
* **Segnale** alla chiusura dell'ora t se `z4 ≤ −5`; **long** all'apertura dell'ora dopo; **uscita** alla chiusura
  dell'ora t+12 (12 ore); dopo un segnale, i segnali delle 12 ore dopo si saltano (pausa).
* Niente stop, niente obiettivo: come la regola congelata.

## 3. Le monete e i costi

* **Universo, mese per mese** con i soli dati di allora: le monete mai usate con la mediana del volume giornaliero in
  USDT degli ultimi 30 giorni di almeno **10 milioni** e almeno 30 giorni di candele. Un trade conta se il segnale cade
  in un mese in cui la moneta è nell'universo.
* **Costi più alti** che nel programma 5, perché sono monete più piccole e i crolli allargano lo scarto: commissione a
  mercato 0,05% e **scarto 0,15%** a ogni lato (0,40% andata e ritorno; nel programma 5 era 0,14%). Funding a ogni
  regolamento fra ingresso e uscita.
* **Il caso**: per ogni trade, 20 ingressi a un'ora presa a caso nello stesso mese e nella stessa moneta, con la stessa
  tenuta e gli stessi costi (come nel programma 5).

## 4. L'esame

Dal **2021-01-01** all'ultima ora scaricata. La regola è **confermata** se tutte e sette:

1. netto medio a trade positivo, intervallo al 95% sopra zero e **p ≤ 0,01** a una coda (bootstrap a blocchi di giorni
   di calendario, 10.000 volte);
2. il netto supera quello del caso, con l'intervallo della differenza sopra zero;
3. positiva in almeno **4 anni su 6** e nell'ultimo anno (dal 2025-10-01);
4. positiva a **costi doppi** (scarto 0,30% a lato);
5. positiva su almeno il **55% delle monete** con almeno 5 trade;
6. positiva **senza il giorno migliore**;
7. positiva sui **crolli propri**: i segnali in ore in cui il Bitcoin non crolla (`z4` del Bitcoin sopra −3). Così si
   vede se il rimbalzo c'è anche quando non è tutto il mercato a cadere, cioè nei giorni che il programma 5 non ha già
   visto sulle sue 12 monete.

È **una** prova di conferma di una regola sola: non è una ricerca. Lo Sharpe corretto non si applica; si riporta per
informazione il rendimento del capitale con una posizione del 10% del capitale a trade.

## 5. Cosa non si fa

* Nessun valore della regola si cambia (soglia, tenuta, pausa, σ): è congelata dal programma 5.
* Se la conferma riesce, la strategia va descritta al proprietario con i suoi numeri e i suoi limiti; prima del bot
  serve il suo sì. `DRY_RUN` resta vero.
