"""IL SUPERVISORE, in esecuzione. Gira da solo su timer: nessun comando da lanciare.

Legge lo stato (registro, autopsia, taratura corrente), chiede a
`bot/learning/supervisor.py` cosa fare, e lo fa. Ogni decisione finisce su Firebase
e dentro docs/state.md, che e' committato: cosi' il "perche'" resta leggibile anche
a mesi di distanza, e senza entrare sulla VPS.

Le modifiche vanno in `tuning.env`, che questo script possiede per intero. Il `.env`
con le chiavi non viene mai toccato da nessun processo automatico.

Uso:
    .venv/bin/python -m scripts.supervisor            # decide e AGISCE
    .venv/bin/python -m scripts.supervisor --dry-run  # dice cosa farebbe
"""
from __future__ import annotations

import argparse
import os
import subprocess
import time
from datetime import datetime, timezone

from bot.config import settings
from bot.core.firebase_client import decode_pairs, get_firebase
from bot.learning.supervisor import NEVER, TUNABLES, Context, decide

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TUNING_FILE = os.path.join(APP_DIR, "tuning.env")

HEADER = """\
# TARATURA AUTOMATICA — generato da scripts/supervisor.py. NON modificare a mano:
# alla prossima decisione verrebbe riscritto. Per tornare ai default: cancella
# questo file e riavvia i servizi. Il .env con le chiavi non e' toccato da qui.
"""


