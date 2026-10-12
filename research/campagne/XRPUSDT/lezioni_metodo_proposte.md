# XRPUSDT — Lezioni di metodo proposte (solo metodo e trappole dei dati)

* **I file di gennaio 2020 di alcune monete cominciano dopo il primo del mese** (XRPUSDT: last dal
  2020-01-06 08:00, mark dalle 03:00, funding dalle 08:00). La scheda dice «primo mese 2020-01» e le
  date di costruzione partono dal primo del mese: i primi giorni sono vuoti. Va guardata la prima
  barra vera in Fase 0 e dichiarata; la prima candela giornaliera è parziale.
* **Guardiano: forme di comando rifiutate in più a quelle già note**: `git -C <radice del repo>`,
  `cd research && ...`, `sed -i` su un file della campagna, Glob senza percorso, lettura dei file
  d'uscita dei comandi in background (stanno sotto /tmp), lo strumento di monitoraggio continuo.
  Regole pratiche: comandi dalla radice senza `cd` né `-C`; gli script scrivono i loro esiti in
  `data/insample/<SIMBOLO>/` (ammessa e fuori da git) invece di stamparli soltanto; per le
  modifiche ai file lo strumento di modifica, mai `sed`.
* **Il tetto dello stop al 6% e lo slippage**: uno stop calcolato al 6% della chiusura del segnale,
  misurato dal riempimento vero (apertura dopo, più slippage), supera di poco il 6%; il controllo del
  bot potrebbe rifiutare quel trade. Meglio fissare il tetto un po' sotto (per esempio 5,9%) o
  misurarlo dal prezzo d'ingresso atteso, deciso prima dei test.
* **Una soglia che conta trade rari va guardata anche per anno prima della validazione**: un
  candidato con quasi tutti i trade in un anno solo supera la verifica di stabilità per la lettera
  della regola (un solo anno con almeno 10 trade) e poi resta sotto i 30 trade in validazione.
  Proposta per il Passo 7: nella stabilità temporale richiedere almeno due anni con 10 trade, o
  dichiarare «non giudicabile» quando ce n'è uno solo.
* **L'orologio della macchina** ha dato durate brevi rispetto al lavoro svolto (40 minuti dalla prima
  all'ultima voce): le misure di processo basate sul campo `data` vanno lette con questo limite.
