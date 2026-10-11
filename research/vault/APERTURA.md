# Apertura del vault — 2026-10-11 19:25 UTC

Frase del proprietario: «APRI IL VAULT», scritta in chat esattamente così l'11 ottobre 2026 alle 17:29 UTC (`research/PROTOCOLLO.md` 4.5, regola 1 e Passo 5). Il vault (2024-01-01 → 2026-09-30) si apre una volta sola.

**Prerequisiti del Passo 5.** Tutte le campagne hanno consegnato: le 20 monete il 9 ottobre (`research/passo4/riepilogo.md`, 3 candidati) e la campagna di gruppo l'11 ottobre (nessuna strategia valida). Test da rieseguire segnalati dalle campagne: nessuno; la suite della ricerca rieseguita l'11 ottobre sul branch principale: 2374 passati. Esito dell'ultima prova a placebo con la regola «nettamente» in vigore (`research/taratura/placebo/risultati.md`, 9 ottobre): l'esame regge.

**Probabilità per moneta del trasferimento (Passo 6, punto 4): 0,02** — il più alto fra `trasferimento.caso_per_moneta_minimo` 0,02, la quota M1 sul totale 6/1.479 = 0,0041 e la quota «netta» in validazione 4/1.348 = 0,0030 della prova a placebo del 9 ottobre. Da qui non cambia più.

## Candidati congelati

Ogni candidato gira UNA volta con il suo codice, dal worktree staccato sulla punta del branch della sua campagna, compresa la sua regola per allineare last e mark (BTCUSDT-V10, consegna 4.4: la sua; BNBUSDT-045 e ADAUSDT-037, consegne 4.5: quella del loro codice).

### Candidato BTCUSDT-V10

Candidato BTCUSDT-V10 (branch `research/campagna/BTCUSDT`, commit 8634b6ac11fd80a92341b966c1a29684c6588b8a)

Semi del tasso del caso: 0-999

SHA-256 dei file congelati (formato di `sha256sum`):

```
34ed067ea5b6d01b5e7d6e91f11e8e844b6e90e25c0d12bc3513b2ff22ca37e1  research/campagne/BTCUSDT/candidati/V10/regole.md
6e79b249d6261731a4933fdb62f8d8b4ece6c41d7f2ea9dc965458b719d80b5e  research/campagne/BTCUSDT/codice/varianti.py
4faac8024b1e315d618b12ad325b11f0b218de6a026fb124f0ab3d066c101b06  research/campagne/BTCUSDT/codice/quadro.py
5df5b8cd4f8089969e0e61c83498ca84a13ea54c622768bae7f1830ec2a67ee1  research/campagne/BTCUSDT/codice/comune.py
350aa8d4a52c3671e79e3f02653051ab0680b63ab7020b65b2232d08b4191217  research/campagne/BTCUSDT/codice/validazione.py
b3d5e1a93954f5b8cad34b74937592cf2b0ade237cbcc1e789a0ee195e6b0970  research/src/motore.py
874f04ca5fec791cba3b54cd25895f52085823c22f5d067eece19abea435ef4e  research/src/dati.py
b823dcfc5f50eb3ad6e55c23c94f02f8b0162121127752e8213e24b75046ae7f  research/src/statistica.py
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  research/src/__init__.py
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  research/__init__.py
```

### Candidato BNBUSDT-045

Candidato BNBUSDT-045 (branch `research/campagna/BNBUSDT`, commit 2e29620af29acfaf70b0340eedfd28a4113cd65c)

Semi del tasso del caso: 0-999

SHA-256 dei file congelati (formato di `sha256sum`):

```
e5b2bd86046e0ff402b60c50a99613300eb967dd22b15444d08c614144a9cf61  research/campagne/BNBUSDT/candidati/BNBUSDT-045/regole.md
55170e59bf87d3582c1f5dd937c6a923c4720881b7ebdc0662f9f45b3878daad  research/campagne/BNBUSDT/codice/varianti.py
96419bd65e0696bbfc985f07853b6f890f81a69d91f82e77a5906fe7aed66c69  research/campagne/BNBUSDT/codice/comune.py
5f4629398cc9294e629bfc7baceaa709afdbf3b9ed6e67ad71dd75317f99ed27  research/campagne/BNBUSDT/codice/validazione.py
27ae6760ad24cd5c49b90371414732e54eaa0f063aed6ef41abfb4942e371748  research/campagne/BNBUSDT/codice/registro.py
395b52409494f79ebec28a57866162b60aa37750cb15482232f536b3bf49a950  research/src/dati.py
b3d5e1a93954f5b8cad34b74937592cf2b0ade237cbcc1e789a0ee195e6b0970  research/src/motore.py
e5d5f0e42b7f4823b6db4a91152b32fc6b2d2bf6b0b3bddf4183ee542d1c3f92  research/src/statistica.py
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  research/src/__init__.py
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  research/__init__.py
736fe598b5179db70d3f63f134922fea428322ce40476c59c9204740653b066f  research/config/parametri.yaml
b4e4731ea4b792e63b5669d316b32e01aaad0b0209c462eac2a719b31f9fc338  research/campagne/BNBUSDT/impronte.json
```

