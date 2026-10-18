# 06 — La seconda stagione della ricerca (13-18 ottobre 2026): ordini limite, protocolli 2, 3 e 4

> Capitolo della storia del progetto: il riepilogo è in [`README.md`](README.md). Scritto il 18 ottobre 2026 da un lettore in sola lettura sul repository, poi ricontrollato da un secondo lettore che ha aperto le fonti e corretto nel testo gli errori trovati (circa 200 affermazioni, 8 corrette (fonti e citazioni; nessun esito d'idea sbagliato), e i conti marcati «calcolo mio» rifatti dai log). Dove il testo dice «bozza» o «questo pezzo», intende questo capitolo.

> **Aggiornamento dopo la verifica (18 ott, commit `896d5196`).** Consegna, ipotesi, log, lezioni e codice della
> campagna PANIERE, e i testi e i risultati di BTC51, sono stati copiati sul branch principale (`research/campagne/PANIERE/`,
> `research/campagne/BTC51/`). Dove questo capitolo dice che le lezioni del paniere «restano solo sul branch», valeva fino
> a quel commit; restano solo sul branch gli elenchi dei trade e dell'avanzamento del paniere (`trade/`, `avanzamento/`,
> circa 133 MiB).

> Bozza per la storia del progetto, pezzo F. Scritta il 18 ottobre 2026 leggendo il repository (branch
> `claude/brave-albattani-1b12fv`, ultimo commit `672663b8`) e i branch remoti `origin/research/campagna/PANIERE` e
> `origin/research/campagna/BTC51`. Solo lettura: nessun file del repository è stato cambiato.

**Come leggere questa bozza.**

* **Orari in UTC**, salvo dove c'è scritto «ora italiana» (in ottobre l'ora italiana è UTC+2). Il diario
  `docs/andremo_live.md` usa l'ora italiana; commit, log delle campagne e file di risultato usano UTC. Lo stesso fatto
  può quindi comparire con due orari diversi di 2 ore: non è una contraddizione.
* **R** è il risultato di un trade diviso il rischio iniziale (la perdita se scatta lo stop). «R medio» è la media per
  trade **dopo i costi**, salvo dove c'è scritto «lordo».
* **Entrate casuali**: strategie finte che entrano in momenti scelti a caso ma escono con le stesse regole della
  variante. Il **p-value** dice quante volte su 1.000 il caso fa almeno altrettanto (più è piccolo, meno è probabile la
  fortuna). Nella campagna PANIERE il confronto col caso si legge invece come **t** contro la «baseline (b)» (le entrate
  casuali di gruppo) e la «baseline (a)» (stessa uscita a ogni barra libera), con una soglia che dipende dal numero di
  «blocchi» (pezzi di tempo indipendenti).
* Ogni numero ha la fonte fra parentesi. «**stima**» = stima di chi ha scritto la fonte o mia. «**calcolo mio**» = conto
  fatto da me per questa bozza sui file citati, da ricontrollare.
* **I nomi si ripetono fra campagne.** V-001, V-020... e I-01, I-02... ricominciano da capo in ogni campagna: V-020 di
  BTC51 (il candidato caduto nel vault) e V-020 di LINK6 (un incrocio della media a 50 su 4 ore) sono strategie
  diverse. Anche «C1, C2» vuol dire tre cose diverse: le varianti dell'idea C del paniere, le due strategie della prova C
  del collaudo, e le conferme C1-C3 del catalogo.

---

## 0. La stagione in una pagina

Dal 13 al 18 ottobre la ricerca ha cambiato terreno tre volte, sempre con lo stesso esito: **nessuna strategia valida**.
Prima una prova sull'esecuzione (gli ordini limite), poi tre protocolli: il paniere di 80 monete a barre giornaliere
(protocollo 2), BTC da solo con un catalogo chiuso di regole e un collaudo del metodo (protocollo 3), LINK con 9 monete
di controllo (protocollo 4). Un solo candidato in tutta la stagione è arrivato al vault (V-020 di BTC51) ed è caduto.

| Quando (UTC) | Cosa | Fonte |
|---|---|---|
| 13 ott 07:13 | Regole della prova degli ordini limite in vigore («Procedi» del proprietario) | `research/esperimenti/ordini_limite/regole.md`, intestazione; commit `39bb60b2` |
| 13 ott 08:02-08:26 | Corse della prova sulle nove strategie; esito «conviene poco» | `research/esperimenti/ordini_limite/risultati.md`, sez. 2; commit `e9f065b3` |
| 13 ott 17:54 | Ricerca automatica del gate fermata (`ops/gate_fermo`) | commit `4c315e80`; diario 13 ott, 20:10 ora italiana |
| 13 ott 18:09 | Il bot in paper entra con ordini limite virtuali | commit `6d50adfa` |
| 13 ott 19:34 | Protocollo 2 (seconda edizione, versione 5.0) approvato | `research/PROTOCOLLO_2.md`, intestazione |
| 13 ott 20:29-21:56 | Passo 0 del protocollo 2, poi STOP | orari dei commit da `7e6a2dec` a `4ce9f293`; `research/passo0_2/rapporto.md` |
| 14 ott ~05:00 | «Procedi» del proprietario allo STOP | `research/PROTOCOLLO_2.md`, correzione 3 |
| 14 ott 06:58-14:12 | Campagna PANIERE: aperta, due fermate per il guardiano, una per gli strumenti, consegna «nessuna strategia valida» | diario 14 ott; `consegna.md` sul branch `research/campagna/PANIERE`, commit `70d17c85` |
| 15 ott | Nessun lavoro di ricerca (solo istantanee automatiche) | `git log` del 15 ott |
| 16 ott mattina | Il proprietario propone il suo protocollo 5.1 su BTC | diario 16 ott, mattina |
| 16 ott 19:26 | Protocollo 3 approvato | `research/PROTOCOLLO_3.md`, intestazione |
| 16 ott 21:01-21:10 | Collaudo del metodo, primo giro: non passa | `research/collaudo_3/esiti.md` |
| 17 ott 06:11 | Correzioni del collaudo approvate; secondo giro passa (06:28-06:49) | `research/PROTOCOLLO_3.md`, appendice 3; `collaudo_3/esiti.md` |
| 17 ott 07:19 | Sessione di ricerca BTC51 aperta | diario 17 ott («09:19 ora italiana») |
| 17 ott 07:49-09:39 | Due difetti trovati dalla ricerca; terzo e quarto giro del collaudo | `collaudo_3/esiti.md` |
| 17 ott 12:12-12:59 | Passo 2 di BTC51 (orari dei commit sul branch): 40 varianti, un candidato (V-020) | `git log origin/research/campagna/BTC51` |
| 17 ott 13:49 | V-020 supera la validazione | `validazione.md` sul branch BTC51, commit `56a33ede` |
| 17 ott 16:23-16:25 | Vault 3 aperto, V-020 eseguita una volta: non lo supera | `research/vault/APERTURA_3.md`; `research/vault/BTC51_risultati.md` |
| 17 ott 17:07-17:09 | V-020 su altre 9 monete: regge su 1, non si trasferisce | `research/altre_monete_3/risultati.md`; commit `22c756d5` |
| 17 ott 17:30 | Campagna BTC51 chiusa, lezioni | `research/campagne/BTC51/lezioni.md`; commit `09795c2d` |
| 17 ott 18:04-20:12 | Bozza del protocollo 4, revisione indipendente (25 punti), approvazione | `research/protocollo_4_note.md`, sez. 0 e 3 |
| 17 ott 20:49-21:54 | Collaudo del protocollo 4: passa al primo giro | `research/collaudo_4/esiti.md` |
| 17 ott 21:58 | Sessione di ricerca LINK6 aperta su un branch con storia propria | `research/campagne/LINK6/STATO.md` |
| 18 ott 06:42-07:54 | Passo 2 di LINK6: 33 varianti su 40, nessun candidato | `research/campagne/LINK6/log.jsonl` |
| 18 ott 08:14-08:30 | Consegna «nessuna strategia valida», lezioni | commit `bb8b444d` (branch LINK6), `f85a233a` (principale) |
| 18 ott ~08:40 | Il proprietario: si continua finché non si trovano strategie valide, anche riscrivendo il gate; prima la storia | `docs/backlog.md`, voce P11 |

---

## 1. Gli esperimenti e i protocolli, uno per uno

### 1.1 La prova degli ordini limite (13 ottobre)

**Perché è nata.** L'analisi dei trade del paper del 12 ottobre aveva trovato che i costi valevano 0,095 R a trade (67,59
USDT su 508 trade, di cui lo scarto di prezzo il 44%: ops 0607), mentre gli effetti trovati dalla ricerca della prima
edizione valevano 0,04-0,09 R **prima** dei costi (`research/esperimenti/ordini_limite/regole.md`, sez. 1, che cita
`research/confronto/risultati.md`). «Costo per trade con ordini limite» era la prima delle tre ipotesi uscite
dall'analisi del paper (diario 12 ott, 22:00 ora italiana; `docs/analisi_trade_16set_12ott.md`). La domanda: quanto
scende il costo, quanti trade saltano, e il guadagno lordo peggiora (la «selezione avversa»: un limite si riempie più
volentieri quando il prezzo va contro)?

**Cosa cambiava.** Solo l'ingresso. Alla chiusura della barra di segnale si mette un ordine limite al prezzo di chiusura
P, valido una sola barra; si riempie se il prezzo **attraversa** P (non basta toccarlo); commissione maker 0,02% e
scarto zero all'ingresso; uscite a mercato come prima (taker 0,05% più lo scarto della fascia) (`regole.md`, sez. 4).
Tre varianti di sensibilità scritte prima: (a) basta toccare; (b) validità due barre; (c) anche le uscite «a segnale» a
limite (sez. 4.6). Nessuna strategia nuova: nove strategie già provate dalle campagne della prima edizione, scelte prima
(le tre del vault più sei con un effetto lordo caduto ai costi; sez. 3).

| Strategia | Cos'è (dalle regole, sez. 3) |
|---|---|
| BTCUSDT-V10 | rottura dall'apertura del giorno, 1h long (candidata del vault dell'11 ott) |
| BNBUSDT-045 | cali bruschi in tendenza nel fine settimana, 1h long (candidata del vault) |
| ADAUSDT-037 | rottura dell'intervallo d'apertura con due filtri, 15m long (candidata del vault) |
| BTCUSDT-V35, ETCUSDT-033, SOLUSDT-023, AVAXUSDT-V-12 | short nell'ultima mezz'ora del giorno UTC, 30m |
| FILUSDT-016, DYDXUSDT-008 | ritardo della moneta rispetto a BTC, 1h long |

**Periodi.** 2020-01-01 → 2023-12-31, i dati di costruzione e validazione delle campagne; niente vault (sez. 2).

**Soglie scritte prima** (sez. 7), sulle mediane delle nove: E1 eseguibile se il tasso di esecuzione è ≥ 70% (sotto il
50% «non eseguibile»); E2 il costo scende di almeno 0,04 R; E3 il lordo non peggiora più di metà del risparmio. Esiti
possibili: «conviene», «conviene poco» (E2 cade), «non conviene» (E3 cade), «non eseguibile».

**Prima dei numeri, una correzione** (`risultati.md`, sez. 1, correzione 1, 07:48 UTC): la regola diceva di riempire
all'apertura della barra se questa apriva già oltre P; ma un limite già nel libro si esegue **al suo prezzo**. Lasciarla
avrebbe regalato ai trade partiti con un salto favorevole la differenza fra P e l'apertura. Trovata scrivendo i test del
motore, prima di qualunque corsa.

**Controllo di parità.** Prima di tutto si rifanno le corse a mercato e si confrontano con i log delle campagne:
passata 13 volte su 13, entro mezza cifra (`risultati.md`, sez. 4). Il motore della ricerca con l'ingresso «mercato» dà
trade identici bit per bit al motore del commit `39bb60b2` (`research/CHANGELOG.md`, riga del 13 ott).

**Esito: «conviene poco»** (`risultati.md`, sez. 2 e 7, periodo intero, mediane sulle nove):

| Misura | Valore | Soglia |
|---|---|---|
| E1, tasso di esecuzione | 98,0% (da 95,1% ADAUSDT-037 a 99,1% BNBUSDT-045) | ≥ 70% → vale |
| E2, risparmio di costo | 0,0225 R (costo da 0,0619 a 0,0394 R; commissioni da 0,0490 a 0,0345; scarto da 0,0172 a 0,0087) | ≥ 0,04 R → **cade** |
| E3, differenza di lordo L − M | −0,0069 R | ≥ −0,0112 R → vale |

Cosa ha detto in più (stessa fonte, sez. 2.1):

* **I trade che saltano sono i migliori**: 67 saltati su 2.747 (2,4%), con R medio a mercato +0,68 contro +0,06 di tutti;
  il 21% sopra 1 R. In validazione BTCUSDT-V10 ne perde 3 da +2,63 R e il suo R passa da +0,048 a +0,020. La perdita di
  lordo si concentra nelle rotture (BTCUSDT-V10 −0,024 R, ADAUSDT-037 −0,043 R, FILUSDT-016 −0,024 R; sez. 7).
* **Anche il caso risparmia**: le entrate casuali eseguite a limite guadagnano +0,0163 R sulle stesse a mercato; il
  vantaggio sul caso non cambia (8 su 9 «nette» sia a mercato sia a limite sul periodo intero; in validazione 1 su 9 in
  entrambi i modi, ADAUSDT-037). Un limite abbassa i costi, **non crea un vantaggio**.
