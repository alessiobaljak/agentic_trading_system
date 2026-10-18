"""Funzioni comuni agli script della campagna LINK6: serie di costruzione, log, conteggio delle varianti.

Solo il periodo di costruzione (dalla prima candela al 2022-09-30): il caricatore rifiuta da solo le date
della validazione (regola 2).
"""
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from research.src import dati  # noqa: E402

CAMPAGNA = Path(__file__).resolve().parents[1]
LOG = CAMPAGNA / "log.jsonl"
CARTELLA_DATI = dati.RADICE_DEFAULT / "data" / "insample" / "LINKUSDT"
SIMBOLO = "LINKUSDT"
INIZIO_DATI = date(2020, 1, 1)
FINE_COSTRUZIONE = date(2022, 9, 30)
VARIANTI_MASSIME = 40
TRADE_MINIMI = 150

_serie = {}


def serie_costruzione(tf):
    """(serie, inizio, fine): la serie di LINKUSDT del timeframe sul periodo di costruzione, con gli indici."""
    if tf not in _serie:
        s = dati.serie_4(SIMBOLO, tf, INIZIO_DATI, FINE_COSTRUZIONE)
        _serie[tf] = (s, 0, len(s.ts) - 1)
    return _serie[tf]


def ora():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def voci():
    if not LOG.exists():
        return []
    return [json.loads(r) for r in LOG.read_text(encoding="utf-8").splitlines() if r.strip()]


def aggiungi(voce):
    """Aggiunge una voce al log (solo in aggiunta); rifiuta una coppia (id, tipo) gia' presente."""
    if any(v.get("id") == voce["id"] and v.get("tipo") == voce["tipo"] for v in voci()):
        raise SystemExit(f"id gia' presente nel log: {voce['id']} ({voce['tipo']})")
    nuova = {"id": voce["id"], "tipo": voce["tipo"], "data": ora()}
    nuova.update({k: v for k, v in voce.items() if k not in ("id", "tipo", "data")})
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(nuova, ensure_ascii=False) + "\n")
    return nuova


def varianti_registrate():
    return [v for v in voci() if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante"]


def leggi_lotto(percorso):
    return {v["id"]: v for v in json.loads(Path(percorso).read_text(encoding="utf-8"))}


def scrivi_avanzamento(nome, riga):
    with (CARTELLA_DATI / nome).open("a", encoding="utf-8") as f:
        f.write(riga + "\n")
