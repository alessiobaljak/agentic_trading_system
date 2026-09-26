'use client';

/**
 * Il documento del GATE, letto dalla dashboard (25 set 2026).
 *
 * Lo scrive la discovery a ogni giro (ogni 3 ore, completo alle 03:30 UTC):
 * `dashboard/gate` su Firestore e lo specchio RTDB `/gate`. Il contratto dei
 * campi e' `docs/controllo_schema.md` §2. All'inizio del giro arriva solo
 * `meta.stato = in_corso` (le sezioni restano quelle del giro precedente);
 * a fine giro il documento intero.
 *
 * La lettura passa dalla stessa sottoscrizione condivisa di `controllo.ts`
 * (RTDB, ripiego Firestore dopo 5 s): un documento solo per tutti i pannelli.
 */
import { creaDocumentoVivo, useDocumentoVivo, type Testata, type ValoreN } from './controllo';

/* ========================================================================== */
/* Tipi — specchio di docs/controllo_schema.md §2                             */
/* ========================================================================== */

/** §2.1 */
export interface MetaGate {
  versione_schema?: number | null;
  stato?: 'in_corso' | 'finito' | 'errore' | string | null;
  fase?: 'optimize' | 'discover' | 'passata_1h' | string | null;
  errore?: string | null;
  iniziato_at?: number | null;
  generato_at?: number | null;
  durata_s?: number | null;
  modalita?: 'completa' | 'solo urgenti' | string | null;
  generato_da?: string | null;
}

export interface Passata {
  coin?: string | null;
  id?: string | null;
  pf?: number | null;
  pnl?: number | null;
}

export interface Candidate {
  totale?: number | null;
  ai?: number | null;
  varianti_referti?: number | null;
  intorno?: number | null;
  casuali?: number | null;
  semi?: number | null;
  gemelle_scartate?: number | null;
  rivalutate?: number | null;
}

/** §2.2 — ogni sezione del gate porta la testata comune (`Testata`): la
 *  discovery la scrive per giro/registro/cervello/strategie, con `errore` se
 *  la sezione e' fallita (fail-open per sezione, come nel controllo). */
export interface Giro extends Testata {
  coin_valutate?: number | null;
  valutazioni?: number | null;
  passate?: number | null;
  passate_lista?: Passata[] | null;
  spec_note?: number | null;
  spec_rivalutate?: number | null;
  spec_con_conferme?: number | null;
  spec_tagliate?: number | null;
  tetto_rivalutazione?: number | null;
  candidate?: Candidate | null;
  passata_1h?: {
    at?: number | null;
    durata_s?: number | null;
    coin?: number | null;
    valutazioni?: number | null;
    passate?: number | null;
  } | null;
  worker?: number | null;
  rss_max_mb?: number | null;
  paper_propone?: {
    scala?: string | null;
    keep?: number | null;
    verdetti_trailing?: number | null;
  } | null;
  ipotesi_uscita?: {
    strategie?: number | null;
    con_scala?: number | null;
  } | null;
  /** (26 set 2026) quante validate sono passate SOLO grazie alla propria
   *  configurazione d'uscita (col passo 1 sulla globale sarebbero state
   *  bocciate): misura dell'artefatto, non una decisione; null se non contata */
  passate_solo_con_propria_config?: number | null;
  /** il paper esplorativo (25 set 2026, F1bis): coppie esplorative attive dopo
   *  il giro e il metro dell'esperimento (poi validate / scartate) */
  esplorative?: {
    attive?: number | null;
    validate_poi?: number | null;
    scartate?: number | null;
  } | null;
  /** il giro completo RIDOTTO (26 set 2026, backlog J10): le spec note valutate
   *  solo sulle coin proprie + la fetta rotante del giorno (`fetta` = «g/7»);
   *  `valutazioni_stimate` si confronta con `valutazioni`; null se non ridotto */
  riduzione?: {
    spec_note?: number | null;
    coin_proprie?: number | null;
    fetta?: string | null;
    valutazioni_stimate?: number | null;
  } | null;
}

export interface DistribuzionePass {
  pass?: number | null;
  coppie?: number | null;
  coin?: number | null;
}

export interface StatisticaT {
  misurate?: number | null;
  sopra_2?: number | null;
  sopra_3?: number | null;
  mediana?: number | null;
  piu_basse?: { coppia?: string | null; t?: number | null }[] | null;
}

/** §2.3 */
export interface Registro extends Testata {
  validate?: number | null;
  coin_coperte?: number | null;
  universo?: number | null;
  copertura?: number | null;
  obiettivo_copertura?: number | null;
  pronto?: boolean | null;
  pronto_per?: 'copertura' | 'numero coppie' | string | null;
  distribuzione_pass?: DistribuzionePass[] | null;
  congelate?: number | null;
  a_un_passo?: number | null;
  finestre_scadute?: number | null;
  coppie?: number | null;
  base?: number | null;
  generate?: number | null;
  generate_con_conferme?: number | null;
  occupazione?: number | null;
  limite?: number | null;
  alleggerito?: boolean | null;
  senza_promessa?: number | null;
  statistica_t?: StatisticaT | null;
  validate_delta_giro?: number | null;
  /** (26 set 2026) validate DECLASSATE: bocciate dal giro completo del gate per
   *  due notti di fila, operate dal bot a un quarto della size finche' non
   *  ripassano */
  declassate?: number | null;
}

