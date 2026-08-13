"""
Parallelizzazione CPU-bound del backtesting (GATE 1).

Il walk-forward è puro calcolo Python per-simbolo e indipendente tra simboli:
si parallelizza su PIÙ PROCESSI (non thread: il GIL renderebbe i thread inutili)
sfruttando tutti i core del runner. Acceleriamo la potenza di calcolo SENZA
ridurre l'universo o le combinazioni.

Uso: ogni worker costruisce il proprio stato pesante (optimizer + contesto BTC) UNA
volta tramite `initializer`, poi `func` lavora un simbolo alla volta leggendo quello
stato. Fallback sequenziale automatico se i worker sono <= 1.
"""
from __future__ import annotations

import os
from concurrent.futures import ProcessPoolExecutor
from typing import Callable, Iterable


def available_gb() -> float:
    """RAM realmente disponibile ORA (Linux). 0 se non leggibile."""
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    return float(line.split()[1]) / 1024 / 1024
    except Exception:  # noqa: BLE001
        pass
    return 0.0


def workers_for(requested: int, avail_gb: float, per_worker_gb: float) -> int:
    """Quanti processi si possono davvero tenere in piedi con questa RAM.

    Ogni worker carica quattro anni di candele e il frame degli indicatori per un
    simbolo: circa un giga e mezzo. Chiederne piu' di quanti la memoria ne regga
    non li rende piu' veloci — li fa uccidere dal kernel a meta' validazione, e il
    servizio risulta `failed` dopo ore di calcolo buttate, senza che nulla nel log
    dell'applicazione spieghi perche'.

    Si tiene un giga di margine per il sistema e per il bot, che gira sulla stessa
    macchina e ha la precedenza: e' lui che sorveglia le posizioni.
    """
    if avail_gb <= 0 or per_worker_gb <= 0:
        return max(1, requested)          # niente misura: non si inventa un limite
    cap = int(max(0.0, avail_gb - 1.0) // per_worker_gb)
    return max(1, min(requested, cap))


def n_workers() -> int:
    """Numero di processi: BACKTEST_WORKERS (o tutti i core), MA limitato dalla RAM
    davvero disponibile. Il tetto vale anche su un valore impostato a mano: un 8
    esplicito che fa finire il run in OOM e' peggio di un 6 automatico che arriva
    in fondo. Quando il tetto scatta, lo dice."""
    env = os.getenv("BACKTEST_WORKERS")
    requested = max(1, int(env)) if env else max(1, os.cpu_count() or 1)
    per_worker = float(os.getenv("BACKTEST_MEM_PER_WORKER_GB", "1.5"))
    avail = available_gb()
    allowed = workers_for(requested, avail, per_worker)
    if allowed < requested:
        print(f"[parallel] worker ridotti da {requested} a {allowed}: "
              f"{avail:.1f} GB disponibili, ~{per_worker:g} GB per worker "
              f"(alza BACKTEST_MEM_PER_WORKER_GB se la stima e' pessimistica)")
    return allowed


def parallel_map(func: Callable, items: list, *, workers: int | None = None,
                 initializer: Callable | None = None, initargs: tuple = ()) -> list:
    """
    Applica `func` a ogni item, in parallelo su più processi (ordine preservato).
    Fallback sequenziale se workers <= 1 o un solo item: in quel caso `initializer`
    viene chiamato una volta nel processo corrente (così `func` trova lo stesso stato).
    """
    workers = workers or n_workers()
    items = list(items)
    if workers <= 1 or len(items) <= 1:
        if initializer is not None:
            initializer(*initargs)
        return [func(it) for it in items]
    with ProcessPoolExecutor(max_workers=workers, initializer=initializer,
                             initargs=initargs) as ex:
        return list(ex.map(func, items))
