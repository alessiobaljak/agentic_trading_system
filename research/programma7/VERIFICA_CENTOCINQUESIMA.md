# Verifica della prova 167 (regole in `CENTOCINQUESIMA.md`), 22 novembre 2026

Modalità verifica: nessun risultato calcolato, nessun prezzo guardato, nessun file di `research/data/` aperto, niente salvato nel repo
(i file di lavoro stanno fuori dal repo). Fatte solo: chiamate a Snapshot (proposte e spazi), elenco dei nomi dei file di
`data.binance.vision` (solo i nomi, per gli stessi simboli abbinati) e l'elenco pubblico dei gettoni di CoinGecko (solo per vedere se
l'identificativo è unico). Regole committate: `164b6c2` (22 novembre 2026, 08:16 UTC).

## Esito: NON eseguibile così com'è. Due punti bloccano, gli altri si chiudono prima del calcolo.

## Cosa risponde davvero ciascuna fonte
* **Snapshot**: `title_contains` è una ricerca di pezzo di parola **senza distinzione fra maiuscole e minuscole** (stessi numeri con
  `burn` e `BURN`); trova anche «burning», «burnt», «afterburn», «burned». Massimo 1.000 righe a chiamata: solo `burn` supera il limite
  (1.128 proposte chiuse), con `skip: 1000` si prende il resto; nessuna altra parola arriva a 1.000. Ordinando per `created` ogni
  parola è stata letta per intero.
* Conteggio di oggi (parola per parola, proposte chiuse): buyback 350, buy back 80, buy-back 20, repurchase 22, burn 1.128, fee switch 15,
  fee share 13, revenue share 34, revenue sharing 36. Senza doppioni: **1.599 proposte in 841 spazi** (le regole dicono 1.551 in 828:
  differenza di 48 e 13 dovuta alla data del conteggio e a nessun limite sulla data di fine; 4 proposte hanno la fine dopo il 31 ottobre 2026).
* Query usata (una per parola, con `skip` a passi di 1.000 finché le righe sono meno di 1.000):
  `{proposals(first:1000,skip:S,where:{title_contains:"PAROLA",state:"closed"},orderBy:"created",orderDirection:asc){id title start end state choices scores scores_total space{id}}}`
  e per gli spazi `{spaces(first:100,where:{id_in:[...50 id...]}){id name symbol coingecko network}}` (con 200 id il servizio dà errore 500).
* **Elenco dei perpetui**: l'elenco delle cartelle di `futures/um/monthly/klines/` dà 1.080 nomi (923 in USDT, 157 in altre valute: USDC,
  BUSD). I perpetui ritirati ci sono (esempio: MATIC dal 2020-10 al 2024-09), quindi la sopravvivenza si corregge, ma **l'archivio mensile
  dà solo il mese**, non il giorno di nascita.
* **CoinGecko** (elenco pubblico senza chiave, risponde 200): lo stesso simbolo ha più identificativi (UNI 5, ID 4, OP 2, LDO 2, QUICK 2).

## Ambiguità e punti non eseguibili

1. **BLOCCANTE: il controllo con CoinGecko, come scritto, cancella gli eventi veri e lascia quelli finti.** Nei dati di Snapshot il campo
   `coingecko` è vuoto per 56 dei 86 spazi abbinati per simbolo, compresi quelli veri: Synthetix (SNX, 14 proposte, il nome più frequente),
   QuickSwap, Convex, GMX, Compound. Le regole dicono «se i due non coincidono la coppia esce», ma non dicono cosa fare se il campo è
   vuoto, né come si ricava «l'identificativo CoinGecko del simbolo» (più identificativi per simbolo; per SNX CoinGecko dà `havven`, non
   «synthetix»). Dall'altra parte, il campo pieno non protegge dalle copie: `otterclam.eth` ha simbolo MATIC e campo `otterclam`.
   *Correzione proposta:* abolire il controllo automatico e fissare **un elenco a mano degli spazi ufficiali** (id dello spazio → perpetuo),
   scritto nel rapporto prima dei risultati, con il criterio «lo spazio è quello del progetto del gettone» (nome dello spazio e rete); oppure
   chiedere i soli spazi con `coingecko` pieno (28 eventi, vedi sotto) e dirlo.
