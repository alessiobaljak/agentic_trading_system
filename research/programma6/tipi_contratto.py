"""I tipi dei contratti perpetui di Binance, per riconoscere nella ricerca i contratti che non sono monete (audit del 26 novembre
2026, problema motore-2; backlog P32).

La ricerca toglieva i contratti su azioni, indici e materie prime solo per nome (``esclusi.py``, fermo al 19 ottobre 2026); il bot
li toglie con il tipo ufficiale (``bot/portafoglio/f5.contratti_monete``: contractType PERPETUAL, underlyingType COIN, niente
TradFi); la ricerca usa la stessa regola piu' i perpetui di pre-mercato su una moneta (``e_moneta_ricerca``, 27 novembre 2026).
Questo script scrive, da ``/fapi/v1/exchangeInfo`` (da www.binance.com), per ogni simbolo in USDT: underlyingType, contractType,
underlyingSubType e onboardDate (ms), in ``tipi_contratto.json``. Un simbolo che sparisce dall'elenco (tolto dal
listino) resta nel file com'era. ``seconda.costruisci_pannello`` toglie i giorni di un contratto che non e' una moneta dal suo
onboardDate in poi: quelli di prima restano, perche' tre simboli di vecchie monete oggi sono azioni (ANTUSDT, MDTUSDT, NUUSDT).

Non tocca ``esclusi.py``, che il bot importa.

Uso: python3 -m research.programma6.tipi_contratto
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

QUI = Path(__file__).parent
FILE = QUI / "tipi_contratto.json"
URL = "https://www.binance.com/fapi/v1/exchangeInfo"
TESTATA = {"User-Agent": "Mozilla/5.0"}
CAMPI = ("underlyingType", "contractType", "underlyingSubType", "onboardDate")
MINIMO = 300                 # un elenco con meno simboli non e' una risposta buona: il file non si tocca


def e_moneta(t: dict) -> bool:
    """Come il bot (``f5.contratti_monete``): perpetuo, sottostante una moneta, niente TradFi."""
    return (t.get("contractType") == "PERPETUAL" and t.get("underlyingType", "COIN") == "COIN"
            and "TradFi" not in (t.get("underlyingSubType") or []))


def e_moneta_ricerca(t: dict) -> bool:
    """La regola della ricerca (``seconda.costruisci_pannello``, ``funding_api.da_scaricare``): quella del bot (``e_moneta``) piu' i
    perpetui di pre-mercato su una moneta (contractType PERPETUAL, underlyingType PREMARKET, senza TradFi ne' Pre-IPO), come conta
    le monete la regola di N3 (paper/REGOLE.md, sezione 11: contratto annunciato senza «TradFi» ne' «Pre-IPO»). 27 novembre 2026
    (secondo controllo indipendente dell'audit del 26 novembre): con la sola regola del bot PREDICTUSDT, pre-mercato su una moneta
    dal 25 ottobre 2026, usciva dalla tabella e spariva l'evento N3 gia' pubblicato del 1° novembre. Il bot non cambia."""
    sotto = t.get("underlyingSubType") or []
    premercato = (t.get("contractType") == "PERPETUAL" and t.get("underlyingType") == "PREMARKET"
                  and "TradFi" not in sotto and "Pre-IPO" not in sotto)
    return e_moneta(t) or premercato


def tipi(info: dict) -> dict:
    """{simbolo: {campo: valore}} dei contratti in USDT di una risposta di exchangeInfo."""
    return {x["symbol"]: {k: x[k] for k in CAMPI if k in x}
            for x in (info or {}).get("symbols", []) if x.get("quoteAsset") == "USDT" and "symbol" in x}


def unisci(vecchi: dict, nuovi: dict) -> dict:
    """I nuovi sostituiscono i vecchi; i simboli che non ci sono piu' restano com'erano."""
    return dict(sorted({**vecchi, **nuovi}.items()))


def leggi(file: Path = FILE) -> dict:
    """{simbolo: tipo}; vuoto se il file non c'e' (allora la ricerca toglie solo per nome, come prima)."""
    try:
        return json.loads(Path(file).read_text(encoding="utf-8"))["simboli"]
    except (OSError, ValueError, KeyError):
        return {}


def scrivi(simboli: dict, file: Path = FILE, aggiornato: str | None = None) -> None:
    """Una riga per simbolo, per vedere bene le differenze in git."""
    testa = {"fonte": URL, "aggiornato": aggiornato or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
             "nota": "underlyingType, contractType, underlyingSubType e onboardDate (ms) da exchangeInfo; un simbolo tolto dal "
                     "listino resta com'era (research/programma6/tipi_contratto.py)"}
    righe = [f" {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}" for k, v in simboli.items()]
    testo = "{\n" + "".join(f" {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)},\n" for k, v in testa.items())
    testo += ' "simboli": {\n' + ",\n".join(righe) + "\n }\n}\n"
    Path(file).write_text(testo, encoding="utf-8")


def main() -> dict:
    import requests
    r = requests.get(URL, headers=TESTATA, timeout=30)
    r.raise_for_status()
    nuovi = tipi(r.json())
    if len(nuovi) < MINIMO:
        raise RuntimeError(f"exchangeInfo con {len(nuovi)} simboli in USDT: risposta sospetta, {FILE.name} non toccato")
    vecchi = leggi()
    tutti = unisci(vecchi, nuovi)
    scrivi(tutti)
    non_monete = sum(1 for t in tutti.values() if not e_moneta_ricerca(t))
    print(f"[tipi_contratto] simboli {len(tutti)} (dalla risposta {len(nuovi)}, rimasti dal file {len(set(vecchi) - set(nuovi))});"
          f" non monete {non_monete}", flush=True)
    return {"simboli": len(tutti), "non_monete": non_monete}


if __name__ == "__main__":
    main()
