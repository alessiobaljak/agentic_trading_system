"""L'esecutore unico della campagna di gruppo, ``research/src/gruppo.py`` (``campagne/GRUPPO/regole.md``, sezione 13).

Si verifica, con 1-3 monete sintetiche (candele giornaliere generate qui con semi fissi, un fattore di mercato
comune, funding a 8 ore) e la variante d'esempio ``dati_gruppo/variante_esempio.py``:

1. i parametri congelati letti da ``parametri.yaml`` e i ``Parametri`` di una moneta;
2. il contratto: le quattro funzioni, il modulo importato dai byte di cui si ha l'impronta, il contesto senza
   simbolo e senza futuro (anche alla creazione), e una variante che chiede il futuro non vede nulla;
3. con UNA moneta, quella con j = 0, e senza il pavimento delle sfasate, ogni numero e' quello del percorso
   delle campagne singole (``conta_trade``, ``esegui``, ``baseline_da_trade``, ``simula_baseline_casuale``,
   ``contro_baseline``), calcolato qui senza ``gruppo.py``; la (a) con 2 trade e meno di 3 blocchi a parte;
4. due monete calcolate a mano: pesi, A, M(s), B, pavimento delle sfasate, blocco, confronti;
5. le sfasate: lo stesso spostamento su tutte le monete, gli ingressi saltati tolti e contati;
6. il filtro di liquidita': gli stessi segnali tolti in ``conta_trade``, nel test e nella (a), le stesse
   barre vietate alla (b), alle sfasate e nel vault;
7. ``ingressi_placebo`` (gli stessi numeri della variante; rifiutato con il marcatore), il via libera (con il
   marcatore GRUPPO, anche con una cartella di uscita fuori da ``campagne/GRUPPO/``; senza marcatore no);
8. la ripresa da un avanzamento interrotto, l'invarianza all'ordine delle monete e al numero di processi;
9. ``controllo_positivo`` (passa senza ritardo, crolla con il ritardo), ``esame_vault`` (criterio, tasso del
   caso, monete che smettono, vault chiuso), ``asticella_di_gruppo``, il caricatore dal disco;
10. le correzioni dopo la revisione del 10 ottobre: il modulo eseguito da capo per ogni moneta, gli import
   ammessi, la strategia casuale che rifa' i trade del test, la ripresa con l'impronta dei dati, i controlli di
   campagna nel corpo dell'esame, la cartella della prova a placebo, t = -inf per le varianti non valutabili, il
   buy and hold con gli stessi pesi, le candele di BTCUSDT, un buco prima della validazione, M'(s) dalla
   lettura comune, un processo che muore;
11. il terzo giro di revisione: ``esame_vault`` con il file di avanzamento (cartella obbligatoria fuori da
   ``campagne/``, 1 o 4 processi, interrotto e ripreso: stessi numeri), le sfasate del vault come quattro
   somme per s e per moneta con le metriche di ``metriche_di_gruppo`` entro 1e-12 relativo, la prova sulle
   monete nel vault; in campagna ogni moneta deve avere candele, funding e candele 1d del last.

Il marcatore si cerca in ``dati.RADICE_PROGETTO``: una fixture automatica (qui per ogni test, e in ``conftest.py``
per tutta la sessione, prima delle fixture di modulo) la punta a una cartella vuota, cosi' questi test non dipendono
da un marcatore vero; i test che simulano una sessione scrivono il marcatore li'
(solo nel processo dei test: con piu' processi si usano dati sintetici in memoria, che non passano da ``dati``).
"""

import dataclasses
import hashlib
import importlib.util
import json
import math
import shutil
import zlib
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import yaml

from research.src import dati, gruppo, motore, statistica
from research.src.motore import Candela, Parametri, Segnale
from research.src.tests.test_dati import zip_in_memoria

VARIANTE = Path(__file__).resolve().parent / "dati_gruppo" / "variante_esempio.py"
MONETE_CSV_VERO = dati.RADICE_DEFAULT / "campagne" / "GRUPPO" / "monete.csv"
GIORNO = 86_400_000
ORIGINE = date(2020, 1, 1)
P = {"n": 5, "stop": 0.06, "target": 0.09, "durata": 5, "registra_ingressi": True}

# tre monete sintetiche (simbolo, primo mese, fascia di slippage), con un mese illiquido e qualche buco
TRE = (("AAAUSDT", "2022-01-01", 0.0005), ("BBBUSDT", "2022-03-01", 0.001), ("CCCUSDT", "2022-07-01", 0.0005))
MESI_SOTTO = (("AAAUSDT", 2022, 9), ("AAAUSDT", 2023, 8), ("CCCUSDT", 2023, 2))


def ms(giorno: date) -> int:
    """Mezzanotte UTC in ms, calcolata con datetime (indipendente da ``dati.ms_da_data``)."""
    return int(datetime(giorno.year, giorno.month, giorno.day, tzinfo=timezone.utc).timestamp()) * 1000


BUCHI = tuple(("CCCUSDT", ms(date(2022, 8, 10)) + k * GIORNO) for k in range(3)) + \
    (("CCCUSDT", ms(date(2023, 3, 5))), ("BBBUSDT", ms(date(2023, 9, 1))))


