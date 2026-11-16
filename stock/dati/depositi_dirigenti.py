"""Gli acquisti dei dirigenti con l'**ora vera** del deposito alla SEC (prova 36, `stock/prove/P036_dirigenti_subito.md`).

    python -m stock.dati.depositi_dirigenti      # scrive stock/prove/dati/P036_depositi.csv.gz (dati pubblici della SEC, niente prezzi)

Il modulo 4 è l'annuncio stesso: il pubblico sa dell'acquisto quando la SEC lo pubblica, cioè all'accettazione
(`acceptanceDateTime` nell'elenco dei depositi dell'azienda, https://data.sec.gov/submissions/CIK##########.json e i file
«-submissions-NNN.json»). Per i comunicati sui risultati (8-K) l'ora del deposito non vale (`stock/dati/bilanci.py`: il comunicato
esce prima del modulo); per il modulo 4 non c'è un comunicato prima. Le operazioni vengono dalle raccolte trimestrali della SEC
(`stock/dati/dirigenti.py`): acquisti sul mercato (codice P, acquisito) di dirigenti o consiglieri, sommati per modulo.

Si usano gli elenchi dei depositi già in `~/stock_dati/sec` (le aziende dell'S&P 500 delle prove 20 e 30); un modulo di un'azienda
senza elenco resta fuori, e il numero si stampa.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from stock.dati.dirigenti import cartella

SEC = Path.home() / "stock_dati" / "sec"
USCITA = Path(__file__).resolve().parents[1] / "prove" / "dati" / "P036_depositi.csv.gz"


def ore_di_accettazione(cartella_sec: Path = SEC) -> dict[str, str]:
    """Numero del deposito → ora di accettazione (testo ISO, UTC), per i moduli 4 degli elenchi in cache."""
    ora: dict[str, str] = {}
    for f in sorted(cartella_sec.glob("CIK*.json")):
        j = json.loads(f.read_text())
        r = j["filings"]["recent"] if "filings" in j else j
        for a, fo, t in zip(r["accessionNumber"], r["form"], r["acceptanceDateTime"]):
            if fo == "4":
                ora[a] = t
    return ora


def acquisti_per_modulo(dal: int, al: int, cartella_345: Path | None = None) -> pd.DataFrame:
    """Un modulo 4 per riga: numero, simbolo (quello scritto nel modulo, cioè quello di allora), valore degli acquisti sul mercato
    di dirigenti o consiglieri, prezzo medio, giorno dell'operazione. Solo i moduli depositati dal 1° gennaio `dal` al 31 dicembre `al`."""
    base = cartella_345 or cartella()
    pezzi = []
    for d in sorted(p for p in base.iterdir() if p.is_dir()):
        kw = dict(sep="\t", dtype=str, keep_default_na=False)
        sub = pd.read_csv(d / "SUBMISSION.tsv", usecols=["ACCESSION_NUMBER", "FILING_DATE", "DOCUMENT_TYPE", "ISSUERTRADINGSYMBOL"], **kw)
        own = pd.read_csv(d / "REPORTINGOWNER.tsv", usecols=["ACCESSION_NUMBER", "RPTOWNER_RELATIONSHIP"], **kw)
        tr = pd.read_csv(d / "NONDERIV_TRANS.tsv", usecols=["ACCESSION_NUMBER", "TRANS_DATE", "TRANS_CODE", "TRANS_ACQUIRED_DISP_CD",
                                                            "TRANS_SHARES", "TRANS_PRICEPERSHARE"], **kw)
        sub = sub[sub["DOCUMENT_TYPE"] == "4"]
        rel = own.groupby("ACCESSION_NUMBER")["RPTOWNER_RELATIONSHIP"].apply(",".join)
        dirigente = set(rel[rel.str.contains("Officer|Director", regex=True)].index)
        tr = tr[(tr["TRANS_CODE"] == "P") & (tr["TRANS_ACQUIRED_DISP_CD"] == "A") & tr["ACCESSION_NUMBER"].isin(dirigente)]
        azioni = pd.to_numeric(tr["TRANS_SHARES"], errors="coerce")
        tr = tr.assign(azioni=azioni, valore=azioni * pd.to_numeric(tr["TRANS_PRICEPERSHARE"], errors="coerce")).dropna(subset=["valore"])
        tr = tr[tr["azioni"] > 0]
        g = tr.groupby("ACCESSION_NUMBER").agg(valore=("valore", "sum"), azioni=("azioni", "sum"), giorno_op=("TRANS_DATE", "max"))
        x = sub.merge(g, left_on="ACCESSION_NUMBER", right_index=True)
        pezzi.append(x)
    df = pd.concat(pezzi, ignore_index=True)
    anno = pd.to_datetime(df["FILING_DATE"], format="%d-%b-%Y").dt.year
    df = df[(anno >= dal) & (anno <= al)].drop_duplicates("ACCESSION_NUMBER")
    out = pd.DataFrame({
        "numero": df["ACCESSION_NUMBER"],
        "simbolo": df["ISSUERTRADINGSYMBOL"].str.upper().str.strip().str.replace("-", ".", regex=False),
        "valore": df["valore"].round(2),
        "prezzo_op": (df["valore"] / df["azioni"]).round(4),
        "giorno_op": pd.to_datetime(df["giorno_op"], format="%d-%b-%Y", errors="coerce").dt.date,
    })
    return out[out["simbolo"] != ""].reset_index(drop=True)


def con_ora(acquisti: pd.DataFrame, ore: dict[str, str]) -> tuple[pd.DataFrame, int]:
    """Aggiunge l'ora di accettazione (UTC); toglie e conta i moduli senza ora."""
    a = acquisti.assign(accettato=acquisti["numero"].map(ore))
    senza = int(a["accettato"].isna().sum())
    a = a.dropna(subset=["accettato"])
    a["accettato"] = pd.to_datetime(a["accettato"], utc=True)
    return a.sort_values(["accettato", "numero"]).reset_index(drop=True), senza


def main() -> None:
    from stock.prove.p028 import decisioni
    from stock.prove.p034 import membri_al
    fini, membri = decisioni()
    tutti = acquisti_per_modulo(2016, 2024)
    ore = ore_di_accettazione()
    a, _ = con_ora(tutti, ore)
    ny = a["accettato"].dt.tz_convert("America/New_York").dt.date
    a = a[[s in membri_al(g, fini, membri) for s, g in zip(a["simbolo"], ny)]].reset_index(drop=True)
    # i moduli senza ora di aziende che erano nell'indice (giorno del deposito dalla raccolta della SEC): il buco della cache
    senza = tutti[~tutti["numero"].isin(a["numero"]) & ~tutti["numero"].isin(set(ore))]
    nell_indice_senza = sum(s in membri_al(g, fini, membri) for s, g in zip(senza["simbolo"], senza["giorno_op"].fillna(fini[0])))
    a["accettato"] = a["accettato"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    USCITA.parent.mkdir(parents=True, exist_ok=True)
    a.to_csv(USCITA, index=False)
    print(f"moduli 2016-2024 con acquisti di dirigenti: {len(tutti)}; nell'S&P 500 al giorno del deposito, con l'ora {len(a)} "
          f"(da 100'000 dollari {(a['valore'] >= 100_000).sum()}); senza ora ma con un simbolo dell'indice al giorno dell'operazione "
          f"{nell_indice_senza} → {USCITA.name}")


if __name__ == "__main__":
    main()
