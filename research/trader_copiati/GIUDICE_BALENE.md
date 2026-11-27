# Il giudice delle balene: copiare solo i conti che guadagnano con la scelta delle monete (idea 152 del registro)

Regole scritte il 24 novembre 2026 dalla sessione principale, **prima di guardare qualunque numero per conto**. Il proprietario
(22 novembre): le idee nuove si provano da sole, senza aspettare il suo via libera. Nessuna spesa: il giudizio lo dà la sessione
principale, dentro l'abbonamento, leggendo un foglio preparato da uno script.

**È una misura in avanti, non una prova nel conto**: non cambia G1, né il paper né il demo, e non entra nel conto delle prove finché non
diventa una strategia (con regole scritte prima, backtest-auditor, flusso di sempre). Si somma ai conti già copiati da
`conto_hyperliquid.py` (`HYPERLIQUID.md`, `HYPERLIQUID_CONTO.md`) senza toccarli.

## Il perché
* La copia di tutti i grandi conti (idea 132) in novembre ha fatto +33,6% (migliori del mese) e +62% (le 20 balene), ma con comprato meno
  venduto in media tra −1,4 e −1,9: hanno guadagnato **stando venduti durante il crollo**, cioè con la direzione del mercato, non con
  la scelta delle monete. Una copia così perde appena il mercato risale.
* Un classificatore a numeri fissi (guadagno del mese) premia proprio quei conti; serve separare **la parte del mercato** dalla **parte
  propria** e guardare la costanza. Il giudizio finale su un conto (una scommessa sola? una moneta sola? un colpo di fortuna?) lo dà chi
  legge, con la stessa logica dei fatti gravi (`research/notizie/FATTI_GRAVI.md`).
* Dati nostri, mai usati per un giudizio per conto: posizioni dal 2 novembre (`hyperliquid/posizioni_*.jsonl.gz`, ogni 4 ore), conti
  scelti (`scelti_*.json`) e, dal 22 novembre, i 600 conti della mappa (`liquidazioni_*.jsonl.gz`, `LIQUIDAZIONI.md`).

## Cosa giudica la sessione (il foglio per conto, ogni lunedì)
Lo script `giudice_balene.py` (da scrivere prima del primo lunedì, **non cambia queste regole**) prepara per ogni conto del gruppo il foglio
`giudice_balene/AAAA-MM-GG.md`. Il prezzo di ogni moneta viene dai nostri file (valore diviso quantità nella riga delle posizioni, o i
prezzi medi della raccolta delle liquidazioni): **nessun dato di Binance** nel giudizio. Finestra: le **4 settimane** finite il lunedì
(le prime due volte, quelle che ci sono dal 2 novembre; sotto i 10 giorni di dati il conto non si giudica).
1. **Il gruppo**: i conti di `scelti_*.json` e quelli della mappa delle liquidazioni con almeno 10 giri letti con posizioni aperte nella
   finestra; sono circa 600-650 e non si sceglie a mano (il numero non torna e il gruppo del 30 novembre è dei soli conti scelti: nota
   del 27 novembre, in fondo).
2. **Guadagno per moneta** (in dollari e in % del valore medio del conto): per ogni intervallo fra due giri, quantità con il segno
   all'inizio × variazione del prezzo; si somma per moneta. Non conta il realizzato dichiarato dal conto: conta solo ciò che si vede
   nelle nostre letture. Spese e funding non si contano nel giudizio (si contano nella misura).
3. **Parte del mercato e parte propria**: il «mercato» è il paniere uguale di Bitcoin, Ether e Solana, nello stesso intervallo.
   Parte del mercato = esposizione netta in dollari all'inizio dell'intervallo (comprato meno venduto) × rendimento del paniere.
   Parte propria = guadagno totale meno parte del mercato; per moneta = quantità × (rendimento della moneta meno rendimento del paniere).
   Si scrivono: totale, parte del mercato, parte propria, quota della parte propria sul totale.
4. **Costanza**: numero di giorni (UTC) con parte propria positiva su quelli osservati; settimane su 4 con parte propria positiva; il
   guadagno proprio del giorno migliore diviso il guadagno proprio totale (se oltre il 50% è un colpo solo); numero di monete con parte
   propria positiva su quelle toccate.
5. **Dimensione delle scommesse**: valore medio e massimo di una posizione sul valore del conto, leva media, numero di monete aperte in
   media, esposizione netta media; la perdita massima dal picco (sulla serie dei giri). (Leva media e massima nel foglio dal 27 novembre:
   nota in fondo.)
6. **Il giudizio**, caso per caso, in tre voci: **costante** (parte propria positiva su almeno 4 giorni su 7 nella media, almeno 3
   settimane su 4, giorno migliore sotto il 50%, parte propria sul totale almeno 40%, almeno 3 monete con parte propria positiva),
   **mercato** (guadagno quasi tutto della parte del mercato), **caso** (tutto il resto: colpo solo, una moneta sola, leva estrema). Le
   soglie sono una guida: chi legge può spostare un conto di voce con una riga di perché, ma **non può promuovere a «costante» un
   conto che non rispetta il giorno migliore sotto il 50% e il guadagno proprio positivo**.