* **Le uscite a limite non convengono** (variante c): costo 0,0217 R ma lordo da 0,0859 a 0,0477 R.
* Riportato al costo del paper (0,095 R) lo stesso terzo varrebbe circa 0,034 R: **stima per proporzione**, non misura.
* Non fatto: GRUPPO-048 (il ritardo dopo un'ora forte di BTC sulle 80 monete), in coda «se il tempo lo permette», perché
  servivano i dati di 80 monete (sez. 2.3).

**Cosa ne è seguito.** La sera stessa il proprietario ha detto «procedi con tutto» (19:50 ora italiana; diario 13 ott,
20:10): (1) **ricerca automatica del gate fermata** con il file `ops/gate_fermo` (commit `4c315e80`, 17:54 UTC); (2)
**ingressi a limite nel paper** (commit `6d50adfa`, 18:09 UTC): ordine virtuale alla chiusura della candela di segnale,
valido una candela, riempito al suo prezzo se attraversato, maker 0,02%, uscite a mercato; ordini in attesa in RTDB
`/ordini_limite`, contatori e segnali saltati in `/paper/ordini_limite`; interruttore `PAPER_INGRESSO_LIMITE`
(predefinito acceso, `bot/config.py`); 13 test nuovi, 2.305 test del bot passati (messaggio del commit); (3) la bozza del
protocollo 2. Il gate **non** simula l'ordine limite: è fermo. La misura nel paper («fra 3-4 settimane: tasso di
esecuzione, costo per trade, R dei segnali saltati», diario 13 ott) **non risulta ancora fatta**: nei risultati ops fino a
`0623` (le risposte `0622`-`0623` sono arrivate il 18 ott alle 09:03 UTC) non c'è una lettura di `/paper/ordini_limite`.
L'unico numero è indiretto: alla lettura del 16 ottobre circa 80 dei 481 trade del paper erano entrati a limite, e il
confronto fra motore e paper «mescola i due modi d'ingresso» (diario 16 ott, 07:45 ora italiana).

### 1.2 Il protocollo 2 (seconda edizione, versione 5.0) e la campagna PANIERE (13-14 ottobre)

