"""Programma 7, ottantottesima prova (prova 150 del registro): l'asimmetria dei rendimenti dai minuti (`OTTANTOTTESIMA.md`).

Due fasi:
  python3 -m research.programma7.ottantottesima raccogli   # dalle candele a 1 minuto: somme giornaliere di r^2 e r^3 (rendimenti a 5 minuti)
  python3 -m research.programma7.ottantottesima esegui     # segnale, portafoglio come G1, esame, registro delle varianti

Raccolta: per ogni moneta dell'universo (quelle che entrano nelle 100 piu' scambiate di almeno una settimana) i mesi di candele a 1 minuto
che servono, dall'archivio pubblico di Binance con il controllo dell'impronta (stesse funzioni di `programma5.strumenti.scarico`); i mesi
gia' presenti in `research/data/p5` si leggono da li'. I file scaricati NON si salvano (10 GB): si tengono solo le somme giornaliere in
`risultati_ottantottesima/giorni/<MONETA>.npz` (riprende da dove si e' fermata).

Letture scelte dove le regole lasciano margine (dichiarate nel rapporto): vedi LETTURE in questo file.
"""
from __future__ import annotations

import hashlib
import io
import json
import math
import re
import sys
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

QUI = Path(__file__).parent
OUT = QUI / "risultati_ottantottesima"
GIORNI = OUT / "giorni"
ID = "ottantottesima"
SEME = 2026
N_PROVE = 308                       # 306 prima di questa prova + le sue 2 varianti
SOGLIA_SHARPE_CORRETTO, SOGLIA_T, MIN_GIORNI = 0.80, 3.0, 5
FINESTRE = {"v7": 7, "v30": 30}
BLOCCHI = 288                       # blocchi da 5 minuti in un giorno

LETTURE = [
    "rendimento r = logaritmo del rapporto fra la chiusura dell'ultimo minuto di un blocco da 5 (allineato alle 00:00 UTC) e quella del blocco prima; "
    "il primo blocco del giorno usa l'ultimo del giorno prima; un blocco con un minuto di chiusura mancante non da' rendimento",
    "giorno 'completo' = tutti i 1.440 minuti presenti; nella finestra contano solo i giorni completi, n = numero dei rendimenti validi; "
    "con meno di 5 giorni completi la moneta e' fuori dall'universo del giorno (il 28 ottobre 2026 manca nell'archivio per tutte: non rattoppato "
    "con l'interfaccia pubblica, per trattare tutte le monete allo stesso modo)",
    "finestra dei 7 (o 30) giorni = i giorni di calendario prima della mezzanotte, mezzanotte esclusa",
    "universo del giorno = le 100 della settimana (lunedi') come G1, intersecato con le monete che hanno il segnale; pesi e banda come G1 "
    "(volatilita' dei 30 giorni dal pannello, `ventiquattresima.pesi_banda`)",
    "ordine: segnale piu' basso = acquisto (RS basso), segnale piu' alto = vendita: `pesi_banda` compra il rango alto, quindi il segnale passato e' -RS",
    "spese a limite come G1 (`cinquantaseiesima.spese_a_limite`, candele a 1 ora); accanto, tutto a mercato",
]


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# ---------------------------------------------------------------------------------------------------------------- raccolta
def _csv_bytes(b: bytes) -> pd.DataFrame:
    from research.programma5.strumenti import motore5 as m5
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        grezzo = z.read(z.namelist()[0])
    h = 0 if grezzo[:1].isalpha() else None
    df = pd.read_csv(io.BytesIO(grezzo), header=h, usecols=[0, 4] if h is None else None)
    if h is None:
        df.columns = ["open_time", "close"]
    else:
        df = df[["open_time", "close"]]
    df["open_time"] = m5._ms(df["open_time"])
    return df


def _scarica_bytes(chiave: str) -> bytes | None:
    from research.programma5.strumenti import scarico as sca
    from research.src.dati import leggi_checksum
    contenuto = sca._prendi(sca.BASE + chiave)
    if contenuto is None:
        return None
    somma = sca._prendi(sca.BASE + chiave + ".CHECKSUM")
    if somma is not None and leggi_checksum(somma, chiave) != hashlib.sha256(contenuto).hexdigest():
        raise RuntimeError(f"impronta diversa per {chiave}")
    return contenuto


