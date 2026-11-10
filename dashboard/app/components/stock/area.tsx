'use client';

import type { Area } from '../aree';
import Azioni from './Azioni';
import Operazioni from './Operazioni';

/**
 * L'area Azioni della plancia: le pagine del menu a sinistra le dichiara la sessione «trading stock», qui, senza toccare il guscio
 * (dashboard/GUIDA_SCHEDA_AZIONI.md). Una pagina = una riga: `{ id, nome, icona?, Contenuto }`; la prima è la schermata principale.
 * L'indirizzo è #azioni/<id>/<resto…>; `Contenuto` riceve `resto` e `vai`. Le strategie (valore, curve, posizioni) e le operazioni
 * giorno per giorno della misura in avanti sul conto demo (stock/avanti/).
 */
export const AREA_AZIONI: Area = {
  id: 'azioni',
  nome: 'Azioni',
  pagine: [
    {
      id: 'strategie',
      nome: 'Strategie',
      icona: (
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round"
          strokeLinejoin="round" aria-hidden="true"><path d="M3 17l5-6 4 3 5-7 4 4" /></svg>
      ),
      Contenuto: () => <Azioni />,
    },
    {
      id: 'operazioni',
      nome: 'Operazioni',
      icona: (
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round"
          strokeLinejoin="round" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h10" /></svg>
      ),
      Contenuto: () => <Operazioni />,
    },
  ],
};
