# Prova 167 — Le proposte di governo che spostano soldi ai possessori del gettone (idea 157)

Regole scritte il 22 novembre 2026 dal cercatore di idee (strategy-scout), **prima di ogni calcolo**, per l'idea 157 del registro
(sessione principale, 22 novembre) e con la decisione del proprietario del 22 novembre (le idee nuove si provano senza aspettare il suo
via libera). La esegue strategy-researcher (prima in modalità verifica), il giudizio lo dà backtest-auditor. Il registro lo aggiorna la
sessione principale. Non spegne e non sostituisce niente.

## Il perché
* Un voto che passa e destina soldi ai possessori (riacquisto con distruzione, quota delle commissioni, distruzione di monete) cambia
  quanto vale tenere il gettone; il voto è pubblico per giorni, ma i forum e gli archivi dei voti li leggono in pochi. Dato **mai usato**
  nella ricerca: `registro --cerca governo` e `--cerca voto` non trovano niente. La prova 95 guardava le commissioni delle catene (un
  numero sui prezzi), non i voti.
* Studi: la letteratura sugli annunci di riacquisto di azioni (Ikenberry, Lakonishok e Vermaelen, Journal of Financial Economics 1995)
  trova un rialzo dopo l'annuncio, ma su dati vecchi e azioni: per i gettoni non è noto che regga (si scrive come dubbio, non come prova).
* Fatto di oggi: le strategie a eventi restano senza materia prima (Binance quota 2-3 perpetui nuovi al mese); i voti sono una fonte di
  eventi che non dipende dalle quotazioni.
* **Rischi scritti prima**: i voti sono spesso proposti da gruppi che hanno già comprato; molti progetti hanno il perpetuo di Binance solo
  da tardi (abbinamento solo se il perpetuo esisteva alla fine del voto); gli spazi più attivi sono pochi.

## Dati (verificati il 22 novembre 2026, solo gratuiti, senza registrazione e senza chiave)
* **Snapshot**, `https://hub.snapshot.org/graphql` (POST): funziona. Le proposte danno `id`, `title`, `start`, `end`, `state`, `choices`,
  `scores`, `scores_total`, `space{id}`; lo spazio dà `symbol`, `coingecko` (identificativo CoinGecko), `network`. Si può filtrare con
  `title_contains` e `state`; massimo 1.000 per chiamata, `skip` fino a 5.000. Archivio dal 2020 (esempio: le prime proposte di
  Uniswap del settembre 2020). Esito: la scelta con il punteggio maggiore (`scores`) e `state = closed`.
* **Tally**: non utilizzabile (`api.tally.xyz/query` risponde 401 «api key required»). **Escluso.** Non si usano forum né chiavi.
* **Elenco dei perpetui di Binance**: `fapi.binance.com` è bloccato da qui (451); si usa l'archivio ufficiale `data.binance.vision`
  (elenco delle cartelle `futures/um/monthly/klines/`, 850 simboli) e i prezzi orari e giornalieri dello stesso archivio, già usati
  dalle prove precedenti. Primo giorno di ogni perpetuo = primo mese nell'archivio.
