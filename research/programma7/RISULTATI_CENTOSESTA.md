# Risultati della prova 168 (G1, G11, G1 neutra e F5 insieme sullo stesso conto)

Eseguita il 22 novembre 2026 da strategy-researcher. Regole: `CENTOSESTA.md` (commit `cbcf8b7`, con la «Chiusura della verifica» che
vale su tutto il resto). Numeri da `risultati_centosesta/esame.json` e `rifatte.json`.

## Riepilogo
* **Esito secondo il criterio scritto: NON PROMETTENTE, per tutte e due le varianti**, per un solo motivo: lo Sharpe corretto con il
  conto per famiglie è **0,73 per A e 0,75 per B**, sotto lo 0,80. Il resto passa: netto positivo, ogni anno positivo (2021-2026), t
  5,08 (A) e 5,13 (B).
* Insieme fanno quasi la stessa cosa di G1 da sola, un po' meglio sul rischio: Sharpe 2,11 (A) e 2,14 (B) contro 1,97 di G1; rendimento
  l'anno quasi uguale (+55,3%, +55,2%, +54,1%); discesa massima 25,7% e 24,9% contro 28,8%. La correlazione settimanale con G1 è 0,97
  (A) e 0,98 (B).
* Varianti provate: 2 (A e B), tutte registrate. In avanti (22 giorni) il conto «un quarto a testa» ha fatto +3,17% contro +2,62% di G1.
* Il giudizio di credibilità non è mio: lo dà backtest-auditor, la decisione è di Alessio.

## La prova come è scritta e scala di tempo
* «A, quattro conti in uno: ogni strategia un quarto del capitale con le sue spese; rendimento della settimana = media dei quattro
  rendimenti netti della stessa settimana.» «B, un portafoglio solo: ogni giorno il peso di ogni moneta = media dei pesi delle quattro
  strategie (F5 tiene i suoi pesi dal lunedì alla domenica); spese solo sulle variazioni del peso netto; funding sul peso netto.»
* Esame: «netto positivo, ogni anno positivo, t almeno 3, Sharpe corretto almeno 0,80 con il conto per famiglie
  (`asticella.corretto_famiglie`, A e B in `nuove`)»; confronto con G1 da sola sulle stesse settimane.
* Scala di tempo: settimanale (somma dei giorni; per A le serie settimanali già salvate). Periodo: dal 4 gennaio 2021 al 4 ottobre 2026,
  300 settimane. Sharpe su 52 settimane. Seme: nessuno (tutto deterministico; scritto 0 nel registro).

## Implementazione
* `research/programma7/centosesta.py` (non committato; contiene anche la funzione `rifatte`, lanciata dopo il calcolo con `--rifatte`,
  senza registrare). Pesi giornalieri con i passi di `VERIFICA_CENTOSESTA.md`, senza toccare motori, caricatori e `asticella.py`.
* A: media di ogni colonna delle quattro serie salvate (G1, G11, G1N; F5 dal file delle parità corrette `risultati_controllo_parita`,
  a spese di mercato), `monete` sommato. B: media dei quattro pesi, `te.conto` per lordo e funding sul peso netto, `cs.spese_a_limite`
  del motore di G1 per le spese; F5 dentro B a pesi costanti ogni giorno, con la banda calcolata dal 2020 e tagliata dal 4 gennaio 2021.
* Commit di partenza `4d3f061` (il codice non era committato al momento del calcolo).
* Esame: `asticella.corretto_famiglie({"168 A", "168 B"}, ...)`; esito calcolato a mano con le condizioni delle regole, non con `te.esito`.

## Varianti provate
2 in tutto: A e B. Registro: `research/trials/centosesta.csv` (2 righe, nessun errore). Nessuna variante non prevista eseguita.

## Risultati (300 settimane, 4 gennaio 2021 - 4 ottobre 2026)
G1, G11, G1N, F5 qui sono le serie salvate (quelle che entrano in A). «Giorno peggiore» solo per G1 e B (punto 6 della chiusura).

| | Rendimento l'anno | Sharpe | Discesa max | Settimana peggiore | Giorno peggiore | Spese l'anno | Ordini |
|---|---|---|---|---|---|---|---|
| A | +55,3% | 2,11 | -25,7% | -10,0% (1 giu 2026) | non calcolabile | 7,04% | 372.802 (somma) |
| B | +55,2% | 2,14 | -24,9% | -9,6% (1 giu 2026) | -8,35% (30 gen 2021) | 6,19% | 145.316 |
| G1 da sola | +54,1% | 1,97 | -28,8% | -9,4% (1 giu 2026) | -8,50% (30 gen 2021) | 6,54% | 117.045 |
| G11 | +60,3% | 2,05 | -28,5% | -8,9% | | 10,25% | 119.957 |
| G1N | +51,3% | 1,91 | -23,1% | -11,1% | | 6,46% | 117.037 |
| F5 (a mercato) | +55,4% | 1,88 | -26,9% | -14,7% (26 feb 2024) | | 4,93% | 18.771 |

