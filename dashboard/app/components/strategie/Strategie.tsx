'use client';

import { useMemo } from 'react';
import { STRATEGIE, giornoUtc, useAdesso, useSerie, useStrategie } from '../../lib/strategie';
import CurveA100, { type SerieCurva } from '../comuni/CurveA100';
import ConfrontoBreve from './ConfrontoBreve';
import SchedaStrategia from './SchedaStrategia';

/**
 * La prima schermata (10 nov 2026; il bot vivo e gli allarmi del demo stanno sopra, in cima a ogni pagina Crypto): le strategie con ordini veri (G1 sul conto demo,
 * con i pulsanti «chiudi tutto» e «riparti», e il conto vero, spento, con la versione del codice da approvare e i suoi comandi:
 * components/strategie/ComandiContoVero.tsx) ben separate da quelle simulate nel paper (G1, G1 neutra, G11,
 * F5, Eventi); poi le curve messe a 100 alla stessa data e G1 demo contro G1 paper dalla partenza del demo, in breve (il giorno per
 * giorno sta in Dettagli). Tutto in diretta da Firebase.
 */
export default function Strategie() {
  const dati = useStrategie();
  const adesso = useAdesso();
  const serie = useSerie(dati.rami);
  const veri = STRATEGIE.filter((s) => s.tipo !== 'paper');
  const paper = STRATEGIE.filter((s) => s.tipo === 'paper');
  const aggiornatoPaper = dati.rami.paper_g1?.stato?.aggiornato;
  const curve = useMemo<SerieCurva[]>(
    () => STRATEGIE.filter((s) => s.tipo !== 'vero').map((s) => ({ chiave: s.ramo, nome: s.nome, colore: s.colore, giorni: serie[s.ramo] ?? {} })),
    [serie],
  );

  return (
    <>
      <h2 className="cr-gruppo-titolo">Ordini veri <span>sul conto demo di Binance (soldi finti) e sul conto vero</span></h2>
      <div className="cr-griglia-veri">
        {veri.map((s) => (
          <SchedaStrategia key={s.ramo} def={s} dati={dati.rami[s.ramo]} adesso={adesso}
            demo={s.tipo === 'demo' ? dati.demo : undefined} contoVero={s.tipo === 'vero' ? dati.contoVero : undefined} />
        ))}
      </div>

      <h2 className="cr-gruppo-titolo">Paper <span>ordini simulati con i prezzi veri, 10.000 dollari virtuali ciascuna</span></h2>
      <div className="cr-griglia">
        {paper.map((s) => (
          <SchedaStrategia key={s.ramo} def={s} dati={dati.rami[s.ramo]} adesso={adesso} />
        ))}
      </div>

      <CurveA100 curve={curve} oggi={aggiornatoPaper ? giornoUtc(aggiornatoPaper) : giornoUtc(adesso)} />

      <ConfrontoBreve paper={dati.rami.paper_g1} demo={dati.rami.demo_binance} />

      <p className="cr-piede-pagina">
        «Oggi»: il giorno UTC in corso contro la chiusura di ieri · «Giorni in guadagno»: i giorni chiusi sopra il giorno prima
      </p>
    </>
  );
}
