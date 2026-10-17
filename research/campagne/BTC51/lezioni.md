# Lezioni della campagna BTC51 (protocollo 3, Passo 9)

Scritto dal coordinamento il 17 ottobre 2026, sul branch principale, dopo il sì del proprietario («ok sì, chiudi la
campagna e scrivi le lezioni»). La campagna è chiusa.

## In una riga

Il metodo collaudato ha cercato su BTC con 40 idee ragionate e ha trovato un solo candidato. Il candidato ha
superato la validazione, è caduto nel vault e non ha retto sulle altre monete. **Nessuna strategia valida trovata;
il metodo ha fermato il candidato prima del paper, come doveva.**

## I numeri del percorso

| Tappa | Esito | Fonte |
|---|---|---|
| Collaudo del metodo (quarto giro) | prezzi senza vantaggio: 0 su 100 oltre la Fase 2, 11 su 100 con p sotto 0,10; vantaggio inserito da 0,2 R in su: 104 su 104 trovati, 0 su 90 senza vantaggio | `research/collaudo_3/esiti.md` |
| Costruzione (2020-01 → 2022-09) | 40 varianti su 40; 22 con R medio positivo, 16 con p-value fino a 0,10, 2 oltre la Fase 2 (V-020, V-030), 1 candidato (V-030 cade nella Fase 4) | `log.jsonl` del branch `research/campagna/BTC51` (commit 739a1853) |
| Validazione (2022-10 → 2023-12) | V-020 supera: 80 trade, +0,167 R, profit factor 1,29, +0,064 R a costi doppi | `validazione.md` dello stesso branch |
| Vault BTC (2024-01 → 2026-09) | V-020 non supera: 180 trade, −0,007 R, profit factor 0,99, p 0,337 | `research/vault/BTC51_risultati.md` |
| Altre 9 monete (vault) | regge solo su LTC; non si trasferisce | `research/altre_monete_3/risultati.md` |

## 1. Idee provate e cosa ne è stato

Le 20 idee della sessione di ricerca (`ipotesi.md` del branch della ricerca), con le varianti e il risultato in
costruzione. Soglia della Fase 2: almeno 150 trade, R medio dopo i costi di almeno 0,2, p-value fino a 0,023.

| Idea | Varianti | Migliore in costruzione | Cosa ne è stato |
|---|---|---|---|
| Rotture dei massimi e minimi (tendenza) | V-001…V-004 (1h, 2h, long e short) | V-003 +0,161 R, p 0,246 | non batte il caso |
| Prezzo sopra la media mobile | V-005…V-007 | V-007 +0,234 R, p 0,106; V-006 p 0,004 ma +0,031 R | non batte il caso con un vantaggio utile |
| Candele con volume anomalo | V-008…V-010 | V-010 p 0,027 ma −0,023 R | no |
| Funding estremo (folla a leva) | V-011 (short sopra +0,03%), V-012 (long sotto 0) | V-012 +0,171 R, p 0,023; V-011 +0,139, p 0,009 | sopra il caso ma sotto 0,2 R; V-012 genera V-020 |
| Rottura del range asiatico | V-013, V-014 | −0,025 R | no |
| Ritorno verso la media (Bollinger, mercato laterale) | V-015, V-016 | −0,135 R | perde |
| Comprare i ribassi in tendenza rialzista | V-017 | +0,025 R, p 0,074 | no |
| Rottura dopo la calma | V-018, V-019 | V-018 +0,196 R, p 0,011 | appena sotto 0,2 R |
| **Funding sotto zero nei giorni feriali** | **V-020** | **+0,223 R, p 0,017** | **candidato: validazione superata, vault fallito, 1 moneta su 9** |
| MACD nella direzione della tendenza | V-021, V-022 | +0,050 R | no |
| Vendere i rimbalzi in tendenza ribassista | V-023 | +0,023 R | no |
| Spremuta contro la folla a leva | V-024, V-025 | V-024 +0,193 R, p 0,002 | sopra il caso, sotto 0,2 R per i costi |
| Liquidità del fine settimana | V-026, V-027 | −0,010 R | no |
| Rotture con tendenza forte (ADX) | V-028, V-029 | +0,024 R | no |
| Tendenza nella calma | V-030 | +0,230 R, p 0,015 | oltre la Fase 2, cade nella Fase 4 (timeframe vicini, un blocco con il 70%, trade estremi) |
| VWAP della giornata | V-031, V-032 | V-032 +0,016 R, p 0,034 | no |
| Volume anomalo nelle ore americane | V-033, V-034 | −0,033 R | no |
| Range asiatico nei feriali | V-035, V-036 | +0,012 R | no |
| Eccesso con volume che rientra | V-037, V-038 | −0,141 R | perde |
| Asimmetria degli eccessi (Bollinger con volume doppio) | V-039, V-040 | V-040 +0,106 R, p 0,001 | vantaggio vero ma piccolo: non paga i costi a 1h |

