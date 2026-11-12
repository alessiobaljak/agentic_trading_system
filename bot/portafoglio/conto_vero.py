"""G1 sul conto vero di Binance (future USDⓈ-M): ordini veri con soldi veri. **Nasce spento.**

Il proprietario, 8 novembre 2026: «procedi anche con il setup del trade live». Il piano è `docs/conto_vero.md` (fase 2) con
`docs/backlog.md`, P26. **Preparare non è accendere**: questo codice manda ordini solo dopo la richiesta esplicita, ripetuta e
consapevole del proprietario (la regola di `DRY_RUN` in `CLAUDE.md`), con le quattro condizioni qui sotto. Seconda tornata dopo la
revisione dell'8 novembre 2026 (`reviews/reports/2026-11-08-fase2-conto-vero.md`, problemi 53-63).

* **Riusa il demo** (`demo_binance.DemoG1`, approvato con la fase 1 l'8 novembre 2026): lo stesso ribilancio di G1 alla decisione del
  giorno (ordini limite al prezzo mark per un'ora, poi a mercato), le stesse protezioni: margine unico, stop sul conto a −35% dal
  massimo con il pavimento del 65% del capitale di partenza, il pulsante che chiude tutto, da fermo le chiusure ogni minuto fino al
  conto vuoto, «riparti» solo a conto vuoto e sopra il pavimento, gli allarmi per tipo. Qui cambiano l'indirizzo, le chiavi,
  l'interruttore, i file, il ramo di Firebase (`/conto_vero`), i comandi, i limiti e il valore del conto (sotto).
* **Solo `fapi.binance.com`**: `_url` rifiuta qualunque altro indirizzo (anche `http` senza la «s»); `ContoVeroG1` accetta solo il
  suo cliente (`ClienteVero`). Le chiavi sono quelle che `bot/config.py` usa per Binance (`BINANCE_API_KEY`, `BINANCE_API_SECRET`).
* **Gli ordini nuovi partono solo con tutte e quattro**:
  (a) il file `ops/conto_vero_acceso`;
  (b) `DRY_RUN` falso (letto con `bot.config._get_bool_sicuro`: solo «false» scritto così);
  (c) i file del repository caricati nel processo (`file_caricati`) e quelli del percorso degli ordini (`PERCORSI_DEGLI_ORDINI`)
      identici a quelli della **versione approvata dal proprietario**: un commit che scrive lui dalla dashboard, con il suo
      accesso a Firebase, in `/commands/conto_vero_versione_approvata` (`{commit, ora}`; decisione del 12 novembre 2026: «ok
      pulsante in dashboard»). Non più un tag di git: un tag lo sposta qualunque sessione (su GitHub le sessioni agiscono come il
      suo utente, revisione dell'8 novembre, problema 54). **Chi può scrivere quel percorso**: dalla dashboard solo lui (le regole,
      `firebase/database.rules.json`, valgono per chi entra con un utente); ma la chiave di amministratore di Firebase ignora le
      regole, e ce l'hanno il bot, `scripts/ops_agent.py` (sulla macchina, riletto dal branch a ogni minuto) e i flussi di GitHub
      che usano Firebase. Il codice del repository non scrive mai i quattro comandi del conto vero (lo controlla un test,
      `tests/test_conto_vero.py`): l'approvazione protegge dagli errori, non da chi cambiasse il codice per aggirarla (revisione
      del 12 novembre 2026, 54 parte ii: la protezione vera è una decisione del proprietario). Il bot legge soltanto. All'avvio il
      processo deve avere in memoria un commit riconoscibile (HEAD del repository, file uguali, nessun file cambiato dopo l'avvio:
      altrimenti serve un riavvio); ogni minuto (ogni 10 da spento) si rilegge il commit approvato e si confrontano con quello il
      commit in memoria e i file di adesso (la macchina scarica il branch ogni minuto). Commit assente, non valido, non presente
      nel repository della macchina o diverso: niente ordini nuovi. **Se Firebase non risponde** vale solo un'approvazione letta
      davvero da Firebase negli ultimi ``APPROVAZIONE_SENZA_RISPOSTA_S`` (10 minuti; problema 74: un buco di pochi secondi non fa
      saltare il ribilancio né lo lascia a metà), sempre con il confronto di git; oltre, niente ordini nuovi finché non risponde
      (`leggi_rtdb_davvero`: l'ultimo valore noto del client non vale mai);
  (d) un capitale in `ops/conto_vero_capitale`: un numero positivo non oltre `CAPITALE_MASSIMO` e non oltre il saldo vero.
  Senza una delle quattro niente ordini nuovi, con l'allarme `ordini_vietati`, e il cliente rifiuta ogni ordine che non sia «solo
  riduzione». Le protezioni (stop sul conto, pulsante, chiusure da fermo, margine unico) restano attive. **Senza (a) o (b)** (problema
  53): se il conto vero non è mai stato acceso, nessuna richiesta a Binance e nessuna chiave letta; se è stato acceso, le protezioni
  restano finché Binance non dice il conto vuoto (posizioni e ordini), poi nessuna richiesta.
* **Parte vuoto e compra solo alla mezzanotte** (il proprietario, 7 novembre 2026): alla prima accensione, e a ogni riaccensione
  dopo un blocco, il conto aspetta la prima decisione di G1 dopo (00:05 UTC). Alla prima accensione il conto dei future deve essere
  vuoto: con posizioni o ordini non del bot niente ordini e l'allarme `conto_non_vuoto` (problema 59). Un ribilancio in corso quando
  arriva un blocco non si annulla: gli ordini limite vivono la loro ora, poi quelli non eseguiti si annullano senza il resto a
  mercato (problema 56). **Niente eventi.**
* **Il valore del conto** (problema 58): il capitale più i redditi del conto da quando la fase è partita (utili e perdite realizzati,
  funding, commissioni: `REDDITI_DEL_CONTO`, letti da `/fapi/v1/income`), più gli utili non realizzati; non il saldo. Versamenti,
  prelievi e ogni altro movimento non cambiano il valore (si scrivono in `/conto_vero/movimenti_non_contati`); un saldo vero sotto il
  valore del bot (un prelievo) ferma gli ordini nuovi.
* **Lo stato perso** (problema 57): senza `data/conto_vero.json` (o con il file illeggibile) dopo un'accensione già avvenuta (Firebase
  `/conto_vero/acceso_dal` o `/conto_vero/fermo`) il conto parte fermo: chiusure fino al conto vuoto, poi serve «riparti». Se lo
  stato locale non dice niente e Firebase non risponde, niente prima accensione finché non risponde (problema 66).
* **Filtri veri**: dal vero `exchangeInfo` di `fapi.binance.com`, riletti a ogni ribilancio e a ogni resto a mercato.
* **Stato e comandi suoi**: `data/conto_vero.json`, RTDB `/conto_vero`, il pulsante `/commands/conto_vero_chiudi_tutto` (o un testo
  nuovo in `ops/conto_vero_chiudi_tutto`). **«Riparti» in due passi, solo dalla dashboard** (12 novembre 2026): la richiesta in
  `/commands/conto_vero_riparti` (vero) e poi la conferma in `/commands/conto_vero_riparti_conferma`, che deve essere il testo
  esatto di questo fermo (`codice_riparti`: l'ora del fermo pubblicata dal bot, in secondi interi); nessun file del repository fa
  ripartire il conto vero (lo potrebbe scrivere una sessione).
* **La versione in dashboard**: `/conto_vero/versione` dice il commit in esecuzione (HEAD all'avvio del processo: hash, data,
  titolo), se i file caricati sono uguali a quel commit, il commit approvato letto e se coincidono; si scrive anche da spento.
* **I limiti** sono le costanti qui sotto, ognuna fissata da un test di guardia (`tests/test_conto_vero.py`); i limiti fissi del
  vecchio sistema (`bot/risk/hard_limits.py`, `circuit_breakers.py`, `kill_switch.py`) non c'entrano e non si toccano.
"""
from __future__ import annotations

import math
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable, Optional
from urllib.parse import urlparse

import requests

from bot.config import _get_bool_sicuro
from bot.portafoglio import demo_binance as demo

