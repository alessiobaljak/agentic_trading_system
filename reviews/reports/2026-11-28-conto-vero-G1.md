# Revisione del 28 novembre 2026: il conto vero torna a G1, capitale letto da Binance, chiusure sotto il minimo, 211, 213, 219, 220, 183

Revisore del percorso degli ordini. Copia di lavoro non committata sul branch `claude/brave-albattani-1b12fv`, sopra `acff1cb`
(il codice del percorso in HEAD è `16c5712`, quello del riavvio del 27 novembre, risposta `ops/results/0782-27nov-riavvio-correzioni-audit.md`).

## Riepilogo e verdetto

**Per il commit (conto vero spento): APPROVE con condizioni. Per l'accensione con soldi veri: REQUEST CHANGES.**

- Il codice fa quello che dice. Le mie tre prove nuove (sezione «Prove del revisore») passano sul codice di oggi: con un prelievo, la fase nuova non scavalca mai
  un motivo duro (versione non approvata); finito il motivo duro, aspetta la decisione dopo; sotto il pavimento del 65% il «riparti» resta
  rifiutato anche con la fase nuova del prelievo in attesa.
- Ma quelle tre regole **non hanno un test nel repository**: tolte dal codice, la suite resta verde (mutazioni M1, M3, M4). Problema 270.
- La regola delle chiusure sotto il minimo è **più larga di quella provata**: il codice manda con «solo riduzione» tutte le riduzioni, la
  revisione delle prove ha misurato e raccomandato solo le chiusure a zero (1,94). Le riduzioni il revisore delle prove le ha calcolate
  (1,92 col limite, 1,90 tutto a mercato, +51,8% l'anno invece di +57,1%), ma non le ha proposte. Problema 269: va scelto e scritto.
- I testi della dashboard dicono ancora «F5 sul conto vero» e «la prossima decisione di F5 (il lunedì)», proprio nella scheda dove Alessio
  approva la versione e fa ripartire il conto. Problema 268, prima dell'accensione.
- Nessun limite fisso toccato; le costanti del conto vero (leva 5, tetto 300, 600, stop 35%, pavimento 65%, 200%, 60%) invariate e fissate dal
  test di guardia. Chiusi 211, 213, 219, 220 (con test che cadono se si toglie la correzione) e 183 nel bot; 180, 181, 182 superati con G1.
- Test: `python3 -B -m pytest tests/ -q -p no:cacheprovider` sul checkout principale: **3131 passed in 174,77 s**, nessun fallimento
  (anche `test_allowlist_runnable[test]` passa qui). I test della ricerca (`research/src/tests`) non li ho lanciati io.

**Condizioni per il commit**
1. Il codice resta con queste impronte (prime 8 cifre): `conto_vero.py` bf5d78c8, `demo_binance.py` 55ddb46e, `main.py` 01f70bd2,
   `monitor.py` f2f6a77c, `state_snapshot.py` 10811867. I test possono cambiare solo per aggiungere quelli del 270.
2. Aggiungere i tre test del 270 (testo pronto in `reviews/reports/2026-11-28-conto-vero-G1-prove.txt`), oppure equivalenti, e verificare che cadano con le mutazioni M1, M3, M4.
3. Prima del riavvio scegliere la regola del 269 (chiusure a zero, come la prova, oppure tutte le riduzioni, come il codice) e scriverla
   in `docs/conto_vero.md` (punto 4, lettera l) con i numeri del revisore delle prove: il riavvio la mette subito sul demo.
4. Riavvio solo con l'ok di Alessio e dopo le letture della sezione «Cosa leggere sulla macchina».

## Oggetto

- **Branch**: `claude/brave-albattani-1b12fv`; modifiche non committate su `acff1cb`.
- **File del percorso** (impronte controllate, uguali a quelle del brief): `bot/portafoglio/conto_vero.py` bf5d78c8,
  `bot/portafoglio/demo_binance.py` 55ddb46e, `bot/main.py` 01f70bd2, `scripts/monitor.py` f2f6a77c, `scripts/state_snapshot.py` 10811867.
- **Test**: `tests/test_conto_vero_g1.py` d2934fb1 (nuovo, 32 test), `test_conto_vero.py` e7dd993f, `test_conto_vero_f5.py` 7f8b9046,
  `test_main_audit.py` 043faf4b, `test_portafoglio_audit.py` 83d66369, `test_stato_audit.py` 5b5a722a.
- **Documenti**: `docs/conto_vero.md` 3630bbf0, `docs/backlog.md` 16c80df9 (diverse da quelle nel rapporto del correttore, 680ed097 e
  f7b9b8e6: ritoccati dopo; solo testo).
- **Non toccati**: `bot/risk/`, `bot/config.py`, `bot/execution/`, `firebase/`, `ops/`, `dashboard/` (`git diff --stat` vuoto).
- **Invarianti coinvolti**: strategia ed età della decisione del conto vero; capitale del conto vero (condizione d); prelievo; valore oltre
  600; chiusure e riduzioni sotto il valore minimo (demo e conto vero); inversione su moneta in sola riduzione; avvisi al telefono; ordine
  dei giri in `main.py`.

## Checklist A–F

### A. Limiti fissi e interruttori
- Valori di `bot/risk/hard_limits.py` invariati (`:17` leva 5, `:18` 3%, `:21` 5%, `:25-26`): **OK**.
- Nessun limite critico spostato in configurazione, ambiente o Firebase: **OK**. Il tetto del capitale resta una costante
  (`conto_vero.py:141`); il saldo letto da Binance può solo abbassarlo (`:874-889`, `min(voluto, saldo)`); il file `ops/conto_vero_capitale`
  può solo abbassarlo (`:653`). Un numero sbagliato nel file ferma gli ordini (`:633-639`, `:916-917`).
- Parametri della dashboard (`user_risk_settings`, vecchio bot): **NON APPLICABILE** (non toccati; restano i difetti noti, mappa sezione 6).
- Limiti propri di G1 sul demo e sul conto vero come costanti: **OK**, fuori da `hard_limits.py` come deciso l'8 novembre; test di guardia
  `tests/test_conto_vero.py:169-194` (ora dice G1, 26 ore, `paper_g1.json`).
- Pulsante che chiude tutto senza Firebase: **OK** e invariato (file `ops/conto_vero_chiudi_tutto` e `ops/demo_binance_chiudi_tutto`,
  `demo_binance.py:1389-1410`). Il fermo ora va sempre al telefono (`:156`, `:785-786`).

### B. Ordini
- Passi e minimi dalle informazioni del simbolo: **OK** (`ordini_del_giorno` `demo_binance.py:365-386`, filtri dall'exchangeInfo a ogni
  ribilancio). Cambia la regola del minimo: sotto il valore minimo partono chiusure **e riduzioni** con «solo riduzione»
  (`ordine_saltato` `:347-353`, `riduce_soltanto` `:341-344`; resto a mercato `:2046-2051`). **PROBLEMA 269** (più larga della prova).
  Che Binance accetti la «solo riduzione» sotto i 5 USDT è scritto solo nel testo dell'errore -4164: da vedere sul demo.
- Identificativo: **OK**. Limite con identificativo nuovo a ogni tentativo e annullo degli aperti prima di contare (scelta del 24
  ottobre, invariata); resto a mercato con identificativo fisso controllato (`:2052-2053`); la chiusura dopo un -4140 ha un identificativo suo
  (`g1c-…`, `:323-330`, `:1850-1851`).
- «Solo riduzione» coerente con una posizione per moneta: **OK** (`:1767-1771`); l'inversione su una moneta in sola riduzione manda solo la
  chiusura (`:1804-1829`) e il resto a mercato non riapre (`:2046-2047`). Il freno del conto vero lascia passare solo «solo riduzione»
  (`conto_vero.py:343-347`).
- Prezzo che attiva gli stop: **NON APPLICABILE** (nessuno stop su Binance; lo stop sul conto legge il valore del conto ogni minuto).
- Leva e margine espliciti: **OK**, invariati (`demo_binance.py:1835-1840`).
- Stop per posizione su Binance: **NON APPLICABILE** a G1 (strategia a portafoglio). Protezioni: stop sul conto e pulsante, esistono e sono
  provati dai test; l'assenza di stop per moneta resta una decisione di Alessio (piano, punto 4 lettera i).

### C. Stato e resilienza
- Stato di Binance che prevale: **OK**. Il capitale ora viene dal saldo vero (`saldo_usdt` `demo_binance.py:469-483`, letto a ogni lettura
  del conto `:1650`); le posizioni e i resti si calcolano dalle posizioni vere, come prima.
- Flussi in tempo reale: **NON APPLICABILE** (solo richieste).
- Decisioni su candele chiuse: **OK**, invariato (la decisione di G1 delle 00:05, età massima 26 ore `conto_vero.py:154`).
- Errori delle interfacce: **OK**. 429 e 418 come prima; in più il 429 che dura oltre 30 minuti senza un giro di protezioni riuscito va al
  telefono una volta (`demo_binance.py:1281-1311`, serie azzerata a `:1187`). Saldo illeggibile o a zero: niente ordini (`conto_vero.py:919-921`);
  a metà della fase nuova la fase non parte (`:865-889`) e si riprova dopo 30 minuti (già chiuse le posizioni: direzione sicura).
- Firebase che non risponde non blocca rischio e chiusure: **OK**. Il segno «telefono» lo scrive solo il giro (`:825-869`), mai il filo;
  un errore lì non risale.
- Orologio: **NON APPLICABILE** (invariato).

### D. Separazione fra paper, demo e conto vero
- **OK**, invariata: `ClienteVero` solo `fapi.binance.com`, demo solo `demo-fapi`, `DRY_RUN` vero o interruttore assente → conto vero
  spento (`conto_vero.py:444-449`); con il conto mai acceso nessuna richiesta e nessuna chiave letta. Lo spento è sempre un motivo duro
  (`:976-978`, `:996-997`): la fase nuova non lo scavalca.

### E. Segreti e sicurezza
- Nessuna chiave nel diff, nei log o in Firebase: **OK** (ricerca nel diff). I log scrivono il saldo del conto vero (non è un segreto; il
  valore del conto era già nello «stato»).
- Chiavi di Binance senza prelievo e limitate all'indirizzo: **da confermare con Alessio** (invariato).
- Regole di Firebase pubblicate con i blocchi del conto vero: **da confermare con Alessio** (invariato; segnaposto nel repository).

### F. Test
- Test della modifica: **PROBLEMA 270** (tre regole di sicurezza senza test). Gli altri cambi hanno test che cadono se si toglie la
  correzione: mutazioni M2 (tetto ignorato: 19 test), M6 (aperture sotto il minimo: 4), M7 (riduzione senza «solo riduzione»: 7), M8 (resto
  che riapre: 2), M9 (telefono sempre segnato: 2), M10 (fermo col limite orario: 2), M11 (capitale da `totalWalletBalance`: 3), M12 (chiusura
  dopo -4140 senza «solo riduzione»: 1), M13 (monitor che tiene fuori ogni 429: 2). Sopravvivono M1, M3, M4 (solo le mie prove le prendono)
  e M5 (saldo a zero dopo le chiusure, difesa in più: nessun test).
- Test dei limiti fissi eseguiti e superati: **OK** (`tests/test_risk.py`, `tests/test_sizing.py`, `tests/test_conto_vero.py:169`, nel giro).
- Comando ed esito: `python3 -B -m pytest tests/ -q -p no:cacheprovider` → `3131 passed in 174.77s`.

## Problemi

**268 — Medio (prima dell'accensione) — `dashboard/app/lib/strategie.ts:61`, `:63`; `dashboard/app/components/strategie/ComandiContoVero.tsx:182`, `:193`**
- La scheda si chiama «F5 sul conto vero»; la descrizione dice «dal 25 novembre 2026 al posto di G1»; il «riparti» dice «riapre alla prossima
  decisione di F5 (il lunedì)» e «fino a 7 giorni dopo». Il codice esegue G1, ogni giorno.
- Guasto: Alessio approva la versione o fa ripartire il conto convinto di accendere F5 con il ciclo del lunedì; si aspetta ordini il lunedì
  e ne vede ogni notte (o il contrario: legge «fino a 7 giorni» e non controlla la mattina dopo).
- Correzione (sessione della dashboard): testi su G1 e la mezzanotte; mostrare nella scheda dell'approvazione `versione.strategia`, che il bot
  ora scrive (`conto_vero.py:536`); un test che confronti il nome della scheda con `conto_vero.STRATEGIA`.

**269 — Medio — `bot/portafoglio/demo_binance.py:341-353`, `:380`, `:2050-2051`**
- Il codice manda con «solo riduzione» sotto il valore minimo ogni chiusura **e ogni riduzione**; gli aumenti sotto il minimo restano saltati.
- La revisione delle prove (`audits/reports/2026-11-28-G1_CONTO_VERO_250.md:179-188`, `:230`) ha raccomandato solo **le chiusure a zero**;
  il suo «1,94» è quella regola. La regola del codice è la variante «riduzioni» del suo calcolo
  (`audits/repro/g1_conto_vero_250_2026-11-28_esito_conto.json`): Sharpe 1,918 col limite e 1,897 tutto a mercato, +51,8% l'anno contro
  +57,1% delle chiusure e +55,9% del bot di oggi, volatilità 0,270 contro 0,294, discesa −27,2% contro −29,4%. La prova 148 (`A2`,
  `research/programma7/ottantaseiesima.py:80-82`) aveva visto la stessa regola peggiore (1,83 contro 1,90).
- Guasto concreto: nessuno di sicurezza («solo riduzione» non apre mai). Ma il conto fa una cosa diversa da quella giudicata: le posizioni
  con il minimo alto (BTC, ETH, BCH, LTC, LINK) scendono quando G1 le riduce e non risalgono quando le aumenta, quindi il conto resta sotto
  il peso voluto (il correttore lo scrive, «non misurato»). Il riavvio lo porta subito sul demo, e il confronto settimanale di paper e demo
  cambia significato da quel giorno.
- Correzione: o limitare la regola a `obiettivo == 0` (come la prova; una riga in `ordine_saltato`/`riduce_soltanto` del solo controllo del
  minimo, con i test cambiati insieme), o tenerla e scriverla nel piano con i numeri qui sopra. Decide Alessio (decisione 3 della revisione
  delle prove), la sessione principale porta i numeri.

**270 — Medio — `bot/portafoglio/conto_vero.py:941`, `:980-988`, `:996-999`, `:1020`, `:800-809`; test mancanti**
- Tre regole che tengono i limiti non hanno test: (a) la fase nuova toglie il blocco (`motivo = None`, quindi il freno del cliente si apre)
  solo se tutti i motivi sono «della fase» (`_solo_della_fase = bool(della_fase) and not ragioni`); (b) dopo un motivo duro la fase nuova
  aspetta la decisione dopo (`blocco_duro`); (c) con la fase nuova di un prelievo in attesa il pavimento del 65% vale ancora per il «riparti».
- Mutazioni sulla copia (`…/scratchpad/rev28nov/mutazioni.py`): togliere `and not ragioni` (M1), il controllo di `blocco_duro` (M4) o
  l'eccezione di `_riparti_ammesso` (M3) lascia verdi tutti i test del percorso. Guasto possibile dopo un ritocco futuro: alla mezzanotte, con
  un prelievo e la versione non approvata, il conto vero chiude tutto e riapre con un codice che Alessio non ha approvato; oppure riparte
  sotto il pavimento, e la perdita supera il 35% deciso l'8 novembre.
- Il codice di oggi è giusto: le mie tre prove passano e cadono con M1, M4, M3.
- Correzione: aggiungere i tre test (`reviews/reports/2026-11-28-conto-vero-G1-prove.txt` e la prova B della copia) a `tests/test_conto_vero_g1.py`. Utile anche un test per M5 (saldo a zero letto dopo le
  chiusure: la fase non parte).

**271 — Basso — `bot/portafoglio/demo_binance.py:1825-1829` e `:1842-1866`**
- Sul conto vero, per una moneta in sola riduzione la voce «chiusa con «solo riduzione»» entra fra i rifiutati **prima** di mandare la
  chiusura. Se Binance rifiuta anche la chiusura (per esempio stato `BREAK`), entra una seconda voce per la stessa moneta.
- Guasto: il peso si conta due volte nell'allarme dell'1% e il testo dice «chiusa» quando non lo è.
- Correzione: scrivere la voce dopo l'esito della chiusura, con il testo giusto.

**272 — Basso — `bot/portafoglio/conto_vero.py:1017-1026`, `:980-990`**
- `_fase_nuova_adesso` guarda solo che nel file ci sia un giorno nuovo, non che la decisione si possa eseguire (età fino a 26 ore, pesi validi).
- Guasto: con un prelievo in attesa e una decisione vecchia o con pesi fuori dai limiti, a ogni giro il blocco si toglie: il freno del
  cliente si apre per il giro, l'allarme `ordini_vietati` con il motivo del prelievo sparisce e lo stato dice «acceso». Nessun ordine parte,
  perché poi `_decisione_da_non_eseguire` ferma il ribilancio: resta visibile solo l'allarme della decisione.
- Da sapere (non un difetto): se il saldo torna al valore del bot proprio al giro della decisione, quella decisione si salta e le posizioni di
  ieri restano un giorno in più (regola di sempre: un blocco finito aspetta la decisione dopo). Lo mostra la mia prova B.
- Correzione: in `_fase_nuova_adesso` gli stessi controlli di età e pesi di `_decisione_da_non_eseguire` (senza scrivere allarmi).

**273 — Basso (prima dell'accensione) — `bot/portafoglio/conto_vero.py:956-959`, `demo_binance.py:469-483`**
- Il capitale e il prelievo si leggono sulla riga USDT; il valore del bot conta solo i redditi in USDT. Il codice non controlla le impostazioni
  che questo presuppone e che il piano chiede ad Alessio (`docs/conto_vero.md:43-45`): niente margine a più valute, niente BNB per le
  commissioni, niente «portfolio margin». Con le commissioni in BNB il valore del bot non le conta (vanno fra i «non contati») e lo stop
  misura un conto un po' più ricco del vero.
- Correzione: all'accensione leggere `GET /fapi/v1/multiAssetsMargin` e `GET /fapi/v1/feeBurn` (solo letture) e fermare gli ordini nuovi, come
  motivo duro, se uno dei due è acceso.

**Chiusi o superati in questo giro**
- **211** chiuso: `telefono` solo a invio riuscito, segnato dal giro (`demo_binance.py:520-552`, `:790-869`); un invio fallito non conta per
  l'ora. Prova: M9.
- **213** chiuso: inversione su moneta in sola riduzione → solo la chiusura; -4140 sul conto vero → chiusura subito (`:1804-1858`); il resto non
  riapre (`:2046`); una chiusura accettata non toglie la moneta dalla memoria del demo (`:1867`). Prove: M7, M8, M12.
- **219** chiuso: 429 oltre 30 minuti al telefono una volta, nel bot e nel monitor (`monitor.py:60`, `:151-175`, `:193-224`). Prova: M13.
- **220** chiuso: fermo e stop sempre al telefono; il monitor conta per tipo (`monitor.py:139-148`). Prova: M10.
- **183** chiuso nel bot (testi con `STRATEGIA`, `versione.strategia`, titolo dello stato); la parte della dashboard è il 268.
- **180, 181, 182** superati: con G1 la decisione è ogni giorno, quindi limiti dei pesi ogni giorno, attese fino alla mezzanotte dopo e
  controllo del margine con i pesi del giorno, come nel G1 approvato prima del 25 novembre.
- L'Alto 2 dell'audit di F5 (posizioni sotto il minimo mai chiuse) è corretto nel codice, con la riserva del 269 e la verifica sul demo.

**Ancora aperti, invariati**: 54 (ii) Alto, 70 Medio, 78 Basso (`reports/2026-11-12-conto-vero-versione-firebase-2.md`); 217 e 221 Bassi
(`reports/2026-11-27-bot*.md`).

## Invarianti modificati

- **Conto vero, strategia**: F5 → **G1** (`conto_vero.py:152-155`), file `data/paper_g1.json` (lo stesso del demo), età massima **194 → 26
  ore**, decisione ogni giorno alle 00:05 UTC. Il giro del conto vero ora parte **subito dopo il paper di G1**, prima del demo
  (`main.py:2739-2757`); per il demo i tempi non cambiano (era già dopo il conto vero).
- **Conto vero, capitale (condizione d)**: non più il file obbligatorio, ma il **saldo USDT del portafoglio dei future** (`walletBalance` della
  riga USDT) letto dopo le chiusure a ogni fase nuova, al massimo **300** (costante) e al massimo il numero facoltativo del file
  (`:874-889`). Un numero nel file sopra il saldo ora vale il saldo (prima: rifiutato). Saldo illeggibile, assente, non numerico o non sopra
  zero: niente ordini nuovi (`:919-921`).
- **Conto vero, fase nuova**: parte alla prima accensione, dopo un prelievo e con un numero nuovo nel file (o il file tolto) (`:625-662`); mai
  dopo uno stop e «riparti» (il pavimento resta sul capitale di partenza) e mai dopo un versamento.
- **Conto vero, prelievo**: prima fermava gli ordini nuovi senza uscita; ora li ferma subito e **alla decisione dopo chiude tutto e riparte
  dal saldo che c'è** (`:973-990`), misurato sulla riga USDT (`:956-959`). Il prelievo e il valore oltre 600 sono motivi «della fase»: non
  fermano la partenza di una fase nuova chiesta; tutti gli altri motivi sì (`blocco_duro`).
- **Valore oltre 600**: senza fase nuova chiesta resta bloccato come prima, finché Alessio non scrive un numero nuovo nel file.
- **Demo e conto vero, minimi**: chiusure e riduzioni sotto il valore minimo partono con «solo riduzione» (prima restavano); aperture e aumenti
  sotto il minimo saltati come prima (269).
- **Demo e conto vero, inversione su una moneta in sola riduzione**: solo la chiusura (213).
- **Avvisi**: segno `telefono` solo a invio riuscito; fermo e stop sempre; 429 oltre 30 minuti una volta; `dal` nel nodo `limiti_binance`.
- **Invariati**: limiti fissi del vecchio bot, costanti del conto vero e del demo, pulsanti, stop sul conto, `DRY_RUN`, indirizzi e chiavi.

## Cosa cambia sul demo al prossimo riavvio

1. Alla mezzanotte partono anche le chiusure e le riduzioni sotto il valore minimo, come ordine limite «solo riduzione» al prezzo mark e,
   dopo l'ora, a mercato «solo riduzione». Più ordini; le posizioni con il minimo alto restano un po' sotto il peso voluto (269). Il numero
   «sotto il minimo» del ribilancio scende, perché queste non si contano più.
2. Un'inversione su una moneta che il demo salta manda la chiusura «solo riduzione» (prima: niente, la posizione restava nel verso sbagliato);
   la moneta resta fra le saltate; dopo l'ora il resto chiude e non apre.
3. Una chiusura «solo riduzione» accettata non toglie più la moneta dalla memoria delle non disponibili.
4. Telefono: il segno arriva un giro dopo l'invio, e solo se Telegram l'ha preso; fermo e stop sempre; 429 lungo una volta.
5. Testi del log con il nome della strategia. Capitale del demo (file, 1.000), stop, pulsanti e limiti: invariati.

## Cosa leggere sulla macchina prima del riavvio

- Battito recente in `ops/heartbeat.md`; sulla macchina HEAD uguale al commit con le impronte sopra, cartella pulita.
- `DRY_RUN` vero (riga `/bot_status/dry_run`); `ops/conto_vero_acceso` e `ops/conto_vero_capitale` assenti; `data/conto_vero.json` assente;
  `/conto_vero/acceso_dal` e `/conto_vero/fermo` vuoti.
- Demo: `/demo_binance/fermo` vuoto; nessun ribilancio in corso (niente `ordini` nello stato del demo: non riavviare fra le 00:05 e le 01:15
  UTC); `ops/demo_binance_capitale` = 1000; `ops/demo_binance_chiudi_tutto` e `ops/demo_binance_riparti` assenti; allarmi accesi.
- Vecchio bot: `/commands/bot_state` (atteso «emergency»), `/commands/kill_switch` (falso), `/positions` e `/ordini_limite` vuoti (lo «stato» non
  li legge: backlog, P36).
- Dopo il riavvio: log d'avvio del demo e del conto vero (strategia G1, file `paper_g1.json`, 26 ore); `/conto_vero/versione` con `strategia`
  G1. **Alla prima mezzanotte**: `/demo_binance/ribilanciamenti/{giorno}/rifiutati` (un -4164 su una «solo riduzione» sotto i 5 USDT
  risponde alla domanda aperta 1), `sotto_il_minimo`, e dopo l'ora `…/limite` e `…/resti_rifiutati`.

## Cosa manca prima dell'accensione con soldi veri

Nel codice e nelle prove:
- 54 (ii) **Alto**: la chiave di amministratore di Firebase (macchina e flussi di GitHub) può scrivere l'approvazione della versione al posto
  di Alessio; serve un'installazione per i soldi veri aggiornata solo da lui e la chiave fuori da GitHub.
- 70 Medio (decisione g del piano): prima della prima accensione lo stop non chiude le posizioni trovate nel conto.
- 78 Basso: il test di guardia del 54 non vede le costanti importate né i nomi a pezzi.
- 268, 269, 270 Medi; 271, 272, 273 Bassi; 217, 221 Bassi.
- Dalla revisione delle prove del 28 novembre: quale esame vale (Alto 1), il demo a 250 USDT (Alto 2), il margine dello stop di 4-5 punti
  (Medio 3), cosa fare oltre 600 USDT e chi avvisa (Medio 5), concentrazione fino al 43,7% senza limiti fissi (Medio 7), il conteggio
  «eseguiti a limite» sbagliato (Medio 9), le commissioni vere del conto.
- Verifiche vere: la «solo riduzione» sotto il minimo accettata da Binance (prima sul demo); una lettura vera del conto (riga USDT di
  `/fapi/v2/account`) e dei redditi (`/fapi/v1/income`) sul conto vero; rifare le prove S1b, S2b, S4 (`giro12nov/test_prove_12nov.py`) e
  `mutazioni2.py`; una revisione nuova sul commit dell'accensione.

Fuori dal codice (Alessio): regole di Firebase pubblicate con i quattro blocchi del conto vero e i pulsanti provati fino in fondo; chiave
di Binance senza prelievo e limitata all'indirizzo della macchina; conto dei future con una posizione per moneta, margine solo in USDT,
niente BNB per le commissioni, niente «portfolio margin», vuoto; le decisioni sì o no del piano (`docs/conto_vero.md`, punto 4, lettere
a-l, con la c e la l nuove di oggi); la richiesta esplicita di accendere e l'ok al riavvio.

## Decisioni per Alessio

1. **Chiusure sotto il minimo** (269): solo le chiusure a zero, come nella prova che è passata (1,94), o anche le riduzioni, come nel codice
   (1,92 col limite, +51,8% l'anno invece di +57,1%, posizioni un po' sotto il peso voluto). Vale dal riavvio anche sul demo.
2. **Il file del capitale**: va bene che non serva più, che resti solo come limite più basso, e che un numero sopra il saldo valga il saldo
   invece di fermare gli ordini? Un numero nuovo (o il file tolto) è la sua richiesta di una fase nuova.
3. **Il prelievo**: va bene che alla mezzanotte dopo il bot chiuda tutto e riparta da solo dal saldo rimasto (circa lo 0,2% del conto di
   commissioni, stima del correttore), invece di restare fermo fino a un suo gesto?
4. **Caso raro**: un prelievo e poi uno stop prima della mezzanotte, con il «riparti» sopra il pavimento: la fase nuova riparte dal saldo
   rimasto e il pavimento del 65% si rifà su quello. Così la perdita totale dalla partenza può superare il 35%. Va bene, o la fase nuova del
   prelievo deve tenere il pavimento di prima?
5. **Oltre 600 USDT** (revisione delle prove, Medio 5): oggi il conto si ferma senza ribilanciare finché non scrive un numero nel file.
6. Restano le decisioni già aperte: 54 (ii), 70 e le lettere a-l del piano.

## Domande aperte

1. Binance accetta davvero un ordine «solo riduzione» sotto il valore minimo (sopra la quantità minima), sia limite sia a mercato? Oggi lo
   dice solo il testo dell'errore -4164; la prima risposta vera verrà dal demo alla prima mezzanotte dopo il riavvio.
2. La sessione principale ha chiesto «chiusure e riduzioni» di proposito, sapendo che la revisione delle prove raccomandava solo le
   chiusure a zero? Se sì, la scelta va scritta con i numeri (269); se no, il codice va ristretto.
3. Sul conto vero di Alessio sono spenti il margine a più valute e i BNB per le commissioni? Il capitale letto dalla riga USDT lo presuppone (273).

## Prove del revisore

- Suite: `python3 -B -m pytest tests/ -q -p no:cacheprovider` → 3131 passed in 174,77 s (checkout principale).
- Copia per le mutazioni: `/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/rev28nov/copia`
  (5 test falliscono già sulla copia perché vogliono git, la dashboard, Firebase e i requisiti: esclusi dal conto). Script
  `…/scratchpad/rev28nov/mutazioni.py`, 14 mutazioni; esiti nella sezione F.
- Prove nuove (passano sul codice di oggi; da copiare in `tests/test_conto_vero_g1.py`).
Testo delle due prove principali in `reviews/reports/2026-11-28-conto-vero-G1-prove.txt` (non è un file di test: dentro `reviews/`
pytest lo raccoglierebbe).

La terza prova (saldo tornato proprio alla decisione: nessuna fase nuova, la decisione del giorno si salta) è nello stesso file della copia,
`…/rev28nov/copia/tests/test_probe_28nov.py`, `test_b_…`; prende la mutazione M14.

## Righe per gli indici

- `INDEX.md`, ultima revisione: «conto vero di nuovo su G1 e capitale dal saldo (28 nov, `reports/2026-11-28-conto-vero-G1.md`): APPROVE con
  condizioni per il commit spento (impronte `conto_vero.py` bf5d78c8, `demo_binance.py` 55ddb46e, `main.py` 01f70bd2, `monitor.py` f2f6a77c,
  `state_snapshot.py` 10811867; tre test del 270 da aggiungere; scelta del 269 prima del riavvio); REQUEST CHANGES per l'accensione. Chiusi
  211, 213, 219, 220, 183 (nel bot), superati 180-182; nuovi Medi 268-270, Bassi 271-273.»
- `REVIEW_LOG.md`: una riga con data 2026-11-28, branch, «non committato su `acff1cb`» e le impronte, oggetto, verdetto, stato «aperta», rapporto.
