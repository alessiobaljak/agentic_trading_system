# Prova 37 — la revisione separata (16 novembre 2026, prima del periodo chiuso)

**Chi ha fatto cosa.** Regole, programma, dati e risultato: la sessione «trading stock» (commit `a4c074e4`, `557283a8`, `20e4ecd6`).
Questa revisione: un agente che non ha scritto né le regole né il codice, in sola lettura sul repository (unico file scritto: questo).
Nessun rendimento dopo il 31 dicembre 2024 usato: gli script del revisore si fermano con un errore se una serie va oltre (il blocco è
scattato una volta, sulle serie `*_chiuso` che `carica_serie()` carica insieme alle altre: le ho escluse per nome, senza guardarne i
valori; vedi il problema Basso 2). Prezzi: quelli di Yahoo già scaricati per la prova (`~/stock_dati/yahoo/p037/`), le barre di Alpaca
di SPY (`~/stock_dati/SPY/`, giorno e minuto) e QQQ riscaricato da Yahoo fino al 31 dicembre 2024 (solo per correggere la miscela).
Il metodo del controllo 5 è stato scritto prima di guardare i rendimenti (`PIANO.md` fra gli script, elenco in fondo).

## Esito: **FAIL** per il criterio «entrare nella miscela»; confermata la bocciatura da sola

* **Da sola: bocciata**, confermato: Sharpe con i costi 0,56 contro 0,87 dello SPY, Sharpe corretto 0,000 (anche togliendo dal conto
  le serie del periodo chiuso), 16 trimestri su 32 in guadagno. Passa solo la condizione dei costi doppi (0,30).
* **Entrare nella miscela:** il calcolo è giusto, fedele all'articolo e si riproduce al centesimo (rifatto da zero: differenza
  massima 4·10⁻¹⁶). Il segnale preso 10 minuti prima della chiusura lo lascia passare. **Ma il passaggio sta tutto in un mese:
  marzo 2020** (22 giorni su 2.264) fa il **101%** del guadagno dei nove anni. Senza marzo 2020 la parte non guadagna (Sharpe −0,06
  sui giorni della miscela), il t scende a 0,07, la miscela nuova è **peggio** della miscela (1,138 contro 1,160) e vince nel 42% dei
  campionamenti. Basta togliere i 5 giorni migliori (4 sono di marzo 2020) per perdere tutto. Con la regola scritta prima
  (`PIANO.md`, punto e) questo è un problema Bloccante. Sul futuro il risultato dice solo questo: **se torna una crisi con giorni da
  ±10% che si alternano, la parte guadagna**. Nei giorni normali, al netto dei costi, è zero.
* Il margine è sottile anche sul resto: il criterio cade con costi più alti del 30% e quando lo scambio si fa all'apertura del giorno
  dopo invece che all'asta di chiusura (Sharpe 0,01). Con un conto da 10.000 dollari le commissioni minime lo portano sotto zero.

## I problemi

**Bloccante 1 — il passaggio dipende da marzo 2020.** Somma dei logaritmi dei rendimenti: 0,387 in marzo 2020 contro 0,383 in tutto
il periodo (`c7_varie.py`). I 10 giorni migliori: 7 di marzo 2020 (+7,8%, +7,8%, +7,4%, +6,2%, +3,7%, +3,4%, +2,9%), più il 26 dic
2018, il 26 nov 2021 e il 26 mar 2018. Il criterio rifatto (`c5_pochi_giorni.py`): senza marzo 2020 non passa (Sharpe della parte
−0,06, costi doppi −0,40, t 0,07, miscela nuova 1,138 contro 1,160, campionamento 42%); senza i 5 giorni migliori non passa (t 0,36,
campionamento 49%); togliendo in modo simmetrico i 5 migliori e i 5 peggiori non passa (t 1,12, costi doppi −0,02). Anche prima dei
costi, senza marzo 2020, lo Sharpe è 0,35 (t 1,04), contro lo 0,90 che l'articolo dichiara fuori dalle crisi. Il campionamento a
blocchi non lo vede: dei 2.000 campioni, i 1.479 con almeno 10 giorni di marzo 2020 vincono nel 93%, gli altri 521 nel 63%
(`c6_miscela.py`). Il campionamento misura la fortuna nell'ordine dei giorni, non la ripetibilità di un episodio solo.