* **Abbinamento spazio → perpetuo** (fissato qui): simbolo dello spazio in maiuscolo (`symbol`) uguale al simbolo base del perpetuo
  USDT (con `1000…` quando il perpetuo ha il prefisso); poi **controllo con il campo `coingecko`** dello spazio contro l'identificativo
  CoinGecko del simbolo (l'interfaccia pubblica senza chiave, con calma fra le chiamate). Se i due non coincidono la coppia **esce** e si
  scrive. Gli spazi il cui gettone di voto non è il gettone del progetto (esempio: voti con un gettone «v…» o rappresentato) escono.
  L'elenco finale delle coppie va scritto nel rapporto prima dei risultati.
* Mai `research/data/` letto dall'autore delle regole; nessuna chiamata a servizi a pagamento.

## Il numero di eventi atteso (stimato solo dai testi dei titoli, senza prezzi)
Conteggio fatto il 22 novembre sulle proposte chiuse con una delle parole sotto nel titolo: **1.551 proposte in 828 spazi** (2020: 42,
2021: 281, 2022: 397, 2023: 354, 2024: 266, 2025: 146, 2026: 65 fino a novembre). Con il simbolo dello spazio uguale a un perpetuo di
Binance di oggi: **146 proposte** (2020: 6, 2021: 21, 2022: 36, 2023: 28, 2024: 28, 2025: 13, 2026: 14), con molti nomi che si ripetono
(SNX 14, MATIC 14, LDO 4, UNI 4, SUSHI 4, CRV 3). Dopo i filtri (voto approvato, perpetuo già quotato alla fine del voto, un solo evento
per moneta ogni 30 giorni, abbinamento controllato con CoinGecko) si attendono **circa 50-90 eventi** nei sei anni, cioè pochi per anno:
**2025 e 2026 hanno 13-14 proposte grezze l'anno, quindi 4-8 eventi: troppo pochi per un t da 3 per anno**. È il punto più debole e si
dice subito: se gli eventi veri sono meno di 40 il rapporto lo scrive e l'esito è «campione troppo piccolo» (non un FAIL sul valore).

## La regola (fissata qui)
1. **Evento**: proposta di Snapshot in uno spazio abbinato, `state = closed`, con **una di queste parole nel titolo** (maiuscole o
   minuscole, parole intere o radice): `buyback`, `buy back`, `buy-back`, `repurchase`, `burn`, `fee switch`, `fee share`,
   `revenue share`, `revenue sharing`. Elenco fissato qui, nessuna parola aggiunta dopo.
2. **Approvato**: la scelta con più punteggio è «For», «Yes», «Approve» o il primo dei due (dove le scelte sono solo due; altrimenti
   l'evento esce) e i voti totali (`scores_total`) sono maggiori di zero. Le proposte con più di 2 scelte e senza un chiaro «sì» escono.
3. **Entrata**: all'apertura (00:00 UTC) del **primo giorno dopo la fine del voto** (`end`); comprare il perpetuo della moneta e vendere
   il perpetuo del Bitcoin per lo stesso valore (la moneta contro il Bitcoin, così il mercato conta meno). Se nel giorno non c'è il
   perpetuo, l'evento esce.
4. **Tenuta**: A = 5 giorni, B = 10 giorni; si chiude all'apertura del giorno corrispondente.
5. Per evento valore delle gambe = 1/10 del capitale (al massimo 10 eventi insieme; un nuovo evento oltre il limite si salta e si conta);
   un solo evento aperto per moneta (il secondo nei 30 giorni esce).
6. Rendimento = rendimento della gamba comprata − quello della venduta + funding vero di tutte e due le gambe − spese.
7. **Spese** confermate dal proprietario: 0,05% a mercato, scarto 0,01% su BTC, ETH e SOL e 0,02% sulle altre; ordine limite 0,02% solo
   come controllo descrittivo; funding vero delle due gambe.
8. **Periodo**: dalla prima proposta in archivio con perpetuo alla data del 31 ottobre 2026 (ultimo mese intero); eventi dal
   1° gennaio 2021 (nel 2020 i perpetui erano pochi e il rapporto li mostra solo come descrizione).

## Varianti (fissate, solo 2)
**A** tenuta 5 giorni; **B** tenuta 10 giorni. Il perché: a 5 giorni si misura la reazione rapida, a 10 quella lenta del flusso dei
riacquisti; non si prova altro. Nessuna parola, tenuta o universo diverso dopo i risultati. Conta **2 prove**. Controlli descrittivi (non
varianti): solo gli eventi del 2024-2026; senza i due spazi più frequenti; la sola gamba comprata senza la vendita del Bitcoin; le
spese con ordine limite; le parole una per una (solo per descrivere, nessuna scelta dopo); la correlazione con G1 e con il Bitcoin.

## La lettura dei testi con l'intelligenza artificiale: solo in avanti
Non si fa sul passato (un modello linguistico conosce già i voti prima della sua data di addestramento). Come **misura in avanti**: dal
giorno in cui la sessione principale decide, ogni proposta nuova chiusa negli spazi abbinati (non solo con le parole fisse) viene
registrata con il testo, l'ora della fine e la decisione del modello («passa e sposta soldi ai possessori»: sì/no/dubbio) **prima di
guardare i prezzi**; dopo almeno 30 eventi in avanti si confronta con la regola semplice. Non fa parte dell'esame e non conta come prova.
Dove vive lo script e il modello da usare lo decide la sessione principale (l'agente che decide da solo con un modello è dell'area
`trader_ai/`: qui si **legge e si registra**, non si fa trading).

## L'esame (regole approvate dal proprietario il 9 e l'11 novembre)
Passa se: netto dopo i costi positivo; **ogni anno positivo** (2021, 2022, 2023, 2024, 2025, 2026 fino a ottobre; un anno con meno di
3 eventi si scrive e si guarda l'anno intero più vicino, ma **non** si salta in silenzio); t almeno 3 (sul netto delle serie
settimanali, come nelle prove 157-162, e anche sul netto per evento); Sharpe corretto almeno 0,80 con il conto per famiglie
(`asticella.corretto_famiglie`, tutte e due le varianti in `nuove`); netto almeno 3% l'anno sul capitale. Tolta l'evento migliore e
tolti i due spazi più frequenti il netto resta positivo. Con meno di 40 eventi: «campione troppo piccolo», non si dichiara né PASS né
FAIL sul valore.

## Punti dubbi (per chi verifica)
1. Abbinamento per simbolo: rischio di coppie sbagliate (gettoni di voto diversi dal gettone del progetto); il controllo con CoinGecko
   è fissato, ma va visto a mano nell'elenco prima dei risultati.
2. Il perpetuo di Binance di oggi ci dice quali monete esistono: è sopravvivenza (monete ritirate non compaiono); si scrive e, dove
   l'archivio ha il perpetuo ritirato, si include.
3. Pochi eventi nel 2025-2026 (4-8 l'anno stimati): l'esame «ogni anno positivo» e il t da 3 sono quasi impossibili da leggere.
4. Alcuni voti sono ratifiche di cose già annunciate nei forum (il mercato sa prima): il rialzo, se c'è, può stare prima dell'entrata.
5. Le scelte e i nomi delle opzioni di Snapshot non sono uniformi: il punto 2 della regola scarta quelli ambigui; il rapporto dice quanti.

## Chiusura della verifica (22 novembre 2026, sessione principale, prima di ogni calcolo)
Dalla verifica di strategy-researcher (`VERIFICA_CENTOCINQUESIMA.md`, 14 punti, 2 bloccanti). **Dove il testo sopra dice diversamente,
vale questa sezione.** Dove c'era una scelta, si è presa la più prudente e senza giudizi a mano.
1. **Spazi ufficiali, con un criterio meccanico** (punti 1 e 2 bloccanti; il controllo con il campo `coingecko` è abolito): uno spazio
   entra solo se in Snapshot ha `verified` vero e `flagged` falso **e** il suo nome (`name`, senza distinzione di maiuscole) contiene la
   sigla del gettone o il nome della moneta nell'elenco dei nomi di `research/notizie/nomi_2026-11.json` (per le monete fuori elenco,
   solo la sigla). Gli spazi con sigla di una stablecoin (USDT, USDC, DAI, BUSD, FDUSD, TUSD, USDE, FRAX, LUSD) o di BTC, ETH, BNB, SOL,
   MATIC, POL, AVAX, ARB, OP, FTM escono sempre, salvo che il nome contenga il nome della moneta (per esempio «Arbitrum DAO» per ARB).
   Nessun elenco a mano. L'elenco degli spazi che entrano e di quelli che escono, con il motivo, si scrive nel rapporto prima dei risultati.
2. **Parole del titolo** (punto 3): parole intere, senza distinzione di maiuscole («burn» non vale dentro un'altra parola); escono i titoli
   con una di queste parole: pause, stop, end, halt, cancel, reduce, suspend, remove, terminate, deprecate. Nient'altro si toglie, né prima
   né dopo i risultati.
3. **Approvato** (punto 7): la scelta con il punteggio più alto deve cominciare con «Yes», «For», «Approve», «Accept», «In favor» (senza
   distinzione di maiuscole); altrimenti la proposta esce.
4. **I 30 giorni** (punto 6): si contano dalla fine del voto dell'ultimo evento tenuto della stessa moneta; un evento scartato non
   riavvia il conto.
5. **Il t e gli anni** (punto 12): sulle serie settimanali di tutte le settimane del periodo (quelle senza posizione valgono zero), come
   nelle prove 157-163, dopo `periodo()` di `asticella`.
6. Punti 4, 5, 8-11, 13 e 14: valgono le correzioni scritte nel rapporto di verifica, punto per punto, così come sono.
7. Sotto i **40 eventi** dopo tutti i filtri l'esito è «campione troppo piccolo» e la prova non entra nel conto (non si calcola nessun
   rendimento); il conto degli eventi si fa e si scrive prima di caricare i prezzi.

## Cosa si consegna
`research/programma7/RISULTATI_CENTOCINQUESIMA.md`, serie in `research/programma7/risultati_centocinquesima/` (giornaliere e settimanali
nette, leggibili da `asticella.py`), script `research/programma7/centocinquesima.py` e uno per i dati
(`centocinquesima_dati.py`: proposte, spazi, abbinamento), varianti in `research/trials/centocinquesima.csv`, dati in `research/data/`
(non committati); l'elenco delle coppie e degli eventi (id della proposta, titolo, fine del voto, esito) nel rapporto; a schermo al
massimo 20 righe.
