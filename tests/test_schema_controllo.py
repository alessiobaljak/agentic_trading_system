"""
PARITA' fra il contratto, chi scrive e chi legge (25 set 2026).

`docs/controllo_schema.md` e' il contratto dei due documenti (`dashboard/controllo`
scritto dal bot, `dashboard/gate` scritto dalla discovery). Lo leggono la
dashboard (`dashboard/app/lib/controllo.ts` + `gate.ts`) e il comando ops
`controllo`. Un nome che cambia in uno solo dei tre posti rompe la dashboard in
silenzio: un campo `undefined` non e' un errore, e' un tile vuoto.

Questo test costruisce i due documenti dalle fixture degli altri test e controlla:
  1. che ogni campo elencato nelle tabelle del contratto (parsate DAL FILE, non
     copiate a mano) esista nel documento, e che il documento non porti campi
     che il contratto non nomina (le testate comuni a parte);
  2. le forme annidate del contratto (le colonne `tipo`, scritte qui a mano
     perche' nel markdown sono prosa): `{campo, campo}` e `list[{campo, campo}]`;
  3. che ogni nome dichiarato nei tipi TypeScript della dashboard esista da
     qualche parte nel documento Python, e viceversa: i tipi sono lo specchio
     del contratto, non possono conoscere campi che il bot non scrive ne'
     ignorare campi che il bot scrive.
"""
from __future__ import annotations

import os
import re

import pytest

from tests.test_controllo import NOW, _fb
from tests.test_controllo import _doc as _doc_controllo
from tests.test_doc_gate import _costruisci, _fixture_piccola

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONTRATTO = os.path.join(ROOT, "docs", "controllo_schema.md")
TS_CONTROLLO = os.path.join(ROOT, "dashboard", "app", "lib", "controllo.ts")
TS_GATE = os.path.join(ROOT, "dashboard", "app", "lib", "gate.ts")

#: la testata che ogni sezione porta (regole comuni del contratto); `dettaglio`
#: e' facoltativo
TESTATA = {"computed_at", "fonti", "lettura", "dettaglio", "errore"}


# --------------------------------------------------------------------------- #
# il contratto, letto dal file                                                 #
# --------------------------------------------------------------------------- #
def campi_del_contratto() -> dict[str, list[str]]:
    """Le tabelle `| campo | tipo | ... |` del contratto, per sezione: la chiave e'
    il numero del paragrafo piu' il nome (`1.2 salute`, `2.1 meta`); dentro §1.4
    i due sotto-elenchi `attivo`/`misurato` diventano `1.4 attivo`/`1.4 misurato`.
    Una riga puo' elencare piu' campi separati da ` / `: si prendono tutti i
    backtick della prima cella."""
    out: dict[str, list[str]] = {}
    sezione = None
    numero = None
    tabella_di_campi = False
    with open(CONTRATTO, encoding="utf-8") as f:
        for riga in f:
            riga = riga.rstrip("\n")
            m = re.match(r"^### (\d+\.\d+) `([a-z_]+)`", riga)
            if m:
                numero, sezione = m.group(1), f"{m.group(1)} {m.group(2)}"
                tabella_di_campi = False
                continue
            m = re.match(r"^`(attivo|misurato)`:\s*$", riga)
            if m and numero:
                sezione = f"{numero} {m.group(1)}"
                tabella_di_campi = False
                continue
            if not riga.startswith("|") or sezione is None:
                continue
            celle = [c.strip() for c in riga.strip("|").split("|")]
            if celle and celle[0] == "campo":
                tabella_di_campi = True
                continue
            if not tabella_di_campi or celle[0].startswith("---"):
                continue
            nomi = re.findall(r"`([A-Za-z_0-9]+)", celle[0])
            out.setdefault(sezione, []).extend(nomi)
    return out


@pytest.fixture(scope="module")
def contratto() -> dict[str, list[str]]:
    c = campi_del_contratto()
    assert {"1.1 meta", "1.2 salute", "1.3 paper", "1.4 attivo", "1.4 misurato",
            "2.1 meta", "2.2 giro", "2.3 registro", "2.4 cervello", "2.5 strategie"} <= set(c), \
        sorted(c)
    return c


