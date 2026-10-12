"""Le misure della prova a placebo dell'esame di gruppo (regole.md di questa cartella, punto 5), dagli esiti di
``esegui.py``. Si lancia solo a prova finita.

Ordine voluto (punto 5): prima i controlli, poi le misure. Se un controllo manca si stampano solo i conteggi e ci si
ferma (codice d'uscita 1, nessun esito):

1. **Soglie**: i minimi e le soglie di ``parametri.yaml`` (sezione ``gruppo``: ``trade_minimi``,
   ``quota_massima_moneta``, ``placebo_soglie``) sono quelli scritti nelle regole (700 e 300 trade, 10%, 80 placebo,
   3% e 13%), e sono quelli che ``esegui.py`` ha usato in ogni riga (``minimi``).
2. **Identita' e regole**: tutte le righe hanno la stessa identita' (codice, regole, strumenti, monete, schede,
   dati); nessuna e' di un lancio di funzionamento o scritta con le regole in bozza; ``regole.md`` adesso non e' in
   bozza, e' quello delle righe (stesso SHA-256) e le impronte delle righe sono quelle compilate al suo punto 7.
3. **Copertura**: ci sono tutte le 24 combinazioni x gli sfasamenti x 2 periodi; gli errori si contano e si elencano
   (tutti).
4. **Fedelta'**: in nessuna riga le barre vietate dei salti sono diverse da quelle di ``gruppo.py``, il pavimento
   riletto dall'avanzamento e' diverso da quello dell'esame, un ingresso non ha la sua barra, il conteggio di
   ``conta_trade_di_gruppo`` e' diverso dai trade dell'esame, il p_value non e' quello della t di Student del suo t,
   o l'esame ha usato un modulo o strumenti diversi dall'identita'.
5. **Campione**: almeno 80 placebo valutabili in costruzione (almeno 700 trade sommati e nessuna moneta oltre il 10%
   in ``conta_trade_di_gruppo``, confronto con la (b) valutabile) e 80 in validazione (almeno 300 trade sommati,
   confronto valutabile). Gli sfasamenti sono k da 0 a 3; se il campione non basta si aggiungono, in ordine,
   k = 4, 5... fino al primo con cui basta, decisi sul solo conteggio. File di k oltre quello si ignorano (e si
   dicono). Se il file del k che serve non c'e', si dice quanti sfasamenti in piu' servirebbero.
6. **z**: ogni z e' un numero finito.

z = Φ⁻¹(1 − p_value) del confronto con la (b) (GRUPPO, sezione 11, punto 3). p_value e' la coda superiore della t di
Student del t del confronto (``statistica.contro_baseline``), e 1 − p_value = T(t): per t >= 0 si calcola
``norm.isf(p_value)``, per t < 0 ``norm.ppf(T(t))``, cosi' anche un p_value arrotondato a 1 da' lo z della formula,
senza limiti messi a mano. «Netta» vuol dire z > 2,00, «p sotto 0,10» vuol dire z > 1,2816 (GRUPPO §11.3).

Le misure che decidono, sulle placebo valutabili di ciascun periodo (n):

* **M1**: in costruzione le placebo con z > 2,00 sono al massimo ⌊0,03 · n⌋;
* **M2**: in validazione le placebo con z > 1,2816 sono al massimo ⌊0,13 · n⌋;
* **M3**: con μ e σ (ddof 1) degli z, 1 − Φ((2,00 − μ)/σ) ≤ 3% in costruzione e 1 − Φ((1,2816 − μ)/σ) ≤ 13% in
  validazione.

L'esame **regge** solo se valgono tutte. Si riportano, senza che decidano: μ e σ; le stesse misure senza il
pavimento delle sfasate; dove il pavimento delle sfasate decide, la deviazione standard di (R medio − B) / pavimento
(sopra 1,10 si propone di togliere la radice di n'/N dal pavimento); in validazione la quota di placebo con R medio
sopra il 90° percentile delle proprie sfasate (atteso circa 10%); l'effetto grappolo; la quota della moneta piu'
presente; gli intervalli al 95% ricampionando le 24 combinazioni (2.000 volte, seme 0); le misure per timeframe,
direzione e regola. In piu', come limiti della prova: le placebo la cui finestra unione non e' quella del pavimento
delle sfasate; quelle con la durata massima dei trade a meno di 60 barre dal margine (uno spostamento in cerchio
potrebbe far guardare al trade i prezzi del segnale); quante cambiano lettura se si toglie dal pavimento la sfasata
che rimette gli ingressi quasi dove la regola li aveva calcolati.

Uso: python research/taratura/placebo_gruppo/riassunto.py [--cartella DIR] [--json FILE]
(la cartella predefinita e' questa, dove il lancio vero scrive ``esiti_k<k>.jsonl``).
"""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import numpy as np
from scipy.stats import norm
from scipy.stats import t as student

