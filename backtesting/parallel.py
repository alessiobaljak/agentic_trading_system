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


def n_workers() -> int:
    """Numero di processi: BACKTEST_WORKERS se impostato, altrimenti tutti i core."""
    env = os.getenv("BACKTEST_WORKERS")
    if env:
        return max(1, int(env))
    return max(1, os.cpu_count() or 1)


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
