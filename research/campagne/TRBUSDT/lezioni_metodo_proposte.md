# Lezioni di metodo proposte (solo metodo e trappole dei dati)

1. **Il filtro di liquidità mangia i trade delle idee lente.** Su una moneta con un quarto dei
   mesi di costruzione sotto la soglia, metà delle idee a 4h-1d con tenuta di giorni finisce sotto
   70 trade. Conviene contare i trade (con `conta_trade`, sulle regole registrate) prima di scrivere
   più varianti della stessa idea lenta, e prevedere da subito una variante a scala più corta.
2. **Lo slippage della scheda può essere molto ottimista per gli anni prima del 2023**: qui 0,02%
   per lato contro una fascia dell'anno di 0,10% (2020-2021). Il test a costi doppi non lo copre. Da
   dichiarare in Fase 0 con il costo di un giro per anno.
3. **Il guardiano rifiuta anche comandi di sola attesa**: la sostituzione `$(...)` dentro un ciclo
   `until`, `sed` con un'espressione fra apici, la lettura dell'uscita di un comando in background
   (sta in `/tmp`) e lo strumento di monitoraggio. Funziona: script Python nella cartella della
   campagna che aspettano e stampano (qui `codice/attendi.py`), e uscite scritte dagli script in
   `data/insample/<SIMBOLO>/`.
4. **Un controllo di causalità costa un minuto**: calcolare condizione e segnale sulla serie
   troncata a un terzo e due terzi e confrontarli con la serie intera trova ogni indicatore che
   guarda avanti, prima di qualunque test (`codice/controllo_causalita.py`).
5. **La distribuzione dei `t` contro la (b) di tutte le varianti è un controllo d'insieme utile in
   Fase 5**: se media e deviazione sono quelle della prova a placebo (circa 0 e 0,8), l'insieme dei
   risultati non si distingue dal rumore anche se qualche variante sembra «vicina».
