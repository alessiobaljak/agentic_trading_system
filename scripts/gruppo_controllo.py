"""IL GRUPPO DI CONTROLLO DEL FUORI CAMPIONE: la RACCOLTA (30 set 2026).

PERCHE' (backlog K3, docs/revisione_sospese_30set.md sezione «C»). La misura
H5 dice se le validate guadagnano DOPO essere state scelte, non se guadagnano
PERCHE' il gate le ha scelte. Per saperlo servono, negli stessi giorni, coppie
che il gate NON ha scelto. Fra ~14 giorni il motore rigiochera', sui giorni
successivi alla data di raccolta, quattro gruppi: validate, 2 conferme,
1 conferma, bocciate. Se le bocciate rendono come le validate, il gate non
seleziona. Questo file fa SOLO la raccolta; l'analisi e' un altro lavoro.

Due raccolte, a ogni giro della discovery (giro a 15 minuti e passata a 1 ora):

  * BOCCIATE: un campione CASUALE di CAMPIONE (50) candidate bocciate con
    almeno MIN_TRADE (30) trade nelle finestre OOS. Casuale davvero: non i
    quasi-passaggi, non le migliori. Il seme si dichiara e si salva in ogni
    riga. La spec si salva INTERA, perche' le spec bocciate non finiscono da
    nessun'altra parte (`persist_specs` salva solo quelle passate).
    Si escludono: le coppie gia' nel registro con almeno una conferma (sono
    nei gruppi della foto), le gia' validate (idem) e le varianti troncate dai
    referti (giudicate su dati vecchi, non su quelli di oggi).
  * FOTO DELLE CONFERME: una volta al giorno (giorno italiano,
    `bot/core/tempo.giorno_locale`), al primo giro PARTITO nel giorno, lo stato
    di ogni coppia del registro: pass_count, validata, declassata, istante. Il
    gruppo di una coppia e' quello della foto del giorno in cui ci entra: una
    coppia che il 1 ott ha 1 conferma resta nel gruppo «1 conferma» anche se
    poi conferma ancora (cosi' i trade buoni non cambiano gruppo).
    30 set 2026, revisione: il giorno dei file, il controllo «gia' fatta oggi»
    e l'istante delle righe sono tutti quelli in cui il giro ha letto il
    registro (il ponte passa `now=letto_at`). Prima il nome del file veniva
    dalla FINE del giro: un giro a cavallo della mezzanotte italiana scriveva
    nella foto del giorno dopo il registro della sera prima, e le foto vere di
    quel giorno venivano saltate.

REGOLE (non si negoziano):
  * FAIL-OPEN: un errore qui non fa fallire ne' rallentare il giro. Al massimo
    una riga di log «[controllo-gruppi] ...». Anche un numero scritto male
    nell'ambiente: si usa il default (`_env_num`).
  * NON CAMBIA NIENTE del giro: verdetti, semi della ricerca e ordine delle
    candidate restano identici. Il campione usa un generatore casuale SUO
    (`random.Random(seme)`), il seme nasce da `secrets` (che non tocca lo
    stato di `random`), e le candidate idonee si ordinano per chiave prima di
    estrarre: il campione dipende solo da (seme, insieme delle idonee), e
    l'insieme delle idonee si salva (formato 2, qui sotto).
  * FILE LOCALI sulla VPS, come il dataset del selettore (`data/selettore/`):
    niente quota Firestore, niente limite di 1 MiB per documento.
    `data/gruppo_controllo/AAAA-MM-GG_bocciate.jsonl` (append, una riga per
    candidata) e `data/gruppo_controllo/AAAA-MM-GG_conferme.jsonl` (una riga
    per coppia, scritto una volta al giorno). In .gitignore.
  * SPAZIO: file piu' vecchi di RITENZIONE_GIORNI (120) cancellati; se la
    cartella supera TETTO_MB (300 MB) non si scrive piu' e lo si dice.
    Byte al giorno (30 set 2026: righe MISURATE su spec generate e su un
    registro finto, il numero di giri e di coppie e' quello di oggi): ~0,96 KB
    per bocciata x 50 x fino a 16 giri al giorno (8 a 15 minuti + 8 passate a
    1 ora, timer ogni 3 ore) = ~0,77 MB; foto ~0,49 KB x 1.532 coppie (ops
    0363) = ~0,74 MB. Totale ~1,1-1,5 MB al giorno, ~180 MB al massimo in 120
    giorni: sotto il tetto.

FORMATO 2 (30 set 2026, revisione della raccolta). Cosa si aggiunge e perche':
  * una riga «tipo: giro» in testa al blocco di ogni giro (nel file delle
    bocciate) e in testa alla foto: versione del codice (commit letto
    all'avvio della discovery), impostazioni del motore e del gate con cui le
    candidate sono state giudicate (scale-out, costi, cooldown, ingresso alla
    candela dopo, soglie GATE_*, MIN_PASSES, fonte delle candele), seme,
    popolazione e impronta delle idonee. Ogni riga porta `giro`, l'id della sua
    riga di giro (`con_giro` le rimette insieme). Una riga sola per giro invece
    di ~0,4 KB in ogni riga: ~1 KB al giro contro ~0,9 MB al giorno. Le righe in
    formato 1 (dal 30 set al primo giro col formato 2) non hanno questi campi:
    si ricostruiscono solo in modo approssimato, dalla data e dal git log;
  * l'ELENCO DELLE IDONEE di ogni giro (le chiavi fra cui si e' estratto),
    compresso a parte: `AAAA-MM-GG_idonee_<giro>.txt.gz`, una chiave per riga,
    ordinate. Col seme salvato l'estrazione si rifa' e si verifica:
    `random.Random(seme).sample(chiavi, min(campione, len(chiavi)))`, e
    `idonee_sha256` e' l'impronta del testo non compresso. Ritenzione breve,
    RITENZIONE_IDONEE_GIORNI (21: fino al rigioco dopo il 7 ott e un margine).
    Spazio STIMATO su chiavi finte della forma vera (~21 caratteri): ~130 KB
    per un giro con ~24.000 idonee (quante sono davvero lo dice la riga di log
    «su M idonee»), al piu' ~2 MB al giorno, ~45 MB in 21 giorni;
  * nella foto, per le generate, `spec_nota` (la spec c'era nel documento delle
    spec quando la foto e' stata scattata) e, una volta al giorno insieme alla
    foto, `AAAA-MM-GG_spec.jsonl` con la spec di ogni generata del registro
    (~155 KiB al giorno, STIMATO da ops 0363): se nei 14 giorni qualcuno azzera
    il documento delle spec, le foto si rigiocano lo stesso. Per le coppie base
    la foto salva i parametri interi (`params`, da `last_params`): il registro
    le puo' potare. Una generata senza spec ha `timeframe` None, non il
    timeframe del bot;
  * la foto e i file si scrivono a parte (col pid nel nome), con fsync, e la
    foto si crea in modo esclusivo (`os.link`): due giri insieme non la scrivono
    due volte, e un file vuoto lasciato da un crash non conta come «fatta».
  Totale col formato 2 (STIMATO): ~1,7 MB al giorno di .jsonl (~200 MB in 120
  giorni) piu' al piu' ~45 MB di idonee: sotto il tetto di 300 MB.

REGOLE DELL'ANALISI (30 set 2026, scritte PRIMA di vedere i numeri; il rigioco
e l'analisi sono un altro lavoro, dopo il 7 ott):
  1. Sempre separate per `interval`: le validate a 15 minuti si confrontano
     solo con le bocciate a 15 minuti; quelle a 1 ora in un confronto a parte.
     La quota e' fissa (CAMPIONE a ogni giro) anche nella passata a 1 ora, che
     valuta molte meno candidate: senza separare, circa meta' delle bocciate
     del giorno sarebbero strategie a 1 ora (se li' le idonee sono almeno 50;
     la riga di log «su M idonee [1h]» lo dira').
  2. Dentro un intervallo, ogni bocciata pesa `popolazione / righe del giro`
     (il giro e' la sua riga «tipo: giro», o `seme` + `interval` +
     `valutata_at` per il formato 1): un giro completo, con molte piu' idonee,
     non pesa quanto un giro urgente.
  3. Una chiave (`key`) estratta in piu' giri conta una volta sola (la prima
     estrazione), o si tratta come misura ripetuta.
  4. Fuori le righe con `run_end` diverso dal giorno della raccolta (passate
     con `--end` nel passato, per esempio `scripts/backfill_passes.sh`).
  5. Il gruppo di una coppia si assegna per `istante`/`giorno` della riga, mai
     per nome del file; per i file scritti prima del formato 2 si tolgono i
     doppioni (giorno, key).
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import random
import secrets
import subprocess
import time

from bot.core.tempo import giorno_locale


def _log(testo: str) -> None:
    print(f"[controllo-gruppi] {testo}")


def _env_num(nome: str, default, tipo):
    """Un numero dall'ambiente, FAIL-OPEN (30 set 2026, revisione): un valore
    scritto male nel .env non deve far fallire l'import di questo modulo, e con
    lui quello della discovery (giro a 15 minuti e passata a 1 ora). Si usa il
    default e lo si dice con una riga di log."""
    valore = os.getenv(nome)
    if valore is None or not str(valore).strip():
        return default
    try:
        return tipo(valore)
    except (TypeError, ValueError):
        _log(f"valore ignorato per {nome}: {valore!r}, uso {default}")
        return default


#: la cartella dei file, relativa alla cartella del servizio (come
#: `data/selettore`). Un test la sposta con l'ambiente.
CONTROLLO_DIR = os.getenv("CONTROLLO_GRUPPI_DIR", "data/gruppo_controllo")
#: interruttore: "false" spegne la raccolta (il giro resta identico)
ATTIVO = os.getenv("CONTROLLO_GRUPPI", "true").lower() != "false"
#: quante bocciate per giro
CAMPIONE = _env_num("CONTROLLO_GRUPPI_CAMPIONE", 50, int)
#: trade OOS minimi perche' una bocciata sia rigiocabile con senso
MIN_TRADE = _env_num("CONTROLLO_GRUPPI_MIN_TRADE", 30, int)
#: rotazione: file piu' vecchi di tanti giorni si cancellano
RITENZIONE_GIORNI = _env_num("CONTROLLO_GRUPPI_RITENZIONE_GIORNI", 120.0, float)
#: rotazione degli elenchi delle idonee (.gz), piu' pesanti e utili solo fino
#: al rigioco (30 set 2026)
RITENZIONE_IDONEE_GIORNI = _env_num("CONTROLLO_GRUPPI_RITENZIONE_IDONEE_GIORNI", 21.0, float)
#: tetto dichiarato di spazio: oltre, non si scrive piu'
TETTO_MB = _env_num("CONTROLLO_GRUPPI_TETTO_MB", 300.0, float)

#: la versione del formato delle righe: chi rilegge controlla questa.
#: 2 dal 30 set 2026: riga «tipo: giro», campo `giro` in ogni riga, elenco
#: delle idonee, `spec_nota`/`params` nella foto, file delle spec del giorno.
FORMATO = 2

_RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_VERSIONE: dict = {}


def versione_codice() -> str | None:
    """Il commit del codice, letto UNA volta per processo (alla prima chiamata:
    la discovery la fa all'avvio, perche' l'agente ops puo' far avanzare il
    ramo mentre il giro gira). `git rev-parse HEAD`; FAIL-OPEN: None se git
    manca o non risponde entro 5 secondi. Non tocca `random`."""
    if "commit" not in _VERSIONE:
        commit = None
        try:
            out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=_RADICE,
                                 capture_output=True, text=True, timeout=5)
            testo = (out.stdout or "").strip()
            if out.returncode == 0 and len(testo) == 40:
                commit = testo
        except Exception:  # noqa: BLE001
            commit = None
        _VERSIONE["commit"] = commit
    return _VERSIONE["commit"]


# --------------------------------------------------------------------------- #
# Nel worker: la voce leggera di una bocciata idonea                           #
# --------------------------------------------------------------------------- #
def voce_idonea(sym: str, spec: dict, r: dict, gia_validate=(),
                config_globale: dict | None = None) -> dict | None:
    """La voce LEGGERA di una candidata bocciata idonea al campione, o None.

    Gira nel worker per ogni valutazione: deve costare quanto un contatore. La
    spec NON c'e' (la si riprende nel processo principale dall'id, per non
    trascinare migliaia di spec fra i processi). Idonea = bocciata, con almeno
    MIN_TRADE trade OOS, non gia' validata, non variante troncata dai referti.
    La configurazione d'uscita e' quella con cui e' stata giudicata: la
    globale se e' caduta al passo 1, quella scelta dal gate se e' caduta
    dopo (passo 3 o holdout). Mai solleva: un errore -> None."""
    try:
        if not ATTIVO or not isinstance(r, dict) or r.get("passed"):
            return None
        n_trade = int(r.get("trades") or 0)
        if n_trade < MIN_TRADE:
            return None
        key = f"{sym}|{spec['id']}"
        if key in (gia_validate or ()):
            return None
        if spec.get("origine") == "referto" and spec.get("ipotesi_da"):
            return None                     # giudicata su dati tagliati nel passato
        glob = dict(config_globale or {})
        scelta = r.get("scale_r_mults") is not None
        uscita = {
            "scale_r_mults": [float(x) for x in (r.get("scale_r_mults")
                                                  or glob.get("scale_r_mults") or [])],
            "sl_to_breakeven": (glob.get("sl_to_breakeven") if r.get("sl_to_breakeven") is None
                                else bool(r["sl_to_breakeven"])),
            "profit_lock_keep": (glob.get("profit_lock_keep") if r.get("profit_lock_keep") is None
                                 else float(r["profit_lock_keep"])),
        }
        hold = r.get("holdout") if isinstance(r.get("holdout"), dict) else {}
        return {
            "key": key, "symbol": sym, "spec_id": spec["id"],
            "trades": n_trade, "pf": r.get("pf"), "pnl": r.get("pnl"),
            "win": r.get("win"), "t_stat": r.get("t_stat"), "max_dd": r.get("max_dd"),
            "window_pnls": list(r.get("window_pnls") or []),
            "data_end": float(r.get("data_end") or 0.0),
            "fail_binding": r.get("fail_binding"),
            "fail_criteria": list(r.get("fail_criteria") or []),
            "fail_shortfall": r.get("fail_shortfall"),
            "near_miss": bool(r.get("near_miss")),
            "holdout_ok": (bool(hold.get("ok")) if hold else None),
            "uscita": uscita,
            "uscita_fonte": "scelta_dal_gate" if scelta else "globale",
        }
    except Exception:  # noqa: BLE001
        return None


# --------------------------------------------------------------------------- #
# Nel processo principale: il campione                                         #
# --------------------------------------------------------------------------- #
def nuovo_seme() -> int:
    """Il seme del giro: da CONTROLLO_GRUPPI_SEME se impostato, altrimenti da
    `secrets` (casuale del sistema, NON tocca lo stato di `random`)."""
    env = os.getenv("CONTROLLO_GRUPPI_SEME", "").strip()
    if env:
        return int(env)
    return secrets.randbits(31)


def _uniche(idonee: list[dict]) -> dict[str, dict]:
    uniche: dict[str, dict] = {}
    for v in idonee or []:
        if isinstance(v, dict) and v.get("key") and v["key"] not in uniche:
            uniche[v["key"]] = v
    return uniche


def chiavi_idonee(idonee: list[dict]) -> list[str]:
    """Le chiavi fra cui `campiona` estrae, nell'ordine in cui le estrae
    (senza doppioni, ordinate): e' l'elenco che si salva a ogni giro."""
    return sorted(_uniche(idonee))


def impronta_idonee(chiavi: list[str]) -> str:
    """L'impronta (sha256) dell'elenco delle idonee: del testo non compresso
    del file `_idonee_`, cioe' le chiavi unite da «\\n»."""
    return hashlib.sha256("\n".join(chiavi).encode("utf-8")).hexdigest()