def _mese(chiave: str) -> str:
    m = re.search(r"-(\d{4}-\d{2})(?:-\d{2})?\.zip$", chiave)
    return m.group(1) if m else ""


def monete_e_finestre() -> dict:
    """{moneta: (primo giorno da leggere, ultimo giorno da leggere)} dalle settimane in cui entra nell'universo."""
    from research.programma6 import seconda as sc, terza as te
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    lun, U, sim = ps["lunedi"], ps["U"], list(ps["simboli"])
    a, b = sc.giorno(2021, 1, 4), sc.giorno(2026, 10, 31)
    k = (lun >= a - 6) & (lun <= b)
    out = {}
    for j in np.flatnonzero(U[k].any(axis=0)):
        w = lun[k][U[k][:, j]]
        out[sim[j]] = (max(int(w.min()) - 31, a - 31), min(int(w.max()) + 6, b - 1))
    return out


def una_moneta(s: str, d0: int, d1: int) -> str:
    from research.programma5.strumenti import motore5 as m5
    from research.programma5.strumenti import scarico as sca
    f = GIORNI / f"{s}.npz"
    if f.exists():
        return "gia'"
    da = pd.Timestamp(d0 * 86400, unit="s", tz="UTC")
    a = pd.Timestamp(d1 * 86400, unit="s", tz="UTC")
    m_da, m_a = da.strftime("%Y-%m"), a.strftime("%Y-%m")
    locali = {p.name: p for p in m5._file(s, "klines")}
    chiavi = [k for k in sca._scelte("klines", s) if m_da <= _mese(k) <= m_a]
    if not chiavi and not locali:
        raise RuntimeError(f"{s}: nessun file nell'archivio")

    def leggi(k):
        nome = k.rsplit("/", 1)[1]
        if nome in locali:
            return _csv_bytes(locali[nome].read_bytes())
        b = _scarica_bytes(k)
        return None if b is None else _csv_bytes(b)
    with ThreadPoolExecutor(max_workers=4) as ex:
        parti = [p for p in ex.map(leggi, chiavi) if p is not None]
    if not parti:
        raise RuntimeError(f"{s}: nessuna candela")
    df = pd.concat(parti, ignore_index=True)
    df["minuto"] = df["open_time"] // 60_000
    df = df.drop_duplicates("minuto").set_index("minuto").sort_index()
    m0, m1 = d0 * 1440, (d1 + 1) * 1440
    df = df[(df.index >= m0) & (df.index < m1)]
    presenti = np.zeros(m1 - m0, dtype=bool)
    presenti[df.index.to_numpy() - m0] = True
    c = np.full(m1 - m0, np.nan)
    c[df.index.to_numpy() - m0] = df["close"].to_numpy(float)
    c[~(c > 0)] = np.nan
    chiusure = c.reshape(-1, 5)[:, 4]                         # ultimo minuto di ogni blocco da 5
    with np.errstate(all="ignore"):
        r = np.diff(np.log(chiusure), prepend=np.nan)         # il primo del periodo non ha il blocco prima
    T = d1 - d0 + 1
    r = r.reshape(T, BLOCCHI)
    ok = np.isfinite(r)
    r0 = np.where(ok, r, 0.0)
    np.savez_compressed(f, d0=d0, d1=d1, s2=(r0 ** 2).sum(axis=1), s3=(r0 ** 3).sum(axis=1), n=ok.sum(axis=1),
                        minuti=presenti.reshape(T, 1440).sum(axis=1), n_file=len(chiavi))
    return f"{len(chiavi)} file"


def raccogli():
    GIORNI.mkdir(parents=True, exist_ok=True)
    mf = monete_e_finestre()
    log(f"monete da raccogliere: {len(mf)}")
    errori = {}

    def lavora(item):
        s, (d0, d1) = item
        for k in range(3):
            try:
                t = time.time()
                r = una_moneta(s, d0, d1)
                log(f"{s}: {r} ({time.time() - t:.0f} s)")
                return
            except Exception as e:  # noqa: BLE001
                errori[s] = repr(e)
                time.sleep(5 * (k + 1))
        log(f"{s}: ERRORE {errori[s]}")
    with ThreadPoolExecutor(max_workers=5) as ex:
        list(ex.map(lavora, sorted(mf.items())))
    manca = [s for s in mf if not (GIORNI / f"{s}.npz").exists()]
    log(f"finito: {len(mf) - len(manca)} monete fatte, mancano {len(manca)}: {manca}")
    (OUT / "raccolta_errori.json").write_text(json.dumps({"mancano": manca, "errori": {s: errori.get(s) for s in manca}}, indent=1))