@pytest.fixture(scope="module")
def doc_controllo() -> dict:
    """La fixture realistica di test_controllo, con il freno globale acceso (cosi'
    la lista delle anomalie non e' vuota e la sua forma si puo' controllare) e il
    portafoglio simulato scritto (cosi' `benchmark.portafoglio` non e' null)."""
    fb = _fb(verdetto_drift="drift")
    fb.set_doc("portfolio", "backtest", {"lettura": "il portafoglio simulato batte il paper",
                                         "updated_at": NOW - 3600})
    doc = _doc_controllo(fb=fb, durata_ms=120)
    assert doc["meta"]["errori"] == [], doc["meta"]["errori"]
    return doc


@pytest.fixture(scope="module")
def doc_gate() -> dict:
    doc = _costruisci(*_fixture_piccola())
    for nome in ("giro", "registro", "cervello", "strategie"):
        assert doc[nome]["errore"] is None, (nome, doc[nome]["errore"])
    return doc


# --------------------------------------------------------------------------- #
# 1. i campi di primo livello di ogni sezione                                  #
# --------------------------------------------------------------------------- #
def _sezione(doc: dict, percorso: str) -> dict:
    nodo = doc
    for p in percorso.split("."):
        nodo = nodo[p]
    return nodo


def _campi_presenti(doc: dict, percorso: str) -> set[str]:
    """I campi di una sezione, tolta la testata comune — che `meta` non porta:
    il suo `errore` (gate) e' un campo del contratto, non la testata."""
    presenti = set(_sezione(doc, percorso))
    return presenti if percorso == "meta" else presenti - TESTATA


@pytest.mark.parametrize("chiave, percorso", [
    ("1.1 meta", "meta"), ("1.2 salute", "salute"), ("1.3 paper", "paper"),
    ("1.4 attivo", "learning.attivo"), ("1.4 misurato", "learning.misurato"),
])
def test_le_sezioni_del_controllo_hanno_i_campi_del_contratto(contratto, doc_controllo, chiave, percorso):
    attesi = set(contratto[chiave])
    presenti = _campi_presenti(doc_controllo, percorso)
    assert attesi - presenti == set(), f"{percorso}: nel contratto ma non nel documento"
    assert presenti - attesi == set(), f"{percorso}: nel documento ma non nel contratto"


@pytest.mark.parametrize("chiave, percorso", [
    ("2.1 meta", "meta"), ("2.2 giro", "giro"), ("2.3 registro", "registro"),
    ("2.4 cervello", "cervello"), ("2.5 strategie", "strategie"),
])
def test_le_sezioni_del_gate_hanno_i_campi_del_contratto(contratto, doc_gate, chiave, percorso):
    attesi = set(contratto[chiave])
    presenti = _campi_presenti(doc_gate, percorso)
    assert attesi - presenti == set(), f"{percorso}: nel contratto ma non nel documento"
    assert presenti - attesi == set(), f"{percorso}: nel documento ma non nel contratto"


def test_il_documento_del_controllo_ha_le_cinque_parti_e_learning_la_sua_testata(doc_controllo):
    assert set(doc_controllo) == {"meta", "salute", "paper", "learning", "manca"}
    assert {"computed_at", "fonti", "lettura", "errore", "attivo", "misurato"} <= set(doc_controllo["learning"])
    for sez in ("salute", "paper", "learning.attivo", "learning.misurato"):
        assert {"computed_at", "fonti", "lettura", "errore"} <= set(_sezione(doc_controllo, sez)), sez


def test_il_documento_del_gate_ha_le_cinque_parti(doc_gate):
    assert set(doc_gate) == {"meta", "giro", "registro", "cervello", "strategie"}


