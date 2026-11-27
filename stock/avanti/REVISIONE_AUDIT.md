# Revisione separata delle correzioni del programma del demo (27 novembre 2026)

Le correzioni A1-A19 dell'audit (`stock/AUDIT_2026-11-27.md`, sezione 3), con l'ok del proprietario del 27 novembre («sì, fai le 19
correzioni e abbassa a 0,80»). Toccano gli ordini del conto demo di Alpaca: prima del commit le ha guardate un revisore separato
(regola del demo: chi scrive il codice non lo approva). Le regole delle tre strategie non cambiano; cambia come il programma reagisce
ai guasti (note del 27 novembre in `REGOLE.md`, `MISCELA.md`, `GAMMA.md`).

## Primo giro: tre revisori, tre «da cambiare»

Tre revisori separati, ognuno con un solo sguardo (gli ordini, i conti, i lavori di GitHub con lo script del server e i test). Tutti e
tre hanno eseguito scenari veri sul codice (copie in una cartella di prova, conto finto), non solo letto. Verdetto di tutti e tre:
**da cambiare**. I problemi più gravi e cosa si è fatto:

| Problema trovato | Gravità | Cosa si è fatto |
|---|---|---|
| Il lavoro della miscela legge i file del suo checkout, vecchi di qualche minuto: dopo la chiusura di una posizione rimasta la vendita diventava guadagno della prima candela (o della prova 45) e la miscela vendeva quasi tutto | bloccante | Il giorno dell'ingresso e le uscite delle posizioni rimaste si leggono dai **nomi degli ordini su Alpaca** (`candela-rim-<giorno>-<titolo>-<ora>`, `gamma-rim-<giorno>-<ora>`), non dai file. Il capitale di oggi conta flusso e valore di mercato solo per i titoli entrati oggi; le altre posizioni con il non realizzato; gli ordini «rim» fuori (`conto.classifica`) |
| Un'uscita non attribuita (ordine «da verificare», chiusura a mano) diventava guadagno di oggi | bloccante | Come sopra: un titolo non entrato oggi non porta più flusso nel capitale di oggi. Le chiusure a mano dal sito di Alpaca restano non attribuibili: scritto nelle regole di usare il comando «chiudi» |
| La regola della banca centrale saltava l'acquisto della vigilia per un falso «posizioni rimaste» (stesso motivo: file vecchi) | alto | Tolto il fermo della sera e della banca centrale per le posizioni rimaste: con il conto per nome non serve più |
| Una riga «aperta» o «parziale» di un giorno prima fermava la prima candela per sempre, senza allarme sulla Plancia | alto | A ogni avvio le righe aperte degli ultimi 15 giorni si ricalcolano con le uscite arrivate dopo (`completa_righe`, anche per la prova 45); il fermo resta solo finché la riga non si chiude, con l'allarme sulla Plancia e il lavoro rosso |
| Prova 45: due casi in cui la riga restava senza guadagno o con metà | alto | `completa_righe` della prova 45 (uscita del giorno dopo, ordini «rim» per nome) |
| Un guasto passeggero mentre si calcola l'elenco del mese scriveva un elenco sbagliato per tutto il mese | alto | Un gruppo che fallisce si riprova un titolo alla volta; con un guasto passeggero o meno del 98% dei membri con le barre l'elenco **non si scrive** e il lavoro esce rosso |
| L'allarme della prova 45 «VOO ancora aperta» si cancellava da solo; l'allarme del fermo non arrivava sulla Plancia | medio | Allarme prima del diario e ripubblicato dopo; chiave `contabilita_candela` sulla Plancia |
| Miscela: se la ricerca per nome falliva il secondo fondo non si provava; un ordine trovato per nome ma morto contava come mandato | medio, basso | «DA VERIFICARE» e si passa al fondo dopo; un ordine trovato ma rifiutato o cancellato conta come non mandato |
| I valori di fine giornata: un solo scrittore, solo «oggi»; la barra giornaliera alle 16:20 può contenere il dopo borsa | medio, basso | La riga si scrive anche la mattina dopo, prima dell'apertura (`ultima_seduta_da_registrare`); le posizioni della miscela al prezzo dell'ultimo minuto della seduta |
| Il limite delle 20:00 non valeva nei giorni a chiusura anticipata | basso | Fine degli ordini fuori orario alla chiusura + 4 ore (al massimo le 20:00) |
| Il token del server si vedeva negli argomenti di curl; dipendenze non fisse; una cella vuota diventava il simbolo «NAN»; azioni di GitHub vecchie | basso | Token letto da stdin; librerie fisse in `stock/requirements.txt` e `stock/requirements-test.txt`; `keep_default_na=False`; azioni aggiornate |
| I test provavano le funzioni pure, quasi mai il collegamento (20 rotture su 39 passavano inosservate) | medio | Aggiunti test di collegamento con un conto finto (chiusura della rimasta con il nome, fermo con l'allarme, elenco con il guasto, ricerca per nome fallita, allarme della prova 45 dopo il diario); i test girano a ogni push (`azioni_test.yml`) |

Limiti che restano, scritti e accettati:

* il server di riserva non pubblica allarmi sulla Plancia (non ha le chiavi: avvia solo i lavori di GitHub);
* i test non fermano gli ordini, apposta: un test rosso non deve mai impedire la chiusura delle 15:55;
* una chiusura a mano dal sito di Alpaca non si attribuisce a nessun giorno;
* le tasse sulle vendite stimate: alla prima esecuzione le operazioni dal 12 novembre perdono le tasse tutte insieme (19,76 dollari
  tolti alla prima candela e dati alla miscela nella riga di quel giorno di `valori.csv`); su una riga «parziale» la tassa si calcola
  sulla quantità intera finché la riga non si completa; Alpaca può addebitarle il giorno dopo. Pochi dollari: solo da sapere;
* i membri dell'S&P 500 si aggiornano dalla routine di ricerca della sessione (dal 25 del mese), non da un lavoro di GitHub.

## Secondo giro: il codice ridisegnato

Il cambio dai file ai nomi degli ordini è grande: due revisori separati (gli ordini, i conti) hanno guardato il codice ridisegnato
prima del commit, con un conto di Alpaca finto (nomi unici con il rifiuto dei doppioni, gambe, esecuzioni, orologio, errori di rete e
503 a comando) e 25 scenari eseguiti. Verdetto di tutti e due: **approvato**, nessun problema bloccante né alto; i bloccanti e gli alti
del primo giro sono risolti. La prova 45 di oggi ha fatto sul conto finto il giro intero (ingresso alle 12:30, asta, riga del diario,
secondo avvio che non fa niente, SPY e QQQ non toccati).

Restano otto problemi medi, tutti rari; si correggono subito dopo questo commit, prima di lunedì 30 novembre (primo giorno normale
della prima candela con il codice nuovo), con un nuovo controllo separato:

* ordini: gli ingressi possono partire dopo le 10:00 se Alpaca non risponde (l'ora non si ricontrolla prima di ogni invio); il comando
  a mano «chiudi_fuori_orario» su una posizione di un altro giorno usa il nome sbagliato e ferma la candela; un solo errore 503 alle
  15:55 lascia le posizioni aperte (si ritenta solo il 429; c'era già); se Alpaca data le esecuzioni in UTC, un'uscita fuori orario
  fra le 19:00 e le 20:00 d'inverno non entra nella riga (da verificare);
* conti: con i file vecchi il guadagno di una posizione rimasta chiusa oggi resta nella miscela per qualche ora (qualche centinaio di
  dollari, al più qualche migliaio); prova 45: un'uscita fuori orario eseguita dopo i 60 secondi lascia la riga «aperta» e la riga di
  `valori.csv` del giorno sbagliata per sempre; prova 45: una VOO chiusa a mano dal sito e un ingresso nuovo lo stesso giorno
  rovinano il diario; la riga di `valori.csv` scritta la mattina dopo con i file di prima del salvataggio della prova 45 è sbagliata
  per sempre.

Rapporti completi della revisione: nella cartella di lavoro della sessione (non nel repository); qui il riassunto.

## Terzo giro: gli otto problemi medi

Corretti tutti e otto, più sei bassi (il 429 ritentato per circa un minuto; una rimasta con la risposta persa cercata per nome; il
limite fuori orario a ridosso della chiusura; un giorno senza righe nel diario che ferma gli ordini e si riscrive; la riga di ieri
registrata prima dell'attesa delle 9:45; la fotografia del conto che si rilegge se le posizioni cambiano). Il comando «chiudi» c'è
ora anche per la prova 45. Tre revisori separati (gli ordini, i conti, le regressioni) con verifica avversariale di ogni problema:
ordini e conti **approvati**, con cinque problemi medi nuovi nelle correzioni stesse, due confermati da due scettici ciascuno:

* con le esecuzioni datate in UTC, la vendita fuori orario delle 19:30 di ieri contava nel flusso di oggi (fino a 9'700 dollari di
  errore della miscela) e due volte nel diario: ora il flusso di oggi conta solo le esecuzioni di ordini mandati oggi, e il diario
  toglie gli ordini fuori orario di un altro giorno;
* prova 45: la riga segnaposto di un giorno con l'ingresso eseguito non si rifaceva più: ora si rifà;
* la riga di `valori.csv` della mattina dopo si poteva scrivere prima che il diario avesse le righe del giorno: ora aspetta;
* alle 15:55 un errore 503 più lungo dei tentativi lasciava le posizioni aperte (c'era già prima).

Il revisore delle regressioni e quattro verifiche si erano fermati per il limite d'uso: rifatti dopo le correzioni da tre revisori
separati. Esito: regressioni **approvate** (nessun comportamento approvato peggiorato; il giro di oggi della prova 45 e il lunedì
della prima candela giusti sul conto finto), conti **approvati** (le tre correzioni dei conti verificate con gli scenari), ordini
**da cambiare** solo per la chiusura delle 15:55: il nuovo giro di tentativi poteva mandare chiusure a mercato dopo le 16:00. Quella
parte **è stata tolta** e la chiusura delle 15:55 è quella approvata al secondo giro (un 503 breve ora si ritenta dentro
`_richiesta`; un guasto più lungo lascia le posizioni alla chiusura fuori orario del giro dopo, come prima). La correzione esce dal
commit e si rifà fuori dalle ore di borsa, con il suo controllo: controllare l'ora prima di ogni chiusura a mercato e, passate le
15:59:15, chiudere fuori orario nello stesso giro.

Restano da fare, scritti in `STATO.md`: quel giro di tentativi; un avvio della prova 45 prima dell'apertura anche d'estate (se il
diario della sera fallisce, d'estate il primo avvio del mattino arriva dopo le 9:30 e la riga di `valori.csv` di quel giorno non si
scrive più); il «giorno prima» del controllo di `registra` che non conosce le feste; qualche test in più sulle scadenze e sulle
esclusioni per nome (le correzioni ci sono e gli scenari dei revisori le provano, ma togliendone una sola nessun test del repository
se ne accorge). Il calo di 19,76 dollari della prima candela nella riga del 27 novembre di `valori.csv` sono le tasse sulle vendite
stimate dal 12 al 25 novembre, tolte tutte insieme alla prima esecuzione: non è una perdita del giorno.
