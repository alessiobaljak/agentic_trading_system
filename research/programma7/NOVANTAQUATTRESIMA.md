# Prova 156 — G1 che esce dal lato venduto dopo una fiammata (voce 12 di `MIGLIORARE_G1.md`)

Regole scritte il 14 novembre 2026 da strategy-improver, **prima di ogni calcolo**: nessun risultato nuovo guardato. Le uniche cifre usate sono
quelle già scritte nella misura (`misure_g1/voce12_rapporto.md`, 12 novembre) e nelle voci 10 e 11. Le regole le committa la sessione principale,
che poi le fa verificare da strategy-researcher; il giudizio lo dà backtest-auditor. Il numero 156 è libero (ultima nel registro: 155).
**Non spegne e non sostituisce niente**: G1 resta com'è (paper e demo), la variante entra accanto; sostituire G1 lo decide solo Alessio.
`DRY_RUN` resta vero. Il tetto per moneta non si ripropone: è la prova 152.

## 1. Perché questa e non un'altra regola del rapporto
Il rapporto propone due strade: il tetto di peso (già prova 152) e l'uscita dopo +20% in un giorno. Si prende la seconda perché è quella che
guarda **il comportamento della moneta**, non la forma dei pesi, e perché i due casi in avanti sono proprio fiammate: JCTUSDT +303% l'8 novembre
(venduto nel paper, voce 11) e TRXUSDT al 34,7% di un lato il 29 ottobre (voce 10, la causa lì resta non chiusa: non si dice che sia una
fiammata). Il tetto non avrebbe fermato una moneta piccola a peso piccolo che sale del 300%; l'uscita sì, dal giorno dopo.

## 2. Il perché economico, e l'avviso onesto
* **Perché dovrebbe funzionare.** Chi è venduto allo scoperto su una moneta che sale molto di giorno in giorno subisce richieste di margine e
  chiude comprando, e la chiusura fa salire ancora il prezzo (la «stretta dei venduti», *short squeeze*): Brunnermeier e Pedersen, «Market
  liquidity and funding liquidity», *Review of Financial Studies* 2009 (le spirali del margine); sul vincolo di vendita allo scoperto,
  Diamond e Verrecchia, *Journal of Financial Economics* 1987. Nelle crypto il rendimento di breve periodo tende a continuare, non a tornare
  indietro: Liu, Tsyvinski e Wu, «Common risk factors in cryptocurrency», *Journal of Finance* 2022 (momento a 1-4 settimane positivo). Se dopo
  +20% la moneta continua a salire per qualche giorno, il lato venduto che la tiene perde ancora; l'uscita evita quella parte.
* **Avviso onesto, il più importante.** Il -119,3 punti del 2026 del rapporto è la perdita **del giorno della fiammata stesso**: nessuna regola che
  agisce dopo lo recupera (si esce solo dal ribilancio dopo). Il guadagno possibile è solo la continuazione nei giorni seguenti, e l'uscita
  perde invece il ritorno giù, che è il caso opposto e comune (le monete piccole gonfiate dopo un balzo spesso tornano indietro; in azioni il
  breve periodo è di inversione, Jegadeesh, *Journal of Finance* 1990). Dal rapporto non si sa quale dei due prevale: lo dirà la prova. Un'altra
  cautela: la misura ha guardato 2021-2026 sul lato venduto, quindi il 20% e l'idea **non sono fuori campione**; gli anni prima del 2026 sono
  una difesa parziale, non una prova pulita. Le fonti sono citate a memoria: strategy-researcher le controlla nella verifica.

## 3. La base: G1 com'è
Come nella prova 155 (`NOVANTATREESIMA.md`): `programma7/prima.py` (funzione `esegui`), stesse scelte delle monete (le 100 più scambiate, segnale
meno il funding dei 7 giorni, banda 20%/40%, inverso della volatilità a 30 giorni, ogni lato al 100%, ordine limite un'ora poi mercato). Periodo
**dal 4 gennaio 2021 al 4 ottobre 2026 compreso** (`FINE` di `prima.py`: il 5 ottobre escluso). Costi confermati dal proprietario il 7 novembre:
0,05% a mercato, 0,02% a limite, scarto 0,01% su BTC, ETH, SOL e 0,02% sulle altre, funding vero. Nessun vault per data.

## 4. La regola (fissata qui)
Per ogni giorno D, alle 00:00 UTC, con i prezzi noti a quell'ora:
1. **La fiammata**: una moneta ha una fiammata nel giorno F se la sua chiusura UTC di F divisa per la chiusura di F−1 meno 1 è **strettamente
   maggiore di 0,20**. Si usa il rendimento giornaliero già nel pannello (`sc.rendimenti`); il rendimento del giorno F−1 per il ribilancio di D
   è la riga `idx−1` (nota a 00:00 di D). Nessun dato di D o dopo. Il 20% viene dalla misura e **non si tocca**.
2. **L'uscita**: se la moneta ha avuto una fiammata nel giorno D−1, **esce dal lato venduto** dal ribilancio di D, e ci resta fuori per N ribilanci
   consecutivi (D, D+1, ..., D+N−1). Una nuova fiammata durante l'esclusione **riparte il conto** da quel giorno. Passati N ribilanci senza nuove
   fiammate, la moneta rientra secondo le regole normali di G1 (banda, segnale).
3. **Come si applica**: G1 decide i pesi come sempre (`vq.pesi_banda`: la banda e la sua memoria **non cambiano**, il giorno dopo la banda
   parte dai pesi di G1 senza uscite). Sul peso venduto finale, **il peso delle monete escluse diventa zero e non si ridistribuisce**: gli altri
   pesi del lato venduto restano quelli di G1 e il lato venduto scende sotto il 100% quel giorno (la parte tolta resta in contanti). Il lato
   comprato non cambia mai. Si sceglie «in contanti» e non «ridistribuito» per non concentrare il lato, che è il difetto della prova 152.
4. **Solo il lato venduto**: una moneta con fiammata che è nel lato comprato non cambia. Una moneta esclusa non si compra al suo posto.
5. **Costi**: il peso modificato passa per gli stessi conti di G1 (`te.conto`, `cs.spese_a_limite`): chiudere una posizione e riaprirla costa le
   commissioni confermate con l'esecuzione di G1 (limite per un'ora, poi mercato), funding vero sulla parte tenuta, zero sulla parte uscita.

