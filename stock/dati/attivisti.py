"""I moduli 13D depositati alla SEC (prova 42, `stock/prove/P042_attivisti.md`): l'ora vera di pubblicazione, l'azienda oggetto, il
simbolo di allora. Dati pubblici della SEC, niente prezzi.

    python -m stock.prove.p042a        # gira su GitHub (azioni-ricerca), con l'indirizzo di contatto nel segreto SEC_CONTATTO

1. Gli indici trimestrali della SEC (`edgar/full-index/AAAA/QTRn/form.gz`): le righe di tipo esattamente «SC 13D» (non le correzioni
   «SC 13D/A»). Ogni deposito compare una volta per ogni codice collegato (l'azienda oggetto e chi deposita): si tiene una riga per
   numero di deposito. L'indice si riduce e si tiene in `~/stock_dati/sec/attivisti/` (le sole righe dei 13D).
2. Per ogni deposito l'intestazione (`…-index-headers.html`): l'ora di accettazione (`<ACCEPTANCE-DATETIME>`, così come la scrive la SEC),
   l'azienda oggetto («SUBJECT COMPANY») e chi deposita («FILED BY»). Le intestazioni lette si tengono in un file per trimestre, così il
   lavoro riprende da dove si è fermato.
3. Il simbolo di allora dai periodi dei moduli dei dirigenti (`stock/prove/dati/sec_simboli.csv.gz`, fatto in locale da
   `azioni_circolazione.codici_dei_moduli`): il periodo iniziato per ultimo prima del giorno del 13D, se non è finito più di 365 giorni
   prima.

L'indirizzo di contatto che la SEC chiede: solo dall'ambiente (`SEC_CONTATTO`, `dirigenti.intestazione`), mai in un file. Al massimo 4
richieste al secondo (la SEC ne ammette 10).
"""
from __future__ import annotations

import gzip
import html
import json
import re
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import requests

from stock.dati.archivio import cartella_dati
from stock.dati.dirigenti import intestazione

QUI = Path(__file__).resolve().parents[1] / "prove" / "dati"
INDICE = "https://www.sec.gov/Archives/edgar/full-index/{anno}/QTR{q}/form.gz"
TESTA = "https://www.sec.gov/Archives/edgar/data/{cik}/{nodash}/{numero}-index-headers.html"
ELENCO = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
DAL, FINO = date(2016, 1, 4), date(2024, 11, 29)
PAUSA = 0.25
_ultimo = [0.0]


def _richiesta(url: str) -> requests.Response:
    for n in range(5):
        attesa = PAUSA - (time.monotonic() - _ultimo[0])
        if attesa > 0:
            time.sleep(attesa)
        _ultimo[0] = time.monotonic()
        try:
            r = requests.get(url, headers=intestazione(), timeout=120)
        except (requests.ConnectionError, requests.Timeout):
            if n == 4:
                raise
            time.sleep(2 ** (n + 2))
            continue
        if r.status_code in (200, 404):
            return r
        time.sleep(2 ** (n + 1))
    r.raise_for_status()
    return r


# --- senza rete ---------------------------------------------------------------------------------------------------------------------
_RIGA = re.compile(r"^SC 13D\s{2,}(?P<nome>.+?)\s{2,}(?P<cik>\d+)\s+(?P<giorno>\d{4}-\d{2}-\d{2})\s+(?P<file>edgar/\S+)\s*$")


def righe_13d(testo: str) -> list[dict]:
    """Dalle righe dell'indice `form.idx`, i soli «SC 13D» (non «/A»): codice, nome, giorno, numero del deposito."""
    out = []
    for riga in testo.splitlines():
        m = _RIGA.match(riga)
        if m:
            numero = m["file"].rsplit("/", 1)[-1].removesuffix(".txt")
            out.append({"cik": int(m["cik"]), "nome": m["nome"].strip(), "giorno": m["giorno"], "numero": numero})
    return out


def _sezione(testo: str, titolo: str) -> tuple[int | None, str | None]:
    i = testo.find(titolo)
    if i < 0:
        return None, None
    resto = testo[i + len(titolo):]
    fine = re.search(r"\n(SUBJECT COMPANY|FILED BY|FILER|GROUP MEMBERS?):", resto)
    pezzo = resto[: fine.start()] if fine else resto
    c = re.search(r"CENTRAL INDEX KEY:\s*(\d+)", pezzo)
    n = re.search(r"COMPANY CONFORMED NAME:\s*(.+)", pezzo)
    return (int(c[1]) if c else None), (n[1].strip() if n else None)


def leggi_intestazione(pagina: str) -> dict:
    """Dall'intestazione di un deposito: l'ora di accettazione (testo «AAAAMMGGhhmmss» com'è), l'oggetto e chi deposita."""
    t = html.unescape(re.sub(r"<(?!ACCEPTANCE-DATETIME)[^>]*>", "", html.unescape(pagina)))
    a = re.search(r"<ACCEPTANCE-DATETIME>\s*(\d{14})", t)
    tipo = re.search(r"CONFORMED SUBMISSION TYPE:\s*(\S.*)", t)
    oggetto, nome_oggetto = _sezione(t, "SUBJECT COMPANY:")
    chi, nome_chi = _sezione(t, "FILED BY:")
    return {"accettazione": a[1] if a else None, "tipo": tipo[1].strip() if tipo else None, "oggetto": oggetto,
            "nome_oggetto": nome_oggetto, "chi": chi, "nome_chi": nome_chi}


