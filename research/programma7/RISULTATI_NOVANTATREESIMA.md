# Risultati della prova 155 (G1 con il freno dell'indice di paura delle opzioni, DVOL)

Eseguita il 13 novembre 2026 con le regole 8010fc8, 946cf8a, 8f87e9d e 1255f47 (tutte committate prima delle varianti). Nessun commit fatto da me.

### Riepilogo
* Parità valida (lordo, funding, giro e monete uguali entro 1e-12 fino al 29 settembre 2026; spese diverse per la causa verificata in 1255f47).
* Periodo giudicato: 21 settembre 2021 – 4 ottobre 2026, 1.840 giorni (262 settimane intere dal 27 settembre 2021). Giorni sopra l'80%: 332 (18,0%). Nessun giorno senza rango dopo il primo.
* Esito secondo l'esame scritto: **A non passa, B non passa.** Criteri che mancano: A: Sharpe corretto per famiglie 0,51 (serve 0,80), differenza con G1 negativa (t semplice −0,79, serve ≥ 2 con media positiva). B: gli stessi due, più lo Sharpe non sopra G1 (1,73 contro 1,70 giornaliero, ma 1,67 contro 1,68 sulle settimane, che è la misura dell'esame). Netto positivo, ogni anno positivo e t ≥ 3 sono rispettati da entrambe.
* Il freno riduce la discesa massima (da −30,1% a −21,6% sulla curva dei giorni; sulle settimane da −28,8% a −17,9%) e costa rendimento (−2,0 e −4,1 punti l'anno). «Non promosso» ma il numero può servire per il capitale piccolo.

### La prova come è scritta
Citata in `programma7/NOVANTATREESIMA.md` (testo, «Regole corrette» punti 1-8, due aggiunte del 13 novembre). Scala di tempo: giornaliera; Sharpe di esame dalle settimane (somma di 7 giorni, per 52); Sharpe giornaliero su 365 giorni come controllo. Segnale: chiusura DVOL di D−1 contro le 180 chiusure D−181..D−2, rango (minori + metà uguali)/presenti, sopra 0,80 stretto. A: m = 0,5; B: m = 0.

### Implementazione
`research/programma7/novantatreesima.py` (G1 rifatta come `prima.esegui`, pesi W di G1 pieno per m, `te.conto`, `cs.spese_a_limite`); serie in `risultati_novantatreesima/` (giorni_*.csv.gz, settimane_*.csv.gz, segnale.csv.gz, esame.json, parita.json). Seme 155 (nessun caso). DVOL: `research/data/dvol/BTC.json` (scaricato con `scarico_dvol`, 2.061 giorni dal 24 marzo 2021).

### Varianti provate
2 (A, B) più 2 controlli descrittivi con un giorno di ritardo (A_ritardo, B_ritardo). Registro `research/trials/novantatreesima.csv`: righe G1_parita e G1_parita_2 (prime due, non ok, storia), G1_parita_3 (ok), A, B, A_ritardo, B_ritardo.

### Risultati (stesso periodo, 1.840 giorni; rendimento netto = media giornaliera × 365; Sharpe giornaliero × √365; t = Sharpe settimanale × √(262/52); spese l'anno)
| | netto l'anno | Sharpe 365 | t sett. | discesa (giorni / settimane) | spese l'anno |
|---|---|---|---|---|---|
| G1 di oggi | +40,4% | 1,70 | 3,77 | −30,1% / −28,8% | 6,4% |
| G1 del riferimento (stessa finestra) | +40,0% | 1,68 | 3,78 (giorni) | −30,1% / −28,8% | 6,6% |
| A (metà) | +38,4% | 1,77 | 3,85 | −21,6% / −17,9% | 6,4% |
| B (fermo) | +36,3% | 1,73 | 3,75 | −21,6% / −17,9% | 6,6% |

Per anno (media × 365; 2021 dal 21 settembre, 2026 fino al 4 ottobre; tutti contano):
* G1 oggi: 2021 +0,7%, 2022 +31,4%, 2023 +8,2%, 2024 +69,3%, 2025 +67,6%, 2026 +35,3%.
* G1 riferimento: +0,2, +30,8, +7,7, +69,3, +67,6, +34,4.
* A: +0,7, +29,7, +10,9, +67,3, +60,3, +33,3.
* B: +0,7, +27,9, +13,4, +65,0, +52,8, +31,1.
Tutti gli anni sono positivi per tutte le serie; il 2021 è appena sopra zero (+0,7%) anche per G1.

Sharpe corretto per famiglie (`corretto_famiglie`, mazzo completo: 267 serie con serie, 46 senza, **191 famiglie**, taglio 0,5; A e B entrano come serie nuove dal 27 settembre 2021): G1 stessi giorni 0,48; A 0,51; B 0,47. Con taglio 0,3 (141 famiglie): 0,49 / 0,52 / 0,48; con 0,7 (227 famiglie): 0,36 / 0,39 / 0,35. **A e B stanno nella stessa famiglia di G1** (gruppo con 57 G1 e altre 33 serie, per correlazione); G1 «stessi giorni» è un candidato a sé solo come confronto, non è nel mazzo. Correlazione giornaliera con G1: A 0,97, B 0,88. Il conto del registro passa da 316 a 318, non entra nella formula.

Differenza con G1 (variante meno G1, giorni):
| | media annua | t semplice | t settimanale | t robusto (7 ritardi) |
|---|---|---|---|---|
| A | −2,0% | −0,79 | −0,88 | −0,81 |
| B | −4,1% | −0,82 | −0,92 | −0,84 |

Giorni sopra e sotto l'80% (G1 di oggi): sopra 332 giorni, +14,1% l'anno, Sharpe 0,54 (somma +0,129); sotto 1.508 giorni, +46,2% l'anno, Sharpe 1,99 (somma +1,908). G1 va peggio nei giorni agitati (ma resta positivo), come la ragione del freno suggerisce; il guadagno evitato e la perdita sono quasi bilanciati, quindi la differenza netta non è significativa.

Controllo con un giorno di ritardo (chiusura di D−2, solo descrittivo, senza soglia): A_ritardo +37,9% l'anno, Sharpe 1,74 (settimane 1,68), discesa −21,6%; B_ritardo +35,2%, Sharpe 1,67 (settimane 1,59). Le versioni ritardate hanno Sharpe sotto le non ritardate (A 1,77, B 1,73): nessun segno di guardare avanti. Differenza con G1: t −1,02 e −1,05.

### Variante migliore e sensibilità
Per l'esame la migliore è A, ma non passa. Le vicine (B più dura, A ritardata, taglio di famiglie) sono tutte sotto G1 come rendimento; A sopra G1 solo per lo Sharpe (1,77 contro 1,70 giornaliero; 1,715 contro 1,681 sulle settimane) e per la discesa, mai in modo significativo.

### Anomalie e possibili errori di motore o dati
* Parità: spese diverse in 953 giorni fino al 29 settembre (somma 0,3665 oggi, 0,3774 riferimento), causa verificata dalla sessione principale (candele a 1 ora mancanti nel riferimento: 6.105 variazioni a mercato contro 137). Ultimi 5 giorni del riferimento diversi per il funding, il lordo, il giro e le monete (`parita.json`). G1 di oggi e di riferimento differiscono in questa finestra di meno di mezzo punto di rendimento annuo.
* Nessun giorno con DVOL mancante dopo il primo giorno giudicato.
* Nessun'altra anomalia: il periodo finisce il 4 ottobre, prima del funding riempito di coda dell'archivio, quindi non tocca questa prova.

### Varianti non previste che proporrei (non eseguite)
Nessuna.

### Domande aperte
Nessuna nuova. Letture scelte da me: (1) «anno» = media giornaliera × 365 per anno di calendario, anche per gli anni parziali; (2) discesa dalla curva composta dal netto giornaliero (e dalle settimane con `te.numeri_settimana`); (3) il t dell'esame è lo Sharpe settimanale × √(settimane/52) (A12 della verifica); (4) «Sharpe sopra G1» richiesto sia sulle settimane sia sui giorni; (5) l'esame del riferimento riscritto sulla stessa finestra per il confronto.


---
## Storia: i due controlli di parità fermati prima (superati dalle regole 1255f47)
## Secondo controllo di parità (regola 8f87e9d, 13 novembre): ANCORA NON VALIDO, fermata
Letta la regola: parità valida se tutte le colonne (lordo, spese, funding, netto, giro, monete) coincidono entro 1e-12 fino al 29 settembre 2026. Primo giorno giudicato 21 settembre 2021 (finestra intera, già nel codice).
* Fino al 29 settembre: lordo (1e-16), funding (1e-16), giro (4e-16) e numero di monete coincidono. **Le spese NO**: differenza massima 0,0053 (il 4 gennaio 2021: 0,00588 oggi contro 0,00060 nel riferimento) e il netto di conseguenza.
* Le spese differiscono in 956 giorni su 2.100 (619 dal 2022 in poi); coincidono in 1.144. Somma delle spese: oggi 0,3665, riferimento 0,3774 (il riferimento è più alto del 3%); a mercato sarebbero 0,5495 (il riferimento non è a mercato: è quello con il limite).
* Ultimi 5 giorni (30 settembre – 4 ottobre): come già scritto (funding dal 30/9, lordo e giro dal 1-2/10, monete 2-4 in meno/più il 2, 3 e 4 ottobre); dettaglio in `risultati_novantatreesima/parita.json`.
* Il codice delle spese (`cinquantaseiesima.py`, `esecuzione.py`) non è cambiato dopo il riferimento (ultima modifica 30 ottobre, il riferimento è dello stesso commit): la causa probabile è nei dati delle candele a 1 ora (che decidono se il limite viene preso). Non verificato, non toccato.
* Per la regola scritta mi fermo: A e B non calcolate. Registro: riga `G1_parita_2` aggiunta (esito «parita NON ok»); la riga `G1_parita` precedente resta.
* Domanda aperta: la regola dell'8f87e9d dà per scontato che le spese coincidano fino al 29 settembre; non è così. Va deciso se rigenerare il riferimento con le candele d'oggi (G1 di confronto = quello di oggi, come già deciso) o altro; serve una regola scritta sulle spese.