## 5. Le varianti (fissate, al massimo 2, nessuna dopo i risultati)
* **A: N = 3** ribilanci (circa tre giorni dopo la fiammata).
* **B: N = 7** ribilanci (una settimana, la finestra stessa del segnale del funding).
La sola cosa che cambia fra le due è la durata; soglia, lato e destino del peso sono identici. Nessun'altra soglia o durata si prova. Conta
**2 prove**: il conto del registro passa da 318 a **320**. Con N = 0 la variante è G1 (serve al controllo di parità).

## 6. Il controllo di parità, prima di tutto
Con N = 0 la regola non toglie nulla e i giorni devono coincidere con `risultati_prima/giorni_G1.csv.gz`, letto **come nelle aggiunte della prova
155** (`NOVANTATREESIMA.md`, sezioni «Aggiunta» e «Seconda aggiunta»): sono valide lordo, funding, giro e numero di monete entro 1e-12 fino al
29 settembre 2026; le spese oggi differiscono dal riferimento nei giorni senza candele a 1 ora (riferimento 6.105 variazioni a mercato su 117.045,
oggi 137), causa già verificata, perciò **il G1 di confronto è quello ricalcolato oggi con N = 0**, stesso pannello e stesse candele. Se lordo,
funding, giro o numero di monete differiscono prima del 30 settembre, ci si ferma e lo si scrive. Il rapporto scrive anche l'esame di G1 di
oggi accanto a quello del riferimento.

## 7. L'esame (regole approvate dal proprietario il 9 novembre, più il paletto contro il guardare il risultato)
Una variante passa solo se **tutte** queste sono vere, sul periodo del punto 3:
1. netto dopo i costi positivo;
2. **ogni anno positivo** (2021 e 2026 sono anni parziali e contano tutti e due);
3. t almeno 3 (serie settimanale, media / (deviazione / radice del numero di settimane));
4. Sharpe corretto almeno **0,80** con `corretto_famiglie` di `programma6/asticella.py` (mazzo completo, taglio 0,5; le due varianti entrano
   come serie nuove a settimane intere dal lunedì 4 gennaio 2021), come in `audits/repro/prova28_2026-11-11.py`;
5. **deve battere G1** sullo stesso periodo: differenza giornaliera (variante meno G1 ricalcolato) con media positiva e **t semplice almeno 2**
   (media / (deviazione / radice di n)); come controlli descrittivi anche il t settimanale e quello robusto (Newey-West, 7 ritardi);
