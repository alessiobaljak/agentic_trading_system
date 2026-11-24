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
   finestra; sono circa 600-650 e non si sceglie a mano.
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
   media, esposizione netta media; la perdita massima dal picco (sulla serie dei giri).
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
    Se il gruppo (a) ha meno di 5 conti in una settimana, quella settimana resta in cassa e si scrive.
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
