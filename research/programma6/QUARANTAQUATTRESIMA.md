# Programma 6 — quarantaquattresima prova: il denaro nuovo delle stablecoin (S1)

Scritto il 21 ottobre 2026, pomeriggio, **prima di scaricare i dati e di qualunque calcolo**. Idea nuova, non nel registro
(la prova 13 usava il funding medio del mercato per il Bitcoin, non i flussi di denaro).

## 1. Perché

Per comprare cripto sugli exchange si usano soprattutto le stablecoin (USDT, USDC e le altre ancorate al dollaro). Quando ne
vengono emesse di nuove, è denaro che entra nel mercato e cerca qualcosa da comprare; quando vengono riscattate, è denaro che
esce (nel 2022 l'offerta è calata per mesi). Studi pubblicati trovano che le emissioni grandi precedono rendimenti del Bitcoin
più alti (Griffin e Shams 2020; Ante, Fiedler e Strehle 2021), altri no: è un'idea con un perché, da provare con una regola
fissata prima. La regola guarda la settimana prima e tiene la settimana dopo, quindi misura se il flusso **anticipa** il
prezzo, non se lo accompagna.

## 2. La regola (valori fissati qui)

* **Dati**: l'offerta totale delle stablecoin ancorate al dollaro, giorno per giorno, da DefiLlama
  (`stablecoins.llama.fi/stablecoincharts/all`, campo `totalCirculatingUSD.peggedUSD`), scaricata una volta con l'impronta
  (`scarico_stablecoin.py`).
* **Segnale** del lunedì: la variazione dell'offerta dal sabato di due settimane prima al sabato prima (il dato del sabato,
  due giorni prima del lunedì, per non usare un dato che a quell'ora non c'era ancora).
* **Posizione** per la settimana (dall'apertura del lunedì a quella del lunedì dopo): **long il perpetuo del Bitcoin al
  100%** se la variazione è sopra zero, altrimenti niente.
* **Costi**: a ogni entrata e uscita commissione 0,05% più 0,01% di scarto; il funding del Bitcoin pagato (o incassato) nei
  giorni tenuti.
* Settimane dal 4 gennaio 2021 al 5 ottobre 2026. Una prova: nel conto del programma 6 diventano **68**.

## 3. L'esame

`terza.esame` e `terza.esito` come le altre (intervallo sopra zero, Sharpe corretto sulle **68** prove almeno 0,95, 4 anni su
6, ultimo anno, costi doppi, trimestri, **più del Bitcoin**: il guadagno oltre quello del Bitcoin tenuto deve essere sopra
zero). Si riportano anche il Bitcoin tenuto sempre sulle stesse settimane, la quota di settimane in posizione, per anno.