export interface Intorno {
  madri?: number | null;
  figlie_passate?: number | null;
  promosse?: string[] | null;
  senza_margine?: number | null;
  madre_non_valutata?: number | null;
  scartate?: number | null;
  ultimo_completo_at?: number | null;
}

export interface Varianti {
  create?: number | null;
  passate?: number | null;
  retro_ok?: number | null;
  promosse?: string[] | null;
  scartate?: number | null;
  sostituzioni?: { figlia?: string | null; madre?: string | null }[] | null;
}

export interface KeepGiro {
  scelti?: ValoreN[] | null;
  non_scelto?: number | null;
  dal_paper?: number | null;
  dal_paper_n?: number | null;
}

export interface Autopsia {
  at?: number | null;
  valutazioni?: number | null;
  passate?: number | null;
  quota?: number | null;
  criterio_principale?: string | null;
  quota_criterio?: number | null;
  quasi_passaggi?: number | null;
}

/** §2.4 */
export interface Cervello extends Testata {
  riga?: string | null;
  intorno?: Intorno | null;
  varianti?: Varianti | null;
  keep_giro?: KeepGiro | null;
  keep_validate?: { distribuzione?: ValoreN[] | null; non_rivalutate?: number | null } | null;
  scala_validate?: { scala?: string | null; n: number }[] | null;
  breakeven_validate?: number | null;
  autopsia?: Autopsia | null;
  autopsia_base_congelata_da_s?: number | null;
  supervisore?: {
    at?: number | null;
    ultima_decisione?: { kind?: string | null; reason?: string | null } | null;
    decisioni_none_di_fila?: number | null;
  } | null;
}

export interface PaperCoppia {
  trades?: number | null;
  vinti?: number | null;
  pnl?: number | null;
  pf_vissuto?: number | null;
  perdite?: number | null;
  verdetto?: string | null;
  motivo?: string | null;
}

export interface Operata {
  chiave?: string | null;
  coin?: string | null;
  strategia?: string | null;
  famiglia?: string | null;
  origine?: string | null;
  genitore?: string | null;
  ipotesi?: string | null;
  pass?: number | null;
  validata_at?: number | null;
  ultimo_pass_at?: number | null;
  pf_promesso?: number | null;
  pnl_promesso_pct?: number | null;
  t?: number | null;
  holdout_ok?: boolean | null;
  scala?: string | null;
  breakeven?: boolean | null;
  keep?: number | null;
  direzione_pf?: { long?: number | null; short?: number | null } | null;
  paper?: PaperCoppia | null;
}

export interface PerFamiglia {
  famiglia?: string | null;
  coppie?: number | null;
  coin?: number | null;
  pf_promesso_mediano?: number | null;
  paper_trades?: number | null;
  paper_pnl?: number | null;
  paper_pf?: number | null;
}

export interface PerCoin {
  coin?: string | null;
  coppie?: number | null;
  paper_trades?: number | null;
  paper_pnl?: number | null;
}

/** §2.5 */
export interface Strategie extends Testata {
  n_operate?: number | null;
  n_con_paper?: number | null;
  n_senza_promessa?: number | null;
  n_sostituite?: number | null;
  n_nate_intorno?: number | null;
  n_da_referto?: number | null;
  n_scadute_dal_giro?: number | null;
  operate?: Operata[] | null;
  operate_troncate?: number | null;
  per_famiglia?: PerFamiglia[] | null;
  per_coin?: PerCoin[] | null;
  promessa_vs_vissuto?: {
    pf_promesso_mediano_operate?: number | null;
    pf_atteso_media_registro?: number | null;
    pf_vissuto_30g?: number | null;
  } | null;
  vite?: { promosse_7g?: number | null; rimosse_7g?: number | null; parziale?: boolean | null } | null;
}

/** Il documento intero (`dashboard/gate`). */
export interface DocGate {
  meta?: MetaGate | null;
  giro?: Giro | null;
  registro?: Registro | null;
  cervello?: Cervello | null;
  strategie?: Strategie | null;
}

const storeGate = creaDocumentoVivo<DocGate>('/gate', 'dashboard', 'gate');

/**
 * Il documento del gate, per i pannelli. `etaS` e' l'eta' di `meta.generato_at`
 * (o di `iniziato_at` mentre il giro e' in corso), ricalcolata ogni 30 s.
 */
export function useGateDoc(): { doc: DocGate | null; caricamento: boolean; etaS: number | null } {
  return useDocumentoVivo<DocGate>(storeGate);
}