_IMPORTATO_ALLE = time.time()          # se l'ora d'avvio del processo non si legge, i file cambiati dopo l'import di questo modulo
RADICE = demo.RADICE
VERO = "https://fapi.binance.com"
HOST_VERO = "fapi.binance.com"
INTERRUTTORE = RADICE / "ops" / "conto_vero_acceso"
FILE_CAPITALE = RADICE / "ops" / "conto_vero_capitale"
FILE_STATO = RADICE / "data" / "conto_vero.json"
FILE_CHIUDI = RADICE / "ops" / "conto_vero_chiudi_tutto"
NESSUN_FILE = Path(os.devnull)         # il «riparti» del conto vero non ha un file: alla classe del demo si passa questo, sempre vuoto
COMANDO_CHIUDI = "/commands/conto_vero_chiudi_tutto"
# i comandi del proprietario dalla dashboard (decisione del 12 novembre 2026). Le regole (firebase/database.rules.json) li lasciano
# scrivere, fra gli utenti, solo a lui; la chiave di amministratore di Firebase le ignora (il bot, scripts/ops_agent.py, i flussi di
# GitHub): nessun codice del repository li scrive, salvo il falso con cui il bot consuma «chiudi tutto» e «riparti» e la conferma
# che toglie; sulla versione approvata il bot non scrive mai (lo controllano due test in tests/test_conto_vero.py)
COMANDO_RIPARTI = "/commands/conto_vero_riparti"                       # primo passo: vero
COMANDO_RIPARTI_CONFERMA = "/commands/conto_vero_riparti_conferma"     # secondo passo: il testo esatto di `codice_riparti`
COMANDO_VERSIONE = "/commands/conto_vero_versione_approvata"           # {commit: 40 caratteri esadecimali, ora}
CHIAVE_ENV, SEGRETO_ENV = "BINANCE_API_KEY", "BINANCE_API_SECRET"     # gli stessi nomi di bot/config.py
RE_COMMIT = re.compile(r"[0-9a-f]{40}")
PERCORSI_DEGLI_ORDINI = ("bot/portafoglio", "bot/execution", "bot/risk", "bot/config.py", "bot/main.py")
FUORI_DAL_CODICE = (".venv", "venv", "site-packages", "dist-packages", "__pycache__")   # l'ambiente Python sta dentro la cartella
OGNI_CONTROLLO_CODICE_S = 60           # il codice contro la versione approvata: ogni minuto (il git pull della macchina)
OGNI_CONTROLLO_CODICE_DA_SPENTO_S = 600   # da spento ogni 10 minuti (problema 75: niente ordini possibili, solo la dashboard)
APPROVAZIONE_SENZA_RISPOSTA_S = 600    # problema 74: senza risposta di Firebase vale l'approvazione letta davvero fino a 10 minuti fa
SECONDA_LETTURA_ENTRO_S = 5.0          # problema 75: la seconda lettura subito solo se la prima non ha aspettato più di così
TEMPO_GIT_S = 15                       # ogni comando git del controllo; al primo che non risponde il controllo vale «non approvato»
LETTURE_VERSIONE_PRIMA_DELL_ALLARME = 3   # controlli di fila senza risposta di Firebase prima dell'allarme «versione_approvata»
TITOLO_MASSIMO = 140                   # caratteri del titolo del commit scritti in /conto_vero/versione
PERCORSI_ORDINE = ("/fapi/v1/order", "/fapi/v1/batchOrders")
# i redditi che fanno il valore del conto (problema 58): tutto il resto (versamenti, prelievi, premi, rimborsi, tipi nuovi) non conta
REDDITI_DEL_CONTO = ("REALIZED_PNL", "FUNDING_FEE", "COMMISSION", "INSURANCE_CLEAR", "DELIVERED_SETTELMENT",
                     "POSITION_LIMIT_INCREASE_FEE")
PAGINE_REDDITI_MAX = 10                # 1.000 righe per pagina: al massimo 10 pagine per lettura (il resto alla lettura dopo)
# problema 64: i redditi si leggono fino a un minuto fa, ogni volta con 15 minuti già letti (le righe che Binance scrive in ritardo,
# anche con la stessa ora di altre già viste), e i doppioni si tolgono con il tipo e l'identificativo della riga (tranId)
RITARDO_REDDITI_S = 60
SOVRAPPOSIZIONE_REDDITI_S = 900
ERRORI_REDDITI_PRIMA_DELL_ALLARME = 3  # letture dei redditi fallite di fila prima dell'allarme «redditi»

# ---- i limiti del conto vero: ognuno ha il suo test di guardia in tests/test_conto_vero.py ----
LEVA = 5                               # come il demo e la ricerca (prova 56): i due lati insieme fanno il 200% del capitale
CAPITALE_MASSIMO = 300.0               # USDT: il capitale del proprietario è 250 euro, 280 USDT (prova 148); sopra, il file non vale
VALORE_MASSIMO_PER_ORDINI = 2 * CAPITALE_MASSIMO   # oltre (con i guadagni), niente ordini nuovi: serve un capitale nuovo
STOP_CONTO = 0.35                      # il proprietario, 1° novembre 2026: chiude tutto a −35% dal massimo del conto
PAVIMENTO_RIPARTI = 0.65               # lo stop scatta anche sotto il 65% del capitale di partenza; «riparti» non riaccende lì sotto
SOMMA_PESI_MASSIMA = 2.0               # G1 ha i due lati da 1 ciascuno; niente eventi qui (revisione con le skill: «non oltre il 200%»)
PESO_MASSIMO_MONETA = 0.60             # il peso più alto di G1 sul passato è il 47,8% (BLZ, 5 febbraio 2024, docs/backlog.md)
ETA_MASSIMA_DECISIONE_S = 26 * 3600    # G1 decide ogni giorno alle 00:05 UTC; una decisione più vecchia non si esegue
# problema 64: «saldo vero sotto il valore del bot» (un prelievo) ferma gli ordini nuovi solo oltre lo 0,5% del valore (almeno 1 USDT)
# e in 3 letture di fila a un minuto l'una dall'altra. Con 280 USDT la tolleranza è 1,40: un giro di funding di G1 (40 monete, 560
# USDT lordi, 0,01%) muove 0,06 USDT, le commissioni di un ribilancio intero (circa 150 USDT a 0,05%) 0,08; un utile o una perdita
# realizzati nell'ultimo minuto (i redditi si leggono con un minuto di ritardo) spariscono alla lettura dopo
TOLLERANZA_SALDO = 0.005
TOLLERANZA_SALDO_MINIMA = 1.0
LETTURE_SALDO_SOTTO = 3


def _url(percorso: str) -> str:
    url = VERO + percorso
    u = urlparse(url)
    if u.scheme != "https" or u.hostname != HOST_VERO:
        raise ValueError(f"indirizzo non ammesso per il conto vero: {url}")
    return url


def file_caricati(radice: Path = RADICE) -> list:
    """I file del repository caricati in questo processo (i moduli di ``sys.modules`` con ``__file__`` dentro la radice), relativi
    alla radice; fuori l'ambiente Python (`.venv` sta dentro la cartella dell'app sulla macchina) e le cartelle nascoste."""
    radice = Path(radice).resolve()
    out = set()
    for m in list(sys.modules.values()):
        f = getattr(m, "__file__", None)
        if not f:
            continue
        try:
            rel = Path(f).resolve().relative_to(radice)
        except (ValueError, OSError):
            continue
        if any(p in FUORI_DAL_CODICE or p.startswith(".") for p in rel.parts[:-1]):
            continue
        out.add(rel.as_posix())
    return sorted(out)


def avvio_del_processo() -> Optional[float]:
    """L'ora (epoch) in cui questo processo è partito, da `/proc` (Linux); None se non si legge."""
    try:
        campi = Path("/proc/self/stat").read_text().rsplit(")", 1)[1].split()
        btime = next(int(r.split()[1]) for r in Path("/proc/stat").read_text().splitlines() if r.startswith("btime "))
        return btime + int(campi[19]) / os.sysconf("SC_CLK_TCK")
    except Exception:  # noqa: BLE001
        return None


def _git(radice, *argomenti):
    return subprocess.run(["git", "--literal-pathspecs", "-C", str(radice), *argomenti], capture_output=True, text=True,
                          timeout=TEMPO_GIT_S)