7. Un conto con meno di 100.000 dollari di valore o meno di 5 monete toccate in 4 settimane non si giudica (resta fuori).

## Quando e come si salva (prima dei prezzi)
8. **Ogni lunedì** nel giro delle 04:17 (il primo giro con i dati della domenica), **prima di guardare la settimana che segue** e prima del
   conto copiato di `HYPERLIQUID_CONTO.md`. Il foglio dice solo le settimane già chiuse.
9. Il giudizio si scrive in `giudice_balene/giudizi/AAAA-MM-GG.json` (indirizzo, voce, motivo breve) e si **committa e si pusha subito**;
   l'ora del commit è la prova. Un giudizio committato non si cambia; una correzione si scrive sotto con la sua ora e conta dalla data
   dopo. Un lunedì saltato si scrive nel diario e non si recupera. L'elenco dei «costanti» del lunedì resta valido per le sette giorni
   dopo, fino al lunedì seguente.

## La misura (fissata ora, prima di ogni giudizio)
10. Tre conti copiati in avanti, con lo stesso metodo di `conto_hyperliquid.py` (pesi dalle posizioni al giro, prezzi di Binance,
    spese 0,05% a mercato e scarto 0,01% su Bitcoin, Ether e Solana, 0,02% sulle altre, funding vero) e a **esposizione uguale** fra i tre:
    (a) i soli conti «costanti» del lunedì; (b) tutti i conti del gruppo giudicabili; (c) i «mercato» e «caso» da soli (controllo).
    Se il gruppo (a) ha meno di 5 conti in una settimana, quella settimana resta in cassa e si scrive. (Come si conta: nota del 27
    novembre, in fondo; il formato del file del giudizio della regola 9 è nella stessa nota.)
11. Il confronto è con **G1** nelle stesse settimane (stesso scarto di spese) e con il solo comprato meno venduto: si scrivono anche la
    correlazione settimanale con il rendimento del paniere (se il «costante» è solo mercato, serve a poco) e il rendimento a esposizione
    netta zero (la parte propria da sola).
12. **Quando si giudica**: dopo **8 settimane** di giudizi (il primo lunedì utile è il 30 novembre, quindi il 25 gennaio 2027; i conti del
    giudizio del lunedì entrano solo dalla settimana dopo). Una settimana è la misura; i numeri si scrivono ogni lunedì ma nessuno
    li giudica prima.
13. **La soglia che fa dire «serve»**, tutte insieme: (a) batte (b) di almeno **+0,3 punti percentuali a settimana** in media, con t sulle
    settimane almeno 2 e almeno **6 settimane su 8** meglio; (b) a esposizione netta zero il rendimento medio di (a) è positivo; (c)
    la correlazione settimanale di (a) con il paniere non è più alta di quella di (b) di oltre 0,2; (d) (a) batte G1 per rendimento
    medio a settimana oppure ha la stessa media con meno oscillazione (deviazione standard delle settimane almeno del 25% più bassa);
    (e) nessuna settimana con perdita oltre il 15% di (a). Se manca una sola condizione: si va avanti altre 8 settimane e poi si chiude.
14. Se serve, si propone una strategia (regole scritte prima, nel conto delle prove con le famiglie, backtest-auditor; il paper lo decide la
    sessione principale, il demo e i soldi veri il proprietario). Se dopo **16 settimane** non serve, il giudice si ferma e si scrive
    il perché, a meno che il proprietario dica altro.

## Limiti dichiarati
Con 8 settimane non si distingue davvero la costanza dalla fortuna: la misura dice se vale la pena una prova vera, non la sostituisce. I
conti dei grandi cambiano indirizzo e strategia; i giri ogni 4 ore perdono i movimenti dentro l'intervallo; un conto che chiude prima di un
giro non si vede.
* (24 novembre, dalla prova dello script sui dati fino al 23 novembre, nessun giudizio) Il valore del conto cambia anche con versamenti e
  prelievi: la discesa dal picco e le percentuali sul valore medio ne risentono (un conto da 85 milioni con «discesa» −99%). Il giudizio
  guarda soprattutto la parte propria e la costanza; la discesa si legge con questa cautela.

## Note del 27 novembre 2026 (audit del 26 novembre, problemi raccolta-4 e raccolta-6), scritte prima del primo giudizio
* **Il gruppo del 30 novembre.** La mappa delle liquidazioni comincia il 22 novembre alle 08:09 UTC: lunedì 30 ha 8 giorni di dati nella
  finestra, meno dei 10 richiesti, quindi **il primo gruppo è fatto solo dei conti scelti** (`scelti_*.json`: migliori del mese e balene).
  Prova a secco dell'audit con i dati fino al 26 novembre alle 20:18: 443 conti letti, 24 giudicabili, tutti dai file scelti; voci proposte
  costante 0, mercato 14, caso 10. Il foglio lo scrive da solo (quanti giudicabili vengono dai conti scelti e quanti dalla sola mappa, e la
  frase sul gruppo quando la mappa ha meno di 10 giorni).