# --------------------------------------------------------------------------- #
# 2. le forme annidate (colonna `tipo` del contratto)                          #
# --------------------------------------------------------------------------- #
def _nodi(doc, percorso: str) -> list:
    """I nodi a un percorso `a.b[].c`: `[]` entra in ogni voce della lista. I
    `null` cadono (sono «non misurato»), ma almeno un nodo deve restare: la
    fixture deve davvero produrre la forma che si controlla."""
    nodi = [doc]
    for passo in percorso.split("."):
        lista = passo.endswith("[]")
        nome = passo[:-2] if lista else passo
        prossimi = []
        for n in nodi:
            v = n.get(nome) if isinstance(n, dict) else None
            if v is None:
                continue
            if lista:
                assert isinstance(v, list), (percorso, nome, type(v))
                prossimi.extend(x for x in v if x is not None)
            else:
                prossimi.append(v)
        nodi = prossimi
    assert nodi, f"{percorso}: nessun nodo nella fixture (tutti null o lista vuota)"
    return nodi


CONTROLLO_ANNIDATE = {
    "salute.rifiuti_ciclo[]": {"motivo", "n"},
    "salute.rifiuti_24h[]": {"motivo", "n"},
    "salute.circuit_breaker": {"halted_for_day", "paused_until_ts", "macro_flat_until_ts",
                               "consecutive_sl", "daily_pnl_pct"},
    "salute.cooldown_coin[]": {"nome", "fino_a"},
    "salute.cooldown_strategie[]": {"nome", "fino_a"},
    "salute.posizioni[]": {"coin", "direzione", "rischio_pct", "upnl"},
    "salute.anomalie[]": {"codice", "famiglia", "gravita", "testo", "valore", "soglia"},
    "paper.ultimi_30g": {"trades", "pnl", "pf", "win_rate"},
    "paper.oggi": {"trades", "vinti", "pnl", "migliore", "peggiore"},
    "paper.oggi.migliore": {"coin", "pnl"},
    "paper.oggi.peggiore": {"coin", "pnl"},
    "paper.giornate": {"con_trade", "positive", "negative", "migliore", "peggiore", "ultime_7"},
    "paper.giornate.migliore": {"data", "pnl"},
    "paper.giornate.peggiore": {"data", "pnl"},
    "paper.giornate.ultime_7[]": {"data", "trades", "pnl"},
    "paper.uscite[]": {"motivo", "etichetta", "trades", "quota", "pnl"},
    "paper.gradini[]": {"gradino", "n"},
    "paper.mfe": {"n", "mediana_r", "quota_1r", "quota_1_5r", "quota_3r"},
    "paper.stop": {"totale", "sbagliati", "quasi", "oltre_primo_tp", "quasi_durata_mediana_h",
                   "primo_gradino_r", "nota"},
    "paper.direzione": {"long", "short"},
    "paper.direzione.long": {"trade", "vinti", "pnl", "mfe_mediana"},
    "paper.direzione.short": {"trade", "vinti", "pnl", "mfe_mediana"},
    "paper.allineamento": {"in_trend", "contro", "neutro", "ignoto"},
    "paper.allineamento.in_trend": {"trade", "pnl"},
    "paper.costi": {"totale", "per_trade", "commissioni", "spread", "funding", "lordo", "netto",
                    "break_even_pct", "stimati", "avvisi"},
    "paper.trailing": {"verdetti_totali", "prematuri", "protetti", "neutri", "verdetti_per_proposta",
                       "prematuri_tf", "protetti_tf", "proposta_paper", "soglia"},
    "paper.benchmark": {"btc_24h_pct", "btc_7g_pct", "nota", "portafoglio"},
    "paper.benchmark.portafoglio": {"lettura", "updated_at"},
    "paper.esplorative": {"trades", "vinti", "pnl", "aperte", "coppie_attive"},
    "paper.declassate": {"trades", "pnl", "aperte"},
    "learning.attivo.freno_globale": {"attivo", "verdetto", "trades", "pf_vissuto", "pf_atteso",
                                      "pf_atteso_nota", "soglia_uscita_pf", "size_x", "leva_x_min",
                                      "motivo", "dal"},
    "learning.attivo.pesi": {"at", "aggiornato_da_nota", "versione", "campioni_sommati", "combinazioni",
                             "soglia_panchina", "in_panchina_n", "spente_n", "in_panchina"},
    "learning.attivo.pesi.in_panchina[]": {"strategia", "regime", "peso", "campione", "win_rate"},
    "learning.attivo.tilt": {"trend_enabled", "trend_strength", "trend_floor", "sentiment_enabled",
                             "sentiment_strength"},
    "learning.attivo.keep_per_coppia": {"distribuzione", "non_rivalutate"},
    "learning.attivo.keep_per_coppia.distribuzione[]": {"valore", "n"},
    "learning.attivo.freno_serie": {"enabled", "perdite_soglia", "fattore", "serie"},
    "learning.attivo.freno_serie.serie[]": {"strategia", "perdite"},
    "learning.attivo.tetti": {"coin_giorno_pct", "direzione_pct", "max_posizioni",
                              "max_posizioni_attivo", "correlate_max"},
    "learning.attivo.impronta": {"freno", "panchina", "cooldown", "keep", "validate", "gate_pronto"},
    "learning.attivo.impronta.keep[]": {"valore", "n"},
    "learning.misurato.deriva": {"at", "coppie_ok", "coppie_watch", "coppie_drift", "soglia_coppia",
                                 "soglia_strategia", "max_trades_coppia", "top"},
    "learning.misurato.deriva.top[]": {"coppia", "verdetto", "trades", "pf_vissuto", "pf_atteso", "motivo"},
    "learning.misurato.calibrazione": {"at", "verdetto", "trades", "correlazione", "trust", "nota"},
    "learning.misurato.trailing": {"verdetti_totali", "prematuri", "protetti", "neutri",
                                   "verdetti_per_proposta", "prematuri_tf", "protetti_tf",
                                   "proposta_paper", "soglia"},
    "learning.misurato.referti": {"n_con_referto", "persi_con_referto", "ingresso", "uscita", "protezione",
                                  "stop_largo", "lock_mai", "controtrend", "ipotesi"},
    "learning.misurato.selettore": {"at", "verdetti", "nota"},
    "learning.misurato.ombra_ai": {"n", "agree", "ultimo_at"},
    "learning.misurato.ipotesi_ai": {"proposte", "accettate", "at"},
    "manca[]": {"evidenza", "perche", "come_avere"},
}