def commit_in_esecuzione(radice: Path = RADICE) -> dict:
    """HEAD del repository adesso: ``{"commit", "data", "titolo"}`` (hash intero, data ISO del commit, titolo accorciato); se git
    non risponde ``{"errore": motivo}``. Chiamato all'avvio del processo dice quale commit il processo sta eseguendo, se
    `codice_approvato` con ``cambiati_dopo`` conferma che i file caricati sono i suoi. Non solleva mai."""
    try:
        r = _git(radice, "log", "-1", "--format=%H%n%cI%n%s", "HEAD")
        righe = r.stdout.split("\n")
        if r.returncode != 0 or len(righe) < 3 or not RE_COMMIT.fullmatch(righe[0]):
            return {"errore": f"HEAD del repository non letto ({r.stderr.strip()[:120] or 'risposta di git non attesa'})"}
        return {"commit": righe[0], "data": righe[1], "titolo": righe[2][:TITOLO_MASSIMO]}
    except Exception as exc:  # noqa: BLE001
        return {"errore": f"HEAD del repository non letto ({type(exc).__name__})"}


def _letto_davvero(fb, percorso: str) -> tuple:
    """(vero solo se Firebase ha risposto davvero a QUESTA lettura, valore). Lo dice il client (`leggi_rtdb_davvero` di
    `bot/core/firebase_client.py`); senza Firebase, con un client che non lo sa dire o con un errore vale falso (con l'ultimo
    valore noto, se c'è): chi decide sui soldi veri non prende mai per risposta un valore vecchio."""
    try:
        davvero = getattr(fb, "leggi_rtdb_davvero", None)
        if callable(davvero):
            risposto, valore = davvero(percorso)
            return risposto is True, valore
        return False, (fb.get_rtdb(percorso) if fb is not None else None)
    except Exception:  # noqa: BLE001
        return False, None


def versione_approvata(fb) -> tuple:
    """Il commit che il proprietario ha approvato dalla dashboard, da `/commands/conto_vero_versione_approvata` (`{commit, ora}`):
    ``(commit, None, True)``; altrimenti ``(None, motivo, ha_risposto)``. Senza risposta di Firebase non c'è mai un commit, nemmeno
    quello letto un minuto prima. Non solleva mai."""
    risposto, v = _letto_davvero(fb, COMANDO_VERSIONE)
    if not risposto:
        return None, "Firebase non risponde: la versione approvata dal proprietario non si legge", False
    if v is None or v == "" or v == {}:
        return None, "nessuna versione approvata dal proprietario (dashboard, scheda del conto vero, «Approva questa versione»)", True
    commit = v.get("commit") if isinstance(v, dict) else None
    if not isinstance(commit, str) or not RE_COMMIT.fullmatch(commit):
        return None, "la versione approvata scritta su Firebase non è valida (serve un commit di 40 caratteri esadecimali)", True
    return commit, None, True


def codice_riparti(fermo) -> Optional[str]:
    """Il testo esatto che conferma il «riparti» di QUESTO fermo: l'ora del fermo che il bot pubblica in `/conto_vero/fermo/ora`,
    in secondi interi (la dashboard scrive `String(Math.floor(ora))`). None se il fermo non ha un'ora leggibile: senza, il
    «riparti» non si può confermare."""
    try:
        ora = float((fermo or {}).get("ora"))
    except (TypeError, ValueError, AttributeError):
        return None
    return str(int(ora)) if math.isfinite(ora) and ora > 0 else None


def codice_approvato(radice: Path = RADICE, commit: Optional[str] = None, percorsi: tuple = PERCORSI_DEGLI_ORDINI,
                     caricati=(), cambiati_dopo: Optional[float] = None, in_memoria: Optional[str] = None,
                     nome: str = "la versione approvata") -> Optional[str]:
    """None se il codice è quello del commit ``commit`` (la versione approvata dal proprietario su Firebase, `versione_approvata`;
    all'avvio, con ``nome`` diverso, il commit in esecuzione); altrimenti il motivo. Il commit deve essere di 40 caratteri
    esadecimali e presente nel repository della macchina. Si confrontano i percorsi degli ordini e i file ``caricati`` (problema
    54): identici al commit (`git diff --quiet <commit> -- ...`), nessun file nuovo non ignorato nei percorsi, ogni file caricato
    presente nel commit; con ``in_memoria`` (il commit che il processo ha caricato all'avvio) anche quel commit uguale a questo
    negli stessi file, perché i file di adesso possono essere già quelli nuovi mentre il processo esegue ancora i vecchi; con
    ``cambiati_dopo`` (l'avvio del processo, problema 61) anche nessun file cambiato dopo quell'ora, perché il processo potrebbe
    avere in memoria la versione di prima. Non solleva mai: un errore di git vale «non approvato»."""
    if not isinstance(commit, str) or not RE_COMMIT.fullmatch(commit):
        return f"{nome} non c'è o non è un commit valido (40 caratteri esadecimali)"
    corto = commit[:8]
    da_nome = {"la versione approvata": "dalla versione approvata", "il commit in esecuzione": "dal commit in esecuzione"}.get(
        nome, f"da {nome}")

    def git(*argomenti):
        return _git(radice, *argomenti)

    caricati = [f for f in caricati if f]
    tutti = list(percorsi) + [f for f in caricati if f not in percorsi]
    try:
        r = git("rev-parse", "-q", "--verify", f"{commit}^{{commit}}")
        if r.returncode != 0:
            return (f"{nome} ({corto}) non è un commit del repository della macchina"
                    + (f" ({r.stderr.strip()[:120]})" if r.stderr.strip() else ""))
        if in_memoria and in_memoria != commit:
            if not RE_COMMIT.fullmatch(str(in_memoria)):
                return "il commit in esecuzione non si conosce: serve un riavvio"
            m = git("diff", "--quiet", in_memoria, commit, "--", *tutti)
            if m.returncode == 1:
                nomi = git("diff", "--name-only", in_memoria, commit, "--", *tutti).stdout.split()
                return (f"il processo esegue il commit {in_memoria[:8]}, diverso {da_nome} ({corto}) in: "
                        f"{', '.join(nomi[:5]) or '?'}" + (f" e altri {len(nomi) - 5}" if len(nomi) > 5 else "")
                        + ": serve un riavvio su quella versione, o l'approvazione di quella in esecuzione")
            if m.returncode != 0:
                return f"confronto fra il commit in esecuzione e {nome} ({corto}) non riuscito: {m.stderr.strip()[:120]}"
        d = git("diff", "--quiet", commit, "--", *tutti)
        if d.returncode == 1:
            nomi = git("diff", "--name-only", commit, "--", *tutti).stdout.split()
            return (f"file del codice diversi {da_nome} ({corto}): {', '.join(nomi[:5]) or '?'}"
                    + (f" e altri {len(nomi) - 5}" if len(nomi) > 5 else ""))
        if d.returncode != 0:
            return f"confronto con {nome} ({corto}) non riuscito: {d.stderr.strip()[:120]}"
        n = git("ls-files", "--others", "--exclude-standard", "--", *percorsi)
        if n.returncode != 0:
            return f"file nuovi non controllati: {n.stderr.strip()[:120]}"
        if n.stdout.split():
            return f"file nuovi nel percorso degli ordini, fuori {da_nome} ({corto}): {', '.join(n.stdout.split()[:5])}"
        if caricati:
            t = git("ls-tree", "-r", "--name-only", commit, "--", *caricati)
            if t.returncode != 0:
                return f"file caricati non controllati: {t.stderr.strip()[:120]}"
            fuori = sorted(set(caricati) - set(t.stdout.split()))
            if fuori:
                return f"file caricati nel processo che {nome} ({corto}) non ha: {', '.join(fuori[:5])}"
        if cambiati_dopo is not None:
            nel_percorso = git("ls-files", "--", *percorsi).stdout.split()
            dopo = sorted(f for f in set(nel_percorso) | set(caricati)
                          if (Path(radice) / f).exists() and (Path(radice) / f).stat().st_mtime >= cambiati_dopo)
            if dopo:
                return f"file cambiati dopo l'avvio del processo (in memoria forse la versione di prima): {', '.join(dopo[:5])}"
    except Exception as exc:  # noqa: BLE001
        return f"git non eseguito ({type(exc).__name__})"
    return None


class ClienteVero(demo.ClienteDemo):
    """Le richieste al conto vero dei future, firmate con la chiave del conto vero. ``blocco``: se c'è un motivo, ogni ordine che non
    sia «solo riduzione» si rifiuta qui, prima di partire (le chiusure passano); lo aggiorna `ContoVeroG1` a ogni giro e nasce chiuso."""

    NOME = "conto_vero"

    def __init__(self, chiave: str, segreto: str, http: Callable = requests.request) -> None:
        super().__init__(chiave, segreto, http)
        self.blocco: Optional[str] = "condizioni del conto vero non ancora controllate"

    @staticmethod
    def _url(percorso: str) -> str:
        return _url(percorso)

    def chiedi(self, metodo: str, percorso: str, parametri: Optional[dict] = None, firmata: bool = False):
        if (self.blocco and metodo in ("POST", "PUT") and percorso in PERCORSI_ORDINE
                and str((parametri or {}).get("reduceOnly", "")).lower() != "true"):
            raise RuntimeError(f"{metodo} {percorso}: ordine rifiutato dal conto vero ({self.blocco}); passano solo le chiusure")
        return super().chiedi(metodo, percorso, parametri, firmata)


