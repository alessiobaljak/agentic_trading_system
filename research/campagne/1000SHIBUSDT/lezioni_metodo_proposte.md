# Lezioni di metodo proposte — 1000SHIBUSDT

Solo errori di metodo e trappole dei dati (sezione 10). Restano qui fino al Passo 7.

1. **Con stop in ATR, battere la (b) può essere un effetto costi.** La (b) entra in barre
   qualunque con lo stesso calcolo dello stop; una condizione che sceglie barre volatili ha
   stop più larghi e quindi un costo per trade più piccolo in R. Il segno: il `t` contro la (b)
   CRESCE a costi doppi (qui 2,08 → 2,56 e 2,15 → 2,48) mentre l'R medio scende sotto zero. Il
   criterio dei costi doppi della Fase 4 (R a costi doppi positivo) lo intercetta; vale la pena
   guardare sempre anche il costo medio in R del candidato e della (b).
2. **L'ordine dei ritocchi può concentrare tutti i ritocchi in una famiglia.** Qui la prima
   della lista (008) è rimasta prima per tutti e 5 i ritocchi, perché i suoi ritocchi o
   diventavano candidati (esclusi dalla lista) o scendevano sotto i 70 trade (scarti che contano
   come ritocchi). Il massimo di 5 ritocchi per famiglia ha funzionato da freno; due ritocchi su
   cinque sono stati sprecati in scarti: prima di scrivere un ritocco con un filtro in più vale
   la pena chiedersi se resta sopra i 70 trade (senza contare regole non registrate).
3. **Uno stop «k ATR» va limitato al tetto del bot prima dei test** (qui con il 6%: ATR mediano
   a 4 ore 3,0%, a 1 giorno 8,0%). Il tetto è rispetto alla chiusura di segnale: rispetto
   all'entrata vera, con il gap all'apertura e lo slippage, lo stop supera di poco il 6% in una
   parte dei trade, e il conteggio va dichiarato.
4. **Il primo mese della scheda può non avere dati per giorni.** Qui la prima candela è del
   2021-05-10, non del 2021-05-01: le date restano quelle di `periodi_campagna`, ma la
   costruzione vera è più corta (673 giorni invece di 682) e va scritto in `fase0_dati.md`.
5. **Forma dei comandi.** Oltre a quelle già in `lezioni/metodo.md`, il guardiano rifiuta la
   lettura dell'uscita dei comandi in background (cartella temporanea della sessione) e una
   parola come `research` usata da sola in un `grep`: gli script lunghi devono scrivere il loro
   resoconto in `data/insample/<SIMBOLO>/`.
6. **Scarico dei dati.** Lo scarico in background si è interrotto una volta con un errore
   (rete); rilanciato in primo piano è andato a termine. Il controllo del CHECKSUM evita file
   rotti su disco.