def simbolo_al(periodi: list[tuple[date, date, str]], giorno: date, finestra: int = 365) -> str | None:
    """`periodi` di un codice: (dal, al, simbolo) in ordine di inizio. Il simbolo del periodo iniziato per ultimo prima del giorno, se
    non è finito più di `finestra` giorni prima."""
    prima = [p for p in periodi if p[0] < giorno]
    if not prima:
        return None
    dal, al, s = max(prima, key=lambda p: (p[0], p[1]))
    return s if (giorno - min(al, giorno)).days <= finestra else None


def carica_simboli() -> dict[int, list[tuple[date, date, str]]]:
    s = pd.read_csv(QUI / "sec_simboli.csv.gz", dtype={"simbolo": str}, keep_default_na=False)
    s["dal"], s["al"] = pd.to_datetime(s["dal"]).dt.date, pd.to_datetime(s["al"]).dt.date
    return {int(k): sorted(zip(g["dal"], g["al"], g["simbolo"])) for k, g in s.groupby("cik")}


# --- con la rete --------------------------------------------------------------------------------------------------------------------
def cartella() -> Path:
    p = cartella_dati() / "sec" / "attivisti"
    p.mkdir(parents=True, exist_ok=True)
    return p


def indice(anno: int, q: int) -> pd.DataFrame:
    f = cartella() / f"indice_{anno}q{q}.csv"
    if f.exists():
        return pd.read_csv(f, dtype={"numero": str})
    r = _richiesta(INDICE.format(anno=anno, q=q))
    r.raise_for_status()
    df = pd.DataFrame(righe_13d(gzip.decompress(r.content).decode("latin-1")), columns=["cik", "nome", "giorno", "numero"])
    df.to_csv(f, index=False)
    return df


def intestazioni(anno: int, q: int, fine: float) -> tuple[pd.DataFrame, bool]:
    """Le intestazioni dei 13D del trimestre (riprende dal file); il secondo valore dice se il trimestre è completo."""
    idx = indice(anno, q).drop_duplicates("numero")
    f = cartella() / f"teste_{anno}q{q}.csv"
    fatte = pd.read_csv(f, dtype={"numero": str, "accettazione": str}) if f.exists() else pd.DataFrame()
    visti = set(fatte["numero"]) if len(fatte) else set()
    nuove = []
    for r in idx.itertuples():
        if r.numero in visti:
            continue
        if time.monotonic() > fine:
            break
        x = _richiesta(TESTA.format(cik=r.cik, nodash=r.numero.replace("-", ""), numero=r.numero))
        d = leggi_intestazione(x.text) if x.status_code == 200 else {}
        nuove.append({"numero": r.numero, "giorno": r.giorno, "stato": x.status_code, **d})
        if len(nuove) == 3 and not len(fatte) and all(n.get("accettazione") is None for n in nuove):
            raise SystemExit(f"le prime 3 intestazioni non si leggono (stati {[n['stato'] for n in nuove]}): il formato è cambiato?")
    tutte = pd.concat([fatte, pd.DataFrame(nuove)], ignore_index=True)
    tutte.to_csv(f, index=False)
    return tutte, len(tutte) >= len(idx)


def controllo_ore(depositi: pd.DataFrame, quanti: int = 8) -> list[str]:
    """Per alcuni depositi del 2024: l'ora dell'intestazione contro `acceptanceDateTime` dell'elenco dei depositi dell'azienda oggetto."""
    righe = []
    for r in depositi[depositi["giorno"] >= "2024-01-01"].head(quanti).itertuples():
        x = _richiesta(ELENCO.format(cik=int(r.oggetto)))
        if x.status_code != 200:
            continue
        rec = x.json()["filings"]["recent"]
        for a, t in zip(rec["accessionNumber"], rec["acceptanceDateTime"]):
            if a == r.numero:
                testa = datetime.strptime(r.accettazione, "%Y%m%d%H%M%S")
                elenco = datetime.fromisoformat(t.replace("Z", "+00:00")).replace(tzinfo=None)
                righe.append(f"{r.numero}: intestazione {testa:%Y-%m-%d %H:%M:%S}, elenco {t} "
                             f"(differenza {(testa - elenco) / timedelta(hours=1):+.2f} ore)")
    return righe


def main(argv: list[str]) -> dict:
    minuti = float(argv[argv.index("--minuti") + 1]) if "--minuti" in argv else 300
    fine = time.monotonic() + 60 * minuti
    pezzi, completo = [], True
    for anno in range(DAL.year, FINO.year + 1):
        for q in (1, 2, 3, 4):
            t, ok = intestazioni(anno, q, fine)
            pezzi.append(t)
            completo &= ok
            print(f"{anno} T{q}: intestazioni {len(t)}{'' if ok else ' (non finito)'}", flush=True)
    d = pd.concat(pezzi, ignore_index=True)
    d = d[d["accettazione"].notna() & d["oggetto"].notna()].copy()
    d["oggetto"] = d["oggetto"].astype(int)
    d = d[(d["giorno"] >= DAL.isoformat()) & (d["giorno"] <= FINO.isoformat()) & (d["tipo"] == "SC 13D")]
    stessa = d["chi"].notna() & (d["chi"] == d["oggetto"])
    d = d[~stessa].copy()
    simboli = carica_simboli()
    d["simbolo"] = [simbolo_al(simboli.get(int(k), []), date.fromisoformat(g)) for k, g in zip(d["oggetto"], d["giorno"])]
    return {"depositi": d, "stessa": int(stessa.sum()), "completo": completo, "controllo": controllo_ore(d) if completo else []}


if __name__ == "__main__":
    print(json.dumps({k: (len(v) if isinstance(v, pd.DataFrame) else v) for k, v in main(sys.argv[1:]).items()}))
