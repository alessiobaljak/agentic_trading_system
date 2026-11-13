# Verifica della prova 155 (NOVANTATREESIMA.md, commit 8010fc8): punti ambigui

Modalità verifica, 13 novembre 2026. Nessun risultato calcolato né guardato. Dell'API di Deribit ho guardato solo i tempi (timestamp) e il
numero di righe. Le regole sono committate (8010fc8, 13 nov 12:21) prima di ogni calcolo. Le righe sotto sono ambiguità da chiudere prima di eseguire.

## 1. Confine del giorno del DVOL (resolution=1D)
* **Fatto misurato**: le righe giornaliere hanno tempo alle 00:00 UTC esatte (passo 86.400.000 ms, 365 righe nel 2022, nessun buco; anche la
  serie a 1 ora parte alle 00:00 UTC del 24 marzo). Il tempo è quello di apertura della candela (la candela a 1 ora ha lo stesso primo tempo).
  Quindi la riga con tempo D−1 00:00 chiude alle 00:00 UTC del giorno D: nota a quell'ora. La riga con tempo D 00:00 è la candela in corso: da non usare.
* **Ambiguità A1**: le regole dicono «chiusura del giorno D−1» ma non dicono che la riga si sceglie per tempo di apertura D−1 (non D).
  Proposta: usare la colonna chiusura della riga con tempo = D−1 00:00 UTC; il tempo di apertura è l'etichetta. Controllo di struttura (non di
  decisione) da fare e registrare: la chiusura della riga 1D con tempo T deve coincidere con la chiusura dell'ultima riga a 1 ora con tempo T+23h.
  Se non coincide, fermarsi e segnalare.
* **Ambiguità A2 (inizio dati)**: le regole dicono «parte il 23 marzo 2021, 284 giorni nel 2021». Interrogando con start 23 marzo 00:00 UTC la prima riga ha
  tempo **24 marzo 2021**, e dal 24 marzo al 31 dicembre i giorni sono 283, non 284. Proposta: valgono i dati come arrivano (prima riga 24 marzo);
  il «284» e il «23 marzo» delle regole sono un errore di conteggio di un giorno e non cambiano niente (il primo giorno giudicato è comunque a settembre).
  Il periodo di giudizio finale è comunque fissato dal rango a 180 giorni (vedi punto 2 e 5).
* **A3**: l'API rende i dati a pezzi di un anno con eventuale `continuation`; nel mio controllo `continuation` era vuoto. Proposta: se un pezzo ha
  `continuation` non vuoto, continuare; dopo l'unione, togliere i doppioni per tempo (tenendo la prima occorrenza) e verificare il passo di 86.400.000 ms.

