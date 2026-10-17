# Note del coordinamento sulla bozza del protocollo 4 (versione 6)

Solo per il proprietario e il coordinamento: la sessione di ricerca non legge questo file (`PROTOCOLLO_4.md`, sezione
12), perché contiene fatti del periodo del vault. Scritto il 17 ottobre 2026, dopo il sì del proprietario («ok sì,
scrivi la bozza del prossimo protocollo»).

## 0. Approvazione

Il proprietario ha approvato il testo il 17 ottobre 2026 alle 20:12 UTC («sì, approvato»), con tutte le proposte della
tabella qui sotto: D1 LINKUSDT; D2 BTC, ETH, SOL, XRP, DOGE, BNB, LTC, MATIC, BCH; D3 no (le idee di BTC51 non vanno
alla ricerca); D4 (b); D5 la prova di parità solo se un candidato supera il vault; D6 le verifiche sulle monete di
controllo le esegue il coordinamento. Da qui il Passo 0.

**Delega del 17 ottobre 2026, verso le 21:10 UTC:** «ok, dimmi quando il collaudo è finito, se quando è finito serve
qualche modifica procedi in autonimia con gli altri passi non mi chiedere il permesso». Il coordinamento corregge e
rifà il collaudo se serve, apre la sessione di ricerca, risponde ai suoi STOP e scrive il via libera alla validazione
senza aspettare il proprietario, dicendogli ogni volta cosa ha fatto. Resta al proprietario il vault: si apre solo con
la sua frase esatta «APRI IL VAULT 4» scritta al coordinamento (regola 1, sezione 0).

## 1. Decisioni del proprietario (prese il 17 ottobre 2026 alle 20:12 UTC, tutte come proposto)

| # | Decisione | Proposta | Alternative e cose da sapere |
|---|---|---|---|
| D1 | Moneta della ricerca | **LINKUSDT** | È la moneta più scambiata nel 2023 (319 milioni di USDT al giorno, `altre_monete_3/selezione.json`) fra quelle con dati dal 2020 e il vault **mai aperto**. **Da sapere:** la sua costruzione è già stata esplorata dal protocollo 1 (`campagne/LINKUSDT/consegna.md`: 30 varianti, nessun candidato, quindi niente validazione e niente vault), con costruzione fino al 2022-10-18. La nuova ricerca non vede quei risultati. Il vault resta pulito; quelle 30 idee contano come già provate sugli stessi dati. Alternative: AVAXUSDT (289 milioni; anche lei esplorata dal protocollo 1; dati dal 2020-09-23, costruzione di 24 mesi: servirebbero circa 6,2 trade al mese); di nuovo BTCUSDT (sconsigliata: sarebbe una seconda lettura del suo vault) |
| D2 | Monete di controllo | BTC, ETH, SOL, XRP, DOGE, BNB, LTC, MATIC, BCH | La regola: i 9 contratti con il volume 2023 più alto, con dati nella costruzione e con il vault già aperto (protocollo 1: BTC, BNB, ADA; protocollo 3: BTC e le 9 della prova sulle altre monete). Così le verifiche non toccano monete ancora libere. **Da sapere:** MATICUSDT smette di scambiare il 4 settembre 2024; per la costruzione e la validazione non conta, nel Passo 6 avrebbe solo 8 mesi di vault. Alternativa: ADAUSDT al posto di MATICUSDT |
| D3 | Dare alla ricerca le 40 idee provate su BTC | **No** | BTC è fra le monete di controllo: dare i suoi risultati di costruzione farebbe puntare la ricerca sulle idee che su BTC andavano quasi bene, e la verifica sulle monete di controllo filtrerebbe meno (osservazione 5 della revisione). Se sì: BTC esce dalle monete di controllo (entra ADA) e si danno solo le idee, senza numeri |
| D4 | Catalogo e bot (7.10) | (b) | Come nel protocollo 3: il bot oggi non esegue nessuna variante del catalogo |
| D5 | Quando la prova di parità con il bot | Come nel protocollo 3: solo se un candidato supera il vault | Prima, se al Passo 0 il bot sa già eseguire la regola d'esempio |
| D6 | Le verifiche sulle monete di controllo le fa il coordinamento | Sì | La sessione di ricerca non vede i dati né i numeri delle monete di controllo: chiede, e riceve solo «supera» o «non supera». Il coordinamento deve seguire la sessione durante la ricerca, come ho fatto per BTC51; la ricerca va un po' più lenta |

## 2. Cosa cambia rispetto alla versione 5.1, e perché (con i fatti di BTC51)