def read_tuning() -> dict:
    out: dict = {}
    try:
        with open(TUNING_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip()
    except FileNotFoundError:
        pass
    return out


def write_tuning(values: dict) -> None:
    """Riscrive il file per intero. Atomico: un file di taratura letto a meta' da un
    servizio che parte in quel momento darebbe una configurazione inventata."""
    body = HEADER + f"# aggiornato: {datetime.now(timezone.utc).isoformat()}\n"
    for k in sorted(values):
        body += f"{k}={values[k]}\n"
    tmp = TUNING_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(body)
    os.replace(tmp, TUNING_FILE)


def current_values() -> dict:
    """Valore EFFETTIVO di ogni parametro tarabile: quello che i processi vedono
    davvero (default del codice, sovrascritto da .env, sovrascritto da tuning.env),
    non quello che ci aspettiamo che sia."""
    return {t.name: float(getattr(settings, t.name)) for t in TUNABLES.values()
            if hasattr(settings, t.name)}


def _autopsy(fb) -> dict:
    """Le due autopsie sommate. La discovery porta il grosso del volume, l'optimizer
    le strategie base: per decidere dove si muore contano insieme."""
    tot = {"evaluated": 0, "passed": 0, "binding": {}, "near": {}}
    for doc_id in ("current", "discover"):
        rep = fb.get_doc("gate_autopsy", doc_id) or {}
        tot["evaluated"] += int(rep.get("evaluated", 0) or 0)
        tot["passed"] += int(rep.get("passed", 0) or 0)
        for k, v in (rep.get("binding") or {}).items():
            tot["binding"][k] = tot["binding"].get(k, 0) + int(v or 0)
        # i QUASI-PASSAGGI raggruppati per criterio: e' il segnale su cui si sceglie
        # la leva, perche' sono le uniche candidate che un allentamento converte
        for n in (rep.get("near_misses") or []):
            crit = n.get("binding")
            if crit:
                tot["near"].setdefault(crit, []).append(float(n.get("shortfall") or 0))
    return tot


def build_context(fb, state: dict, tuned: dict | None = None) -> Context:
    reg = fb.get_doc("strategy_registry", "validated") or {}
    pairs = decode_pairs(reg.get("pairs"))
    min_passes = int(os.getenv("OPTIMIZER_MIN_PASSES", "3"))
    validated = len([1 for r in pairs.values()
                     if int(r.get("pass_count", 0) or 0) >= min_passes])
    now = time.time()
    # STAGNAZIONE = da quanto non arriva una coppia validata. Si azzera appena ne
    # arriva una: e' il segnale che la ricerca sta producendo, e finche' produce non
    # c'e' niente da tarare.
    since = float(state.get("validated_since", 0) or 0)
    prev = state.get("last_validated")
    # si riparte da zero SOLO se il conteggio e' davvero cresciuto rispetto a una
    # misura precedente. Un `prev` assente non e' "zero validate": e' "non lo so
    # ancora", e trattarlo come un aumento azzererebbe la stagnazione a ogni giro —
    # il supervisore non arriverebbe mai a decidere niente.
    if since <= 0 or (prev is not None and validated > int(prev)):
        since = now
    a = _autopsy(fb)
    # quante passate al giorno: dal timer systemd, con un default prudente
    runs = float(os.getenv("SUPERVISOR_RUNS_PER_DAY", "8"))
    return Context(
        ready=bool(reg.get("ready")), validated=validated,
        days_stagnant=max(0.0, (now - since) / 86400.0),
        evaluated=a["evaluated"], passed=a["passed"], binding=a["binding"],
        near=a["near"],
        current=current_values(), tuned=dict(tuned or {}),
        min_passes=min_passes, runs_per_day=runs,
        budget=float(os.getenv("SUPERVISOR_FALSE_POSITIVE_BUDGET", "1.0")),
        independence=float(os.getenv("SUPERVISOR_CONFIRM_INDEPENDENCE", "0.5")),
        stagnant_after_days=float(os.getenv("SUPERVISOR_STAGNANT_DAYS", "2")),
        # DISARMATO per default: e' l'unica azione irreversibile che il supervisore
        # puo' decidere da solo, azzera le conferme accumulate e non e' annullabile
        # da remoto. Si arma con SUPERVISOR_FAST_GATE_DAYS>0 quando c'e' qualcuno
        # che guarda. Vedi il commento in bot/learning/supervisor.py.
        fast_gate_after_days=float(os.getenv("SUPERVISOR_FAST_GATE_DAYS", "0")),
        days_since_fast_gate=max(0.0, (now - float(state.get("last_fast_gate", 0) or 0))
                                 / 86400.0) if state.get("last_fast_gate") else 999.0,
        fast_gate_cooldown_days=float(os.getenv("SUPERVISOR_FAST_GATE_COOLDOWN", "7")),
    )


def _launch_fast_gate() -> str:
    """Lancia fast_gate in background dentro tmux, cosi' sopravvive alla fine di
    questo processo (dura ore) e resta ispezionabile a mano."""
    cmd = ["tmux", "new-session", "-d", "-s", "fastgate",
           f"cd {APP_DIR} && bash scripts/fast_gate.sh --yes >> fastgate.log 2>&1"]
    try:
        subprocess.run(cmd, check=True, timeout=30)
        return "avviato in tmux (sessione 'fastgate')"
    except Exception as exc:  # noqa: BLE001
        return f"NON avviato: {str(exc)[:120]}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="mostra le decisioni senza applicarle")
    args = ap.parse_args()

    fb = get_firebase()
    state = fb.get_doc("supervisor", "state") or {}
    tuning = read_tuning()
    ctx = build_context(fb, state, tuning)
    decisions = decide(ctx)

    print(f"[supervisor] validate={ctx.validated} ready={ctx.ready} "
          f"stagnazione={ctx.days_stagnant:.1f}g · valutazioni={ctx.evaluated} "
          f"passate={ctx.passed} (tasso {ctx.pass_rate * 100:.3f}%)")

    applied: list[dict] = []
    for d in decisions:
        print(f"[supervisor] {d.kind.upper()}: {d.reason}")
        if d.kind == "set_param":
            if d.param in NEVER:      # cintura: la logica non lo propone, qui non passa
                print(f"[supervisor] RIFIUTATO: {d.param} — {NEVER[d.param]}")
                continue
            print(f"[supervisor]   {d.param}: {d.old:g} -> {d.new:g}")
            if not args.dry_run:
                tuning[d.param] = f"{d.new:g}"
                write_tuning(tuning)
        elif d.kind == "revert":
            # si torna al punto noto togliendo le voci: il valore di partenza e'
            # quello del codice o del .env, che non e' stato toccato da nessuno.
            for nome in (d.detail.get("reverted") or []):
                tuning.pop(nome, None)
                print(f"[supervisor]   disfatto {nome}")
            if not args.dry_run:
                write_tuning(tuning)
        elif d.kind == "fast_gate":
            if not args.dry_run:
                res = _launch_fast_gate()
                print(f"[supervisor]   fast_gate {res}")
                d.detail["launch"] = res
                state["last_fast_gate"] = time.time()
        applied.append({"kind": d.kind, "reason": d.reason, "param": d.param,
                        "old": d.old, "new": d.new, "detail": d.detail,
                        "at": time.time()})

    if not args.dry_run:
        state.update({
            "updated_at": time.time(), "validated": ctx.validated,
            "last_validated": ctx.validated, "ready": ctx.ready,
            "validated_since": time.time() - ctx.days_stagnant * 86400.0,
            "pass_rate": round(ctx.pass_rate, 6),
            "tuning": tuning, "last_decisions": applied[-10:],
            # storico: le ultime venti decisioni con il motivo. E' l'unico modo di
            # rispondere fra due mesi a "perche' questa soglia sta a questo valore?"
            "history": ([*(state.get("history") or []), *applied])[-20:],
        })
        fb.set_doc("supervisor", "state", state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
