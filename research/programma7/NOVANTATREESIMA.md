# Prova 155 — G1 con l'esposizione secondo l'indice di paura delle opzioni (DVOL), idea 141

Regole scritte il 13 novembre 2026 (giro delle 12:17) dallo strategy-scout, **prima di ogni calcolo**: nessun risultato guardato (solo un
controllo che i dati esistano). La prova la esegue strategy-researcher, il giudizio lo dà backtest-auditor. Il numero 155 è libero (ultima
nel registro: 154). Non spegne e non sostituisce niente: G1 resta com'è, la variante entra accanto.

## Il perché forte
* **Dato mai usato così.** L'indice di volatilità di Deribit (DVOL: la volatilità che le opzioni a 30 giorni sul Bitcoin si aspettano) è
  stato usato solo come segnale di direzione sul Bitcoin e sull'Ether (prova 47, a settimana; prova 121, inclinazione, no). **Mai come
  freno di rischio di G1** (`--cerca dvol`, `--cerca agitazione`, `--cerca esposizione`: la sola prova di esposizione variabile è la 42, F6,
  su F5 e con la volatilità già avvenuta, non quella attesa; no, corretto 0,31). Il DVOL guarda avanti, la volatilità realizzata guarda indietro.
* **Ragione economica.** G1 è long e short fra monete decise dal funding: chi paga per posizioni affollate. Le posizioni affollate si
  sciolgono tutte insieme nelle giornate di panico (Brunnermeier e Pedersen, «Market liquidity and funding liquidity», *Review of
  Financial Studies* 2009: nei momenti di stress il capitale scarseggia e le posizioni affollate si chiudono a cascata) e il mercato
  delle opzioni, dove si compra protezione, vede la tensione prima del prezzo. Fonte per il metodo: Moreira e Muir, «Volatility-managed
  portfolios», *Journal of Finance* 2017 (qui con la volatilità attesa invece di quella passata).
* **Avviso onesto.** La volatilità passata applicata a F5 (prova 42) ha tolto anche le settimane migliori e non ha migliorato lo Sharpe:
  la probabilità che qui funzioni è medio-bassa. Si prova perché il segnale è un'altra informazione e perché G1 è la strategia sul demo:
  un freno che riduce la discesa massima senza costare Sharpe sarebbe utile al capitale piccolo.

## Dati e periodo
* DVOL del Bitcoin, gratuito: `https://www.deribit.com/api/v2/public/get_volatility_index_data?currency=BTC&resolution=1D` con
  `start_timestamp` e `end_timestamp` in millisecondi, a pezzi di un anno (cinque righe: tempo, apertura, massimo, minimo, chiusura).
  **Verificato il 13 novembre 2026**: la serie giornaliera parte il 23 marzo 2021 (284 giorni nel 2021, 366 nel 2022 e nel 2023). Prima
  del 23 marzo 2021 non esiste: il giudizio è su **dal 23 marzo 2021 al 4 ottobre 2026** (`an.FINE`), non dal 4 gennaio 2021.
* Rendimenti giornalieri di G1 con funding vero: quelli della prova 120 (`programma7/PRIMA.md`, `research/programma7/risultati_prima`),
  stessi costi e stessa esecuzione, **senza rifare le scelte delle monete**: si cambia solo il peso del giorno.

## Il segnale (fissato qui)
Ogni giorno D alle 00:00 UTC si usa la chiusura del DVOL del giorno D−1 (nota a fine giornata). Si calcola il suo rango percentile
sulle 180 chiusure precedenti (D−180 … D−1; servono 180 giorni: il primo giorno giudicato è quindi il 19 settembre 2021 circa, e **il
confronto fra G1 e la variante si fa solo da quel giorno**). Se il rango è **sopra l'80%**, quel giorno l'esposizione di G1 si riduce;
altrimenti resta piena. Il ribasso dell'esposizione costa le commissioni del riequilibrio (0,05% a mercato sul valore tolto o rimesso;
ordine limite 0,02% dove G1 già lo usa), scarto 0,01% su BTC, ETH e SOL e 0,02% sulle altre, funding vero sulla parte tenuta.