2. **BLOCCANTE: l'abbinamento per simbolo prende spazi spam.** Dei 86 spazi abbinati, molti sono copie: 12 spazi di persone con simbolo
   MATIC, ETH, USDC, BNB, CAT, MEME, PEOPLE (esempi: `dapang.eth` e `polygondaoo.eth` con lo stesso testo; un titolo «A lamp stood on the
   table»). Senza vaglio a mano la prova misura 69 eventi, di cui oltre 20 finti. *Correzione:* il punto 1, più: «gli spazi con simbolo
   uguale a ETH, BNB, USDC o a una stablecoin escono sempre»; lista a mano scritta prima dei risultati (la regola dice «va visto a mano
   nell'elenco prima dei risultati» ma non chi lo fa né con quale criterio).
3. **Parole nel titolo e gettone sbagliato.** Con «burn» a pezzo di parola passano titoli che non c'entrano: «Burn PFP to get free mints»,
   «SCCP-193: Lower LUSD Wrapper Burn Fee», «Request to refund 37,875 USDC.e burned by self-disputing», «Suspend Q2 XVS Burn». E titoli sul
   gettone di un altro progetto dentro lo spazio di un aggregatore (spazio Convex con «[Frax] FIP 77 – FXS buyback»; «Pause AAVE Buybacks»,
   approvata, è l'opposto di un riacquisto). Le regole non dicono se «parola intera o radice» valga per `burn` (radice = anche «burning»,
   «afterburn»). *Correzione:* scrivere che vale il pezzo di parola come fa Snapshot (come è scritto), e che i falsi si contano nel rapporto
   ma **non si tolgono dopo** i risultati; oppure fissare ora un elenco di titoli da escludere (cioè fare il vaglio a mano a prima).
4. **Entrata e fine del voto.** «All'apertura del primo giorno dopo la fine»: nessuna delle 108 proposte approvate ha la fine alle 00:00
   esatte, quindi il caso del voto che finisce a mezzanotte non si presenta oggi, ma va scritto («fine esattamente 00:00 → lo stesso giorno
   è escluso, si entra il giorno dopo»). Il ritardo fra fine e entrata va da 0 a 24 ore: va bene, non guarda avanti.
5. **Perpetuo esistente alla fine del voto.** L'archivio mensile dà il mese di nascita: per un voto nel mese di quotazione non si sa se il
   perpetuo c'era. Si risolve con la regola 3 («se nel giorno non c'è il perpetuo, l'evento esce») usando i file giornalieri del giorno di
   entrata; va scritto che serve anche per la gamba del Bitcoin e che l'ultimo giorno dei perpetui ritirati si legge dai file giornalieri.
   Il numero di eventi sotto usa il mese e può variare di pochi eventi.
6. **I 30 giorni.** Non è scritto da quando si contano (dalla fine del voto del primo evento tenuto o dall'entrata?), né se un evento scartato
   riavvia il conto. Oggi i due modi danno lo stesso numero (nessuna catena di tre), ma va scritto: *«i 30 giorni si contano dalla fine del
   voto dell'ultimo evento tenuto; un evento scartato non riavvia il conto»*. La regola 5 («un solo evento aperto per moneta») e quella dei 30
   giorni sono due cose diverse (tenuta di 5 o 10 giorni contro 30): va scritto che vale la seconda.
7. **«Approvato».** La regola 2 prende «For/Yes/Approve» o «il primo dei due»: a 2 scelte «il primo» vale anche se è «Against»? (nei dati le
   prime scelte sono quasi sempre sì, ma ci sono scelte come «sYES» o testi lunghi: sono i spazi spam del punto 2). Tre scelte «For/Against/
   Abstain»: la regola dice che escono salvo un chiaro «sì» (se «For» vince, resta: ma se «Yes, let's do it» vince? non è nell'elenco: esce).
   *Correzione:* scrivere che il confronto è sul testo intero, senza distinzione maiuscole, e che «Yes, let's do it» **esce**; il rapporto
   conta i casi: 66 con nome chiaro, 42 con «primo dei due», 24 ambigui, 10 con due scelte e vincitore la seconda, 17 senza voti.
8. **Il perpetuo con prefisso 1000.** «`1000…` quando il perpetuo ha il prefisso» ma l'elenco ha anche `1000CATUSDT` e `CATUSDT` insieme, e
   prefissi `1000000`. *Correzione:* se due perpetui hanno lo stesso simbolo di base si prende quello con più storia, e il rendimento non
   dipende dal fattore (è un rendimento, non un prezzo); scrivere il caso nel rapporto. I simboli cambiati nel tempo (MATIC → POL, FTM → S)
   non hanno regola: l'evento esce se il simbolo dello spazio non è nell'elenco.
9. **Contenitore del limite 10 eventi.** Regola 5: il limite di 10 aperti insieme non è mai raggiunto con i numeri attuali (nessun giorno ha
   due eventi di monete diverse nello stesso giorno fra gli approvati e dopo il vaglio): va bene, ma resta scritto.
10. **Date del periodo.** «Dalla prima proposta in archivio con perpetuo alla data del 31 ottobre 2026»; eventi dal 1° gennaio 2021. Va scritto
    che i voti con fine dopo il 31 ottobre 2026 (oggi 4) escono e che l'uscita di un evento di fine ottobre (tenuta 10 giorni) arriva dopo
    il 31 ottobre: *si chiude all'apertura del giorno corrispondente se c'è nell'archivio, altrimenti l'evento esce* (come per la prova 163, punto 17).
11. **Spese e funding.** Come per la prova 163: scrivere la formula delle spese (commissione + scarto per ogni gamba a ogni scambio: entrata
    e uscita, due gambe) e che il funding vero si prende dai file mensili del funding dell'archivio (fino al 31 ottobre 2026; non il pannello con la media dei 90 giorni).
12. **Serie settimanali, anni, t.** Come per la 163: settimane lunedì-domenica, rendimento della settimana = somma dei rendimenti giornalieri
    netti, anni di calendario, t = Sharpe settimanale annualizzato × radice(settimane/52). Con 40-50 eventi su 6 anni le settimane senza evento
    sono quasi tutte vuote: va scritto se il t è sul totale delle settimane o sulle sole settimane con posizione aperta.
13. **Controllo «senza i due spazi più frequenti».** «Più frequenti» per numero di eventi tenuti dopo i filtri (oggi SNX e ETHFI): scriverlo.
14. **Lettura con l'intelligenza artificiale in avanti**: non fa parte dell'esame, ma non ha né data di inizio né dove si registra: ok se
    resta fuori da questa prova (solo da decidere dalla sessione principale).

## Eventi dopo i filtri (solo titoli, scelte e nomi dei file: nessun prezzo)
Filtri applicati: titolo con una delle parole, `state closed`, approvato (nome chiaro o «primo dei due», voti > 0), fine dal 1° gennaio 2021
al 31 ottobre 2026, perpetuo presente nel mese della fine (archivio mensile), un solo evento per moneta in 30 giorni.

| Come si tolgono gli spazi finti | Eventi prima dei 30 giorni | Eventi dopo i 30 giorni | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|
| Nessun controllo (solo simbolo, come scritto salvo CoinGecko) | 81 | 69 | 8 | 11 | 11 | 15 | 14 | 10 |
| Solo spazi con `coingecko` pieno (lettura più vicina alla regola) | 29 | 28 | 3 | 4 | 3 | 3 | 9 | 6 |
| Vaglio a mano mio, 28 spazi ufficiali (**solo indicativo, non fa parte delle regole**) | 52 | 49 | 6 | 7 | 5 | 9 | 13 | 9 |

* Nel vaglio a mano: SNX 10, ETHFI 5, QUICK 4, AAVE 2, FLOKI 2; **togliendo SNX ed ETHFI restano 34**. Nell'elenco a mano restano titoli
  con la parola ma che non c'entrano col gettone (alcuni di SNX sulle commissioni dei «wrapper»): per la regola contano, e si dichiara.
* Con la lettura stretta (CoinGecko pieno) gli eventi sono **28**: sotto i 40, l'esito sarebbe «campione troppo piccolo». Con il vaglio a
  mano sono 49 (34 senza i due spazi più frequenti): sopra i 40, ma l'esame «ogni anno positivo» e il t da 3 per anno con 5-9 eventi l'anno
  restano molto deboli (come le regole già scrivono). Anche il numero atteso dalle regole (50-90) è alto per la lettura stretta.
* Il conteggio dei prezzi (il perpetuo nel giorno esatto e la gamba del Bitcoin) può togliere ancora qualche evento: non guardato.

## Punti verificati e a posto
* Le sole parole elencate si fissano con la query scritta sopra; la paginazione oltre 1.000 righe funziona (`skip`), serve solo per `burn`.
* Snapshot e archivio rispondono senza chiave e senza costo; i perpetui ritirati ci sono nell'archivio.
* Nessuna fine di voto alle 00:00 esatte tra le proposte approvate; nessun giorno con due eventi di monete diverse dopo il vaglio.
* L'esame, le due varianti e i file consegnati sono eseguibili (stessa struttura delle prove 157-162).

## Domande aperte (testuali)
1. Il controllo con CoinGecko (punto 1) va sostituito da un elenco a mano degli spazi ufficiali scritto prima dei risultati, oppure si usano
   solo gli spazi con il campo `coingecko` pieno (28 eventi: «campione troppo piccolo»)? Chi compila l'elenco a mano e con quale criterio?
2. Gli spazi con simbolo di una stablecoin o di ETH, BNB escono sempre (punto 2)?
3. Le proposte con la parola nel titolo che non riguardano il gettone (punto 3) restano nella prova e si contano, o si fissa ora un elenco di esclusioni?
4. Da quando si contano i 30 giorni, e un evento scartato riavvia il conto (punto 6)?
5. «Il primo dei due» vale anche se è «Against» (punto 7)? «Yes, let's do it» esce?
6. Il t da 3 si calcola sulle sole settimane con posizione o su tutte (punto 12)?
