# Lezioni di metodo proposte — campagna PANIERE (solo metodo e trappole dei dati)

1. **Lo stop in ATR giornalieri senza tetto produce violazioni di liquidazione dopo i crolli.** Con 2,5 ATR(20) a
   barre giornaliere lo stop arriva al 79-95% del prezzo su monete appena crollate (8 trade su 2.327 in
   PANIERE-043): basta una violazione per scartare un candidato. Va saputo PRIMA di approvare un terreno: o un tetto
   allo stop (in percentuale, sotto 0,8 volte la distanza della liquidazione) o un filtro che non entra quando l'ATR
   supera una soglia, deciso prima delle varianti. Oggi lo scopre la Fase 4, dopo tutto il budget.
2. **Gli strumenti dell'esame vanno provati sul terreno della campagna prima dell'apertura.** In questa campagna
   `gruppo.py` non passava la serie di paniere alle varianti e costruiva l'ingresso a mercato invece che a limite:
   due STOP e circa 4,7 ore di pausa. Una prova di codice con una variante finta del terreno nuovo (un ordine
   limite riempito, una classifica letta dal contesto) l'avrebbe mostrato prima.
3. **Nel file delle impronte solo le serie che la sessione può scaricare.** `impronte_1d.json` registrava 96 file a 8
   ore di BTCUSDT che le regole del paniere vietano di scaricare: la sessione deve escluderli a mano dal confronto.
4. **I parametri «di scelta» non si spostano nella robustezza.** `monete_in_ritardo = 0` voleva dire «tutte»: lo
   script di Fase 4 lo ha spostato a −1 e 1 (due casi senza senso, poi corretti). Nel modulo conviene un parametro
   diverso per la scelta (per esempio `tutte: true`) e uno numerico per il taglio.
5. **La fine della costruzione taglia i trade aperti («fine dati») e può metterli fra i giorni migliori.** Il 15-16
   gennaio 2023 sono i due giorni migliori dei candidati per le uscite forzate a metà del rialzo di gennaio: la prova
   sugli estremi li toglie, ma andrebbe detto nella lettura di ogni variante breve.
6. **Con l'ordine limite e le soglie del gruppo molte idee lente non arrivano a 700 trade sommati** (7 su 18): conviene
   stimare la frequenza a mente prima di scrivere le varianti di un'idea a barre giornaliere.
7. **Le forme rifiutate dal guardiano restano le stesse**: `2>&1`, `sed -i`, `git log` fuori dalla propria cartella
   (tre errori miei, già scritti in `lezioni/metodo.md`).
