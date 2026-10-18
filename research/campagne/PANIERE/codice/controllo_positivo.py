"""Controllo positivo degli strumenti (regole del gruppo, sezione 5, punto 10; lezioni/metodo.md), prima della prima variante.

Solo con gruppo.controllo_positivo, timeframe "1d", in entrambe le direzioni, con il modulo che ha l'uscita più
corta della campagna (codice/ritardo.py: uscita dopo 5 barre, stop 2,5 ATR(20), tetto 60 barre). Scrive una nota
nel log prima e una dopo (non è una variante: niente budget, niente verifica_di), e l'esito intero in
lavoro/controllo_positivo_<direzione>.json. Prima controlla gli import dei tre moduli delle varianti.
"""

import json
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[4]
CODICE = Path(__file__).resolve().parent
sys.path.insert(0, str(RADICE))
sys.path.insert(0, str(CODICE))

from research.src import gruppo  # noqa: E402
import registro  # noqa: E402

CARTELLA = CODICE.parent
MODULO = CODICE / "ritardo.py"
P = {"direzione": None, "k": 1.5, "monete_in_ritardo": 0, "giorni_deviazione": 60, "giorni_minimi_deviazione": 40,
     "barre_uscita": 5, "multiplo_atr": 2.5, "barre_atr": 20, "barre_massime": 60}


def riassunto(esame):
    b = esame.get("baseline_b", {})
    a = esame.get("baseline_a", {})
    return {
        "trade": esame.get("metriche", {}).get("trade"),
        "r_medio": esame.get("metriche", {}).get("r_medio"),
        "blocco": esame.get("blocco"),
        "numero_blocchi": esame.get("numero_blocchi", b.get("numero_blocchi")),
        "valutabile": esame.get("valutabile"),
        "t_contro_b": b.get("t"), "soglia_b": b.get("soglia"), "netta_b": b.get("netta"),
        "valutabile_b": b.get("valutabile"), "media_b": b.get("media"),
        "monete_senza_ingressi": b.get("monete_senza_ingressi"),
        "quota_trade_candidato_senza_ingressi": b.get("quota_trade_candidato_senza_ingressi"),
        "t_contro_a": a.get("t"), "soglia_a": a.get("soglia"), "netta_a": a.get("netta"),
        "valutabile_a": a.get("valutabile"), "media_a": a.get("media"),
        "effetto_grappolo": esame.get("effetto_grappolo"),
        "terreno": esame.get("opzioni", {}).get("terreno"),
    }


def main():
    for nome in ("tendenza.py", "trasversale.py", "ritardo.py"):
        gruppo.controlla_import_della_variante((CODICE / nome).read_bytes(), CODICE / nome)
    print("import ammessi nei tre moduli")
    for direzione in ("long", "short"):
        p = dict(P, direzione=direzione)
        registro.aggiungi({
            "tipo": "nota",
            "testo": (f"Controllo positivo degli strumenti, {direzione}, PRIMA del calcolo: gruppo.controllo_positivo "
                      "con codice/ritardo.py (uscita dopo 5 barre, la più corta della campagna), timeframe 1d, "
                      "costruzione, senza ritardo e con il ritardo di una barra. Previsione: senza ritardo R medio "
                      "molto positivo e t contro la (b) alto; con il ritardo t sotto la metà. Può non passare per le "
                      "monete su cui la (b) non entra o per i pochi blocchi (regole.md, sezione 6): lo riporto com'è."),
            "parametri": p,
        })
        esito = gruppo.controllo_positivo(MODULO, p, "1d", direzione, id=f"PANIERE-controllo-positivo-{direzione}")
        (CARTELLA / "lavoro" / f"controllo_positivo_{direzione}.json").write_text(
            json.dumps(esito, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        voce = {
            "tipo": "nota",
            "testo": f"Controllo positivo degli strumenti, {direzione}, esito (lavoro/controllo_positivo_{direzione}.json).",
            "passa": esito["passa"],
            "condizioni": esito["condizioni"],
            "t_senza_ritardo": esito["t_senza_ritardo"],
            "t_con_ritardo": esito["t_con_ritardo"],
            "senza_ritardo": riassunto(esito["esami"]["senza_ritardo"]),
            "con_ritardo": riassunto(esito["esami"]["con_ritardo"]),
        }
        registro.aggiungi(voce)
        print(direzione, "passa", esito["passa"], "t", esito["t_senza_ritardo"], "ritardo", esito["t_con_ritardo"])
    print("fatto")


if __name__ == "__main__":
    main()