**Alto 1 — il margine sui costi è sottile.** I costi tolgono il 2,04% l'anno su un guadagno lordo del 6,63% (scarto e slittamento
1,36%, commissioni 0,59%, prestito 0,21%). La strategia scambia tutti i giorni (2.264 su 2.264), in media 0,17 volte il conto per
parte. Il criterio passa con i costi fino a 1,2 volte quelli delle regole e cade a 1,3 volte (campionamento 79%); con uno slittamento
di 2 punti base invece di 1 il t è 1,35. Con 10.000 dollari di conto lo Sharpe è −0,03 (il minimo di 1 dollaro a ordine pesa troppo)
(`c4_costi.py`).

**Alto 2 — tutto il vantaggio sta nella prima notte dopo il segnale.** Con lo scambio all'apertura del giorno dopo (tenuto da apertura
ad apertura) lo Sharpe è 0,01; con un giorno di ritardo −0,54 (t −1,63), e −0,41 anche senza marzo 2020 (`c2_tempi.py`). La
strategia esiste solo se si compra e si vende all'asta di chiusura, su tutte e due le parti, ogni giorno. Un ordine perso o arrivato
tardi non è un costo neutro.

**Alto 3 — i numeri dell'articolo sono stati scelti su quasi tutti i nostri giorni.** L'80% dei giorni della prova (1.814 su 2.264) e
il 78% di quelli della miscela (1.604 su 2.054) cadono dentro il campione dell'articolo (10 set 1997 – 17 mar 2023), dove sono state
scelte la fascia fino al 2,5%, la scala dell'1,5%, l'ultima settimana e il rimbalzo. Dopo il 17 marzo 2023 (450 giorni): Sharpe 0,53,
t 0,70, +4,6% (senza costi 0,90). Va nella direzione giusta, ma non è una prova. Il sospetto era scritto prima nelle regole.

**Medio 1 — il risultato cambia molto spostando un giorno al mese.** Tenere il rimbalzo il primo giorno del mese invece del secondo
porta lo Sharpe da 0,56 a 0,79 (senza marzo 2020: 0,43). Il programma ha scelto la lettura alla lettera, che è la meno favorevole:
nessuna scelta di comodo. Ma un risultato che si muove così per 108 giorni su 2.264 è fragile (`c1_fedelta.py`).

**Medio 2 — le chiusure giornaliere di Alpaca sono sbagliate in alcuni giorni di marzo 2020.** Il 12 marzo 2020 Alpaca dà 255,24 per
SPY; Yahoo dà 248,11, come l'ultimo minuto della seduta di Alpaca (248,10). In 20 giorni, tutti di marzo 2020, la differenza supera i
10 punti base (massimo 279). La «seconda fonte» del programma (correlazione 0,9955) segnalava un errore di Alpaca, non di Yahoo, e non
è stato guardato. Su questa prova non conta: rifacendo la miscela della prova 25 con i prezzi di Yahoo il criterio non cambia (1,179
contro 1,078, campionamento 85%). Ma il comprare e tenere lo SPY e le parti SPY delle prove 15 e 16 (quindi la miscela della prova 25)
usano quei prezzi (`c3_dati.py`, `c3_marzo.py`, `c6_miscela.py`).

**Basso 1** — il t della parte è calcolato su 2016-2024 (1,67), la miscela sui giorni comuni dal novembre 2016 (lì il t è 1,53).
Tutte e due sopra 1,3; le regole non dicono quale. **Basso 2** — `carica_serie()` mette nel conto dello Sharpe corretto anche le 9
serie `*_chiuso` (rendimenti del periodo chiuso di altre prove). Qui non cambia niente (0,000 con 28 gruppi o con 24), ma tocca tutte
le prove. **Basso 3** — il campionamento passa con poco margine: con 10 semi diversi fra l'82,8% e l'86,5%, con blocchi di 10 giorni
l'82,7%. **Basso 4** — il segnale usa la chiusura stessa: con il prezzo di SPY 10 minuti prima lo Sharpe va da 0,56 a 0,53 e il
criterio passa lo stesso (controllo 2).

## 0. L'ordine dei commit