## 2. Rango sulle 180 chiusure precedenti
Le regole scrivono «sulle 180 chiusure precedenti (D−180 … D−1)» ma poi parlano della chiusura di D−1 come del valore da giudicare: se fa parte delle 180 o no è ambiguo.
* **Proposta**: valore = chiusura di D−1; confronto = le 180 chiusure di D−181 … D−2 (le 180 prima di lei, lei esclusa). Rango = quota di quelle 180
  con valore **strettamente minore** del valore, più la metà dei pari (rango medio); esposizione ridotta se rango > 0,80 (strettamente sopra, come «sopra l'80%»).
  Perché: è la lettura standard del rango «contro la propria storia» e non dà alla chiusura di D−1 un posto nel proprio confronto. Con la lettura
  alternativa (D−180 … D−1 compresa) il rango minimo non sarebbe zero e il massimo sarebbe 100%: differisce per un passo di 1/181.
  Da registrare in nota la lettura scelta. Non provare l'altra (non è una variante ammessa).
* Primo giorno giudicato: con serie dal 24 marzo 2021 e 180 giorni di confronto più il valore, D−181 ≥ 24 marzo → D ≥ **21 settembre 2021** (24 marzo + 181 giorni).
  «19 settembre circa» è solo indicativo: vale il giorno che esce dalla regola, scritto nel rapporto.
* **Giorni mancanti**: nessun buco trovato nel 2022; la regola non dice cosa fare. Proposta: se nella finestra delle 180 mancano dei giorni, il rango si calcola
  su quelli presenti purché siano almeno 170; con meno, il giorno resta a esposizione piena e si conta; se manca la chiusura di D−1, esposizione piena. Contare e scrivere i giorni toccati.
* Soglia: 0,80 fissa; «sopra l'80%» = rango > 0,80.

## 3. I rendimenti di G1 della prova 120 e il costo del riequilibrio
* **Cosa esiste**: `research/programma7/risultati_prima/giorni_G1.csv.gz`, 2.100 righe, colonne `lordo, spese, funding, netto, netto_doppio, giro, long, short, monete, giorno`.
  `giorno` = numero di giorno (18631 = 4 gennaio 2021, ultimo 20730 = 4 ottobre 2026). Le spese sono già quelle con l'ordine limite (`spese_a_limite`).
  Esiste anche `settimane_G1_mercato.csv.gz` (spese a mercato).
* **Bastano?** No. Mancano i pesi per moneta: le colonne sono somme. Per la variante A il lordo e il funding si scalano proporzionalmente (peso×0,5), ma le **spese
  del riequilibrio** dipendono dal costo per moneta (0,01% su BTC, ETH, SOL; 0,02% altre) e dal prezzo del limite, quindi servono i pesi per moneta.
* **Strada (senza calcolare)**: ripetere la costruzione di `programma7/prima.py` `esegui`, righe 59-75: `pan = sc.pannello()`; `ps = te.pannello_settimane(...)`;
  `giorni = np.arange(se.INIZIO, FINE)`, `FINE = sc.giorno(2026,10,5)`; `Ud = universo_del_giorno(giorni, ps["lunedi"], ps["U"])`; `sig = ot.sigma_30(pan, idx)`;
  `W = vq.pesi_banda(np.where(isfinite(sig), -se.funding_7(pan, idx), nan), Ud, sig)`; `R = sc.rendimenti(pan)[idx]`; `F = nan_to_num(pan["funding"][idx])`;
  `costo = sc.costi_moneta(pan["simboli"])`. Poi i pesi della variante `W_var[d] = W[d] * m[d]` con m = 1 (G1), 0,5 (A) o 0 (B), e gli stessi conti:
  `te.conto(W_var, R, F, costo)` per lordo, funding (a mercato) e `cs.spese_a_limite(W_var, R, giorni, simboli, costo)` per le spese con il limite.
  Controllo di parità obbligatorio prima di tutto: con m = 1 sempre, la serie `netto` deve riprodurre quella di `giorni_G1.csv.gz` (differenza zero); se no, fermarsi.
* **Nota**: la regola dice «senza rifare le scelte delle monete, si cambia solo il peso del giorno»: W si calcola con la stessa memoria (la banda `pesi_banda` ha memoria del peso
  del giorno prima). **Ambiguità A4**: nella variante, il peso della banda del giorno dopo si calcola sui pesi pieni di G1 (non sui pesi ridotti), e il moltiplicatore si applica
  solo all'esecuzione. Proposta: sì, scelte di G1 invariate, `W_var = m × W` con W di G1 pieno; i costi di riequilibrio sono la variazione di `W_var` fra un giorno e l'altro
  (che include sia le variazioni di G1 sia l'entrata/uscita del freno).
* `revisione_g1n/nucleo.py` ha `variazioni(W, R, F, costo)` e `spese_limite(...)` ma è del lavoro su G1 neutra; per questa prova la strada è quella di `prima.py` sopra,
  **ambiguità A5** (quale usare). Proposta: `prima.py` (+ `cs.spese_a_limite`), perché è quella che ha prodotto i giorni della prova 120 e la parità si controlla.

## 4. Variante B: chiusura e riapertura
Le regole dicono «posizioni chiuse e riaperte quando il rango torna sotto l'80%» e al punto dei costi «0,05% a mercato … ordine limite 0,02% dove G1 già lo usa»: non dicono l'ordine né il prezzo.
* **Proposta**: stesso meccanismo di G1: tutte le variazioni di peso alle 00:00 UTC del giorno D, prezzo di riferimento l'apertura della candela a 1 ora delle 00:00; ordine limite per
  un'ora, se non preso passa a mercato alla candela successiva (come in `costo_limite` di `cinquantaseiesima.py`, usato da `spese_a_limite`). La chiusura è la variazione −W_giorno_prima, la
  riapertura +W_giorno_riapertura (con i pesi che G1 avrebbe quel giorno, non quelli vecchi: le posizioni riaperte sono quelle di G1 pieno del giorno). Nessun costo di tenuta da fermi, funding zero da fermi.
* Giorno di riapertura: il primo giorno D con rango ≤ 0,80.
* **A6**: in A e B il lordo di un giorno ridotto = peso ridotto × rendimento del giorno (da apertura di D ad apertura di D+1, come in `te.conto`); nessun rendimento è «tolto» a posteriori.

## 5. Periodo e l'anno parziale
* G1 della prova 120 va dal **4 gennaio 2021 al 4 ottobre 2026** (2.100 giorni, `FINE` = 5 ottobre escluso), non dal 23 marzo: l'universo parte dal 4 gennaio e le monete grandi nel 2021 ci sono.
  Le regole dicono «dal 23 marzo 2021 al 4 ottobre 2026 (`an.FINE`)»: **A7**, `an.FINE` non esiste in `prima.py` (c'è `FINE`); l'estremo finale è lo stesso, 4 ottobre incluso.
* Il confronto G1 contro variante parte però dal primo giorno con rango disponibile (21 settembre 2021 secondo la lettura del punto 2): **prima di quel giorno non c'è confronto**, e
  tutti gli indicatori dell'esame (netto, t, Sharpe, anni, discesa) si calcolano su **21 settembre 2021 → 4 ottobre 2026** per G1 e per le varianti.
* **A8 anno 2021**: «ogni anno positivo (2021 e 2026 anni parziali: si segnano)». Proposta: 2021 = 21 settembre – 31 dicembre; 2026 = 1 gennaio – 4 ottobre. Entrambi contano nel «ogni anno positivo»
  (sono anni con giorni giudicati); se uno dei due è negativo si scrive e l'esame segna «non passa», non «da ripetere». Il segnale «si segnano» non dice se contano: questa è la lettura più dura, quella che il proprietario
  ha usato nelle altre prove (verificare sul metodo se diversa: `programma7/METODO.md`).

## 6. Lo Sharpe corretto per famiglie
* `corretto_famiglie(nuove, candidate)` in `research/programma6/asticella.py` (riga 374). `nuove` = `{nome: serie settimanale netta}`, indicizzata dal **lunedì come numero di giorno** (usa `periodo`, che taglia
  fra 4 gennaio 2021 e 5 ottobre 2026 e toglie le settimane ferme prima della prima operata); `candidate` = `{nome: {"sharpe","settimane","asimmetria","curtosi"}}` da `te.numeri_settimana(x)`.
  Mazzo = `mazzo(nuove)` (prove del registro con serie + serie nuove, più gli Sharpe delle prove senza serie). Taglio `TAGLIO = 0.5` (0,3 e 0,7 solo come controllo); la correlazione dei rendimenti per gruppi è
  **settimanale** (`MIN_COMUNI = 52`).
* **A9 (nome e mazzo)**: nelle regole il «conto 316 → 318» non è definito nei file che ho letto (l'esempio di prova 28 usa 308 e 309: `N_REGISTRO, N_BRIEF`). Con `corretto_famiglie` il conto è il numero di famiglie (`len(sr_g)`),
  non il numero delle prove, quindi 316/318 non entra nel calcolo: si può scrivere come controllo. Proposta: passare le due varianti come due serie nuove («155 A» e «155 B»), con la **versione intera di G1 e delle
  varianti sul periodo del giudizio (dal 21 settembre 2021)**; lo Sharpe e le settimane del candidato vengono dalle sole settimane del giudizio, il mazzo per le famiglie resta il periodo standard
  (le prove altre non si accorciano). Dichiarare nel rapporto le famiglie e il gruppo di appartenenza di ogni variante; se A e B sono nella famiglia di G1, si segna.
* **A10**: la settimana parziale del 20 settembre 2021 (lunedì) contiene il giorno di partenza 21 settembre: la serie settimanale per `corretto_famiglie` comincia dal lunedì successivo (27 settembre) o dalla settimana parziale? Proposta: dal lunedì 27 settembre 2021, e i
  giorni del 21–26 settembre entrano solo nei controlli giornalieri; ultima settimana: lunedì 28 settembre 2026 (con giorni fino al 4 ottobre, intera). Così le settimane sono tutte intere.

## 7. Il controllo del ritardo e il test della differenza
* **Segnale con un giorno di ritardo in più**: alle 00:00 UTC di D si usa la chiusura di D−2 (non D−1), con la stessa finestra (180 prima di lei, lei esclusa) e la stessa soglia 0,80, per A e per B. Si riporta
  Sharpe e netto; è un controllo descrittivo, nessuna soglia di passaggio nelle regole. **A11**: nessuna soglia di esito scritta per questo controllo. Proposta: segnalare come «guarda avanti sospetto» se la variante con ritardo ha Sharpe più alto di quella senza di più di 0,2, altrimenti niente (da scrivere come lettura del ricercatore, non come criterio dell'esame).
* **Differenza delle serie, t almeno 2**: le regole dicono «con la differenza di serie giornaliere (variante meno G1) positiva e t almeno 2» senza dire quale t. **A12**. Proposta: serie giornaliera `d = netto_variante − netto_G1` sui giorni da 21 settembre 2021;
  t = media(d) / (dev.standard(d, ddof=1) / √n) **semplice** (non con errori robusti), con n = numero di giorni (non settimane). Come controllo aggiungere un t sulla serie **settimanale** (somma di 7 giorni, settimane intere) e uno con errori robusti
  (blocchi di 7 giorni, o Newey-West a 7 ritardi); se la lettura semplice dà ≥ 2 e le altre no, segnarlo nel rapporto, ma l'esame segue la lettura semplice sui giorni. «Positiva» = media > 0.
* **Sharpe «sopra G1 sullo stesso periodo»**: Sharpe giornaliero × √365 (la solita misura delle serie giornaliere, perché le valute girano sette giorni), per G1 e variante sullo stesso periodo; il t «almeno 3» dell'esame
  è `Sharpe × √(anni)` come in `corretto_famiglie` (`i["sharpe"] × sqrt(settimane/52)`), dalle settimane.
* **Discesa massima** «di G1 e delle varianti sullo stesso periodo»: sulla curva del capitale composta dal netto giornaliero (somma e prodotto vanno uguali nella pratica nel settore: usare il metodo di `te.numeri_settimana` per coerenza con l'esame, e la curva giornaliera come controllo).

## Altri punti trovati
* **Costo del DVOL non è un costo**: la serie DVOL non ha spese; il ritardo reale fra la chiusura alle 00:00 UTC e l'ordine è 0 (la candela chiude esattamente quando si ordina): ammesso solo perché la chiusura del DVOL del
  giorno D−1 è calcolata all'ora esatta; se la chiusura fosse pubblicata con un ritardo di minuti (dati in tempo reale) lo scarto non cambia i risultati sul passato. Non serve un ritardo aggiuntivo; il controllo con un giorno in più copre il caso.
* **Conto**: «Conta 2 prove» e «famiglia di G1 se la correlazione supera il TAGLIO»: l'appartenenza alla famiglia la decide `gruppi()`, non il ricercatore; si segna l'esito.
* **Salvataggio della serie DVOL**: dove? Proposta: `research/programma7/risultati_novantatreesima/dvol_btc_1d.csv.gz` (non in `research/data/`, che non si committa); è un dato esterno, non un caricatore ufficiale: **A13**, il metodo dice «solo tramite
  i caricatori ufficiali»; per il DVOL nessun caricatore esiste (la prova 47 ne usa uno?). Proposta: verificare con `grep -rn "get_volatility_index_data" research/`; se esiste un caricatore, usare quello; altrimenti il download dell'API pubblica
  nella prova è previsto dalle regole stesse (sezione Dati), e va dichiarato come l'unica eccezione.
* **Registro delle varianti**: `research/trials/NOVANTATREESIMA.csv` o `155.csv`? Proposta: `research/trials/novantatreesima.csv`, con 3 righe: G1 di controllo (parità), A, B, più le righe dei controlli (ritardo +1 giorno) marcate «controllo», non conteggiate come varianti.

## Esito della verifica
Le regole sono eseguibili con le letture sopra; le ambiguità che cambiano risultati sono A1 (riga da usare), il confronto del rango (punto 2), A4 (pesi della banda), A8 (anno 2021) e A12 (quale t). Da chiudere dalla sessione principale/Alessio prima del calcolo.