Quello che resta, come conoscenza su BTC (osservato sulla costruzione):

- seguire la tendenza con rotture e medie mobili non ha battuto entrate casuali con le stesse uscite;
- il ritorno verso la media ha perso sempre, da 30 minuti a 12 ore;
- le rotture delle bande con volume doppio continuano, ma valgono +0,07/+0,11 R a trade, meno dei costi a 1h;
- il funding negativo seguito da un acquisto era l'unica famiglia con più varianti vicine alla soglia. Nel vault
  (2024-2026) non ha retto né su BTC né sulle grandi monete. Nei ribassi lunghi (2022H1, 2026H1) il funding resta
  negativo a lungo e il segnale perde: lì sembra misurare la tendenza, non una folla da spremere (inferito).

## 2. Errori di metodo (trovati e corretti, o rimasti)

Trovati e corretti prima di usare il periodo che toccavano:

1. **Le entrate casuali premiavano la larghezza dello stop.** Nel primo giro del collaudo le strategie finte su
   prezzi senza vantaggio battevano il caso in media di 0,027 R. Corretto con le entrate casuali alla stessa
   larghezza di stop (sezione 10.1), poi collaudo superato.
2. **I buchi del mark diventavano buchi finti nel last** (6 giorni del 2021-2022): il riscaldamento degli indicatori
   ripartiva, e a 1d la costruzione restava allo 0%. Trovato dalla sessione di ricerca al Passo 1, corretto nel
   caricatore, collaudo rifatto.
3. **I pareggi del p-value cambiavano con la versione di numpy** (5,6e-17 di differenza): trovato dalla sessione di
   ricerca, che girava con Python 3.13 e numpy 2.5 mentre il collaudo era stato fatto con 3.11 e 1.26. Corretto con
   una tolleranza; collaudo rifatto con le versioni della ricerca.

Rimasti nel testo del protocollo, e visti all'opera su V-020:

4. **Un filtro nato dai dati è passato come idea nuova.** I soli giorni feriali vengono dall'analisi dei trade di
   V-012 sugli stessi dati (Fase 3). La variante specchio V-011 mostrava l'effetto opposto. È proprio l'unico
   candidato, ed è caduto nel vault.
5. **La verifica dei trade estremi è troppo larga.** Senza il 5% migliore V-020 restava a +0,012 R e la verifica
   passava. Nel vault, senza i 9 migliori, −0,220 R.
6. **La robustezza non muove le soglie a zero** (±20% di zero è zero): il segnale d'ingresso di V-020 non è mai
   stato spostato (backlog).
7. **La validazione non chiede di distinguere dal caso.** +0,167 R su 80 trade sta a circa 1,2 errori standard da
   zero (consegna, limite 5). La validazione toglie chi crolla, non conferma chi resta: un candidato debole arriva
   al vault, e il vault si apre una volta sola.
8. **La stabilità nel tempo guarda 4 blocchi, non i mercati.** V-020 era già debole nel 2022H1 (+0,040 R su 65
   trade, BTC −57%): una strategia solo long su un segnale che si accende nei ribassi doveva essere guardata nei
   ribassi lunghi.
9. **Il p-value da solo separa poco sui prezzi veri.** 16 varianti su 40 con p fino a 0,10, contro 11 su 100 nel
   collaudo: su BTC molte regole battono le entrate casuali di poco (V-039 e V-040 p 0,001 con +0,07/+0,11 R). A
   fermarle è stata la soglia di 0,2 R dopo i costi.