| File | Commit | Ora (UTC) |
|---|---|---|
| `P037_ribilanciamento.md` (regole) | `a4c074e4` | 2026-11-16 10:36:34 |
| `p037.py`, `test_ribilanciamento.py` | `557283a8` | 10:39:04 |
| prezzi di Yahoo scaricati (data dei file in `~/stock_dati/yahoo/p037/`) | — | 10:39:08-09 |
| `P037_risultati.md`, `serie/P037_*.csv` | `20e4ecd6` | 10:39:43 |

Regole, poi programma, poi prezzi, poi risultato. **OK.** Test delle azioni: 144 verdi (`python -m pytest stock/tests -q`).

## 1. Fedeltà all'articolo

Letti la sezione 1.2, la sezione 2.1 (tabella 1, figura 4), la sezione 4 (tabella 6, figura 6), l'appendice B e le figure 2-3.

| Punto | Articolo | Programma | Effetto (`c1_fedelta.py`, Sharpe con i costi) |
|---|---|---|---|
| Segnale a fascia | Deriva del peso alla chiusura di t, poi ritorno al 60% se fuori fascia (B.1); predice il rendimento di t+1 (eq. 1) | Uguale | — |
| Fascia: un lato o due | Testo: «distance … exceeds δ», «\|Threshold Signal\| ≥ δ» (pag. 10-12); formula B.1: «w − 60% ≥ δ» (un lato solo, quasi certo un refuso) | Due lati (il testo) | Un lato: 0,52 (senza marzo 2020 0,80: il segnale resta negativo per mesi, cioè lunghi SPY nel rialzo; non è ribilanciamento) |
| Media | 26 fasce da 0 a 2,5% a passi di 0,1% (eq. 2) | Uguale | Fasce 0,1-2,5%: 0,56; 0-2,0%: 0,56 (come la tabella D.6) |
| Calendario | Ritorno al 60% alla chiusura dell'ultimo giorno di borsa del mese (B.2) | Uguale (il segnale dell'ultimo giorno è prima del ritorno) | — |
| Ultima settimana | «last week (i.e., 5 days)», «week4 = Dummy5Days» (pag. 14 e 16) | Ultimi 5 giorni di borsa | Ultimi 4 (il picco della figura 3): 0,60 |
| Rimbalzo | «on the first business day of a new month … sign(Calendar Signal−4)»; R(t+1) = w(t)·(…) | Peso deciso alla chiusura del 1° giorno, tenuto il 2°; segnale di 4 giorni di borsa prima, cioè del quart'ultimo giorno del mese prima (le due letture di «−4», «4 giorni prima» e «giorno −4 della figura 3», coincidono) | Tenuto il 1° giorno: 0,79 (senza marzo 2020 0,43); senza rimbalzo: 0,58 |
| Scala | −fascia/1,5%, per pareggiare il rischio delle due parti (11,6% l'anno ciascuna nel loro campione) | Uguale, senza ricalibrare (giusto: ricalibrare sarebbe guardare avanti) | Da noi 12,5% e 10,1%; scala 1%: 0,58, 2%: 0,50 |
| Peso | Media delle due posizioni | Uguale | — |
| Strumenti | Futures S&P 500 e Tesoro 10 anni | SPY e IEF (7-10 anni) | Dichiarato nelle regole |
| Leva | Nessun limite | ±1 | Senza limite 0,56 (solo 2 giorni oltre 1) |

**Esito: OK.** La regola è quella della sezione 4, presa alla lettera; dove l'articolo è ambiguo (il giorno del rimbalzo) il
programma ha preso la lettura meno favorevole. L'articolo nelle regressioni tiene conto del momento (correlazione 67% con i segnali,
segno opposto), la strategia della sezione 4 no: il programma fa come la sezione 4. Prima dei costi lo Sharpe è 0,80 (l'articolo
1,11 sul 1997-2023).

## 2. Sguardo nel futuro e tempi

* **Il peso deciso alla chiusura di t si applica al rendimento da chiusura t a chiusura t+1** (`p037.py`, `conto`: `shift(1)`).
  Verificato a mano: il 12 marzo 2020 SPY −9,57%, peso tenuto il 13 marzo 0,85; 0,85 × (8,55% + 0,65%) = 7,82%, meno i costi 7,80%
  come nella serie. Nessun altro sguardo avanti: il calendario di borsa è noto prima; `finisce_a_fine_mese` vale solo per il 31
  dicembre 2024, che è davvero l'ultimo giorno del mese.