@lru_cache(maxsize=None)
def _serie_intera(simbolo: str, primo: str, fine: str, ms_barra: int, seme: int, buchi: tuple) -> tuple:
    """Candele sintetiche: passeggiata casuale con un fattore comune a tutte le monete (le crypto si muovono insieme)."""
    t_origine = ms(ORIGINE)
    t0 = ms(date.fromisoformat(primo))
    t_fine = ms(date.fromisoformat(fine) + timedelta(days=1))
    n = (t_fine - t0) // ms_barra
    scarto = (t0 - t_origine) // ms_barra
    comune = np.random.default_rng([seme, ms_barra, 7]).normal(size=(t_fine - t_origine) // ms_barra)[scarto:scarto + n]
    rng = np.random.default_rng([zlib.crc32(simbolo.encode()), seme, ms_barra])
    propria = rng.normal(size=n)
    scala = 0.035 * math.sqrt(ms_barra / GIORNO)
    rendimenti = scala * (0.6 * comune + 0.8 * propria)
    ombre = np.abs(rng.normal(size=(n, 2))) * 0.4 * scala
    chiusura = 20.0 + zlib.crc32(simbolo.encode()) % 80
    togli = set(buchi)
    candele = []
    for k in range(n):
        apertura = chiusura
        chiusura = apertura * math.exp(float(rendimenti[k]))
        ts = t0 + k * ms_barra
        if ts in togli:
            continue
        alto = max(apertura, chiusura) * (1 + float(ombre[k, 0]))
        basso = min(apertura, chiusura) * (1 - float(ombre[k, 1]))
        candele.append(Candela(ts, apertura, alto, basso, chiusura, 1.0, ts + ms_barra - 1))
    return tuple(candele)


@lru_cache(maxsize=None)
def _funding_intero(simbolo: str, primo: str, fine: str, seme: int) -> tuple:
    """Regolamenti sintetici ogni 8 ore."""
    t0, t_fine = ms(date.fromisoformat(primo)), ms(date.fromisoformat(fine) + timedelta(days=1))
    passo = 8 * 3_600_000
    tassi = np.random.default_rng([zlib.crc32(simbolo.encode()), seme, 99]).normal(1e-4, 2e-4, size=(t_fine - t0) // passo)
    return tuple((t0 + k * passo, float(t)) for k, t in enumerate(tassi))


#: le chiamate a ``serie`` del caricatore finto, in questo processo
CHIAMATE = []


@dataclasses.dataclass(frozen=True)
class CaricatoreFinto:
    """Un caricatore in memoria (stessi metodi di ``gruppo.CaricatoreDisco``), deterministico in ogni processo."""

    monete: tuple = TRE
    mesi_sotto: tuple = MESI_SOTTO
    buchi: tuple = BUCHI
    fine_dati: tuple = ()  # (simbolo, ultimo giorno) per le monete che smettono prima
    fine_generale: str = "2023-12-31"
    guasto: str = ""
    seme: int = 0

    def _info(self, simbolo):
        for s, primo, slippage in self.monete:
            if s == simbolo:
                return primo, slippage
        raise KeyError(simbolo)

    def _fine(self, simbolo):
        return dict(self.fine_dati).get(simbolo, self.fine_generale)

    def scheda(self, simbolo):
        primo, slippage = self._info(simbolo)
        return {"primo_mese": date.fromisoformat(primo), "slippage_per_lato": slippage}

    def serie(self, simbolo, timeframe, inizio, fine):
        CHIAMATE.append((simbolo, inizio.isoformat(), fine.isoformat()))
        if simbolo == self.guasto:
            raise RuntimeError("guasto simulato")
        primo, _ = self._info(simbolo)
        buchi = tuple(sorted(ts for s, ts in self.buchi if s == simbolo))
        tutte = _serie_intera(simbolo, primo, self._fine(simbolo), dati.durata_intervallo(timeframe), self.seme, buchi)
        da, a = ms(inizio), ms(fine + timedelta(days=1))
        candele = [c for c in tutte if c.ts >= da and c.close_ts < a]
        funding = [f for f in _funding_intero(simbolo, primo, self._fine(simbolo), self.seme) if da <= f[0] < a]
        return {"candele": candele, "candele_mark": list(candele), "funding": funding,
                "mesi_sotto_liquidita": [(an, me) for s, an, me in self.mesi_sotto if s == simbolo],
                "barre_tolte": {"last": 0, "mark": 0},
                # i giorni dei file 1d del last: qui un giorno per ogni giorno con candele
                "giorni_1d": len({c.ts // GIORNO for c in candele})}

    def btc(self, timeframe, inizio, fine):
        tutte = _serie_intera("BTCUSDT", "2021-01-01", self.fine_generale, dati.durata_intervallo(timeframe),
                              self.seme, ())
        return [c for c in tutte if c.ts >= ms(inizio) and c.close_ts < ms(fine + timedelta(days=1))]


@pytest.fixture(autouse=True)
def progetto(tmp_path_factory, monkeypatch):
    """Un progetto finto SENZA marcatore: ``dati.RADICE_PROGETTO`` punta qui per ogni test (in questo processo)."""
    cartella = tmp_path_factory.mktemp("progetto")
    monkeypatch.setattr(dati, "RADICE_PROGETTO", cartella)
    CHIAMATE.clear()
    gruppo.carica_modulo_variante(VARIANTE).azzera_registro()
    return cartella


def metti_marcatore(progetto: Path, simbolo: str = "GRUPPO") -> None:
    (progetto / "research" / "campagne" / "GRUPPO").mkdir(parents=True, exist_ok=True)
    (progetto / "research" / ".sessione").write_text(json.dumps({"tipo": "campagna", "simbolo": simbolo}), "utf-8")
    shutil.copyfile(MONETE_CSV_VERO, progetto / "research" / "campagne" / "GRUPPO" / "monete.csv")


def monete_di(caricatore) -> dict:
    return {s: j for j, (s, _, _) in enumerate(caricatore.monete)}


def esame(tmp_path, periodo="costruzione", caricatore=None, p=None, nome="GRUPPO-001", processi=1, **altro):
    caricatore = caricatore or CaricatoreFinto()
    altro.setdefault("monete", monete_di(caricatore))
    return gruppo.esame_di_gruppo(VARIANTE, P if p is None else p, "1d", periodo, nome, processi=processi,
                                  cartella_campagna=tmp_path / "campagna", caricatore=caricatore, **altro)


def senza_file(risultato) -> str:
    """Il risultato in JSON canonico, senza i percorsi dei file (cambiano con la cartella) e i conteggi della ripresa."""
    copia = dict(risultato)
    copia.pop("file", None)
    copia.pop("ripresa", None)
    return json.dumps(copia, sort_keys=True)


def registro():
    return gruppo.carica_modulo_variante(VARIANTE).REGISTRO


def modulo_indipendente():
    """La variante importata qui con importlib, senza ``gruppo.carica_modulo_variante``."""
    spec = importlib.util.spec_from_file_location("variante_esempio_dei_test", VARIANTE)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def parametri_dal_yaml(slippage: float, **altro) -> Parametri:
    """I ``Parametri`` scritti qui dal file, senza ``gruppo.py`` (regole.md, sezione 2, punto 8)."""
    y = yaml.safe_load(dati.PERCORSO_PARAMETRI.read_text("utf-8"))
    bot = y["fatti"]["regole_dimensione_bot"]
    return Parametri(commissione_per_lato=y["fatti"]["commissione_taker_per_lato"]["valore"], slippage_per_lato=slippage,
                     rischio_per_trade=bot["rischio_per_trade"], leva_max=bot["leva_max"],
                     modalita_margine=bot["modalita_margine_proposta"],
                     tasso_margine_mantenimento=bot["tasso_margine_mantenimento"],
                     margine_minimo_da_liquidazione=y["regole_esame"]["margine_minimo_da_liquidazione"],
                     capitale_iniziale=y["gruppo"]["capitale_per_moneta_usdt"],
                     riempimento_intrabarra=y["regole_esame"]["riempimento_intrabarra"], **altro)


def ctx_vuoto():
    return SimpleNamespace(timeframe="1d", ms_per_barra=GIORNO, btc_chiuse_entro=lambda ts: [],
                           funding_regolato_entro=lambda ts: [])


def con_filtro(fabbrica, mesi):
    """Il filtro di liquidita' scritto qui, barra per barra, con ``dati.barra_vietata_liquidita``."""
    def crea(*argomenti):
        strategia = fabbrica(*argomenti)

        def filtrata(storia, posizione):
            decisione = strategia(storia, posizione)
            if isinstance(decisione, Segnale) and dati.barra_vietata_liquidita(storia[-1].ts, mesi):
                return None
            return decisione
        return filtrata
    return crea


def righe_trade(pezzo_o_trade):
    return [dict(zip(pezzo_o_trade["trade"]["campi"], r)) for r in pezzo_o_trade["trade"]["righe"]]


def pezzi(risultato, tipo):
    """I pezzi del file di avanzamento di un esame (``fase1`` o ``sfasate``), per simbolo."""
    voci = [json.loads(r) for r in Path(risultato["file"]["avanzamento"]).read_text("utf-8").splitlines() if r.strip()]
    return {v["simbolo"]: v for v in voci if v["pezzo"] == tipo and v["impronta"] == risultato["impronte"]["esame"]}


# ---------------------------------------------------------------------------
# (1) parametri congelati
# ---------------------------------------------------------------------------


def test_regole_del_gruppo_sono_quelle_di_parametri_yaml():
    regole = gruppo.regole_del_gruppo()
    y = yaml.safe_load(dati.PERCORSO_PARAMETRI.read_text("utf-8"))
    g = y["gruppo"]
    assert regole["trade_minimi"] == {"costruzione": 700, "validazione": 300, "vault": 300} == g["trade_minimi"]
    assert regole["quota_massima_moneta"] == 0.10 == g["quota_massima_moneta"]
    assert regole["simulazioni_baseline_casuale"] == 200 and regole["passo_semi"] == 1000
    assert regole["sfasamenti_pavimento"] == 200 and regole["fittizie_vault"] == 1000
    assert regole["margine_sfasamento_giorni"] == 30 and regole["capitale_per_moneta"] == 1000.0
    assert (regole["anni_trade_minimi"], regole["trade_migliori_tolti"], regole["giorni_migliori_tolti"],
            regole["monete_migliori_tolte"]) == (100, 30, 3, 3)
    assert regole["taglio_costruzione"] == date(2023, 1, 16) and regole["inizio_validazione"] == date(2023, 1, 17)
    assert regole["asticella_q"] == 0.10 and regole["numero_monete"] == 80
    assert (regole["bootstrap_ricampionamenti"], regole["bootstrap_seme"]) == (2000, 0)
    assert (regole["pf_minimo_vault"], regole["percentile_caso_vault"]) == (1.10, 90)
    assert regole["impronta"] == hashlib.sha256(dati.PERCORSO_PARAMETRI.read_bytes()).hexdigest()


def test_parametri_moneta_dal_yaml_e_dalla_scheda():
    assert gruppo.parametri_moneta(0.0005) == parametri_dal_yaml(0.0005)
    doppi = gruppo.parametri_moneta(0.001, moltiplicatore_costi=2, ritardo_barre=1, riempimento_intrabarra="target_prima")
    assert doppi == dataclasses.replace(parametri_dal_yaml(0.001), moltiplicatore_costi=2.0, ritardo_barre=1,
                                        riempimento_intrabarra="target_prima")
    assert (doppi.capitale_iniziale, doppi.leva_max, doppi.modalita_margine) == (1000.0, 2.0, "isolated")
    with pytest.raises(ValueError):
        gruppo.parametri_moneta(0.0005, riempimento_intrabarra="a_caso")
    with pytest.raises(ValueError):
        gruppo.parametri_moneta(0.0005, ritardo_barre=-1)


# ---------------------------------------------------------------------------
# (2) contratto, contesto, niente futuro
# ---------------------------------------------------------------------------


def test_contesto_senza_simbolo_e_senza_futuro():
    btc = [Candela(k * GIORNO, 1, 2, 0.5, 1.5, 1, k * GIORNO + GIORNO - 1) for k in range(10)]
    funding = [(k * GIORNO // 3, 0.0001) for k in range(30)]
    orologio = gruppo._Orologio()
    ctx = gruppo._crea_contesto("1d", GIORNO, btc, funding, orologio)
    assert set(gruppo.Contesto.__slots__) == {"timeframe", "ms_per_barra", "btc_chiuse_entro", "funding_regolato_entro"}
    with pytest.raises(AttributeError):
        ctx.simbolo = "AAAUSDT"
    with pytest.raises(AttributeError):
        ctx.timeframe = "1h"
    # prima di ogni barra: niente, nemmeno sotto la vista
    assert len(ctx.btc_chiuse_entro(10 ** 15)) == 0 and len(ctx.funding_regolato_entro(10 ** 15)._base) == 0
    orologio.adesso = btc[4].close_ts
    vista = ctx.btc_chiuse_entro(10 ** 15)
    assert len(vista) == 5 and vista[-1] == btc[4] and len(vista._base) == 5
    assert len(ctx.btc_chiuse_entro(btc[2].close_ts)) == 3 and len(ctx.btc_chiuse_entro(btc[2].close_ts - 1)) == 2
    assert [t for t, _ in ctx.funding_regolato_entro(10 ** 15)] == [t for t, _ in funding if t <= btc[4].close_ts]
    with pytest.raises(IndexError):
        vista[5]
    # un'esecuzione nuova riparte da capo: la lista sotto la vista si accorcia
    orologio.adesso = btc[1].close_ts
    assert len(ctx.btc_chiuse_entro(10 ** 15)) == 2 and len(ctx.btc_chiuse_entro(10 ** 15)._base) == 2
    with pytest.raises(TypeError):
        ctx.btc_chiuse_entro(1.5)


def test_contratto_e_modulo_per_impronta(tmp_path):
    rotto = tmp_path / "rotto.py"
    rotto.write_text("def crea_variante(ctx, p):\n    return lambda: None\n", "utf-8")
    with pytest.raises(gruppo.ContrattoNonRispettato, match="crea_a"):
        gruppo.carica_modulo_variante(rotto)
    buono = tmp_path / "buono.py"
    buono.write_bytes(VARIANTE.read_bytes())
    impronta = hashlib.sha256(buono.read_bytes()).hexdigest()
    assert gruppo.carica_modulo_variante(buono, impronta) is gruppo.carica_modulo_variante(buono)
    with pytest.raises(RuntimeError, match="cambiato"):
        gruppo.carica_modulo_variante(buono, "0" * 64)


def test_una_variante_che_chiede_il_futuro_non_vede_nulla(tmp_path):
    p = dict(P, sonda=True, registra_ingressi=False)
    conta = gruppo.conta_trade_di_gruppo(VARIANTE, p, "1d", processi=1, monete=monete_di(CaricatoreFinto()),
                                         caricatore=CaricatoreFinto())
    assert conta["trade_stimati"] > 0
    esame(tmp_path, "validazione", p=p)
    sonde = registro()["sonde"]
    assert sonde["violazioni"] == 0
    assert sonde["creazioni_non_vuote"] == 0 and sonde["creazioni"] > 0
    # la prova non e' vuota: BTC e funding si vedono, fino ad adesso
    assert sonde["chiamate"] > 10_000 and sonde["non_vuote_btc"] > 10_000 and sonde["non_vuote_funding"] > 10_000


# ---------------------------------------------------------------------------
# (3) una moneta sola (j = 0) = il percorso delle campagne singole
# ---------------------------------------------------------------------------


def _percorso_singolo(caricatore, simbolo, periodo, p, periodi):
    """Il percorso delle campagne singole su una moneta, scritto qui con motore e statistica, senza gruppo.py."""
    date_m = periodi["monete"][simbolo]
    fine = periodi["fine_costruzione"] if periodo == "costruzione" else periodi["fine_validazione"]
    serie = caricatore.serie(simbolo, "1d", date_m["inizio"], fine)
    candele, mark, funding, mesi = serie["candele"], serie["candele_mark"], serie["funding"], serie["mesi_sotto_liquidita"]
    par = parametri_dal_yaml(caricatore.scheda(simbolo)["slippage_per_lato"])
    mod = modulo_indipendente()
    q = dict(p, registra_ingressi=False)
    crea_v = con_filtro(mod.crea_variante(ctx_vuoto(), q), mesi)
    crea_a = con_filtro(mod.crea_a(ctx_vuoto(), q), mesi)
    inizio_c = None if periodo == "costruzione" else periodi["inizio_validazione_ts"]
    nel = (lambda t: True) if inizio_c is None else (lambda t: t.ts_entrata >= inizio_c)
    out = {"candele": candele, "par": par}
    if periodo == "costruzione":
        out["conta"] = motore.conta_trade(candele, crea_v, periodi["fine_costruzione_ts"], par, None, mark, funding)
    out["trade"] = [t for t in motore.esegui(candele, None, mark, funding, crea_v(), par).trades if nel(t)]
    trade_a = [t for t in motore.esegui(candele, None, mark, funding, crea_a(), par).trades if nel(t)]
    out["trade_a"] = trade_a
    out["base_a"] = statistica.baseline_da_trade(
        [t.r for t in trade_a], statistica.lunghezza_blocco([t.ts_entrata for t in trade_a], [t.ts_uscita for t in trade_a]))
    vietate = list(motore.barre_vietate_segnale_non_valido(candele, mod.crea_segnale(ctx_vuoto(), q), par))
    vietate += dati.barre_vietate_liquidita(candele, mesi)
    if inizio_c is not None:
        vietate.append((0, next(i for i, c in enumerate(candele) if c.ts >= inizio_c)))
    out["base_b"] = motore.simula_baseline_casuale(
        candele, mod.crea_casuale(ctx_vuoto(), q), len(out["trade"]), motore.durata_media_barre(out["trade"], GIORNO),
        par, None, mark, funding, vietate, n_simulazioni=200, primo_seme=0)
    r = [t.r for t in out["trade"]]
    blocco = statistica.lunghezza_blocco([t.ts_entrata for t in out["trade"]], [t.ts_uscita for t in out["trade"]])
    out["blocco"] = blocco
    out["conf_a"] = statistica.contro_baseline(r, blocco, out["base_a"])
    out["conf_b"] = statistica.contro_baseline(r, blocco, out["base_b"])
    out["metriche"] = motore.calcola_metriche(motore.Risultato(out["trade"], [], 1000.0, 1000.0))
    return out


@pytest.mark.parametrize("periodo", ["costruzione", "validazione"])
def test_una_moneta_e_il_percorso_delle_campagne_singole(tmp_path, periodo):
    car = CaricatoreFinto(monete=TRE[:1])
    periodi = dati.periodi_gruppo({"AAAUSDT": date(2022, 1, 1)})
    assert periodi["monete"]["AAAUSDT"]["fine_costruzione"] == dati.periodi_campagna(date(2022, 1, 1))["fine_costruzione"]
    singolo = _percorso_singolo(car, "AAAUSDT", periodo, P, periodi)
    ris = esame(tmp_path, periodo, caricatore=car)
    if periodo == "costruzione":
        conta = gruppo.conta_trade_di_gruppo(VARIANTE, P, "1d", processi=1, monete={"AAAUSDT": 0}, caricatore=car)
        assert conta["trade_stimati"] == singolo["conta"]["trade"] == len(singolo["trade"]) == ris["metriche"]["trade"]
        assert conta["per_moneta"]["AAAUSDT"]["segnali_non_validi"] == singolo["conta"]["segnali_non_validi"]
    # gli stessi trade, nello stesso ordine
    salvati = [json.loads(r) for r in Path(ris["file"]["trade"]).read_text("utf-8").splitlines()]
    assert [(t["ts_entrata"], t["ts_uscita"], t["r"], t["pnl"]) for t in salvati] == \
        [(t.ts_entrata, t.ts_uscita, t.r, t.pnl) for t in singolo["trade"]]
    assert ris["metriche"]["r_medio"] == singolo["metriche"]["r_medio"]
    assert ris["metriche"]["profit_factor"] == singolo["metriche"]["profit_factor"]
    assert ris["blocco"] == singolo["blocco"]
    # (a): stessi numeri di baseline_da_trade (la (a) ha piu' di 3 blocchi)
    base_a = singolo["base_a"]
    assert base_a["valutabile"] and base_a["n_blocchi"] >= 3
    assert (ris["baseline_a"]["media"], ris["baseline_a"]["errore_standard"], ris["baseline_a"]["deviazione_standard"]) \
        == (base_a["media"], base_a["errore_standard"], base_a["deviazione_standard"])
    assert ris["per_moneta"]["AAAUSDT"]["a"]["media"] == base_a["media"]
    # (b): semi da 0 a 199, stessi numeri di simula_baseline_casuale
    base_b = singolo["base_b"]
    for chiave in ("media", "errore_standard", "errore_minimo_candidato", "n_simulazioni", "percentile_90"):
        assert ris["baseline_b"][chiave] == base_b[chiave], chiave
    assert ris["baseline_b"]["semi"]["primo_per_moneta"] == {"AAAUSDT": 0}
    assert ris["percentile_caso"] == statistica.percentile_del_candidato(singolo["metriche"]["r_medio"], base_b["valori"])
    # i confronti senza il pavimento delle sfasate sono quelli di contro_baseline
    for chiave_g, conf in (("baseline_a", singolo["conf_a"]), ("baseline_b", singolo["conf_b"])):
        senza = ris[chiave_g]["senza_pavimento_sfasate"]
        for k in ("t", "p_value", "netta", "valutabile", "soglia", "errore_candidato", "errore_standard"):
            assert senza[k] == conf[k], (chiave_g, k)
    # con il pavimento delle sfasate, l'errore del candidato non scende sotto nessuno dei due pavimenti
    pav = ris["pavimento_sfasate"]["pavimento"]
    assert pav > 0
    assert ris["baseline_a"]["pavimento_minimo"] == ris["baseline_b"]["pavimento_minimo"] == pav
    assert ris["baseline_b"]["errore_candidato"] == max(singolo["conf_b"]["errore_candidato"], pav)
    assert ris["baseline_b"]["errore_minimo"] == max(base_b["errore_minimo_candidato"], pav)


def test_una_moneta_con_la_a_di_pochi_trade(tmp_path):
    """La (a) con 2 trade e meno di 3 blocchi: nel gruppo e_j = max(dev_j, D) (sezione 5, punto 3, terza bozza), che con
    una moneta sola e' dev_j (D = dev_j), e il confronto si fa."""
    car = CaricatoreFinto(monete=TRE[:1])
    p = dict(P, a_ingressi_massimi=2)
    ris = esame(tmp_path, caricatore=car, p=p)
    periodi = dati.periodi_gruppo({"AAAUSDT": date(2022, 1, 1)})
    singolo = _percorso_singolo(car, "AAAUSDT", "costruzione", p, periodi)
    r_a = [t.r for t in singolo["trade_a"]]
    assert len(r_a) == 2 and singolo["base_a"]["n_blocchi"] < 3
    assert singolo["base_a"]["valutabile"] is False and singolo["conf_a"]["valutabile"] is False
    dev = float(np.std(r_a, ddof=1))  # a mano: l'errore di un trade solo (D = dev con una moneta)
    assert ris["baseline_a"]["errore_standard"] == dev
    assert ris["baseline_a"]["media"] == float(np.mean(r_a))
    assert ris["baseline_a"]["senza_pavimento_sfasate"]["valutabile"] is True
    assert ris["baseline_a"]["valutabile"] is True


# ---------------------------------------------------------------------------
# (4)-(5) due e tre monete, a mano; le sfasate
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def esame_tre(tmp_path_factory):
    """L'esame di costruzione sulle tre monete, una volta per il modulo (processi=1, ingressi registrati).

    Gli ingressi registrati dalla strategia casuale, nell'ordine: per ogni moneta (AAA, BBB, CCC: le piu' lunghe per
    prime) quelli del controllo della strategia casuale (1) e delle 200 simulazioni della (b); poi le 200 sfasate di
    ogni moneta, nello stesso ordine.
    """
    cartella = tmp_path_factory.mktemp("tre")
    modulo = gruppo.carica_modulo_variante(VARIANTE)
    modulo.azzera_registro()
    ris = esame(cartella, "costruzione")
    return {"ris": ris, "ingressi": [list(x) for x in modulo.REGISTRO["ingressi"]], "cartella": cartella}


def test_due_monete_calcolate_a_mano(tmp_path):
    car = CaricatoreFinto(monete=TRE[:2], mesi_sotto=(), buchi=())
    ris = esame(tmp_path, caricatore=car, p=dict(P, registra_ingressi=False))
    p1, p2 = pezzi(ris, "fase1"), pezzi(ris, "sfasate")
    n = {s: len(p1[s]["dati"]["trade"]["righe"]) for s in ("AAAUSDT", "BBBUSDT")}
    tot = n["AAAUSDT"] + n["BBBUSDT"]
    assert ris["metriche"]["trade"] == tot and ris["per_moneta"]["BBBUSDT"]["peso"] == n["BBBUSDT"] / tot
    w = {s: n[s] / tot for s in n}
    # (a): A = somma w_j A_j, errore = somma w_j e_j, deviazione = radice(somma w_j dev_j^2)
    a = {s: p1[s]["dati"]["a"]["base"] for s in n}
    assert all(a[s]["n_blocchi"] >= 3 for s in n)
    assert math.isclose(ris["baseline_a"]["media"], w["AAAUSDT"] * a["AAAUSDT"]["media"] + w["BBBUSDT"] * a["BBBUSDT"]["media"],
                        rel_tol=1e-12)
    assert math.isclose(ris["baseline_a"]["errore_standard"],
                        w["AAAUSDT"] * a["AAAUSDT"]["errore_standard"] + w["BBBUSDT"] * a["BBBUSDT"]["errore_standard"],
                        rel_tol=1e-12)
    assert math.isclose(ris["baseline_a"]["deviazione_standard"],
                        math.sqrt(sum(n[s] * a[s]["deviazione_standard"] ** 2 for s in n) / tot), rel_tol=1e-12)
    # (b): M(s) = somma n_j m_j(s) / somma n_j sulle monete con trade in s; semi 1000 j
    m = {s: p1[s]["dati"]["b"]["r_medio_per_seme"] for s in n}
    assert (p1["AAAUSDT"]["dati"]["b"]["primo_seme"], p1["BBBUSDT"]["dati"]["b"]["primo_seme"]) == (0, 1000)
    valori = []
    for k in range(200):
        presenti = [s for s in n if m[s][k] is not None]
        if presenti:
            valori.append(sum(n[s] * m[s][k] for s in presenti) / sum(n[s] for s in presenti))
    assert math.isclose(ris["baseline_b"]["media"], float(np.mean(valori)), rel_tol=1e-12)
    assert math.isclose(ris["baseline_b"]["errore_minimo_candidato"], float(np.std(valori, ddof=1)), rel_tol=1e-12)
    assert ris["per_moneta"]["AAAUSDT"]["b_j"] == float(np.mean([x for x in m["AAAUSDT"] if x is not None]))
    # pavimento delle sfasate: M'(s) = somma degli R / numero dei trade, poi la formula della sezione 5, punto 5
    per_s = {s: p2[s]["dati"]["per_s"] for s in n}
    numero = len(per_s["AAAUSDT"])
    mm, nn = [], []
    for k in range(numero):
        quanti = per_s["AAAUSDT"][k][0] + per_s["BBBUSDT"][k][0]
        if quanti:
            mm.append((per_s["AAAUSDT"][k][1] + per_s["BBBUSDT"][k][1]) / quanti)
            nn.append(quanti)
    mm = np.asarray(mm)
    pav = float(np.std((mm - mm.mean()) * np.sqrt(np.asarray(nn) / tot), ddof=1))
    assert math.isclose(ris["pavimento_sfasate"]["pavimento"], pav, rel_tol=1e-9)
    # blocco e confronto sui trade sommati, ordinati per uscita, simbolo, entrata
    trade = sorted([(t["ts_uscita"], s, t["ts_entrata"], t["r"]) for s in n for t in righe_trade(p1[s]["dati"])])
    r = [x[3] for x in trade]
    assert ris["metriche"]["r_medio"] == pytest.approx(float(np.mean(r)), rel=1e-12)
    blocco = statistica.lunghezza_blocco([x[2] for x in trade], [x[0] for x in trade])
    assert ris["blocco"] == blocco and ris["n_blocchi"] == tot // blocco
    base_b = {"tipo": "b", "media": ris["baseline_b"]["media"], "errore_standard": ris["baseline_b"]["errore_standard"],
              "errore_minimo_candidato": ris["baseline_b"]["errore_minimo_candidato"]}
    atteso = statistica.contro_baseline(r, blocco, base_b, pavimento_minimo=ris["pavimento_sfasate"]["pavimento"],
                                        dettagli=True)
    assert ris["baseline_b"]["pavimento_minimo"] == ris["pavimento_sfasate"]["pavimento"]
    assert ris["baseline_b"]["t"] == atteso["t"] and ris["t"] == atteso["t"]
    assert ris["p_value"] == atteso["p_value"] and ris["baseline_b"]["netta"] == atteso["netta"]
    assert ris["effetto_grappolo"] == statistica.effetto_grappolo(atteso["errore_candidato_senza_pavimento"], r)
    assert ris["quota_moneta_piu_presente"] == max(n.values()) / tot


def test_lo_sfasamento_e_lo_stesso_su_tutte_le_monete(esame_tre):
    ris, ingressi = esame_tre["ris"], esame_tre["ingressi"]
    p1, p2 = pezzi(ris, "fase1"), pezzi(ris, "sfasate")
    monete = sorted(p2)
    assert monete == ["AAAUSDT", "BBBUSDT", "CCCUSDT"]
    assert len({p2[s]["condizione"] for s in monete}) == 1  # una griglia sola
    periodi = dati.periodi_gruppo({s: date.fromisoformat(primo) for s, primo, _ in TRE})
    inizio = ms(date(2022, 1, 1))
    fine = periodi["fine_costruzione_ts"]
    L = (fine + 1 - inizio) // GIORNO
    margine = max(30, max(-(-p1[s]["dati"]["durata_massima_ms"] // GIORNO) for s in monete))
    griglia = statistica.griglia_sfasamenti(L, margine, 200)
    assert ris["pavimento_sfasate"]["L"] == L and ris["pavimento_sfasate"]["numero"] == 200
    assert ris["pavimento_sfasate"]["finestra_unione"] == [inizio, fine]
    # gli ingressi delle sfasate (registrati dalla strategia casuale) sono gli ingressi del candidato spostati di d_s,
    # in cerchio sulla finestra unione, tolti quelli fuori dalla finestra della moneta, nei buchi o vietati
    car = CaricatoreFinto()
    in_ordine = ["AAAUSDT", "BBBUSDT", "CCCUSDT"]  # le piu' lunghe per prime
    blocchi_b = 201 * len(in_ordine)  # per moneta: il controllo della strategia casuale e le 200 (b)
    for posto, s in enumerate(in_ordine):
        date_m = periodi["monete"][s]
        candele = car.serie(s, "1d", date_m["inizio"], periodi["fine_costruzione"])["candele"]
        indice = {c.ts: i for i, c in enumerate(candele)}
        mod = modulo_indipendente()
        vietate = list(motore.barre_vietate_segnale_non_valido(candele, mod.crea_segnale(ctx_vuoto(), P),
                                                               parametri_dal_yaml(car.scheda(s)["slippage_per_lato"])))
        vietate += dati.barre_vietate_liquidita(candele, [(a, m) for x, a, m in MESI_SOTTO if x == s])
        vietata = set(i for a, b in vietate for i in range(a, b)) | {len(candele) - 1}
        saltati = {"fuori_finestra": 0, "buco": 0, "vietata": 0}
        for k, d in enumerate(griglia["sfasamenti"]):
            attesi = set()
            for ts in p1[s]["dati"]["ts_segnali"]:
                nuovo = inizio + (((ts - inizio) // GIORNO + d) % L) * GIORNO
                if nuovo < date_m["inizio_ts"] or nuovo + GIORNO - 1 > fine:
                    saltati["fuori_finestra"] += 1
                elif nuovo not in indice:
                    saltati["buco"] += 1
                elif indice[nuovo] in vietata:
                    saltati["vietata"] += 1
                else:
                    attesi.add(indice[nuovo])
            assert set(ingressi[blocchi_b + posto * 200 + k]) == attesi, (s, k)
        tot = p2[s]["dati"]["saltati_totali"]
        assert {k: tot[k] for k in saltati} == saltati
        # il controllo della strategia casuale: gli ingressi alle barre di segnale dei trade del test
        assert set(ingressi[posto * 201]) == {indice[ts] for ts in p1[s]["dati"]["ts_segnali"]}
        assert p1[s]["dati"]["controllo_casuale"] == {"trade_rifatti": len(p1[s]["dati"]["ts_segnali"])}
    # i saltati si contano: ingressi + saltati prima del motore = segnali x sfasamenti
    for s in monete:
        d = p2[s]["dati"]
        assert d["ingressi_totali"] + d["saltati_totali"]["fuori_finestra"] + d["saltati_totali"]["buco"] + \
            d["saltati_totali"]["vietata"] == d["n_segnali"] * 200
        trade_sfasati = sum(x[0] for x in d["per_s"])
        assert trade_sfasati == d["ingressi_totali"] - d["saltati_totali"]["posizione_aperta"] - d["segnali_non_validi"] \
            - d["segnali_senza_barra"] - d["capitale_esaurito"]
    assert p2["CCCUSDT"]["dati"]["saltati_totali"]["buco"] > 0 and p2["AAAUSDT"]["dati"]["saltati_totali"]["vietata"] > 0


def test_risultato_completo_in_json(esame_tre):
    ris = esame_tre["ris"]

    def puro(x):
        if isinstance(x, dict):
            return all(isinstance(k, str) and puro(v) for k, v in x.items())
        if isinstance(x, list):
            return all(puro(v) for v in x)
        return x is None or type(x) in (bool, int, float, str)

    assert puro(ris)
    assert json.dumps(json.loads(json.dumps(ris)), sort_keys=True) == json.dumps(ris, sort_keys=True)
    for chiave in ("metriche", "per_moneta", "blocco", "n_blocchi", "uscite_massime_in_un_giorno", "durata_massima_ms",
                   "effetto_grappolo", "baseline_a", "baseline_b", "pavimento_sfasate", "percentile_caso",
                   "buy_and_hold_per_anno", "estremi", "stabilita", "posizioni_aperte_insieme", "candidato", "t",
                   "p_value", "liquidazione", "monete_con_trade", "quota_moneta_piu_presente", "quota_monete_sopra_b_j"):
        assert chiave in ris, chiave
    met = ris["metriche"]
    for chiave in ("profit_factor", "trade", "r_medio", "r_medio_per_anno", "r_medio_senza_30_migliori", "drawdown_max"):
        assert chiave in met, chiave
    assert set(ris["estremi"]) >= {"senza_trade_migliori", "senza_giorni_migliori", "senza_monete_migliori"}
    for chiave in ("pesi", "n_monete", "semi", "pavimento_sfasate", "t", "soglia", "netta", "valutabile",
                   "trade_per_simulazione_medio", "n_simulazioni", "quota_barre_vietate_segnale_non_valido"):
        assert chiave in ris["baseline_b"], chiave
    # i trade salvati, nell'ordine fisso
    salvati = [json.loads(r) for r in Path(ris["file"]["trade"]).read_text("utf-8").splitlines()]
    assert len(salvati) == met["trade"]
    assert [(t["ts_uscita"], t["simbolo"], t["ts_entrata"]) for t in salvati] == \
        sorted((t["ts_uscita"], t["simbolo"], t["ts_entrata"]) for t in salvati)
    assert ris["posizioni_aperte_insieme"] == motore.posizioni_aperte_insieme(salvati)
    # buy and hold pesato a mano per il primo anno
    p1 = pezzi(ris, "fase1")
    anno = sorted(ris["buy_and_hold_per_anno"])[0]
    presenti = [s for s in p1 if p1[s]["dati"]["trade"]["righe"] and anno in p1[s]["dati"]["buy_and_hold"]]
    pesi = {s: len(p1[s]["dati"]["trade"]["righe"]) for s in presenti}
    atteso = sum(pesi[s] * p1[s]["dati"]["buy_and_hold"][anno]["long"] for s in presenti) / sum(pesi.values())
    assert ris["buy_and_hold_per_anno"][anno]["long"] == pytest.approx(atteso, rel=1e-12)
    # stabilita': B ripesata sui trade dell'anno, a mano
    b_j = {s: ris["per_moneta"][s]["b_j"] for s in ris["per_moneta"]}
    for anno, voce in ris["stabilita"]["anni"].items():
        dell_anno = [t for t in salvati if datetime.fromtimestamp(t["ts_uscita"] / 1000, timezone.utc).year == int(anno)]
        assert voce["trade"] == len(dell_anno)
        attesa = sum(b_j[t["simbolo"]] for t in dell_anno) / len(dell_anno)
        assert voce["b_ripesata"] == pytest.approx(attesa, rel=1e-12)


# ---------------------------------------------------------------------------
# (6) il filtro di liquidita'
# ---------------------------------------------------------------------------


def test_il_filtro_di_liquidita_e_lo_stesso_dappertutto(esame_tre):
    ris, ingressi = esame_tre["ris"], esame_tre["ingressi"]
    car = CaricatoreFinto()
    periodi = dati.periodi_gruppo({s: date.fromisoformat(primo) for s, primo, _ in TRE})
    p1 = pezzi(ris, "fase1")
    conta = gruppo.conta_trade_di_gruppo(VARIANTE, dict(P, registra_ingressi=False), "1d", processi=1,
                                         monete=monete_di(car), caricatore=car)
    for s, _, _ in TRE:
        mesi = [(a, m) for x, a, m in MESI_SOTTO if x == s]
        trade = righe_trade(p1[s]["dati"])
        # stesso filtro in conta_trade e nel test: stessi trade
        assert conta["trade_stimati_per_moneta"][s] == len(trade)
        # nessun trade (ne' del candidato ne' della (a)) nasce da un segnale di un mese illiquido
        for t in trade:
            assert not dati.barra_vietata_liquidita(t["ts_entrata"] - GIORNO, mesi)
        candele = car.serie(s, "1d", periodi["monete"][s]["inizio"], periodi["fine_costruzione"])["candele"]
        vietate = {i for a, b in dati.barre_vietate_liquidita(candele, mesi) for i in range(a, b)}
        assert p1[s]["dati"]["vietate"]["liquidita"] == len(vietate)
        if s == "AAAUSDT":
            assert len(vietate) == 30  # settembre 2022
    # la (b) e le sfasate non entrano mai in quelle barre (registro della strategia casuale: prima il controllo e le
    # (b), poi le sfasate, nell'ordine AAA, BBB, CCC)
    for posto, s in enumerate(["AAAUSDT", "BBBUSDT", "CCCUSDT"]):
        mesi = [(a, m) for x, a, m in MESI_SOTTO if x == s]
        candele = car.serie(s, "1d", periodi["monete"][s]["inizio"], periodi["fine_costruzione"])["candele"]
        vietate = {i for a, b in dati.barre_vietate_liquidita(candele, mesi) for i in range(a, b)}
        for blocco in (ingressi[posto * 201 + 1:(posto + 1) * 201], ingressi[603 + posto * 200:603 + (posto + 1) * 200]):
            assert all(not (set(x) & vietate) for x in blocco)
    # senza il filtro la variante sarebbe entrata in settembre 2022 su AAAUSDT (il test non e' vuoto)
    mod = modulo_indipendente()
    candele = car.serie("AAAUSDT", "1d", date(2022, 1, 1), periodi["fine_costruzione"])["candele"]
    liberi = motore.esegui(candele, None, None, [], mod.crea_variante(ctx_vuoto(), P)(), parametri_dal_yaml(0.0005)).trades
    assert any(dati.barra_vietata_liquidita(t.ts_entrata - GIORNO, [(2022, 9)]) for t in liberi)


def test_il_filtro_di_liquidita_dal_disco(tmp_path):
    """Il caricatore dal disco: file 1d finti, il mese con poco volume e' sotto la soglia e nessun segnale lo usa."""
    radice = tmp_path / "research"
    monete = (("AAAUSDT", "2022-01-01", "0.0500%"), ("BBBUSDT", "2022-03-01", "0.1000%"))
    poco = (2022, 6)
    for simbolo, primo, fascia in monete:
        schede = radice / "campagne" / "GRUPPO" / "schede"
        schede.mkdir(parents=True, exist_ok=True)
        (schede / f"{simbolo}.md").write_text(
            f"| Campo | Valore |\n|---|---|\n| Simbolo | `{simbolo}` |\n| Primo mese di dati | {primo} |\n"
            f"| Fascia di slippage per lato | {fascia} |\n| Fine dell'in-sample | 2023-12-31 |\n", "utf-8")
    for simbolo, primo in [(s, p) for s, p, _ in monete] + [("BTCUSDT", "2021-01-01")]:
        candele = _serie_intera(simbolo, primo, "2023-12-31", GIORNO, 0, ())
        mesi = sorted({(dati.mese_utc(c.ts)) for c in candele})
        tipi = ("klines", "markPriceKlines") if simbolo != "BTCUSDT" else ("klines",)
        for anno, mese in mesi:
            del_mese = [c for c in candele if dati.mese_utc(c.ts) == (anno, mese)]
            volume = (1.0 if (anno, mese) == poco and simbolo == "AAAUSDT" else 1e7)
            testo = "\n".join(f"{c.ts},{c.open},{c.high},{c.low},{c.close},{volume},{c.close_ts},{volume * 5},1,0,0,0"
                              for c in del_mese)
            for tipo in tipi:
                percorso = dati.percorso_mese(simbolo, tipo, "1d", anno, mese, radice)
                percorso.parent.mkdir(parents=True, exist_ok=True)
                percorso.write_bytes(zip_in_memoria(percorso.stem + ".csv", testo))
            if simbolo != "BTCUSDT":
                f = dati.percorso_mese(simbolo, "fundingRate", None, anno, mese, radice)
                f.parent.mkdir(parents=True, exist_ok=True)
                righe = "\n".join(f"{c.ts},8,0.0001" for c in del_mese)
                f.write_bytes(zip_in_memoria(f.stem + ".csv", "calc_time,funding_interval_hours,last_funding_rate\n"
                                             + righe))
    car = gruppo.CaricatoreDisco(str(radice))
    assert car.scheda("BBBUSDT")["slippage_per_lato"] == 0.001
    serie = car.serie("AAAUSDT", "1d", date(2022, 1, 1), date(2023, 1, 1))
    assert serie["mesi_sotto_liquidita"] == [poco] and serie["barre_tolte"] == {"last": 0, "mark": 0}
    # i giorni dei file 1d del last nei mesi interi del periodo (dati.liquidita_mensile): 2022 e gennaio 2023
    assert serie["giorni_1d"] == 365 + 31
    assert car.serie("AAAUSDT", "1d", date(2021, 6, 1), date(2021, 7, 31))["giorni_1d"] == 0
    ris = gruppo.esame_di_gruppo(VARIANTE, dict(P, registra_ingressi=False), "1d", "costruzione", "GRUPPO-002",
                                 processi=1, radice=radice, monete=["AAAUSDT", "BBBUSDT"])
    assert Path(ris["file"]["trade"]).parent == radice / "campagne" / "GRUPPO" / "trade"
    assert ris["per_moneta"]["AAAUSDT"]["mesi_sotto_liquidita"] == 1
    assert ris["per_moneta"]["AAAUSDT"]["barre_vietate"]["liquidita"] == 30
    salvati = [json.loads(r) for r in Path(ris["file"]["trade"]).read_text("utf-8").splitlines()]
    assert all(not dati.barra_vietata_liquidita(t["ts_entrata"] - GIORNO, [poco]) for t in salvati
               if t["simbolo"] == "AAAUSDT")
    assert ris["metriche"]["trade"] > 0


# ---------------------------------------------------------------------------
# (7) ingressi_placebo, marcatore, via libera
# ---------------------------------------------------------------------------


def test_ingressi_placebo_danno_gli_stessi_numeri_della_variante(tmp_path, esame_tre):
    car = CaricatoreFinto()
    periodi = dati.periodi_gruppo({s: date.fromisoformat(primo) for s, primo, _ in TRE})
    mod = modulo_indipendente()
    placebo = {}
    for s, _, _ in TRE:
        candele = car.serie(s, "1d", periodi["monete"][s]["inizio"], periodi["fine_costruzione"])["candele"]
        placebo[s] = [candele[i].ts for i in mod.barre_di_rottura(candele, P)]
    con_placebo = json.loads(json.dumps(esame(tmp_path, ingressi_placebo=placebo)))
    come_variante = json.loads(json.dumps(esame_tre["ris"]))
    assert con_placebo["ingressi"]["tipo"] == "placebo"
    assert {s: v["ingressi_dati"]["senza_barra"] for s, v in con_placebo["per_moneta"].items()} == \
        {"AAAUSDT": 0, "BBBUSDT": 0, "CCCUSDT": 0}
    for chiave in ("ingressi", "impronte", "file"):
        con_placebo.pop(chiave)
        come_variante.pop(chiave)
    for risultato in (con_placebo, come_variante):
        for voce in risultato["per_moneta"].values():
            voce.pop("ingressi_dati")
    assert json.dumps(con_placebo, sort_keys=True) == json.dumps(come_variante, sort_keys=True)
    conta = gruppo.conta_trade_di_gruppo(VARIANTE, P, "1d", processi=1, monete=monete_di(car), caricatore=car,
                                         ingressi_placebo=placebo)
    assert conta["trade_stimati"] == esame_tre["ris"]["metriche"]["trade"]


def test_con_il_marcatore_ingressi_placebo_si_rifiuta(tmp_path, progetto):
    metti_marcatore(progetto)
    # con l'elenco e il caricatore ufficiali (gli altri argomenti dei test si rifiutano a parte)
    with pytest.raises(dati.VietatoInCampagna, match="ingressi_placebo"):
        gruppo.esame_di_gruppo(VARIANTE, P, "1d", "costruzione", "GRUPPO-005", processi=1, cartella_campagna=tmp_path,
                               ingressi_placebo={"AAVEUSDT": []})
    with pytest.raises(dati.VietatoInCampagna, match="ingressi_placebo"):
        gruppo.conta_trade_di_gruppo(VARIANTE, P, "1d", processi=1, ingressi_placebo={"AAVEUSDT": []})
    assert not (tmp_path / "avanzamento").exists() and not (tmp_path / "trade").exists()


def _scrivi_via_libera(progetto: Path, impronte: dict, formato="sha256sum") -> Path:
    righe = ["esito: l'esame di gruppo regge (regole.md, sezione 11)", ""]
    for nome, impronta in impronte.items():
        righe.append(f"{impronta}  {nome}" if formato == "sha256sum" else f"{nome} {impronta}")
    percorso = progetto / "research" / "campagne" / "GRUPPO" / "via_libera_validazione.md"
    percorso.parent.mkdir(parents=True, exist_ok=True)
    percorso.write_text("\n".join(righe) + "\n", "utf-8")
    return percorso


def _impronte_vere() -> dict:
    file = {"research/src/gruppo.py": gruppo.__file__, "research/src/statistica.py": statistica.__file__,
            "research/src/motore.py": motore.__file__, "research/src/dati.py": dati.__file__,
            "research/config/parametri.yaml": dati.PERCORSO_PARAMETRI}
    return {nome: hashlib.sha256(Path(p).read_bytes()).hexdigest() for nome, p in file.items()}


def test_via_libera_con_il_marcatore(tmp_path, progetto):
    metti_marcatore(progetto)
    car = CaricatoreFinto(monete=TRE[:2])
    fuori = tmp_path / "altrove"  # una cartella di uscita fuori da campagne/GRUPPO/: il controllo resta
    # manca il file
    with pytest.raises(gruppo.ViaLiberaNonValida, match="manca"):
        gruppo.esame_di_gruppo(VARIANTE, P, "1d", "validazione", "GRUPPO-003", processi=1, cartella_campagna=fuori,
                               caricatore=car, monete=monete_di(car))
    assert CHIAMATE == []  # rifiutato prima di toccare i dati
    vere = _impronte_vere()
    # un'impronta diversa
    _scrivi_via_libera(progetto, dict(vere, **{"research/src/motore.py": "0" * 64}))
    with pytest.raises(gruppo.ViaLiberaNonValida, match="motore.py"):
        gruppo.esame_di_gruppo(VARIANTE, P, "1d", "validazione", "GRUPPO-003", processi=1, cartella_campagna=fuori,
                               caricatore=car, monete=monete_di(car))
    # meno di cinque impronte
    _scrivi_via_libera(progetto, {k: v for k, v in vere.items() if k != "research/config/parametri.yaml"})
    with pytest.raises(gruppo.ViaLiberaNonValida, match="parametri.yaml"):
        gruppo.esame_di_gruppo(VARIANTE, P, "1d", "validazione", "GRUPPO-003", processi=1, cartella_campagna=fuori,
                               caricatore=car, monete=monete_di(car))
    assert CHIAMATE == []
    # un via libera giusto nella cartella di uscita non conta: conta solo quello della radice del progetto
    fuori.mkdir(parents=True, exist_ok=True)
    (fuori / "via_libera_validazione.md").write_text(
        "\n".join(f"{v}  {k}" for k, v in vere.items()) + "\n", "utf-8")
    with pytest.raises(gruppo.ViaLiberaNonValida, match="parametri.yaml"):
        gruppo.esame_di_gruppo(VARIANTE, P, "1d", "validazione", "GRUPPO-003", processi=1, cartella_campagna=fuori,
                               caricatore=car, monete=monete_di(car))
    # le cinque impronte giuste: il controllo passa (poi, in campagna, gli argomenti dei test si rifiutano: le
    # monete e il caricatore sono quelli ufficiali, test a parte)
    _scrivi_via_libera(progetto, vere)
    assert gruppo.controlla_via_libera() == vere
    with pytest.raises(dati.VietatoInCampagna, match="monete"):
        gruppo.esame_di_gruppo(VARIANTE, P, "1d", "validazione", "GRUPPO-003", processi=1, cartella_campagna=fuori,
                               caricatore=car, monete=monete_di(car))
    # anche nella forma «percorso impronta»
    assert gruppo.controlla_via_libera(_scrivi_via_libera(progetto, vere, formato="inverso")) == vere
    assert CHIAMATE == []


def test_in_campagna_monete_caricatore_e_radice_sono_quelli_ufficiali(tmp_path, progetto):
    """Con un marcatore di campagna si esamina solo l'elenco ufficiale, con i dati del progetto (regole.md, sezione 0, punto 4)."""
    metti_marcatore(progetto)
    car = CaricatoreFinto()
    for chiamata in (
        lambda: gruppo.esame_di_gruppo(VARIANTE, P, "1d", "costruzione", "GRUPPO-004", processi=1,
                                       cartella_campagna=tmp_path, caricatore=car),
        lambda: gruppo.esame_di_gruppo(VARIANTE, P, "1d", "costruzione", "GRUPPO-004", processi=1,
                                       cartella_campagna=tmp_path, monete=["AAAUSDT", "BBBUSDT"]),
        lambda: gruppo.conta_trade_di_gruppo(VARIANTE, P, "1d", processi=1, radice=tmp_path),
        lambda: gruppo.controllo_positivo(VARIANTE, P, "1d", "long", processi=1, cartella_campagna=tmp_path,
                                          caricatore=car, monete=monete_di(car)),
        lambda: gruppo.esame_vault(VARIANTE, P, "1d", cartella=tmp_path / "vault", processi=1, caricatore=car,
                                   monete=monete_di(car)),
        lambda: gruppo.esame_vault(VARIANTE, P, "1d", cartella=tmp_path / "vault", processi=1),
    ):
        with pytest.raises(dati.VietatoInCampagna):
            chiamata()
    assert CHIAMATE == [] and not (tmp_path / "vault").exists()
    # fuori campagna gli stessi argomenti vanno bene
    (progetto / "research" / ".sessione").unlink()
    assert gruppo.conta_trade_di_gruppo(VARIANTE, dict(P, registra_ingressi=False), "1d", processi=1,
                                        caricatore=CaricatoreFinto(monete=TRE[:1]), monete=["AAAUSDT"])["trade_stimati"] > 0


def test_senza_marcatore_la_validazione_parte_senza_via_libera(tmp_path, progetto):
    assert not (progetto / "research" / "campagne" / "GRUPPO" / "via_libera_validazione.md").exists()
    ris = esame(tmp_path, "validazione", caricatore=CaricatoreFinto(monete=TRE[:2]), p=dict(P, registra_ingressi=False))
    periodi = dati.periodi_gruppo({s: date.fromisoformat(primo) for s, primo, _ in TRE[:2]})
    salvati = [json.loads(r) for r in Path(ris["file"]["trade"]).read_text("utf-8").splitlines()]
    assert salvati and all(t["ts_entrata"] >= periodi["inizio_validazione_ts"] for t in salvati)
    assert ris["validazione"]["p_value_asticella"] == 1.0  # meno di 300 trade
    giorni = periodi["giorni_validazione"]
    assert ris["pavimento_sfasate"]["L"] == giorni and ris["pavimento_sfasate"]["tutti_gli_interi"] is True
    assert ris["pavimento_sfasate"]["numero"] == giorni - 2 * 30 + 1
    p1 = pezzi(ris, "fase1")
    for s in p1:
        assert p1[s]["dati"]["vietate"]["prima_del_periodo"] == p1[s]["dati"]["barre"] - p1[s]["dati"]["barre_nel_periodo"]


# ---------------------------------------------------------------------------
# (8) ripresa, ordine delle monete, numero di processi
# ---------------------------------------------------------------------------


def test_ripresa_da_un_avanzamento_interrotto(tmp_path):
    q = dict(P, registra_ingressi=False)
    intero = esame(tmp_path / "intero", p=q)
    # l'esame si ferma sulla terza moneta (CCCUSDT, l'ultima: le piu' lunghe per prime)
    with pytest.raises(gruppo.ErroreDiMoneta, match="guasto simulato"):
        esame(tmp_path / "ripreso", p=q, caricatore=CaricatoreFinto(guasto="CCCUSDT"))
    file = tmp_path / "ripreso" / "campagna" / "avanzamento" / "GRUPPO-001_costruzione.jsonl"
    assert [json.loads(r)["simbolo"] for r in file.read_text("utf-8").splitlines()] == ["AAAUSDT", "BBBUSDT"]
    # una riga interrotta a meta' si ignora
    with open(file, "ab") as flusso:
        flusso.write(b'{"formato": 1, "impronta": "tron')
    CHIAMATE.clear()
    ripreso = esame(tmp_path / "ripreso", p=q)
    assert senza_file(ripreso) == senza_file(intero)
    # i pezzi gia' fatti non si rifanno: ogni moneta ricarica i suoi dati (per controllarne l'impronta), ma si
    # calcolano solo la fase 1 di CCCUSDT e le sfasate di tutte
    assert sorted(c[0] for c in CHIAMATE) == ["AAAUSDT", "AAAUSDT", "BBBUSDT", "BBBUSDT", "CCCUSDT", "CCCUSDT"]
    assert ripreso["ripresa"] == {"pezzi_ripresi": 2, "pezzi_calcolati": 4, "righe_di_altre_impronte": 0,
                                  "righe_illeggibili": 1}
    assert intero["ripresa"]["pezzi_ripresi"] == 0 and intero["ripresa"]["pezzi_calcolati"] == 6
    righe = file.read_text("utf-8").split("\n")
    assert righe[2] == '{"formato": 1, "impronta": "tron'  # la riga rotta resta, chiusa da un a capo
    # una ripresa con i pezzi tutti fatti non calcola nulla e non aggiunge righe
    prima = len(file.read_text("utf-8").splitlines())
    tutto = esame(tmp_path / "ripreso", p=q)
    assert senza_file(tutto) == senza_file(intero)
    assert tutto["ripresa"]["pezzi_ripresi"] == 6 and tutto["ripresa"]["pezzi_calcolati"] == 0
    assert len(file.read_text("utf-8").splitlines()) == prima
    # un'altra versione (p diversi) non riusa nessun pezzo, e non cancella le righe di prima
    CHIAMATE.clear()
    altra = esame(tmp_path / "ripreso", p=dict(q, durata=6))
    assert len(CHIAMATE) == 6 and len(file.read_text("utf-8").splitlines()) == prima + 6
    assert altra["ripresa"]["pezzi_ripresi"] == 0 and altra["ripresa"]["righe_di_altre_impronte"] == 6


def test_esito_uguale_con_1_o_4_processi_e_con_ogni_ordine_delle_monete(tmp_path, esame_tre):
    q = dict(P, registra_ingressi=False)
    uno = esame(tmp_path / "uno", p=q)
    quattro = esame(tmp_path / "quattro", p=q, processi=4, monete={"CCCUSDT": 2, "AAAUSDT": 0, "BBBUSDT": 1})
    rovescio = CaricatoreFinto(monete=tuple(reversed(TRE)))
    tre = esame(tmp_path / "tre", p=q, processi=3, caricatore=rovescio, monete={"BBBUSDT": 1, "CCCUSDT": 2, "AAAUSDT": 0})
    assert senza_file(uno) == senza_file(quattro) == senza_file(tre)
    assert uno["metriche"]["trade"] == esame_tre["ris"]["metriche"]["trade"]
    conta_1 = gruppo.conta_trade_di_gruppo(VARIANTE, q, "1d", processi=1, monete=monete_di(rovescio), caricatore=rovescio)
    conta_4 = gruppo.conta_trade_di_gruppo(VARIANTE, q, "1d", processi=4, monete=monete_di(rovescio),
                                           caricatore=CaricatoreFinto())
    assert json.dumps(conta_1, sort_keys=True) == json.dumps(conta_4, sort_keys=True)


def test_la_posizione_j_cambia_i_semi(tmp_path):
    q = dict(P, registra_ingressi=False)
    car = CaricatoreFinto(monete=TRE[:2])
    a = esame(tmp_path / "a", p=q, caricatore=car, monete={"AAAUSDT": 0, "BBBUSDT": 1})
    b = esame(tmp_path / "b", p=q, caricatore=car, monete={"AAAUSDT": 5, "BBBUSDT": 1})
    assert a["baseline_b"]["semi"]["primo_per_moneta"] == {"AAAUSDT": 0, "BBBUSDT": 1000}
    assert b["baseline_b"]["semi"]["primo_per_moneta"]["AAAUSDT"] == 5000
    assert a["baseline_b"]["media"] != b["baseline_b"]["media"]
    assert a["metriche"] == b["metriche"]


def test_il_margine_segue_la_posizione_piu_lunga(tmp_path):
    """Margine = il piu' alto fra 30 giorni e la durata massima dei trade, in barre per eccesso (sezione 5, punto 5)."""
    car = CaricatoreFinto(monete=TRE[:1])
    ris = esame(tmp_path, caricatore=car, p={"n": 5, "stop": 0.5, "target": 3.0, "durata": 45})
    assert ris["durata_massima_barre"] == 45 == ris["pavimento_sfasate"]["durata_massima_barre"]
    assert ris["pavimento_sfasate"]["margine"] == 45 == ris["pavimento_sfasate"]["margine_richiesto"]
    L = ris["pavimento_sfasate"]["L"]
    assert pezzi(ris, "sfasate")["AAAUSDT"]["condizione"]  # la griglia: da 45 a L - 45
    griglia = statistica.griglia_sfasamenti(L, 45, 200)
    assert griglia["sfasamenti"][0] == 45 and griglia["sfasamenti"][-1] == L - 45


def test_costi_doppi_su_test_b_e_sfasate(tmp_path):
    car = CaricatoreFinto(monete=TRE[:2])
    q = dict(P, registra_ingressi=False)
    normale = esame(tmp_path / "1", caricatore=car, p=q)
    doppi = esame(tmp_path / "2", caricatore=car, p=q, moltiplicatore_costi=2, con_baseline_a=False)
    assert doppi["opzioni"] == {"moltiplicatore_costi": 2.0, "ritardo_barre": 0, "riempimento_intrabarra": "stop_prima",
                                "con_baseline_a": False}
    t1 = [json.loads(r) for r in Path(normale["file"]["trade"]).read_text("utf-8").splitlines()]
    t2 = [json.loads(r) for r in Path(doppi["file"]["trade"]).read_text("utf-8").splitlines()]
    assert [(t["ts_entrata"], t["simbolo"]) for t in t1] == [(t["ts_entrata"], t["simbolo"]) for t in t2]
    assert all(b["r"] < a["r"] for a, b in zip(t1, t2))
    assert doppi["baseline_b"]["media"] < normale["baseline_b"]["media"]
    assert doppi["pavimento_sfasate"]["media_r_sfasate"] < normale["pavimento_sfasate"]["media_r_sfasate"]
    assert doppi["baseline_a"] is None and doppi["candidato"] is None
    assert doppi["impronte"]["esame"] != normale["impronte"]["esame"]


# ---------------------------------------------------------------------------
# conta_trade_di_gruppo: somma, quota, scarto, stima di validazione
# ---------------------------------------------------------------------------


def test_conta_trade_di_gruppo_a_mano():
    car = CaricatoreFinto()
    conta = gruppo.conta_trade_di_gruppo(VARIANTE, dict(P, registra_ingressi=False), "1d", processi=1,
                                         monete=monete_di(car), caricatore=car)
    per = conta["trade_stimati_per_moneta"]
    tot = sum(per.values())
    assert conta["trade_stimati"] == tot and conta["monete_con_trade"] == 3
    assert conta["quota_moneta_piu_presente"] == max(per.values()) / tot
    assert conta["esito"] == "scarto"  # sotto 700, e con 3 monete ognuna ha piu' del 10%
    assert len(conta["motivi"]) == 2
    periodi = dati.periodi_gruppo({s: date.fromisoformat(primo) for s, primo, _ in TRE})
    stima = sum(per[s] * periodi["giorni_validazione"] / periodi["monete"][s]["giorni_costruzione"] for s in per)
    assert conta["stima_trade_validazione"] == pytest.approx(stima, rel=1e-12)


def test_nessun_trade(tmp_path):
    ris = esame(tmp_path, caricatore=CaricatoreFinto(monete=TRE[:1]), p=dict(P, n=10_000, registra_ingressi=False))
    assert ris["metriche"]["trade"] == 0 and ris["valutabile"] is False and ris["t"] == -math.inf
    assert ris["candidato"] is False and Path(ris["file"]["trade"]).read_text("utf-8") == ""


# ---------------------------------------------------------------------------
# (9) controllo positivo, vault, asticella
# ---------------------------------------------------------------------------


def test_controllo_positivo_passa_senza_ritardo_e_crolla_con_il_ritardo(tmp_path):
    car = CaricatoreFinto(monete=TRE[:2])
    q = {"n": 5, "stop": 0.2, "target": 1.0, "durata": 1}
    ris = gruppo.controllo_positivo(VARIANTE, q, "1d", "long", processi=1, cartella_campagna=tmp_path,
                                    caricatore=car, monete=monete_di(car))
    assert ris["passa"] is True
    assert ris["condizioni"] == {"batte_nettamente_a_e_b_senza_ritardo": True,
                                 "t_con_ritardo_sotto_meta_di_quello_senza": True}
    assert ris["t_senza_ritardo"] > 2 and ris["t_con_ritardo"] < ris["t_senza_ritardo"] / 2
    assert ris["esami"]["con_ritardo"]["opzioni"]["ritardo_barre"] == 1
    assert ris["esami"]["senza_ritardo"]["ingressi"] == {"tipo": "guarda_avanti", "direzione": "long"}
    # gli ingressi guardano avanti solo in gruppo.py: la variante della sessione non vede barre non chiuse
    corto = gruppo.controllo_positivo(VARIANTE, dict(q, direzione="short"), "1d", "short", processi=1,
                                      cartella_campagna=tmp_path, caricatore=car, monete=monete_di(car), id="cp-short")
    assert corto["passa"] is True
    with pytest.raises(ValueError, match="direzione"):
        gruppo.controllo_positivo(VARIANTE, q, "1d", "short", processi=1, cartella_campagna=tmp_path, caricatore=car,
                                  monete=monete_di(car), id="cp-sbagliato")


#: le quattro monete sintetiche del vault: BBBUSDT smette di avere candele il 2025-06-30, AAAUSDT ha marzo 2025
#: sotto la liquidita'
VAULT_MONETE = (("AAAUSDT", "2023-07-01", 0.0005), ("BBBUSDT", "2023-09-01", 0.001), ("CCCUSDT", "2023-07-01", 0.0005),
                ("DDDUSDT", "2023-07-01", 0.001))
VAULT_ARGOMENTI = dict(mesi_sotto=(("AAAUSDT", 2025, 3),), buchi=(), fine_dati=(("BBBUSDT", "2025-06-30"),),
                       fine_generale="2026-09-30")
VAULT_J = {"AAAUSDT": 0, "BBBUSDT": 1, "CCCUSDT": 2, "DDDUSDT": 3}


def vault(cartella, caricatore=None, q=None, processi=1, **altro):
    caricatore = caricatore or CaricatoreFinto(monete=VAULT_MONETE, **VAULT_ARGOMENTI)
    q = q or {"n": 3, "stop": 0.06, "target": 0.09, "durata": 2}
    return gruppo.esame_vault(VARIANTE, q, "1d", cartella=cartella, processi=processi, monete=VAULT_J,
                              caricatore=caricatore, **altro)


def test_esame_vault(tmp_path):
    car = CaricatoreFinto(monete=VAULT_MONETE, **VAULT_ARGOMENTI)
    q = {"n": 3, "stop": 0.06, "target": 0.09, "durata": 2, "registra_ingressi": True}
    ris = vault(tmp_path / "coordinamento", car, q, file_trade=tmp_path / "vault.jsonl")
    salvati = [json.loads(r) for r in (tmp_path / "vault.jsonl").read_text("utf-8").splitlines()]
    assert len(salvati) == ris["metriche"]["trade"] >= 300 and all(t["ts_entrata"] >= ms(date(2024, 1, 1)) for t in salvati)
    assert ris["monete_che_smettono"] == {"BBBUSDT": "2025-06-30"}
    assert max(t["ts_uscita"] for t in salvati if t["simbolo"] == "BBBUSDT") < ms(date(2025, 7, 1))
    # a 1d le sfasate sono meno di 1.000: tutti gli interi fra il margine e L - margine
    sf = ris["sfasate"]
    assert sf["L"] == 1004 and sf["tutti_gli_interi"] is True and sf["sfasate"] == 1004 - 2 * sf["margine"] + 1
    # il criterio e il tasso del caso, rifatti qui dai numeri riportati
    r_medi = [d["r_medio"] for d in sf["dettaglio"] if d["n_trade"] > 0]
    p90 = statistica.percentile(r_medi, 90)
    assert ris["percentile_90_sfasate"] == p90
    metriche = motore.metriche_di_gruppo({s: [t for t in salvati if t["simbolo"] == s]
                                          for s in ("AAAUSDT", "BBBUSDT", "CCCUSDT", "DDDUSDT")}, 4, 1000.0, 30)
    assert ris["criterio"] == json.loads(json.dumps(statistica.criterio_vault(metriche, p90, 300, 1.10)))
    passate = [d for d in sf["dettaglio"] if d["n_trade"] > 0 and d["profit_factor"] >= 1.10
               and d["rendimento_totale"] > 0 and d["r_medio"] > p90]
    assert sf["passate"] == len(passate) and ris["tasso_del_caso"] == len(passate) / sf["sfasate"]
    assert 0 < ris["tasso_del_caso"] < 0.5
    # il filtro di liquidita' vale nel vault: nessun ingresso da segnali di marzo 2025 su AAAUSDT, ne' della variante
    # ne' della (b) ne' delle sfasate
    assert all(not dati.barra_vietata_liquidita(t["ts_entrata"] - GIORNO, [(2025, 3)]) for t in salvati
               if t["simbolo"] == "AAAUSDT")
    candele = car.serie("AAAUSDT", "1d", date(2023, 7, 1), date(2026, 9, 30))["candele"]
    vietate = {i for a, b in dati.barre_vietate_liquidita(candele, [(2025, 3)]) for i in range(a, b)}
    blocchi = registro()["ingressi"]
    assert len(blocchi) == 4 * 201 + 4 * sf["sfasate"]  # per moneta il controllo della casuale e 200 (b); le sfasate
    for blocco in blocchi[1:201] + blocchi[804:804 + sf["sfasate"]]:  # AAAUSDT, la prima (piu' lunga, poi in ordine)
        assert not (set(blocco) & vietate)
    assert "t" in ris["baseline_b"] and ris["baseline_b"]["pavimento_sfasate"] is not None
    # la prova sulle monete, solo da riportare (regole.md, sezione 9, punto 5): estremi_di_gruppo con B e le b_j
    # della (b) del vault, sui trade sommati
    assert ris["baseline_b"]["valutabile"] is True
    attesi = statistica.estremi_di_gruppo(
        [statistica.TradeDiGruppo(t["simbolo"], t["ts_entrata"], t["ts_uscita"], t["r"], t["pnl"]) for t in salvati],
        ris["baseline_b"]["media"], ris["baseline_b"]["b_per_moneta"], 30, 3, 3)
    assert ris["estremi"] == json.loads(json.dumps(attesi))
    assert "passa" not in ris["estremi"] and ris["passa"] == ris["criterio"]["esito"]
    # il file di avanzamento: una riga per pezzo, le sfasate con le quattro somme per s e non i trade
    righe = [json.loads(r) for r in (tmp_path / "coordinamento" / "avanzamento" / "vault_1d.jsonl").read_text(
        "utf-8").splitlines()]
    assert ris["file"]["avanzamento"] == str(tmp_path / "coordinamento" / "avanzamento" / "vault_1d.jsonl")
    assert sorted((r["pezzo"], r["simbolo"]) for r in righe) == sorted(
        [("fase1", s) for s in VAULT_J] + [("sfasate", s) for s in VAULT_J])
    assert {r["impronta"] for r in righe} == {ris["impronte"]["esame"]}
    for riga in righe:
        if riga["pezzo"] == "sfasate":
            assert "trade_compatti" not in riga["dati"] and "per_s" not in riga["dati"]
            somme = riga["dati"]["per_s_vault"]
            assert len(somme) == sf["sfasate"] and all(len(v) == 4 and isinstance(v[0], int) for v in somme)
    n_s = [sum(r["dati"]["per_s_vault"][k][0] for r in righe if r["pezzo"] == "sfasate") for k in range(sf["sfasate"])]
    assert n_s == [d["n_trade"] for d in sf["dettaglio"]]
    assert ris["ripresa"] == {"pezzi_ripresi": 0, "pezzi_calcolati": 8, "righe_di_altre_impronte": 0,
                              "righe_illeggibili": 0}


def test_esame_vault_a_vault_chiuso(tmp_path):
    radice = tmp_path / "research"
    schede = radice / "campagne" / "GRUPPO" / "schede"
    schede.mkdir(parents=True)
    (schede / "AAAUSDT.md").write_text(
        "| Campo | Valore |\n|---|---|\n| Simbolo | `AAAUSDT` |\n| Primo mese di dati | 2022-01-01 |\n"
        "| Fascia di slippage per lato | 0.0500% |\n| Fine dell'in-sample | 2023-12-31 |\n", "utf-8")
    with pytest.raises(gruppo.ErroreDiMoneta, match="VaultChiuso") as errore:
        gruppo.esame_vault(VARIANTE, P, "1d", cartella=tmp_path / "coordinamento", processi=1, radice=radice,
                           monete=["AAAUSDT"])
    assert isinstance(errore.value.__cause__, dati.VaultChiuso)


def test_esame_vault_vuole_una_cartella_fuori_da_campagne(tmp_path):
    """Il file di avanzamento del vault: cartella obbligatoria e fuori da research/campagne/ (regole.md, sezione 9)."""
    radice = tmp_path / "research"
    with pytest.raises(TypeError, match="cartella"):
        gruppo.esame_vault(VARIANTE, P, "1d", processi=1, radice=radice, monete=VAULT_J,
                           caricatore=CaricatoreFinto(monete=VAULT_MONETE, **VAULT_ARGOMENTI))
    for cartella in (None, radice / "campagne", radice / "campagne" / "GRUPPO" / "vault",
                     dati.RADICE_DEFAULT / "campagne" / "GRUPPO" / "vault"):
        with pytest.raises(ValueError, match="cartella"):
            vault(cartella, radice=radice)
    assert CHIAMATE == [] and not radice.exists()
    assert not (dati.RADICE_DEFAULT / "campagne" / "GRUPPO" / "vault").exists()


def test_esame_vault_vuole_file_trade_fuori_da_campagne(tmp_path):
    """Revisione avversaria: anche ``file_trade``, che tiene i trade sommati del vault, non va in research/campagne/."""
    radice = tmp_path / "research"
    for file_trade in (radice / "campagne" / "GRUPPO" / "trade" / "vault.jsonl",
                       dati.RADICE_DEFAULT / "campagne" / "GRUPPO" / "trade" / "vault_revisione.jsonl"):
        with pytest.raises(ValueError, match="file_trade .* e' sotto"):
            vault(tmp_path / "coordinamento", radice=radice, file_trade=file_trade)
        assert not file_trade.exists()
    assert CHIAMATE == [] and not radice.exists() and not (tmp_path / "coordinamento").exists()


def test_asticella_di_gruppo():
    def voce(nome, p, trade_ok=True, r_ok=True):
        return {"id": nome, "periodo": "validazione",
                "validazione": {"p_value_asticella": p, "trade_minimi_superati": trade_ok, "r_medio_positivo": r_ok}}

    esito = gruppo.asticella_di_gruppo([voce("G1", 0.01), voce("G2", 0.04, r_ok=False), voce("G3", 1.0, trade_ok=False),
                                        voce("G4", 0.5)])
    assert esito["m"] == 4 and esito["q"] == 0.10
    # BH al 10% su 4: 0.01 <= 0.025, 0.04 <= 0.05, 0.5 > 0.075, 1.0 > 0.1
    assert [c["passa_asticella"] for c in esito["candidati"]] == [True, True, False, False]
    assert [c["va_al_vault"] for c in esito["candidati"]] == [True, False, False, False]
    with pytest.raises(ValueError):
        gruppo.asticella_di_gruppo([{"periodo": "costruzione"}])


# ---------------------------------------------------------------------------
# (10) correzioni dopo la revisione degli strumenti (10 ottobre 2026)
# ---------------------------------------------------------------------------

RADICE_REPO = Path(__file__).resolve().parents[3]


@dataclasses.dataclass(frozen=True)
class CaricatoreSenzaBtc(CaricatoreFinto):
    """Il caricatore finto, ma senza le candele di BTCUSDT (i file di quel timeframe mancano)."""

    def btc(self, timeframe, inizio, fine):
        return []


@dataclasses.dataclass(frozen=True)
class CaricatoreGuastoAlleSfasate(CaricatoreFinto):
    """Il caricatore finto, ma la seconda lettura di ``guasto_alle_sfasate`` (il pezzo delle sfasate) fallisce.

    Conta le letture in ``CHIAMATE``: vale solo con ``processi=1``.
    """

    guasto_alle_sfasate: str = ""

    def serie(self, simbolo, timeframe, inizio, fine):
        if simbolo == self.guasto_alle_sfasate and any(c[0] == simbolo for c in CHIAMATE):
            raise RuntimeError("guasto simulato nelle sfasate")
        return super().serie(simbolo, timeframe, inizio, fine)


@dataclasses.dataclass(frozen=True)
class CaricatoreConDatiMancanti(CaricatoreFinto):
    """Il caricatore finto, ma a ogni moneta manca una parte dei dati della Fase 0 (``manca``)."""

    manca: str = ""

    def serie(self, simbolo, timeframe, inizio, fine):
        serie = dict(super().serie(simbolo, timeframe, inizio, fine))
        if self.manca == "candele":
            serie["candele"], serie["candele_mark"] = [], []
        elif self.manca == "funding":
            serie["funding"] = []
        elif self.manca == "giorni_1d":
            serie["giorni_1d"] = 0
        elif self.manca == "giorni_1d_assente":
            del serie["giorni_1d"]
        return serie


def _variante_modificata(tmp_path: Path, nome: str, *sostituzioni) -> Path:
    """La variante d'esempio con alcune righe cambiate, scritta in ``tmp_path``."""
    testo = VARIANTE.read_text("utf-8")
    for vecchio, nuovo in sostituzioni:
        assert testo.count(vecchio) == 1, vecchio
        testo = testo.replace(vecchio, nuovo)
    percorso = tmp_path / nome
    percorso.write_text(testo, "utf-8")
    return percorso


VARIANTE_CON_CACHE = '''
"""Una variante con uno stato AL LIVELLO DEL MODULO: la chiusura vista per ogni istante, da chi la vede per primo."""
from research.src.motore import Segnale

CHIUSURE = {}


def _segnale(chiusura):
    return Segnale("long", stop=chiusura * 0.94, target=chiusura * 1.09)


def _esce(stato, i):
    if stato["entrata"] is None:
        stato["entrata"] = i
    return "chiudi" if i - stato["entrata"] >= 2 else None


def crea_variante(ctx, p):
    def crea():
        stato = {"entrata": None}

        def strategia(storia, posizione):
            barra = storia[-1]
            CHIUSURE.setdefault(barra.ts, barra.close)
            i = len(storia) - 1
            if posizione is None:
                stato["entrata"] = None
                if i >= 5 and barra.close > sum(CHIUSURE[storia[k].ts] for k in range(i - 5, i)) / 5:
                    return _segnale(barra.close)
                return None
            return _esce(stato, i)
        return strategia
    return crea


def crea_a(ctx, p):
    return crea_variante(ctx, p)


def crea_casuale(ctx, p):
    def crea(ingressi):
        stato = {"entrata": None}

        def strategia(storia, posizione):
            i = len(storia) - 1
            if posizione is None:
                stato["entrata"] = None
                return _segnale(storia[-1].close) if i in ingressi else None
            return _esce(stato, i)
        return strategia
    return crea


def crea_segnale(ctx, p):
    def crea():
        return lambda storia: _segnale(storia[-1].close) if len(storia) > 5 else None
    return crea
'''


def test_uno_stato_al_livello_del_modulo_non_passa_da_una_moneta_all_altra(tmp_path):
    """Il modulo della variante si esegue da capo per ogni moneta (regole.md, sezione 3, punto 3; revisione, sguardo/e1d)."""
    variante = tmp_path / "variante_cache.py"
    variante.write_text(VARIANTE_CON_CACHE, "utf-8")
    car = CaricatoreFinto()
    periodi = dati.periodi_gruppo({s: date.fromisoformat(primo) for s, primo, _ in TRE})

    def conta_a_mano(moduli):
        """conta_trade moneta per moneta, nell'ordine dell'esame (le piu' lunghe per prime), con i moduli dati."""
        conti = {}
        for s, modulo in zip(["AAAUSDT", "BBBUSDT", "CCCUSDT"], moduli):
            serie = car.serie(s, "1d", periodi["monete"][s]["inizio"], periodi["fine_costruzione"])
            crea = con_filtro(modulo.crea_variante(ctx_vuoto(), {}), serie["mesi_sotto_liquidita"])
            conti[s] = motore.conta_trade(serie["candele"], crea, periodi["fine_costruzione_ts"],
                                          parametri_dal_yaml(car.scheda(s)["slippage_per_lato"]), None,
                                          serie["candele_mark"], serie["funding"])["trade"]
        return conti

    def nuovo():
        spec = importlib.util.spec_from_file_location("variante_cache_dei_test", variante)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        return modulo

    isolati = conta_a_mano([nuovo(), nuovo(), nuovo()])
    uno_solo = nuovo()
    contaminati = conta_a_mano([uno_solo, uno_solo, uno_solo])
    assert contaminati != isolati  # la prova non e' vuota: con un modulo solo BBB e CCC leggono le chiusure di AAA
    uno = gruppo.conta_trade_di_gruppo(variante, {}, "1d", processi=1, monete=monete_di(car), caricatore=car)
    tre = gruppo.conta_trade_di_gruppo(variante, {}, "1d", processi=3, monete=monete_di(car), caricatore=car)
    assert uno["trade_stimati_per_moneta"] == tre["trade_stimati_per_moneta"] == isolati
    # e due volte di fila nello stesso processo: stesso esito (il modulo in cache non si usa nei pezzi)
    assert gruppo.conta_trade_di_gruppo(variante, {}, "1d", processi=1, monete=monete_di(car),
                                        caricatore=car)["trade_stimati_per_moneta"] == isolati


@pytest.mark.parametrize("riga", ["import aiuto", "from . import aiuto", "from research.src import statistica",
                                  "import research.src.dati as d", "from research import src",
                                  "from research.src.gruppo import Contesto", "import yaml"])
def test_import_vietati_nel_modulo_della_variante(tmp_path, riga):
    """Un file di codice importato non sarebbe nell'impronta della variante (contratto, punto 1; revisione, sguardo/e6)."""
    (tmp_path / "aiuto.py").write_text("STOP = 0.06\n", "utf-8")
    variante = _variante_modificata(tmp_path, "con_import.py", ("from collections import deque\n",
                                                                 f"from collections import deque\n{riga}\n"))
    with pytest.raises(gruppo.ContrattoNonRispettato, match="import non ammessi"):
        gruppo.carica_modulo_variante(variante)
    with pytest.raises(gruppo.ContrattoNonRispettato, match="import non ammessi"):
        gruppo.conta_trade_di_gruppo(variante, P, "1d", processi=1, monete=monete_di(CaricatoreFinto()),
                                     caricatore=CaricatoreFinto())
    assert CHIAMATE == []  # prima di toccare i dati
    # anche dentro una funzione
    dentro = "def f():\n    " + riga + "\n"
    with pytest.raises(gruppo.ContrattoNonRispettato):
        gruppo.controlla_import_della_variante(dentro)


def test_import_ammessi_nel_modulo_della_variante():
    for riga in ("import math", "from collections import deque", "import numpy as np", "from numpy import random",
                 "import numpy.linalg", "from research.src.motore import Segnale", "from research.src import motore",
                 "import research.src.motore", "from __future__ import annotations", "import sys, types"):
        gruppo.controlla_import_della_variante(riga + "\n")


def test_la_strategia_casuale_deve_rifare_i_trade_del_test(tmp_path):
    """crea_casuale con un'altra uscita cambierebbe (b) e pavimento senza avviso (contratto, punto 2; revisione, sguardo/e8)."""
    sbagliata = _variante_modificata(
        tmp_path, "casuale_sbagliata.py",
        ('def crea_casuale(ctx, p):\n    durata = int(p["durata"])', 'def crea_casuale(ctx, p):\n    durata = 1'))
    car = CaricatoreFinto(monete=TRE[:2])
    with pytest.raises(gruppo.ErroreDiMoneta, match="crea_casuale") as errore:
        gruppo.esame_di_gruppo(sbagliata, dict(P, registra_ingressi=False), "1d", "costruzione", "GRUPPO-009",
                               processi=1, cartella_campagna=tmp_path / "c", caricatore=car, monete=monete_di(car))
    assert isinstance(errore.value.__cause__, gruppo.ContrattoNonRispettato)
    # anche in validazione (il controllo usa tutti i trade del test, anche quelli prima del periodo)
    with pytest.raises(gruppo.ErroreDiMoneta, match="crea_casuale"):
        gruppo.esame_di_gruppo(sbagliata, dict(P, registra_ingressi=False), "1d", "validazione", "GRUPPO-009",
                               processi=1, cartella_campagna=tmp_path / "c", caricatore=car, monete=monete_di(car))
    # la variante d'esempio lo passa, anche con il ritardo di una barra
    ris = esame(tmp_path / "giusta", caricatore=car, p=dict(P, registra_ingressi=False), ritardo_barre=1,
                con_baseline_a=False)
    assert all(v["controllo_casuale"]["trade_rifatti"] >= v["trade"] for v in ris["per_moneta"].values())


def test_la_ripresa_con_dati_diversi_ricalcola(tmp_path):
    """L'impronta dei dati e' nella riga di avanzamento (regole.md, sezione 13; revisione, sguardo/e2)."""
    q = dict(P, registra_ingressi=False)
    car0, car1 = CaricatoreFinto(monete=TRE[:2]), CaricatoreFinto(monete=TRE[:2], seme=1)
    prima = esame(tmp_path / "stessa", p=q, caricatore=car0)
    dopo = esame(tmp_path / "stessa", p=q, caricatore=car1)  # stesso id, stessa cartella, prezzi diversi
    da_capo = esame(tmp_path / "nuova", p=q, caricatore=car1)
    assert prima["impronte"]["esame"] == dopo["impronte"]["esame"]  # l'esame e' lo stesso, i dati no
    assert senza_file(dopo) == senza_file(da_capo) != senza_file(prima)
    assert dopo["ripresa"]["pezzi_ripresi"] == 0 and dopo["ripresa"]["pezzi_calcolati"] == 4
    # con i dati di prima si riprende tutto, anche dopo le righe dei dati nuovi
    di_nuovo = esame(tmp_path / "stessa", p=q, caricatore=car0)
    assert senza_file(di_nuovo) == senza_file(prima) and di_nuovo["ripresa"]["pezzi_calcolati"] == 0


def test_i_controlli_di_campagna_stanno_nel_corpo_dell_esame(tmp_path, progetto):
    """Via libera e rifiuti valgono anche chiamando il corpo dell'esame (sezione 7, punto 2.4; revisione, sguardo/e3)."""
    metti_marcatore(progetto)
    car = CaricatoreFinto(monete=TRE[:2])

    def corpo(periodo, sorgente, **altro):
        argomenti = dict(moltiplicatore_costi=1.0, ritardo_barre=0, riempimento_intrabarra=None, con_baseline_a=True,
                         processi=1, radice=dati.RADICE_DEFAULT, cartella_campagna=tmp_path / "fuori", monete=None,
                         caricatore=None, sorgente_richiesta=lambda posizioni: dict(sorgente))
        argomenti.update(altro)
        return gruppo._esame(VARIANTE, P, "1d", periodo, "GRUPPO-010", **argomenti)

    with pytest.raises(gruppo.ViaLiberaNonValida, match="manca"):
        corpo("validazione", {"tipo": "modulo"}, monete=monete_di(car), caricatore=car)
    with pytest.raises(dati.VietatoInCampagna, match="monete, caricatore"):
        corpo("costruzione", {"tipo": "modulo"}, monete=monete_di(car), caricatore=car)
    with pytest.raises(dati.VietatoInCampagna, match="placebo"):
        corpo("costruzione", {"tipo": "placebo", "per_moneta": {}, "impronta": "x"})
    _scrivi_via_libera(progetto, _impronte_vere())
    with pytest.raises(dati.VietatoInCampagna, match="placebo"):
        corpo("validazione", {"tipo": "placebo", "per_moneta": {}, "impronta": "x"})
    assert CHIAMATE == [] and not (tmp_path / "fuori").exists()


def test_la_prova_a_placebo_scrive_fuori_da_campagne(tmp_path):
    """I numeri della prova a placebo non vanno in campagne/ (regole.md, sezione 11, punto 5; revisione, sguardo/e9)."""
    car = CaricatoreFinto(monete=TRE[:1])
    placebo = {"AAAUSDT": [ms(date(2022, 3, 1))]}
    radice = tmp_path / "research"
    for cartella in (None, radice / "campagne" / "GRUPPO", radice / "campagne",
                     dati.RADICE_DEFAULT / "campagne" / "GRUPPO" / "prova"):
        with pytest.raises(ValueError, match="placebo"):
            gruppo.esame_di_gruppo(VARIANTE, P, "1d", "costruzione", "PLACEBO-001", processi=1, radice=radice,
                                   cartella_campagna=cartella, caricatore=car, monete=monete_di(car),
                                   ingressi_placebo=placebo)
    assert CHIAMATE == [] and not radice.exists()
    assert not (dati.RADICE_DEFAULT / "campagne" / "GRUPPO" / "prova").exists()
    # fuori da campagne/ si puo'
    ris = gruppo.esame_di_gruppo(VARIANTE, dict(P, registra_ingressi=False), "1d", "costruzione", "PLACEBO-001",
                                 processi=1, radice=radice, cartella_campagna=tmp_path / "taratura", caricatore=car,
                                 monete=monete_di(car), ingressi_placebo=placebo)
    assert Path(ris["file"]["trade"]).parent == tmp_path / "taratura" / "trade"


def test_una_variante_non_valutabile_per_la_sola_a_ha_t_meno_infinito_e_p_value_uno(tmp_path):
    """Sezione 8 del protocollo (t = -inf) e regole.md, sezione 7, punto 5 (p-value 1): revisione, a_non_valutabile."""
    monete = tuple((f"{c * 3}USDT", "2022-01-01", 0.0005) for c in "ABCDEFGHI")
    car = CaricatoreFinto(monete=monete, mesi_sotto=(), buchi=())
    p = {"n": 1, "stop": 0.06, "target": 0.09, "durata": 1, "a_ingressi_massimi": 1}
    ris = esame(tmp_path, "validazione", caricatore=car, p=p)
    assert ris["metriche"]["trade"] >= 300 and ris["valutabile"] is False
    assert any("(a)" in m for m in ris["motivi_non_valutabile"])
    assert ris["baseline_b"]["valutabile"] is True and 0 < ris["baseline_b"]["p_value"] < 1
    assert ris["t"] == -math.inf and ris["p_value"] == 1.0
    assert ris["validazione"]["trade_minimi_superati"] is True and ris["validazione"]["p_value_asticella"] == 1.0
    costruzione = esame(tmp_path, "costruzione", caricatore=CaricatoreFinto(monete=TRE[:2]),
                        p=dict(P, a_ingressi_massimi=1, registra_ingressi=False))
    assert costruzione["valutabile"] is False and costruzione["t"] == -math.inf and costruzione["candidato"] is False
    assert math.isfinite(costruzione["baseline_b"]["t"])


def test_buy_and_hold_con_gli_stessi_pesi_anche_con_una_moneta_assente(tmp_path):
    """La (c) con gli stessi w_j (regole.md, sezione 5, punto 8): una moneta senza candele in un anno non ripesa le altre."""
    car = CaricatoreFinto(monete=(("AAAUSDT", "2021-07-01", 0.0005), ("BBBUSDT", "2022-03-01", 0.001)), mesi_sotto=(),
                          buchi=())
    ris = esame(tmp_path, caricatore=car, p=dict(P, registra_ingressi=False))
    p1 = pezzi(ris, "fase1")
    n = {s: len(p1[s]["dati"]["trade"]["righe"]) for s in p1}
    tot = sum(n.values())
    assert n["AAAUSDT"] > 0 and n["BBBUSDT"] > 0
    assert "2021" in p1["AAAUSDT"]["dati"]["buy_and_hold"] and "2021" not in p1["BBBUSDT"]["dati"]["buy_and_hold"]
    bh = ris["buy_and_hold_per_anno"]
    assert bh["2021"]["long"] == pytest.approx(n["AAAUSDT"] / tot * p1["AAAUSDT"]["dati"]["buy_and_hold"]["2021"]["long"],
                                               rel=1e-12)
    assert bh["2021"]["peso_presente"] == pytest.approx(n["AAAUSDT"] / tot) and bh["2021"]["monete_presenti"] == 1
    assert bh["2022"]["peso_presente"] == pytest.approx(1.0) and bh["2022"]["monete_presenti"] == 2


def test_le_candele_di_btc_si_riportano_e_in_campagna_devono_esserci(tmp_path):
    """Revisione, btc_mancante: BTC mancante non passa in silenzio (regole.md, sezione 2, punto 2, e sezione 3, punto 3)."""
    car = CaricatoreFinto(monete=TRE[:1])
    ris = esame(tmp_path / "con", caricatore=car, p=dict(P, registra_ingressi=False))
    periodi = dati.periodi_gruppo({"AAAUSDT": date(2022, 1, 1)})
    btc = car.btc("1d", gruppo.INIZIO_ARCHIVIO, periodi["fine_costruzione"])
    assert ris["btc"] == {"candele": len(btc), "prima_ts": btc[0].ts, "ultima_close_ts": btc[-1].close_ts}
    assert ris["btc"]["ultima_close_ts"] == periodi["fine_costruzione_ts"]
    # senza marcatore l'esame gira e lo dice
    senza = esame(tmp_path / "senza", caricatore=CaricatoreSenzaBtc(monete=TRE[:1]), p=dict(P, registra_ingressi=False))
    assert senza["btc"] == {"candele": 0, "prima_ts": None, "ultima_close_ts": None}
    # in campagna (il marcatore lo legge chi avvia l'esame e lo passa ai pezzi) si ferma
    regole = gruppo.regole_del_gruppo()
    opzioni = gruppo._opzioni_del_motore(regole, 1.0, 0, None)
    for caricatore, motivo in ((CaricatoreSenzaBtc(monete=TRE[:1]), "nessuna candela"),
                               (CaricatoreFinto(monete=(("AAAUSDT", "2020-07-01", 0.0005),)), "non coprono")):
        base = gruppo._compito_base(VARIANTE, P, "1d", regole, opzioni, caricatore)
        compito = dict(base, tipo="fase1", simbolo="AAAUSDT", j=0, periodo="costruzione", sorgente={"tipo": "modulo"},
                       inizio=caricatore.scheda("AAAUSDT")["primo_mese"].isoformat(), fine="2023-01-16",
                       inizio_conteggio_ts=None, con_a=True)
        gruppo._prepara(dict(compito, in_campagna=False))
        with pytest.raises(ValueError, match=motivo):
            gruppo._prepara(dict(compito, in_campagna=True))


@pytest.mark.parametrize("manca, motivo", [
    ("candele", "nessuna candela 1d di last e mark fra 2022-01-01 e 2023-01-16"),
    ("funding", "nessun regolamento di funding fra 2022-01-01 e 2023-01-16"),
    ("giorni_1d", "nessuna candela 1d del last fra 2022-01-01 e 2023-01-16"),
    ("giorni_1d_assente", "nessuna candela 1d del last"),
])
def test_in_campagna_ogni_moneta_deve_avere_i_dati_della_fase_0(manca, motivo):
    """Terzo giro di revisione, dati mancanti: in campagna una moneta senza dati non pesa zero in silenzio.

    Senza le candele del timeframe la moneta darebbe zero trade, senza il funding costi piu' bassi, senza i file 1d
    del last tutti i mesi sotto la liquidita' (regole.md, sezione 2, punto 5): con il marcatore (letto da chi avvia
    l'esame e passato ai pezzi) ``_prepara`` alza ValueError; senza marcatore nulla cambia.
    """
    caricatore = CaricatoreConDatiMancanti(monete=TRE[:1], manca=manca)
    regole = gruppo.regole_del_gruppo()
    opzioni = gruppo._opzioni_del_motore(regole, 1.0, 0, None)
    base = gruppo._compito_base(VARIANTE, P, "1d", regole, opzioni, caricatore)
    compito = dict(base, tipo="fase1", simbolo="AAAUSDT", j=0, periodo="costruzione", sorgente={"tipo": "modulo"},
                   inizio="2022-01-01", fine="2023-01-16", inizio_conteggio_ts=None, con_a=True)
    senza = gruppo._prepara(dict(compito, in_campagna=False))
    assert (len(senza.candele) == 0) == (manca == "candele") and (len(senza.funding) == 0) == (manca == "funding")
    with pytest.raises(ValueError, match=motivo) as errore:
        gruppo._prepara(dict(compito, in_campagna=True))
    assert "AAAUSDT" in str(errore.value) and "regole.md, sezione 2" in str(errore.value)
    # con tutti i dati, in campagna, si passa
    completo = dict(compito, caricatore=CaricatoreFinto(monete=TRE[:1]))
    assert len(gruppo._prepara(dict(completo, in_campagna=True)).candele) > 0


def test_senza_marcatore_i_dati_mancanti_non_cambiano_l_esame(tmp_path):
    """Senza marcatore (prova a placebo, coordinamento) una moneta senza candele resta una moneta con zero trade."""
    q = dict(P, registra_ingressi=False)
    ris = esame(tmp_path, caricatore=CaricatoreConDatiMancanti(monete=TRE[:2], manca="candele"), p=q)
    assert ris["metriche"]["trade"] == 0 and ris["valutabile"] is False
    assert all(v["barre"] == 0 and v["trade"] == 0 for v in ris["per_moneta"].values())
    conta = gruppo.conta_trade_di_gruppo(VARIANTE, q, "1d", processi=1, monete=["AAAUSDT", "BBBUSDT"],
                                         caricatore=CaricatoreConDatiMancanti(monete=TRE[:2], manca="giorni_1d"))
    uguale = gruppo.conta_trade_di_gruppo(VARIANTE, q, "1d", processi=1, monete=["AAAUSDT", "BBBUSDT"],
                                          caricatore=CaricatoreFinto(monete=TRE[:2]))
    assert json.dumps(conta, sort_keys=True) == json.dumps(uguale, sort_keys=True)


def test_un_buco_prima_della_validazione_con_il_ritardo_non_ferma_l_esame(tmp_path):
    """Revisione, prova_buco: a 1d, con il ritardo di una barra e un buco il giorno prima della validazione.

    Il segnale di tre giorni prima entra il primo giorno di validazione (p = -3 nella finestra, L i giorni di
    validazione) e quello di due giorni prima della fine entra l'ultimo giorno (p = L - 3): prima gli istanti
    «coprivano L + 1 barre, oltre L» e l'esame si fermava. Ora i due segnali hanno lo stesso resto modulo L e si
    contano come coincidenti (regole.md, sezione 2, punto 9: i buchi non fermano una variante).
    """
    periodi = dati.periodi_gruppo({s: date.fromisoformat(primo) for s, primo, _ in TRE[:2]})
    inizio = periodi["inizio_validazione"]
    car = CaricatoreFinto(monete=TRE[:2], mesi_sotto=(), buchi=(("AAAUSDT", ms(inizio - timedelta(days=1))),))
    ogni_10 = list(range(ms(inizio + timedelta(days=10)), ms(date(2023, 12, 20)), 10 * GIORNO))
    placebo = {"AAAUSDT": [ms(inizio - timedelta(days=3))] + ogni_10 + [ms(date(2023, 12, 29))], "BBBUSDT": ogni_10}
    ris = esame(tmp_path, "validazione", caricatore=car, p=dict(P, durata=2, registra_ingressi=False),
                ingressi_placebo=placebo, ritardo_barre=1)
    salvati = [json.loads(r) for r in Path(ris["file"]["trade"]).read_text("utf-8").splitlines()]
    aaa = [t for t in salvati if t["simbolo"] == "AAAUSDT"]
    assert aaa[0]["ts_entrata"] == ms(inizio) and aaa[-1]["ts_entrata"] == ms(date(2023, 12, 31))
    L = periodi["giorni_validazione"]
    assert ris["pavimento_sfasate"]["L"] == L and ris["pavimento_sfasate"]["segnali_coincidenti"] == 1
    assert ris["per_moneta"]["AAAUSDT"]["sfasate"]["segnali_fuori_dalla_finestra_unione"] == 1
    assert ris["pavimento_sfasate"]["valutabile"] is True
    # i due segnali stanno a distanza L sul calendario: (L - 3) - (-3) = L
    p_primo = (ms(inizio - timedelta(days=3)) - ms(inizio)) // GIORNO
    p_ultimo = (ms(date(2023, 12, 29)) - ms(inizio)) // GIORNO
    assert (p_primo, p_ultimo) == (-3, L - 3)


def test_le_sfasate_del_vault_hanno_le_metriche_di_metriche_di_gruppo(tmp_path, monkeypatch):
    """Terzo giro di revisione, voce del vault: le sfasate del vault sono quattro somme per s e per moneta.

    Con le somme (``motore.somme_dei_trade``) e ``motore.metriche_di_gruppo_da_somme`` ogni sfasata ha le metriche
    che ``motore.metriche_di_gruppo`` darebbe sui suoi trade: lo stesso numero di trade, profit factor, rendimento
    e R medio uguali entro 1e-12 relativo (regole.md, sezione 9, punto 4).
    """
    visti = []
    vera = motore.somme_dei_trade

    def spia(trade):
        trade = list(trade)
        visti.append(trade)
        return vera(trade)

    monkeypatch.setattr(motore, "somme_dei_trade", spia)
    ris = vault(tmp_path / "coordinamento")
    sf = ris["sfasate"]
    numero = sf["sfasate"]
    # un pezzo per moneta con trade, nell'ordine dei compiti (primo mese, poi simbolo), una chiamata per s
    ordine = [s for s in sorted(VAULT_J, key=lambda s: (dict((m, p) for m, p, _ in VAULT_MONETE)[s], s))
              if ris["per_moneta"][s]["trade"] > 0]
    assert len(visti) == len(ordine) * numero
    per_moneta = {s: visti[i * numero:(i + 1) * numero] for i, s in enumerate(ordine)}
    vicini = 0
    for k, d in enumerate(sf["dettaglio"]):
        attese = motore.metriche_di_gruppo({s: per_moneta[s][k] for s in ordine if per_moneta[s][k]},
                                           ris["monete_nel_periodo"], 1000.0)
        assert d["n_trade"] == attese["n_trade"]
        for chiave in ("profit_factor", "rendimento_totale"):
            assert d[chiave] == pytest.approx(attese[chiave], rel=1e-12, abs=0.0), (k, chiave)
        assert (d["r_medio"] is None) == (attese["n_trade"] == 0)
        if attese["n_trade"]:
            assert d["r_medio"] == pytest.approx(attese["r_medio"], rel=1e-12, abs=0.0), k
            vicini += 1
    assert vicini > 0.9 * numero


def test_esame_vault_con_1_o_4_processi_e_dopo_un_interruzione_da_gli_stessi_numeri(tmp_path):
    """Terzo giro di revisione: il vault ha il file di avanzamento in sola aggiunta e la ripresa (regole.md, sezione 13).

    Un vault interrotto nelle sfasate (per esempio dal tempo massimo di un comando) si rilancia con gli stessi
    argomenti e riprende dai pezzi gia' fatti: con 1 processo, con 4, interrotto e ripreso (anche con 4 processi)
    i numeri sono gli stessi.
    """
    uno = vault(tmp_path / "uno")
    quattro = vault(tmp_path / "quattro", processi=4)
    assert senza_file(uno) == senza_file(quattro)
    assert quattro["ripresa"]["pezzi_calcolati"] == 8 and quattro["ripresa"]["pezzi_ripresi"] == 0
    # interrotto alle sfasate di DDDUSDT: i compiti vanno per primo mese (AAA, CCC, DDD del 2023-07, poi BBB)
    CHIAMATE.clear()
    guasto = CaricatoreGuastoAlleSfasate(monete=VAULT_MONETE, guasto_alle_sfasate="DDDUSDT", **VAULT_ARGOMENTI)
    with pytest.raises(gruppo.ErroreDiMoneta, match="guasto simulato nelle sfasate"):
        vault(tmp_path / "ripreso", guasto)
    file = tmp_path / "ripreso" / "avanzamento" / "vault_1d.jsonl"
    salvate = [(r["pezzo"], r["simbolo"]) for r in map(json.loads, file.read_text("utf-8").splitlines())]
    assert sorted(salvate) == sorted([("fase1", s) for s in VAULT_J] + [("sfasate", "AAAUSDT"), ("sfasate", "CCCUSDT")])
    # una riga interrotta a meta' si ignora
    with open(file, "ab") as flusso:
        flusso.write(b'{"formato": 2, "impronta": "tron')
    ripreso = vault(tmp_path / "ripreso", processi=4)
    assert senza_file(ripreso) == senza_file(uno)
    assert ripreso["ripresa"] == {"pezzi_ripresi": 6, "pezzi_calcolati": 2, "righe_di_altre_impronte": 0,
                                  "righe_illeggibili": 1}
    # ripreso a pezzi tutti fatti: niente da calcolare, nessuna riga nuova
    prima = len(file.read_text("utf-8").splitlines())
    tutto = vault(tmp_path / "ripreso")
    assert senza_file(tutto) == senza_file(uno)
    assert tutto["ripresa"]["pezzi_ripresi"] == 8 and tutto["ripresa"]["pezzi_calcolati"] == 0
    assert len(file.read_text("utf-8").splitlines()) == prima
    # un altro candidato nella stessa cartella non riusa nulla e non cancella le righe di prima
    altro = vault(tmp_path / "ripreso", q={"n": 3, "stop": 0.06, "target": 0.09, "durata": 3})
    assert altro["ripresa"]["pezzi_ripresi"] == 0 and altro["ripresa"]["righe_di_altre_impronte"] == prima - 1
    assert altro["impronte"]["esame"] != uno["impronte"]["esame"]


def test_il_vault_prende_m_sfasate_dalla_lettura_comune(tmp_path, monkeypatch):
    """M'(s) del pavimento con statistica.medie_sfasate anche nel vault (regole.md, sezione 0, punto 4, e sezione 5, punto 5)."""
    chiamate = []
    vera = statistica.medie_sfasate

    def spia(riassunti, numero):
        chiamate.append((json.loads(json.dumps(riassunti)), numero))
        return vera(riassunti, numero)

    monkeypatch.setattr(statistica, "medie_sfasate", spia)
    car = CaricatoreFinto(monete=(("AAAUSDT", "2023-07-01", 0.0005), ("BBBUSDT", "2023-09-01", 0.001)), mesi_sotto=(),
                          buchi=(), fine_generale="2026-09-30")
    q = {"n": 3, "stop": 0.06, "target": 0.09, "durata": 2}
    ris = gruppo.esame_vault(VARIANTE, q, "1d", cartella=tmp_path / "coordinamento", processi=1,
                             monete={"AAAUSDT": 0, "BBBUSDT": 1}, caricatore=car)
    assert len(chiamate) == 1 and chiamate[0][1] == ris["sfasate"]["sfasate"]
    medie, quanti = vera(*chiamate[0])
    assert quanti == [d["n_trade"] for d in ris["sfasate"]["dettaglio"]]
    pav = statistica.pavimento_sfasamento(medie, quanti, ris["metriche"]["trade"])
    assert ris["baseline_b"]["pavimento_sfasate"] == pav["pavimento"]
    # il criterio di ogni sfasata resta sulle sue metriche (sezione 9, punto 4, motore.metriche_di_gruppo_da_somme):
    # stessi R medi a meno degli arrotondamenti
    for m, d in zip(medie, ris["sfasate"]["dettaglio"]):
        assert (m is None) == (d["r_medio"] is None) and (m is None or m == pytest.approx(d["r_medio"], rel=1e-12))


def test_un_processo_che_muore_ferma_l_esame_invece_di_lasciarlo_fermo(tmp_path):
    """Revisione, prova_figlio_ucciso e senza_guardia: un processo morto senza errore da' ErroreDiMoneta, subito.

    Si prova in un interprete a parte con un tempo massimo: se l'esame restasse fermo il test fallirebbe
    invece di bloccare la suite.
    """
    import subprocess
    import sys

    variante = _variante_modificata(
        tmp_path, "muore.py",
        ("from collections import deque\n", "import multiprocessing\nimport os\nfrom collections import deque\n"),
        ('def crea_variante(ctx, p):\n', 'def crea_variante(ctx, p):\n'
                                         '    if multiprocessing.current_process().name != "MainProcess":\n'
                                         '        os._exit(3)\n'))
    # l'interprete a parte non ha la fixture di conftest.py: il progetto senza marcatore lo sceglie lo script
    vuoto = tmp_path / "progetto_vuoto"
    vuoto.mkdir()
    corpo = (
        "from pathlib import Path\n"
        "from research.src import dati, gruppo\n"
        "from research.src.tests.test_gruppo_esecutore import CaricatoreFinto, monete_di, VARIANTE\n"
        f"dati.RADICE_PROGETTO = Path({str(vuoto)!r})\n"
        "def prova(modulo):\n"
        "    car = CaricatoreFinto()\n"
        "    try:\n"
        "        gruppo.conta_trade_di_gruppo(modulo, {'n': 5, 'stop': 0.06, 'target': 0.09, 'durata': 5}, '1d',\n"
        "                                     processi=2, monete=monete_di(car), caricatore=car)\n"
        "        print('ESITO: finito')\n"
        "    except gruppo.ErroreDiMoneta as errore:\n"
        "        print('ESITO: ErroreDiMoneta', 'morto senza un errore' in str(errore))\n")
    con_guardia = tmp_path / "con_guardia.py"
    con_guardia.write_text(corpo + f"if __name__ == '__main__':\n    prova({str(variante)!r})\n", "utf-8")
    senza_guardia = tmp_path / "senza_guardia.py"
    senza_guardia.write_text(corpo + "prova(VARIANTE)\n", "utf-8")
    for script in (con_guardia, senza_guardia):
        uscita = subprocess.run([sys.executable, str(script)], cwd=RADICE_REPO, capture_output=True, text=True,
                                timeout=180)
        righe = [r for r in uscita.stdout.splitlines() if r.startswith("ESITO")]
        assert righe == ["ESITO: ErroreDiMoneta True"], (script.name, uscita.stdout[-2000:], uscita.stderr[-2000:])
    # un SystemExit del codice della variante diventa ErroreDiMoneta anche nel processo che chiama
    esce = _variante_modificata(tmp_path, "esce.py", ("from collections import deque\n",
                                                      "import sys\nfrom collections import deque\n"),
                                ('def crea_variante(ctx, p):\n', 'def crea_variante(ctx, p):\n    sys.exit(5)\n'))
    with pytest.raises(gruppo.ErroreDiMoneta, match="SystemExit"):
        gruppo.conta_trade_di_gruppo(esce, P, "1d", processi=1, monete=monete_di(CaricatoreFinto()),
                                     caricatore=CaricatoreFinto())
