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