GATE_ANNIDATE = {
    "giro.passate_lista[]": {"coin", "id", "pf", "pnl"},
    "giro.candidate": {"totale", "ai", "varianti_referti", "intorno", "casuali", "semi",
                       "gemelle_scartate", "rivalutate"},
    "giro.passata_1h": {"at", "durata_s", "coin", "valutazioni", "passate"},
    "giro.paper_propone": {"scala", "keep", "verdetti_trailing"},
    "giro.ipotesi_uscita": {"strategie", "con_scala"},
    "giro.esplorative": {"attive", "validate_poi", "scartate"},
    "registro.distribuzione_pass[]": {"pass", "coppie", "coin"},
    "registro.statistica_t": {"misurate", "sopra_2", "sopra_3", "mediana", "piu_basse"},
    "registro.statistica_t.piu_basse[]": {"coppia", "t"},
    "cervello.intorno": {"madri", "figlie_passate", "promosse", "senza_margine", "madre_non_valutata",
                         "scartate", "ultimo_completo_at"},
    "cervello.varianti": {"create", "passate", "retro_ok", "promosse", "scartate", "sostituzioni"},
    "cervello.varianti.sostituzioni[]": {"figlia", "madre"},
    "cervello.keep_giro": {"scelti", "non_scelto", "dal_paper", "dal_paper_n"},
    "cervello.keep_giro.scelti[]": {"valore", "n"},
    "cervello.keep_validate": {"distribuzione", "non_rivalutate"},
    "cervello.keep_validate.distribuzione[]": {"valore", "n"},
    "cervello.scala_validate[]": {"scala", "n"},
    "cervello.autopsia": {"at", "valutazioni", "passate", "quota", "criterio_principale", "quota_criterio",
                          "quasi_passaggi"},
    "cervello.supervisore": {"at", "ultima_decisione", "decisioni_none_di_fila"},
    "cervello.supervisore.ultima_decisione": {"kind", "reason"},
    "strategie.operate[]": {"chiave", "coin", "strategia", "famiglia", "origine", "genitore", "ipotesi",
                            "pass", "validata_at", "ultimo_pass_at", "pf_promesso", "pnl_promesso_pct",
                            "t", "holdout_ok", "scala", "breakeven", "keep", "direzione_pf", "paper"},
    "strategie.operate[].direzione_pf": {"long", "short"},
    "strategie.operate[].paper": {"trades", "vinti", "pnl", "pf_vissuto", "perdite", "verdetto", "motivo"},
    "strategie.per_famiglia[]": {"famiglia", "coppie", "coin", "pf_promesso_mediano", "paper_trades",
                                 "paper_pnl", "paper_pf"},
    "strategie.per_coin[]": {"coin", "coppie", "paper_trades", "paper_pnl"},
    "strategie.promessa_vs_vissuto": {"pf_promesso_mediano_operate", "pf_atteso_media_registro",
                                      "pf_vissuto_30g"},
    "strategie.vite": {"promosse_7g", "rimosse_7g", "parziale"},
}