* Per anno (2026 parziale, 39 settimane). A: 2021 +127,1%, 2022 +30,8%, 2023 +14,2%, 2024 +62,7%, 2025 +64,6%, 2026 +24,4%. B: +126,6%,
  +30,6%, +14,5%, +63,9%, +64,0%, +23,7%. G1: +109,9%, +31,2%, +7,7%, +68,0%, +72,5%, +28,5%. Tutti positivi.
* Esame: A Sharpe corretto 0,73, t 5,08; B 0,75, t 5,13 (famiglie: 200 su 289 serie e 48 prove senza serie; tutte le prove di G1 e
  simili cadono nello stesso gruppo grande). Ultimo anno: A +41,3%, B +38,9%. Costi doppi: positivi per tutte e due. Per confronto,
  G1 da sola nella sua prova (57) aveva 0,86 con il conto di allora (non confrontabile: conto per gruppi diverso).
* Correlazione settimanale (netto): G1-G11 0,89; G1-G1N 0,91; G1-F5 0,80; G11-G1N 0,84; G11-F5 0,72; G1N-F5 0,69; B-G1 0,98; B-A 1,00.
* Peso lordo di B: medio 1,98, massimo 2,00 (la media dei pesi non è normalizzata; G1N arriva a lordo fino a 3 nella sua scalatura).
* Controlli descrittivi (non nel conto):
  * **F9** (F5 con ordini limite, parità corrette): Sharpe 1,94, +56,9% l'anno, discesa -26,7%, spese 3,48% (F5 a mercato: 4,93%).
  * **B con la sola F5** contro la serie settimanale di F5: Sharpe 1,88 (uguale), +52,0% contro +55,4% l'anno, discesa -23,6%, spese
    4,38% contro 4,93%, ordini 109.751 contro 18.771, correlazione 0,976, scarto medio -0,07 punti a settimana. Cioè la lettura
    «pesi costanti ogni giorno» toglie circa 3,4 punti l'anno a F5 (riequilibrio giornaliero e composizione diversa).
* **In avanti a tavolino** (`risultati_centosesta/avanti.csv`, 21 letture dal 31 ottobre al 22 novembre = 20 intervalli, 22 giorni;
  per ogni giorno la risposta «stato» con ora «eseguito» più vicina alle 04:15 UTC, il 31 ottobre solo quella delle 16:59; il 2-5
  novembre un intervallo di 3 giorni): cumulato G1 +2,62%, G11 +0,88%, G1N +3,11%, F5 +6,06%, **un quarto a testa +3,17%**.
  Intervallo peggiore: G1 -1,98% e un quarto a testa -1,98% (entrambi 21-22 novembre). Discesa sugli intervalli: un quarto a testa
  -3,88%, G1 -4,60%. Sono rendimenti fra due letture, non a mezzanotte, e 22 giorni sono pochissimi: solo descrittivo.

## Variante migliore e sensibilità
Per Sharpe corretto B (0,75) sta sopra A (0,73), ma nessuna delle due supera 0,80: **nessuna variante passa**. Fra le due la differenza è
piccola (Sharpe 2,14 contro 2,11, spese 6,19% contro 7,04%); B costa meno perché le differenze fra le strategie si compensano
(145.316 ordini contro 372.802 sommati, ma ogni ordine di B è più piccolo). Non ci sono altre varianti vicine nelle regole.

## Anomalie e possibili errori
1. **Serie salvate e codice di oggi non coincidono del tutto.** Rifacendo G1, G11 e G1N con il codice di oggi, il netto settimanale
   differisce dalle serie salvate (30 ottobre) in 140 settimane su 300 per le spese (di norma meno di un decimo di punto), e di molto
   nell'ultima settimana (28 settembre 2026): per G1 lordo +0,92 punti e funding +0,20 punti, netto massimo 0,73 punti; G11 0,91 e G1N 0,87.
   Per F5 il massimo è 0,18 punti. La prima settimana (4 gennaio 2021) differisce di 0,50 punti nelle spese. Il rendimento l'anno
   cambia poco: G1 rifatta +54,4% (salvata +54,1%), Sharpe 1,98 (1,97), spese 6,35% (6,54%), discesa uguale (-28,75%); ordini
   117.037 contro 117.045. Non ho trovato la causa (pannello cambiato il 6 e il 10 novembre, candele orarie o altro). A usa le salvate,
   B il codice di oggi: il confronto A-B porta questo piccolo scarto. **Non l'ho corretto né aggirato.** G1 rifatta (stesso codice di B):
   +54,4%, Sharpe 1,98, discesa -28,8%, spese 6,35%, settimana peggiore -9,4%, giorno peggiore -8,50%: il confronto con B non cambia.
