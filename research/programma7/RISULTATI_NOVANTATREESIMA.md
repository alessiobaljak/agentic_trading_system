# Risultati della prova 155 (G1 con il freno dell'indice di paura delle opzioni): FERMATA al controllo di parità

Eseguita il 13 novembre 2026. **Le varianti A e B non sono state calcolate**, come da ordine («se non coincide, fermati»).

### Riepilogo
* Il DVOL è stato scaricato (`scarico_dvol`: BTC 2.061 giorni, dal 24 marzo 2021 al 13 novembre 2026; impronta in `research/programma6/scarico_dvol.json`).
* **La parità di G1 con m = 1 NON coincide** con `risultati_prima/giorni_G1.csv.gz`: stessi 2.100 giorni (4 gennaio 2021 – 4 ottobre 2026), ma
  differenza massima sul netto 0,0116 (1,16 punti in un giorno), sul lordo 0,0127, sulle spese 0,0053.
* Esito secondo l'esame scritto: **non eseguibile, nessun esito** (né passa né non passa): nessuna variante calcolata.

### La prova come è scritta e scala di tempo
Regole `programma7/NOVANTATREESIMA.md` (8010fc8) con la sezione «Regole corrette il 13 novembre» (946cf8a), punto 3: «con m = 1 i giorni devono
coincidere con `risultati_prima/giorni_G1.csv.gz`; se non coincidono ci si ferma e lo si scrive». Scala di tempo: giornaliera (settimane per lo Sharpe).

### Implementazione
`research/programma7/novantatreesima.py` (G1 rifatta come `prima.esegui`: `sc.pannello`, `vq.pesi_banda`, `te.conto`, `cs.spese_a_limite`; poi il segnale
e le varianti, mai raggiunti). Commit al momento della prova: HEAD senza modifiche mie (nessun commit fatto). Parità salvata in
`risultati_novantatreesima/parita.json`.

### Varianti provate
0 varianti. Registro `research/trials/novantatreesima.csv`: una sola riga, «G1_parita» (controllo, esito «parita NON ok»).

### Risultati della parità
* Righe: 2.100 contro 2.100; giorni uguali; soglia usata 1e-12.
* Dove differisce (diagnosi con la stessa G1, nessuna variante): **solo gli ultimi giorni**. Lordo diverso in 3 giorni (2, 3 e 4 ottobre 2026), funding diverso in
  5 giorni (dal 30 settembre), giro diverso in 4 giorni (dal 1 ottobre), numero di monete diverso in 3 giorni. Tutti i giorni prima del 30 settembre 2026 coincidono (differenza sotto 1e-12 su lordo, funding, giro, monete).
* Lettura (non verificata): il commit e4cb480 del 10 novembre («il pannello del programma 6 non usa più un ultimo giorno pubblicato a metà») ha cambiato
  il pannello dopo il calcolo della prova 120; la coda del pannello (ultimi giorni di settembre e primi di ottobre 2026) oggi è diversa da allora.
  Non l'ho corretto né aggirato.

### Variante migliore e sensibilità
Non applicabile.

### Anomalie e possibili errori di motore o dati
* Il pannello attuale non riproduce gli ultimi 3-5 giorni (30 settembre – 4 ottobre 2026) di `giorni_G1.csv.gz`. Probabile causa: modifica del pannello del 10 novembre (e4cb480) o riempimento del funding. Da decidere alla sessione principale: rifare `giorni_G1.csv.gz` con il pannello d'oggi, o ammettere una tolleranza scritta (le regole non ne hanno), o chiudere il periodo prima del 30 settembre.
* Parità con il resto del periodo: esatta.

### Varianti non previste che proporrei (non eseguite)
Nessuna.

### Domande aperte
1. Come si chiude la parità: rigenerare il file di riferimento con il pannello d'oggi (cambia la prova 120 in coda), oppure fissare per iscritto che il confronto vale fino al 29 settembre 2026, oppure una tolleranza? Senza una decisione scritta non calcolo A e B.
2. Primo giorno giudicato: con la regola dei 170 presenti il rango sarebbe calcolabile già dall'11 settembre 2021 se si accettano finestre troncate dall'inizio della serie; la lettura del punto 5 («circa il 21 settembre») richiede 180 giorni pieni. Io avrei usato il 21 settembre 2021 (D−181 ≥ 24 marzo); da confermare.

## Secondo controllo di parità (regola 8f87e9d, 13 novembre): ANCORA NON VALIDO, fermata
Letta la regola: parità valida se tutte le colonne (lordo, spese, funding, netto, giro, monete) coincidono entro 1e-12 fino al 29 settembre 2026. Primo giorno giudicato 21 settembre 2021 (finestra intera, già nel codice).
* Fino al 29 settembre: lordo (1e-16), funding (1e-16), giro (4e-16) e numero di monete coincidono. **Le spese NO**: differenza massima 0,0053 (il 4 gennaio 2021: 0,00588 oggi contro 0,00060 nel riferimento) e il netto di conseguenza.
* Le spese differiscono in 956 giorni su 2.100 (619 dal 2022 in poi); coincidono in 1.144. Somma delle spese: oggi 0,3665, riferimento 0,3774 (il riferimento è più alto del 3%); a mercato sarebbero 0,5495 (il riferimento non è a mercato: è quello con il limite).
* Ultimi 5 giorni (30 settembre – 4 ottobre): come già scritto (funding dal 30/9, lordo e giro dal 1-2/10, monete 2-4 in meno/più il 2, 3 e 4 ottobre); dettaglio in `risultati_novantatreesima/parita.json`.
* Il codice delle spese (`cinquantaseiesima.py`, `esecuzione.py`) non è cambiato dopo il riferimento (ultima modifica 30 ottobre, il riferimento è dello stesso commit): la causa probabile è nei dati delle candele a 1 ora (che decidono se il limite viene preso). Non verificato, non toccato.
* Per la regola scritta mi fermo: A e B non calcolate. Registro: riga `G1_parita_2` aggiunta (esito «parita NON ok»); la riga `G1_parita` precedente resta.
* Domanda aperta: la regola dell'8f87e9d dà per scontato che le spese coincidano fino al 29 settembre; non è così. Va deciso se rigenerare il riferimento con le candele d'oggi (G1 di confronto = quello di oggi, come già deciso) o altro; serve una regola scritta sulle spese.