# ---------------------------------------------------------------------------------------------------------------- esame
def carica_somme(pan: dict, simboli: list):
    """Matrici (giorni del pannello x monete) delle somme giornaliere, NaN dove la moneta non e' stata raccolta."""
    T, S = pan["close"].shape
    t0 = pan["t0"]
    S2, S3, N, FULL = (np.full((T, S), np.nan), np.full((T, S), np.nan), np.zeros((T, S)), np.zeros((T, S), dtype=bool))
    for j, s in enumerate(simboli):
        f = GIORNI / f"{s}.npz"
        if not f.exists():
            continue
        z = np.load(f)
        d0, d1 = int(z["d0"]), int(z["d1"])
        a, b = max(d0, t0), min(d1, t0 + T - 1)
        sl = slice(a - d0, b - d0 + 1)
        dst = slice(a - t0, b - t0 + 1)
        S2[dst, j], S3[dst, j], N[dst, j] = z["s2"][sl], z["s3"][sl], z["n"][sl]
        FULL[dst, j] = z["minuti"][sl] == 1440
    return S2, S3, N, FULL


def asimmetria(S2, S3, N, FULL, idx: np.ndarray, L: int) -> np.ndarray:
    """RS per ogni giorno idx (indice nel pannello) con i L giorni prima (mezzanotte esclusa); NaN con meno di 5 giorni completi."""
    out = np.full((len(idx), S2.shape[1]), np.nan)
    f = FULL.astype(float)
    c2 = np.vstack([np.zeros((1, S2.shape[1])), np.cumsum(np.where(FULL, np.nan_to_num(S2), 0), axis=0)])
    c3 = np.vstack([np.zeros((1, S2.shape[1])), np.cumsum(np.where(FULL, np.nan_to_num(S3), 0), axis=0)])
    cn = np.vstack([np.zeros((1, S2.shape[1])), np.cumsum(np.where(FULL, N, 0), axis=0)])
    cf = np.vstack([np.zeros((1, S2.shape[1])), np.cumsum(f, axis=0)])
    a, b = idx - L, idx                                          # giorni [a, b)
    s2, s3, n, nf = c2[b] - c2[a], c3[b] - c3[a], cn[b] - cn[a], cf[b] - cf[a]
    with np.errstate(all="ignore"):
        rs = np.sqrt(n) * s3 / s2 ** 1.5
    return np.where((nf >= MIN_GIORNI) & (s2 > 0) & np.isfinite(rs), rs, np.nan)


def misure(sett: pd.DataFrame, btc) -> dict:
    from research.programma6 import seconda as sc, sesta as se, terza as te
    return te.esame(sett, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)