QUI = Path(__file__).resolve().parent
REGOLE = ("incrocio_medie", "rsi", "rottura_20", "bollinger", "macd", "momento_10")
DIREZIONI = ("long", "short")
TIMEFRAME = ("1h", "4h")
PERIODI = ("costruzione", "validazione")
COMBINAZIONI = tuple((tf, r, d) for tf in TIMEFRAME for r in REGOLE for d in DIREZIONI)
K_DELLA_PROVA = (0, 1, 2, 3)
#: i minimi e le soglie scritti nelle regole (GRUPPO, sezione 11, punto 3; regole.md di questa cartella, punti 4 e
#: 5): si controlla che parametri.yaml dica lo stesso
SOGLIE_DELLE_REGOLE = {"trade_minimi": {"costruzione": 700, "validazione": 300}, "quota_massima_moneta": 0.10,
                       "campione_minimo": 80, "quota_costruzione": 0.03, "quota_validazione": 0.13}
#: «netta» vuol dire z > 2,00; «p sotto 0,10» vuol dire z > 1,2816 (GRUPPO, sezione 11, punto 3)
Z_SOGLIA = {"costruzione": 2.00, "validazione": 1.2816}
NOME_CONTEGGIO = {"costruzione": "M1", "validazione": "M2"}
SOGLIA_DEVIAZIONE_PAVIMENTO = 1.10
#: la durata massima dei trade che si segnala: a meno di tante barre dal margine (regole.md, punto 3.4: 60 barre
#: di riscaldamento, piu' delle 50 che la regola piu' lunga guarda)
BARRE_DI_GUARDIA = 60
RICAMPIONAMENTI = 2000
SEME = 0


def etichetta(timeframe: str, regola: str, direzione: str, periodo: str, k: int) -> str:
    return f"GRUPPO|{timeframe}|{regola}|{direzione}|{periodo}|{int(k)}"


def z_di(confronto: Mapping) -> float:
    """z = Φ⁻¹(1 − p_value), con 1 − p_value = T(t) della t di Student del confronto (``gradi_liberta``)."""
    t, gradi = float(confronto["t"]), int(confronto["gradi_liberta"])
    if t >= 0:
        return float(norm.isf(float(confronto["p_value"])))
    return float(norm.ppf(student.cdf(t, gradi)))


def p_coerente(confronto: Mapping) -> bool:
    """Il p_value e' la coda superiore della t di Student del t del confronto (come in ``statistica``)."""
    try:
        t, gradi, p = float(confronto["t"]), int(confronto["gradi_liberta"]), float(confronto["p_value"])
    except (KeyError, TypeError, ValueError):
        return False
    return math.isclose(p, float(student.sf(t, gradi)), rel_tol=1e-9, abs_tol=1e-300)


def coda_normale(soglia: float, mu: float, sigma: float) -> float:
    """1 − Φ((soglia − μ) / σ)."""
    return float(norm.sf((soglia - mu) / sigma))


def limite(quota: float, n: int) -> int:
    """⌊quota · n⌋ con l'aritmetica esatta della quota scritta in decimali (0,03 · 100 = 3, non 2,9999...)."""
    return math.floor(Fraction(str(quota)) * int(n))


# ---------------------------------------------------------------------------
# Soglie e regole (dal branch principale e da questa cartella)
# ---------------------------------------------------------------------------


def soglie_da_parametri(percorso: Path) -> Dict[str, object]:
    """I minimi e le soglie della prova da ``parametri.yaml`` (sezione ``gruppo``)."""
    import yaml

    gruppo = yaml.safe_load(Path(percorso).read_text(encoding="utf-8"))["gruppo"]
    soglie = gruppo["placebo_soglie"]
    return {"trade_minimi": {p: gruppo["trade_minimi"][p] for p in PERIODI},
            "quota_massima_moneta": gruppo["quota_massima_moneta"],
            "campione_minimo": soglie["placebo_valutabili_minime_per_periodo"],
            "quota_costruzione": soglie["netta_costruzione_max"],
            "quota_validazione": soglie["p_sotto_010_validazione_max"]}


def stato_delle_regole(percorso: Path, leggi_impronte, in_bozza, sha256_file) -> Dict[str, object]:
    testo = Path(percorso).read_text(encoding="utf-8")
    return {"sha256": sha256_file(Path(percorso)), "bozza": bool(in_bozza(testo)), "impronte": leggi_impronte(testo)}


# ---------------------------------------------------------------------------
# Lettura
# ---------------------------------------------------------------------------


def k_presenti(cartella: Path) -> List[int]:
    trovati = set()
    for percorso in Path(cartella).glob("esiti_k*.jsonl"):
        trovato = re.fullmatch(r"esiti_k(\d+)\.jsonl", percorso.name)
        if trovato:
            trovati.add(int(trovato.group(1)))
    return sorted(trovati)


def leggi(cartella: Path) -> Tuple[Dict[int, List[dict]], int]:
    """{k: tutte le righe del suo file, nell'ordine} per ogni ``esiti_k<k>.jsonl`` della cartella, e le righe
    illeggibili."""
    righe: Dict[int, List[dict]] = {}
    illeggibili = 0
    for k in k_presenti(cartella):
        righe[k] = []
        for testo in (Path(cartella) / f"esiti_k{k}.jsonl").read_text(encoding="utf-8").splitlines():
            if not testo.strip():
                continue
            try:
                righe[k].append(json.loads(testo))
            except json.JSONDecodeError:
                illeggibili += 1
    return righe, illeggibili