def campiona(idonee: list[dict], n: int, seme: int) -> list[dict]:
    """`n` voci estratte a caso, senza ripetizioni, con un generatore SOLO
    nostro. Le idonee si tolgono dai doppioni e si ordinano per chiave prima
    di estrarre: stesso seme + stesse idonee = stesso campione, qualunque sia
    l'ordine in cui i worker le hanno restituite. Il campione esce ordinato per
    chiave."""
    uniche = _uniche(idonee)
    chiavi = sorted(uniche)
    rng = random.Random(int(seme))
    scelte = rng.sample(chiavi, min(max(0, int(n)), len(chiavi)))
    return [uniche[k] for k in sorted(scelte)]


def togli_dal_registro(idonee: list[dict], pairs: dict) -> list[dict]:
    """Via le candidate che nel registro hanno gia' almeno una conferma: stanno
    nei gruppi della foto (1 conferma, 2 conferme, validate), non fra le
    bocciate. Una coppia a zero conferme nel registro resta idonea."""
    out = []
    for v in idonee or []:
        rec = (pairs or {}).get(v.get("key"))
        try:
            pc = int((rec or {}).get("pass_count", 0) or 0) if isinstance(rec, dict) else 0
        except (TypeError, ValueError):
            pc = 0
        if pc < 1:
            out.append(v)
    return out


