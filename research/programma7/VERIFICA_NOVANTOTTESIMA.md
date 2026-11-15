# Verifica della prova 160 (regole `NOVANTOTTESIMA.md`, commit 3dc968b)

Esito: **eseguibile, nessuna ambiguità che cambi l'esito**; letture scelte elencate sotto. I numeri non erano stati guardati prima.

## Controlli
* Regole committate (3dc968b, più la nota di 161 in dd1399d). Controllo dati dell'archivio (`buchi_archivio`): un'unica moneta con giorni mancanti da settembre, non toccata da queste serie (le serie sono già calcolate).
* Colonne: G1 con lo stop `giorni_G1_con_stop.csv.gz` ha `giorno, capitale_inizio_giorno, rendimento, spese, funding`; il coperto «161 B» `giorni_B.csv.gz` ha l'indice senza nome (giorno) e `netto` (rendimento sul patrimonio composto). Nomi diversi, si usano `rendimento` e `netto`.
* Date: 2.100 giorni in entrambe, dal 18631 (lunedì 4 gennaio 2021) al 20730 (4 ottobre 2026), identiche; 300 settimane intere. Il capitale di G1 è la composizione del rendimento giornaliero (verificato sulle prime righe).

## Letture scelte (nessuna cambia l'esito; la sensibilità è misurata nei controlli)
1. Il primo giorno non ha costo d'ingresso (le due serie sono già nette delle loro spese d'ingresso). Il riequilibrio avviene all'apertura del primo giorno di ogni mese, prima del rendimento di quel giorno.
2. Valore spostato = |peso di G1 alla deriva − peso fissato| × patrimonio; costo = spostato × (0,05% + 0,02%) sulla gamba di G1 + spostato × (0,05% + 0,01%) sulla gamba del coperto, tolto dal patrimonio prima di dividere. Non si usa il 0,15% a pronti del coperto (le regole dicono 0,05%).
3. Il rendimento della miscela è il patrimonio di fine giorno su quello di fine giorno prima (il costo del riequilibrio cade nel giorno del primo del mese). Le settimane si compongono dai giorni, lunedì in giorni dall'epoca.
4. Esame: stesso conto della 161 (`terza.numeri_settimana`): Sharpe settimanale per √52, t = Sharpe × √(settimane/52); «anno positivo» = media settimanale dell'anno positiva (controllo con il rendimento composto dell'anno: stesso verdetto); Sharpe corretto con `corretto_famiglie` sul mazzo completo (che già contiene 158 e 161 A/B) più «160 A» e «160 B».
5. «Utile»: (1) discesa massima = massimo calo dal picco della curva giornaliera, 5 punti = 5 punti percentuali (≥ 0,05 sotto G1); (2) Sharpe settimanale √52 della miscela ≥ Sharpe di G1 − 0,05; (3) mesi di calendario con rendimento composto negativo, meno di G1 (stretto); i mesi parziali di gennaio 2021 e ottobre 2026 contano (70 mesi).
6. Newey-West: pesi di Bartlett, 13 e 26 ritardi, sulle settimane, varianza con divisione per n; t = media / errore. Parti = G1 con lo stop da solo e il coperto 161 B da solo. Controllo descrittivo, non cambia l'esame.
7. Rendimento in USDT su 1.000: composto l'anno × 1.000 (si scrive anche la media × 52).