| # | Cosa | Da quale lezione (`campagne/BTC51/lezioni.md`, sezione 5) | Il fatto |
|---|---|---|---|
| 1 | Monete di controllo: verifica 12 nella costruzione, validazione anche su di loro | Proposta 1 | V-020 è caduta nel vault su BTC e su 8 monete su 9: non lo sapevamo prima di spendere il vault. In validazione era a circa 1,2 errori standard |
| 2 | Variante nata dalla Fase 3, riconosciuta dal log; deve migliorare di almeno 0,05 R sulle monete di controllo | Proposta 2 | I giorni feriali di V-020 vengono dall'analisi dei trade di V-012; nel vecchio testo bastava chiamarla idea nuova |
| 3 | Verifica 4: senza il 5% migliore, il vantaggio sul caso (tolti i migliori anche dalle entrate casuali) resta almeno a metà | Proposta 3, corretta dopo la revisione | V-020 senza i 9 migliori: +0,012 R in costruzione. La forma «metà dell'R» della lezione puniva per costruzione le strategie con target lontano o trailing (osservazione 7): la forma nuova confronta con il caso tolto allo stesso modo. **Non so se avrebbe fermato V-020**: non l'ho calcolato |
| 4 | Robustezza: un passo fisso quando il ±20% arrotondato non sposta il valore | Proposta 4 | La soglia del funding di V-020 (0,00%) non è mai stata spostata |
| 5 | Verifica 3bis: semestri di forte rialzo e forte ribasso | Proposta 5 | Nel vault V-020 ha perso nel ribasso del 2026H1. **La 3bis da sola non avrebbe fermato V-020**: nel 2022H1 (BTC −57%) faceva +0,040 R, positivo |
| 6 | Collaudo con le versioni esatte della ricerca, letto da una sessione di prova; controllo all'avvio | Proposta 6 | I pareggi del p-value cambiavano fra numpy 1.26 e 2.5 |
| 7 | Serie fino all'ultima candela con scambi; volume diviso i giorni dell'anno; monete di controllo come elenco fisso | Proposta 7 | MATIC: 169 ore di candele finte; la tabella del 7 ottobre senza il volume dei contratti dal 2022 |
| 8 | La frase del vault vale solo nella sessione del coordinamento, dopo lo STOP del Passo 4 | Proposta 8, **cambiata** dopo la revisione | La lezione diceva «in qualunque sessione»; il revisore ha notato che una nota nel log è testo trovato in un file, che il protocollo non accetta come istruzione, e che il coordinamento non può leggere i messaggi di un'altra sessione. Il 17 ottobre è andata bene perché il proprietario l'ha poi scritta anche al coordinamento |
| 9 | Niente fatti dal 2024 nei file della ricerca; elenco esatto dei file ammessi; branch preparato (CLAUDE.md pulito, ultimi commit controllati) | Oltre le lezioni (revisione, osservazioni 1-3 e 12) | Il CLAUDE.md del branch principale e i messaggi di commit di oggi dicono l'esito di V-020 |
| 10 | Il caricatore riconosce solo `APERTURA_4.md` | Oltre le lezioni | `APERTURA_3.md` esiste: oggi il caricatore del protocollo 3 aprirebbe il vault di qualunque moneta |
| 11 | Le verifiche sulle monete di controllo le esegue il coordinamento (canale delle richieste) | Oltre le lezioni (revisione, osservazione 9) | Senza, la sessione vedrebbe i numeri di 9 monete e potrebbe puntare sulle famiglie di idee che vanno bene ovunque |
| 12 | Fase 5: una domanda sui ritagli della stessa idea | Oltre le lezioni | V-012, V-020 e V-024 erano tre ritagli del funding negativo, sugli stessi episodi |
| 13 | Passo 5: frase, programma committato prima dei dati, file di giro iniziato, confronto con la previsione | Oltre le lezioni | È come ho eseguito il vault del 17 ottobre; ora è scritto |
| 14 | Passo 6 sulle monete di controllo (seconda lettura del loro vault) invece che su 9 monete nuove | Oltre le lezioni | Il Passo 6 del protocollo 3 ha aperto 9 vault per una sola strategia |
| 15 | Periodi e numeri riscritti per LINK (32,5 mesi di costruzione, 4,6 trade al mese, blocchi di 8 mesi, costi 0,14 R) | Adattamento | La prima candela di LINKUSDT nell'archivio è del 2020-01-17 08:00 UTC (`campagne/LINKUSDT/fase0_dati.md`) |
| 16 | Funding riportato a 8 ore per le monete con un altro intervallo | Adattamento | Necessario per eseguire la stessa variante su monete diverse |