* **Il segnale usa la chiusura del giorno.** Misurato con le barre al minuto di SPY di Alpaca (nessun giorno senza prezzo; giorni di
  chiusura alle 13 scritti a mano). Per IEF non ci sono dati al minuto: due casi estremi, IEF alla chiusura (ottimista) e IEF fermo a
  ieri (pessimista). Lo scambio resta all'asta di chiusura (`c2_tempi.py`, `c2b_criterio.py`):

| Segnale | Sharpe | t | Senza marzo 2020 | Criterio miscela |
|---|---|---|---|---|
| Chiusura (programma) | 0,56 | 1,67 | 0,02 | passa (85%) |
| SPY 5 min prima, IEF chiusura / fermo | 0,54 / 0,47 | 1,62 / 1,40 | 0,02 / −0,02 | — |
| SPY 10 min prima, IEF chiusura / fermo | 0,53 / 0,51 | 1,60 / 1,54 | 0,04 / 0,07 | passa (85% / 88%) |
| SPY 15 min prima, IEF chiusura / fermo | 0,50 / 0,49 | 1,50 / 1,47 | 0,02 / 0,07 | — |
| SPY 30 min prima, IEF chiusura / fermo | 0,49 / 0,38 | 1,48 / 1,15 | 0,07 / −0,01 | — |
| Scambio all'apertura del giorno dopo | 0,01 | 0,02 | −0,01 | — |
| Un giorno di ritardo | −0,54 | −1,63 | −0,41 | — |

**Esito:** la piccola occhiata in avanti costa poco (Basso 4). Ma il vantaggio esiste solo con l'asta di chiusura (Alto 2). Da
verificare: IEF è quotato al Nasdaq, dove gli ordini per l'asta di chiusura si accettano, se ricordo bene, fino alle 15:50: il
segnale va calcolato prima.

## 3. I dati

* Yahoo: 2.768 giorni dal 2 gennaio 2014 al 31 dicembre 2024, gli stessi per SPY, IEF e TLT, **nessun doppione**. Dal 2016: 2.264
  giorni, **gli stessi di Alpaca**, nessuno mancante da una parte o dall'altra (`c3_dati.py`).
* Rettifiche: 44 dividendi di SPY e 132 di IEF (mensili); il salto della chiusura rettificata torna con dividendo / chiusura del giorno
  prima entro 0,009 punti base. Sei salti minuscoli (al massimo 0,017 punti base) senza dividendo, tutti nel 2014-2015: arrotondamenti
  (`c3_dati.py`, `c7_varie.py`). Yahoo ha anche i tre dividendi di SPY che mancano ad Alpaca.
* Yahoo contro Alpaca su SPY: rendimenti rettificati, correlazione 0,99551, differenza mediana 0,15 punti base (come nel risultato).
  Le differenze sopra i 10 punti base sono 20 giorni, tutti di marzo 2020, ed è **Alpaca** a sbagliare (Medio 2; tabella giorno per
  giorno in `c3_marzo.py`). La chiusura di Yahoo cade sempre dentro la barra delle 16:00 di Alpaca, quella dove si stampa l'asta di
  chiusura (13 marzo: Yahoo 269,32, barra delle 16:00 fra 266,00 e 271,10; ultimo minuto della seduta 270,93); il giornaliero di
  Alpaca cade invece negli scambi fuori seduta (12 marzo: 255,24, quando dopo le 16 SPY si è scambiato fra 242 e 264,5). Le
  chiusure di Yahoo sono quindi i prezzi che un ordine per l'asta di chiusura avrebbe avuto.
* IEF e TLT non hanno una seconda fonte: limite. IEF ha 18 giorni con rendimento esattamente zero (plausibile: un centesimo su 100
  dollari è un punto base).

**Esito: OK** per i prezzi della prova; problema Medio 2 per i prezzi di Alpaca usati altrove.

## 4. I costi