def attese(ks: Sequence[int]) -> List[str]:
    return [etichetta(tf, r, d, periodo, k) for k in ks for (tf, r, d) in COMBINAZIONI for periodo in PERIODI]


def buone_ed_errori(righe: Mapping[int, Sequence[dict]], ks: Sequence[int]) -> Tuple[Dict[str, dict], List[dict]]:
    """{etichetta: l'ultima riga senza errore} e le righe con errore, dei soli ``ks``."""
    buone: Dict[str, dict] = {}
    errori: List[dict] = []
    for k in ks:
        for voce in righe.get(k, ()):
            if voce.get("errore"):
                errori.append(voce)
            else:
                buone[voce["etichetta"]] = voce
    return buone, errori


def valutabile(riga: Mapping, soglie: Mapping, confronto: str = "contro_b") -> bool:
    """La placebo entra in n: supera i controlli della campagna e il confronto con la (b) e' valutabile."""
    esame = riga.get("esame")
    if not esame or not esame.get(confronto) or not esame[confronto].get("valutabile"):
        return False
    if riga["periodo"] == "costruzione":
        conta = riga.get("conta") or {}
        return conta.get("esito") == "registrabile" and esame["trade"] >= soglie["trade_minimi"]["costruzione"]
    return esame["trade"] >= soglie["trade_minimi"]["validazione"]


# ---------------------------------------------------------------------------
# I controlli
# ---------------------------------------------------------------------------


def controllo_soglie(soglie: Mapping, tutte: Iterable[Mapping]) -> List[str]:
    diverse = []
    for chiave, scritto in SOGLIE_DELLE_REGOLE.items():
        if soglie.get(chiave) != scritto:
            diverse.append(f"parametri.yaml: {chiave} = {soglie.get(chiave)!r}, le regole dicono {scritto!r}")
    attesi = {"costruzione": soglie["trade_minimi"]["costruzione"], "validazione": soglie["trade_minimi"]["validazione"],
              "quota_massima_moneta": soglie["quota_massima_moneta"]}
    altri = sorted({r["etichetta"] for r in tutte if not r.get("errore") and r.get("minimi") != attesi})
    if altri:
        diverse.append(f"{len(altri)} righe con minimi diversi da parametri.yaml, per esempio {altri[0]}")
    return diverse


def controllo_regole(tutte: Sequence[Mapping], regole: Mapping) -> List[str]:
    """Le regole delle righe sono quelle chiuse di adesso, e le impronte sono quelle del loro punto 7."""
    problemi = []
    funzionamento = sum(1 for r in tutte if r.get("funzionamento") or (r.get("identita") or {}).get("funzionamento"))
    if funzionamento:
        problemi.append(f"{funzionamento} righe di un lancio di funzionamento")
    bozza = sum(1 for r in tutte if r.get("regole_bozza"))
    if bozza:
        problemi.append(f"{bozza} righe scritte con regole.md in bozza")
    if regole["bozza"]:
        problemi.append("regole.md e' ancora in BOZZA")
    identita = next((r.get("identita") for r in tutte if r.get("identita")), None)
    if identita is not None:
        if identita.get("regole.md") != regole["sha256"]:
            problemi.append("regole.md e' cambiato dopo il lancio (SHA-256 diverso da quello delle righe)")
        if identita.get("strumenti") != regole["impronte"]:
            problemi.append("le impronte delle righe non sono quelle compilate al punto 7 di regole.md")
    return problemi


def controllo_fedelta(righe: Sequence[Mapping]) -> Dict[str, List[str]]:
    """I controlli interni degli esiti che, se uno manca, fermano il riassunto (punto 4 della docstring)."""
    trovati: Dict[str, List[str]] = {"vietate_diverse": [], "pavimento_ricalcolato_diverso": [],
                                     "ingressi_senza_barra": [], "conta_diversa_dall_esame": [],
                                     "p_value_incoerente": [], "esame_con_altro_codice": []}
    for r in righe:
        e, c = r.get("esame"), r.get("conta")
        if c and c.get("ingressi_senza_barra"):
            trovati["ingressi_senza_barra"].append(r["etichetta"])
        if not e:
            continue
        if e.get("vietate_diverse"):
            trovati["vietate_diverse"].append(r["etichetta"])
        if e.get("sfasate") and not e["sfasate"].get("pavimento_uguale"):
            trovati["pavimento_ricalcolato_diverso"].append(r["etichetta"])
        if e.get("ingressi_senza_barra"):
            trovati["ingressi_senza_barra"].append(r["etichetta"])
        if r["periodo"] == "costruzione" and c and c.get("trade_stimati") != e.get("trade"):
            trovati["conta_diversa_dall_esame"].append(r["etichetta"])
        for nome in ("contro_b", "senza_pavimento"):
            confronto = e.get(nome)
            if confronto and confronto.get("valutabile") and not p_coerente(confronto):
                trovati["p_value_incoerente"].append(f"{r['etichetta']} ({nome})")
        identita = r.get("identita") or {}
        if "impronta_variante" in e and (e["impronta_variante"] != (identita.get("codice") or {}).get("placebo_gruppo.py")
                                         or e.get("impronte_strumenti") != identita.get("strumenti")):
            trovati["esame_con_altro_codice"].append(r["etichetta"])
    return {k: v for k, v in trovati.items() if v}