def righe_bocciate(campione: list[dict], spec_di, *, seme: int, popolazione: int,
                   interval: str, run_end: str, start: str, windows: int,
                   now: float, modalita: str = "", giro: str | None = None) -> list[dict]:
    """Le righe da scrivere, con la spec INTERA ripresa da `spec_di(sym, id)`.
    Una voce senza spec ritrovabile si salta (non si potrebbe rigiocare).
    `giro`: l'id della riga «tipo: giro» del blocco (formato 2)."""
    out = []
    for v in campione:
        spec = spec_di(v["symbol"], v["spec_id"])
        if not isinstance(spec, dict):
            continue
        out.append({
            "formato": FORMATO, "tipo": "bocciata", "giro": giro,
            "key": v["key"], "symbol": v["symbol"], "spec": spec,
            "timeframe": spec.get("timeframe") or interval,
            "interval": interval,
            # l'istante della valutazione: `valutata_at` e' l'orologio del
            # giro (l'istante in cui ha letto il registro), `data_end` l'ultima
            # candela vista. Il rigioco conta SOLO i trade nati dopo `data_end`.
            "valutata_at": float(now), "data_end": v.get("data_end"),
            "giorno": giorno_locale(now),
            "run_end": run_end, "start": start, "windows": int(windows),
            "modalita": modalita,
            "uscita": v.get("uscita"), "uscita_fonte": v.get("uscita_fonte"),
            "motivo": {"binding": v.get("fail_binding"),
                       "criteri": v.get("fail_criteria"),
                       "shortfall": v.get("fail_shortfall"),
                       "quasi_passaggio": v.get("near_miss"),
                       "holdout_ok": v.get("holdout_ok")},
            "numeri": {"trades": v.get("trades"), "pf": v.get("pf"), "pnl": v.get("pnl"),
                       "win": v.get("win"), "t_stat": v.get("t_stat"),
                       "max_dd": v.get("max_dd"), "window_pnls": v.get("window_pnls")},
            "seme": int(seme), "popolazione": int(popolazione),
        })
    return out


