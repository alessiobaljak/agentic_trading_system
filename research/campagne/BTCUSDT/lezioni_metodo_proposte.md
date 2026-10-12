# Lezioni di metodo proposte dalla campagna BTCUSDT

Solo errori di metodo e trappole dei dati: niente idee né risultati. Per il coordinamento,
che le filtra al Passo 7.

1. **Gli stop agganciati a un livello di prezzo falsano le baseline (a) e (b).**
   * Il problema: se lo stop è un livello (apertura del giorno, estremo della barra, numero
     tondo), la (a) e la (b) emettono lo stesso calcolo anche dove il livello è
     vicinissimo all'ingresso. Lì i costi in R diventano enormi e la media delle baseline
     va molto sotto zero.
   * Il numero: in questa campagna −0,83 e −0,31 R per una variante con R +0,15.
   * La conseguenza: un candidato che ha lo stop lontano per costruzione (la sua condizione
     d'ingresso lo garantisce) batte «nettamente» il caso senza alcun potere predittivo.
     Qui è successo a V11: t 3,01 con lo stop originale, 1,01 con lo stop fisso al 2%.
   * Proposta: per ogni candidato con lo stop a un livello di prezzo, una verifica
     obbligatoria con lo stop a distanza fissa, per candidato e baseline, registrata prima.
     Si potrebbe anche scrivere la regola nel protocollo.
2. **Il test del ritardo ha lo stesso difetto.** Con lo stop fissato al prezzo della barra
   del segnale, il ritardo cambia la distanza vera dello stop secondo il movimento della
   barra di mezzo. Nel controllo positivo, il lookahead col ritardo dava ancora t 8,4
   contro la (b), per effetto della normalizzazione (N006). Il t residuo del ritardo va
   letto con questo in mente.
3. **Il funding nei file di Binance arriva con qualche millisecondo di ritardo** (fino a
   47 ms, in 2.233 settlement su 4.383 di BTCUSDT). Senza arrotondamento il motore non
   riconosce il settlement all'apertura di una barra come ambiguo. Corretto in
   `src/dati.py` (commit 2fedf41, CHANGELOG dell'8 ottobre).
4. **L'ordine dei ritocchi per t contro la (b) può spendere il budget su varianti che non
   possono diventare candidati.** V19 aveva t 2,20 ma R lordo +0,045 contro costi di
   0,12 R. Cinque ritocchi l'hanno resa «netta» (t fino a 3,58) senza mai rendere l'R
   robusto ai costi doppi. Proposta: escludere dalla lista dei ritocchi le varianti con R
   lordo medio sotto i costi medi in R, perché nessun filtro può recuperarli.
5. **Parametri che interagiscono nella robustezza.** Spostare di −20% la finestra di 365
   giorni (a 292) con un minimo fisso di 300 valori dà zero trade: il caso non conta, ma
   va previsto quando si scrivono i parametri.
6. **Nella registrazione della validazione si scrive anche la previsione numerica.**
   L'ho dimenticata (N018): il formato della registrazione dovrebbe chiederla.
7. **Guardiano, regole pratiche in più:**
   * i file di uscita dei comandi in background (cartella temporanea della sessione) non
     si possono leggere: gli script scrivano i loro risultati nel log o in
     `data/insample/<SIMBOLO>/`;
   * i percorsi relativi con `..` e `find .` vengono rifiutati: usare percorsi assoluti.