6. **il paletto contro il guardare il risultato**: l'idea nasce dai numeri del 2026, quindi nel conto per anno **almeno 4 anni su 5 fra il 2021 e
   il 2025 devono avere la differenza con G1 positiva** (somma delle differenze giornaliere dell'anno > 0). Si scrive anche la differenza del 2026
   (che non conta per il paletto) e quanta parte della differenza totale viene dal 2026 e dal 2021.
Una variante che migliora solo il 2026 e il 2021, o che riduce la perdita ma lascia lo Sharpe sotto G1, è **non promossa**; i numeri si scrivono
lo stesso. Il giudizio sul risultato non lo dà chi lo calcola.

## 8. I controlli descrittivi (senza soglia)
1. **Quante uscite**: giornate-moneta uscite dal lato venduto (e distinte), per anno e per variante, e quota del peso venduto tolto.
2. **Cosa fanno le monete escluse dopo**: per ogni uscita, il rendimento cumulato della moneta da D a D+N−1 e a D+1, +3, +7 (chiusura a chiusura),
   media, mediana e quota che sale ancora, per anno; accanto, lo stesso per le altre monete del lato venduto negli stessi giorni. Serve a dire
   se continuano a salire (l'uscita aiuta) o tornano giù (l'uscita costa).
3. **Il lato venduto e quello comprato da soli**, ogni anno, per G1 e per le varianti (prezzo, funding, spese, totale come nella voce 12), per
   vedere che il lato comprato sia identico e dove sta la differenza.
4. Il caso JCTUSDT (8 novembre 2026, fuori periodo e solo in avanti): se la regola, applicata ai prezzi pubblici, avrebbe tolto la moneta il 9
   novembre; solo una riga, senza entrare nell'esame. Lo stesso per TRXUSDT del 29 ottobre solo se una fiammata c'era davvero.
5. Discesa massima settimanale di G1 e delle varianti; correlazione delle serie con G1 (famiglia di G1 o no secondo il `TAGLIO`).

## 9. Cosa si consegna
Rapporto in `research/programma7/RISULTATI_NOVANTAQUATTRESIMA.md`, serie giornaliere in `risultati_novantaquattresima/`, script
`novantaquattresima.py`, varianti A e B (anche se falliscono) in `research/trials/novantaquattresima.csv` con il formato di
`novantesima.csv`; a schermo al massimo 20 righe. Nessun file del bot toccato.

## 10. Testo della riga del registro
| 156 | G1 che esce dal lato venduto per N ribilanci (A: 3, B: 7) dopo una fiammata di oltre +20% in un giorno (peso in contanti, lato comprato invariato), dal 4 gen 2021, esame con paletto «4 anni su 5 del 2021-2025 meglio di G1»; voce 12 del piano di G1, short squeeze e momento di breve periodo (Brunnermeier-Pedersen RFS 2009, Liu-Tsyvinski-Wu JF 2022) (`programma7/NOVANTAQUATTRESIMA.md`) | 2 | da fare | da fare |

## Regole corrette il 14 novembre 2026 dopo la verifica, prima di ogni calcolo (sessione principale)
La verifica di strategy-researcher (`VERIFICA_NOVANTAQUATTRESIMA.md`) ha trovato ambiguità; nessuna variante è stata calcolata (sono
stati solo contati i giorni-moneta oltre il 20% per le due letture del punto 1). Le letture che valgono:
1. **La fiammata** è il rendimento tenuto di G1: `sc.rendimenti` (dall'apertura delle 00:00 UTC del giorno F all'apertura del giorno
   dopo), **strettamente maggiore di 0,20**. Il testo «da chiusura a chiusura» sopra è sostituito da questo: è la lettura della misura
   di partenza (`misure_g1/voce12_venduto_2026.py`) ed è nota all'apertura del giorno F + 1, quando si decide.
2. **Conta per ogni moneta**, venduta o no il giorno F; si toglie solo il peso **negativo** di G1 (una moneta comprata non si tocca).
3. **N giorni di calendario**: dopo una fiammata nel giorno F la moneta non può essere venduta nei giorni F + 1 … F + N. Una fiammata
   nuova nel giorno F' mentre è fuori sposta la fine a max(fine in corso, F' + N).
4. **Il peso in contanti**: la banda di G1 resta com'è; dopo la banda si mette a zero il peso negativo delle monete escluse, senza
   ridistribuirlo; i conti con `te.conto` e `cs.spese_a_limite` sulla matrice nuova; il funding della parte tolta è zero. «Lato comprato
   identico» vale per prezzo e funding; le spese possono differire di poco.
5. **Parità con N = 0**: come nella prova 155 (lordo, funding, giro e monete uguali a `risultati_prima/giorni_G1.csv.gz` fino al 29
   settembre 2026 entro 1e-12; le spese differiscono per le candele a 1 ora, causa verificata il 13 novembre); G1 di confronto è
   quello ricalcolato oggi con N = 0.
6. **L'esame**: ogni anno positivo e il paletto «4 anni su 5 fra il 2021 e il 2025 meglio di G1» sulla **somma** dei rendimenti netti
   giornalieri dell'anno; t della differenza semplice sui giorni (media / (deviazione / √n)), almeno 2 con media positiva; **in più lo
   Sharpe della variante sopra quello di G1 sullo stesso periodo** (come nella prova 155); Sharpe corretto con `corretto_famiglie` e il
   mazzo completo, serie «156 A» e «156 B»; conto del registro da 318 a 320.
7. **Le fonti**: Brunnermeier e Pedersen 2009 restano (spirali di margine). Diamond e Verrecchia 1987 parlano del divieto di vendere
   allo scoperto che rallenta l'arrivo delle cattive notizie, non della continuazione dopo un balzo: non sostengono la regola. Liu,
   Tsyvinski e Wu 2022 trovano un momento a 1-4 settimane, non a un giorno; Jegadeesh 1990 è un'inversione a un mese nelle azioni.
   Quindi **la ragione per una continuazione a pochi giorni è debole**: si scrive, non si cambia la regola.
8. Il controllo sul caso di JCTUSDT e TRXUSDT (8.4) si fa solo sulla fiammata, con il pannello, senza pesi di G1 dopo il 4 ottobre.