# --------------------------------------------------------------------------- #
# La foto delle conferme                                                       #
# --------------------------------------------------------------------------- #
def foto_conferme(pairs: dict, now: float, *, validate, declassate=(), operate=(),
                  timeframe_di=None, config_di=None, spec_nota_di=None) -> list[dict]:
    """Una riga per coppia del registro. `validate`/`declassate`/`operate` sono
    gli insiemi calcolati dal chiamante con le funzioni del registro
    (`bot/core/registry.py`), cosi' la definizione e' quella del bot.
    `timeframe_di(rec, key)`, `config_di(last_params)` e `spec_nota_di(rec,
    key)` sono facoltativi.

    30 set 2026, revisione: per le coppie BASE (`generated` falso) la riga
    porta anche `params`, la copia intera di `last_params` (adx_min, vol_mult,
    rr, atr_mult_stop...): la strategia base non ha una spec, e senza i suoi
    parametri dalla foto non si ricostruisce (il registro la puo' potare)."""
    validate, declassate, operate = set(validate or ()), set(declassate or ()), set(operate or ())
    out = []
    for key in sorted(pairs or {}):
        rec = pairs[key]
        if not isinstance(rec, dict):
            continue
        try:
            pc = int(rec.get("pass_count", 0) or 0)
        except (TypeError, ValueError):
            pc = 0
        riga = {
            "formato": FORMATO, "tipo": "conferme",
            "key": key, "symbol": rec.get("symbol") or key.split("|", 1)[0],
            "strategy": rec.get("strategy") or key.split("|", 1)[-1],
            "pass_count": pc, "validata": key in validate,
            "declassata": key in declassate, "operata": key in operate,
            "generated": bool(rec.get("generated")),
            "sostituita_da": rec.get("sostituita_da"),
            "validated_at": rec.get("validated_at"),
            "last_pass_data_end": rec.get("last_pass_data_end"),
            "istante": float(now), "giorno": giorno_locale(now),
        }
        if not riga["generated"]:
            lp = rec.get("last_params")
            riga["params"] = dict(lp) if isinstance(lp, dict) else {}
        if timeframe_di is not None:
            try:
                riga["timeframe"] = timeframe_di(rec, key)
            except Exception:  # noqa: BLE001
                riga["timeframe"] = None
        if config_di is not None:
            try:
                riga["uscita"] = config_di(rec.get("last_params"))
            except Exception:  # noqa: BLE001
                riga["uscita"] = None
        if spec_nota_di is not None:
            try:
                riga["spec_nota"] = spec_nota_di(rec, key)
            except Exception:  # noqa: BLE001
                riga["spec_nota"] = None
        out.append(riga)
    return out