| Ipotesi (`c4_costi.py`) | Sharpe | t |
|---|---|---|
| Regole (SPY mezzo scarto 0,185 pb, IEF 1 pb, slittamento 1 pb per parte, IB fisso, prestito 0,5%) | 0,56 | 1,67 |
| Asta di chiusura senza scarto né slittamento (solo commissioni e prestito) | 0,71 | 2,14 |
| IEF mezzo scarto 0,5 / 2 pb | 0,58 / 0,50 | 1,75 / 1,51 |
| Slittamento 0 / 2 pb | 0,66 / 0,45 | 1,98 / 1,35 |
| Prestito 0,25% / 2% | 0,57 / 0,51 | 1,69 / 1,52 |
| Senza commissioni (broker a zero) | 0,62 | 1,87 |
| Costi ×1,25 / ×1,5 / ×2 / ×3 | 0,49 / 0,43 / 0,30 / 0,02 | 1,48 / 1,29 / 0,89 / 0,06 |
| Conto da 10.000 / 1.000.000 dollari | −0,03 / 0,59 | −0,09 / 1,77 |

Il criterio della miscela al crescere dei costi: passa a ×1,0 (85%), ×1,1 (84%), ×1,2 (81%); **non passa a ×1,3** (79%), ×1,4 (77%),
×1,5 (t 1,29, 74%).

**Esito:** le ipotesi sono ragionevoli, anzi prudenti per l'asta di chiusura (dove lo scarto non si paga). Non contati: le tasse di
borsa sulle vendite (SEC e FINRA, frazioni di punto base) e gli interessi sul ricavato della vendita allo scoperto (a favore). Lo scarto
di IEF non è misurato. Il punto debole non sono le ipotesi ma il margine (Alto 1) e la taglia del conto.

## 5. Dipendenza da pochi giorni (metodo scritto prima: `PIANO.md`)

| Sottoperiodo (`c5_pochi_giorni.py`) | Sharpe con i costi (senza costi) | t | Totale | Miscela nuova / miscela |
|---|---|---|---|---|
| 2016-2019 | −0,09 (0,26) | −0,18 | −2,6% | 1,21 / 1,32 |
| 2020 | 1,59 (1,73) | 1,60 | +32,3% | 1,54 / 1,03 |
| 2021-2024 | 0,57 (0,91) | 1,14 | +13,8% | 1,07 / 0,95 |
| 2016-2024 senza il 2020 | 0,25 (0,59) | 0,71 | +10,8% | 1,13 / 1,10 |
| fino al 17 mar 2023 / dopo | 0,57 / 0,53 | 1,54 / 0,70 | +40,1% / +4,6% | 1,00 / 0,89 e 1,97 / 1,83 |

| Criterio rifatto | Giorni | Sharpe parte | Costi doppi | Corr | Nuova | Miscela | SPY | t | Campion. | Esito |
|---|---|---|---|---|---|---|---|---|---|---|
| Tutto | 2.054 | 0,53 | 0,28 | −0,00 | 1,185 | 1,082 | 0,89 | 1,67 | 85% | passa |
| Senza marzo 2020 | 2.032 | −0,06 | −0,40 | −0,06 | 1,138 | 1,160 | 1,10 | 0,07 | 42% | **non passa** |
| Senza il 1° semestre 2020 | 1.929 | 0,20 | −0,16 | −0,09 | 1,216 | 1,179 | 1,12 | 0,78 | 74% | non passa |
| Senza i 5 / 10 / 20 migliori | | 0,05 / −0,25 / −0,70 | | | | | | 0,36 / −0,46 / −1,65 | 49% / 23% / 4% | non passa |
| Senza i 5+5 / 10+10 / 20+20 estremi | | 0,32 / 0,18 / 0,04 | −0,02 / −0,20 / −0,38 | | | | | 1,12 / 0,87 / 0,53 | 81% / 74% / 59% | non passa |

**Esito: Bloccante 1.** Fuori dal 2020 c'è qualcosa prima dei costi nel 2021-2024 (0,91), niente nel 2016-2019; dopo i costi resta
poco o niente.

## 6. Il criterio per la miscela, rifatto

Rifatto con un codice mio (`rev.py`, `crit.py`, `c6_miscela.py`), con il campionamento ufficiale (`p032.campionamento`, seme 32):
**tutti i numeri tornano**: correlazione −0,00, miscela nuova 1,185 contro 1,082 della miscela e 0,89 dello SPY, Sharpe della parte
0,53 (costi doppi 0,28), t 1,67, campionamento 85%. La miscela della prova 25 è la media delle sei parti (differenza 1·10⁻¹⁶); la
miscela nuova è 0,75 × miscela + 0,25 × parte sui 2.054 giorni comuni dal 1° novembre 2016 (differenza 1·10⁻¹⁶): **come dicono le
regole**. Sensibilità: 10 semi da 82,8% a 86,5%; blocchi di 5, 10, 60, 120 giorni: 85,2%, 82,7%, 89,0%, 92,5%. Con la miscela
corretta con i prezzi di Yahoo: 1,179 contro 1,078, 85%; con lo SPY di Yahoo 0,87 invece di 0,89. **Esito: riproducibile; non
robusto** (controllo 5).