### Candidato ADAUSDT-037

Candidato ADAUSDT-037 (branch `research/campagna/ADAUSDT`, commit 47d6b2cce7d9ac8983c0bfa680c5c82696eae6aa)

Semi del tasso del caso: 0-999

SHA-256 dei file congelati (formato di `sha256sum`):

```
731a06569ef2d6f4408af87c648b7e2b0f3b92a02475ff41a27241b5c73654c9  research/campagne/ADAUSDT/candidati/ADAUSDT-037/regole.md
e447ec1898e2b62f0600a9e0450fb8da3b6544590a8e7abf0f0c51bbdad04841  research/campagne/ADAUSDT/codice/varianti.py
acf2086ab5c3f302dfc1f5b708398197e33f6a7683f23426b3ceeb323a667215  research/campagne/ADAUSDT/codice/comune.py
861f7dc8761a21f07138ceef2a9aa9ab1cd14813e28936fb3dc91768cd3913bd  research/campagne/ADAUSDT/codice/registrazioni.py
228e16a68d05e9312303eaf240775300a5bd91f2098a6eb9a5f143ef19c214cf  research/campagne/ADAUSDT/codice/validazione.py
99f50c6ca28b05a894ebbf5bb8ebe0bb39df9ebc32d05d2602f4d0dbac7f945f  research/campagne/ADAUSDT/codice/run.py
a2629684dcba6d344e7050343c63d884f56c2e2df7d538fd7b6eac091ebc48d3  research/campagne/ADAUSDT/codice/registro.py
395b52409494f79ebec28a57866162b60aa37750cb15482232f536b3bf49a950  research/src/dati.py
b3d5e1a93954f5b8cad34b74937592cf2b0ade237cbcc1e789a0ee195e6b0970  research/src/motore.py
e5d5f0e42b7f4823b6db4a91152b32fc6b2d2bf6b0b3bddf4183ee542d1c3f92  research/src/statistica.py
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  research/src/__init__.py
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  research/__init__.py
```

## Scelte scritte prima di vedere i dati

Il protocollo non le fissa; proposte al proprietario prima della frase e approvate con essa (diario dell'11 ottobre):

1. **Semi.** Le 1000 entrate casuali della quarta condizione del `criterio_vault` e del tasso del caso usano i semi 0-999 (`simulazioni_caso: 1000`); la baseline (b) del vault, solo per il rapporto, usa i semi 0-199 come in validazione.
2. **Serie calda e taglio.** Ogni candidato carica la serie dal primo giorno della sua campagna al 2026-09-30 con la sua regola di caricamento, come in validazione; contano solo i trade entrati dal 2024-01-01 00:00 UTC, e le entrate casuali non possono entrare prima di quell'istante. Metriche del criterio sui soli trade del vault.
3. **Tasso del caso.** Ogni strategia fittizia si giudica con lo stesso `criterio_vault` e con lo stesso 90° percentile degli R medi delle 1000 (lei compresa); il lanciatore riporta anche quante fittizie superano ogni condizione. Sotto i 30 trade del vault l'esito del candidato è «non si sa».
4. **Regola dei dati** (regola tecnica del coordinamento, detta al proprietario l'11 ottobre): un file mensile mancante o illeggibile, una serie che non arriva all'ultima barra del 2026-09-30, un mese con meno del 50% delle barre allineate o senza funding fermano il giro PRIMA di eseguire il candidato, senza risultato e senza consumare il vault; i mesi sotto il 99% (giorni di mark mancanti, come nell'in-sample) si riportano con un avviso. Dopo l'esecuzione del candidato ogni fine scrive un risultato.
5. **Lanciatori** (branch `research/coordinamento`, commit 92946ab2, committati prima di questo file):

```
e41893c0863570afc66641af4b3958f96ef06ec4c9c235dc9d4795d125d1ff8d  research/vault_strumenti/BTCUSDT.py
3168e3e4ea61fcece0c8ccd9426a7c9071a3d8f068d6d2015ad62a6d68b45383  research/vault_strumenti/BNBUSDT.py
ed89a4d0104762bae6345b7c562ee8f79c900a9a3df17ef328edf72b70064c98  research/vault_strumenti/ADAUSDT.py
```

6. **Passo 5, punto 2.** I dati del vault delle altre 17 monete di campagna si scaricano dopo i tre giudizi, prima del Passo 6; la ricucitura delle migrazioni (MATICUSDT → POLUSDT, FTMUSDT → SUSDT) si decide al Passo 6 con il proprietario, sui dati.