@pytest.mark.parametrize("percorso", sorted(CONTROLLO_ANNIDATE))
def test_le_forme_annidate_del_controllo(doc_controllo, percorso):
    for nodo in _nodi(doc_controllo, percorso):
        assert isinstance(nodo, dict), (percorso, nodo)
        assert set(nodo) == CONTROLLO_ANNIDATE[percorso], percorso


@pytest.mark.parametrize("percorso", sorted(GATE_ANNIDATE))
def test_le_forme_annidate_del_gate(doc_gate, percorso):
    for nodo in _nodi(doc_gate, percorso):
        assert isinstance(nodo, dict), (percorso, nodo)
        assert set(nodo) == GATE_ANNIDATE[percorso], percorso


# --------------------------------------------------------------------------- #
# 3. i tipi TypeScript della dashboard                                         #
# --------------------------------------------------------------------------- #
def campi_ts(percorso: str, escludi: set[str]) -> set[str]:
    """I nomi dei campi di tutte le `export interface` di un file .ts (anche gli
    oggetti scritti in linea dentro un campo). `escludi` sono le interfacce
    che non descrivono il documento (gli attrezzi della sottoscrizione)."""
    with open(percorso, encoding="utf-8") as f:
        src = f.read()
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    src = re.sub(r"//[^\n]*", "", src)
    nomi: set[str] = set()
    for m in re.finditer(r"export interface (\w+)[^{]*\{", src):
        if m.group(1) in escludi:
            continue
        # il corpo dell'interfaccia: fino alla graffa che chiude quella aperta
        i, prof = m.end(), 1
        while i < len(src) and prof:
            prof += {"{": 1, "}": -1}.get(src[i], 0)
            i += 1
        corpo = src[m.end():i - 1]
        nomi.update(re.findall(r"(?:^|[\s{;])([A-Za-z_][A-Za-z_0-9]*)\??\s*:", corpo))
    return nomi


def chiavi_python(doc, salta: set[str] = frozenset()) -> set[str]:
    """Tutte le chiavi del documento, a ogni profondita'. Sotto le chiavi in
    `salta` non si scende: sono mappe con chiavi dinamiche (nomi di famiglie)."""
    out: set[str] = set()

    def visita(n):
        if isinstance(n, dict):
            for k, v in n.items():
                out.add(k)
                if k not in salta:
                    visita(v)
        elif isinstance(n, list):
            for x in n:
                visita(x)

    visita(doc)
    return out


@pytest.mark.skipif(not os.path.exists(TS_CONTROLLO), reason="dashboard non nel checkout")
def test_i_tipi_ts_del_controllo_sono_lo_specchio_del_documento(doc_controllo):
    ts = campi_ts(TS_CONTROLLO, {"Documento", "DocumentoVivo"})
    py = chiavi_python(doc_controllo, salta={"verdetti"})
    assert ts - py == set(), "nei tipi TS ma il bot non lo scrive"
    assert py - ts == set(), "scritto dal bot ma sconosciuto ai tipi TS"


