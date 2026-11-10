'use client';

import { STRATEGIE, giornoUtc, useAdesso, useSerie, useStrategie } from '../../lib/strategie';
import CurveA100 from './CurveA100';
import DemoControPaper from './DemoControPaper';
import RigaStato from './RigaStato';
import SchedaStrategia from './SchedaStrategia';

/**
 * La prima schermata (10 nov 2026): in cima il bot vivo e gli allarmi del demo; poi le strategie con ordini veri (G1 sul conto demo,
 * con i pulsanti «chiudi tutto» e «riparti», e il conto vero, spento) ben separate da quelle simulate nel paper (G1, G1 neutra, G11,
 * F5, Eventi); poi le curve messe a 100 alla stessa data e G1 demo contro G1 paper giorno per giorno. Tutto in diretta da Firebase.
 */
export default function Strategie() {
  const dati = useStrategie();
  const adesso = useAdesso();
  const serie = useSerie(dati.rami);
  const veri = STRATEGIE.filter((s) => s.tipo !== 'paper');
  const paper = STRATEGIE.filter((s) => s.tipo === 'paper');
  const aggiornatoPaper = dati.rami.paper_g1?.stato?.aggiornato;

  return (
    <>
      <RigaStato dati={dati} adesso={adesso} />

      <h2 className="cr-gruppo-titolo">Ordini veri <span>sul conto demo di Binance (soldi finti) e sul conto vero</span></h2>
      <div className="cr-griglia-veri">
        {veri.map((s) => (
          <SchedaStrategia key={s.ramo} def={s} dati={dati.rami[s.ramo]} adesso={adesso}
            demo={s.tipo === 'demo' ? dati.demo : undefined} />
        ))}
      </div>

      <h2 className="cr-gruppo-titolo">Paper <span>ordini simulati con i prezzi veri, 10.000 dollari virtuali ciascuna</span></h2>
      <div className="cr-griglia">
        {paper.map((s) => (
          <SchedaStrategia key={s.ramo} def={s} dati={dati.rami[s.ramo]} adesso={adesso} />
        ))}
      </div>

      <CurveA100 serie={serie} oggi={aggiornatoPaper ? giornoUtc(aggiornatoPaper) : giornoUtc(adesso)} />

      <DemoControPaper paper={dati.rami.paper_g1} demo={dati.rami.demo_binance} fasi={dati.demo.fasi} />

      <p className="cr-piede-pagina">
        «Oggi» è il giorno UTC in corso contro la chiusura di ieri; «giorni in guadagno» conta i giorni chiusi sopra il giorno prima.
        Posizioni, diario giorno per giorno e risultati sul passato: scheda Dettagli.
      </p>
    </>
  );
}
