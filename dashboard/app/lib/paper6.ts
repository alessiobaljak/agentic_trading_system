'use client';

/**
 * Il PAPER DEL PROGRAMMA 6 letto dalla dashboard (20 ott 2026).
 *
 * Le candidate del programma 6 (research/programma6/paper/) si calcolano ogni mattina fuori dalla macchina, dai dati
 * pubblici di Binance del giorno prima; `scripts/pubblica_paper6.py`, lanciato da GitHub Actions, scrive il documento
 * in RTDB `/paper6` e in Firestore `dashboard/paper6`. Niente soldi veri, niente ordini: e' una misura.
 */
import { creaDocumentoVivo, useDocumentoVivo } from './controllo';

export interface CandidataPaper6 {
  nome?: string | null;
  descrizione?: string | null;
  periodi?: number | null;
  unita?: string | null;
  totale?: number | null;
  sharpe?: number | null;
  ultimo?: { data?: string | null; netto?: number | null } | null;
}

export interface PosizionePaper6 {
  moneta?: string | null;
  peso?: number | null;
}

export interface DocPaper6 {
  meta?: { versione_schema?: number | null; generato_at?: number | null; fonte?: string | null; errore?: string | null } | null;
  dati_fino_al?: string | null;
  funding_stimato_dal?: string | null;
  inizio_misura?: { giorni?: string | null; settimane?: string | null } | null;
  verdetto?: string | null;
  candidate?: CandidataPaper6[] | null;
  posizioni?: Record<string, { lunedi?: string | null; long?: PosizionePaper6[] | null; short?: PosizionePaper6[] | null }> | null;
  nuove_nell_universo?: string[] | null;
  strategie?: StrategiaPaper6[] | null;
  eventi_n3?: EventoN3[] | null;
  eventi_e4?: { simbolo?: string | null; data?: string | null; r7?: number | null }[] | null;
  settimana_in_corso?: Record<string, { lunedi?: string | null; fino_al?: string | null; netto_senza_costi?: number | null }> | null;
  passato?: Record<string, { mese?: string | null; valore?: number | null }[]> | null;
}

export interface StrategiaPaper6 {
  nome?: string | null;
  stato?: string | null;
  monete?: string | null;
  regola?: string | null;
  passato?: string | null;
}

export interface EventoN3 {
  mercato?: string | null;
  simbolo?: string | null;
  ingresso?: string | null;
  stato?: string | null;
  r?: number | null;
  fermata?: boolean | null;
}

const storePaper6 = creaDocumentoVivo<DocPaper6>('/paper6', 'dashboard', 'paper6');

export function usePaper6(): { doc: DocPaper6 | null; caricamento: boolean; etaS: number | null } {
  return useDocumentoVivo<DocPaper6>(storePaper6);
}