# ---------------------------------------------------------------------------
# Le misure
# ---------------------------------------------------------------------------


def misure_periodo(righe: Sequence[Mapping], periodo: str, soglie: Mapping,
                   confronto: str = "contro_b") -> Dict[str, object]:
    """M1 (costruzione) o M2 (validazione) e M3 su un insieme di placebo valutabili di un periodo."""
    n = len(righe)
    z = np.array([z_di(r["esame"][confronto]) for r in righe], dtype=float)
    soglia_z = Z_SOGLIA[periodo]
    quota = soglie["quota_costruzione"] if periodo == "costruzione" else soglie["quota_validazione"]
    conteggio = int(np.count_nonzero(z > soglia_z))
    tetto = limite(quota, n)
    mu = float(z.mean()) if n else math.nan
    sigma = float(z.std(ddof=1)) if n >= 2 else math.nan
    coda = coda_normale(soglia_z, mu, sigma) if (n >= 2 and sigma > 0) else math.nan
    if periodo == "costruzione":
        diverse = sum(1 for r, x in zip(righe, z) if bool(r["esame"][confronto].get("netta")) != (x > soglia_z))
    else:
        diverse = sum(1 for r, x in zip(righe, z) if (float(r["esame"][confronto]["p_value"]) < 0.10) != (x > soglia_z))
    return {
        "n": n, "nome_conteggio": NOME_CONTEGGIO[periodo], "soglia_z": soglia_z, "conteggio": conteggio,
        "limite": tetto, "quota": conteggio / n if n else math.nan, "regge_conteggio": bool(n and conteggio <= tetto),
        "mu": mu, "sigma": sigma, "coda_m3": coda, "soglia_m3": quota,
        "regge_m3": bool(math.isfinite(coda) and coda <= quota),
        "letture_diverse_da_netta_o_p": diverse,
    }


def deviazione_dove_decide_il_pavimento(righe: Sequence[Mapping]) -> Dict[str, object]:
    """Sulle placebo in cui il pavimento delle sfasate e' l'errore del candidato: sd((R medio − B) / pavimento)."""
    valori = []
    for r in righe:
        e = r["esame"]
        pav = (e.get("pavimento_sfasate") or {}).get("pavimento")
        if e.get("pavimento_decide") and pav and e.get("B") is not None and e.get("r_medio") is not None:
            valori.append((float(e["r_medio"]) - float(e["B"])) / float(pav))
    sd = float(np.std(valori, ddof=1)) if len(valori) >= 2 else math.nan
    return {"placebo": len(valori), "deviazione_standard": sd,
            "oltre_soglia": bool(math.isfinite(sd) and sd > SOGLIA_DEVIAZIONE_PAVIMENTO)}


def distribuzione(valori: Iterable[Optional[float]]) -> Dict[str, object]:
    arr = np.array([float(v) for v in valori if v is not None and math.isfinite(float(v))], dtype=float)
    if not arr.size:
        return {"n": 0}
    return {"n": int(arr.size), "mediana": float(np.median(arr)), "q25": float(np.percentile(arr, 25)),
            "q75": float(np.percentile(arr, 75)), "minimo": float(arr.min()), "massimo": float(arr.max())}


def intervalli_per_combinazione(per_periodo: Mapping[str, Sequence[Mapping]], ricampionamenti: int = RICAMPIONAMENTI,
                                seme: int = SEME) -> Dict[str, Dict[str, object]]:
    """Intervalli al 95% ricampionando le 24 combinazioni (con tutti i loro sfasamenti) con reinserimento.

    Per ogni ricampionamento: quota con z oltre la soglia del periodo (2,00 in costruzione, 1,2816 in validazione),
    μ, σ e la coda della M3 di ciascun periodo. Gli indici delle combinazioni sono gli stessi nei due periodi.
    """
    indice = {c: j for j, c in enumerate(COMBINAZIONI)}
    gruppi = {periodo: [[] for _ in COMBINAZIONI] for periodo in PERIODI}
    for periodo in PERIODI:
        for r in per_periodo[periodo]:
            z = z_di(r["esame"]["contro_b"])
            gruppi[periodo][indice[(r["timeframe"], r["regola"], r["direzione"])]].append((z, z > Z_SOGLIA[periodo]))
    rng = np.random.default_rng(seme)
    scelte = rng.integers(0, len(COMBINAZIONI), size=(ricampionamenti, len(COMBINAZIONI)))
    risultato: Dict[str, Dict[str, object]] = {}
    for periodo in PERIODI:
        quote, mu, sigma, code = [], [], [], []
        for riga in scelte:
            valori = [v for j in riga for v in gruppi[periodo][j]]
            if len(valori) < 2:
                continue
            z = np.array([v[0] for v in valori])
            quote.append(sum(v[1] for v in valori) / len(valori))
            m, s = float(z.mean()), float(z.std(ddof=1))
            mu.append(m)
            sigma.append(s)
            code.append(coda_normale(Z_SOGLIA[periodo], m, s) if s > 0 else math.nan)

        def _i(x):
            arr = np.array([v for v in x if math.isfinite(v)])
            return (float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))) if arr.size else (math.nan, math.nan)

        risultato[periodo] = {"quota": _i(quote), "mu": _i(mu), "sigma": _i(sigma), "coda_m3": _i(code),
                              "ricampionamenti_validi": len(quote)}
    return risultato


