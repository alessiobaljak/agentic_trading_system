# Programma 7 — settantacinquesima prova: il funding di Hyperliquid al contrario, sulle monete che non ha visto (HLI)

Scritto il 30 ottobre 2026 alle 09:58 UTC (ora dell'orologio), **prima di qualunque calcolo su queste monete**. È l'idea 114, nata dai
dati della prova 135: lì vendere le monete dove Hyperliquid paga più di Binance faceva Sharpe −2,38, negativo in tutti e quattro gli anni.
Il verso al contrario **è stato visto su quei dati**, quindi si prova solo su monete che la prova 135 non ha usato: quelle dalla 101ª
alla 200ª per volume di Binance (la prova 135 usava le prime 100).

## 1. Perché (scritto dopo aver visto la prova 135, e per questo da confermare)

* **Hyperliquid è la piattaforma dei grandi portafogli sulla catena**, che si vedono e che spesso sanno qualcosa prima (le posizioni sono
  pubbliche e vengono seguite). Se su una moneta i long di Hyperliquid pagano molto più dei long di Binance, chi ha più informazione sta
  comprando lì, e il prezzo sale anche su Binance nei giorni dopo.
* **Il dubbio più grande**: l'idea è nata guardando i dati; su monete diverse (più piccole, meno seguite) può non esserci. È la stessa
  prudenza della prova 64 (G7, l'idea nata da G5 provata su Gate.io) e della 122.
* **Altri dubbi**: le monete 101-200 costano di più da scambiare (la regola del funding fra monete non ha retto sulle 101-150 per i costi,
  prove 50 e 51); lo storico di Hyperliquid c'è solo per le monete quotate oggi (sopravvivenza).

## 2. La regola (fissata qui)

* **Tutto come la prova 135** (`settantatreesima.py`: il funding di Hyperliquid e di Binance dei 7 giorni prima, sommati per giorno con la
  stessa convenzione), con il **verso al contrario**: **long il quinto con lo scarto (Hyperliquid meno Binance) più alto, short il quinto
  con il più basso**, banda 20/40, pesi secondo l'inverso della volatilità, almeno 20 monete con il segnale, deciso ogni giorno alle 00:00,
  ordini limite e costi come G1 (`cinquantaduesima.conto`).
* **L'universo**: le monete **dalla 101ª alla 200ª** per volume di ogni settimana (`terza.pannello_settimane(..., da=100, a=200)`, come
  la prova 7), con il segnale.
* **Periodo**: dal 5 giugno 2023 al 5 ottobre 2026, come la prova 135.
* **Una regola nuova provata su dati non usati**: nel conto delle prove diventa **234** (come le prove 64 e 122).

## 3. L'esame

* **La conferma passa se**, sulle monete 101-200:
  * l'esame delle prove a portafoglio dà VALIDA (`terza.esame`, `terza.esito`: lo Sharpe corretto con l'aggiunta sopra 0,95 contando
    tutte le prove, il netto con l'intervallo sopra zero, gli anni, i trimestri, i costi doppi);
  * e lo Sharpe è sopra quello di **G1 sulle stesse monete** (il funding di Binance da solo, stesso universo e stesso conto).
* **Se passa**: revisore separato (che cerchi anche errori di dati e di date nel funding di Hyperliquid), poi la misura in avanti nel
  paper del bot (`DRY_RUN` vero), insieme alla stessa regola sulle prime 100.
* **Se non passa**: il verso al contrario resta un numero visto sui dati della prova 135, da guardare solo in avanti.
* **Per capire, senza decidere niente**: la stessa regola sulle prime 100 (già vista, Sharpe atteso intorno a +2 prima di rifare i
  costi); i due lati; per anno; le spese; la correlazione con G1.
