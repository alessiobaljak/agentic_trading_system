# Programma 7 — risultati dell'ottantottesima prova (prova 150: l'asimmetria dei minuti)

Regole in `OTTANTOTTESIMA.md` (commit 50f97e7, scritte prima del calcolo). Codice: `ottantottesima.py`; dati completi: `risultati_ottantottesima/esame.json`; registro delle varianti: `research/trials/ottantottesima.csv`. Dal 4 gennaio 2021 al 31 ottobre 2026.

## Letture scelte dove le regole lasciano margine (da confermare)

* rendimento r = logaritmo del rapporto fra la chiusura dell'ultimo minuto di un blocco da 5 (allineato alle 00:00 UTC) e quella del blocco prima; il primo blocco del giorno usa l'ultimo del giorno prima; un blocco con un minuto di chiusura mancante non da' rendimento
* giorno 'completo' = tutti i 1.440 minuti presenti; nella finestra contano solo i giorni completi, n = numero dei rendimenti validi; con meno di 5 giorni completi la moneta e' fuori dall'universo del giorno (il 28 ottobre 2026 manca nell'archivio per tutte: non rattoppato con l'interfaccia pubblica, per trattare tutte le monete allo stesso modo)
* finestra dei 7 (o 30) giorni = i giorni di calendario prima della mezzanotte, mezzanotte esclusa
* universo del giorno = le 100 della settimana (lunedi') come G1, intersecato con le monete che hanno il segnale; pesi e banda come G1 (volatilita' dei 30 giorni dal pannello, `ventiquattresima.pesi_banda`)
* ordine: segnale piu' basso = acquisto (RS basso), segnale piu' alto = vendita: `pesi_banda` compra il rango alto, quindi il segnale passato e' -RS
* spese a limite come G1 (`cinquantaseiesima.spese_a_limite`, candele a 1 ora); accanto, tutto a mercato
* Sharpe corretto (probabilita', `terza.sharpe_corretto`, 52 settimane): N = 308 (306 + 2 varianti); la varianza viene dagli Sharpe dei gruppi del conto (`asticella`) piu' le 2 varianti.

## Le 2 varianti

| variante | rendimento l'anno | Sharpe | anni positivi | t | Sharpe corretto | giro (media sett.) | spese l'anno | a mercato (rend., Sharpe) | corr. G1 giorni | corr. segnali (rango) | esito |
|---|---|---|---|---|---|---|---|---|---|---|---|
| v7 (7 giorni) | -1.4% | -0.04 | 3/6 | -0.10 | 0.00 | 4.52 | 15.0% | -2.7%, -0.08 | -0.01 | -0.08 | non passa: netto non positivo; anni positivi 3/6; t -0.10 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| v30 (30 giorni) | -10.8% | -0.35 | 2/6 | -0.85 | 0.00 | 1.87 | 6.4% | -11.2%, -0.37 | -0.01 | -0.09 | non passa: netto non positivo; anni positivi 2/6; t -0.85 sotto 3; Sharpe corretto 0.00 sotto 0,80 |

## Dettagli per variante

### v7 (7 giorni)
* Rendimento l'anno -1.4%, volatilita' 32.7%, Sharpe -0.04, discesa -65.9%, 304 settimane; netto a costi doppi per settimana -0.315%.
* Per anno: 2021 +35.9%, 2022 +5.6%, 2023 +15.0%, 2024 -7.9%, 2025 -15.1%, 2026 -50.1%.
* Lato long +21.5% l'anno, lato short -19.0%, funding +3.0% l'anno (come somme sull'anno, prima dei costi).
* Spese 15.0% l'anno (limite); tutto a mercato 16.3%. Ordini: {'variazioni': 121892, 'eseguite_con_il_limite': 12790, 'senza_candele_a_1_ora': 108969}.
* Movimenti: 5.3 entrate e 5.3 uscite al giorno; durata media 9.7 giorni; monete con segnale (mediana) 100; giorni con posizioni 2127 su 2127.
* Correlazione con G1: rendimenti giornalieri -0.01, settimanali -0.00; correlazione di rango dei due segnali (media dei giorni) -0.08.
* Miscela 50/50 con G1 (solo informativa, rendimenti netti): +25.2% l'anno, Sharpe 1.19, discesa -28.5%; G1 da solo sugli stessi giorni +51.8%, Sharpe 1.89.
* Sharpe corretto 0.00 (solo con i gruppi 0.00); t -0.10.
* **Esito: non passa: netto non positivo; anni positivi 3/6; t -0.10 sotto 3; Sharpe corretto 0.00 sotto 0,80**

### v30 (30 giorni)
* Rendimento l'anno -10.8%, volatilita' 30.5%, Sharpe -0.35, discesa -70.7%, 304 settimane; netto a costi doppi per settimana -0.329%.
* Per anno: 2021 -18.9%, 2022 -2.8%, 2023 +9.5%, 2024 -35.0%, 2025 -23.0%, 2026 +9.7%.
* Lato long +18.2% l'anno, lato short -27.7%, funding +4.7% l'anno (come somme sull'anno, prima dei costi).
* Spese 6.4% l'anno (limite); tutto a mercato 6.8%. Ordini: {'variazioni': 115151, 'eseguite_con_il_limite': 11443, 'senza_candele_a_1_ora': 103568}.
* Movimenti: 1.7 entrate e 1.7 uscite al giorno; durata media 30.8 giorni; monete con segnale (mediana) 100; giorni con posizioni 2127 su 2127.
* Correlazione con G1: rendimenti giornalieri -0.01, settimanali -0.06; correlazione di rango dei due segnali (media dei giorni) -0.09.
* Miscela 50/50 con G1 (solo informativa, rendimenti netti): +20.5% l'anno, Sharpe 1.04, discesa -25.7%; G1 da solo sugli stessi giorni +51.8%, Sharpe 1.89.
* Sharpe corretto 0.00 (solo con i gruppi 0.00); t -0.85.
* **Esito: non passa: netto non positivo; anni positivi 2/6; t -0.85 sotto 3; Sharpe corretto 0.00 sotto 0,80**

