# Prova 169 — La scadenza delle opzioni di Deribit: l'ora prima e le due ore dopo (idea 158)

Regole scritte il 22 novembre 2026 da strategy-scout, **prima di ogni calcolo** (nessun prezzo guardato), per l'indirizzo del proprietario
del 22 novembre («non si tratta di predire prima [...] la reazione ci sarà dopo»; le idee si provano senza aspettare il via libera). Le
committa la sessione principale; la esegue strategy-researcher (prima in modalità verifica), il giudizio lo dà backtest-auditor.
Non spegne e non sostituisce niente.

## Il fatto e chi è costretto ad agire
* **Il fatto**: ogni venerdì alle 08:00 UTC scadono le opzioni settimanali di Deribit su Bitcoin ed Ether; l'ultimo venerdì del mese
  scadono anche quelle mensili (e a fine trimestre le trimestrali). Il prezzo di chiusura è la media dell'indice nei 30 minuti prima delle
  08:00. La data e l'ora sono fisse e note da anni.
* **Chi è costretto**: chi vende le opzioni (i market maker) si copre di continuo comprando e vendendo il sottostante; alla scadenza le
  opzioni spariscono e la copertura va chiusa. Se i market maker sono corti di opzioni vicine al prezzo (gamma negativa), per coprirsi
  vendono quando il prezzo scende e comprano quando sale; scaduto il contratto, quella pressione sparisce. Non è una scelta: la copertura
  è un obbligo del loro mestiere, con orario fisso.
* **Fonte seria**: studio su 1.059 giorni di scadenza di Deribit dal 2021 al 2023 con candele da cinque minuti, rivista Finance Research
  Letters (autori e titolo da confermare nella verifica; lo conosco solo dal riassunto di CryptoSlate, «Bitcoin's $2.24 billion Friday
  options expiry teased a reversal then gave it back within hours»): il Bitcoin tende a scendere nell'ora prima della scadenza e a
  recuperare nelle due ore dopo, di più quando le opzioni vicine al prezzo sono molte e la gamma stimata è negativa. **Avvertenza**: studio
  su dati vecchi (2021-2023), nessuna conferma in avanti; l'effetto può essere sparito. Sul 2024-2026 è fuori campione (controllo scritto
  sotto).
* **Perché non è da manuale**: non è un indicatore sul prezzo; il calendario è un obbligo di copertura. Mai provato: `--cerca Deribit`,
  `scadenz`, `gamma` danno solo 110 (vendere opzioni), 121-123 (inclinazione), 155 (freno con l'indice di paura), 159 (base dei future
  trimestrali): nessuna è uno studio a eventi sull'orario di scadenza.
* **Probabilità: bassa.** L'effetto, se c'è, è di pochi decimi di punto per evento, e una coppia (corto, poi lungo) costa quattro scambi
  (circa 0,24% con le spese confermate). Si prova perché è economico (due varianti, dati gratuiti) e perché la ragione è un obbligo vero.

## Quanti eventi ci si aspetta (stima dal calendario, senza prezzi)
* Venerdì dal 1° gennaio 2021 al 30 ottobre 2026: circa **305** per ciascuna moneta (Bitcoin ed Ether), circa 610 coppie moneta-giorno.
* Ultimi venerdì del mese (mensili e trimestrali): **70** per moneta, circa 140 coppie.
* **Soglia che ferma la prova prima di caricare i prezzi**: se le scadenze confermate dalle liquidazioni di Deribit sono meno di **250**
  venerdì (variante A) o meno di **60** ultimi venerdì (variante B) per il Bitcoin, la prova si ferma e il rapporto lo dice.

## Dati (tutti gratuiti, senza registrazione e senza chiave)
* **Calendario delle scadenze**: `https://www.deribit.com/api/v2/public/get_last_settlements_by_currency?currency=BTC&type=delivery&count=1000&search_start_timestamp=<ms>`
  (e `ETH`), a pagine con `continuation`. Chiamata di prova del 22 novembre 2026: risposta valida (`BTC-22NOV26`, orario 08:00 UTC, prezzo
  indice 59.005,81), la storia parte dal 31 dicembre 2020 (`BTC-31DEC20-24000-P`). Una scadenza vale se per quel giorno ci sono liquidazioni
  alle 08:00 UTC; per distinguere venerdì e ultimo venerdì basta la data (si controlla che il venerdì abbia scadenze di opzioni, non solo del
  future giornaliero: nella pagina provata comparivano i future giornalieri, **da verificare** se le opzioni stanno nello stesso elenco o
  vanno cercate con `public/get_instruments?expired=true`).