# --------------------------------------------------------------------------- #
# Disco                                                                        #
# --------------------------------------------------------------------------- #
def percorso(giorno: str, tipo: str, cartella: str | None = None) -> str:
    return os.path.join(cartella or CONTROLLO_DIR, f"{giorno}_{tipo}.jsonl")


def percorso_idonee(giorno: str, giro: str, cartella: str | None = None) -> str:
    """Il file compresso con l'elenco delle idonee di un giro (formato 2)."""
    return os.path.join(cartella or CONTROLLO_DIR, f"{giorno}_idonee_{giro}.txt.gz")


def _jsonl_n(righe: list[dict]) -> tuple[str, int]:
    parti = []
    for r in righe:
        try:
            parti.append(json.dumps(r, ensure_ascii=False, allow_nan=False))
        except (TypeError, ValueError):
            continue                        # un NaN salta LA RIGA, non il giro
    return "".join(p + "\n" for p in parti), len(parti)


def _jsonl(righe: list[dict]) -> str:
    return _jsonl_n(righe)[0]


def _scrivi_a_parte(path: str, dati, esclusivo: bool = False, binario: bool = False) -> bool:
    """Scrive `dati` in un file temporaneo col pid nel nome, fa fsync e poi lo
    mette al suo posto (30 set 2026, revisione). Con `esclusivo` il file finale
    si CREA soltanto (`os.link`, che fallisce se esiste gia'): due giri insieme
    non scrivono la foto due volte, e chi arriva secondo ritorna False. Il
    temporaneo si toglie sempre. Su un filesystem senza link fisici si ripiega
    su `os.replace` (atomico, ma senza l'esclusione)."""
    tmp = f"{path}.{os.getpid()}.tmp"
    try:
        with open(tmp, "wb" if binario else "w", **({} if binario else {"encoding": "utf-8"})) as fh:
            fh.write(dati)
            fh.flush()
            os.fsync(fh.fileno())
        if not esclusivo:
            os.replace(tmp, path)
            return True
        try:
            os.link(tmp, path)
        except FileExistsError:
            return False
        except OSError:
            if os.path.exists(path):
                return False
            os.replace(tmp, path)
        return True
    finally:
        try:
            if os.path.exists(tmp):
                os.unlink(tmp)
        except OSError:
            pass


