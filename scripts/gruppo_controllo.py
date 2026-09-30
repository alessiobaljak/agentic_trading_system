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
    `bot/core/tempo.giorno_locale`), al primo giro del giorno, lo stato di
    ogni coppia del registro: pass_count, validata, declassata, istante. Il
    gruppo di una coppia e' quello della foto del giorno in cui ci entra: una
    coppia che il 1 ott ha 1 conferma resta nel gruppo «1 conferma» anche se
    poi conferma ancora (cosi' i trade buoni non cambiano gruppo).

REGOLE (non si negoziano):
  * FAIL-OPEN: un errore qui non fa fallire ne' rallentare il giro. Al massimo
    una riga di log «[controllo-gruppi] ...».
  * NON CAMBIA NIENTE del giro: verdetti, semi della ricerca e ordine delle
    candidate restano identici. Il campione usa un generatore casuale SUO
    (`random.Random(seme)`), il seme nasce da `secrets` (che non tocca lo
    stato di `random`), e le candidate idonee si ordinano per chiave prima di
    estrarre: il campione dipende solo da (seme, insieme delle idonee).
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
"""
from __future__ import annotations

import json
import os
import random
import secrets
import time

from bot.core.tempo import giorno_locale

#: la cartella dei file, relativa alla cartella del servizio (come
#: `data/selettore`). Un test la sposta con l'ambiente.
CONTROLLO_DIR = os.getenv("CONTROLLO_GRUPPI_DIR", "data/gruppo_controllo")
#: interruttore: "false" spegne la raccolta (il giro resta identico)
ATTIVO = os.getenv("CONTROLLO_GRUPPI", "true").lower() != "false"
#: quante bocciate per giro
CAMPIONE = int(os.getenv("CONTROLLO_GRUPPI_CAMPIONE", "50"))
#: trade OOS minimi perche' una bocciata sia rigiocabile con senso
MIN_TRADE = int(os.getenv("CONTROLLO_GRUPPI_MIN_TRADE", "30"))
#: rotazione: file piu' vecchi di tanti giorni si cancellano
RITENZIONE_GIORNI = float(os.getenv("CONTROLLO_GRUPPI_RITENZIONE_GIORNI", "120"))
#: tetto dichiarato di spazio: oltre, non si scrive piu'
TETTO_MB = float(os.getenv("CONTROLLO_GRUPPI_TETTO_MB", "300"))

#: la versione del formato delle righe: chi rilegge controlla questa
FORMATO = 1


def _log(testo: str) -> None:
    print(f"[controllo-gruppi] {testo}")


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


def campiona(idonee: list[dict], n: int, seme: int) -> list[dict]:
    """`n` voci estratte a caso, senza ripetizioni, con un generatore SOLO
    nostro. Le idonee si tolgono dai doppioni e si ordinano per chiave prima
    di estrarre: stesso seme + stesse idonee = stesso campione, qualunque sia
    l'ordine in cui i worker le hanno restituite. Il campione esce ordinato per
    chiave."""
    uniche: dict[str, dict] = {}
    for v in idonee or []:
        if isinstance(v, dict) and v.get("key") and v["key"] not in uniche:
            uniche[v["key"]] = v
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
                   now: float, modalita: str = "") -> list[dict]:
    """Le righe da scrivere, con la spec INTERA ripresa da `spec_di(sym, id)`.
    Una voce senza spec ritrovabile si salta (non si potrebbe rigiocare)."""
    out = []
    for v in campione:
        spec = spec_di(v["symbol"], v["spec_id"])
        if not isinstance(spec, dict):
            continue
        out.append({
            "formato": FORMATO, "tipo": "bocciata",
            "key": v["key"], "symbol": v["symbol"], "spec": spec,
            "timeframe": spec.get("timeframe") or interval,
            "interval": interval,
            # l'istante della valutazione: `valutata_at` e' l'orologio del
            # giro, `data_end` l'ultima candela vista. Il rigioco conta SOLO i
            # trade nati dopo `data_end`.
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
                  timeframe_di=None, config_di=None) -> list[dict]:
    """Una riga per coppia del registro. `validate`/`declassate`/`operate` sono
    gli insiemi calcolati dal chiamante con le funzioni del registro
    (`bot/core/registry.py`), cosi' la definizione e' quella del bot.
    `timeframe_di(rec, key)` e `config_di(last_params)` sono facoltativi."""
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
        out.append(riga)
    return out


# --------------------------------------------------------------------------- #
# Disco                                                                        #
# --------------------------------------------------------------------------- #
def percorso(giorno: str, tipo: str, cartella: str | None = None) -> str:
    return os.path.join(cartella or CONTROLLO_DIR, f"{giorno}_{tipo}.jsonl")


def _jsonl(righe: list[dict]) -> str:
    parti = []
    for r in righe:
        try:
            parti.append(json.dumps(r, ensure_ascii=False, allow_nan=False))
        except (TypeError, ValueError):
            continue                        # un NaN salta LA RIGA, non il giro
    return "".join(p + "\n" for p in parti)


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
            now: float | None = None) -> int:
    """Cancella i .jsonl piu' vecchi di `giorni`. Ritorna quanti."""
    cartella = cartella or CONTROLLO_DIR
    soglia = (time.time() if now is None else now) - giorni * 86400
    tolti = 0
    try:
        for nome in os.listdir(cartella):
            p = os.path.join(cartella, nome)
            if nome.endswith(".jsonl") and os.path.getmtime(p) < soglia:
                os.remove(p)
                tolti += 1
    except FileNotFoundError:
        pass
    return tolti


def leggi(path: str) -> list[dict]:
    """Rilegge un file della raccolta (per l'analisi e per i test). Le righe
    illeggibili si saltano."""
    out = []
    with open(path, encoding="utf-8") as fh:
        for riga in fh:
            riga = riga.strip()
            if not riga:
                continue
            try:
                out.append(json.loads(riga))
            except ValueError:
                continue
    return out


# --------------------------------------------------------------------------- #
# Il giro                                                                      #
# --------------------------------------------------------------------------- #
def raccogli(*, idonee: list[dict], pairs: dict, spec_di, foto_di, interval: str,
             run_end: str, start: str, windows: int, now: float | None = None,
             modalita: str = "", seme: int | None = None,
             cartella: str | None = None) -> str:
    """Scrive il campione delle bocciate e, se oggi non c'e' ancora, la foto
    delle conferme. Ritorna la riga di log (gia' stampata). NON SOLLEVA MAI.

    `foto_di()` costruisce le righe della foto: si chiama SOLO se la foto di
    oggi manca, cosi' nei giri successivi non costa niente."""
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
            _log(f"{tolti} file piu' vecchi di {RITENZIONE_GIORNI:g} giorni cancellati")
        usato = spazio_usato(cartella)
        if usato > TETTO_MB * 1024 * 1024:
            riga = (f"tetto di spazio superato ({usato / 1048576:.0f} MB su {TETTO_MB:g}): "
                    f"niente scritto in questo giro")
            _log(riga)
            return riga
        giorno = giorno_locale(now)
        # 1) le bocciate
        seme = nuovo_seme() if seme is None else int(seme)
        pool = togli_dal_registro(idonee, pairs)
        n_pop = len({v.get("key") for v in pool})
        campione = campiona(pool, CAMPIONE, seme)
        righe = righe_bocciate(campione, spec_di, seme=seme, popolazione=n_pop,
                               interval=interval, run_end=run_end, start=start,
                               windows=windows, now=now, modalita=modalita)
        n_boc = 0
        try:
            if righe:
                testo = _jsonl(righe)
                with open(percorso(giorno, "bocciate", cartella), "a", encoding="utf-8") as fh:
                    fh.write(testo)
                n_boc = testo.count("\n")
            parte_boc = f"salvate {n_boc} bocciate su {n_pop} idonee (seme {seme})"
        except Exception as exc:  # noqa: BLE001
            parte_boc = f"bocciate NON salvate ({type(exc).__name__}: {str(exc)[:80]})"
        # 2) la foto, una volta al giorno: scritta a parte e poi rinominata,
        #    cosi' un file a meta' non vale come «foto fatta»
        p_foto = percorso(giorno, "conferme", cartella)
        try:
            if os.path.exists(p_foto):
                parte_foto = "foto conferme: già fatta oggi"
            else:
                foto = foto_di()
                tmp = p_foto + ".tmp"
                with open(tmp, "w", encoding="utf-8") as fh:
                    fh.write(_jsonl(foto))
                os.replace(tmp, p_foto)
                parte_foto = f"foto conferme: {len(foto)} coppie"
        except Exception as exc:  # noqa: BLE001
            parte_foto = f"foto conferme NON salvata ({type(exc).__name__}: {str(exc)[:80]})"
        riga = f"{parte_boc} · {parte_foto} [{interval}]"
        _log(riga)
        return riga
    except Exception as exc:  # noqa: BLE001
        riga = f"raccolta saltata (si prosegue): {type(exc).__name__}: {str(exc)[:120]}"
        try:
            _log(riga)
        except Exception:  # noqa: BLE001
            pass
        return riga
