"""Impronte dei file di riferimento di BTCUSDT (last, nove timeframe)."""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune as C  # noqa: E402
from research.src import dati  # noqa: E402

imp = dati.registra_impronte("BTCUSDT")
print(len(imp), "file")
shutil.copy(C.RADICE_REPO / "research/data/insample/BTCUSDT/impronte.json",
            C.RADICE_REPO / "research/campagne/LINKUSDT/impronte_btcusdt.json")