* **Prezzi**: candele orarie del perpetuo di Binance (`BTCUSDT`, `ETHUSDT`) dall'archivio mensile `data.binance.vision/data/futures/um/monthly/klines/<SIMBOLO>/1h/`
  (prova del 22 novembre: file di marzo 2021 presente, risposta 200). Funding: archivio mensile ufficiale di Binance.
* **Periodo**: 1° gennaio 2021 – 31 ottobre 2026 (il 2021 conta intero).

## La regola (fissata qui)
1. Per ogni evento (venerdì di scadenza, moneta) alle **07:00 UTC** (apertura della candela oraria): **corto** il perpetuo.
2. Alle **08:00 UTC** (apertura della candela): chiude il corto e apre **lungo**.
3. Alle **10:00 UTC** (apertura): chiude il lungo. Un'ora prima (corto 07:00-08:00) e due ore dopo (lungo 08:00-10:00), come nello studio.
4. Pesi: Bitcoin ed Ether a metà del capitale ciascuno nei venerdì in cui ci sono tutti e due; altrimenti tutto sulla moneta che c'è.
   Nessuna leva oltre 1 volta il capitale; nessuna posizione fuori da queste tre ore.
5. Funding vero: il pagamento delle 08:00 UTC va alla gamba corta (aperta fino alle 08:00 compresa, convenzione del motore di G1).
6. **Spese** (confermate dal proprietario): 0,05% a mercato su ogni scambio + scarto 0,01% su Bitcoin ed Ether (non cambiano con le monete:
   solo queste due). Quattro scambi per evento (apri corto, chiudi e apri lungo = 2, chiudi lungo). Ordine limite (0,02%) solo come
   controllo descrittivo.
7. Rendimento di un giorno di evento = somma dei due tratti − spese + funding; negli altri giorni zero. Settimane da lunedì a domenica.

## Varianti (fissate, solo 2; contano 2 prove, una sola famiglia)
* **A**: tutti i venerdì di scadenza (circa 305 per moneta).
* **B**: solo gli ultimi venerdì del mese (circa 70 per moneta): le scadenze grandi, dove la copertura pesa di più (non si usa
  l'interesse aperto, che non è affidabile nella fonte gratuita).
Nessun orario, soglia o sottoinsieme diverso dopo i risultati. **Controlli descrittivi** (non varianti, nessuno cambia il verdetto):
il tratto corto da solo e il tratto lungo da solo; il solo 2024-2026 (fuori dal periodo dello studio); le spese con ordine limite; il
solo Bitcoin; le tre ore delle altre ore del venerdì (stesso orario, giorni senza scadenza grande) come confronto «a vuoto».

## L'esame (regole approvate dal proprietario il 9 e l'11 novembre)
Passa se: netto dopo i costi positivo; **ogni anno positivo** (2021, 2022, 2023, 2024, 2025, 2026 fino a ottobre); t almeno 3; Sharpe
corretto almeno 0,80 con il conto per famiglie (`asticella.corretto_famiglie`, tutte e due le varianti in `nuove`); eventi sopra la
soglia di cui sopra. Se i giorni sono pochi per avere un t da 3, il verdetto è «non promosso» e lo scrive il rapporto, senza correggere.
Serie settimanali nette come nelle prove 157-162.

## Cosa si consegna
`research/programma7/RISULTATI_CENTOSETTIMA.md`, serie in `research/programma7/risultati_centosettima/` (giornaliere e settimanali nette,
leggibili da `asticella.py`), script `research/programma7/centosettima.py` e `centosettima_dati.py` (calendario e candele, sul modello
di `centounesima_dati.py`), varianti in `research/trials/centosettima.csv`, dati in `research/data/` (non committati); a schermo al
massimo 20 righe. Nessuna chiamata a servizi a pagamento.