## 7. Eccesso di adattamento e conto delle prove

* **Scelte dell'articolo prese sugli stessi anni:** almeno sei (fascia fino al 2,5% dalla figura 2; media delle fasce; scala 1,5% per
  pareggiare il rischio nel loro campione; ultimi 5 giorni dalla figura 3, dove il picco è a 4; rimbalzo del primo giorno con il
  segnale di 4 giorni prima dalla figura 4; media delle due parti). Gli autori dicono di aver rifatto la fascia sulla sola prima metà
  dei dati con risultati simili (nota 10); per le altre scelte no.
* **Sovrapposizione:** 80% dei nostri giorni (1.814 su 2.264), 78% di quelli della miscela, dentro il loro campione (`c7_varie.py`).
* **Conto:** 91 prove; Sharpe corretto 0,000. Delle prove passate dal criterio della miscela (28, 30-37) l'hanno superato la 31 (caduta
  alla revisione) e la 37: senza alcun vantaggio vero, la sola soglia del t a 1,3 si supera per caso circa una volta su dieci.

**Esito: Alto 3.**

## 8. Riproducibilità

`python -m stock.prove.p037` rilanciato in una copia (`git archive HEAD stock`): `P037_risultati.md` identico tranne l'ora; le due
serie diverse solo all'ultima cifra (al massimo 4·10⁻¹⁶). Il ricalcolo da zero (`c8_riproduci.py`) rifà la serie committata
(differenza massima 4,2·10⁻¹⁶) e tutte le varianti del risultato (costi doppi 0,30, senza costi 0,80, senza limite 0,56, solo fascia
0,56, solo calendario 0,14, un giorno di ritardo −0,54, con TLT 0,79; peso medio 0,27, massimo 1,09; asimmetria 5,77; anni uguali).
**Esito: OK.**

## Domande aperte

1. **Il periodo chiuso non sarebbe una prova cieca per questa strategia.** Il suo guadagno viene solo dalle crisi con giorni enormi
   che si alternano. Che nel 2025 ci sia stata una crisi breve di questo tipo (aprile 2025) è noto a tutti, non è un dato guardato: un
   buon risultato sul periodo chiuso sarebbe in gran parte prevedibile. Il mio consiglio è di non aprirlo per questa prova. Decide la
   sessione principale.
2. **Una parte che guadagna solo nelle crisi** (asimmetria 5,77) può avere senso in una miscela, ma è un'altra domanda: servono regole
   scritte prima per un pezzo «da crisi» e un secondo episodio indipendente. IEF esiste da luglio 2002: il 2003-2015, con la crisi del
   2008, sarebbe fuori dal nostro periodo, ma resta dentro quello dell'articolo.
3. Da verificare prima di qualsiasi demo: l'orario limite degli ordini per l'asta di chiusura di IEF e lo scarto di IEF misurato.
4. Il problema Medio 2 (chiusure di Alpaca di marzo 2020) e il Basso 2 (serie `*_chiuso` nel conto dello Sharpe corretto) toccano
   altre prove: da mettere in `stock/REGISTRO.md` o nel backlog delle azioni.

## Gli script del revisore

Tutti in
`/tmp/claude-0/-home-user-agentic-trading-system/55688ced-bd2e-59dc-8673-d3e30f31b49e/scratchpad/revisione_p037/` (fuori dal
repository: la cartella si può svuotare): `PIANO.md` (metodo scritto prima), `rev.py` (ricalcolo indipendente e blocco delle date),
`crit.py` (criterio della miscela), `c1_fedelta.py`, `c2_tempi.py`, `c2b_criterio.py`, `c3_dati.py`, `c3_marzo.py`, `c4_costi.py`,
`c5_pochi_giorni.py`, `c6_miscela.py`, `c7_varie.py` (da lanciare dalla radice del repository), `c8_riproduci.py`; il PDF
dell'articolo è in `../articolo_ribilanciamento/a.pdf`.