def _foto_fatta(path: str) -> bool:
    """La foto del giorno c'e' davvero: il file esiste e non e' vuoto (un file
    vuoto lasciato da un crash della macchina non conta, si rifa')."""
    try:
        return os.path.getsize(path) > 0
    except OSError:
        return False


def spazio_usato(cartella: str | None = None) -> int:
    tot = 0
    cartella = cartella or CONTROLLO_DIR
    try:
        for nome in os.listdir(cartella):
            p = os.path.join(cartella, nome)
            if os.path.isfile(p):
                tot += os.path.getsize(p)
    except FileNotFoundError:
        return 0
    return tot


def pulisci(cartella: str | None = None, giorni: float = RITENZIONE_GIORNI,
            now: float | None = None, giorni_idonee: float | None = None) -> int:
    """Cancella i .jsonl piu' vecchi di `giorni`, gli elenchi delle idonee
    (.gz) piu' vecchi di `giorni_idonee` (RITENZIONE_IDONEE_GIORNI) e i
    temporanei (.tmp) rimasti da un crash da piu' di un giorno. Ritorna quanti."""
    cartella = cartella or CONTROLLO_DIR
    adesso = time.time() if now is None else now
    soglia = adesso - giorni * 86400
    g_idonee = RITENZIONE_IDONEE_GIORNI if giorni_idonee is None else giorni_idonee
    soglia_gz = adesso - g_idonee * 86400
    soglia_tmp = adesso - 86400
    tolti = 0
    try:
        for nome in os.listdir(cartella):
            p = os.path.join(cartella, nome)
            eta = os.path.getmtime(p)
            if ((nome.endswith(".jsonl") and eta < soglia)
                    or (nome.endswith(".gz") and eta < soglia_gz)
                    or (nome.endswith(".tmp") and eta < soglia_tmp)):
                os.remove(p)
                tolti += 1
    except FileNotFoundError:
        pass
    return tolti