def per_gruppo(per_periodo: Mapping[str, Sequence[Mapping]], chiave: str, soglie: Mapping) -> Dict[str, Dict[str, object]]:
    valori = sorted({r[chiave] for periodo in PERIODI for r in per_periodo[periodo]})
    return {v: {periodo: misure_periodo([r for r in per_periodo[periodo] if r[chiave] == v], periodo, soglie)
                for periodo in PERIODI} for v in valori}


def limiti_della_prova(per_periodo: Mapping[str, Sequence[Mapping]]) -> Dict[str, object]:
    """Le misure dei limiti della prova (regole.md, punto 8), sulle placebo valutabili; non decidono."""
    finestre, durate, vicine = [], [], {}
    for periodo in PERIODI:
        cambiano = valide = esatte = 0
        distanze, scarti = [], []
        for r in per_periodo[periodo]:
            e = r["esame"]
            pav = e.get("pavimento_sfasate") or {}
            if pav.get("finestra_unione") is not None and list(pav["finestra_unione"]) != list(r["finestra_unione"]):
                finestre.append(r["etichetta"])
            if e.get("durata_massima_barre") is not None and e["durata_massima_barre"] >= r["margine"] - BARRE_DI_GUARDIA:
                durate.append(r["etichetta"])
            v = (e.get("sfasate") or {}).get("senza_la_piu_vicina")
            if not v:
                continue
            distanze.append(v["distanza_barre"])
            esatte += v["distanza_barre"] == 0
            if v.get("scarto_in_sd") is not None:
                scarti.append(v["scarto_in_sd"])
            if v.get("t") is not None:
                valide += 1
                gradi = e["contro_b"]["gradi_liberta"]
                prima = z_di(e["contro_b"]) > Z_SOGLIA[periodo]
                p_senza = float(student.sf(float(v["t"]), int(gradi)))
                dopo = z_di({"t": v["t"], "gradi_liberta": gradi, "p_value": p_senza}) > Z_SOGLIA[periodo]
                cambiano += prima != dopo
        vicine[periodo] = {"con_la_misura": valide, "cambiano_lettura": cambiano, "distanza_esatta_0": esatte,
                           "distanza_barre": distribuzione(distanze), "scarto_in_sd": distribuzione(scarti)}
    return {"finestra_diversa_dal_pavimento": finestre, "durata_vicina_al_margine": durate,
            "senza_la_sfasata_piu_vicina": vicine}


# ---------------------------------------------------------------------------
# Il riassunto
# ---------------------------------------------------------------------------


def _campione(righe: Sequence[Mapping], soglie: Mapping) -> Tuple[Dict[str, List[Mapping]], Dict[str, object]]:
    per_periodo = {periodo: [r for r in righe if r["periodo"] == periodo and valutabile(r, soglie)]
                   for periodo in PERIODI}
    tutte = {periodo: [r for r in righe if r["periodo"] == periodo] for periodo in PERIODI}
    scarti: Counter = Counter()
    for r in tutte["costruzione"]:
        if r.get("conta") and r["conta"]["esito"] == "scarto":
            motivi_scarto = " ".join(r["conta"]["motivi"])
            scarti["sotto il minimo di trade"] += "sotto" in motivi_scarto
            scarti["una moneta oltre il 10%"] += "oltre" in motivi_scarto
    motivi: Counter = Counter()
    for r in righe:
        e = r.get("esame")
        if e and e.get("contro_b") and not e["contro_b"].get("valutabile"):
            motivi[f"{r['periodo']}: {e['contro_b'].get('motivo_non_valutabile')}"] += 1
        elif e and not e.get("contro_b"):
            motivi[f"{r['periodo']}: nessun trade"] += 1
    minimo_v = soglie["trade_minimi"]["validazione"]
    info = {"valutabili": {periodo: len(per_periodo[periodo]) for periodo in PERIODI},
            "minimo": soglie["campione_minimo"], "scarti_costruzione": dict(scarti),
            "sotto_il_minimo_di_trade_validazione": sum(1 for r in tutte["validazione"] if r.get("esame")
                                                        and r["esame"]["trade"] < minimo_v),
            "non_valutabili_per_motivo": dict(motivi)}
    return per_periodo, info