def esegui():
    import research.programma7.cinquantaduesima as kp
    from research.programma6 import asticella as ast
    from research.programma6 import ottava as ot
    from research.programma6 import seconda as sc
    from research.programma6 import sesta as se
    from research.programma6 import terza as te
    from research.programma6 import ventiquattresima as vq
    from research.programma7 import prima as g1
    from research.src.prove import registra
    OUT.mkdir(parents=True, exist_ok=True)
    fine = sc.giorno(2026, 10, 31) + 1                               # fino al 31 ottobre incluso
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    simboli = list(pan["simboli"])
    giorni = np.arange(se.INIZIO, fine, dtype=np.int64)
    idx = giorni - pan["t0"]
    Ud = g1.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    sig = ot.sigma_30(pan, idx)
    R = sc.rendimenti(pan)[idx]
    F = np.nan_to_num(pan["funding"][idx])
    costo = sc.costi_moneta(pan["simboli"])
    btc = pd.Series(ps["R"][:, simboli.index("BTCUSDT")], index=ps["lunedi"])
    S2, S3, N, FULL = carica_somme(pan, simboli)
    # G1 (riferimento): stesso codice della prima prova, fino al 31 ottobre
    ct_g1 = np.where(np.isfinite(sig), -se.funding_7(pan, idx), np.nan)
    W_g1 = vq.pesi_banda(ct_g1, Ud, sig)
    lim_g1, _ = kp.conto(W_g1, R, F, costo, giorni, pan["simboli"])
    sett_g1 = g1.per_settimana(lim_g1, giorni)
    # lo Sharpe corretto: V = Sharpe dei gruppi gia' nel conto + le 2 varianti; N = 308 (come l'ottantasettesima)
    prove = ast.le_prove()
    serie = {n: ast.periodo(s) for n, s, _ in prove if s is not None}
    serie.update({n: ast.periodo(s) for n, s in ast.serie_nuove().items()})
    soli = [sr for _, s, sr in prove if s is None]
    gr = ast.gruppi(serie, ast.TAGLIO)
    sr_base = ast.per_v(gr, soli, True)
    log("Sharpe dei gruppi gia' nel conto:", len(sr_base))
    ris, daily, sett_all, W_all = {}, {}, {}, {}
    for nome, L in FINESTRE.items():
        par = {"finestra_giorni": L, "banda": "20/40", "pesi": "inverso volatilita 30 giorni", "blocchi_minuti": 5,
               "ordine": "limite 0,02% un'ora poi mercato 0,05%", "dal": "2021-01-04", "al": "2026-10-31", "N_prove": N_PROVE}
        try:
            RS = asimmetria(S2, S3, N, FULL, idx, L)
            ct = np.where(np.isfinite(sig) & np.isfinite(RS), -RS, np.nan)
            W = vq.pesi_banda(ct, Ud, sig)
            lim, ordini = kp.conto(W, R, F, costo, giorni, pan["simboli"])
            mer = te.conto(W, R, F, costo)
            sett, sett_mer = g1.per_settimana(lim, giorni), g1.per_settimana(mer, giorni)
            sett.to_csv(OUT / f"settimane_{nome}.csv.gz")
            lim.assign(giorno=giorni).to_csv(OUT / f"giorni_{nome}.csv.gz", index=False)
            e = misure(sett, btc)
            em = misure(sett_mer, btc)
            e["a_mercato"] = {k: em["intero"][k] for k in ("sharpe", "annuo", "discesa_max")} | {"spese_annue": em["spese_annue"]}
            e["ordini"], e["movimenti"] = ordini, g1.movimenti(W)
            e["monete_con_segnale_mediana"] = float(np.median((np.isfinite(ct) & Ud).sum(axis=1)))
            e["giorni_con_posizioni"] = int((np.abs(W).sum(axis=1) > 0).sum())
            e["giorni"] = int(len(giorni))
            # correlazioni con G1: rendimenti giornalieri, settimanali e rango dei due segnali nelle 100 monete
            e["correlazione_G1_giornaliera"] = float(np.corrcoef(lim["netto"], lim_g1["netto"])[0, 1])
            c = sett.index.intersection(sett_g1.index)
            e["correlazione_G1_settimanale"] = float(np.corrcoef(sett.loc[c, "netto"], sett_g1.loc[c, "netto"])[0, 1])
            cr = []
            for k in range(len(giorni)):
                jj = np.flatnonzero(Ud[k] & np.isfinite(ct[k]) & np.isfinite(ct_g1[k]))
                if len(jj) >= 10:
                    cr.append(pd.Series(ct[k, jj]).rank().corr(pd.Series(ct_g1[k, jj]).rank()))
            e["correlazione_segnali_rango"] = float(np.nanmean(cr))
            # miscela 50/50 con G1 sugli stessi giorni (informativa)
            mix = 0.5 * lim["netto"].to_numpy() + 0.5 * lim_g1["netto"].to_numpy()
            mix_s = pd.DataFrame({"netto": mix, "settimana": g1.lunedi_del_giorno(giorni)}).groupby("settimana")["netto"].sum()
            mix_s = pd.DataFrame({"netto": mix_s, "netto_doppio": mix_s, "giro": 0.0, "spese": 0.0, "funding": 0.0, "long": 0.0,
                                  "short": 0.0, "monete": 1})
            em50 = te.numeri_settimana(mix_s[mix_s.index >= se.INIZIO]["netto"])
            e["miscela_50_50_G1"] = {k: em50[k] for k in ("annuo", "sharpe", "discesa_max")}
            e["solo_G1_stesse_settimane"] = {k: te.numeri_settimana(sett_g1[sett_g1.index >= se.INIZIO]["netto"])[k]
                                             for k in ("annuo", "sharpe", "discesa_max")}
            daily[nome], sett_all[nome], W_all[nome] = lim, sett, W
            ris[nome] = e
        except Exception as ex:  # noqa: BLE001
            registra(ID, nome, par, "giorno", 0, {}, "errore", note=repr(ex), seme=SEME)
            ris[nome] = {"errore": repr(ex)}
    buone = [n for n in ris if "errore" not in ris[n]]
    sr_v = sr_base + [ris[n]["intero"]["sharpe"] for n in buone]
    for nome in buone:
        e = ris[nome]
        i = e["intero"]
        e["t"] = i["sharpe"] * math.sqrt(i["settimane"] / 52)
        e["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr_v, 52, n_prove=N_PROVE)
        e["sharpe_corretto_solo_gruppi"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr_base, 52,
                                                              n_prove=N_PROVE)
        anni = e["per_anno"]
        perche = []
        if not i["annuo"] > 0:
            perche.append("netto non positivo")
        if not all(v > 0 for v in anni.values()):
            perche.append(f"anni positivi {sum(1 for v in anni.values() if v > 0)}/{len(anni)}")
        if e["t"] < SOGLIA_T:
            perche.append(f"t {e['t']:.2f} sotto 3")
        if e["sharpe_corretto"] < SOGLIA_SHARPE_CORRETTO:
            perche.append(f"Sharpe corretto {e['sharpe_corretto']:.2f} sotto 0,80")
        e["esito"] = "passa l'esame: va a backtest-auditor" if not perche else "non passa: " + "; ".join(perche)
        par = {"finestra_giorni": FINESTRE[nome], "banda": "20/40", "pesi": "inverso volatilita 30 giorni", "blocchi_minuti": 5,
               "ordine": "limite 0,02% un'ora poi mercato 0,05%", "dal": "2021-01-04", "al": "2026-10-31", "N_prove": N_PROVE}
        registra(ID, nome, par, "giorno (somme per settimana)", int(e["giorni"]),
                 {k: round(float(v), 4) for k, v in {"annuo": i["annuo"], "sharpe": i["sharpe"], "t": e["t"],
                                                     "sharpe_corretto": e["sharpe_corretto"], "discesa_max": i["discesa_max"],
                                                     "spese_annue": e["spese_annue"], "corr_G1_giorni": e["correlazione_G1_giornaliera"]}.items()}
                 | {"anni_positivi": f"{sum(1 for v in anni.values() if v > 0)}/{len(anni)}"}, e["esito"], seme=SEME,
                 note=f"{e['ordini']['variazioni']} variazioni di peso; monete con segnale mediana {e['monete_con_segnale_mediana']:.0f}")
    (OUT / "esame.json").write_text(json.dumps({"letture": LETTURE, "N_prove": N_PROVE, "G1_riferimento": ris.get("v7", {}).get("solo_G1_stesse_settimane"),
                                                **ris}, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    scrivi(ris, buone)
    return ris


def scrivi(ris: dict, buone: list):
    pc = lambda v: f"{100 * v:+.1f}%"  # noqa: E731
    r = ["# Programma 7 — risultati dell'ottantottesima prova (prova 150: l'asimmetria dei minuti)", "",
         "Regole in `OTTANTOTTESIMA.md` (commit 50f97e7, scritte prima del calcolo). Codice: `ottantottesima.py`; dati completi: "
         "`risultati_ottantottesima/esame.json`; registro delle varianti: `research/trials/ottantottesima.csv`. Dal 4 gennaio 2021 al 31 ottobre 2026.", "",
         "## Letture scelte dove le regole lasciano margine (da confermare)", ""] + [f"* {x}" for x in LETTURE]
    r += [f"* Sharpe corretto (probabilita', `terza.sharpe_corretto`, 52 settimane): N = {N_PROVE} (306 + 2 varianti); la varianza viene dagli Sharpe "
          "dei gruppi del conto (`asticella`) piu' le 2 varianti.", "",
          "## Le 2 varianti", "",
          "| variante | rendimento l'anno | Sharpe | anni positivi | t | Sharpe corretto | giro (media sett.) | spese l'anno | a mercato (rend., Sharpe) | corr. G1 giorni | corr. segnali (rango) | esito |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for n in buone:
        e = ris[n]; i = e["intero"]; a = e["per_anno"]; m = e["a_mercato"]
        r.append(f"| {n} ({FINESTRE[n]} giorni) | {pc(i['annuo'])} | {i['sharpe']:.2f} | {sum(1 for v in a.values() if v > 0)}/{len(a)} | {e['t']:.2f} | "
                 f"{e['sharpe_corretto']:.2f} | {e['giro_medio']:.2f} | {100 * e['spese_annue']:.1f}% | {pc(m['annuo'])}, {m['sharpe']:.2f} | "
                 f"{e['correlazione_G1_giornaliera']:.2f} | {e['correlazione_segnali_rango']:.2f} | {e['esito']} |")
    for n in ris:
        if n not in buone:
            r.append(f"| {n} | errore: {ris[n]['errore']} |")
    r += ["", "## Dettagli per variante", ""]
    for n in buone:
        e = ris[n]; i = e["intero"]
        r += [f"### {n} ({FINESTRE[n]} giorni)",
              f"* Rendimento l'anno {pc(i['annuo'])}, volatilita' {100 * i['volatilita']:.1f}%, Sharpe {i['sharpe']:.2f}, discesa {100 * i['discesa_max']:.1f}%, "
              f"{i['settimane']} settimane; netto a costi doppi per settimana {100 * e['costi_doppi']:.3f}%.",
              "* Per anno: " + ", ".join(f"{a} {pc(v)}" for a, v in e["per_anno"].items()) + ".",
              f"* Lato long {pc(e['long_annuo'])} l'anno, lato short {pc(e['short_annuo'])}, funding {pc(e['funding_annuo'])} l'anno (come somme sull'anno, prima dei costi).",
              f"* Spese {100 * e['spese_annue']:.1f}% l'anno (limite); tutto a mercato {100 * e['a_mercato']['spese_annue']:.1f}%. Ordini: {e['ordini']}.",
              f"* Movimenti: {e['movimenti']['entrate_al_giorno']:.1f} entrate e {e['movimenti']['uscite_al_giorno']:.1f} uscite al giorno; durata media "
              f"{e['movimenti']['durata_media_giorni']:.1f} giorni; monete con segnale (mediana) {e['monete_con_segnale_mediana']:.0f}; giorni con posizioni {e['giorni_con_posizioni']} su {e['giorni']}.",
              f"* Correlazione con G1: rendimenti giornalieri {e['correlazione_G1_giornaliera']:.2f}, settimanali {e['correlazione_G1_settimanale']:.2f}; "
              f"correlazione di rango dei due segnali (media dei giorni) {e['correlazione_segnali_rango']:.2f}.",
              f"* Miscela 50/50 con G1 (solo informativa, rendimenti netti): {pc(e['miscela_50_50_G1']['annuo'])} l'anno, Sharpe {e['miscela_50_50_G1']['sharpe']:.2f}, "
              f"discesa {100 * e['miscela_50_50_G1']['discesa_max']:.1f}%; G1 da solo sugli stessi giorni {pc(e['solo_G1_stesse_settimane']['annuo'])}, "
              f"Sharpe {e['solo_G1_stesse_settimane']['sharpe']:.2f}.",
              f"* Sharpe corretto {e['sharpe_corretto']:.2f} (solo con i gruppi {e['sharpe_corretto_solo_gruppi']:.2f}); t {e['t']:.2f}.",
              f"* **Esito: {e['esito']}**", ""]
    (QUI / "RISULTATI_OTTANTOTTESIMA.md").write_text("\n".join(r) + "\n", encoding="utf-8")


if __name__ == "__main__":
    fase = sys.argv[1] if len(sys.argv) > 1 else "esegui"
    if fase == "raccogli":
        raccogli()
    else:
        esegui()
    print("OTTANTOTTESIMA FINITA", fase, flush=True)
