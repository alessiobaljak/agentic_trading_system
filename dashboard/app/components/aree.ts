/**
 * LE AREE DELLA PLANCIA, in un punto solo (10 nov 2026, il proprietario: «In alto vedrei solo Crypto e Stock o altre che magari
 * creiamo in futuro, quando clicchi su una si apre la schermata principale e sulla sinistra hai il menu con i diversi entry point per
 * la singola dashboard»). Per un'area nuova: una cartella sua in components/ con il suo `area.tsx` (vedi crypto/area.tsx e
 * stock/area.tsx) e una riga qui sotto. Il guscio (DashboardShell.tsx) non si tocca.
 *
 * Gli indirizzi sono `#<area>/<pagina>/<resto…>`: per esempio #crypto/strategie, #crypto/dettagli/g1demo, #azioni/strategie.
 */
import type { ComponentType, ReactNode } from 'react';
import { AREA_CRYPTO } from './crypto/area';
import { AREA_AZIONI } from './stock/area';

export interface PropsPagina {
  /** quello che nell'indirizzo viene dopo la pagina (in #crypto/dettagli/g1 è ['g1']) */
  resto: string[];
  /** cambia il resto dell'indirizzo restando nella stessa pagina; `sostituisci` non lascia un passo nella cronologia */
  vai: (resto: string[], opzioni?: { sostituisci?: boolean }) => void;
}

export interface Pagina {
  /** il nome nell'indirizzo: minuscolo, senza spazi */
  id: string;
  /** il nome nel menu a sinistra */
  nome: string;
  /** un'icona piccola per il menu (svg 24×24 con stroke currentColor), facoltativa */
  icona?: ReactNode;
  Contenuto: ComponentType<PropsPagina>;
}

export interface Area {
  /** il nome nell'indirizzo */
  id: string;
  /** il nome in alto */
  nome: string;
  /** la prima è la schermata principale dell'area */
  pagine: Pagina[];
  /** facoltativo: mostrato in cima a tutte le pagine dell'area (per Crypto: bot vivo e allarmi del demo) */
  Testata?: ComponentType;
}

export const AREE: Area[] = [AREA_CRYPTO, AREA_AZIONI];