def riassumi(righe_per_k: Mapping[int, Sequence[dict]], *, soglie: Mapping, regole: Mapping,
             illeggibili: int = 0) -> Dict[str, object]:
    """Tutto il riassunto come dizionario. ``fase`` dice dove si e' fermato: «soglie», «identita'», «regole»,
    «copertura», «fedelta'», «campione», «z» o «misure» (solo allora ci sono le misure e l'esito)."""
    tutte = [r for k in sorted(righe_per_k) for r in righe_per_k[k]]
    presenti = sorted(righe_per_k)
    out: Dict[str, object] = {"k_presenti": presenti, "righe_lette": len(tutte), "righe_illeggibili": illeggibili,
                              "soglie": dict(soglie)}
    out["commit_principale"] = sorted({r.get("commit_principale") for r in tutte if r.get("commit_principale")})
    out["commit_prova"] = sorted({r.get("commit_prova") for r in tutte if r.get("commit_prova")})
    diverse = controllo_soglie(soglie, tutte)
    if diverse:
        out.update(fase="soglie", problemi=diverse)
        return out
    identita = {json.dumps(r.get("identita"), sort_keys=True) for r in tutte}
    out["identita_diverse"] = len(identita)
    if len(identita) > 1:
        out["fase"] = "identita'"
        return out
    if tutte:
        out["identita"] = json.loads(next(iter(identita)))
    problemi = controllo_regole(tutte, regole)
    if problemi:
        out.update(fase="regole", problemi=problemi)
        return out

    # gli sfasamenti: 0..3, poi 4, 5... solo finche' il campione non basta (sul solo conteggio)
    ks = list(K_DELLA_PROVA)
    while True:
        buone, errori = buone_ed_errori(righe_per_k, ks)
        out["k"] = list(ks)
        attesi = attese(ks)
        mancanti = [e for e in attesi if e not in buone]
        aperti = sorted({e["etichetta"] for e in errori if e.get("etichetta") not in buone})
        out["copertura"] = {"attese": len(attesi), "presenti": len(attesi) - len(mancanti), "mancanti": mancanti,
                            "errori_senza_riga_buona": aperti, "righe_con_errore": len(errori),
                            "errori": [(e.get("etichetta"), str(e.get("errore", "")).splitlines()[0][:200])
                                       for e in errori]}
        if mancanti:
            out["fase"] = "copertura"
            return out
        righe = [buone[e] for e in attesi]
        fedelta = controllo_fedelta(righe)
        if fedelta:
            out.update(fase="fedelta'", fedelta=fedelta)
            return out
        per_periodo, info = _campione(righe, soglie)
        out["campione"] = info
        pochi = [periodo for periodo in PERIODI if len(per_periodo[periodo]) < soglie["campione_minimo"]]
        if not pochi:
            break
        prossimo = max(ks) + 1
        if prossimo in righe_per_k:
            ks.append(prossimo)
            continue
        # quanti sfasamenti in tutto servirebbero, al ritmo di valutabili per sfasamento visto fin qui (solo conteggio)
        servono = {}
        for periodo in pochi:
            per_k = len(per_periodo[periodo]) / len(ks)
            servono[periodo] = None if per_k == 0 else max(len(ks) + 1,
                                                           math.ceil(soglie["campione_minimo"] / per_k))
        totale = max((v for v in servono.values() if v is not None), default=None)
        info["sfasamenti_totali_stimati"] = servono
        info["prossimi_k"] = None if totale is None else list(range(prossimo, prossimo + totale - len(ks)))
        out["fase"] = "campione"
        return out
    out["k_ignorati"] = [k for k in presenti if k not in ks]

    non_finiti = [r["etichetta"] for periodo in PERIODI for r in per_periodo[periodo]
                  if not math.isfinite(z_di(r["esame"]["contro_b"]))]
    if non_finiti:
        out.update(fase="z", z_non_finiti=non_finiti)
        return out

    out["fase"] = "misure"
    misure = {periodo: misure_periodo(per_periodo[periodo], periodo, soglie) for periodo in PERIODI}
    out["misure"] = misure
    regge = {"M1": misure["costruzione"]["regge_conteggio"], "M2": misure["validazione"]["regge_conteggio"],
             "M3_costruzione": misure["costruzione"]["regge_m3"], "M3_validazione": misure["validazione"]["regge_m3"]}
    out["condizioni"] = regge
    out["regge"] = all(regge.values())
    # informative
    tutte_p = {periodo: [r for r in righe if r["periodo"] == periodo] for periodo in PERIODI}
    senza = {periodo: [r for r in tutte_p[periodo] if valutabile(r, soglie, "senza_pavimento")
                       and math.isfinite(z_di(r["esame"]["senza_pavimento"]))] for periodo in PERIODI}
    out["senza_pavimento_sfasate"] = {periodo: misure_periodo(senza[periodo], periodo, soglie, "senza_pavimento")
                                      if len(senza[periodo]) >= 2 else {"n": len(senza[periodo])} for periodo in PERIODI}
    out["dove_decide_il_pavimento"] = {periodo: deviazione_dove_decide_il_pavimento(per_periodo[periodo])
                                       for periodo in PERIODI}
    con_p90 = [r for r in per_periodo["validazione"] if (r["esame"].get("sfasate") or {}).get("sopra_p90") is not None]
    sopra = sum(1 for r in con_p90 if r["esame"]["sfasate"]["sopra_p90"])
    out["sopra_p90_sfasate_validazione"] = {"n": len(con_p90), "sopra": sopra,
                                            "quota": sopra / len(con_p90) if con_p90 else math.nan}
    out["effetto_grappolo"] = {periodo: distribuzione(r["esame"].get("effetto_grappolo") for r in per_periodo[periodo])
                               for periodo in PERIODI}
    out["quota_moneta_piu_presente"] = {periodo: distribuzione(r["esame"].get("quota_moneta_piu_presente")
                                                               for r in per_periodo[periodo]) for periodo in PERIODI}
    out["intervalli_95_per_combinazione"] = intervalli_per_combinazione(per_periodo)
    out["per_timeframe"] = per_gruppo(per_periodo, "timeframe", soglie)
    out["per_direzione"] = per_gruppo(per_periodo, "direzione", soglie)
    out["per_regola"] = per_gruppo(per_periodo, "regola", soglie)
    out["limiti"] = limiti_della_prova(per_periodo)
    return out