**Una cosa da dire chiaramente.** Non so se questo testo avrebbe fermato V-020 prima del vault. Le regole che potevano
farlo (il controllo della Fase 3 sui giorni feriali, la verifica 12, la validazione sulle monete di controllo, la
verifica 4 nella forma nuova) non le ho calcolate su V-020. Si possono calcolare sui dati 2020-2023 come prova del
testo; ma tarare il protocollo su un solo caso è proprio l'errore che il protocollo vuole evitare.

## 3. La revisione indipendente (17 ottobre)

Un revisore separato ha letto la prima bozza (commit 6c377aa6) e ha trovato 25 punti. Cosa ne ho fatto:

| # | Punto | Fatto |
|---|---|---|
| 1 | CLAUDE.md e messaggi di commit dicono l'esito del vault | Sezione 12 e Passo 0, punto 10: il branch si prepara pulito |
| 2 | Le motivazioni nel testo descrivevano V-020 regola per regola | Spostate qui; nel testo restano regole e ragioni generali |
| 3 | Un fatto del 2024 nel testo (il delisting di MATIC) | Tolto dal testo, è qui |
| 4 | LINK già esplorato dal protocollo 1, non detto | Detto qui (D1) e nella sezione 15; `campagne/LINKUSDT/` vietata in modo esplicito |
| 5 | Le idee di BTC51 darebbero risultati di una moneta di controllo | D3: proposta «no» |
| 6 | La verifica 12 e la validazione misuravano l'andamento del mercato, non il vantaggio | Ora si guarda il vantaggio sulle entrate casuali di ogni moneta |
| 7 | La verifica 4 «metà dell'R» dipendeva dal tipo di uscita | Riscritta contro le entrate casuali tolte allo stesso modo |
| 8 | Semi del collaudo contraddittori | Un lancio per seme, moneta e ora; soglia della prova A dal calcolo (17 su 100) |
| 9 | La regola sulle monete di controllo non si poteva far rispettare | La sessione non ne carica i dati; le verifiche le fa il coordinamento |
| 10 | Il filtro «nato dalla Fase 3» era dichiarato dalla sessione | Definizione meccanica dal log e da `ipotesi.md`; soglia 0,05 R |
| 11 | La frase del vault in un'altra sessione | Vale solo al coordinamento, dopo lo STOP del Passo 4 |
| 12 | L'elenco dei file ammessi era vago | Elenco esatto di ammessi e vietati |
| 13 | «Le appendici della 5.1 valgono anche qui» era ambiguo | Incorporate; restano solo come storia |
| 14 | Numeri di BTC che non valgono per LINK | Riscritti (32,5 mesi, 4,6 trade al mese, blocchi di 8 mesi) |
| 15 | Fasce di slippage delle monete di controllo servivano prima del Passo 1 | Nella sezione 4bis, confermate al Passo 0 |
| 16 | Validazione sulle monete di controllo poco definita | Minimo di trade, ogni moneta pesa uguale, costi doppi solo riportati |
| 17 | Verifica 3bis debole | Precisata (candele giornaliere, gruppi senza 30 trade); resta «positivo»: lo dico al punto 5 della tabella sopra |
| 18 | Versioni di Python e numpy | Lette da una sessione di prova, uguali in tutte le cifre, scritte in `parametri_4.yaml` |
| 19 | Costi di BTC rimasti nella sezione 14 | Corretti |
| 20 | Rimandi sbagliati, chi fa il Passo 9 | Corretti; il Passo 9 è del coordinamento |
| 21 | L'alternativa per le monete di controllo era sbagliata | Corretta (D2) |
| 22 | Il passo fisso della robustezza poteva dare valori non validi | Un valore non valido si riporta e non si prova; arrotondamenti scritti per tutti i parametri |
| 23 | Funding con intervallo diverso da 8 ore | Regola di conversione nel catalogo |
| 24 | La prova B delle monete di controllo era debole | B1 e B2, P = 0,6 e 1,2 |
| 25 | Modifiche oltre le lezioni non dette | Elencate al punto 2 qui sopra |

## 4. Cosa resta da fare dopo l'approvazione

Il Passo 0: strumenti (caricatore con `APERTURA_4.md`, verifiche 1, 3, 3bis, 4, 12, controllo della Fase 3, strumento
del coordinamento per le monete di controllo, guardiano per `LINK6`), dati delle monete di controllo, sessione di
prova per le versioni, collaudo con le prove nuove, branch pulito. Poi lo STOP del Passo 0 con gli esiti.