**Perché è nato** (`research/PROTOCOLLO_2.md`, sez. 1). La prima edizione (protocollo 4.5) aveva provato 630 varianti su
20 monete più 30 nel gruppo di 80: 45 candidate in costruzione, 7 in validazione, 3 al vault, 0 passate, contro 0,02
attese per caso (`research/confronto/risultati.md`). Gli effetti veri (ultima mezz'ora del giorno UTC 0,04-0,08 R lordi;
ritardo delle monete dopo un'ora forte di BTC 0,04-0,09 R, t 2,06 contro soglia 2,16) stavano sotto i costi di un giro
a 15 minuti-1 ora (0,05-0,14 R). Gli ordini limite tagliavano i costi solo di un terzo. Il gate passava lo 0,29% delle
prove e le passate facevano −0,06 R a trade (ops 0601 e 0604). La domanda del proprietario del 13 ottobre alle 19:20 ora
italiana era «cosa fare del gate, con che approccio» (diario 13 ott, 20:10; le parole fra virgolette sono in
`docs/backlog.md`, voce P6). Conclusione del testo: l'esame regge,
**cambia il terreno**.

**Cosa cambiava** (sez. 2 del testo):

| Cosa | Prima edizione | Protocollo 2 |
|---|---|---|
| Candela | 15m-1h | **1 giorno UTC** |
| Durata | ore | da 2 a 60 giorni (uscita a tempo a 60 barre) |
| Unità di prova | una moneta per campagna | **il paniere delle 80 monete del gruppo**, una campagna sola |
| Idee | 30 varianti per moneta | **3 idee con fonte, 18 varianti, al massimo 3 ritocchi per famiglia e 12 in tutto** (numeri chiesti dal proprietario) |
| Ingresso | a mercato | **ordine limite** alla chiusura, valido un giorno |
| Periodi | 70/30 per moneta | taglio comune al 2023-01-16 |
| Vault | 2024-01-01 → 2026-09-30, una apertura | lo stesso, già aperto l'11 ottobre: «contaminazione dichiarata», nessuna idea dal vault, una apertura per tutte le candidate |
| Esame finale | paper solo se chiesto | **paper obbligatorio** dopo il vault: 6 mesi o 150 trade, regola scritta prima (sez. 9) |

**Periodi** (sez. 6): costruzione dal primo giorno di ogni moneta (mai prima del 2020-01-01) al 2023-01-16; validazione
2023-01-17 → 2023-12-31; vault 2024-01-01 → 2026-09-30 (marcatore nuovo `APERTURA_2.md`, frase «APRI IL VAULT 2»).

**Soglie.** L'esame di gruppo della campagna GRUPPO: trade sommati delle 80 monete, blocchi di tempo, baseline (a) e
(b), strategie «sfasate», candidato = batte nettamente (a) e (b) con R medio > 0 (sez. 7). Minimi di trade sommati
**700 in costruzione, 300 in validazione, 300 nel vault** (correzione 1 del 13 ott, 20:40 UTC: il testo diceva per errore
300/100/300). Vault: profit factor ≥ 1,10, almeno 300 trade, R sopra il 90° percentile delle sfasate (sez. 8).

**Le tre idee** (sez. 5): **A** tendenza (Moskowitz, Ooi e Pedersen 2012; Hurst, Ooi e Pedersen 2017; Liu e Tsyvinski
2021): rottura dei massimi/minimi a 20 e 55 giorni, segno del rendimento a 60 giorni con la media a 100; **B** momentum
fra monete (Liu, Tsyvinski e Wu 2022; Jegadeesh e Titman 1993): long le prime 10 (o 20) per rendimento a 4 o 2
settimane, short le ultime; **C** ritardo delle monete dopo un giorno forte di Bitcoin (Ciaian, Rajcaniova e Kancs 2018,
più il risultato della campagna GRUPPO): dopo un giorno di BTC oltre k deviazioni standard (k 1,5 o 2), long le monete
rimaste indietro (tutte, C1, o le 20 più indietro, C2), uscita dopo 5 giorni. Stop 2,5 ATR(20) giornalieri per tutte. La
terza idea l'ha chiesta il proprietario all'approvazione (sez. 13).

**Il Passo 0 (13 ottobre sera, `research/passo0_2/rapporto.md`).**

* Dati: 245 serie giornaliere, 0 errori, 9.406 file con impronta (`research/campagne/PANIERE/impronte_1d.json`).
* Motore a 1 giorno: la stessa strategia a 1d e a 8h dà gli stessi trade (24 long, 16 short su BTC), funding diverso di
  −0,0003 e +0,0007 R a trade → si usano barre di 1 giorno (soglia 0,005 R, sez. 3.4 del testo).
* **Lo stop a 2,5 ATR(20) è il 22,2% del prezzo in mediana** (da 13,3% a 27,8% sulle 80 monete; BTC 11,8%). Il testo
  aveva stimato 6-12% (sez. 3.2): la stima era sbagliata di 2-3 volte. Costo per trade 0,0068 R in mediana (0,0043-0,0113).
* **Il funding pesa**: un long su BTC tenuto 25 giorni nel 2020-2023 ha pagato in media 0,23 R di funding (24 trade).
* La prova a placebo a 1 giorno (strategie da manuale con gli ingressi spostati, sugli stessi prezzi veri; sezione 2.1
  di questa bozza) regge, dopo due correzioni scritte prima degli esiti: parametri più corti per il giorno (a 1 ora
  davano 227-420 trade, sotto 700) e un tetto di 60 barre alle posizioni (senza, duravano centinaia di giorni).
* Il **controllo positivo** (una strategia che guarda avanti, deve passare) **non passa** nella forma del gruppo: la (b)
  non si costruisce su 13-16 monete dalla storia corta, e con 7 blocchi anche +0,3 R a trade non è «netto» (t 2,42
  contro soglia 2,6).
* STOP con quattro domande; risposta «procedi» il 14 ottobre verso le 05:00 UTC (rapporto, ultima sezione): parametri
  congelati (`research/config/parametri_2.yaml`), esame com'è (ogni variante riportata con t e blocchi), la regola delle
  monete su cui la (b) non entra (fuori dal confronto, non valutabile solo se portano più del 10% dei trade; commit
  `c9bb86ad`), funding «da ricordare».

**La campagna (14 ottobre).** Sessione `session_01R2mwB6hCHhcKeRgNM7Zuad`, aperta alle 06:58 UTC (diario 14 ott, 09:00
ora italiana); ultracode non risultava attivo. Tre fermate prima della prima variante, tutte per mancanze del
coordinamento (sezione 4 di questa bozza): il guardiano le negava le regole del gruppo (07:13 UTC), poi lo strumento per
leggere le notifiche (07:52), poi gli strumenti non passavano alla variante il paniere e non entravano a limite (08:42 e
09:14). Correzione 5 (commit `08e2c95a`, 09:47), placebo rifatto una terza volta (09:54-11:40), ripartenza alle 12:01,
consegna alle 14:12 (commit `70d17c85` sul branch). Misure di processo: 6,97 ore dalla prima all'ultima voce, 4,69 di
pause, 2,28 di lavoro; 5 rifiuti del guardiano (`consegna.md` del branch, ultima sezione). Il log ha 151 voci: 61
registrazioni, 60 risultati, 21 note, 8 scarti, 1 correzione (calcolo mio su `log.jsonl` del branch; il diario dice lo
stesso).

**Esito: «nessuna strategia valida trovata per il paniere»**, dopo tutto il budget (18 varianti e 12 ritocchi):

| Idea | Varianti esaminate | Scarti (sotto 700 trade) | Miglior t contro (b) | Esito |
|---|---|---|---|---|
| A, tendenza | 4 | 2 (rottura a 55 giorni, long e short) | 1,00 (A1-20 long, 7 blocchi) | morta a questo orizzonte |
| B, momentum fra monete | 3 | 3 | 0,46 | morta |
| C, ritardo dopo BTC | 4 + 11 ritocchi | 2 + 1 ritocco | 3,24 (PANIERE-040) | due candidati, caduti in Fase 4 |

Fonte: `research/campagne/PANIERE/consegna.md` sul branch `research/campagna/PANIERE` (commit `70d17c85`).

I due candidati, tutti e due long dopo un giorno forte di BTC oltre 1,25 deviazioni, uscita dopo 3 giorni: PANIERE-040
(le 20 monete più indietro: 1.363 trade, +0,130 R, t 3,24 contro la (b), 25 blocchi) e PANIERE-043 (tutte le monete
indietro: 2.327 trade, +0,135 R, t 3,20, 16 blocchi). Sono **caduti** su due verifiche della Fase 4: il **ritardo di una
barra** (t a 0,49 e 0,34 volte: parte del recupero arriva il giorno stesso dell'ingresso) e la **liquidazione** (6 e 8
violazioni: lo stop a 2,5 ATR giornalieri dopo i crolli arriva al 79-95% del prezzo, oltre 0,8 volte la distanza di
liquidazione). La seconda è un limite del terreno, non dell'idea (stessa fonte). Lo stop dei candidati (22% del prezzo)
era comunque oltre il tetto del 6% del bot: il bot non li avrebbe potuti eseguire (stessa fonte, «Rischi e limiti»).

**Cosa non è stato fatto.** Nessuna validazione, nessun vault («APRI IL VAULT 2» mai scritto), nessun paper. Le lezioni
della campagna (`lezioni_metodo_proposte.md` e `lezioni_moneta.md`) **restano solo sul branch**: il backlog dice «da qui
decide il proprietario: unire le lezioni (Passo 7)» (`docs/backlog.md`, voce P6) e non ho trovato un commit che le unisca
al principale (la cartella `research/campagne/PANIERE/` del principale ha solo dati, schede e regole). `CLAUDE.md` dice
che la seconda edizione «è chiusa».

### 1.3 Il protocollo 3 (versione 5.1 su BTC) e la campagna BTC51 (16-17 ottobre)

**Perché è nato.** Non da una lezione scritta del paniere: è il testo del proprietario. Il 16 ottobre mattina ha
caricato un «Protocollo di ricerca strategie su BTC, versione 5.1» (una moneta, catalogo chiuso di indicatori, 40
varianti, ingressi a mercato o limit sotto la chiusura) e ha detto l'obiettivo: «rifare il gate per avere prima di tutto
un METODO efficace, valido e senza buchi di processo, provato su BTC, e poi replicarlo sulle altre monete» (diario 16
ott, mattina). La versione 5 da cui deriva non è nel repository (l'appendice 1 elenca solo le differenze). Lo stesso
giorno la lettura ufficiale del fuori campione aveva confermato «la prossima modifica va nel gate» (diario 16 ott, 07:45
ora italiana). Il testo **non cita** la campagna PANIERE (ricerca di «PANIERE» e «seconda edizione» in
`research/PROTOCOLLO_3.md`: nessun risultato).

**Cosa cambiava** (rispetto ai protocolli 1 e 2):

* **Una sola moneta**, BTCUSDT; **catalogo chiuso**: 16 indicatori con valori ammessi, 12 segnali d'ingresso (E1-E12), 7
  filtri (F1-F7), 3 conferme (C1-C3), 3 stop (S1-S3), 5 uscite (U1-U4, U2s), ingresso a mercato (M) o limit (L, a 0,25 o
  0,5 ATR oltre la chiusura, validità 1 o 3 candele); al massimo 3 condizioni (`PROTOCOLLO_3.md`, sez. 7).
* **40 varianti**, il numero più alto con meno di un falso candidato atteso (40 × 2,3% ≈ 0,9; sez. 8.3).
* **Vantaggio minimo 0,2 R dopo i costi** (con stop all'1% i costi valgono circa 0,12 R; sez. 5.1, 6).
* Confronto con **1.000 entrate casuali** (seme 2026), stesso tipo d'ingresso; p ≤ 0,023 in costruzione (sez. 10).
* **Validazione come filtro, senza p-value**; la significatività si giudica una volta sola nel vault, con Benjamini-Hochberg
  al 10% (sez. 10.3-10.4).
* 11 verifiche della Fase 4 (robustezza ±20%, timeframe vicini, 4 blocchi di tempo, senza il 5% dei trade migliori, costi
  doppi, troncamento, liquidazione, riempimento severo, e tre informative).
* Passo 6 sulle 9 monete con più volume nel 2023 (si trasferisce se regge su 3); Passo 8 paper con 40 trade.
* Aggiunte del coordinamento (appendice 2): **il collaudo del metodo** (sezione 2 di questa bozza), il paper come esame
  finale, chi esegue cosa (Passo 0 e 5-8 il coordinamento sul principale, Passi 1-4 una sessione di ricerca sul branch
  `research/campagna/BTC51` con il guardiano), le entrate casuali scelte fra **tutte** le candele (non solo quelle libere
  dal candidato), il vault con la frase «APRI IL VAULT 3».

**Periodi** (sez. 4): costruzione dal 2020-01-01 al 2022-09-30; validazione 2022-10-01 → 2023-12-31; vault 2024-01-01 →
2026-09-30. Il testo pensava a una costruzione da settembre 2019 (36,5 mesi, per avere circa 154 trade alla frequenza
minima); l'archivio pubblico di Binance parte dal 2020-01-01, quindi la costruzione dura 33 mesi (diario 16 ott, sera;
`fase0_dati.md` del branch BTC51, sez. 1-2). **Minimi di trade**: 150 costruzione, 60 validazione, 100 vault (sez. 5.2).

**Fatti del bot al Passo 0** (`research/config/bot_3.md`): in paper lo stop scatta se lo tocca il last o il mark; leva di
base 2, rischio 1%, stop più largo ammesso 6%; il bot **non sa eseguire nessuna variante del catalogo** come la scrive il
protocollo; il suo ordine limite in paper è al prezzo di chiusura (k = 0), diverso dal limit del catalogo. Scelta del
proprietario: tutto il catalogo, con le aggiunte al bot prima del paper (sez. 7.10, scelta «b»).

**Strumenti nuovi** (`research/CHANGELOG.md`, 16 ott): `catalogo3.py`, `motore3.py`, `statistica3.py`. Tre verificatori
indipendenti hanno scritto i test dal testo del protocollo: 381 (catalogo), 53 (motore), 117 (statistiche) secondo il
CHANGELOG, 551 in tutto secondo il diario; il messaggio del commit `dd2ef133` dice 115 test delle statistiche. Hanno
trovato 4 difetti, corretti prima del collaudo (sezione 4).

**La ricerca (17 ottobre).** Sessione `session_01M5hqfZnxRHH4mdN89emaQU`, aperta alle 07:19 UTC con il messaggio
`research/apertura/btc51.md`; ultracode non risultava attivo, detto al proprietario (diario 17 ott, mattina). Branch
creato senza i file delle ricerche passate (460 file invece di circa 3.000) e con un `CLAUDE.md` pulito (commit
`fc24e7e9`). Al Passo 1 la sessione ha trovato due difetti degli strumenti (sezione 4), corretti dal coordinamento con il
collaudo rifatto. Passo 2:

* **Primo lotto**, 19 varianti su 8 idee (V-001…V-019): nessuna oltre la Fase 2. Le tre più vicine: V-011 (short con
  funding alto), V-012 (long con funding sotto zero), V-018 (rottura dopo la calma) (`ipotesi.md` del branch, «Fase 3
  dopo il primo lotto»).
* **V-020**, nata dall'analisi dei trade di V-012: «nei feriali +0,278 R su 169 trade, nel fine settimana −0,134 su 59»
  → V-012 solo nei giorni feriali. 180 trade, +0,223 R, p 0,017: supera la Fase 2 e la Fase 4, ma senza il 5% dei trade
  migliori (9) resta a +0,012 R (`consegna.md` del branch, sez. 4).
* Altre 3 varianti (V-021…V-023) e la Fase 5: a 23 varianti **la sessione voleva fermarsi** («I 17 tentativi che
  restano non li uso: ogni variante in più aggiunge circa il 2,3% di probabilità di un falso candidato»; `ipotesi.md`,
  «Fase 5 — sfida alla conclusione»). **Il proprietario ha chiesto di usarli tutti**: seconda tornata V-024…V-040 su 9
  idee nuove; una sola, V-030 (tendenza nella calma, 30 minuti), ha superato la Fase 2 ed è caduta nella Fase 4
  (timeframe vicini −0,000 e −0,053 R, il 70% della somma in un blocco, −0,117 R senza i trade migliori).
* Totale: 40 su 40; 22 con R medio positivo, 16 con p ≤ 0,10, 2 oltre la Fase 2, 1 candidato (`research/campagne/BTC51/
  lezioni.md`, tabella iniziale). La sessione stessa ha scritto: «Avere un solo candidato è esattamente quello che darebbe
  il caso» (`ipotesi.md`, «Fase 5, seconda volta»).

**Validazione** (via libera alle 13:39 UTC; esecuzione unica alle 13:49; `validazione.md` del branch): V-020 fa 80 trade,
+0,167 R, profit factor 1,29, +0,064 R a costi doppi: **supera** tutte le condizioni. Ma +0,167 R su 80 trade sta a circa
1,2 errori standard da zero, e il 2023 da solo fa +0,112 R (stessa fonte, sez. 5). La previsione scritta prima della
validazione era sbagliata (diceva fra −0,1 e +0,15 R).

**Consegna** (commit `1b222fb5`, 15:44 UTC): previsione per il vault scritta prima: circa 175 trade (110-230), +0,08 R
(da −0,10 a +0,20), probabilità di superarlo **circa 1 su 4** (inferito) (`consegna.md` del branch, sez. 6). Il bot non sa
eseguire V-020 (mancano funding regolato come segnale, filtro sui giorni, uscita a tempo per strategia, orologio da 1 ora;
sez. 7).

**Vault** (`research/vault/APERTURA_3.md`, `BTC51_risultati.md`). Il proprietario ha scritto «APRI IL VAULT 3» nella
sessione di ricerca (note del log alle 16:21 e 16:22 UTC), e al coordinamento «ho aperto direttamente io il vault nella
campagna» (18:17 ora italiana). Il coordinamento ha controllato le impronte (candidato 4 su 4, strumenti 9 su 9), rifatto
costruzione e validazione con lo stesso programma (stessi numeri), aperto il vault alle 16:23 UTC ed eseguito V-020 una
volta sola alle 16:24:53. La frase esatta è arrivata al coordinamento solo alle 16:36 UTC, a vault già aperto («conferma
l'apertura, non apre un secondo giro»).

| | Costruzione | Validazione | **Vault** |
|---|---|---|---|
| Trade | 180 | 80 | 180 |
| R medio | +0,223 | +0,167 | **−0,007** |
| Profit factor | 1,46 | 1,29 | 0,99 |
| A costi doppi | +0,147 | +0,064 | −0,104 |
| p contro il caso | 0,017 | — | 0,337 |
| Senza i 9 trade migliori | +0,012 | — | −0,220 |

Fonte: `research/vault/BTC51_risultati.md`, «Metriche affiancate». Supera solo il minimo di 100 trade e **non supera** le
altre quattro condizioni. Il 2024
era ancora buono (33 trade, +10,9 R); il primo semestre del 2026 ha dato 80 trade a −0,166 R, con il funding sotto zero
nel 38% dei regolamenti (massimo di tutto il 2020-2026) e BTC a −33%. Già in costruzione il semestre peggiore era un
ribasso forte con molto funding negativo (2022H1: 65 trade a +0,040 R, BTC −57%). Lettura del coordinamento (inferita):
nei ribassi lunghi il funding negativo misura la tendenza, non una folla di short da spremere. La previsione aveva i trade
giusti (180 contro 175) e l'R dentro l'intervallo, sotto il centro.

**Prova su altre monete** (`research/altre_monete_3/risultati.md`, esecuzione unica alle 17:07 UTC): le 9 monete con più
volume nel 2023 (ETH, SOL, XRP, DOGE, APT, BNB, LTC, MATIC delistata, BCH). V-020 **regge solo su LTC** (242 trade, +0,062
R, p 0,020); perde sulle altre 7 con il periodo intero (da −0,018 a −0,120 R) e su MATIC (−0,333 su 35 trade). Servivano 3
monete: **non si trasferisce**. Il 2024 è positivo su 7 monete su 8, il 2026 negativo su 6 su 8, con correlazioni basse
(media 0,26): lettura «il mercato è cambiato», inferita.

**Chiusura** (commit `09795c2d`, 17:30 UTC): `research/campagne/BTC51/lezioni.md` con 20 idee, nove errori di metodo,
cinque trappole dei dati, otto proposte (sezione 6 di questa bozza). La prova di parità col bot (prova C) non è mai
partita.

### 1.4 Il protocollo 4 (versione 6 su LINK) e la campagna LINK6 (17-18 ottobre)

**Perché è nato.** Dalle otto proposte di BTC51 (`research/campagne/BTC51/lezioni.md`, sez. 5), prima di tutte «provare
l'idea sulle altre monete prima del vault, sul periodo già usato». Il proprietario ha detto «ok sì, scrivi la bozza del
prossimo protocollo». Prima bozza alle 18:04 UTC (commit `6c377aa6`); un **revisore indipendente** ha trovato 25 punti,
tre bloccanti per fughe di informazione sul vault, più uno: LINK era già stato esplorato dal protocollo 1 (30 varianti,
nessun candidato, vault mai aperto) e il testo non lo diceva (`research/protocollo_4_note.md`, sez. 3). Bozza corretta
alle 18:26 (commit `8153a333`), **approvata alle 20:12 UTC** con tutte le proposte (sez. 0-1 delle note). Alle 21:10 UTC
circa il proprietario ha **delegato** il seguito: «procedi in autonimia con gli altri passi non mi chiedere il permesso»,
tranne il vault (note, sez. 0).

**Cosa cambiava rispetto al protocollo 3** (`research/protocollo_4_note.md`, sez. 2, sedici punti; i principali):

* **Ricerca su LINKUSDT** (la moneta più scambiata nel 2023 fra quelle con dati dal 2020 e vault mai aperto: 319 milioni
  di USDT al giorno; note, D1), con **9 monete di controllo** (BTC, ETH, SOL, XRP, DOGE, BNB, LTC, MATIC, BCH: quelle
  con il vault già aperto; `PROTOCOLLO_4.md`, sez. 4bis). La sessione di ricerca non ne vede i dati né i numeri: chiede
  al coordinamento e riceve «supera» o «non supera» (regola 10).
* **Verifica 12** della Fase 4: la variante deve battere le proprie entrate casuali su almeno 7 monete di controllo su 9,
  con media positiva dopo i costi. **Validazione** anche sulle monete di controllo (vantaggio medio sul caso ≥ 0,1 R).
* Una variante **«nata dalla Fase 3»** si riconosce dal log (un solo elemento cambiato, non scritto prima) e deve
  migliorare di almeno 0,05 R la media sulle monete di controllo, se no è scartata e consuma il tentativo.
* **Verifica 4 nuova**: senza il 5% dei trade migliori (tolti anche alle entrate casuali) il vantaggio sul caso deve
  restare almeno a metà. **Verifica 3bis**: semestri di forte rialzo e forte ribasso (±30%). **Robustezza** con un passo
  fisso quando il ±20% non sposta il valore (soglie a zero).
* **Stesse versioni di Python e numpy** del collaudo, controllate all'avvio della ricerca (regola 11).
* **Niente fatti dal 2024** nei file che la ricerca legge; elenco esatto dei file ammessi; branch con **storia propria**
  e `CLAUDE.md` pulito (sez. 3 e 12).
* La frase del vault («APRI IL VAULT 4») vale **solo nella sessione del coordinamento** (sez. 0); il caricatore riconosce
  solo `APERTURA_4.md` (prima `APERTURA_3.md` avrebbe aperto il vault di qualunque moneta).
* Passo 6 sulle monete di controllo invece che su 9 vault nuovi.

**Periodi** (sez. 4): costruzione dal 2020-01-17 08:00 (prima candela oraria di LINKUSDT) al 2022-09-30, circa 32,5 mesi;
validazione 2022-10-01 → 2023-12-31; vault 2024-01-01 → 2026-09-30. Minimi 150/60/100; frequenza minima circa 4,6 trade
al mese; costi circa 0,14 R con stop all'1% (slippage di LINK 0,02% per lato) (sez. 5-6; `research/config/
parametri_4.yaml`).

**Passo 0** (17 ottobre sera): strumenti nuovi (`statistica4.py`, `controllo4.py`, caricatore e guardiano per LINK6;
suite della ricerca 3.149 test passati: `research/CHANGELOG.md`, riga del 17 ott, protocollo 4); dati delle monete di
controllo (9.120 file attesi, 8.664 presenti, 0 errori, 0 CHECKSUM mancanti; mancano i primi mesi di SOL, DOGE, BNB e
MATIC, quotate dopo gennaio 2020: `research/passo0_4/scarico.json`); versioni lette da una sessione di prova (Python
3.13.16, numpy 2.5.3, scipy 1.18.1: `collaudo_4/esiti.md`); collaudo passato al primo giro (sezione 2); branch della
ricerca con storia propria (commit `8e9147ef`, 644 test su 644: diario 17 ott, notte).

**La ricerca.** Sessione `session_01U9dN6txp5poepfrCk4btAp`, aperta alle 21:58 UTC direttamente sul branch LINK6
(`STATO.md`). Passo 1 alle 22:24 UTC (912 file con il CHECKSUM, impronte uguali al Passo 0; log N-002). Il coordinamento
lo ha confermato per delega alle 22:38, ma **la sessione non ha preso per buono un messaggio automatico «a nome del
proprietario»** e ha aspettato lui: 8 ore (log N-003, N-004). Poi:

* **Prima tornata** (06:42-06:56 UTC): 13 idee, 26 varianti con la Fase 2, nessuna oltre. La migliore, V-004 (long con
  funding sotto zero, 1h), +0,128 R, p 0,047. La sua modifica V-019 (uscita dopo 48 ore invece di 24) è stata **fermata
  dal controllo sulle monete di controllo**: +0,010 R di media in più, contro 0,05 richiesti (richiesta R-001 eseguita alle
  07:10; `research/monete_di_controllo_4/R-001.json`). STOP a 27 su 40 (log N-009, 07:24): la sessione proponeva di
  fermarsi.
* Il coordinamento, per delega, alle 07:36 le ha chiesto di usare i 13 tentativi rimasti **solo** con idee con un perché
  e una fonte precedente al 2024 (note, sez. 5). Il messaggio delle 07:38 risultava consegnato ma la sessione è ripartita
  solo dopo il secondo invio delle 07:43 (lezioni LINK6, sez. 2, punto 5).
* **Seconda tornata** (07:51-07:54): 3 idee nuove, 6 varianti, nessuna oltre la Fase 2. La sessione si è fermata a **33 su
  40** perché le combinazioni rimaste «sarebbero state ritagli di idee già provate o modifiche suggerite dai risultati»
  (diario 18 ott, mattina; con altre parole in `fase5.md`, «Perché mi fermo a 33 su 40»).
* STOP confermato per delega alle 08:01 UTC (note, sez. 5; il log della sessione dice «routine delle 08:03», N-012).
  Passo 3 vuoto, Passo 4 «nessuna strategia valida trovata» (commit `bb8b444d`, 08:14), Passo 9 dal coordinamento (commit
  `f85a233a`, 08:30). **Il vault di LINK non è stato aperto, e nemmeno il periodo di validazione è stato caricato**
  (`validazione.md`).

**Esito**: 16 idee, 33 varianti su 40, nessuna oltre la Fase 2. In media le 32 varianti fanno quanto le loro entrate
casuali (−0,030 R contro −0,032; 16 su 32 le battono; p-value medio 0,478; prova di uniformità p 0,416)
(`research/campagne/LINK6/lezioni.md`, sez. 1; ricontrollato da me sul log: stessi numeri). Il Passo 2 ha richiesto circa
17 minuti di lavoro della sessione (lezioni, sez. 2, punto 1).

**Cosa è successo dopo.** Il 18 ottobre verso le 08:40 UTC il proprietario: «la domanda non è se vuoi continuare e
dobbiamo continuare fino a quando non trovi delle strategie valide... se serve riscriviamo totalmente il gate non mi
interessa (prima però voglio che tu storicizzi tutti i dati raccolti...)» (`docs/backlog.md`, voce P11). È il motivo di
questa storia.

---

## 2. Il collaudo del metodo (protocolli 3 e 4)

### 2.1 Cosa prova

Il collaudo prova **la bilancia, non BTC né LINK** (`PROTOCOLLO_3.md`, sez. 13bis; `PROTOCOLLO_4.md`, sez. 13bis). Si
fa prima della ricerca, non consuma varianti, non usa dati di validazione o del vault. Se una prova non passa, la ricerca
non comincia. Tre prove:

* **Prova A, «la bilancia vuota deve segnare zero».** Serie di prezzi **senza direzione** costruite dalle candele vere
  della costruzione: dal secondo giro, ogni candela si gira o no a caso, alla pari, e la volatilità resta al suo posto.
  Su queste serie nessuna regola può avere un vantaggio vero. Si estraggono a caso dal catalogo varianti finte finché
  100 arrivano alla Fase 2. Passa se al massimo 5 superano la Fase 2 (attese 2,3) e al massimo 15 hanno p < 0,10
  (attese 10).
* **Prova B, «il peso noto deve essere pesato».** Tre regole d'esempio (B1 MACD long a mercato, B2 la stessa short, B3
  la stessa long con limit) sulle 30 serie senza direzione a 1 ora, con un vantaggio inserito apposta di ampiezza P
  dopo ogni segnale (e restituito lentamente in 240 candele, così il caso non ne guadagna). Passa se senza vantaggio al
  massimo 3 serie su 30 superano la Fase 2, e con almeno 0,35 R netti almeno l'80% la supera.
* **Prova C, «laboratorio e negozio devono dare lo stesso peso».** La stessa strategia nel motore e nel bot, sugli
  stessi 12 mesi: segnali identici al 100%, trade identici al 98%. **Mai eseguita**: il bot non sa eseguire il catalogo, e
  il proprietario ha deciso (17 ott) di farla solo se un candidato supera il vault (appendice 3, punto 4).
* Solo nel protocollo 4, **la verifica sulle monete di controllo**: con le varianti finte (quante battono il caso su 7
  monete su 9: attese circa 9 su 100, STOP oltre 17) e con il vantaggio inserito (deve passare almeno 8 prove su 10).

**Il precedente nel protocollo 2.** Lo stesso ruolo l'avevano la **prova a placebo** (strategie da manuale con gli
ingressi spostati tutti dello stesso intervallo, sui prezzi veri: devono risultare «nette» al massimo il 3% delle volte)
e il **controllo positivo** (una strategia che guarda il giorno dopo: deve passare) (`research/taratura/placebo_paniere/
regole.md`). Tre lanci: 13 ottobre (dopo due correzioni), 14 ottobre mattina (identico bit per bit, regola del 10%), 14
ottobre 09:54-11:40 con l'ordine limite: 46 valutabili in costruzione e 47 in validazione, 0 «nette» su 46, 0 con p <
0,10 su 47 (`research/taratura/placebo_paniere/risultati.md`). Il controllo positivo invece non è mai passato nella forma
piena: con l'ordine limite il long senza ritardo batte la (b) (t 2,54, p 0,022) ma non la (a) (t 1,48 con 7 blocchi), lo
short resta non valutabile (16 monete senza (b), 13,3% dei trade) (`research/passo0_2/rapporto.md`, «La correzione
5»). Il diario chiama la placebo «prova sui prezzi mescolati»: non è esatto, i prezzi erano quelli veri.

### 2.2 I giri del protocollo 3

| Giro | Quando (UTC) | Perché si è rifatto | Prova A: oltre la Fase 2 / p < 0,10 | Prova B | Esito |
|---|---|---|---|---|---|
| 1 | 16 ott 21:01-21:10 | primo | 0 su 100 / **21** (soglia 15) | B1 e B3 passano; B2 non valutabile (nessuna prova arriva a 0,35 R) | **non passa** |
| 2 | 17 ott 06:28-06:49 | tre correzioni del metodo approvate alle 06:11 | 0 / 13 | passa: 114 su 114 con almeno 0,2 R netti, 0 su 90 senza vantaggio | passa |
| 3 | 17 ott 07:49-08:16 | caricatore corretto (buchi del solo mark) | 0 / 11 | passa: 104 su 104 con almeno 0,2 R | passa |
| 4 | 17 ott 09:13-09:39 | pareggi del p-value corretti; versioni della macchina di ricerca (Python 3.13.16, numpy 2.5.3) | 0 / 11 | passa: 104 su 104, 0 su 90 | **passa**; impronte che valgono per la ricerca |

Fonte: `research/collaudo_3/esiti.md` (tabella iniziale e sezioni per giro). Nel quarto giro: 473 varianti estratte per
averne 100, p-value per decimi 11, 10, 15, 12, 5, 9, 9, 15, 7, 7; R medio delle varianti −0,071 contro −0,081 delle loro
entrate casuali. Nella prova B le entrate casuali non guadagnano dal vantaggio inserito (−0,004 / +0,003 / −0,032 R,
terzo giro). Per B3 (limit a 0,25 ATR) gli ordini eseguiti erano il 55% (giro 1) e il 63% (giro 2): con il limit sotto la
chiusura un ordine su tre o quattro non si riempie, mentre con il limit **alla** chiusura della prova del 13 ottobre si
riempiva il 98%.

**Il difetto trovato dal primo giro** (`collaudo_3/esiti.md`, «La causa del difetto»): sui prezzi rimescolati le varianti
battevano il caso in media di 0,027 R a trade. La causa non era un errore che guarda il futuro né la tendenza di fondo, ma
**la larghezza dello stop**: le varianti entravano quando lo stop era largo (dopo candele grandi, soprattutto con lo stop al
minimo delle ultime candele e con il volume anomalo), pagando meno costi e meno regole prudenti per ogni R; le entrate
casuali entravano con stop di larghezza media. Tre correzioni (approvate dal proprietario il 17 ottobre alle 06:11 UTC,
`PROTOCOLLO_3.md`, appendice 3): (1) entrate casuali con la **stessa distribuzione di larghezza dello stop** del candidato
(5 fasce); (2) serie senza vantaggio con **la direzione di ogni candela girata a caso** invece dell'ordine mescolato (il
mescolamento toglieva il legame fra volatilità passata e futura); (3) ampiezze del vantaggio inserito 0 / 0,6 / 1,2
invece di 0 / 0,3 / 0,6 (il vantaggio inserito rende circa un terzo di P). Con le correzioni 1 e 2 la diagnosi dava 12 su
100 (soglia 15).

Un caso limite: nella prova A la variante finta 309 (15 minuti, 602 trade) non ha trovato entrate casuali possibili alla
stessa larghezza di stop in 4 milioni di giri: sostituita; nella ricerca lo stesso caso sarebbe uno STOP con domanda
(`collaudo_3/esiti.md`, terzo giro).

### 2.3 Il giro del protocollo 4

Un solo giro, il 17 ottobre dalle 20:49 alle 21:54 UTC, con Python 3.13.16, numpy 2.5.3 e scipy 1.18.1, **passato senza
correzioni** (`research/collaudo_4/esiti.md`):

| Prova | Soglia | Esito |
|---|---|---|
| A, oltre la Fase 2 | ≤ 5 su 100 | 0 su 100 |
| A, p < 0,10 | ≤ 15 su 100 | 14 su 100 |
| A, battono il caso su ≥ 7 monete di controllo su 9 | STOP oltre 17 | 12 su 100 (1 supera la verifica 12 intera, ma non la Fase 2) |
| B1 / B2 / B3 senza vantaggio | ≤ 3 su 30 | 0 / 0 / 0 |
| B1 / B2 / B3 con almeno 0,35 R | ≥ 80% | 29 su 29 / 29 su 29 / 30 su 30 |
| B.6, verifica 12 con vantaggio P = 1,2 | ≥ 8 su 10 | B1 10 su 10, B2 10 su 10 (anche con P = 0,6) |
| C | dopo il vault | non eseguita |

Un'informazione emersa qui pesa su tutta la campagna: su LINK, con 32,5 mesi di costruzione, **400 varianti finte su 501
non arrivano a 150 trade**, e fra le 100 che ci arrivano 87 sono a 15 minuti, 30 minuti o 1 ora e solo 3 a 4 ore o più
(`collaudo_4/esiti.md`; lezioni LINK6, sez. 5, punto 3). Le strategie lente, dove i costi pesano meno, non arrivano ai
minimi.

### 2.4 Cosa il collaudo non prova

* La **parità col bot** (prova C) non è mai stata fatta, in nessuno dei due protocolli.
* Le serie senza direzione di monete diverse sono **indipendenti**, mentre le monete vere si muovono insieme: con le monete
  vere la verifica 12 filtra un po' meno di quanto misurato (`collaudo_4/esiti.md`, «Cose da sapere», punto 4).
* Il collaudo prova gli strumenti, **non i comandi della guida pratica sotto il guardiano**: la guida faceva leggere le
  versioni con `python3 -c`, che il guardiano rifiuta (lezioni LINK6, sez. 2, punto 3).
* Il collaudo dice che la bilancia vede i vantaggi inseriti da 0,2 R netti in su (104 su 104 nel quarto giro del
  protocollo 3), costruiti in un modo preciso (uno spostamento del prezzo dopo ogni segnale, su tre regole d'esempio);
  non dice niente su vantaggi sotto 0,2 R o di forma diversa, né sulle regole di validazione e vault, che sui prezzi senza
  direzione non si esercitano.

---

## 3. Tutte le idee e le varianti, per famiglia

Il raggruppamento è mio: le lezioni di LINK6 mettono per esempio VWAP, ore americane e compressione dentro «tendenza»
(`research/campagne/LINK6/lezioni.md`, sez. 1). Per BTC51 e LINK6 ogni riga viene dalle voci `registrazione` e
`risultato` del log (BTC51: `log.jsonl` sul branch `research/campagna/BTC51`; LINK6: `research/campagne/LINK6/log.jsonl`
e `consegna.md`); tutto sul periodo di costruzione. Colonne: trade, R medio dopo i costi, R medio delle entrate casuali
(«caso»), p-value. Soglia della Fase 2: almeno 150 trade, R ≥ 0,2, p ≤ 0,023. Per PANIERE: trade sommati sulle 80 monete,
R medio, t contro la (b) / soglia, blocchi (`consegna.md` del branch PANIERE).

### 3.1 Tendenza (rotture di canali, medie mobili, MACD, RSI che passa 50, ADX)

| Campagna | Variante, in parole | tf, verso | Trade | R | Caso | p (o t/soglia) | Esito |
|---|---|---|---|---|---|---|---|
| PANIERE | 016 A1-20: rottura del massimo di 20 giorni | 1d long | 727 | +0,477 (senza i 30 migliori −0,069) | — | t 1,00 / 2,52, 7 blocchi | no |
| PANIERE | 017 A1-20 | 1d short | 789 | +0,006 | — | 0,01 / 2,87 | no |
| PANIERE | 018-019 A1-55: rottura a 55 giorni | 1d long/short | 385, 382 stimati | — | — | — | scarti (< 700) |
| PANIERE | 020 A2: rendimento a 60 giorni positivo e sopra la media a 100 | 1d long | 1.283 | +0,096 | — | 0,21 / 3,31, 4 blocchi | no |
| PANIERE | 021 A2 | 1d short | 1.633 | −0,056 | — | −0,51 / 2,87 | no |
| BTC51 | V-001 rottura di 55 candele, trailing | 1h long | 237 | +0,069 | +0,010 | 0,252 | no |
| BTC51 | V-002 | 1h short | 194 | −0,051 | −0,092 | 0,303 | no |
| BTC51 | V-003 rottura di 20 candele, trailing | 2h long | 199 | +0,161 | +0,109 | 0,246 | no |
| BTC51 | V-004 | 2h short | 176 | −0,060 | −0,066 | 0,457 | no |
| BTC51 | V-005 chiusura che incrocia la EMA 50, uscita al segnale opposto | 4h long | 201 | +0,161 | +0,174 | 0,704 | no |
| BTC51 | V-006 | 4h short | 200 | +0,031 | −0,056 | **0,004** | no (R piccolo) |
| BTC51 | V-007 incrocio EMA 20/50, stop 3 ATR, uscita al segnale opposto | 1h long | 214 | +0,234 | +0,147 | 0,106 | no |
| BTC51 | V-021 MACD sopra la EMA 200, trailing | 2h long | 157 | +0,050 | +0,077 | 0,606 | no |
| BTC51 | V-022 MACD sotto la EMA 200 | 2h short | 165 | −0,081 | −0,043 | 0,678 | no |
| BTC51 | V-028 rottura di 20 con ADX > 25 | 1h long | 230 | −0,026 | −0,001 | 0,609 | no |
| BTC51 | V-029 | 1h short | 214 | +0,024 | −0,096 | 0,064 | no |
| BTC51 | V-030 rottura di 55 con volatilità bassa (ATR percentile < 30°), trailing | 30m long | 180 | +0,230 | −0,018 | **0,015** | Fase 2 sì, **Fase 4 no** |
| LINK6 | V-001 rottura di 55 sopra la EMA 200, trailing | 1h long | 229 | −0,085 | −0,030 | 0,766 | no |
| LINK6 | V-002 sotto la EMA 200 | 1h short | 183 | −0,061 | −0,051 | 0,548 | no |
| LINK6 | V-015 RSI 14 che passa 50 con ADX > 25 | 1h long | 316 | −0,076 | −0,019 | 0,825 | no |
| LINK6 | V-016 | 1h short | 271 | −0,008 | −0,053 | 0,237 | no |
| LINK6 | V-017 MACD sopra la EMA 200 | 2h long | 232 | −0,012 | +0,016 | 0,692 | no |
| LINK6 | V-018 | 2h short | 191 | +0,017 | −0,061 | 0,103 | no |
| LINK6 | V-020 chiusura che incrocia la SMA 50 | 4h long | 199 | +0,091 | +0,084 | 0,354 | no |
| LINK6 | V-021 | 4h short | 199 | +0,010 | −0,083 | **0,001** | no (R piccolo) |
| LINK6 | V-028 incrocio EMA 20/50, stop 3 ATR, uscita al segnale opposto | 1h long | 220 | +0,242 | +0,165 | 0,130 | no |
| LINK6 | V-029 | 1h short | 220 | +0,084 | −0,076 | **0,003** | no (R piccolo) |

Cosa ne è stato: **la tendenza non ha mai battuto il caso con un vantaggio utile**, a nessun orizzonte (giorni sul
paniere, ore su BTC e LINK). Le varianti long con R alto (A1-20 long +0,477, V-007 +0,234, V-028 +0,242) avevano entrate
casuali altrettanto alte o vivevano di pochi trade (V-028: 51,6 R su 53,2 nel 2020; `fase5.md` di LINK6). Gli short con
p piccolo hanno R vicino a zero (sezione 3.11).

### 3.2 Momentum fra monete (solo PANIERE, idea B)

| Variante | Trade | R | t (b) / soglia | Esito |
|---|---|---|---|---|
| 022 B1 long: prime 10 per rendimento a 4 settimane | 527 stimati | — | — | scarto |
| 023 B1 short: ultime 10 | 592 stimati | — | — | scarto |
| 024 B2 long: prime 10 a 2 settimane | 692 stimati | — | — | scarto |
| 025 B2 short | 730 | −0,045 | 0,12 / 2,25, 12 blocchi | no |
| 026 B3 long: prime 20 a 4 settimane | 819 | −0,045 | −1,44 / 2,52 | no (peggio del caso) |
| 027 B3 short | 846 | −0,020 | 0,46 / 2,37 | no |

Morta a questo orizzonte; 3 varianti su 6 non arrivavano nemmeno a 700 trade sommati con l'ordine limite.

### 3.3 Relazioni fra monete: il ritardo dopo un giorno forte di Bitcoin (PANIERE, idea C)

| Variante | Trade | R | t (b) / soglia | Note |
|---|---|---|---|---|
| 028 C1-1,5 long: tutte le monete in ritardo, k 1,5, uscita 5 giorni | 1.297 | +0,157 | 1,69 / 2,25 | |
| 029 C1-1,5 short | 743 | −0,033 | −0,07 / 2,32 | lato short: niente |
| 030 C1-2 long (k 2) | 870 | +0,267 | **2,48 / 2,25** | netta contro la (b), non contro la (a) (2,17) |
| 031 C1-2 short; 033 C2-1,5 short | 350, 534 stimati | — | — | scarti |
| 032 C2-1,5 long: le 20 più in ritardo | 803 | +0,168 | 2,14 / 2,18 | |
| 036-038 ritocchi di 030 (filtro BTC sopra la media a 100; uscita 10 o 3 giorni) | 793-951 | +0,173…+0,238 | 1,69…2,13 | nessuno netto |
| 039 = 032 con uscita a 3 giorni | 886 | +0,132 | **2,38 / 2,17** | |
| **040** = 039 con k 1,25 | 1.363 | +0,130 | **3,24 / 2,11**, (a) 2,19 / 2,11, 25 blocchi | **candidato** |
| 041 = 032 con k 1,25 | 1.230 | +0,163 | **2,83 / 2,11** | |
| 042 = 028 con k 1,25 | 1.963 | +0,144 | 2,05 / 2,16 | |
| **043** = 042 con uscita a 3 giorni | 2.327 | +0,135 | **3,20 / 2,18**, (a) 2,20 / 2,18, 16 blocchi | **candidato** |
| 044 = 042 con il filtro di BTC | 1.233 | +0,214 | 2,28 / 2,28 | |
| 045, 047 ritocchi dello short; 046 scarto (641) | 915, 766 | +0,015, +0,096 | 0,44, 1,25 | |

Cosa ne è stato: i due candidati sono caduti in Fase 4 (ritardo di una barra e liquidazione; sezione 1.2). Il vantaggio è
**per metà il mercato che continua**: comprare tutte le monete dopo un giorno forte, senza la condizione di ritardo, dà
+0,075 R (t 1,97, PANIERE-089); vive in 36-63 giorni di segnale in tre anni e dipende da cosa fa BTC dopo (+0,39 R se
sale nei 5 giorni, −0,10 se scende) (`consegna.md` PANIERE, «Cosa abbiamo capito»). Era la stessa idea che nella campagna
GRUPPO a 1 ora si era fermata a t 2,06 contro 2,16 (`PROTOCOLLO_2.md`, sez. 1, punto 2), e che la prova degli ordini
limite aveva in coda come GRUPPO-048 senza eseguirla. Il filtro «BTC sopra la media a 100» separava bene i trade nello
studio dei fallimenti ma come ritocco non ha mai alzato il t (riduce trade e blocchi) (`lezioni_moneta.md` del branch).

### 3.4 Ritorno alla media (comprare la debolezza, vendere la forza)

| Campagna | Variante, in parole | tf, verso | Trade | R | Caso | p |
|---|---|---|---|---|---|---|
| BTC51 | V-015 ritorno dentro le Bollinger in mercato laterale (ADX < 20), limit 0,25 ATR | 30m long | 243 | −0,135 | −0,098 | 0,718 |
| BTC51 | V-016 | 30m short | 276 | −0,149 | −0,091 | 0,832 |
| BTC51 | V-017 RSI 7 che risale sopra 30, sopra la EMA 200, limit | 30m long | 327 | +0,025 | −0,060 | 0,074 |
| BTC51 | V-023 RSI 7 che riscende sotto 70, sotto la EMA 200, limit | 1h short | 152 | +0,023 | −0,051 | 0,201 |
| BTC51 | V-026 RSI 7 agli estremi nel fine settimana, limit | 1h long | 155 | −0,010 | −0,054 | 0,309 |
| BTC51 | V-027 | 1h short | 164 | −0,010 | −0,071 | 0,213 |
| BTC51 | V-037 rientro nelle bande con volume 1,5 volte | 1h short | 150 | −0,141 | −0,095 | 0,696 |
| BTC51 | V-038 | 1h long | 233 | −0,229 | −0,084 | 0,990 |
| LINK6 | V-009 ritorno dentro le Bollinger con ADX < 20 | 30m long | 316 | −0,161 | −0,103 | 0,835 |
| LINK6 | V-010 | 30m short | 327 | −0,150 | −0,061 | 0,940 |
| LINK6 | V-013 rientro nelle Bollinger 2,5 con limit a 0,5 ATR | 1h long | 217 | −0,100 | −0,015 | 0,912 |
| LINK6 | V-014 | 1h short | 226 | −0,130 | −0,039 | 0,908 |
| LINK6 | V-022 RSI 14 agli estremi 30/70 | 1h long | 273 | −0,088 | −0,009 | 0,883 |
| LINK6 | V-023 | 1h short | 301 | −0,197 | −0,038 | 0,993 |
| LINK6 | V-024 stocastico agli estremi | 2h long | 238 | −0,102 | −0,020 | 0,886 |
| LINK6 | V-025 | 2h short | 366 | −0,125 | −0,042 | 0,946 |
| LINK6 | V-032 rientro nel fine settimana con la candela di rifiuto | 1h long | 159 | −0,085 | −0,065 | 0,609 |
| LINK6 | V-033 | 1h short | 167 | −0,048 | −0,041 | 0,538 |

Cosa ne è stato: **18 varianti su 18 sotto 0,03 R**, 16 negative (calcolo mio sulle righe qui sopra); su LINK tutte e
dieci negative e sotto le loro entrate casuali (lezioni LINK6, sez. 1). V-038 fa peggio del caso con chiarezza (p 0,990): dopo un eccesso al ribasso con volume
alto BTC ha continuato a scendere (`ipotesi.md` di BTC51, I-19). La prima edizione aveva già scritto «ritorno alla media
di poche ore: non riprovare così com'è» (`docs/capito.md`, 12 ott, da `research/confronto/lezioni_comuni.md`, sez. 4).

### 3.5 Rotture di volatilità e bande di Bollinger

| Campagna | Variante, in parole | tf, verso | Trade | R | Caso | p |
|---|---|---|---|---|---|---|
| BTC51 | V-018 rottura delle Bollinger con volatilità bassa, trailing | 1h long | 230 | +0,196 | −0,009 | **0,011** |
| BTC51 | V-019 | 1h short | 187 | +0,059 | −0,110 | 0,036 |
| BTC51 | V-039 chiusura sotto la banda con volume doppio | 1h short | 433 | +0,074 | −0,104 | **0,001** |
| BTC51 | V-040 sopra la banda con volume doppio | 1h long | 419 | +0,106 | −0,081 | **0,001** |
| LINK6 | V-011 rottura dopo la compressione | 1h long | 212 | −0,054 | −0,044 | 0,554 |
| LINK6 | V-012 | 1h short | 160 | +0,043 | −0,008 | 0,245 |

Cosa ne è stato: su BTC c'è un'informazione vera ma piccola: le rotture con volume doppio continuano in tutte e due le
direzioni, più del caso (p 0,001), ma valgono +0,07/+0,11 R, meno dei costi a 1 ora (lezioni BTC51, sez. 1). V-018 si
è fermata a 0,004 R dalla soglia; tre quarti della sua somma veniva dal primo semestre 2020 (`ipotesi.md` di BTC51,
Fase 3). Su LINK la compressione non dà niente.

### 3.6 Volume anomalo

| Campagna | Variante, in parole | tf, verso | Trade | R | Caso | p |
|---|---|---|---|---|---|---|
| BTC51 | V-008 volume doppio e candela verde | 4h long | 161 | −0,051 | −0,003 | 0,737 |
| BTC51 | V-009 volume doppio e candela rossa | 4h short | 183 | +0,031 | −0,058 | 0,109 |
| BTC51 | V-010 volume doppio e candela verde | 1h long | 831 | −0,023 | −0,084 | 0,027 |
| BTC51 | V-033 volume doppio nelle ore degli Stati Uniti | 1h long | 451 | −0,033 | −0,083 | 0,139 |
| BTC51 | V-034 | 1h short | 460 | −0,041 | −0,096 | 0,110 |
| LINK6 | V-007 volume doppio con la direzione della candela | 2h long | 312 | +0,030 | −0,025 | 0,119 |
| LINK6 | V-008 | 2h short | 339 | +0,024 | −0,035 | 0,089 |
| LINK6 | V-026 rottura di 20 nelle ore degli Stati Uniti con volume 1,5 volte | 1h long | 222 | −0,018 | −0,027 | 0,429 |
| LINK6 | V-027 | 1h short | 197 | −0,036 | −0,062 | 0,343 |

Cosa ne è stato: niente vicino alla soglia. È anche la famiglia che nel primo giro del collaudo produceva più p-value
falsi (segnale di volume: 8 su 21 sotto 0,10; conferma di volume: 7 su 16), perché le candele anomale portano stop larghi
(`collaudo_3/esiti.md`, «La causa del difetto»): prima della correzione, il volume sembrava funzionare per un difetto
del confronto.

### 3.7 Funding (il pagamento periodico fra long e short)

| Campagna | Variante, in parole | tf, verso | Trade | R | Caso | p | Esito |
|---|---|---|---|---|---|---|---|
| BTC51 | V-011 funding regolato sopra +0,03%, uscita dopo 24 ore | 1h short | 224 | +0,139 | −0,073 | **0,009** | no (R < 0,2) |
| BTC51 | V-012 funding sotto 0, uscita dopo 24 ore | 1h long | 228 | +0,171 | −0,002 | **0,023** | no (R < 0,2) |
| BTC51 | **V-020** = V-012 solo nei giorni feriali | 1h long | 180 | +0,223 | −0,004 | **0,017** | **candidato**; validazione +0,167 su 80; **vault −0,007 su 180**; altre monete 1 su 9 |
| BTC51 | V-024 «spremuta»: rottura di 20 con funding sotto 0 | 30m long | 160 | +0,193 | −0,091 | **0,002** | no (R < 0,2) |
| BTC51 | V-025 rottura dei minimi con funding sopra +0,03% | 30m short | 184 | +0,019 | −0,100 | 0,068 | no |
| LINK6 | V-003 funding sopra +0,05%, target 2 R o 24 ore | 1h short | 202 | +0,002 | −0,038 | 0,298 | no |
| LINK6 | V-004 funding sotto 0, target 2 R o 24 ore | 1h long | 174 | +0,128 | −0,013 | 0,047 | no (la migliore di LINK6) |
| LINK6 | V-019 = V-004 con uscita dopo 48 ore (nata dalla Fase 3) | 1h long | — | — | — | — | **scarto**: sulle monete di controllo +0,010 R invece di +0,05 (R-001) |

Cosa ne è stato: su BTC il diario la chiama «l'unica famiglia del catalogo che ha dato p-value piccoli in tutte e due le
direzioni» (17 ott, pomeriggio); non è esatto, perché anche le rotture delle bande con volume doppio (V-039 e V-040) hanno
p 0,001 in tutte e due. È stata comunque la famiglia più vicina alla soglia su BTC e la migliore anche su LINK. Ma non ha mai superato lo 0,2 R se non con un filtro nato dai dati (V-020), ed è
caduta nel vault (sezione 3.11).

### 3.8 Orari, sessioni e giorni della settimana

| Campagna | Variante, in parole | tf, verso | Trade | R | Caso | p |
|---|---|---|---|---|---|---|
| BTC51 | V-013 rottura del range della notte asiatica (00-08 UTC) | 1h long | 380 | −0,025 | −0,081 | 0,135 |
| BTC51 | V-014 | 1h short | 361 | −0,156 | −0,100 | 0,861 |
| BTC51 | V-035 = V-013 solo nei feriali | 1h long | 296 | +0,012 | −0,078 | 0,067 |
| BTC51 | V-036 | 1h short | 268 | −0,098 | −0,099 | 0,485 |
| LINK6 | V-005 rottura del range asiatico, stop al minimo delle ultime 5 candele | 1h long | 412 | −0,079 | −0,051 | 0,740 |
| LINK6 | V-006 | 1h short | 344 | +0,005 | −0,059 | 0,104 |

Altre varianti con un filtro di orario o di giorno sono nelle loro famiglie: V-020 (feriali, funding), V-026/027 di BTC51
(fine settimana, ritorno), V-033/034 di BTC51 e V-026/027 di LINK6 (ore degli Stati Uniti, volume), V-032/033 di LINK6
(fine settimana, ritorno). Cosa ne è stato: niente. Lo schema «feriali meglio del fine settimana» è comparso in 4 delle 5
varianti di BTC analizzate (V-012, V-018, V-024, V-032; non in V-011), sempre sugli stessi dati: «resta un'osservazione»
(`ipotesi.md` di BTC51, «Fase 5, seconda volta»). Usato una volta come filtro (V-020), ha prodotto l'unico candidato,
caduto.

### 3.9 VWAP (il prezzo medio del giorno pesato per il volume)

| Campagna | Variante, in parole | tf, verso | Trade | R | Caso | p |
|---|---|---|---|---|---|---|
| BTC51 | V-031 sopra il VWAP, la chiusura incrocia la EMA 20 con volume 1,5 volte, uscita alle 21:00 | 1h long | 246 | −0,070 | −0,039 | 0,680 |
| BTC51 | V-032 | 1h short | 331 | +0,016 | −0,081 | 0,034 |
| LINK6 | V-030 sopra il VWAP, RSI 14 che passa 50 | 1h long | 777 | −0,034 | −0,061 | 0,210 |
| LINK6 | V-031 | 1h short | 768 | +0,027 | −0,070 | **0,003** |

Niente: gli short battono di poco gli short casuali, con R vicino a zero.

### 3.10 L'esecuzione (non un'idea): ordini limite

* Prova del 13 ottobre sulle nove strategie: costi −36%, nessun vantaggio nuovo, i trade saltati sono i migliori (1.1).
* Nel protocollo 2 l'ingresso a limite era obbligatorio: ha mandato 7 varianti su 18 sotto i 700 trade sommati
  (`lezioni_metodo_proposte.md` del branch PANIERE, punto 6).
* Nei protocolli 3 e 4 era una scelta della variante (limit a 0,25 o 0,5 ATR oltre la chiusura): 6 varianti di BTC51
  (V-015, V-016, V-017, V-023, V-026, V-027) e 2 di LINK6 (V-013, V-014), tutte nel ritorno alla media e tutte sotto la
  soglia. Nessuna variante di tendenza è stata provata con il limit.

### 3.11 Le idee che tornano in più campagne

1. **Funding sotto zero, poi long.** Prima edizione: «debole guadagno, mai netto» su BTC (+0,053 R, t 1,28), BNB, XRP;
   perdita o nulla su AVAX («nel 2022 il funding negativo accompagnava il ribasso»), LTC, LINK (−0,41 R) e altre
   (`research/confronto/lezioni_comuni.md`, sez. 3.4). BTC51: tre varianti sopra il caso (V-012, V-020, V-024), «ma
   costruite sugli stessi episodi di funding negativo, quindi non tre prove indipendenti» (`ipotesi.md` BTC51); V-020
   candidato, caduto nel vault proprio nei ribassi con molto funding negativo (2026H1). Altre monete nel vault: regge solo
   su LTC. LINK6: di nuovo la famiglia migliore (V-004 +0,128 R, p 0,047), senza superare la soglia; la stessa regola
   sulle 9 monete di controllo in costruzione fa in media +0,015 R (BTC +0,142 su 245 trade, ETH +0,082, MATIC +0,064,
   BNB +0,024, LTC +0,005, XRP −0,004, SOL −0,036, BCH −0,067, DOGE −0,075; `R-001.json`, campo `vecchia`). **Tre volte
   la stessa idea, tre volte lo stesso esito**: c'è qualcosa sul periodo 2020-2022 di BTC, non regge altrove né dopo.
   L'avvertenza della prima edizione su AVAX nel 2022 descriveva in anticipo il modo in cui V-020 è caduta; la sessione di
   BTC51 non poteva leggerla, per regola (la ricerca non vede le campagne passate).
2. **Funding alto, poi short.** Prima edizione: «perde o fa come il caso su tutte le monete», con BTC l'unica non negativa
   (+0,069 R, t 1,47) (`lezioni_comuni.md`, sez. 1.5). BTC51: V-011 +0,139 R, p 0,009, metà della somma dal primo semestre
   2020 e nessun trade nel 2022 (`ipotesi.md` BTC51, Fase 3). LINK6: V-003 +0,002 R. Non regge.
3. **L'incrocio EMA 20/50 a 1 ora, long, identico.** BTC51 V-007 e LINK6 V-028 hanno la stessa specifica (stop 3 ATR,
   uscita al segnale opposto) e quasi lo stesso esito: +0,234 e +0,242 R, ma entrate casuali +0,147 e +0,165, p 0,106 e
   0,130. La sessione di LINK6 non ha visto le idee di BTC51 (decisione D3 del proprietario: «no»; `protocollo_4_note.md`,
   sez. 1), eppure ha riscritto quasi le stesse varianti: anche V-005/V-006 di BTC51 contro V-020/V-021 di LINK6 (incrocio
   della media a 50 su 4 ore), V-021/V-022 contro V-017/V-018 (MACD su 2 ore con la EMA 200), V-013/V-014 contro
   V-005/V-006 (range asiatico), V-012 contro V-004 (funding). Osservazione mia: **con lo stesso catalogo, lo stesso
   modello e la stessa letteratura, una campagna nuova su un'altra moneta riprova in gran parte le stesse regole**.
4. **Short di tendenza con p-value piccolo e R vicino a zero.** BTC51 V-006 (p 0,004, +0,031 R); LINK6 V-021 (p 0,001,
   +0,010), V-029 (0,003, +0,084), V-031 (0,003, +0,027). Spiegazione scritta per LINK (`fase5.md`): in un periodo che sale
   (LINK +184%) uno short a caso perde, e uno short che entra solo nei ribassi lo batte senza guadagnare. Vale anche per BTC:
   le entrate casuali degli short di BTC51 fanno in media −0,082 R, quelle dei long −0,016 (calcolo mio sul log di BTC51,
   18 short e 22 long); per LINK −0,051 e −0,014 (lezioni LINK6, sez. 1; ricontrollato).
5. **Ritorno alla media**: perde in BTC51 e LINK6 (3.4), come già nella prima edizione.
6. **Range asiatico**: BTC51 (V-013/014, poi V-035/036 nei feriali) e LINK6 (V-005/006): sempre vicino a zero o negativo.
7. **Tendenza**: paniere a 1 giorno, BTC e LINK a ore: mai sopra il caso con un vantaggio utile (3.1).
8. **Ritardo dopo BTC**: GRUPPO a 1 ora (t 2,06 contro 2,16, prima edizione), PANIERE a 1 giorno (due candidati caduti in
   Fase 4). È l'unica idea «fra monete» provata due volte, e due volte è arrivata vicino alla soglia senza passare.
9. **Ultima mezz'ora del giorno UTC** (la famiglia più ripetuta della prima edizione, 6 campagne): ripresa solo nella prova
   degli ordini limite; in validazione le quattro strategie hanno R negativo sia a mercato sia a limite (BTCUSDT-V35 −0,140
   / −0,104, ETCUSDT-033 −0,098 / −0,066, SOLUSDT-023 −0,033 / −0,013, AVAXUSDT-V-12 −0,086 / −0,052; `risultati.md` degli
   ordini limite, sez. 5.2). Il catalogo dei protocolli 3 e 4 non ha un ingresso a un'ora fissa del giorno come
   l'ultima mezz'ora: ha il filtro di sessione (F5), la rottura del range asiatico (E10) e l'uscita alle 21:00 (U2s).

**Numeri d'insieme.** BTC51: R medio delle 40 varianti +0,022 contro −0,046 delle loro entrate casuali, 29 su 40 le
battono, p-value medio 0,291, 9 con p ≤ 0,023 (calcolo mio sul log di BTC51). LINK6: −0,030 contro −0,032, 16 su 32, p
medio 0,478, 3 con p ≤ 0,023 (lezioni LINK6). Su BTC molte regole battono il caso di poco; su LINK no. In tutte e due solo
la soglia dei 0,2 R le ha fermate.

---

## 4. Errori di metodo e difetti degli strumenti, con la correzione

### 4.1 Prova degli ordini limite e protocollo 2 (13-14 ottobre)

| # | Cosa | Come è stato trovato | Correzione | Fonte |
|---|---|---|---|---|
| 1 | La regola riempiva all'apertura un limite già nel libro se la barra apriva oltre: regalava il salto | scrivendo i test del motore, prima delle corse | riempimento sempre al prezzo del limite | `esperimenti/ordini_limite/risultati.md`, sez. 1 |
| 2 | Minimi di trade sbagliati nel testo del protocollo 2 (300/100/300) | rileggendo prima del Passo 0 | 700/300/300 del gruppo | `PROTOCOLLO_2.md`, correzione 1 |
| 3 | Con `vault/APERTURA.md` dell'11 ottobre il caricatore avrebbe accettato date 2024-2026 anche per la seconda edizione | al Passo 0 | marcatore nuovo `APERTURA_2.md` | `PROTOCOLLO_2.md`, correzione 2; `CHANGELOG.md`, 13 ott |
| 4 | La stima della distanza dello stop nel testo (6-12%) era sbagliata: misurata 22,2% | misura del Passo 0 | **nessuna**: i parametri sono stati approvati così; dopo è arrivato il problema della liquidazione (riga 12) | `PROTOCOLLO_2.md`, sez. 3.2; `passo0_2/rapporto.md` (rilievo mio) |
| 5 | Placebo a 1 giorno: con i parametri a 1 ora pochi trade (227-420); senza tetto posizioni lunghe centinaia di giorni, esame non valutabile | primi lanci | parametri per il giorno; tetto di 60 barre | `passo0_2/rapporto.md` |
| 6 | Controllo positivo: la (b) non entra sulle monete dalla storia corta; con 7 blocchi +0,3 R non è «netto» | controllo positivo del Passo 0 | regola del 10%; esame lasciato com'è, ogni variante riportata con t e blocchi | `PROTOCOLLO_2.md`, correzione 3; commit `c9bb86ad` |
| 7 | Il guardiano negava alla campagna le regole del gruppo, che il messaggio di apertura chiedeva di leggere | STOP della sessione alle 07:13 | lettura ammessa del solo file `GRUPPO/regole.md` | commit `298b1a7f`; `CHANGELOG.md`, 14 ott |
| 8 | Il guardiano negava lo strumento per leggere le notifiche, cioè le frasi del coordinamento; il canale era stato provato su una sessione **senza** guardiano | secondo STOP (07:52) | strumento ammesso; la frase la scrive il proprietario | commit `158f90a0`; diario 14 ott, 10:15 |
| 9 | Gli strumenti non passavano il paniere alla variante (idee B e C2 non eseguibili) e costruivano l'ingresso **a mercato** invece che a limite | due note della sessione (08:42, 09:14) | correzione 5; placebo e controllo positivo rifatti | commit `08e2c95a`; `PROTOCOLLO_2.md`, correzione 5 |
| 10 | Il file delle impronte conteneva 96 file a 8 ore di BTC che la sessione non poteva scaricare | Fase 0 della campagna | esclusi a mano dalla sessione | `lezioni_metodo_proposte.md` del branch PANIERE, punto 3 |
| 11 | Un parametro di scelta (`monete_in_ritardo = 0` = «tutte») spostato a −1 e +1 nella robustezza | Fase 4 | voce di correzione PANIERE-087 | log del branch PANIERE; stessa lezione, punto 4 |
| 12 | Stop in ATR giornalieri senza tetto: dopo i crolli arriva al 79-95% del prezzo e viola la liquidazione | Fase 4, dopo tutto il budget | nessuna (campagna finita); proposta: tetto allo stop o filtro sull'ATR deciso prima | `lezioni_metodo_proposte.md`, punto 1 |
| 13 | Tre errori di forma della sessione sotto il guardiano (`git log` fuori dalla cartella, `sed -i`, `2>&1`) | rifiuti del guardiano | nessuna, già scritti in `research/lezioni/metodo.md` | `consegna.md` PANIERE, misure di processo |
| 14 | Le lezioni della campagna non sono state unite al principale | — | nessuna al 18 ottobre | `docs/backlog.md`, P6 (rilievo mio, sezione 1.2) |

### 4.2 Protocollo 3 e campagna BTC51 (16-17 ottobre)

| # | Cosa | Come è stato trovato | Correzione | Fonte |
|---|---|---|---|---|
| 15 | Riempimento severo: il motore chiedeva più dello «almeno 0,05%» del testo | verificatore indipendente | confronto non stretto | commit `ba85fc49` |
| 16 | Entrate casuali: la prima versione teneva più spesso i trade brevi (stop), il caso sembrava peggiore di 0,07 R; 6 p-value su 12 sotto 0,10 senza vantaggio | verificatore indipendente | strategia che entra a caso con probabilità tarata | commit `dd2ef133` |
| 17 | Il calcolo si fermava dicendo «i trade non ci stanno» quando ci stavano | stesso | si ferma solo se nemmeno una strategia che entra appena libera ci arriva | stesso |
| 18 | E11 (funding): la variante non si rinormalizzava e nella robustezza cambiava lato | stesso | il lato resta | stesso |
| 19 | Arrotondamenti a metà; soglie di E6 ed E8 nella robustezza | stesso | per eccesso; si sposta la soglia della direzione | stesso |
| 20 | **p-value non tarato** per la larghezza dello stop (21 su 100 sotto 0,10) | collaudo, primo giro | entrate casuali con la stessa distribuzione di larghezza; serie con la direzione girata; vantaggio inserito più grande | `collaudo_3/esiti.md`; `PROTOCOLLO_3.md`, appendice 3 |
| 21 | I 6 giorni senza mark diventavano buchi anche nel last: il riscaldamento ripartiva (a 1 giorno 0% della costruzione usabile, poi 40%) | sessione di ricerca al Passo 1 | il mark mancante si prende dal last della stessa candela | commit `0bbf0389` e `015f9ba9`; `PROTOCOLLO_3.md`, 9.6 |
| 22 | Un pareggio esatto fra candidato e simulazione differiva all'ultima cifra (5,6e-17) con numpy 2.5 e non contava, a favore del candidato | sessione di ricerca, due test falliti sulla sua macchina | tolleranza di un miliardesimo di R | commit `7b189254` e `65867d33` |
| 23 | Il collaudo era stato fatto con Python 3.11 e numpy 1.26, la ricerca girava con 3.13 e 2.5 | conseguenza della 22 | quarto giro con le versioni della ricerca | `collaudo_3/esiti.md`; lezioni BTC51, sez. 2 |
| 24 | **Un filtro nato dai dati è passato come idea nuova** (i feriali di V-020, dai trade di V-012) | dopo il vault | protocollo 4: definizione meccanica e controllo sulle monete di controllo | lezioni BTC51, sez. 2, punto 4 |
| 25 | Verifica dei trade estremi troppo larga (V-020 a +0,012 R senza i 9 migliori: passava) | dopo il vault | protocollo 4, verifica 4 nuova | lezioni BTC51, punto 5 |
| 26 | La robustezza non muove le soglie a zero (±20% di zero è zero) | segnalato dalla sessione | protocollo 4, passo fisso | lezioni BTC51, punto 6; backlog P8 |
| 27 | La validazione non distingue dal caso (+0,167 R su 80 trade ≈ 1,2 errori standard) | consegna e vault | protocollo 4: validazione anche sulle monete di controllo | lezioni BTC51, punto 7 |
| 28 | La stabilità guarda 4 blocchi di tempo, non i mercati (V-020 debole già nel ribasso 2022H1) | dopo il vault | protocollo 4, verifica 3bis (che però da sola non avrebbe fermato V-020: nel 2022H1 era +0,040, positivo) | lezioni BTC51, punto 8; `protocollo_4_note.md`, sez. 2, punto 5 |
| 29 | Sui prezzi veri il p-value separa poco: 16 su 40 con p ≤ 0,10, contro 11 su 100 nel collaudo; a fermare è stata la soglia di 0,2 R | lettura dei risultati | nessuna (resta la soglia) | lezioni BTC51, punto 9 |
| 30 | La frase del vault è stata scritta nella sessione di ricerca; il coordinamento ha aperto il vault sulla base di un messaggio non esatto del proprietario e delle note nel log, prima di ricevere la frase esatta | — | protocollo 4: la frase vale solo al coordinamento, dopo lo STOP del Passo 4 | `vault/APERTURA_3.md`; `protocollo_4_note.md`, sez. 2, punto 8 |
| 31 | Il Passo 6 ha usato il vault di 9 monete nuove per una sola strategia | — | protocollo 4: Passo 6 sulle monete di controllo | `protocollo_4_note.md`, sez. 2, punto 14 |
| 32 | A 23 varianti la sessione voleva fermarsi; usare i 17 tentativi rimasti (richiesta del proprietario) ha prodotto un'altra variante oltre la Fase 2 (V-030), falsa | Fase 5 | nessuna; il protocollo 4 lascia ancora aperta la domanda (riga 41) | `ipotesi.md` di BTC51 (rilievo mio, inferito) |
| 33 | Ultracode non attivo nella sessione di ricerca (come in PANIERE e poi in LINK6) | `get_session` dopo l'apertura | nessuna: detto al proprietario | diario 17 ott; lezioni LINK6, sez. 2, punto 6 |

### 4.3 Protocollo 4 e campagna LINK6 (17-18 ottobre)

| # | Cosa | Come è stato trovato | Correzione | Fonte |
|---|---|---|---|---|
| 34 | Fughe di informazione sul vault: il `CLAUDE.md` del principale e i titoli dei commit dicevano l'esito di V-020; le motivazioni del testo descrivevano V-020; un fatto del 2024 (il delisting di MATIC) nel testo | revisore indipendente | branch con storia propria, `CLAUDE.md` pulito, motivazioni in un file che la ricerca non legge | `protocollo_4_note.md`, sez. 3, punti 1-3 |
| 35 | LINK già esplorato dal protocollo 1, non detto nel testo | revisore | detto nelle note e nella sez. 15; cartella del protocollo 1 vietata alla ricerca | stesso, punto 4 |
| 36 | Con `APERTURA_3.md` esistente il caricatore del protocollo 3 avrebbe aperto il vault di qualunque moneta | scrivendo il protocollo 4 | il caricatore riconosce solo `APERTURA_4.md` | `protocollo_4_note.md`, sez. 2, punto 10; `CHANGELOG.md`, 17 ott |
| 37 | La guida pratica faceva leggere le versioni con `python3 -c`, che il guardiano rifiuta | sessione di ricerca all'avvio | lettura con uno script | commit `a0f5b8ad` (branch) e `338de989` (principale) |
| 38 | La delega del proprietario non era nel messaggio di apertura: la sessione ha aspettato 8 ore una conferma che il coordinamento aveva già dato | log N-003, N-004 | proposta per il prossimo protocollo | lezioni LINK6, sez. 2, punto 1 |
| 39 | Due testi diversi per il canale delle richieste («commit precedente» nelle regole del collaudo, «stesso commit» nella guida) | richiesta R-001 | proposta: un solo testo | lezioni LINK6, punto 2; `R-001.json`, nota |
| 40 | La routine del coordinamento risultava consegnata ma la sessione non è ripartita | dopo il primo invio (07:38) | secondo invio; «conta la voce nel log della sessione» | lezioni LINK6, punto 5 |
| 41 | Non è scritto se si può fermare la ricerca prima delle 40 varianti: l'ha deciso il coordinamento | STOP a 27 su 40 | proposta: regola dei tentativi rimasti nella Fase 5 | lezioni LINK6, punto 4 |
| 42 | Lo script della sessione per la Fase 2 è caduto su V-001 (array trattato come lista), dopo il calcolo ma prima di scrivere il risultato | sessione | voce di correzione nel log, stessa specifica rieseguita una volta | `research/campagne/LINK6/log.jsonl`, voce `correzione` di V-001 |

Nessuno strumento è cambiato durante la ricerca LINK6: le impronte sono rimaste quelle del collaudo (lezioni LINK6, sez. 2).
**Delle difese nuove del protocollo 4, solo due sono state messe alla prova davvero**: il controllo delle versioni
all'avvio (log N-001) e il controllo della Fase 3 sulle monete di controllo (R-001, che ha fermato V-019). La verifica 12,
la 3bis, la verifica 4 nuova, la robustezza a passo fisso e la validazione sulle monete di controllo non sono mai partite,
perché nessuna variante ha superato la Fase 2 (rilievo mio, dal log). Il coordinamento ha scritto: «Non so se questo testo
avrebbe fermato V-020 prima del vault... non le ho calcolate su V-020» (`protocollo_4_note.md`, sez. 2, ultima parte).

---

## 5. Trappole dei dati

1. **L'archivio pubblico di Binance non ha BTCUSDT prima del 2020-01-01** (i mesi del 2019 rispondono 404), anche se il
   contratto esiste da settembre 2019: la costruzione del protocollo 3 è di 33 mesi invece dei 36,5 pensati
   (`fase0_dati.md` di BTC51, sez. 1-2). Per LINKUSDT la prima candela oraria è del 2020-01-17 08:00, ma le candele native
   a 6 ore, 12 ore e 1 giorno di quel giorno aprono prima (06:00 e 00:00), prima dell'inizio degli scambi (log LINK6,
   N-002).
2. **Giorni interi senza prezzo mark** negli stessi giorni su molte monete: 2021-07-01, dal 2021-07-24 al 27, 2022-07-31
   (costruzione), 2022-10-02, 2023-02-24 (validazione), 2026-06-29 (vault, su tutte le monete tranne MATIC), più due buchi
   di 15 minuti (2020-01-19 13:15, 2023-11-10 03:45) (`fase0_dati.md` di BTC51, sez. 3; `vault/BTC51_risultati.md`;
   `altre_monete_3/risultati.md`; `passo0_4/fatti_monete.json`). Trattati come buchi, rendevano inutilizzabile la
   costruzione a 1 giorno (errore 21).
3. **Buchi anche nel last** su alcune monete di controllo: SOL, XRP e LTC hanno 72 ore mancanti dal 2022-02-26 e 48 dal
   2022-04-01 (`passo0_4/fatti_monete.json`, campo `buchi_dettaglio_1h`). Su BNB, SOL, XRP, LTC ci sono anche centinaia di
   candele da 15 minuti con il mark ma senza il last (campo `mark_senza_last`: 896, 557, 500, 495). Non ho verificato come
   il motore le tratta.
4. **Candele a volume zero in mezzo alla serie** su LINK (6 a 15 minuti, 1 a 30 minuti, 2021-2022): tenute (lezioni LINK6,
   sez. 3).
5. **Il funding cambia frequenza di regolamento**: SOL nel novembre 2022 passa da 8 a 4 e poi a 2 ore, e torna a 8 il 18
   novembre (`fatti_monete.json`, `intervalli_funding`). Per confrontare la stessa soglia fra monete il protocollo 4
   riporta il tasso a 8 ore (`CHANGELOG.md`, 17 ott).
6. **Il funding cambia con il mercato, e con lui il numero di trade di una regola sul funding**: su BTC il funding era sotto
   zero nel 3% dei regolamenti del 2024H1 e nel 38% del 2026H1 (`vault/BTC51_risultati.md`); su BCH V-020 fa 14,8 trade al
   mese contro 5,5 su BTC (`altre_monete_3/risultati.md`).
7. **Tabella delle monete incompleta**: `research/universo/candidate.csv` (7 ottobre) aveva il volume 2023 solo per i
   contratti quotati prima del 2022; ne mancavano 127, fra cui APT, che entrava fra le prime 9 (`altre_monete_3/
   risultati.md`; backlog P9).
8. **Media del volume sui soli giorni presenti**: premia i contratti appena quotati (ORDI 55 giorni nel 2023, 1000SATS 20).
   Usato il volume dell'anno diviso 365 (stesse fonti).
9. **Contratti morti con candele finte**: MATICUSDT smette di scambiare il 2024-09-04 alle 08:00 UTC, ma l'archivio ha
   altre 169 ore a prezzo fermo e volume zero, e mark e funding fino al 2026-09 senza scambi. La serie va fermata
   all'ultima candela con scambi (stesse fonti).
10. **Paniere a barre giornaliere**: il funding ha 17 mesi in meno del prezzo (le monete che partono nel mese del listing)
    (`passo0_2/rapporto.md`, tabella, punto 1); ICPUSDT senza file di funding da maggio 2021 ad agosto 2022, quindi long un
    po' favoriti lì; la costruzione finisce il 16 gennaio 2023 a metà di un rialzo, e i trade chiusi a «fine dati» (48-57
    per variante C long) fanno +1,1-1,5 R: i due giorni migliori dei candidati sono il 15 e 16 gennaio (`consegna.md`
    PANIERE, «Rischi e limiti»); sulle monete dalla storia corta le entrate casuali possono non entrare.
11. **30 minuti nativi o aggregati**: delle quattro strategie a 30 minuti della prova degli ordini limite, una usava i 30
    minuti aggregati dai 15 e tre i file nativi; per la parità si è fatto come ogni campagna (`ordini_limite/
    risultati.md`, nota 1).
12. **Periodi con una direzione forte**: BTC quasi triplicato nella costruzione (`collaudo_3/esiti.md`, diagnosi), LINK
    +184% (`fase5.md` di LINK6). Gli short casuali perdono, e gli short di tendenza sembrano battere il caso senza
    guadagnare (3.11, punto 4).
13. **Dati già usati**: la costruzione di LINK era già stata esplorata dal protocollo 1 (30 varianti, fino al
    2022-10-18): «le idee provate allora contano come idee già provate su questi dati» (`PROTOCOLLO_4.md`, sez. 15;
    `protocollo_4_note.md`, D1). Il vault 2024-2026 delle 9 monete di controllo è già stato aperto (protocollo 3).
14. **Trappole per chi legge la storia**: ora italiana nel diario e UTC nei file (2 ore di differenza); nomi delle
    varianti e delle idee che ricominciano in ogni campagna; «versione 5» che indica sia il protocollo 2 (versione 5.0) sia
    il testo del proprietario da cui viene il protocollo 3 (versione 5, non nel repository); sigle con più significati
    (C1/C2, (a)/(b)).

---

## 6. Lezioni e proposte scritte, e quali sono state messe in pratica

### 6.1 Dalla prova degli ordini limite (13 ottobre)

| Proposta (`ordini_limite/risultati.md`, sez. 2.2) | Messa in pratica? |
|---|---|
| Provare l'ingresso a limite nel paper, con una misura di qualche settimana, prima di cambiare il gate | **Sì** il paper (commit `6d50adfa`); **no** la misura (non ancora fatta al 18 ottobre); il gate è fermo |
| Uscite a mercato | Sì: protocolli 2, 3 e 4 |
| Senza decisione, bot e gate come oggi | superata dal «procedi con tutto» del 13 ottobre |

Nel protocollo 2 l'ingresso a limite è diventato obbligatorio (sez. 3.1); nei protocolli 3 e 4 è un'opzione con un limit
diverso (0,25 o 0,5 ATR oltre la chiusura, validità 1 o 3), che il bot in paper **non** esegue (il suo limite è alla
chiusura: `research/config/bot_3.md`, punto 3).

### 6.2 Dalla prima edizione al protocollo 2

Tutte le conclusioni della sezione 1 del protocollo 2 sono diventate regole del testo: barre giornaliere per far scendere i
costi, paniere per avere abbastanza trade, poche idee con fonte per tenere onesta la soglia, ordine limite, paper come esame
finale. La misura del Passo 0 ha confermato i costi bassi (0,0068 R) ma ha mostrato due costi nuovi: il funding e la
larghezza dello stop.

### 6.3 Dalla campagna PANIERE (lezioni del branch, copiate sul principale il 18 ottobre)

| Lezione (`lezioni_metodo_proposte.md` del branch PANIERE) | Ripresa dopo? |
|---|---|
| 1. Stop in ATR giornalieri senza tetto → violazioni di liquidazione; decidere prima un tetto o un filtro | Non risulta citata. Nel protocollo 3 lo stop in ATR si calcola sul timeframe della variante (soprattutto ore) e il controllo di liquidazione c'era già (sez. 9.4) |
| 2. Gli strumenti dell'esame vanno provati sul terreno della campagna prima dell'apertura | **In spirito sì**: il collaudo del metodo del protocollo 3. Ma il testo lo motiva con la richiesta del proprietario di un metodo senza buchi (`PROTOCOLLO_3.md`, appendice 2, punto 1), non con PANIERE |
| 3. Nel file delle impronte solo le serie scaricabili | Non risulta citata |
| 4. Parametri «di scelta» separati da quelli numerici nella robustezza | Non applicabile: nel catalogo chiuso i valori sono solo quelli del catalogo |
| 5. La fine della costruzione taglia i trade aperti e può metterli fra i giorni migliori | Non risulta citata (le regole del collaudo 3 dicono solo come si chiude a fine dati, punto 18) |
| 6. Stimare la frequenza prima di scrivere le varianti lente | C'era già (stima dei trade prima di ogni variante); il protocollo 3 la tiene (sez. 8.4) |
| 7. Le forme di comando rifiutate dal guardiano restano le stesse | Le guide pratiche dei protocolli 3 e 4 esistono, ma nel protocollo 4 un comando della guida stessa era rifiutato (errore 37) |

### 6.4 Dal collaudo del protocollo 3 al protocollo 4

Le tre correzioni (entrate casuali alla stessa larghezza di stop, serie con la direzione girata, vantaggio inserito più
grande) sono **incorporate** nel testo del protocollo 4 (sez. 10.1, 13bis.1, 13bis.3). La lezione sulle versioni è
diventata la regola 11. La prova C resta rimandata a dopo il vault in tutti e due.

### 6.5 Dalla campagna BTC51 al protocollo 4: le otto proposte

| Proposta (`campagne/BTC51/lezioni.md`, sez. 5) | Nel protocollo 4 | Esercitata in LINK6? |
|---|---|---|
| 1. Provare l'idea sulle altre monete prima del vault, sul periodo già usato | monete di controllo, verifica 12, validazione sulle monete di controllo (sez. 4bis, Fase 4, 10.3) | no (nessuna variante oltre la Fase 2) |
| 2. Un filtro nato dai trade deve reggere anche dove non è nato | Fase 3, punti 3-4 (definizione meccanica, +0,05 R sulle monete di controllo) | **sì**: ha scartato V-019 |
| 3. Trade estremi più severi | verifica 4 nuova, contro le entrate casuali tolte allo stesso modo (cambiata dopo la revisione: la forma «metà dell'R» puniva le uscite lontane) | no |
| 4. Robustezza delle soglie a zero | verifica 1, passo fisso | no |
| 5. Stabilità per tipo di mercato | verifica 3bis | no |
| 6. Collaudo con le versioni della ricerca, controllo all'avvio | regola 11; collaudo con le versioni lette da una sessione di prova | **sì** (log N-001) |
| 7. Scelta delle monete univoca, serie fino all'ultima candela con scambi | sez. 4bis, «regole dei dati»; elenco fisso | in parte (la regola dell'ultima candela non è servita su LINK) |
| 8. La frase del vault vale in qualunque sessione | **cambiata** dopo la revisione: vale **solo** al coordinamento | no (vault mai chiesto) |

Fonte della colonna centrale: `research/protocollo_4_note.md`, sez. 2; della colonna di destra: log di LINK6 (rilievo mio).
Il backlog dice: «il protocollo 4 ha messo in pratica tutte e otto le proposte, l'ottava cambiata» (voce P10).

### 6.6 Dalla revisione indipendente del protocollo 4

25 punti, tutti trattati prima dell'approvazione (`protocollo_4_note.md`, sez. 3); fra quelli che contano per chi
riscrive il gate: misurare le verifiche su più monete **contro il caso di ogni moneta** e non con l'R semplice, perché le
monete salgono e scendono insieme (punto 6); far eseguire al coordinamento, e non alla ricerca, le verifiche sulle monete di
controllo, perché altrimenti la ricerca punterebbe sulle famiglie che vanno bene ovunque (punto 9); riconoscere una
variante «nata dai risultati» dal log, non da come la si chiama (punto 10).

### 6.7 Dalla campagna LINK6: le sette proposte (aperte)

| Proposta (`campagne/LINK6/lezioni.md`, sez. 6) | Stato al 18 ottobre |
|---|---|
| 1. Non ripetere la stessa ricerca su un'altra grande moneta; se si continua, cambiare qualcosa di strutturale (idee fuori dal catalogo a una moneta, o la stessa regola su più monete insieme) | aperta (backlog P11); il proprietario ha detto di continuare, anche riscrivendo il gate, dopo questa storia |
| 2. La delega del proprietario nel messaggio di apertura | aperta |
| 3. Regola dei tentativi rimasti nella Fase 5 | aperta |
| 4. Un solo testo per il canale delle richieste | aperta |
| 5. Comandi della guida provati sotto il guardiano al Passo 0 | aperta |
| 6. Test dello scettico separato per direzione | aperta |
| 7. Ultracode: requisito o no, e come garantirlo | aperta |

### 6.8 Osservazioni mie per chi riscrive il gate (inferite dai file, da verificare)

1. **Il metodo è tarato, il terreno è povero.** Nel collaudo del protocollo 3 (quarto giro) la bilancia trova 104
   vantaggi inseriti su 104 da 0,2 R in su e 0 falsi su 90; in quello del protocollo 4 88 su 88 da 0,35 R e 0 su 90
   (`collaudo_3/esiti.md`; `collaudo_4/esiti.md`). Le 73 varianti vere di BTC51 e LINK6 non hanno dato una
   strategia: con questo catalogo, su queste monete, a 15 minuti-4 ore, nel 2020-2022, un vantaggio di 0,2 R dopo i costi
   non c'era (lezioni LINK6, sez. 5, punto 2). Riscrivere l'esame senza cambiare le idee rischia di ridare lo stesso esito.
2. **Un catalogo chiuso e lo stesso modello producono le stesse idee** (3.11, punto 3). Cambiare moneta non è cambiare
   idea.
3. **Più tentativi non hanno mai aiutato.** In BTC51 i 17 tentativi in più chiesti dal proprietario hanno dato un falso
   oltre la Fase 2 (V-030) e i due p-value più piccoli con R sotto 0,2 (V-039, V-040); in LINK6 i 6 in più hanno dato due
   dei tre p-value più piccoli con R sotto 0,1 (V-029, V-031). È quello che dice la tabella dei falsi candidati
   (`PROTOCOLLO_3.md`, sez. 8.3).
4. **Il p-value contro il caso premia anche cose che non pagano**: la larghezza dello stop (collaudo, giro 1), la direzione
   di fondo del periodo per gli short (3.11, punto 4). La soglia sull'R dopo i costi è stata la difesa che ha funzionato
   ogni volta.
5. **Le cose sapute non arrivano alla ricerca, per costruzione.** La separazione fra ricerca e storia evita le fughe dal
   vault, ma la sessione di BTC51 ha riscoperto l'idea del funding negativo senza sapere che la prima edizione l'aveva già
   vista perdere nei ribassi del 2022 (3.11, punto 1). Chi riscrive il gate deve decidere quali lezioni passano alla
   ricerca come **regole di metodo** (il protocollo 4 lo fa: sez. 3) e quali come **idee già bruciate**.
6. **I costi strutturali del terreno vanno misurati prima di approvare i parametri**: nel protocollo 2 la stima dello stop
   era sbagliata di 2-3 volte, e le quattro domande dello STOP del Passo 0 non toccavano la liquidazione (rapporto, «Lo
   STOP»): il problema è uscito solo in Fase 4, dopo tutto il budget (errori 4 e 12); nei protocolli 3 e 4 il bot non sa eseguire nessuna variante del catalogo (`bot_3.md`), e la prova di parità
   non è mai partita.
7. **Il processo funziona quando le sessioni si fermano e chiedono**: due difetti degli strumenti in BTC51 trovati dalla
   ricerca prima di qualunque variante; la sessione LINK6 che non si fida di un messaggio automatico. Costa tempo (4,69
   ore di pause in PANIERE, 8 ore di attesa in LINK6), ma non ha mai lasciato passare un numero sbagliato.

---

## Cose incerte o non verificate

* Il numero di test dei verificatori indipendenti del protocollo 3: 117 test delle statistiche nel `CHANGELOG.md`, 115 nel
  messaggio del commit `dd2ef133`; 551 in tutto nel diario (coerente con 117).
* L'ora della conferma dello STOP di LINK6: 08:01 UTC nelle note del coordinamento e in `STATO.md`, «routine delle 08:03»
  nel log della sessione (N-012). Probabilmente decisione e consegna del messaggio: non verificato.
* La misura degli ordini limite nel paper: non trovata; le risposte ops `0622` e `0623` del 18 ottobre (09:03 UTC, dopo
  il commit `672663b8`) non la contengono.
* Che le lezioni della campagna PANIERE non siano mai state unite al principale: dedotto dall'assenza dei file sul
  principale e da `docs/backlog.md` (P6); non ho cercato in tutti i branch.
* Le similitudini fra le varianti di BTC51 e LINK6 (3.11, punto 3) e i numeri d'insieme di BTC51 (R medio +0,022, 29 su 40,
  p medio 0,291, entrate casuali per direzione) sono calcoli miei sul log, non scritti in nessun file del progetto.
* Come il motore tratta le candele con il mark ma senza il last e i buchi del last di SOL, XRP e LTC (sezione 5, punto 3):
  non verificato nel codice.
* Il testo «versione 5» del proprietario, da cui deriva il protocollo 3: non è nel repository.
* Il diario del 17 ottobre dice che il funding è «l'unica famiglia» con p-value piccoli nelle due direzioni su BTC; il log
  di BTC51 mostra p 0,001 in tutte e due le direzioni anche per V-039 e V-040 (sezione 3.7).
* Gli orari della campagna PANIERE nel diario: «aperta alle 06:58 UTC» e «un'apertura alle 09:09» (ora italiana, cioè 07:09
  UTC) nella stessa giornata; non ho chiarito la differenza di 11 minuti.
* Gli orari del Passo 2 di BTC51 (12:12-12:59 UTC) sono quelli dei commit, che possono essere stati spinti a gruppi: non
  sono per forza gli orari del lavoro.
