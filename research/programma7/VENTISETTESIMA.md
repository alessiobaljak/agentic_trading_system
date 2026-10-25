# Programma 7 — ventisettesima prova: F5 con l'esposizione secondo il carry atteso (F5C)

Scritto il 25 ottobre 2026, alle 06:35 UTC, **prima di qualunque calcolo**. Idea 57 della coda di `research/REGISTRO.md`. Vale
`programma6/VENTIQUATTRESIMA.md` (F5) dove qui non si dice altro.

## 1. Perché

Il guadagno di F5 ha due parti: il funding che il lato venduto incassa e il lato comprato paga (noto prima della settimana: è il
segnale stesso) e il movimento dei prezzi. Il **carry atteso** della settimana è la differenza di funding fra i due lati, pesata con
i pesi di F5. Quando è grande, F5 ha carburante anche se i prezzi stanno fermi; quando è piccolo, guadagna solo dal prezzo e il
rischio è lo stesso. Scalare l'esposizione con il carry atteso è una regola con un perché esatto, diversa dall'idea 45 (il livello
medio del funding del mercato) e **mai guardata sui dati**. Il dubbio scritto prima: se il grosso del rendimento di F5 viene dal
prezzo e non dal funding, il carry atteso non dice niente; e un'esposizione variabile aggiunge giro.

## 2. La regola (valori fissati qui)

* Segnale, universo, banda e pesi: **identici a F5** (`ventiquattresima.pesi_banda`, parità corrette).
* **Carry atteso** della settimana k: Σ sul lato short di |w| · f7 − Σ sul lato long di w · f7, con f7 il funding dei 7 giorni prima
  (`sesta.funding_7`, lo stesso del segnale), in frazione per settimana.
* **Fattore di esposizione**: il carry atteso diviso la **mediana del carry atteso delle 26 settimane precedenti** (almeno 8; prima,
  fattore 1), **fra 0,5 e 1,5**; i pesi di F5 moltiplicati per il fattore (esposizione lorda da 100% a 300%).
* Costi e funding come F5; dal 4 gennaio 2021.
* Due serie nel conto: **F5C** e il **controllo a esposizione casuale** (lo stesso fattore mescolato fra le settimane, seme 2026: se F5C
  non fa meglio del fattore mescolato, il merito non è del carry): nel conto diventano **158**.

## 3. L'esame

`terza.esame` dal 4 gennaio 2021 (anni pieni 2021-2025), Sharpe corretto con l'aggiunta e il t, confronto con F5 sulle stesse
settimane e con il controllo; la decisione del proprietario del 24 ottobre. Si riportano la quota del rendimento di F5 che viene dal
funding, il carry atteso medio e la correlazione fra carry atteso e rendimento della settimana (F5 non scalata).