## 3. Trappole dei dati

1. **Mark mancanti.** Nove giorni senza mark in BTC 2020-2026 (fra cui 2026-06-29, che manca su tutte le monete):
   il mark si prende dal last (sezione 9.6).
2. **Tabella delle monete incompleta.** `research/universo/candidate.csv` (7 ottobre) ha il volume 2023 solo per
   i contratti quotati prima del 2022: ne mancavano 127 con dati nel 2023, e APT stava fra le prime 9.
3. **La media del volume sui soli giorni presenti premia i contratti appena quotati** (ORDI con 55 giorni nel 2023,
   1000SATS con 20). Usato il volume dell'anno diviso 365.
4. **Contratti morti con candele finte.** MATICUSDT ha 169 ore a prezzo fermo e volume zero dopo l'ultimo scambio
   (4 settembre 2024), e mark e funding fino al 2026-09 senza scambi. La serie si ferma all'ultima candela con
   scambi.
5. **Il funding cambia frequenza con il mercato.** Su BTC il funding era sotto zero nel 3% dei regolamenti del
   2024H1 e nel 38% del 2026H1; sulle altre monete molto più spesso (BCH 14,8 trade al mese contro 5,5 su BTC). Un
   segnale sul funding ha un numero di trade che dipende dal mercato.

## 4. Cosa ha funzionato e va tenuto

- **Il collaudo del metodo prima della ricerca:** ha trovato un difetto vero delle entrate casuali prima che toccasse
  una variante.
- **Strumenti in sola lettura con le impronte**, e la sessione di ricerca che si ferma e chiede: due difetti trovati
  dalla ricerca stessa, nessuno strumento cambiato in silenzio.
- **La previsione scritta prima del vault:** 175 trade previsti, 180 veri; R dentro l'intervallo dichiarato.
- **Una sola esecuzione, con il file di giro iniziato e il programma committato prima dei dati.**
- **La prova sulle altre monete:** ha detto che il fallimento non era un caso di BTC (una sola esecuzione, 28 secondi
  dopo lo scarico dei dati).
- **Il coordinamento che parla da solo con la sessione di ricerca** (routine a un colpo sulla sessione), senza copia
  e incolla del proprietario.

## 5. Cosa cambiare nella prossima versione del protocollo (proposte, decide il proprietario)

In ordine di importanza:

1. **Provare l'idea sulle altre monete prima del vault, sul periodo già usato** (costruzione e validazione delle
   stesse 9 monete). Non consuma dati mai visti e dice se l'idea è generale o un caso di BTC prima di spendere
   l'unica apertura del vault (non sappiamo come sarebbe andata V-020 su quel periodo: non è stato provato).
2. **Un filtro nato dall'analisi dei trade (Fase 3) deve reggere anche dove non è nato:** sulla variante specchio, o
   sulle altre monete in costruzione. Altrimenti si tratta come un ritocco e costa una variante in più.
3. **Verifica dei trade estremi più severa:** senza il 5% migliore, l'R medio deve restare almeno a metà di quello
   intero (V-020: +0,012 contro +0,223, non sarebbe passata).
4. **Robustezza delle soglie a zero:** uno spostamento di un passo fisso (per il funding ±0,005%).
5. **Stabilità per tipo di mercato:** oltre ai 4 blocchi di tempo, il risultato nei semestri di forte rialzo e di
   forte ribasso, scritto prima.
6. **Collaudo sulle stesse versioni di Python e numpy della macchina di ricerca**, e il controllo delle versioni
   all'avvio della sessione.
7. **Scelta delle monete scritta in modo univoco:** volume dell'anno diviso i giorni dell'anno (o una copertura
   minima), tabella costruita su tutti i contratti, serie fino all'ultima candela con scambi.
8. **La frase del vault vale in qualunque sessione del proprietario:** la sessione che la riceve la registra nel log,
   il coordinamento esegue. Il 17 ottobre è andata così, ma il testo non lo diceva.

Resta aperto: la prova di parità con il bot (collaudo, Prova C) non è mai partita, perché nessun candidato è
arrivato al paper; il bot non sa ancora eseguire le strategie del catalogo (backlog).
