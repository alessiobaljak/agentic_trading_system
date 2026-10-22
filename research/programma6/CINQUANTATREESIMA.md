# Programma 6 — cinquantatreesima prova: il funding di ogni moneta rispetto alla sua storia (F8)

Scritto il 22 ottobre 2026, sera, **prima del calcolo**. Idea nuova: F5 confronta le monete fra loro; qui ogni moneta si
confronta **con sé stessa**, come chiede il proprietario («strategie per tutte le crypto»): la regola vale per ognuna da sola.

## 1. Perché

Koijen, Moskowitz, Pedersen e Vrugt («Carry», *Journal of Financial Economics* 2018) trovano che il «carry» funziona in tutti i
mercati anche nel tempo, non solo fra un titolo e l'altro: quando il costo di tenere una posizione è insolitamente alto, il
rendimento dopo è più basso. Per un perpetuo il costo del long è il funding: quando una moneta paga un funding molto più alto
del suo solito, i long sono affollati e tendono a perdere; quando è molto più basso, il contrario.

## 2. La regola (valori fissati qui)

* **Monete**: l'universo della settimana (le 100 più scambiate, dati corretti).
* **z** di ogni moneta il lunedì: (funding dei 7 giorni prima − la media dello stesso numero nelle **26 settimane** prima) /
  la sua deviazione (almeno 13 settimane).
* **Posizione**: **short** se z > **1**, **long** se z < **−1**, altrimenti niente.
* **Pesi**: ogni moneta presa pesa 2 × (1/volatilità dei 30 giorni) / Σ(1/volatilità) di **tutte** le monete dell'universo (così
  che con tutte le monete prese il totale sia 2, come F5); l'esposizione netta cambia con il mercato.
* Costi e funding come F5 (`terza.conto`). Dal 4 gennaio 2021 al 5 ottobre 2026. Una prova: nel conto diventano **112**.

## 3. L'esame

`terza.esame` e `terza.esito` con lo Sharpe corretto rivisto (`asticella.py`), soglia 0,95; si riportano anche il numero medio di
long e short, l'esposizione netta media, il beta verso il Bitcoin e la correlazione con F5.
