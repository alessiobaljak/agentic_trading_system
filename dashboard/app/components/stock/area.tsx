'use client';

import type { Area } from '../aree';
import Azioni from './Azioni';

/**
 * L'area Azioni della plancia: le pagine del menu a sinistra le dichiara la sessione «trading stock», qui, senza toccare il guscio
 * (dashboard/GUIDA_SCHEDA_AZIONI.md). Una pagina = una riga: `{ id, nome, icona?, Contenuto }`; la prima è la schermata principale.
 * L'indirizzo è #azioni/<id>/<resto…>; `Contenuto` riceve `resto` e `vai`. Oggi una sola pagina, il segnaposto.
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
  ],
};
