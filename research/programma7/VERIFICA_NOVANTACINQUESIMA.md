# Verifica della prova 157 (NOVANTACINQUESIMA.md, commit 0a0b941) — modalità verifica

Nessun rendimento calcolato. Regole committate (0a0b941, 15 novembre 2026, prima di ogni calcolo).

## Controlli sui dati fatti (solo presenza, nessun rendimento)
* Pannello: parte dal 1° gennaio 2020 e arriva al 12 novembre 2026. BTCUSDT ed ETHUSDT: apertura del perpetuo presente in tutti i 2.191 giorni dal 6 ottobre 2020 al 5 ottobre 2026; funding presente, mai vuoto.
* Funding: per tutti i 2.191 giorni e per le due monete, il funding del pannello è identico a quello letto dai file veri (`funding_giorni`), nessun giorno mancante nei file, nessun giorno riempito con la media. L'ultimo giorno dei file è il 31 ottobre 2026.
* Pronti scaricati (mesi 2020-12 .. 2026-10, con `novantacinquesima_dati.py`, che passa da fuori l'elenco dei mesi; il file della 97 non è toccato) in `research/data/spot_1d/`: apertura a pronti presente in tutti i 2.101 giorni dal 4 gennaio 2021 al 5 ottobre 2026 (compreso il 5, serve all'uscita finale), nessun buco. Scarto massimo apertura pronti contro perpetuo: BTC 0,19%, ETH 0,52% (nessun giorno oltre il 2%).
* Impronte (sha256): BTCUSDT.csv.gz `f7d154a55dd47534b0fdeca70ff78a7fbae657faf27fae74abc74f3575fa18c2` (18.980 byte); ETHUSDT.csv.gz `5a77427447048847463e2952ea04dce017e85c074d9db62a2ee3d2fbaac06740` (17.154 byte). Anche in `risultati_novantacinquesima/impronte_pronti.json`.
* Esistono i file di confronto: `risultati_prima/giorni_G1.csv.gz`, `settimane_G1.csv.gz`, `risultati_trentacinquesima/settimane_CC.csv.gz`.

## Ambiguità che possono cambiare i numeri

**A1. Deriva delle gambe: «senza ribilanciare la deriva (come la 97)» contro «rendimento del giorno per unità di nozionale».**
Un conto giornaliero con nozionale 1 ogni giorno equivale a ribilanciare ogni giorno gratis; la deriva vera (nozionale che cresce con il prezzo, funding calcolato sul valore del perpetuo, base cumulata invece di sommata) dà numeri un po' diversi. La 97 era settimanale, qui il periodo di tenuta può durare mesi, quindi la differenza non è la stessa della 97.
Lettura proposta: conto giornaliero per unità di nozionale al giorno (rendimento dello spot meno quello del perpetuo apertura-apertura, più il funding del giorno come è nel pannello), nessuna deriva modellata; si dichiara che è un ribilanciamento giornaliero senza costo e si scrive nel rapporto. Se si preferisce la deriva vera, va scritto prima.

**A2. Cosa decide «passa l'esame».** Le regole citano `terza.esito`, ma questa funzione (a) controlla lo Sharpe corretto a 0,95 e non 0,80, (b) non calcola il t, (c) richiede solo 4 anni positivi, e aggiunge condizioni che le regole non citano (intervallo del netto sopra zero, anno ultimo, costi doppi, due trimestri su quattro per anno, extra su Bitcoin).
Lettura proposta: passa solo se valgono le quattro condizioni scritte nelle regole: netto positivo; ogni anno positivo (anni da `terza.esame`, assegnati dal lunedì della settimana, 2021 e 2026 parziali inclusi); t = Sharpe × radice(settimane/52) almeno 3 (come in `asticella.corretto_famiglie`); Sharpe corretto per famiglie almeno 0,80. Il testo di `terza.esito` e le altre condizioni si riportano solo come descrizione, senza peso sul verdetto.

**A3. Dove si paga l'uscita finale del 4 ottobre 2026.** «Si conta anche l'uscita finale» non dice in quale giorno/settimana.
Lettura proposta: costo di uscita sul giorno 4 ottobre (l'ultimo giorno, settimana 28 settembre - 4 ottobre), per le posizioni aperte in quel giorno; i rendimenti del 4 ottobre usano l'apertura del 5 ottobre come uscita.

**A4. Quale nozionale per i costi con una moneta sola dentro.** Le regole dicono 50% e 50% e capitale pieno 1,5 × nozionale totale. Lettura proposta: rendimento del giorno per capitale = (0,5 × rendimento di BTC dentro + 0,5 × rendimento di ETH dentro) / 1,5, costi della moneta pesati allo stesso modo (0,5 per moneta); per nozionale: divisione per 1 invece di 1,5. «Guadagno in USDT l'anno» su 1.000 USDT di capitale = rendimento annuo per capitale × 1.000, con anno = 365 giorni sulla media giornaliera (o 52 settimane sulla settimanale: sceglierò la media settimanale × 52, come la 97).

## Ambiguità che non cambiano i numeri principali (solo descrittive)
* **B1. Giorni positivi / a zero / negativi:** il giorno dell'uscita costa (netto un po' negativo) pur essendo fuori. Lettura: «fuori» = nessuna moneta dentro durante il giorno (anche se il netto è un po' negativo per il costo); si riportano separati: fuori, dentro positivi, dentro negativi.
* **B2. Rendimento per anno nei controlli descrittivi:** per anno di calendario sommando i giorni (la scomposizione funding/base/spese), mentre l'esame usa l'anno del lunedì (come `terza.esame`). Si scrivono tutti e due, il verdetto usa solo il secondo.
* **B3. Salita massima del prezzo in posizione aperta:** massimo, su ogni periodo continuo dentro e per moneta, di (apertura pronti del giorno / apertura pronti di entrata) − 1, dall'ingresso all'uscita.
* **B4. Controllo con ordini limite:** perpetuo a 0,02% (senza scarto) e pronti 0,10% + 0,01% di scarto; si intende per lato, uno scarto di 0,01% anche sul perpetuo? Lettura: perpetuo 0,02% + 0,01% di scarto (`costi_moneta` con la commissione limite), pronti 0,11%; se si intende senza scarto sul perpetuo, serve dirlo.
* **B5. Correlazioni:** su giorni comuni (G1 `netto` giornaliero), settimane comuni (G1, 97 CC `netto` per capitale, BTC come rendimento della settimana di `programma7`/`pannello_settimane` lunedì-lunedì), Pearson.
* **B6. «Sempre dentro»:** stesso conto con segnale sempre 1 dal 4 gennaio 2021, entrata una volta, uscita finale come A3.
* **B7. Gruppo di famiglia:** serie `CB30` e `CB90` aggiunte come serie nuove al mazzo, due alla volta (non una per volta): lettura: un solo calcolo con tutte e due le serie nuove nel mazzo, una `candidate` per ognuna.

## Esito
Ci sono quattro ambiguità che possono cambiare i numeri (A1 soprattutto, poi A2, A3, A4). Non calcolo. Dati e pronti pronti. Per chiudere servono le risposte della sessione principale alle letture proposte sopra.
