'use client';

/**
 * Il BACKLOG letto dalla dashboard (1 ott 2026, backlog J2).
 *
 * Lo scrive `scripts/report_giornaliero.py` sulla macchina dopo ogni giro del
 * gate, leggendo `docs/backlog.md` (una fonte sola, niente da aggiornare a
 * mano): `dashboard/backlog` su Firestore e lo specchio RTDB `/backlog`.
 */
import { creaDocumentoVivo, useDocumentoVivo } from './controllo';

export interface VoceBacklog {
  sigla?: string | null;
  titolo?: string | null;
  testo?: string | null;
}

export interface GruppoBacklog {
  numero?: number | null;
  nome?: string | null;
  cosa_serve?: string | null;
  voci?: VoceBacklog[] | null;
}

export interface DocBacklog {
  meta?: {
    versione_schema?: number | null;
    generato_at?: number | null;
    fonte?: string | null;
    commit?: string | null;
    errore?: string | null;
  } | null;
  aggiornato?: string | null;
  gruppi?: GruppoBacklog[] | null;
  aspetta_si?: VoceBacklog[] | null;
  n_voci?: number | null;
}

const storeBacklog = creaDocumentoVivo<DocBacklog>('/backlog', 'dashboard', 'backlog');

export function useBacklog(): { doc: DocBacklog | null; caricamento: boolean; etaS: number | null } {
  return useDocumentoVivo<DocBacklog>(storeBacklog);
}