* **Regola 1, «circa 600-650».** Il numero non torna: con la scelta della mappa per valore in classifica metà dei 600 conti non ha
  posizioni a leva (225 con il conto a leva a zero nel giro del 26 novembre alle 20:18); dai dati fino al 26 novembre 352 indirizzi della
  mappa hanno almeno 10 giri con posizioni e 119 passano anche i limiti della regola 7 (verifica dell'audit). Due cambi alla raccolta,
  dalla scelta di lunedì 30 novembre: la mappa tiene i 600 conti con più posizioni aperte fra i primi 1.500 della classifica
  (`LIQUIDAZIONI.md`, nota del 27 novembre), e le **balene** di `hyperliquid.py` saltano i conti con il conto a leva a zero, cioè sotto i
  10.000 dollari (nel giro del 27 novembre alle 02:13 13 dei 40 conti copiati non avevano posizioni; 4 delle 20 balene della settimana,
  con 45,1, 33,6, 31,2 e 29,0 milioni in classifica, avevano il conto a leva a 566, 0, 0,0007 e 0 dollari; fonte:
  `posizioni_2026-11.jsonl.gz` e `scelti_balene_2026-11-23.json`). Il gruppo resta senza scelte a mano. I conti nuovi della mappa hanno dati dal 30 novembre e si giudicano dal 14
  dicembre (10 giorni); il 7 dicembre entrano quelli che erano già fra i 600 della settimana del 23 novembre.
* **Regola 5 nel foglio.** Leva media e massima = esposizione lorda (somma dei valori delle posizioni aperte) diviso il valore del conto,
  giro per giro (prima la leva media non si calcolava: la variabile c'era ma restava vuota); con il peso medio e massimo di una posizione e
  le monete aperte in media. Per i conti della mappa le posizioni sotto i 10.000 dollari non sono salvate: leva e pesi un poco più bassi
  del vero. La voce «caso» per leva estrema la decide chi legge (regola 6).
* **Il file del giudizio** (regola 9), letto dalla misura: `{"lunedi": "AAAA-MM-GG", "scritto_il": "AAAA-MM-GG HH:MM", "giudizi":
  [{"indirizzo": "0x…", "voce": "costante" | "mercato" | "caso", "motivo": "…"}], "correzioni": [{"ora": "AAAA-MM-GG HH:MM", "indirizzo":
  "0x…", "voce": "…", "motivo": "…"}]}`. In `giudizi` un elemento per ogni conto giudicabile del foglio, con l'indirizzo intero (è nel
  `.json` del foglio); `scritto_il` è l'ora UTC in cui il giudizio è scritto (se manca, la misura lo fa valere dal lunedì alle 08:00);
  una correzione conta dal giorno dopo la sua ora.
* **La misura delle regole 10-11, come si conta** (`conto_hyperliquid.misura_giudice`; la chiama il conto della copia del mattino, e da
  sola `python3 -m research.trader_copiati.conto_hyperliquid --giudice`; scrive `giudice_balene/MISURA.md` e `misura.json`; senza giudizi
  non fa niente). A ogni giro valgono i conti del giudizio già scritto (`scritto_il` prima dell'ora del giro), fino al giudizio del
  lunedì dopo e al più 8 giorni dal suo lunedì: dopo un lunedì saltato i tre conti restano in cassa. Le posizioni vengono da
  `posizioni_*.jsonl.gz` e, per i conti della mappa, da `liquidazioni_*.jsonl.gz`. Ogni conto letto con valore sopra zero e posizioni
  abbinate ai perpetui di Binance va a esposizione 2 (come il gruppo «a esposizione uguale» di `HYPERLIQUID.md`), si fa la media, e il
  totale va a esposizione **2 per tutti e tre** i conti copiati («a esposizione uguale fra i tre»). Entrata all'ora dopo il giro, prezzi
  orari, spese (0,05% più lo scarto: 0,01% su Bitcoin, Ether e Solana, 0,02% sulle altre) e funding di Binance, come
  `conto_hyperliquid.py`. (a) i «costanti», in cassa se sono meno di 5; (b) tutti i conti del giudizio; (c) «mercato» e «caso». Per ogni
  settimana (dal lunedì 00:00 UTC; un tratto conta nella settimana della sua entrata): il netto; il «solo comprato meno venduto»
  (esposizione netta × paniere uguale di Bitcoin, Ether e Solana, ribilanciato a ogni tratto, senza spese); il netto a esposizione netta
  zero (netto meno il solo comprato meno venduto); il paniere; G1 dall'ultimo ricalcolo del confronto settimanale
  (`gate2/exports/ricalcolo_g1_ricerca_*.json`: lordo meno spese a mercato meno funding, solo le settimane con 7 giorni); dalla terza
  settimana completa la correlazione settimanale con il paniere. Una settimana è completa quando i prezzi di Binance arrivano al lunedì
  dopo; se manca il prezzo di una moneta tenuta, il conto si ferma lì finché l'archivio non lo pubblica (come `conto_hyperliquid.py`).
  Nessuno guarda la relazione fra i tre prima del 25 gennaio 2027 (regola 12).
