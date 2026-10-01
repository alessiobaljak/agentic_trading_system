'use client';

/**
 * Il REPORT GIORNALIERO (1 ott 2026), letto dalla dashboard.
 *
 * Lo scrive `scripts/report_giornaliero.py` sulla macchina dopo ogni giro del
 * gate (`bot/learning/report.py`): `dashboard/report_giornaliero` su Firestore
 * e lo specchio RTDB `/report_giornaliero`. La struttura e' FISSA: nove
 * sezioni, sempre nello stesso ordine; qui si disegnano cosi' come arrivano.
 */
import { creaDocumentoVivo, useDocumentoVivo } from './controllo';

export interface TabellaReport {
  colonne?: string[] | null;
  righe?: (string | number | null)[][] | null;
}

export interface SezioneReport {
  id?: string | null;
  titolo?: string | null;
  righe?: string[] | null;
  tabella?: TabellaReport | null;
  fonte?: string | null;
  errore?: string | null;
}

export interface DocReport {
  meta?: {
    versione_schema?: number | null;
    generato_at?: number | null;
    giorno?: string | null;
    oggi?: string | null;
    commit?: string | null;
    stato?: string | null;
  } | null;
  sezioni?: SezioneReport[] | null;
}

const storeReport = creaDocumentoVivo<DocReport>('/report_giornaliero', 'dashboard', 'report_giornaliero');

export function useReport(): { doc: DocReport | null; caricamento: boolean; etaS: number | null } {
  return useDocumentoVivo<DocReport>(storeReport);
}
