# Verifica della prova 156 (`NOVANTAQUATTRESIMA.md`, commit 1b8dbce del 14 novembre 2026)
Modalità verifica di strategy-researcher: nessuna variante calcolata, nessun risultato guardato. Letti: le regole, `METODO` indirettamente tramite i
codici (`prima.py`, `novantatreesima.py`, `seconda.py`, `terza.py`, `ventiquattresima.py`, `cinquantaseiesima.py`, `asticella.py`) e le sezioni
finali di `NOVANTATREESIMA.md`. Le regole sono committate (1b8dbce, 14 novembre 08:20) prima di ogni calcolo.
Due sole misure sui dati (non sulle varianti), per decidere il punto 1: quante celle del pannello hanno un rendimento sopra il 20% con le due
letture possibili. Il pannello ufficiale (`sc.pannello()`) arriva al 12 novembre 2026 e contiene JCTUSDT.

**Esito: le regole si eseguono, ma con 3 ambiguità che cambiano i numeri (A1, A3, A5) e altre minori. Propongo le letture qui sotto; vanno
scritte come «Regole corrette dopo la verifica» in `NOVANTAQUATTRESIMA.md` (lo fa la sessione principale) prima del calcolo.**

## Ambiguità che cambiano i numeri

**A1. La fiammata: due definizioni nella stessa regola (punto 4.1).** Il testo dice «chiusura di F divisa per la chiusura di F−1 meno 1» e subito
dopo «si usa il rendimento già nel pannello (`sc.rendimenti`)». Ma `sc.rendimenti` è **apertura del giorno → apertura del giorno dopo** (e la
chiusura se manca l'apertura dopo; i valori mancanti diventano 0), non chiusura su chiusura. Le due letture danno fiammate diverse: su tutto il
pannello 6.561 celle sopra il 20% con `rendimenti`, 6.463 con chiusura/chiusura, 130 celle in cui le due dicono cose diverse (l'apertura del giorno
dopo non è uguale alla chiusura: scarto mediano 0,008%, oltre 1e-6 nel 56% delle celle).
Lettura proposta: **`R = sc.rendimenti(pan)`, fiammata nel giorno F se `R[F] > 0.20` (strettamente maggiore)**. Perché: (a) è la lettura che dà
la parte di regola «già nel pannello»; (b) è quella della misura di partenza (`voce12_venduto_2026.py`, riga 43: `(W < 0) & (R > 0.20)`);
(c) coincide con la posizione davvero tenuta (si esce all'apertura di D, che è la fine di R[D−1]): la perdita evitata è proprio quella misurata.
Per il ribilancio di D si guarda `R[idx−1]` (apertura D−1 → apertura D, nota alle 00:00 di D). La dicitura «chiusura» va corretta in «prezzo
delle 00:00 UTC». Nessuna colonna di prezzo nuova.

**A2. La fiammata conta solo se la moneta è venduta in quel momento? (punti 2 e 4).** Il punto 2 dice «se la moneta ha avuto una fiammata nel giorno
D−1, esce dal lato venduto»; il punto 4 dice che una moneta con fiammata nel lato comprato «non cambia». Non è scritto: (a) se la fiammata di una
moneta né venduta né comprata a D−1 (o comprata) apre l'esclusione, così che poi, se entra nel lato venduto a D, D+1…, è tolta; (b) se una moneta
che sta per ENTRARE nel lato venduto il giorno D (peso nullo a D−1) dopo una fiammata è tolta.
Lettura proposta: **la fiammata conta per ogni moneta, a prescindere dal peso a D−1; l'esclusione riguarda solo il peso negativo (venduto)
di G1 a ogni giorno di D…D+N−1; il lato comprato non si tocca mai.** Perché: è la lettura più semplice («una moneta uscita dal lato venduto»
=  non si vende per N giorni), non usa il peso di ieri (che dipende dalla banda), e il caso (b) è proprio quello della stretta dei venduti
(non si apre una vendita su una moneta appena esplosa). Il rapporto scrive quanti casi erano (a)/(b) rispetto a «solo se venduta a D−1» (descrittivo).

**A3. «Ribilanci» e il conto da zero (punto 2).** «N ribilanci consecutivi (D, D+1, …)»: G1 ribilancia ogni giorno, e la parentesi dice D+N−1, quindi
sono **N righe di giorni consecutivi di calendario**, non «i ribilanci in cui G1 cambia davvero i pesi». Lettura proposta: giorni di calendario
consecutivi (righe del pannello), anche quando la moneta nel frattempo non è venduta da G1.
Nuova fiammata durante l'esclusione: «riparte il conto da quel giorno» è ambiguo di un giorno. Lettura proposta: se la nuova fiammata è nel
giorno F' (nota a F'+1), l'esclusione dura fino a **F'+N incluso** (cioè N righe da F'+1), più lunga di quella in corso, mai più corta
(`fine = max(fine_vecchia, F'+N)`). Perché: la fiammata è nota solo alle 00:00 di F'+1, come per la prima; con N=3 e fiammata il giorno F' si evita di leggere «da F'» come uscita retroattiva.
Una fiammata il giorno stesso di rientro (D+N) vale: la fiammata di D+N−1 (nota a D+N) estende l'esclusione.

**A4. Il peso in contanti e la banda (punto 3).** Il testo è chiaro sulla banda («non cambia, il giorno dopo parte dai pesi di G1 senza
uscite»), ma serve dirlo in forma di codice. Lettura proposta: `W = vq.pesi_banda(...)` calcolata **una volta sola, intatta**; poi
`Wv = W.copy(); Wv[(W < 0) & esclusa] = 0` (nessuna rinormalizzazione; il lato comprato intatto); poi `te.conto(Wv, R, F, costo)` e
`cs.spese_a_limite(Wv, R, giorni, simboli, costo)` come in `prima.py` (G1) e in `novantatreesima.py` (`conta`). Il funding della parte tolta è
zero perché `fund_i = x * F` con x = 0. Chiusura e riapertura costano via la deriva dei pesi di `te.conto` e `cu.variazioni` (le uscite a D, le
riaperture a D+N se G1 è ancora venduto). Nessun conto a parte.
Conseguenza da scrivere, che non è un errore: la **deriva** divide per `1 + netto` (conto) o `1 + lordo` (spese a limite) di tutto il portafoglio, quindi
togliendo una gamba venduta cambia anche la deriva del lato comprato e le **sue spese cambiano di poco** (il prezzo e il funding del lato
comprato restano identici). Il punto 8.3 dice «vedere che il lato comprato sia identico»: va letto «identico in prezzo e funding; spese
quasi uguali (differenza scritta)».

## Ambiguità minori

**A5. Controllo di parità con N = 0.** La regola rimanda alla 155 e il comportamento è chiaro (confronto con `giorni_G1.csv.gz` valido su lordo,
funding, giro, monete entro 1e-12 fino al 29 settembre; spese diverse per la causa già nota; si ferma se qualcosa differisce prima del 30
settembre; G1 di confronto = ricalcolato oggi con N = 0). Con N = 0 la maschera è tutta falsa e `Wv = W`: la parità è su costruzione, ma
si fa lo stesso. Lettura: stesso codice di `novantatreesima.py` (colonne `lordo, spese, funding, netto, giro, monete`); ripetere il test
anche sul **G1 della prova 155 di oggi** (`risultati_novantatreesima/giorni_G1.csv.gz`, già calcolato con le stesse candele) come controllo in più su
spese e netto esatti: lo propongo, lo leggerebbe solo come parità di codice, non come risultato. Se non lo si vuole, basta il riferimento delle regole.
Il G1 di confronto va scritto «G1 ricalcolato oggi» e il suo esame accanto a quello del riferimento (come 155).

**A6. «Ogni anno positivo» per la variante** (7.2). Lettura: somma dei rendimenti giornalieri netti dell'anno > 0 (equivale a `mean × 365 > 0` di
`numeri_giorni` della 155). Anni per data UTC del giorno di tenuta; 2021 parte il 4 gennaio, 2026 finisce il 4 ottobre, parziali e contano.

**A7. Il paletto 4 anni su 5** (7.6). Lettura, già esplicita nel testo: **somma delle differenze giornaliere** (variante meno G1 ricalcolato)
nell'anno > 0, per 2021…2025; non il rendimento composto. «Differenza positiva» è strettamente > 0. Si scrivono anche la differenza 2026 e le
quote del 2026 e del 2021 sulla differenza totale (somma del 2026 e del 2021 divise per la somma di tutti i giorni; se la somma totale è ≤ 0 si
scrivono i valori assoluti e «non definita»).

**A8. t della serie settimanale** (7.3): `numeri_settimana` + `sharpe × √(settimane/52)` come in 155: coincide con media / (deviazione ddof=1 / √n)
perché Sharpe = media/dev × √52. Nessuna ambiguità. Serie settimanali: 4 gennaio 2021 (lunedì) → settimana che finisce il 4 ottobre 2026
(la prima e l'ultima sono intere; 301 settimane circa, come G1).

**A9. Il t della differenza** (7.5): semplice sui giorni, `media / (dev ddof=1 / √n)`, n = giorni dal 4 gennaio 2021 al 4 ottobre 2026 (tutti,
compresi quelli in cui la differenza è zero), come `t_semplice` della 155. Newey-West con 7 ritardi e t settimanale (somma delle differenze per
settimana) solo descrittivi. Nessuna ambiguità.

**A10. Sharpe corretto** (7.4): `ast.corretto_famiglie({"156 A": serieA, "156 B": serieB}, cand)` con `cand` = Sharpe, settimane, asimmetria,
curtosi delle serie settimanali (le due varianti e, per confronto, «156 G1 ricalcolato oggi»), taglio 0,5, come 155. Il conto passa da 318 a 320 nel
registro (non entra nella formula, che conta le famiglie). Nota: `mazzo()` già contiene le serie della 155 (A e B) e anche G1 («57 G1» del
riferimento): i nomi «156 A», «156 B» non devono coincidere con nessuno (altrimenti sostituirebbero la serie nel mazzo). `periodo()` taglia le
serie al 4 gennaio 2021 – 5 ottobre 2026 e toglie le settimane ferme iniziali: per G1/A/B non cambia nulla. Controlli con tagli 0,3 e 0,7 come in 155 (descrittivi).

**A11. «Deve battere G1» e il paletto «Sharpe sotto G1»** (7.5 e ultima frase della 7). Le condizioni elencate 1-6 non includono «lo Sharpe sopra
G1», ma la chiusa dice che una variante che «lascia lo Sharpe sotto G1» è non promossa. Lettura proposta: **si calcola anche lo Sharpe sopra
G1 (settimanale e giornaliero a 365 giorni), come condizione 7 aggiuntiva** (come `sharpe_sopra_G1` in 155); si scrive l'esito con e senza.
Va confermata dalla sessione principale: se non la si vuole, si dice.

**A12. Le monete e i giorni fuori dal pannello.** `R` mancante diventa 0 (nessuna fiammata). 133 celle hanno la chiusura ma non l'apertura del giorno
dopo (si usa la chiusura): coperte dal ripiego di `rendimenti`, nessuna scelta. Le monete fuori dall'universo del giorno hanno peso 0 in G1: non
cambia nulla. Il primo giorno (4 gennaio 2021) usa `R[idx−1]` del 3 gennaio: il pannello comincia il 1 gennaio 2020, nessun problema.

## Controlli descrittivi (8): letture proposte
* **8.1** «giornate-moneta uscite» = celle (giorno, moneta) con `W < 0` e maschera vera (cioè peso di G1 davvero tolto); «distinte» = monete diverse
  e anche episodi (serie consecutive di giorni). Quota del peso venduto tolto = somma del peso tolto / somma del peso venduto di G1 sui giorni
  (e media giornaliera). Per anno e per variante.
* **8.2** Una «uscita» = una cella (giorno D, moneta) tolta, non solo l'inizio dell'episodio, perché la maschera può restare accesa per N giorni
  (con doppia lettura: all'inizio dell'episodio descritto a parte). Rendimento cumulato (composto di `R`) da D a D+N−1 inclusi, e a D+1, D+3,
  D+7 **inclusi** (2, 4, 8 righe di R, cioè dal prezzo di D alle 00:00 alla chiusura del giorno indicato). L'«altro lato venduto» = le altre monete
  con `W < 0` e non escluse negli stessi giorni, media semplice per cella (non pesata), media, mediana e quota > 0 per anno. Dove la moneta
  esce dal pannello prima, R = 0 (come il motore).
* **8.3** «Come nella voce 12»: la voce 12 usa un altro motore (`revisione_g1n/nucleo.py`, lati fissi) e somme non composte dall'1 gennaio.
  `te.conto` dà per lato solo il totale (colonne `long`, `short`, a mercato). Lettura: prezzo = somma di `x·R`, funding = somma di `x·F`,
  spese = quelle di `te.conto` (a mercato) per lato, totale = `long`/`short` di `te.conto`; **non** si prova a rifare le spese a limite per lato
  (la deriva cambia). Il rapporto lo dice: a mercato per lato, a limite solo nel totale.
* **8.4** JCTUSDT e TRXUSDT: il pannello ufficiale arriva al 12 novembre 2026 e contiene JCTUSDT, quindi si legge `R` del pannello (nessun dato
  scaricato). Una riga per ciascuna: fiammata sì/no con la regola A1 e se il peso di G1 sarebbe stato tolto il 9 novembre (G1 oggi non è
  calcolato oltre il 4 ottobre, quindi si risponde «la regola avrebbe escluso la moneta dal 9 novembre» solo sulla fiammata, senza pesi). Se si
  vuole anche il peso di G1, serve estendere `FINE`: **non lo farei** (fuori dalle regole). TRXUSDT: una fiammata il 28 ottobre c'era sì/no
  secondo `R`; si scrive il numero.
* **8.5** Discesa massima settimanale con `numeri_settimana` (composta sulla serie settimanale); correlazione fra le serie settimanali di G1 e
  delle varianti; «famiglia di G1 o no» = se G1 e la variante stanno nello stesso gruppo di `corretto_famiglie` (campo `gruppo`) a taglio 0,5.
* **Prova di coerenza dell'implementazione (non esame).** La misura di partenza dà per il lato venduto 176 giornate-moneta con fiammata nel 2026
  (85 nel 2021, 75 nel 2024), contate dal 1° gennaio e con un altro motore. Si scrive il conto di oggi (G1 della prova, dal 4 gennaio 2021) accanto,
  senza soglia: una differenza grande è un avviso di errore di lettura di A1, non un risultato.

## Le fonti (controllo a memoria: non ho strumenti di ricerca in rete in questa sessione, quindi non verificato online)
* Brunnermeier e Pedersen, «Market liquidity and funding liquidity», *RFS* 22(6), 2009: **esiste** e parla delle spirali di margine e di
  liquidità; non parla in particolare di «stretta dei venduti» con +20% in un giorno, ma l'idea (chiusure forzate che spingono il prezzo) è coerente.
* Diamond e Verrecchia, *JFE* 18(2), 1987, «Constraints on short-selling and asset price adjustment to private information»: **esiste**, ma dice
  che il vincolo alla vendita allo scoperto **rallenta l'aggiustamento dei prezzi alle cattive notizie**; non è una fonte per la stretta dei
  venduti né per la continuazione dopo un balzo. Proposta: toglierla dal «perché» (o dire che non c'entra con la continuazione).
* Liu, Tsyvinski e Wu, «Common risk factors in cryptocurrency», *JF* 77(2), 2022: **esiste**; trova il momento (rendimenti delle ultime 1-4
  settimane predicono i successivi) e la dimensione. È un effetto **settimanale**, non da un giorno solo: sostiene l'ipotesi solo per analogia.
* Jegadeesh, «Evidence of predictable behavior of security returns», *JF* 45(3), 1990: **esiste**; inversione a **un mese** nelle azioni (la
  settimana è Lehmann 1990), non giornaliera. Va letta come «l'inversione di breve esiste nelle azioni», non come prova per le crypto.
Nessuna delle citazioni è falsa; due (Diamond-Verrecchia, Liu-Tsyvinski-Wu) dicono meno di quanto il testo lascia pensare. Non cambia le regole.

## Il resto della consegna (nessuna ambiguità)
Registro: `research/trials/novantaquattresima.csv` con `prove.registra` come `novantatreesima.py` (seme 156, commit, parità come riga di controllo a
parte); controlli descrittivi nel rapporto. Prova senza 1 ora di candele: stesse spese di G1 (causa nota). Periodo 4 gennaio 2021 – 4 ottobre 2026
(`se.INIZIO`, `pr.FINE`, il 5 ottobre escluso, che è un lunedì: l'ultima settimana intera finisce domenica 4). Nessun file di dati nuovo, nessun
scarico, nessun cambio ai motori.

## Domande per la sessione principale
1. Confermare A1 (la fiammata si legge dal pannello `rendimenti`, apertura → apertura, e il testo «chiusura» si corregge) e A3 (durata: N giorni di
   calendario, estensione `max` con nuova fiammata, fino a F'+N).
2. Confermare A2 (fiammata conta anche per monete non vendute il giorno prima) e A11 (Sharpe sopra G1 come condizione aggiuntiva).
3. Togliere o ridimensionare Diamond e Verrecchia nel «perché» (non sostiene la continuazione).