## Varianti (fissate, al massimo 2)
A: sopra l'80% l'esposizione scende a metà (da 2 a 1). B: sopra l'80% si sta fermi (esposizione 0, posizioni chiuse e riaperte quando
il rango torna sotto l'80%). Nessuna soglia diversa, nessuna variante dopo i risultati. Conta **2 prove** (famiglia di G1 se la
correlazione dei rendimenti giornalieri supera il `TAGLIO` di `programma6/asticella.py`, probabile: allora la famiglia è la stessa e
il conto non sale molto; si segna). **Controlli descrittivi, non varianti**: quota di giorni sopra l'80%; rendimento di G1 nei giorni
sopra e sotto la soglia (se G1 va uguale o meglio nei giorni agitati il freno non ha ragione d'essere); rendimento per anno; discesa
massima di G1 e delle varianti sullo stesso periodo; il segnale con un giorno di ritardo in più, per vedere se c'è guardare avanti.

## L'esame (regole approvate dal proprietario il 9 novembre)
Passa se: netto dopo i costi positivo; **ogni anno positivo** (2021 e 2026 anni parziali: si segnano); t almeno 3; Sharpe corretto almeno
0,80 con il conto per famiglie (`corretto_famiglie` in `programma6/asticella.py`, esempio `audits/repro/prova28_2026-11-11.py` voce 11);
**in più, per essere utile**: lo Sharpe della variante deve stare sopra quello di G1 sullo stesso periodo, con la differenza di serie
giornaliere (variante meno G1) positiva e t almeno 2. Un freno che solo riduce la discesa e perde Sharpe è **non promosso**, ma si
scrive il numero (può servire per il capitale piccolo).

## Cosa si consegna
Rapporto su file in `research/programma7/RISULTATI_NOVANTATREESIMA.md`, serie giornaliere in `risultati_novantatreesima/`, script
`novantatreesima.py`, la serie del DVOL salvata (non committare `research/data/`), a schermo al massimo 20 righe.

## Testo della riga del registro
| 155 | G1 con il freno dell'indice di paura delle opzioni (DVOL di Deribit, rango sulle 180 chiusure precedenti sopra l'80%: esposizione a metà (A) o ferma (B)), dal 23 marzo 2021, dati mai usati come freno di G1 (`programma7/NOVANTATREESIMA.md`); idea 141 (Moreira e Muir JF 2017, Brunnermeier e Pedersen RFS 2009) | 2 | da fare | da fare |

## Regole corrette il 13 novembre 2026 dopo la verifica, prima di ogni calcolo (sessione principale)
La verifica di strategy-researcher (`VERIFICA_NOVANTATREESIMA.md`, punti A1-A13) ha trovato ambiguità; nessun segnale e nessun risultato
è stato calcolato. Le letture che valgono:
1. **Dati del DVOL**: si scaricano con il caricatore esistente `research/programma6/scarico_dvol.py` (in `research/data/dvol/`, fuori da
   git; impronta nel suo `scarico_dvol.json`). La riga giornaliera ha il tempo dell'apertura alle 00:00 UTC: la chiusura del giorno D−1 è
   la riga con il tempo di D−1 ed è nota alle 00:00 UTC di D. La serie comincia **il 24 marzo 2021** (283 giorni nel 2021), non il 23:
   vale il dato com'è.
2. **Il rango**: la chiusura di D−1 si confronta con le 180 chiusure prima di lei (D−181 … D−2): rango = (quante sono minori + metà di
   quelle uguali) / numero di chiusure presenti. «Sopra l'80%» vuol dire rango strettamente maggiore di 0,80. Se fra le 180 ne mancano
   più di 10 (meno di 170 presenti), quel giorno l'esposizione resta piena.
