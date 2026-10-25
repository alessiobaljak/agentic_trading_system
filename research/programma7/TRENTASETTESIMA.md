# Programma 7 — trentasettesima prova: i flussi dell'ETF sul Bitcoin come segnale del giorno dopo (G24)

Scritto il 25 ottobre 2026, alle 08:03 UTC, **prima di qualunque calcolo sui prezzi**. Idea 63 della coda di `research/REGISTRO.md`.
Fonte: il file storico pubblico di iShares per il fondo IBIT (NAV per quota e quote in circolazione, ogni giorno di borsa dal 5 gennaio
2024; letto il 25 ottobre 2026, 705 righe). Il sito Farside (i flussi di tutti gli ETF) blocca gli strumenti automatici: si usa il fondo
più grande come sostituto, dichiarato. Il file di iShares è per uso personale e **non si copia nel repository** (è nella cartella dati,
fuori da git): si pubblicano solo i risultati.

## 1. Perché, e il dubbio

I flussi degli ETF americani a pronti sono domanda vera di Bitcoin (chi compra l'ETF fa comprare Bitcoin all'emittente), pubblica ogni
sera; non è leva, non è funding: un'informazione diversa da tutto quello che abbiamo provato, messa insieme con i prezzi come chiede il
proprietario. L'ipotesi: la domanda degli investitori tradizionali arriva a ondate e un giorno di flussi forti anticipa altri acquisti.
**Il dubbio scritto prima**: i flussi seguono il prezzo (chi compra dopo il rialzo), le quote in circolazione cambiano con un giorno di
ritardo rispetto agli ordini (le creazioni si regolano il giorno dopo), la storia è corta (dal 2024, dentro un mercato in salita), e un
emittente solo. Probabilità bassa-media.

## 2. La regola (valori fissati qui)

* **Flusso del giorno d** (giorno di borsa americano): (quote in circolazione di d − quote di d−1) × NAV di d, in dollari.
* **Segnale**, con gli ultimi 20 flussi noti: **long** il Bitcoin se il flusso di d è positivo **e** sopra la mediana dei 20 flussi precedenti;
  **short** se è negativo **e** sotto la mediana; altrimenti niente. I primi 20 giorni di borsa servono solo a riempire la finestra.
* **Operazione**: entrata all'apertura della candela oraria delle **02:00 UTC** del primo giorno di calendario dopo d (il file di iShares
  è aggiornato la sera americana di d, cioè prima delle 02:00 UTC), uscita all'apertura delle 02:00 UTC del giorno dopo (24 ore); perpetuo
  BTCUSDT, costi del Bitcoin a mercato in entrata e in uscita; niente funding. Se il giorno dopo d è un giorno di borsa con un flusso nuovo, la
  posizione si decide di nuovo (un'operazione al giorno di calendario, al massimo).
* **Controlli**: (a) i flussi mescolati a caso fra i giorni (2.000 permutazioni, seme 2026): la distribuzione della media delle operazioni;
  (b) il Bitcoin tenuto sempre negli stessi giorni (per separare il segnale dal mercato in salita del 2024-2025).
* Una prova a eventi: nel conto **169**, le prove a eventi **28**.

## 3. L'esame

Media delle operazioni sopra zero con **p ≤ 0,01** (bootstrap), positiva nelle due metà (2024; 2025-2026), e sopra il controllo (b) sugli
stessi giorni; contando le 28 prove a eventi la soglia è 0,00036. Si riportano: quante operazioni long e short, il rendimento medio di
ciascun lato, per anno, la quota di permutazioni che fa almeno come i flussi veri, e lo Sharpe della serie giornaliera.