@pytest.mark.skipif(not os.path.exists(TS_GATE), reason="dashboard non nel checkout")
def test_i_tipi_ts_del_gate_sono_lo_specchio_del_documento(doc_gate):
    # gate.ts importa `Testata` e `ValoreN` da controllo.ts: si aggiungono
    testata_e_valore_n = {"computed_at", "fonti", "lettura", "dettaglio", "errore", "valore", "n"}
    ts = campi_ts(TS_GATE, set()) | testata_e_valore_n
    py = chiavi_python(doc_gate)
    assert ts - py == set(), "nei tipi TS ma la discovery non lo scrive"
    assert py - ts == set(), "scritto dalla discovery ma sconosciuto ai tipi TS"


# --------------------------------------------------------------------------- #
# 4. cio' che la dashboard legge davvero                                        #
# --------------------------------------------------------------------------- #
COMPONENTI = os.path.join(ROOT, "dashboard", "app", "components")


def _accessi(nome_file: str, radici: dict[str, str]) -> set[str]:
    """Le catene `radice.a.b` lette in un componente, tradotte in percorsi del
    documento (`radici` mappa la variabile locale al suo percorso: `p` ->
    `paper`). Solo i nomi di campo: `.length`/`.map` e simili cadono."""
    with open(os.path.join(COMPONENTI, nome_file), encoding="utf-8") as f:
        src = f.read()
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    src = re.sub(r"//[^\n]*", "", src)
    metodi = {"length", "map", "filter", "reduce", "join", "slice", "some", "every", "find",
              "toFixed", "toLocaleString", "toUpperCase", "toLowerCase", "has", "add", "delete",
              "entries", "get", "set", "sort", "includes", "startsWith", "replace", "split"}
    out: set[str] = set()
    for m in re.finditer(r"\b([A-Za-z_][A-Za-z_0-9]*)((?:\?\.|\.)[A-Za-z_][A-Za-z_0-9]*)+", src):
        parti = m.group(0).replace("?.", ".").split(".")
        if parti[0] not in radici:
            continue
        campi = [p for p in parti[1:] if p not in metodi]
        if campi:
            out.add(".".join(([radici[parti[0]]] if radici[parti[0]] else []) + campi))
    return out


def _esiste(doc, percorso: str) -> bool:
    """Il percorso esiste nel documento: dentro le liste si guarda la prima voce
    non nulla; un `null` lungo il cammino vale come «campo che c'e'»."""
    nodo = doc
    for p in percorso.split("."):
        if isinstance(nodo, list):
            nodo = next((x for x in nodo if x is not None), None)
        if nodo is None:
            return True
        if not isinstance(nodo, dict) or p not in nodo:
            return False
        nodo = nodo[p]
    return True


@pytest.mark.skipif(not os.path.isdir(COMPONENTI), reason="dashboard non nel checkout")
def test_i_campi_letti_dai_pannelli_esistono_nel_documento_del_controllo(doc_controllo):
    letture = {
        "ControlloHero.tsx": {"meta": "meta", "salute": "salute", "paper": "paper",
                              "attivo": "learning.attivo"},
        "ControlloPaper.tsx": {"p": "paper"},
        "TopVitals.tsx": {"controllo": ""},
        "RiskControl.tsx": {"controllo": ""},
        "LearningAttivoMisurato.tsx": {"l": "learning", "salute": "salute"},
    }
    mancanti = []
    for nome, radici in letture.items():
        for percorso in sorted(_accessi(nome, radici)):
            if not _esiste(doc_controllo, percorso):
                mancanti.append(f"{nome}: {percorso}")
    assert mancanti == [], mancanti


@pytest.mark.skipif(not os.path.isdir(COMPONENTI), reason="dashboard non nel checkout")
def test_i_campi_letti_dai_pannelli_esistono_nel_documento_del_gate(doc_gate):
    letture = {
        "GateCervello.tsx": {"g": "giro", "c": "cervello", "r": "registro", "meta": "meta"},
        "StrategieOperate.tsx": {"s": "strategie"},
    }
    mancanti = []
    for nome, radici in letture.items():
        for percorso in sorted(_accessi(nome, radici)):
            # `disc`/`chiave` di StrategieOperate sono lo stato dell'ordinamento
            # (variabile locale `ordine`), non campi: `s.` non li tocca
            if not _esiste(doc_gate, percorso):
                mancanti.append(f"{nome}: {percorso}")
    assert mancanti == [], mancanti
