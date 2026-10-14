"""Le varianti, una alla volta e in serie: conta, registra (o scarta), esamina in costruzione, scrive il risultato.

Solo con gruppo.conta_trade_di_gruppo e gruppo.esame_di_gruppo (timeframe "1d", periodo "costruzione"; il terreno
della seconda edizione lo decide il marcatore). Per ogni variante, nell'ordine di previsioni.json:
1. se nel log c'è già il suo risultato o il suo scarto, si salta;
2. se non è ancora registrata: conta_trade_di_gruppo una volta sola, poi «scarto» (sotto 700 trade o una moneta
   oltre il 10%) oppure «registrazione» con previsione, criterio e trade stimati, PRIMA dell'esame;
3. esame_di_gruppo (riprende da solo dal file di avanzamento) e voce «risultato» con il dizionario dell'esame
   copiato così com'è.
Le voci del log hanno id progressivi presi da registro.py; una variante registrata e non ancora esaminata si
riprende dal suo id. Uso: lotto.py <nome variante> [<nome variante> ...] oppure «tutte».
"""

import hashlib
import json
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[4]
CODICE = Path(__file__).resolve().parent
sys.path.insert(0, str(RADICE))
sys.path.insert(0, str(CODICE))

from research.src import gruppo  # noqa: E402
import registro  # noqa: E402

PREVISIONI = json.loads((CODICE / "previsioni.json").read_text(encoding="utf-8"))

IDEE = {
    "A": {"modulo": "tendenza.py", "parametri": "varianti_A.json", "idea": "A — Tendenza",
          "fonte": "Moskowitz, Ooi, Pedersen, «Time Series Momentum», Journal of Financial Economics 2012; Hurst, Ooi, "
                   "Pedersen, «A Century of Evidence on Trend-Following Investing», Journal of Portfolio Management 2017; "
                   "Liu, Tsyvinski, «Risks and Returns of Cryptocurrency», Review of Financial Studies 2021",
          "meccanismo": "dopo una rottura o con rendimento e media concordi il prezzo continua per settimane: diffusione "
                        "lenta delle informazioni e flussi che seguono il prezzo"},
    "B": {"modulo": "trasversale.py", "parametri": "varianti_B.json", "idea": "B — Momentum trasversale fra monete",
          "fonte": "Liu, Tsyvinski, Wu, «Common Risk Factors in Cryptocurrency», Journal of Finance 2022; Jegadeesh, "
                   "Titman, «Returns to Buying Winners and Selling Losers», Journal of Finance 1993",
          "meccanismo": "le monete più forti (più deboli) delle settimane precedenti continuano a fare meglio (peggio) "
                        "del paniere la settimana dopo: sottoreazione e flussi che inseguono i vincitori"},
    "C": {"modulo": "ritardo.py", "parametri": "varianti_C.json", "idea": "C — Ritardo dopo un giorno forte di Bitcoin",
          "fonte": "Ciaian, Rajcaniova, Kancs, «Virtual relationships: Short- and long-run evidence from BitCoin and "
                   "altcoin markets», Journal of International Financial Markets, Institutions and Money 2018",
          "meccanismo": "dopo un giorno forte di Bitcoin le monete rimaste indietro recuperano nei giorni dopo: flussi e "
                        "notizie arrivano prima su Bitcoin"},
}


def parametri_di(nome):
    idea = IDEE[nome[0]]
    for p in json.loads((CODICE / idea["parametri"]).read_text(encoding="utf-8")):
        if p["nome"] == nome:
            q = dict(p)
            q.pop("nome")
            return idea, q
    raise KeyError(nome)


def stato_nel_log(nome):
    """(id, fatto) della variante: id della registrazione o dello scarto, fatto = ha già risultato o scarto."""
    voci = registro.voci()
    id_variante = None
    for v in voci:
        if v.get("variante") == nome and v["tipo"] in ("registrazione", "scarto"):
            id_variante = v["id"]
            if v["tipo"] == "scarto":
                return id_variante, True
    if id_variante is None:
        return None, False
    fatto = any(v["id"] == id_variante and v["tipo"] == "risultato" for v in voci)
    return id_variante, fatto


def variante_n():
    return 1 + sum(1 for v in registro.voci() if v["tipo"] == "registrazione" and v.get("tipo_test") == "variante")


def lavora(nome):
    id_variante, fatto = stato_nel_log(nome)
    if fatto:
        print(nome, "già fatta", id_variante)
        return
    idea, p = parametri_di(nome)
    modulo = CODICE / idea["modulo"]
    impronta = hashlib.sha256(modulo.read_bytes()).hexdigest()
    if id_variante is None:
        conta = gruppo.conta_trade_di_gruppo(modulo, p, "1d")
        comuni = {
            "tipo_test": "variante", "variante": nome, "idea": idea["idea"], "timeframe": "1d",
            "direzione": p["direzione"], "parametri": p, "modulo": f"codice/{idea['modulo']}",
            "impronta_modulo": impronta, "periodo": "costruzione",
            "trade_stimati": conta["trade_stimati"], "trade_stimati_per_moneta": conta["trade_stimati_per_moneta"],
            "monete_con_trade": conta["monete_con_trade"],
            "quota_moneta_piu_presente": conta["quota_moneta_piu_presente"],
            "moneta_piu_presente": conta["moneta_piu_presente"],
        }
        if conta["esito"] == "scarto":
            voce = registro.aggiungi(dict({"tipo": "scarto", "motivi": conta["motivi"],
                                           "testo": "scarto di conta_trade_di_gruppo: non consuma budget"}, **comuni))
            print(nome, "scarto", voce["id"], conta["trade_stimati"], conta["motivi"])
            return
        id_variante = registro.prossimo_id()
        registro.aggiungi(dict({
            "tipo": "registrazione", "famiglia": id_variante, "ritocco_di": None, "fonte": idea["fonte"],
            "meccanismo": idea["meccanismo"], "previsione": PREVISIONI["previsioni"][nome],
            "criterio_successo": PREVISIONI["criterio_successo"],
            "stima_trade_validazione": conta["stima_trade_validazione"], "variante_n": variante_n(),
        }, **comuni), id_voce=id_variante)
        print(nome, "registrata", id_variante, conta["trade_stimati"])
    esame = gruppo.esame_di_gruppo(modulo, p, "1d", "costruzione", id_variante)
    registro.aggiungi(dict({"tipo": "risultato", "variante": nome, "impronta_modulo": impronta}, **esame),
                      id_voce=id_variante)
    print(nome, "risultato", id_variante, "t contro (b)", esame.get("baseline_b", {}).get("t"))


def main():
    nomi = PREVISIONI["ordine"] if sys.argv[1:] == ["tutte"] else sys.argv[1:]
    for nome in nomi:
        lavora(nome)
    print("fatto")


if __name__ == "__main__":
    main()
