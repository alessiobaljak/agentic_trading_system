"""I costi di un'operazione (`METODO.md`, sezione 5).

Nessun valore predefinito per le commissioni: il broker non è ancora scelto, e un numero non
verificato sul suo listino non entra nel codice. Chi usa il simulatore li passa.
"""
from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Costi:
    # commissione = max(minima, per_azione * azioni, percentuale * valore), al massimo `massima_percentuale` del valore
    per_azione: float = 0.0
    minima: float = 0.0
    percentuale: float = 0.0
    massima_percentuale: float | None = None
    # metà dello scarto fra acquisto e vendita, in proporzione del prezzo (misurato: `stock/dati/scarto.py`)
    mezzo_scarto: float = 0.0
    # costo in più per gli ordini a mercato e gli stop (impatto, ritardo), in proporzione del prezzo
    slittamento: float = 0.0
    # interesse annuo sul valore delle posizioni allo scoperto (prestito dei titoli)
    prestito_annuo: float = 0.0

    def commissione(self, azioni: float, prezzo: float) -> float:
        azioni = abs(azioni)
        if azioni == 0:
            return 0.0
        valore = azioni * prezzo
        c = max(self.minima, self.per_azione * azioni, self.percentuale * valore)
        if self.massima_percentuale is not None:
            c = min(c, self.massima_percentuale * valore)
        return c

    def raddoppiati(self) -> "Costi":
        """Tutti i costi per due: ogni risultato si mostra anche così (se regge solo con i costi
        bassi, non regge)."""
        return replace(self, per_azione=2 * self.per_azione, minima=2 * self.minima,
                       percentuale=2 * self.percentuale,
                       massima_percentuale=None if self.massima_percentuale is None else 2 * self.massima_percentuale,
                       mezzo_scarto=2 * self.mezzo_scarto, slittamento=2 * self.slittamento,
                       prestito_annuo=2 * self.prestito_annuo)
