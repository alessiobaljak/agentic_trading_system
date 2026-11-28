'use client';

import type { Area, PropsPagina } from '../aree';
import Azioni from './Azioni';
import Dettagli, { SCELTE_AZIONI } from './Dettagli';

/**
 * L'area Azioni della plancia: le pagine del menu a sinistra le dichiara la sessione «trading stock», qui, senza toccare il guscio
 * (dashboard/GUIDA_SCHEDA_AZIONI.md). Una pagina = una riga: `{ id, nome, icona?, Contenuto }`; la prima è la schermata principale.
 * Speculare all'area Crypto (richiesta del proprietario del 28 novembre 2026): la schermata principale Strategie, poi Dettagli (una
 * strategia alla volta, #azioni/dettagli/<candela, miscela, prova45>), che ha preso il posto della vecchia pagina Operazioni.
 */
function PaginaDettagli({ resto, vai }: PropsPagina) {
  return <Dettagli pagina={resto[0] ?? SCELTE_AZIONI[0].pagina} onPagina={(p) => vai([p], { sostituisci: true })} />;
}

const icona = (d: React.ReactNode) => (
  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round"
    strokeLinejoin="round" aria-hidden="true">{d}</svg>
);

export const AREA_AZIONI: Area = {
  id: 'azioni',
  nome: 'Azioni',
  pagine: [
    { id: 'strategie', nome: 'Strategie', icona: icona(<path d="M3 17l5-6 4 3 5-7 4 4" />), Contenuto: () => <Azioni /> },
    // la stessa icona dei Dettagli delle crypto
    { id: 'dettagli', nome: 'Dettagli', icona: icona(<><path d="M4 20V10M10 20V4M16 20v-7M22 20H2" /></>), Contenuto: PaginaDettagli },
  ],
};