2. **Buchi dei dati nel periodo** (punto 9 della chiusura; letti dal pannello ufficiale, che ha già i giorni riempiti dall'interfaccia
   pubblica; non ho rilanciato `buchi_archivio` perché riscrive `buchi_archivio.json` e scarica dati): sì, ci sono. 5 giorni (26 feb - 2 apr
   2022, vari giorni) su circa 50 monete (FIL, FLM, FLOW, FTM, GRT, HBAR, LTC, MANA, NEAR, SAND, SOL, TRX, XLM, XRP, ZEC e altre), 26 giorni su
   BNX (17 apr 2022 - 21 feb 2023), 26 su ICP (1-26 settembre 2022), 29 su TLM (1-29 marzo 2023), 2 su GMT. Nessun giorno senza candele per tutte le
   monete. Il giorno 28 ottobre 2026 e il buco di MDT (13-20 ottobre) cadono dopo la fine del periodo. Sono gli stessi dati di G1, G11, G1N
   e F5, quindi toccano tutte le serie allo stesso modo. Non so se il caricatore li tratta come rendimento zero o come moneta fuori universo.
3. G1 e G1N hanno lo stesso numero di variazioni (117.037): plausibile (ogni posizione cambia di peso ogni giorno), segnalato perché è identico.
4. F5 in A è a spese di mercato (4,93% l'anno) e le altre tre a ordini limite: A è più prudente di come girerebbe F5 a limite (F9, 3,48%).
5. Il confronto con G1 «sulle stesse settimane» coincide con le sue 300 settimane intere (punto 6 della chiusura).

## Varianti non previste che proporrei (non eseguite)
* B con F5 a ordini limite (F9) al posto di F5 a mercato, per togliere la differenza di spese fra le quattro.
* B con F5 a quote fisse che derivano col prezzo (lettura b della verifica), per togliere i 3,4 punti persi dal riequilibrio giornaliero.
* Miscele a due (G1 + F5, le meno correlate: 0,80) invece delle quattro: le altre tre sono quasi la stessa serie (0,84-0,91).

## Domande aperte
1. Le serie salvate di G1, G11, G1N differiscono da quelle rifatte oggi (anomalia 1): va rifatta la serie salvata, o si lascia com'è? Chi ne
   cerca la causa?
2. I buchi del pannello nel periodo (anomalia 2) sono trattati come zero o come moneta fuori universo? L'effetto sulle serie è noto?
3. Lo Sharpe corretto di A e B (0,73 e 0,75) è calcolato sul mazzo come sta, con la F5 vecchia (prima della correzione delle parità del
   23 ottobre) ancora dentro; con la F5 corretta potrebbe cambiare di poco. Va rifatto con il mazzo corretto?
4. Nessuna soglia scritta per dire «meglio di G1»: i numeri sono sopra e vanno ad Alessio (rischio più basso di 3-4 punti di discesa,
   rendimento uguale, correlazione 0,97-0,98).

## Letture delle regole che ho dovuto scegliere
* L'ora di ogni risposta «stato» è quella della riga `_eseguito:_` in testa al file (non l'ora di una riga interna).
* In avanti il 31 ottobre ha una sola lettura con le quattro (16:59), quindi è il punto di partenza; il rendimento dei giorni successivi
  parte da lì. Il 3 e il 4 novembre mancano (nessuna risposta con le quattro): intervallo unico 2-5 novembre.
* Ordini di A: per G1, G11 e G1N le variazioni del motore sulle serie giornaliere rifatte (G1 salvata: 117.045), per F5 le
  variazioni settimanali di peso non nulle (18.771); per B `n_tot` della stessa funzione.
* Il giorno peggiore di G1 è dal file salvato dei giorni (-8,5049%) e dalla serie rifatta (-8,5041%, stesso giorno).
* «Rendimento l'anno» = media settimanale per 52, come `te.esame`; discesa massima sul capitale composto settimana per settimana.
* Buchi dei dati: verificati dal pannello caricato e non con `buchi_archivio`, per non riscrivere il suo file e non scaricare nulla.
