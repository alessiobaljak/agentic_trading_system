# Prova 163 — L'arbitraggio vero del funding fra Binance e Hyperliquid (idea 153)

Regole scritte il 21 novembre 2026 dalla sessione principale, **prima di ogni calcolo**, con il via libera del proprietario dello stesso
giorno («procedi», dopo la proposta: comprare una moneta su una borsa e venderla sull'altra, così il prezzo non conta, e incassare la
differenza del funding; solo dati gratuiti, nessuna spesa). La esegue strategy-researcher (prima in modalità verifica), il giudizio lo dà
backtest-auditor. Non spegne e non sostituisce niente.

## Il perché
* La stessa moneta paga funding diversi sulle due borse: dal giugno 2023 al 5 ottobre 2026 lo scarto medio fra Hyperliquid e Binance è
  **+5,9% l'anno** sulle 213 monete abbinate (`RISULTATI_SETTANTATREESIMA.md`); secondo BitMEX (rapporto del secondo trimestre 2026,
  citato in `SETTANTATREESIMA.md`) Hyperliquid ha pagato in media il 7,17% l'anno più di Binance sul Bitcoin e il 5,31% sull'Ether.
* Le prove 135 e 137 hanno usato quello scarto come **segnale** per comprare e vendere solo su Binance (no). Qui non si scommette sul
  prezzo: si tengono **due gambe opposte sulla stessa moneta, una per borsa**, e si incassa la differenza. Nella prova 162 (USDT contro
  USDC, stessa borsa) la differenza era troppo piccola (2-5% l'anno lordo); fra due borse con clientele diverse è più grande.
* Perché resta lì: serve capitale su due piattaforme con margini separati (una sulla catena), e i grandi arbitraggisti la riducono ma non
  la chiudono. Con capitale piccolo l'ostacolo è minore.
* **Rischi scritti prima**: le gambe hanno margini separati (nessuna compensazione fra le borse): un movimento forte può liquidare una
  gamba prima che si spostino i soldi; il rischio di una delle due piattaforme (non misurabile qui, si scrive); lo storico di Hyperliquid
  c'è solo per le monete quotate oggi (sopravvivenza, come nella 135).

## Dati
* Funding di Hyperliquid: `fundingHistory` dell'interfaccia pubblica (ogni ora), monete abbinate come in `settantatreesima.funding_hl`
  (prefisso `k` = `1000…USDT`). Funding di Binance: l'archivio mensile ufficiale (niente stima del pannello: si usano solo mesi interi).
* Prezzi: candele orarie e giornaliere di tutte e due le borse (Binance: archivio, prezzo mark; Hyperliquid: `candleSnapshot` pubblico).
* **Periodo**: dal 5 giugno 2023 (come la 135) al **31 ottobre 2026** (ultimo mese intero dell'archivio del funding di Binance).
* **Universo fissato prima**: le monete abbinate, presenti su tutte e due le borse con almeno 30 giorni interi di funding e prezzi su
  tutte e due; elenco e primo giorno scritti nel rapporto prima dei risultati.

## La regola (fissata qui)
1. Per ogni moneta, alla decisione del giorno D (apertura delle 00:00 UTC) si calcola d = media giornaliera di (somma del funding di
   Hyperliquid del giorno − somma del funding di Binance del giorno) sui **L** giorni interi prima di D (solo pagamenti con orario prima
   delle 00:00 di D).
2. Se d > +θ: **venduta su Hyperliquid e comprata su Binance** (si incassa d); se d < −θ: il contrario; altrimenti nessuna posizione.
3. Pesi uguali fra le monete scelte; valore di ogni gamba = capitale / numero di monete scelte (in totale una gamba vale 1 volta il
   capitale). **Capitale diviso a metà fra le due borse**: leva circa 2 su ciascuna.
4. **Margine, controllato ogni ora con i prezzi delle due borse**: ogni borsa ha il suo margine (metà capitale ± i guadagni e le perdite
   delle sue gambe ± funding e spese). Una volta al giorno, alla decisione, si riporta il margine a metà per borsa con un trasferimento
   (costo fisso 1 USDT a trasferimento, effetto dalla decisione dopo, cioè un giorno di ritardo). Se in un'ora il margine di una borsa
   scende sotto il **mantenimento** (0,5% del valore delle sue gambe, come nella 161) quella gamba è **liquidata**: si chiude al prezzo di
   quell'ora con una perdita del 1% in più, e l'altra gamba si chiude alla decisione dopo. Il giorno «a rischio» è quello in cui il
   margine di una borsa scende sotto il 10% del valore delle sue gambe.
5. Rendimento giornaliero = (rendimento della gamba comprata − quello della venduta, ciascuno sulla sua borsa) + funding vero di tutte
   le scadenze di ciascuna borsa (orari dopo l'apertura di D fino all'apertura di D+1 compresa, come nel motore di G1) − spese.
6. **Spese**: Binance come confermato dal proprietario (0,05% a mercato + scarto 0,01% su BTC, ETH, SOL e 0,02% sulle altre); Hyperliquid
   la commissione pubblica del livello base per chi prende liquidità (da scrivere con la fonte nella verifica; se non verificabile, 0,045%)
   più lo stesso scarto. Sempre a mercato (conservativo). Si paga solo sul valore scambiato: apertura, chiusura, cambio di lato,
   riequilibrio quando cambia il numero di monete.

## Varianti (fissate, solo 2)
* **A (lenta)**: L = 30 giorni, θ = 10% l'anno (0,0274% al giorno), decisione solo il primo giorno del mese.
* **B (settimanale)**: L = 7 giorni, θ = 20% l'anno (0,0548% al giorno), decisione solo il lunedì.
Le soglie stanno sopra il costo di un giro completo (quattro gambe, circa 0,28% del valore) diviso per la tenuta. Nessuna soglia, finestra
o universo diverso dopo i risultati. Conta **2 prove**. Controlli descrittivi (non varianti): solo Bitcoin ed Ether; le prime 30 monete
per volume contro le altre (il «siamo piccoli»); le spese con ordine limite; quante liquidazioni e giorni a rischio; il guadagno senza la
moneta migliore; la correlazione con G1.

## L'esame (regole approvate dal proprietario il 9 e l'11 novembre)
Passa se: netto dopo i costi positivo; **ogni anno positivo** (2023 da giugno, 2024, 2025, 2026 fino a ottobre); t almeno 3; Sharpe
corretto almeno 0,80 con il conto per famiglie (`asticella.corretto_famiglie`, tutte e due le varianti in `nuove`); **nessuna
liquidazione**; netto almeno **3% l'anno** sul capitale (sotto: «non promosso per poco valore»). Serie settimanali nette come nelle prove
157-162.

## Cosa si consegna
`research/programma7/RISULTATI_CENTOUNESIMA.md`, serie in `research/programma7/risultati_centounesima/` (giornaliere e settimanali nette,
leggibili da `asticella.py`), script `research/programma7/centounesima.py` (e uno script per i dati se serve, sul modello di
`novantanovesima_dati.py`), varianti in `research/trials/centounesima.csv`, dati in `research/data/` (non committati); a schermo al
massimo 20 righe. Nessuna chiamata a servizi a pagamento.