# ---------------------------------------------------------------------------
# Stampa
# ---------------------------------------------------------------------------


def _pc(x: float) -> str:
    return "n.d." if x is None or not math.isfinite(x) else f"{100 * x:.2f}%"


def _n(x: float, cifre: int = 3) -> str:
    return "n.d." if x is None or not math.isfinite(x) else f"{x:.{cifre}f}"


def _riga_misure(m: Mapping) -> str:
    if m.get("n", 0) < 2:
        return f"n {m.get('n', 0)}: troppo poche"
    soglia = f"z > {m['soglia_z']:.4g}".replace(".", ",")
    return (f"n {m['n']}; {m['nome_conteggio']} {m['conteggio']} con {soglia} (limite {m['limite']}, quota "
            f"{_pc(m['quota'])}); μ {_n(m['mu'])}, σ {_n(m['sigma'])}; M3 P({soglia}) {_pc(m['coda_m3'])} (soglia "
            f"{_pc(m['soglia_m3'])})")


def stampa(r: Mapping, scrivi=print) -> None:
    scrivi(f"file di k {r['k_presenti']}; righe {r['righe_lette']}, illeggibili {r['righe_illeggibili']}; commit "
           f"principale {[c[:8] for c in r['commit_principale']]}, prova {[c[:8] for c in r['commit_prova']]}")
    if r["fase"] == "soglie":
        scrivi("SOGLIE DIVERSE DALLE REGOLE: nessuna misura")
        for p in r["problemi"]:
            scrivi(f"  {p}")
        return
    if r["fase"] == "identita'":
        scrivi(f"IDENTITA' DIVERSE ({r['identita_diverse']}): righe di codici, regole, strumenti o dati diversi; "
               "nessuna misura")
        return
    if r["fase"] == "regole":
        scrivi("REGOLE NON CHIUSE O CAMBIATE: nessuna misura")
        for p in r["problemi"]:
            scrivi(f"  {p}")
        return
    c = r["copertura"]
    scrivi(f"sfasamenti usati {r['k']}; copertura: {c['presenti']} su {c['attese']} (24 combinazioni x "
           f"{len(r['k'])} sfasamenti x 2 periodi); righe con errore {c['righe_con_errore']}, errori senza una riga "
           f"buona {len(c['errori_senza_riga_buona'])}")
    for etichetta_, testo in c["errori"]:
        scrivi(f"  errore: {etichetta_}: {testo}")
    if r["fase"] == "copertura":
        scrivi(f"COPERTURA INCOMPLETA: nessuna misura finche' mancano placebo. Mancano ({len(c['mancanti'])}):")
        for e in c["mancanti"]:
            scrivi(f"  {e}")
        return
    if r["fase"] == "fedelta'":
        scrivi("CONTROLLI DI FEDELTA' NON SUPERATI: nessuna misura")
        for nome, etichette in r["fedelta"].items():
            scrivi(f"  {nome}: {len(etichette)}: {', '.join(etichette)}")
        return
    cam = r["campione"]
    scrivi(f"campione: valutabili in costruzione {cam['valutabili']['costruzione']}, in validazione "
           f"{cam['valutabili']['validazione']} (minimo {cam['minimo']} per periodo); scarti in costruzione "
           f"{cam['scarti_costruzione']}; validazione sotto il minimo di trade "
           f"{cam['sotto_il_minimo_di_trade_validazione']}")
    if cam["non_valutabili_per_motivo"]:
        scrivi(f"non valutabili: {cam['non_valutabili_per_motivo']}")
    if r["fase"] == "campione":
        scrivi(f"CAMPIONE INSUFFICIENTE: servono altri sfasamenti, decisi sul solo conteggio (stima degli sfasamenti "
               f"totali {cam['sfasamenti_totali_stimati']}); prossimi k da lanciare: {cam['prossimi_k']}")
        return
    if r.get("k_ignorati"):
        scrivi(f"file di k non richiesti dal conteggio, ignorati: {r['k_ignorati']}")
    if r["fase"] == "z":
        scrivi(f"z NON FINITI ({len(r['z_non_finiti'])}): la formula non da' un numero; nessuna misura")
        for e in r["z_non_finiti"]:
            scrivi(f"  {e}")
        return
    m = r["misure"]
    scrivi("costruzione: " + _riga_misure(m["costruzione"]))
    scrivi("validazione: " + _riga_misure(m["validazione"]))
    cond = r["condizioni"]
    scrivi("condizioni: " + ", ".join(f"{k} {'regge' if v else 'NON regge'}" for k, v in cond.items()))
    scrivi("ESITO: l'esame di gruppo regge sui prezzi veri" if r["regge"] else
           "ESITO: l'esame di gruppo NON regge: STOP (regole.md, punto 6)")
    scrivi("--- solo informative ---")
    for periodo in PERIODI:
        scrivi(f"letture diverse fra z e «netta»/«p < 0,10» del confronto, {periodo}: "
               f"{m[periodo]['letture_diverse_da_netta_o_p']}")
    for periodo in PERIODI:
        scrivi(f"senza il pavimento delle sfasate, {periodo}: {_riga_misure(r['senza_pavimento_sfasate'][periodo])}")
    for periodo in PERIODI:
        d = r["dove_decide_il_pavimento"][periodo]
        scrivi(f"dove decide il pavimento delle sfasate, {periodo}: {d['placebo']} placebo, sd((R - B)/pavimento) "
               f"{_n(d['deviazione_standard'])}{' OLTRE 1,10' if d['oltre_soglia'] else ''}")
    s = r["sopra_p90_sfasate_validazione"]
    scrivi(f"validazione, R medio sopra il 90° percentile delle proprie sfasate: {s['sopra']} su {s['n']} "
           f"({_pc(s['quota'])}, atteso circa 10%)")
    for periodo in PERIODI:
        g, q = r["effetto_grappolo"][periodo], r["quota_moneta_piu_presente"][periodo]
        scrivi(f"{periodo}: effetto grappolo mediana {_n(g.get('mediana', math.nan), 2)} "
               f"(25-75%: {_n(g.get('q25', math.nan), 2)}-{_n(g.get('q75', math.nan), 2)}); quota della moneta piu' "
               f"presente mediana {_pc(q.get('mediana', math.nan))}, massimo {_pc(q.get('massimo', math.nan))}")
    for periodo, iv in r["intervalli_95_per_combinazione"].items():
        scrivi(f"intervalli al 95% ricampionando le combinazioni, {periodo}: quota {_pc(iv['quota'][0])}-"
               f"{_pc(iv['quota'][1])}; μ {_n(iv['mu'][0])}-{_n(iv['mu'][1])}; σ {_n(iv['sigma'][0])}-"
               f"{_n(iv['sigma'][1])}; coda M3 {_pc(iv['coda_m3'][0])}-{_pc(iv['coda_m3'][1])}")
    for chiave in ("per_timeframe", "per_direzione", "per_regola"):
        scrivi(f"{chiave.replace('_', ' ')}:")
        for valore, mm in r[chiave].items():
            for periodo in PERIODI:
                scrivi(f"  {valore} {periodo}: {_riga_misure(mm[periodo])}")
    lim = r["limiti"]
    scrivi(f"limiti: finestra unione diversa da quella del pavimento in {len(lim['finestra_diversa_dal_pavimento'])} "
           f"placebo {lim['finestra_diversa_dal_pavimento']}; durata massima dei trade a meno di {BARRE_DI_GUARDIA} "
           f"barre dal margine in {len(lim['durata_vicina_al_margine'])} {lim['durata_vicina_al_margine']}")
    for periodo, v in lim["senza_la_sfasata_piu_vicina"].items():
        scrivi(f"  senza la sfasata piu' vicina agli ingressi della regola, {periodo}: {v['cambiano_lettura']} su "
               f"{v['con_la_misura']} cambiano lettura; distanza 0 in {v['distanza_esatta_0']}; distanza mediana "
               f"{v['distanza_barre'].get('mediana', 'n.d.')} barre; scarto mediano "
               f"{_n(v['scarto_in_sd'].get('mediana', math.nan), 2)} sd")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Le misure della prova a placebo dell'esame di gruppo")
    parser.add_argument("--cartella", type=Path, default=QUI, help="la cartella degli esiti_k<k>.jsonl")
    parser.add_argument("--json", type=Path, default=None, help="scrive anche il riassunto in JSON")
    args = parser.parse_args(argv)
    sys.path.insert(0, str(QUI))
    import esegui as E  # mette nel percorso il branch principale; trova parametri.yaml

    soglie = soglie_da_parametri(E.PRINCIPALE / "research" / "config" / "parametri.yaml")
    regole = stato_delle_regole(E.REGOLE_DELLA_PROVA, E.leggi_impronte, E.in_bozza, E.sha256_file)
    righe, illeggibili = leggi(args.cartella)
    risultato = riassumi(righe, soglie=soglie, regole=regole, illeggibili=illeggibili)
    proprio = Path(__file__).resolve()
    risultato["riassunto_py"] = {"sha256": E.sha256_file(proprio), "commit": E._git(QUI, "rev-parse", "HEAD").strip(),
                                 "non_committato": bool(subprocess.run(
                                     ["git", "-C", str(QUI), "status", "--porcelain", "--", proprio.name],
                                     capture_output=True, text=True).stdout.strip())}
    stampa(risultato)
    if risultato["riassunto_py"]["non_committato"]:
        print("ATTENZIONE: riassunto.py ha modifiche non committate: questo non e' l'esito della prova")
    if args.json is not None:
        args.json.write_text(json.dumps(risultato, indent=1, ensure_ascii=False, default=list), encoding="utf-8")
    definitivo = risultato["fase"] == "misure" and not risultato["riassunto_py"]["non_committato"]
    return 0 if definitivo else 1


if __name__ == "__main__":
    raise SystemExit(main())