def leggi(path: str, tipo: str | None = None) -> list[dict]:
    """Rilegge un file della raccolta (per l'analisi e per i test). Le righe
    illeggibili si saltano. Con `tipo` («bocciata», «conferme», «spec»,
    «giro») solo le righe di quel tipo."""
    out = []
    with open(path, encoding="utf-8") as fh:
        for riga in fh:
            riga = riga.strip()
            if not riga:
                continue
            try:
                d = json.loads(riga)
            except ValueError:
                continue
            if tipo is None or (isinstance(d, dict) and d.get("tipo") == tipo):
                out.append(d)
    return out


def leggi_idonee(path: str) -> list[str]:
    """Rilegge l'elenco delle idonee di un giro (file `_idonee_` compresso)."""
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        testo = fh.read()
    return testo.split("\n") if testo else []


def con_giro(righe: list[dict]) -> list[dict]:
    """Le righe di dati (bocciate, conferme, spec) con i campi della loro riga
    «tipo: giro» sotto `motore` (le impostazioni) e `giro_info` (il resto).
    Le righe di formato 1, senza giro, escono come sono."""
    giri = {r.get("giro"): r for r in righe if isinstance(r, dict) and r.get("tipo") == "giro"}
    out = []
    for r in righe:
        if not isinstance(r, dict) or r.get("tipo") == "giro":
            continue
        g = giri.get(r.get("giro"))
        if g is not None:
            r = {**r, "motore": g.get("motore"),
                 "giro_info": {k: v for k, v in g.items() if k != "motore"}}
        out.append(r)
    return out