3. **I pesi**: si rifà G1 con `programma7/prima.py` (funzione `esegui`), stesse scelte delle monete di G1 pieno; la variante usa
   `m × W` con m = 1, 0,5 o 0 e i conti di `te.conto` e `cs.spese_a_limite` (`programma6/cinquantaseiesima.py`). **Controllo di parità
   obbligatorio prima di tutto**: con m = 1 i giorni devono coincidere con `risultati_prima/giorni_G1.csv.gz`; se non coincidono ci si
   ferma e lo si scrive.
4. **Variante B**: chiusura e riapertura alle 00:00 UTC con l'esecuzione di G1 (limite per un'ora, poi a mercato); alla riapertura i pesi
   sono quelli di G1 di quel giorno; da fermi il funding è zero.
5. **Periodo**: dal primo giorno con il rango calcolabile (circa il 21 settembre 2021) al 4 ottobre 2026 compreso (`FINE` di `prima.py`,
   il 5 ottobre escluso). Tutti gli indici dell'esame, per G1 e per le varianti, sullo stesso periodo. Il 2021 (dal 21 settembre) e il
   2026 (fino al 4 ottobre) sono anni parziali e **contano tutti e due** per «ogni anno positivo».
6. **Sharpe corretto**: `corretto_famiglie` di `programma6/asticella.py` con il mazzo completo (`mazzo()`), taglio 0,5; le due varianti
   entrano come serie nuove a settimane intere dal lunedì 27 settembre 2021. Il conto del registro passa da 316 a 318 (non entra nella
   formula, che conta le famiglie).
7. **La differenza con G1**: t semplice sulle differenze giornaliere (media / (deviazione / √n)), che deve essere almeno 2 con media
   positiva; come controlli descrittivi anche il t settimanale e quello robusto (Newey-West, 7 ritardi). Il controllo con un giorno di
   ritardo in più usa la chiusura di D−2; è solo descrittivo, senza soglia: i numeri si scrivono e li giudica backtest-auditor.
8. **Registri**: le varianti vanno in `research/trials/novantatreesima.csv`; rapporto `RISULTATI_NOVANTATREESIMA.md`, serie in
   `risultati_novantatreesima/`, script `novantatreesima.py`.

## Aggiunta del 13 novembre 2026 dopo il controllo di parità (sessione principale; nessuna variante calcolata)
Il controllo di parità (`risultati_novantatreesima/parita.json`) ha dato 2.100 giorni uguali ma differenze negli ultimi giorni: il lordo
dal 2 ottobre 2026, il funding dal 30 settembre, il giro dal 1° ottobre; fino al 29 settembre lordo, funding, giro e numero di monete
coincidono. Il riferimento `giorni_G1.csv.gz` è stato calcolato all'inizio di ottobre, quando la coda del pannello aveva il funding
riempito e un giorno pubblicato a metà; il pannello di oggi ha i dati veri (commit e4cb480 del 10 novembre e il file del funding di
ottobre). Lettura che vale:
1. La parità è **valida se tutte le colonne (lordo, spese, funding, netto, giro, numero di monete) coincidono entro 1e-12 fino al 29
   settembre 2026 compreso**. Se una colonna, spese comprese, differisce prima del 30 settembre, ci si ferma e lo si scrive.
2. Se la parità è valida, **G1 di confronto è quello ricalcolato oggi con m = 1** sullo stesso pannello delle varianti, per tutto il
   periodo fino al 4 ottobre 2026: G1 e varianti usano gli stessi dati. Le differenze degli ultimi 5 giorni con il riferimento si
   scrivono nel rapporto.
3. **Primo giorno giudicato**: il primo con 180 chiusure intere prima di D−1 (circa il 21 settembre 2021). La regola dei 170 presenti
   vale per i giorni mancanti dentro la finestra, non per una finestra tagliata all'inizio della serie.
