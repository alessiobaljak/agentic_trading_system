# Verifica della prova 168 (regole in `CENTOSESTA.md`), 22 novembre 2026

Modalità verifica: nessun risultato calcolato, nessun rendimento guardato. Regole committate: `7548ef9` (22 novembre 2026, 12:03 UTC).
Letti solo gli indici, le colonne e le date delle serie settimanali (mai i valori), gli script delle prove 24, 57, 69, 88, e con
`grep` le righe «equity» delle risposte «stato» (mai gli archivi). Niente aperto in `research/data/`. Il controllo dei dati
(`buchi_archivio`) è partito ma è lento: al momento di scrivere non era ancora finito (non fa parte delle quattro richieste).

## Esito: eseguibile solo dopo aver chiuso 1 punto bloccante e 7 ambiguità. B si può fare, senza toccare i motori.

## Cosa risulta

**Le quattro serie esistono e si leggono come in `asticella.py`** (`d["netto"]`, indice = numero del giorno del lunedì):
* F5 `programma6/risultati_ventiquattresima/settimane_F5.csv.gz`: 354 righe, dal 6 gen 2020 al 12 ott 2026, nessun buco, nessun vuoto.
* G1 `programma7/risultati_prima`, G11 `risultati_tredicesima`, G1N `risultati_ventiseiesima`: 300 righe ciascuna, dal 4 gen 2021 al
  28 set 2026 (l'ultima settimana finisce il 4 ottobre), passo 7 giorni, nessun vuoto.
* **Settimana di partenza comune: lunedì 4 gennaio 2021. Ultima: lunedì 28 settembre 2026. 300 settimane** (con `asticella.periodo()` e
  intersezione degli indici). G1, G11 e G1N hanno posizione già nella prima settimana (colonna `monete`); F5 le ha dal 31 agosto 2020.
  Anni: 2021 con 52 settimane, 2026 parziale (39).

## Punti, uno per uno

### 1. BLOCCANTE: quale serie di F5 (variante A, e anche il confronto)
Le regole dicono `risultati_ventiquattresima/settimane_F5` (è la serie che `asticella.py` ha nel mazzo come «24 F5»). Quella serie è **quella
di prima della correzione delle parità del funding del 23 ottobre** (`programma6/CONTROLLO_PARITA.md`: lo Sharpe pubblicato era il valore
più alto delle parità decise dal residuo di arrotondamento). Verificato: tutte le colonne differiscono da
`programma6/risultati_controllo_parita/settimane_F5.csv.gz` (la serie corretta, la stessa che usano le prove 57, 69 e 88 per il
confronto e il paper del bot). G1, G11 e G1N usano già `se.funding_7` corretto. Quindi A mescolerebbe tre serie corrette con una non
corretta, mentre B (pesi calcolati con il codice di oggi) userebbe la corretta: A e B non sarebbero confrontabili.
*Correzione più prudente:* «Per F5 si usa `programma6/risultati_controllo_parita/settimane_F5.csv.gz` (parità corrette). La serie
`risultati_ventiquattresima` non si usa». Nota: anche così F5 è con spese a mercato (0,05% + scarto), mentre G1, G11 e G1N sono con
ordini limite (motore `cs.spese_a_limite`); la versione di F5 a limite esiste (`F9`, stesso file di parità o `risultati_cinquantaseiesima`).
Scrivere se A usa F5 a mercato (più prudente, come scritto) o F9; si propone F5 a mercato e si dice nel rapporto che le spese di F5 sono più alte.

### 2. Pesi giornalieri per B: si ottengono tutti e quattro senza toccare niente
Tutte le funzioni sono già nei moduli esistenti (nessuna modifica a motori e caricatori). Passi, per giorni `giorni = arange(se.INIZIO, FINE)`,
`FINE = sc.giorno(2026,10,5)`, `idx = giorni - pan["t0"]`, `ps = te.pannello_settimane(pan, indicatori_si=False)`, `Ud = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"])`, `sig = ot.sigma_30(pan, idx)`:
* **G1** (prova 57, `programma7/prima.py`): `W_G1 = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, idx), np.nan), Ud, sig)`.
* **G11** (prova 69, `tredicesima.py`): `W_G11 = vq.pesi_banda(np.where(np.isfinite(sig), t13.segnale_fresco(pan, idx, Ud), np.nan), Ud, sig)`.
* **G1 neutra** (prova 88, `ventiseiesima.py`): `beta = f5n.beta_delle_monete(pan, Ud, idx)` e `W_G1N = f5n.scala_neutra(W_G1, beta)[0]`, con `f5n = research.programma7.ventiquattresima`.
* **F5** (prova 24): `vq.pesi_banda` calcolato sulle sole righe settimanali: `lun = ps["lunedi"] - pan["t0"]; sg = ot.sigma_30(pan, lun); Wt = vq.pesi_banda(np.where(np.isfinite(sg), -se.funding_7(pan, lun), np.nan), ps["U"], sg)`; poi i pesi dei giorni
  `W_F5 = pr.universo_del_giorno(giorni, ps["lunedi"], Wt)` (la funzione è generica: prende per ogni giorno la riga del suo lunedì).
  **Va calcolato su tutte le settimane dal 2020**, poi tagliato da `se.INIZIO`: la banda (entra al 20%, resta fino al 40%) ha memoria, e F5 ha già posizione dal 31 agosto 2020. Se si partisse da `INIZIO` i pesi sarebbero diversi da quelli della serie F5.
  G1, G11 e G1N invece partono da `INIZIO` senza storia: è così che sono state calcolate le loro serie, e va tenuto uguale.
* Il costo, il lordo e il funding sul peso netto: `Wn = (W_G1 + W_G11 + W_G1N + W_F5)/4`, `R = sc.rendimenti(pan)[idx]`, `F = np.nan_to_num(pan["funding"][idx])`, `costo = sc.costi_moneta(pan["simboli"])`, `te.conto(Wn, R, F, costo)` (dà lordo, funding con `x*F` sul peso netto, giro) e le spese con `cs.spese_a_limite(Wn, R, giorni, pan["simboli"], costo)`, poi `netto = lordo - spese - funding`, e `pr.per_settimana(...)`. È lo stesso schema di G1/G11/G1N.
* **Ambiguità (da scrivere):** «F5 tiene i suoi pesi dal lunedì alla domenica» ha due letture.
  (a) pesi costanti ogni giorno (come sopra): `te.conto` e `cu.variazioni` rifanno ogni giorno il peso di F5 verso il bersaglio, quindi il netto paga una piccola spesa di riequilibrio giornaliera che nel vero F5 (quote fisse, i pesi derivano col prezzo per sette giorni) non c'è; anche il lordo differisce un poco (interesse composto giornaliero contro settimanale). È la lettura più semplice e costa di più (prudente).
  (b) quote fisse con deriva: richiede di far derivare i pesi di F5 giorno per giorno fuori dai motori (codice nuovo, `W*(1+R)/(1+lordo)` come in `cu.variazioni`).
  *Correzione più prudente:* scegliere (a), scriverlo, e fare nel rapporto un controllo descrittivo: B costruita con la sola F5 contro la serie settimanale di F5 (differenza di spese e netto), per dire quanto vale la differenza. Non è una variante.
* Pesi di G1N: lordo massimo fino a 3 per scalatura `LIMITI (0.5, 1.5)`: la media dei quattro non è normalizzata; è la regola scritta («media dei pesi»), va solo ricordato nel rapporto.

### 3. Spese di B: «0,02% con ordine limite come nel motore di G1»
Scritto così sembra una commissione fissa dello 0,02%. Il motore di G1 non lo è: `cs.spese_a_limite` paga `MAKER = 0,02%` solo se la candela oraria dell'apertura scende sotto l'apertura (per comprare; sopra, per vendere), altrimenti paga `a mercato (0,05%) + scarto + il movimento contro` fino all'apertura dopo; senza candele orarie, a mercato. *Correzione:* «Le spese di B sono `cs.spese_a_limite(Wn, R, giorni, simboli, costo)` del motore di G1, applicate alle variazioni del peso netto (con il peso che deriva col prezzo, come `cu.variazioni`); 0,05% e scarto sono quelli di `sc.costi_moneta`». Aggiungere che il numero di ordini = `n_tot` restituito da quella funzione (variazioni di peso netto non nulle, per moneta e giorno).

### 4. Funding sul peso netto
Eseguibile come scritto: `te.conto` usa `x * F` con `F` giornaliero del pannello; nessuna riga da cambiare. Il funding del pannello dopo il 31 ottobre non entra (il periodo finisce il 4 ottobre). A: il funding di ogni strategia è già nelle sue serie.

### 5. Variante A: colonne e conti non scritti
La serie `settimane_A.csv.gz` deve passare da `te.esame`, che legge `netto`, `netto_doppio`, `spese`, `funding`, `long`, `short`, `giro`, `monete`; le regole dicono solo `netto`. *Correzione:* «A = media delle quattro serie di ogni colonna (`lordo`, `spese`, `funding`, `netto`, `netto_doppio`, `giro`, `long`, `short`), `monete` = somma; il capitale si riporta a un quarto a testa ogni settimana (media aritmetica del rendimento settimanale, senza composizione fra i conti)». Il giorno peggiore non si può dare per A: esiste solo il file dei giorni di G1 (`risultati_prima/giorni_G1.csv.gz`); G11 e G1N non salvano i giorni e F5 è settimanale. *Correzione:* «il giorno peggiore si riporta per G1 e per B; per A si riporta solo la settimana peggiore».

### 6. Esame: due scritte che non coincidono con il codice
* `te.esito` ha la soglia dello Sharpe corretto a **0,95** (vecchia) e «positiva in meno di 4 anni»; le regole dicono 0,80 e «ogni anno positivo». *Correzione:* scrivere che l'esito si calcola a mano con le condizioni delle regole (netto positivo, ogni anno di calendario positivo, 2026 parziale compreso, t = Sharpe × radice(settimane/52) almeno 3, `corretto_famiglie` almeno 0,80), senza usare `te.esito`.
* `corretto_famiglie(nuove, candidate)` va chiamata con `candidate = {"168 A": e["intero"], "168 B": e["intero"]}`; le serie già nel mazzo non cambiano, ma attenzione: il mazzo contiene ancora la F5 vecchia (punto 1) e la serie F5 corretta entrerebbe solo se data in `nuove` con un nome diverso, oppure no. *Correzione:* non cambiare il mazzo e dire che il conto per famiglie è quello del mazzo come sta (ricordando la F5 vecchia).
* «Confronto con G1 sulle stesse settimane»: le 300 settimane sono quelle di G1 intere, quindi il confronto equivale alle sue cifre (`risultati_prima/esame.json`, ordini inclusi). Va scritto.
* «Numero di ordini e spese l'anno» di A: *correzione:* ordini = somma dei quattro; spese l'anno = media delle quattro (colonna `spese` mediata ×52).

### 7. Periodo e settimana di partenza
Scritto «dalla prima settimana in cui tutte e quattro hanno una posizione al 4 ottobre 2026, `periodo()`»: è eseguibile, il risultato è 4 gennaio 2021 – 28 settembre 2026 (300 settimane). Si consiglia di scriverlo, così non si interpreta (F5 comincerebbe già nel 2020 e `periodo()` taglia al 5 ottobre, giorno dopo l'ultima settimana comune).

### 8. Parte in avanti: si può fare, con limiti da scrivere
* Le risposte «stato» hanno la riga `- equity: **$...** su $10,000 (...)` sotto le sezioni «## Paper F5», «## Paper G1 (», «## Paper G11», «## Paper G1N» (grep sulle righe, in ordine di numero di file).
* **Partenza comune: lunedì 26 ottobre 2026** (prima decisione di tutte e quattro, log `ops/results/0674-26ott-log-bot-prima-decisione-g1n-e-f5`: F5 e G1N con 10.000 e costo 4,00 al primo ribilancio; G1 e G11 giravano già dal 24 ottobre, con le sezioni «stato» dal 24 ottobre, F5 e G1N con le sezioni «stato» solo dal 31 ottobre).
* **Le righe «equity» di tutte e quattro insieme esistono solo da sabato 31 ottobre 2026** (file `0682-31ott-stato-pomeriggio`): 21 giorni distinti fino al 22 novembre. Dal 26 al 30 ottobre non c'è nessuna risposta «stato» con le quattro (ci sono solo i log del ribilancio con «equity» al momento del ribilancio, non risposte «stato»). Mancano anche il 3 e il 4 novembre.
* Ambiguità: non è una risposta per mattina ma da 1 a 5 al giorno, a ore diverse (dalle 00:13 alle 22:19). *Correzione più prudente:* «per ogni giorno si prende la risposta con l'ora della riga di stato del paper più vicina alle 04:15 UTC (l'ora del controllo del mattino, presente dal 13 novembre); il rendimento di un intervallo è equity finale / equity iniziale − 1 su giorni di calendario veri; il 2-5 novembre (nessuna risposta il 3 e il 4) è un solo intervallo di 3 giorni; il conto "un quarto a testa" = media dei rendimenti degli intervalli, e si dichiara che sono rendimenti dei giorni fra due letture, non a mezzanotte». Dire anche che la lettura del 26-30 ottobre si poteva fare solo con i log e che non si usa.
* Il costo `costi` della F5 ricomincia da 4,00 il 31 ottobre (da 6,44 di una prova precedente di F5 del 22-25 ottobre): sono due paper diversi, vale solo la serie dal 26 ottobre. *Correzione:* scriverlo e partire dal 31 ottobre.
* Nessun riavvio che azzeri il capitale dal 31 ottobre (il costo cumulato non cala in nessuna delle quattro).
* Resta da dire che il paper G1 e il G1N hanno 10.000 USDT ciascuno e il confronto «G1 da sola» è G1 sullo stesso intervallo.

### 9. Piccole cose
* `research/trials/centosesta.csv` e `centosesta.py` non esistono ancora (previsto).
* Le due varianti sono A e B; nessuna altra. Nessun seme (tutto deterministico): scrivere «seme 0» nel registro.

## Domande aperte (testuali)
1. Per A si usa F5 corretta di `risultati_controllo_parita` a spese di mercato (proposta) oppure F9 (stessa F5 con ordini limite)?
2. «F5 tiene i pesi dal lunedì alla domenica»: pesi costanti ogni giorno (lettura a, prudente, con riequilibrio giornaliero a spese) o quote con deriva (lettura b, codice nuovo)?
3. Per la parte in avanti: si parte dal 31 ottobre (prime risposte «stato» con le quattro) o dal 26 ottobre usando anche le righe di log del ribilancio?
4. La spesa di B è quella del motore di G1 (`spese_a_limite`, non un 0,02% fisso)?