# --------------------------------------------------------------------------- #
# Il giro                                                                      #
# --------------------------------------------------------------------------- #
def raccogli(*, idonee: list[dict], pairs: dict, spec_di, foto_di, interval: str,
             run_end: str, start: str, windows: int, now: float | None = None,
             modalita: str = "", seme: int | None = None,
             cartella: str | None = None, motore: dict | None = None,
             spec_foto_di=None) -> str:
    """Scrive il campione delle bocciate e, se oggi non c'e' ancora, la foto
    delle conferme. Ritorna la riga di log (gia' stampata). NON SOLLEVA MAI.

    `foto_di()` costruisce le righe della foto: si chiama SOLO se la foto di
    oggi manca, cosi' nei giri successivi non costa niente. `spec_foto_di()`,
    facoltativa, le righe del file delle spec del giorno, scritto insieme alla
    foto. `motore`: le impostazioni del motore e del gate del giro (formato 2),
    scritte nella riga «tipo: giro». `now`: l'istante del giro; il ponte della
    discovery passa quello in cui ha letto il registro."""
    try:
        now = time.time() if now is None else float(now)
        cartella = cartella or CONTROLLO_DIR
        if not ATTIVO:
            riga = "raccolta spenta (CONTROLLO_GRUPPI=false)"
            _log(riga)
            return riga
        os.makedirs(cartella, exist_ok=True)
        tolti = pulisci(cartella, now=now)
        if tolti:
            _log(f"{tolti} file vecchi cancellati (.jsonl oltre {RITENZIONE_GIORNI:g} giorni, "
                 f"idonee oltre {RITENZIONE_IDONEE_GIORNI:g})")
        usato = spazio_usato(cartella)
        if usato > TETTO_MB * 1024 * 1024:
            riga = (f"tetto di spazio superato ({usato / 1048576:.0f} MB su {TETTO_MB:g}): "
                    f"niente scritto in questo giro")
            _log(riga)
            return riga
        giorno = giorno_locale(now)
        # 0) il giro: id, popolazione, elenco e impronta delle idonee
        seme = nuovo_seme() if seme is None else int(seme)
        pool = togli_dal_registro(idonee, pairs)
        chiavi = chiavi_idonee(pool)
        n_pop = len(chiavi)
        giro_id = f"{int(now)}-{interval}-{seme}"
        nome_idonee = None
        parte_idonee = ""
        if chiavi:
            try:
                p_id = percorso_idonee(giorno, giro_id, cartella)
                _scrivi_a_parte(p_id, gzip.compress("\n".join(chiavi).encode("utf-8")),
                                binario=True)
                nome_idonee = os.path.basename(p_id)
            except Exception as exc:  # noqa: BLE001
                parte_idonee = f" · idonee NON salvate ({type(exc).__name__})"
        riga_giro = {
            "formato": FORMATO, "tipo": "giro", "giro": giro_id,
            "istante": now, "giorno": giorno, "interval": interval, "modalita": modalita,
            "run_end": run_end, "start": start, "windows": int(windows),
            "seme": seme, "campione": int(CAMPIONE), "min_trade": int(MIN_TRADE),
            "popolazione": n_pop, "idonee_sha256": impronta_idonee(chiavi),
            "idonee_file": nome_idonee, "motore": dict(motore or {}),
        }
        # 1) le bocciate, dopo la riga del giro
        campione = campiona(pool, CAMPIONE, seme)
        righe = righe_bocciate(campione, spec_di, seme=seme, popolazione=n_pop,
                               interval=interval, run_end=run_end, start=start,
                               windows=windows, now=now, modalita=modalita, giro=giro_id)
        n_boc = 0
        try:
            testo_righe, n_boc = _jsonl_n(righe)
            with open(percorso(giorno, "bocciate", cartella), "a", encoding="utf-8") as fh:
                fh.write(_jsonl([riga_giro]) + testo_righe)
            parte_boc = f"salvate {n_boc} bocciate su {n_pop} idonee (seme {seme})"
        except Exception as exc:  # noqa: BLE001
            parte_boc = f"bocciate NON salvate ({type(exc).__name__}: {str(exc)[:80]})"
        # 2) la foto, una volta al giorno: scritta a parte e poi creata in modo
        #    esclusivo, cosi' un file a meta' (o vuoto) non vale come «foto fatta»
        p_foto = percorso(giorno, "conferme", cartella)
        try:
            if _foto_fatta(p_foto):
                parte_foto = "foto conferme: già fatta oggi"
            else:
                if os.path.exists(p_foto) and os.path.getsize(p_foto) == 0:
                    os.remove(p_foto)       # vuoto: lasciato da un crash
                foto = [dict(r, giro=giro_id) if isinstance(r, dict) else r
                        for r in (foto_di() or [])]
                if _scrivi_a_parte(p_foto, _jsonl([riga_giro] + foto), esclusivo=True):
                    # le spec del giorno SOLO dopo aver vinto la foto (riverifica del
                    # 30 set 2026): se due giri la fanno insieme, chi perde la foto
                    # non deve sovrascrivere le spec con la riga di un altro giro
                    parte_spec = ""
                    if spec_foto_di is not None:
                        try:
                            spec_righe = [dict(r, giro=giro_id) for r in (spec_foto_di() or [])
                                          if isinstance(r, dict)]
                            testo_spec, n_spec = _jsonl_n(spec_righe)
                            _scrivi_a_parte(percorso(giorno, "spec", cartella),
                                            _jsonl([riga_giro]) + testo_spec)
                            parte_spec = f", spec {n_spec}"
                        except Exception as exc:  # noqa: BLE001
                            parte_spec = f", spec NON salvate ({type(exc).__name__})"
                    parte_foto = f"foto conferme: {len(foto)} coppie{parte_spec}"
                else:
                    parte_foto = "foto conferme: già fatta da un altro giro"
        except Exception as exc:  # noqa: BLE001
            parte_foto = f"foto conferme NON salvata ({type(exc).__name__}: {str(exc)[:80]})"
        riga = f"{parte_boc}{parte_idonee} · {parte_foto} [{interval}]"
        _log(riga)
        return riga
    except Exception as exc:  # noqa: BLE001
        riga = f"raccolta saltata (si prosegue): {type(exc).__name__}: {str(exc)[:120]}"
        try:
            _log(riga)
        except Exception:  # noqa: BLE001
            pass
        return riga