class ContoVeroG1(demo.DemoG1):
    NOME = "conto_vero"
    HOST = HOST_VERO
    COMANDO_CHIUDI, COMANDO_RIPARTI = COMANDO_CHIUDI, COMANDO_RIPARTI
    INTERRUTTORE_DI_SERIE, FILE_CAPITALE_DI_SERIE = INTERRUTTORE, FILE_CAPITALE
    FILE_COMANDI_DI_SERIE = (FILE_CHIUDI,)
    LEVA, STOP_CONTO, PAVIMENTO_RIPARTI, CAPITALE_MASSIMO = LEVA, STOP_CONTO, PAVIMENTO_RIPARTI, CAPITALE_MASSIMO
    SOMMA_PESI_MASSIMA, PESO_MASSIMO_MONETA = SOMMA_PESI_MASSIMA, PESO_MASSIMO_MONETA
    ETA_MASSIMA_DECISIONE_S = ETA_MASSIMA_DECISIONE_S
    VALORE_MASSIMO_PER_ORDINI = VALORE_MASSIMO_PER_ORDINI
    TOLLERANZA_SALDO, TOLLERANZA_SALDO_MINIMA, LETTURE_SALDO_SOTTO = TOLLERANZA_SALDO, TOLLERANZA_SALDO_MINIMA, LETTURE_SALDO_SOTTO
    MANCA_CHIAVE = f"manca la chiave del conto vero ({CHIAVE_ENV} e {SEGRETO_ENV} nell'ambiente del bot)"
    CHIAVE_ILLEGGIBILE = "chiave del conto vero non leggibile"
    CHIAVE_VALORE_VERO = "valore_vero_del_conto"

    def __init__(self, fb, cliente: Optional[ClienteVero] = None, file_stato: Path = FILE_STATO, file_g1: Path = demo.FILE_G1,
                 interruttore: Path = INTERRUTTORE, file_chiudi: Path = FILE_CHIUDI,
                 file_capitale: Path = FILE_CAPITALE, verifica_codice: Optional[Callable[[], Optional[str]]] = None,
                 radice: Path = RADICE) -> None:
        if cliente is not None and not isinstance(cliente, ClienteVero):
            raise TypeError("il conto vero parla solo con ClienteVero (fapi.binance.com)")
        # nessun file per il «riparti» (12 novembre 2026): alla classe del demo va un file sempre vuoto, e `_comando_file` qui sotto
        # non lo guarda nemmeno
        super().__init__(fb, cliente=cliente, file_stato=file_stato, file_g1=file_g1, interruttore=interruttore,
                         file_chiudi=file_chiudi, file_riparti=NESSUN_FILE, file_capitale=file_capitale)
        self.radice = Path(radice)
        self._versione: dict = {}                         # HEAD del repository all'avvio del processo (`commit_in_esecuzione`)
        self._approvata: Optional[str] = None             # il commit approvato letto da Firebase all'ultimo controllo
        self._versione_muta = 0                           # controlli di fila senza risposta di Firebase
        self._versione_scritta: Optional[dict] = None     # l'ultima `/conto_vero/versione` arrivata davvero su Firebase
        self._conferma_attesa: Optional[str] = None       # la conferma del «riparti» del fermo in corso (`_da_fermo`)
        self._verifica_finta = verifica_codice is not None   # solo nei test: nessuna versione da leggere o da pubblicare
        # il codice che questo processo ha in memoria deve essere un commit riconoscibile: HEAD del repository all'avvio, con i file
        # caricati uguali e nessuno cambiato dopo l'avvio. Altrimenti niente ordini finché non si riavvia, anche se dopo i file
        # tornano uguali (problemi 54 e 61): quello che gira non è una versione che il proprietario possa approvare
        if verifica_codice is None:
            self._versione = commit_in_esecuzione(self.radice)
            self._verifica_codice = self._verifica_versione
            self._codice_all_avvio = self._versione.get("errore") or codice_approvato(
                radice=self.radice, commit=self._versione.get("commit"), caricati=file_caricati(self.radice),
                cambiati_dopo=avvio_del_processo() or _IMPORTATO_ALLE, nome="il commit in esecuzione")
        else:
            self._verifica_codice = verifica_codice
            self._codice_all_avvio = verifica_codice()
        # problema 77: prima del primo controllo il codice non vale «approvato»
        self._codice_ora: Optional[str] = self._codice_all_avvio or "versione approvata non ancora letta"
        self._codice_controllato = 0.0
        self._controllato_da_spento = False               # l'ultimo controllo era da spento: all'accensione se ne fa uno subito
        self._letta_davvero: Optional[tuple] = None        # (commit approvato o None, ora) dall'ultima risposta vera di Firebase
        self._fermo_da_riscrivere = False                  # problema 76: l'ultima scrittura di /conto_vero/fermo non è arrivata
        self.cronometro: Callable[[], float] = time.monotonic   # quanto dura una lettura (problema 75); nei test uno finto
        self._spento_scritto: Optional[str] = None
        self._motivo_spento_ora: Optional[str] = None
        self._blocco_ora: Optional[str] = None
        self._firebase_letto: Optional[dict] = None      # /conto_vero/acceso_dal o /conto_vero/fermo, letto una volta
        self._capitale_cr: Optional[float] = None         # il capitale della fase in corso (None prima della prima fase)
        self._redditi = 0.0                               # i redditi del conto dalla partenza della fase (problema 58)
        self._redditi_letti = 0.0
        self._dry_run_letto: tuple = (object(), True)
        self.orologio: Callable[[], float] = time.time   # l'ora vera (problema 65); nei test un orologio finto

    # ---- niente eventi sul conto vero ----
    def eventi_accesi(self) -> bool:
        return False

    def eventi_aperti(self) -> dict:
        return {}

    # ---- (a) e (b) ----
    def acceso(self) -> bool:
        """Per il giro ereditato dal demo, che lo decide qui sopra: `tick` gira anche senza interruttore, nel solo modo protezione."""
        return True

    def interruttore_acceso(self) -> bool:
        return demo.DemoG1.acceso(self)

    def _dry_run(self) -> bool:
        """`DRY_RUN` con `_get_bool_sicuro`, riletto solo quando il valore cambia (problema 63: l'avviso di un valore scritto male una
        volta, non a ogni giro)."""
        grezzo = os.environ.get("DRY_RUN")
        if self._dry_run_letto[0] != grezzo:
            self._dry_run_letto = (grezzo, _get_bool_sicuro("DRY_RUN"))
        return self._dry_run_letto[1]

    def motivo_spento(self) -> Optional[str]:
        if not self.interruttore_acceso():
            return f"manca l'interruttore ops/{self.interruttore.name}"
        if self._dry_run():
            return "DRY_RUN vale vero (solo «false» scritto così lo spegne)"
        return None

    def cliente(self) -> Optional[ClienteVero]:
        if self._cliente is None:
            k, s = os.environ.get(CHIAVE_ENV, ""), os.environ.get(SEGRETO_ENV, "").replace("\\n", "\n")
            if k and s:
                self._cliente = ClienteVero(k, s)
        return self._cliente

    def tick(self, now: float) -> None:
        self._controlla_versione(now)                  # anche da spento: la dashboard mostra la versione prima dell'accensione
        motivo = self.motivo_spento()
        self._motivo_spento_ora = motivo
        if motivo and not self._protezioni_da_spento(now, motivo):
            return
        if not motivo:
            self._spento_scritto = None
        if self._cliente is not None:                  # il freno del cliente si riapre solo dopo il controllo di questo giro
            self._cliente.blocco = "condizioni di questo giro non ancora controllate"
        super().tick(now)
        if self._fermo_da_riscrivere:                  # problema 76: senza il fermo su Firebase la dashboard non può far ripartire
            self._scrivi("fermo", self.carica().get("fermo") or None)
        if motivo:                                     # da fermo il conto vuoto lo dice `_da_fermo`; lo stato lo scrive il giro dopo
            st = self.carica()
            if (st.get("fermo") or {}).get("vuoto") and not st.get("spento_vuoto"):
                st["spento_vuoto"] = now
                self.salva(st)
                print(f"[{self.NOME}] spento ({motivo}) e conto vuoto: da adesso nessuna richiesta a Binance")

    # ---- (c): la versione approvata dal proprietario su Firebase ----
    def _verifica_versione(self) -> Optional[str]:
        """Il controllo del minuto: None se il commit approvato dal proprietario c'è, Firebase ha risposto adesso, e sia il commit
        che il processo ha in memoria sia i file di adesso sono quelli di quel commit; altrimenti il motivo. Una lettura persa
        capita: si riprova una volta, subito, se la prima non ha aspettato oltre ``SECONDA_LETTURA_ENTRO_S`` (problema 75). Senza
        risposta vale solo il commit dell'ultima risposta vera, se è di non oltre ``APPROVAZIONE_SENZA_RISPOSTA_S`` fa (problema
        74), sempre con il confronto di git qui sotto; una risposta vera senza approvazione (revocata) vale subito."""
        ora = self.orologio()
        for _ in range(2):
            inizio = self.cronometro()
            commit, motivo, risposto = versione_approvata(self.fb)
            if risposto or self.cronometro() - inizio > SECONDA_LETTURA_ENTRO_S:
                break
        self._versione_muta = 0 if risposto else self._versione_muta + 1
        if risposto:
            self._letta_davvero = (commit, ora)
        elif self._letta_davvero and self._letta_davvero[0]:
            if 0 <= ora - self._letta_davvero[1] <= APPROVAZIONE_SENZA_RISPOSTA_S:
                commit, motivo = self._letta_davvero[0], None
            else:
                motivo = (f"Firebase non risponde e l'approvazione letta l'ultima volta è di oltre "
                          f"{APPROVAZIONE_SENZA_RISPOSTA_S // 60} minuti fa: la versione approvata dal proprietario non si legge")
        self._approvata = commit
        if motivo:
            return motivo
        return codice_approvato(radice=self.radice, commit=commit, caricati=file_caricati(self.radice),
                                in_memoria=self._versione.get("commit"))

    def _controlla_versione(self, now: float) -> None:
        """Ogni ``OGNI_CONTROLLO_CODICE_S`` (da spento ogni ``OGNI_CONTROLLO_CODICE_DA_SPENTO_S``, problema 75; all'accensione subito):
        rilegge la versione approvata e rifà il confronto; a ogni giro scrive `/conto_vero/versione` se è cambiata o se la
        scrittura di prima non è arrivata. Non solleva mai: le protezioni del giro non si fermano per questo."""
        spento = self.motivo_spento() is not None
        intervallo = OGNI_CONTROLLO_CODICE_DA_SPENTO_S if spento else OGNI_CONTROLLO_CODICE_S
        if not (0 <= now - self._codice_controllato < intervallo) or (self._controllato_da_spento and not spento):
            self._codice_controllato, self._controllato_da_spento = now, spento
            try:
                self._codice_ora = self._verifica_codice()
            except Exception as exc:  # noqa: BLE001
                self._codice_ora = f"controllo della versione non riuscito ({type(exc).__name__})"
        self._pubblica_versione(now)

    def _blocco_del_codice(self) -> Optional[str]:
        """Perché il codice ferma gli ordini nuovi, in una frase; None se è quello approvato."""
        if self._codice_all_avvio:
            return (f"il codice caricato all'avvio non è una versione che si possa approvare ({self._codice_all_avvio}): serve un "
                    f"riavvio")
        return self._codice_ora

    def _pubblica_versione(self, now: float) -> None:
        """`/conto_vero/versione` per la dashboard: il commit in esecuzione (HEAD all'avvio del processo: hash, data, titolo), se i
        file caricati sono uguali a quel commit (``pulito``), il commit approvato letto e se coincidono (altrimenti ``blocco``).
        Si scrive quando cambia e si riprova finché la scrittura non è confermata; non mentre Firebase non risponde (problema 75)."""
        if self._verifica_finta or self.fb is None or self._versione_muta:
            return
        blocco = self._blocco_del_codice()
        v = {"commit": self._versione.get("commit"), "data": self._versione.get("data"), "titolo": self._versione.get("titolo"),
             "pulito": self._codice_all_avvio is None, "motivo": self._codice_all_avvio, "approvata": self._approvata,
             "coincidono": blocco is None, "blocco": blocco}
        v = {k: x for k, x in v.items() if x is not None}
        if v == self._versione_scritta:
            return
        try:
            if self.fb.set_rtdb(f"/{self.NOME}/versione", {**v, "aggiornato": now}) is not False:
                self._versione_scritta = v
        except Exception:  # noqa: BLE001
            pass

    def _protezioni_da_spento(self, now: float, motivo: str) -> bool:
        """Problema 53: senza interruttore o con `DRY_RUN` vero niente ordini nuovi. Se il conto vero è stato acceso almeno una volta
        e Binance non ha ancora detto il conto vuoto, restano stop, pulsante e chiusure da fermo (solo ordini «solo riduzione»): vero.
        Mai acceso, o già vuoto: nessuna richiesta e nessuna chiave letta (falso)."""
        st = self.carica()
        if st.get("spento_vuoto") or not self._acceso_una_volta(st):
            if self._cliente is not None:
                self._cliente.blocco = motivo
            self._scrivi_spento(now, motivo, "conto vuoto: nessuna richiesta a Binance" if st.get("spento_vuoto") else None)
            return False
        chiave = f"protezioni|{motivo}"
        if self._spento_scritto != chiave:
            self._spento_scritto = chiave
            print(f"[{self.NOME}] spento ({motivo}): niente ordini nuovi; stop sul conto, pulsante e chiusure restano attivi finché "
                  f"Binance non dice il conto vuoto")
        return True

    def _scrivi_spento(self, now: float, motivo: str, aggiunta: Optional[str]) -> None:
        chiave = f"{motivo}|{aggiunta}"
        if self._spento_scritto == chiave:
            return
        self._spento_scritto = chiave
        testo = f"spento: {motivo}" + (f"; {aggiunta}" if aggiunta else "")
        print(f"[{self.NOME}] {testo}")
        self._scrivi("stato", {"stato": testo, "acceso": False, "aggiornato": now})
        st = self.carica()
        if st and st.get("blocco") != motivo:          # alla riaccensione si aspetta la decisione di G1 dopo
            st["blocco"] = motivo
            self.salva(st)

    def _acceso_su_firebase(self) -> Optional[dict]:
        """`/conto_vero/acceso_dal` o `/conto_vero/fermo` su Firebase (letti una volta per processo, aggiornati quando li scrive questo
        processo): il segno che il conto vero è già stato acceso, anche con il file di stato perso."""
        if self._firebase_letto is None:
            if self.fb is None:
                return None
            (risposto_a, a), (risposto_f, f) = (_letto_davvero(self.fb, f"/{self.NOME}/acceso_dal"),
                                                _letto_davvero(self.fb, f"/{self.NOME}/fermo"))
            trovato = (a if isinstance(a, dict) and a else None) or (f if isinstance(f, dict) and f else None)
            # problema 66: il «mai acceso» si tiene solo se Firebase ha risposto davvero a tutte e due le letture; altrimenti si
            # rilegge al giro dopo (un segno trovato vale anche dall'ultimo valore noto: è il lato prudente)
            if trovato or (risposto_a and risposto_f):
                self._firebase_letto = trovato or {}
            return trovato
        return self._firebase_letto or None

    def _acceso_una_volta(self, st: dict) -> bool:
        return bool(st.get("acceso_dal") or st.get("fermo") or self._acceso_su_firebase())

    def _mai_acceso_detto_da_firebase(self) -> bool:
        """Problema 66 (prova r1 della revisione dell'8 novembre 2026): vero solo quando Firebase ha risposto davvero sulla traccia
        dell'accensione. Con lo stato locale che non dice niente e Firebase muto non si sa se il conto era già acceso (e magari
        fermo): la prima accensione aspetta la risposta."""
        self._acceso_su_firebase()
        return self._firebase_letto is not None

    def _scrivi(self, ramo: str, valore) -> None:
        if ramo in ("acceso_dal", "fermo") and isinstance(valore, dict) and valore:
            self._firebase_letto = valore
        if ramo == "stato" and isinstance(valore, dict) and valore.get("stato") == "acceso" and self._blocco_ora:
            valore = {**valore, "stato": f"solo protezioni, niente ordini nuovi: {self._blocco_ora}"}
        if self.fb is None:                            # come il demo (`DemoG1._scrivi`), più l'esito del fermo
            return
        arrivata = self.fb.set_rtdb(f"/{self.NOME}/{ramo}", valore) is not False
        if ramo == "fermo":                            # problema 76: si riscrive a ogni giro finché non arriva
            self._fermo_da_riscrivere = not arrivata

    # ---- lo stato perso (57) e il valore del conto (58), a ogni giro prima delle protezioni ----
    def conto_ridotto(self, c: ClienteVero, st: dict, now: float) -> dict:
        st = self._stato_perso(c, st, now)
        st = super().conto_ridotto(c, st, now)
        self._aggiorna_redditi(c, st, now)
        return st

    def _stato_perso(self, c: ClienteVero, st: dict, now: float) -> dict:
        """Problema 57: il file di stato manca (o non si legge) ma il conto vero era già stato acceso (Firebase): il conto parte fermo
        (chiusure fino al conto vuoto), la richiesta di «riparti» che c'era non vale, serve un «riparti» nuovo in due passi dalla
        dashboard."""
        if st.get("acceso_dal") or st.get("fermo"):
            return st
        illeggibile = self.file_stato.exists() and not st
        prima = self._acceso_su_firebase()
        if not (illeggibile or prima):
            return st
        motivo = (f"stato del conto vero perso ({self.file_stato.name} {'illeggibile' if illeggibile else 'mancante'}) dopo "
                  f"un'accensione: fermo, chiusure fino al conto vuoto, poi «Riparti» in due passi dalla dashboard")
        st = {"fermo": {"motivo": motivo, "ora": now, "equity": None, "chiuse": 0, "errori": [], "tentativi": 0,
                        "ultimo_controllo": 0.0, "riparti_pulito": False}, "stato_perso": now}
        if prima and prima.get("ora") and "compra_alla_decisione_di_g1_dopo_il" in prima:
            st["acceso_dal"] = float(prima["ora"])
        st["fermo"]["riparti_pulito"] = self._pulisci_riparti(st)   # la richiesta e la conferma che c'erano non contano
        try:
            st["eseguito_chiudi"] = self.file_chiudi.read_text(encoding="utf-8").strip() if self.file_chiudi.exists() else ""
        except Exception:  # noqa: BLE001
            pass
        self._scrivi("fermo", st["fermo"])
        self._allarme(st, now, "stato_perso", motivo)
        self.salva(st)
        print(f"[{self.NOME}] ALLARME: {motivo}")
        return st

    def _aggiorna_redditi(self, c: ClienteVero, st: dict, now: float) -> None:
        """Problemi 58 e 64: i redditi del conto dalla partenza della fase, letti ogni minuto da `/fapi/v1/income` fino a
        ``RITARDO_REDDITI_S`` fa, ripartendo ``SOVRAPPOSIZIONE_REDDITI_S`` prima della fine della lettura di prima; una riga si conta
        una volta sola (tipo e tranId). Contano solo `REDDITI_DEL_CONTO` in USDT; il resto va in `/conto_vero/movimenti_non_contati`.
        Un errore di lettura tiene i redditi di prima (le protezioni non si fermano per questo) e dopo
        ``ERRORI_REDDITI_PRIMA_DELL_ALLARME`` errori di fila scrive l'allarme `redditi`; i limiti di Binance risalgono."""
        cr = st.get("conto_ridotto")
        if not cr:
            self._capitale_cr, self._redditi = None, 0.0
            return
        r = st.get("redditi")
        if not isinstance(r, dict) or r.get("fase") != cr.get("dal") or "inizio_ms" not in r:
            inizio = int(float(cr.get("dal") or now) * 1000)
            r = {"fase": cr.get("dal"), "inizio_ms": inizio, "letto_fino_ms": inizio, "somma": 0.0, "visti": {}, "non_contati": {}}
            st["redditi"] = r
        self._capitale_cr, self._redditi = float(cr["capitale"]), float(r.get("somma") or 0.0)
        if now - self._redditi_letti < demo.OGNI_CONTROLLO_STOP_S and now >= self._redditi_letti:
            return
        fine = int((now - RITARDO_REDDITI_S) * 1000)
        da = max(int(r["inizio_ms"]), int(r["letto_fino_ms"]) - SOVRAPPOSIZIONE_REDDITI_S * 1000)
        if fine <= da:
            return
        self._redditi_letti = now
        try:
            visti, inizio, cambiati = r.setdefault("visti", {}), da, False
            for _ in range(PAGINE_REDDITI_MAX):
                righe = c.chiedi("GET", "/fapi/v1/income", {"startTime": inizio, "endTime": fine, "limit": 1000},
                                 firmata=True) or []
                for x in righe:
                    tipo, valuta, v = x.get("incomeType") or "?", x.get("asset") or "USDT", float(x.get("income") or 0)
                    ms = int(x.get("time") or 0)
                    chiave = (f"{tipo}:{x['tranId']}" if x.get("tranId") is not None
                              else f"{tipo}:{ms}:{x.get('symbol')}:{x.get('income')}")
                    if chiave in visti or ms <= int(r["inizio_ms"]):   # già contata, o della fase di prima
                        continue
                    visti[chiave] = ms
                    if tipo in REDDITI_DEL_CONTO and valuta == "USDT":
                        r["somma"] = round(float(r.get("somma") or 0.0) + v, 8)
                    else:
                        nc = r.setdefault("non_contati", {})
                        nc[f"{tipo} {valuta}"] = round(float(nc.get(f"{tipo} {valuta}") or 0.0) + v, 8)
                        cambiati = True
                if len(righe) < 1000:
                    break
                ultima = max(int(x.get("time") or 0) for x in righe)
                if ultima <= inizio:
                    break
                inizio = ultima                        # la stessa ora si rilegge: i doppioni li toglie `visti`
            r["letto_fino_ms"] = fine
            r["visti"] = {k: ms for k, ms in visti.items() if ms >= fine - SOVRAPPOSIZIONE_REDDITI_S * 1000}
            r["errori"] = 0
            self._redditi = float(r["somma"])
            self._allarme(st, now, "redditi", None)
            if cambiati:
                self._scrivi("movimenti_non_contati", {"ora": now, "movimenti": r["non_contati"]})
                print(f"[{self.NOME}] movimenti del conto non contati nel valore del bot: {r['non_contati']}")
        except (RuntimeError, requests.RequestException) as exc:
            r["errori"] = int(r.get("errori") or 0) + 1
            testo_errore = demo.senza_firma(exc)[:150]
            print(f"[{self.NOME}] redditi del conto non letti, resta il valore di prima: {testo_errore}")
            if r["errori"] >= ERRORI_REDDITI_PRIMA_DELL_ALLARME:
                self._allarme(st, now, "redditi", f"i redditi del conto non si leggono da {r['errori']} letture: il valore del "
                                                  f"bot non conta le entrate e le uscite più recenti ({testo_errore})")

    def _livello_di_stop(self, st: dict) -> float:
        """Problema 69: prima della prima accensione il conto non ha posizioni del bot; lo stop non chiude quelle del proprietario (il
        59 non le tocca con il ribilancio, lo stop nemmeno). Il pulsante resta: è un comando suo."""
        if not st.get("acceso_dal"):
            return 0.0
        return super()._livello_di_stop(st)

    def _da_fermo(self, c: ClienteVero, st: dict, now: float) -> dict:
        self._conferma_attesa = codice_riparti(st.get("fermo"))   # la conferma che vale per QUESTO fermo, e solo in questo giro
        try:
            st = super()._da_fermo(c, st, now)
        finally:
            self._conferma_attesa = None
        if not st.get("fermo"):                        # problema 68: il «riparti» accettato spegne l'allarme dello stato perso
            st.pop("stato_perso", None)
            self._allarme(st, now, "stato_perso", None)
        return st

    # ---- «riparti» in due passi, solo dalla dashboard (decisione del proprietario del 12 novembre 2026) ----
    def _comando_file(self, f: Path, st: dict, chiave: str) -> bool:
        if chiave == "eseguito_riparti":               # nessun file fa ripartire il conto vero: lo potrebbe scrivere una sessione
            return False
        return super()._comando_file(f, st, chiave)

    def _comando(self, percorso: Optional[str]) -> bool:
        if percorso == self.COMANDO_RIPARTI:
            return self._riparti_confermato()
        return super()._comando(percorso)

    def _riparti_confermato(self) -> bool:
        """Vero solo con la richiesta (`/commands/conto_vero_riparti` vero) E la conferma (`/commands/conto_vero_riparti_conferma`
        uguale al testo esatto di questo fermo, `codice_riparti`). Li scrive solo il proprietario dalla dashboard, e le regole di
        Firebase accettano la conferma solo con la richiesta già scritta. La richiesta senza conferma, o con la conferma di un
        altro fermo, non fa niente e resta dov'è (la dashboard mostra il secondo passo)."""
        atteso = self._conferma_attesa
        if self.fb is None or not atteso:
            return False
        try:
            chiesto, conferma = self.fb.get_rtdb(self.COMANDO_RIPARTI), self.fb.get_rtdb(COMANDO_RIPARTI_CONFERMA)
        except Exception:  # noqa: BLE001
            return False
        return chiesto is True and isinstance(conferma, str) and conferma == atteso

    def _riparti(self, st: dict) -> bool:
        """Come il demo (la richiesta si consuma con la scrittura del falso confermata, altrimenti niente «riparti»); in più si
        toglie la conferma: vale una volta sola."""
        consumato = super()._riparti(st)
        if consumato:
            try:
                self.fb.set_rtdb(COMANDO_RIPARTI_CONFERMA, None)
            except Exception:  # noqa: BLE001
                pass
        return consumato

    def _pulisci_riparti(self, st: dict, solo_firebase: bool = False) -> bool:
        """All'entrata nel fermo la richiesta e la conferma che c'erano non valgono: si tolgono da Firebase. Vero solo se le due
        scritture sono confermate; finché non lo sono il «riparti» non si accetta e si riprova a ogni giro (`_da_fermo` del demo).
        Nessun file."""
        if self.fb is None:
            return True
        try:
            return (self.fb.set_rtdb(self.COMANDO_RIPARTI, False) is not False
                    and self.fb.set_rtdb(COMANDO_RIPARTI_CONFERMA, None) is not False)
        except Exception:  # noqa: BLE001
            return False

    def _valori(self, margine: float, saldo: float) -> tuple:
        """Problema 58: con una fase in corso il valore è il capitale più i redditi più gli utili non realizzati (margine − saldo),
        e il saldo è il capitale più i redditi: versamenti e prelievi non contano. Prima della prima fase, il conto intero (senza
        ordini possibili: il ribilancio vuole il capitale fissato)."""
        if self._capitale_cr is None:
            return super()._valori(margine, saldo)
        base = self._capitale_cr + self._redditi
        return base + (margine - saldo), base

    def parti_da_zero(self, c: ClienteVero, st: dict, now: float) -> dict:
        """Come il demo; i redditi della fase nuova si contano da dopo le chiusure della fase di prima."""
        prima = st.get("conto_ridotto")
        st = super().parti_da_zero(c, st, now)
        cr = st.get("conto_ridotto")
        if cr is not None and cr is not prima:
            # problema 65: l'ora vera dopo le chiusure (e l'attesa che le segue), nell'ora di Binance: le righe delle chiusure della
            # fase di prima hanno un'ora più bassa e restano fuori
            inizio = int(self.orologio() * 1000) + int(getattr(c, "scarto_ora_ms", 0) or 0)
            st["redditi"] = {"fase": cr["dal"], "inizio_ms": inizio, "letto_fino_ms": inizio, "somma": 0.0, "visti": {},
                             "non_contati": {}}
            self._capitale_cr, self._redditi = float(cr["capitale"]), 0.0
            self.salva(st)
        return st

    # ---- (c) e (d): niente ordini nuovi, le protezioni restano ----
    def motivo_niente_ordini(self, c: ClienteVero, st: dict, now: float) -> Optional[str]:
        ragioni = []
        self._controlla_versione(now)                  # già fatto in cima al giro: qui solo se è passato un minuto
        if self._codice_all_avvio:
            ragioni.append(self._blocco_del_codice())
        if self._codice_ora and self._codice_ora != self._codice_all_avvio:
            ragioni.append(self._codice_ora)
        self._allarme(st, now, "versione_approvata", None if self._versione_muta < LETTURE_VERSIONE_PRIMA_DELL_ALLARME else (
            f"Firebase non risponde da almeno {LETTURE_VERSIONE_PRIMA_DELL_ALLARME} controlli di fila: la versione approvata dal "
            f"proprietario non si legge; vale l'ultima letta fino a {APPROVAZIONE_SENZA_RISPOSTA_S // 60} minuti dalla lettura, poi "
            f"niente ordini nuovi finché non risponde; stop sul conto, pulsante a file e chiusure restano attivi"))
        if not st.get("acceso_dal") and not self._mai_acceso_detto_da_firebase():
            ragioni.append("Firebase non risponde e lo stato locale non dice se il conto vero è già stato acceso: niente prima "
                           "accensione finché non risponde")
        voluto = self.capitale_voluto()
        cr = st.get("conto_ridotto")
        if self._valore_vero is None:
            self._conto(c)                             # il saldo vero, prima di qualunque ordine
        if voluto is None:
            ragioni.append(self.capitale_errato or f"manca il capitale (ops/{self.file_capitale.name}, un numero fino a "
                                                   f"{self.CAPITALE_MASSIMO:g} USDT)")
        elif voluto > float(self._valore_vero) and not (cr and float(cr.get("capitale") or 0) == voluto):
            ragioni.append(f"capitale {voluto:g} USDT oltre il saldo vero del conto ({float(self._valore_vero):,.2f} USDT)")
        if cr:
            cap = float(cr.get("capitale") or 0)
            valore, base = self._valori(float(self._valore_vero), float(self._saldo_vero))
            if self._saldo_sotto(st, now, base):
                ragioni.append(f"il saldo vero del conto ({float(self._saldo_vero):,.2f} USDT) è sotto il valore del bot "
                               f"({base:,.2f}) in {self.LETTURE_SALDO_SOTTO} letture di fila: un prelievo? serve un capitale nuovo")
            if not 0 < cap <= self.CAPITALE_MASSIMO:
                ragioni.append(f"capitale in corso {cap:g} USDT fuori dal tetto di {self.CAPITALE_MASSIMO:g}")
            elif valore > self.VALORE_MASSIMO_PER_ORDINI:
                ragioni.append(f"il conto del bot vale {valore:,.2f} USDT, oltre {self.VALORE_MASSIMO_PER_ORDINI:g}: serve un "
                               f"capitale nuovo")
        if st.get("acceso_dal"):
            self._allarme(st, now, "conto_non_vuoto", None)
        elif not ragioni:                              # problema 59: alla prima accensione il conto dei future dev'essere vuoto
            _, _, posizioni = self._conto(c)
            aperti = sorted({o["symbol"] for o in c.chiedi("GET", "/fapi/v1/openOrders", firmata=True) or []})
            non_vuoto = None
            if posizioni or aperti:
                non_vuoto = (f"il conto non è vuoto alla prima accensione (posizioni: {', '.join(sorted(posizioni)) or 'nessuna'}; "
                             f"ordini aperti: {', '.join(aperti) or 'nessuno'}): niente ordini finché il proprietario non lo svuota")
                ragioni.append(non_vuoto)
            self._allarme(st, now, "conto_non_vuoto", non_vuoto)   # con altri motivi resta com'era all'ultimo controllo
        return "; ".join(ragioni) or None

    def _saldo_sotto(self, st: dict, now: float, base: float) -> bool:
        """Problema 64: vero se il saldo vero è sotto il valore del bot di oltre la tolleranza in ``LETTURE_SALDO_SOTTO`` letture di fila,
        a un minuto l'una dall'altra (il saldo si rilegge ogni minuto); una lettura nella tolleranza azzera il conto."""
        tolleranza = max(self.TOLLERANZA_SALDO_MINIMA, self.TOLLERANZA_SALDO * base)
        if float(self._saldo_vero) >= base - tolleranza:
            st.pop("saldo_sotto", None)
            return False
        sotto = st.setdefault("saldo_sotto", {"dal": now, "volte": 0, "ultima": 0.0})
        if now - float(sotto["ultima"]) >= demo.OGNI_CONTROLLO_STOP_S or now < float(sotto["ultima"]):
            sotto["volte"], sotto["ultima"] = int(sotto["volte"]) + 1, now
        return int(sotto["volte"]) >= self.LETTURE_SALDO_SOTTO

    def _ordini_nuovi_ammessi(self, c: ClienteVero, st: dict, now: float) -> bool:
        st.setdefault("entrate_chiuse_fino", int(now // 86400) - 1)   # funding e commissioni dal primo giorno di questo conto
        if self._motivo_spento_ora:
            motivo = self._motivo_spento_ora
            self._vuoto_da_spento(c, st, now)
        else:
            st.pop("spento_vuoto", None)
            motivo = self.motivo_niente_ordini(c, st, now)
        self._blocco_ora = motivo
        c.blocco = motivo
        self._allarme(st, now, "ordini_vietati", motivo and (
            f"niente ordini nuovi: {motivo}; stop sul conto, pulsante e chiusure restano attivi"))
        if motivo:
            if st.get("blocco") != motivo:
                print(f"[{self.NOME}] niente ordini nuovi: {motivo}")
            st["blocco"] = motivo
            if st.get("ordini") and now >= float(st["ordini"]["piazzati"]) + demo.VALIDITA_LIMITE_S:
                self._ordini_scaduti_senza_mercato(c, st, now)
            return False
        if "blocco" in st or not st.get("acceso_dal"):
            # l'accensione: si compra solo alla prima decisione di G1 dopo (la mezzanotte UTC), mai a metà giornata
            st.pop("blocco", None)
            giorno = self._giorno_g1(now)
            st["ultimo_giorno"] = max(int(st.get("ultimo_giorno") or 0), giorno)
            st["acceso_dal"] = now
            dopo = time.strftime("%Y-%m-%d", time.gmtime(giorno * 86400))
            self._scrivi("acceso_dal", {"ora": now, "compra_alla_decisione_di_g1_dopo_il": dopo})
            print(f"[{self.NOME}] acceso: ordini solo dalla prima decisione di G1 dopo quella del {dopo} (la mezzanotte UTC)")
        return True

    def _vuoto_da_spento(self, c: ClienteVero, st: dict, now: float) -> None:
        """Senza interruttore o con `DRY_RUN` vero, ogni minuto: se Binance dice il conto vuoto (niente posizioni, niente ordini
        aperti), da adesso nessuna richiesta (problema 53)."""
        if now - float(st.get("vuoto_controllato") or 0) < demo.OGNI_CONTROLLO_STOP_S:
            return
        st["vuoto_controllato"] = now
        _, _, posizioni = self._conto(c)
        if posizioni or c.chiedi("GET", "/fapi/v1/openOrders", firmata=True):
            return
        st.pop("ordini", None)
        st["spento_vuoto"] = now                       # lo stato lo scrive il giro dopo, senza richieste
        print(f"[{self.NOME}] spento ({self._motivo_spento_ora}) e conto vuoto: da adesso nessuna richiesta a Binance")

    def _ordini_scaduti_senza_mercato(self, c: ClienteVero, st: dict, now: float) -> None:
        """Problema 56: con un blocco gli ordini limite di un ribilancio in corso non si annullano subito: vivono la loro ora, come
        in G1; dopo, quelli non eseguiti si annullano e il resto a mercato non parte (sarebbe un ordine nuovo)."""
        ordini = st["ordini"]
        simboli = sorted({o.get("simbolo") for o in ordini.get("lista") or [] if o.get("simbolo")})
        for s in simboli:
            c.chiedi("DELETE", "/fapi/v1/allOpenOrders", {"symbol": s}, firmata=True)
        self._scrivi(f"ribilanciamenti/{ordini.get('chiave') or 'in_corso'}/scaduti_senza_mercato",
                     {"ora": now, "monete": simboli, "motivo": st.get("blocco")})
        st.pop("ordini")
        self._allarme(st, now, "ordini", None)
        print(f"[{self.NOME}] ordini limite scaduti annullati, niente resto a mercato ({len(simboli)} monete): {st.get('blocco')}")

    # ---- gli ordini: solo con il capitale fissato, solo con i filtri veri ----
    def ribilancia(self, c: ClienteVero, st: dict, pesi: dict, giorno: int, now: float, solo: Optional[set] = None) -> dict:
        if solo is not None:
            raise RuntimeError("niente eventi sul conto vero")
        cap = float((st.get("conto_ridotto") or {}).get("capitale") or 0)
        if not 0 < cap <= self.CAPITALE_MASSIMO:
            raise RuntimeError(f"conto vero senza un capitale fissato fino a {self.CAPITALE_MASSIMO:g} USDT: niente ordini")
        if getattr(c, "blocco", None):
            raise RuntimeError(f"niente ordini nuovi: {c.blocco}")
        return super().ribilancia(c, st, pesi, giorno, now, solo)

    def _filtri_degli_ordini(self, info: dict, st: dict, now: float, ribilancio: bool = False) -> dict:
        """I filtri del vero exchangeInfo di fapi.binance.com, riletto a ogni ribilancio e a ogni resto a mercato; mai la copia fissa
        `filtri_conto_vero.json` del demo."""
        f = demo.filtri(info)
        if not f:
            raise RuntimeError("exchangeInfo del conto vero senza filtri leggibili: niente ordini")
        if ribilancio:
            st["filtri_letti"] = now
            self._scrivi("filtri", {"letti": now, "monete": len(f), "da": HOST_VERO})
        return f

    def _ambiente(self, now: float) -> dict:
        amb = super()._ambiente(now)
        amb.pop("filtri_del_conto_vero_del", None)
        amb.update({"filtri": f"exchangeInfo di {HOST_VERO} a ogni ribilancio",
                    "versione_approvata": f"il commit scritto dal proprietario in {COMANDO_VERSIONE}",
                    "commit_in_esecuzione": self._versione.get("commit"),
                    "codice_all_avvio": self._codice_all_avvio or "uguale al commit in esecuzione",
                    "valore_massimo_per_ordini": self.VALORE_MASSIMO_PER_ORDINI,
                    "valore": "capitale più redditi del conto (versamenti e prelievi esclusi)",
                    "riparti": "in due passi dalla dashboard (richiesta e conferma), nessun file"})
        return amb


_ULTIMO_ERRORE_DI_CREAZIONE = [None]                # l'ultimo errore scritto nel log
_ERRORE_DI_CREAZIONE_SCRITTO = [None]               # l'ultimo errore arrivato davvero su Firebase
ALLARME_DI_CREAZIONE = f"/{ContoVeroG1.NOME}/allarmi/creazione"


def _allarme_di_creazione(fb, valore) -> bool:
    """Scrive (o toglie, con None) l'allarme della creazione su Firebase; vero solo se la scrittura è confermata. Non solleva mai."""
    try:
        return fb is not None and fb.set_rtdb(ALLARME_DI_CREAZIONE, valore) is not False
    except Exception:  # noqa: BLE001
        return False


def crea_conto_vero(fb, classe=None) -> Optional["ContoVeroG1"]:
    """Crea il conto vero senza poter fermare il bot (revisione dell'8 novembre 2026, problema 71): un errore nel costruttore non
    deve impedire l'avvio del demo e dei paper (la regola del proprietario dell'8 novembre: nessuna strategia in corso si perde).
    Torna None e lo scrive nel log (una volta per errore diverso) e su Firebase, in `/conto_vero/allarmi/creazione` (problema 73:
    la dashboard e lo stato lo mostrano fra gli allarmi del conto vero; si riscrive finché la scrittura non è confermata e si
    toglie alla prima creazione riuscita); il bot riprova a ogni giro."""
    try:
        conto = (classe or ContoVeroG1)(fb)
    except Exception as exc:  # noqa: BLE001
        testo = demo.senza_firma(f"{type(exc).__name__}: {exc}")[:300]
        if testo != _ULTIMO_ERRORE_DI_CREAZIONE[0]:
            _ULTIMO_ERRORE_DI_CREAZIONE[0] = testo
            _ERRORE_DI_CREAZIONE_SCRITTO[0] = None
            print(f"[conto_vero] ERRORE nella creazione, il conto vero non gira (si riprova a ogni giro): {testo}")
        if _ERRORE_DI_CREAZIONE_SCRITTO[0] != testo and _allarme_di_creazione(fb, {
                "ora": time.time(), "testo": f"il conto vero non è stato creato e non gira (demo e paper continuano; si riprova a "
                                             f"ogni giro): {testo}"}):
            _ERRORE_DI_CREAZIONE_SCRITTO[0] = testo
        return None
    _ULTIMO_ERRORE_DI_CREAZIONE[0] = None
    _ERRORE_DI_CREAZIONE_SCRITTO[0] = None
    _allarme_di_creazione(fb, None)                    # anche quello lasciato da un processo di prima
    return conto
