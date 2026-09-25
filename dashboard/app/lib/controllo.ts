'use client';

/**
 * Il documento orario del CONTROLLO, letto dalla dashboard (25 set 2026).
 *
 * Il bot scrive ogni ora `dashboard/controllo` (Firestore) e il suo specchio
 * RTDB `/controllo`: due semafori («è rotto?», «perde?»), la salute, il paper,
 * il learning e la lista di cio' che il controllo NON puo' dare. Il contratto
 * dei campi e' `docs/controllo_schema.md` §1: i nomi qui sotto sono quelli, e
 * ogni campo e' facoltativo perche' `null` vuol dire «non misurato» e una
 * sezione puo' fallire da sola (fail-open: il resto del documento esce).
 *
 * UNA sola sottoscrizione per tutta la pagina: il documento e' letto una volta
 * dal RTDB (arriva in un colpo, niente query) e distribuito a tutti i pannelli
 * che chiamano `useControllo()`. Se il RTDB non risponde con un documento entro
 * 5 secondi (o risponde «vuoto»), si ripiega su Firestore `dashboard/controllo`:
 * lo specchio RTDB e' l'ultima scrittura del bot e puo' mancare dopo un reset.
 */
import { useEffect, useState } from 'react';
import { onValue, ref, type Unsubscribe } from 'firebase/database';
import { doc as fsDoc, onSnapshot } from 'firebase/firestore';
import { getDb, getRtdb } from './firebase';
import { durata } from './viz';

/* ========================================================================== */
/* Tipi — specchio di docs/controllo_schema.md §1                             */
/* ========================================================================== */

export type Semaforo = 'verde' | 'giallo' | 'rosso';
export type Gravita = 'rosso' | 'giallo' | 'info';
export type Famiglia = 'sistema' | 'paper';

/** §1.6 — una riga della lista `salute.anomalie`. */
export interface Anomalia {
  codice?: string | null;
  famiglia?: Famiglia | null;
  gravita?: Gravita | null;
  testo?: string | null;
  valore?: number | string | null;
  soglia?: number | string | null;
}

/** La testata che ogni sezione porta (contratto, «regole comuni»). */
export interface Testata {
  computed_at?: number | null;
  fonti?: string[] | null;
  lettura?: string | null;
  dettaglio?: string | null;
  errore?: string | null;
}

export interface ContaMotivo {
  motivo?: string | null;
  n?: number | null;
}

/** Una voce di distribuzione `[{valore, n}]` (regole comuni del contratto:
 *  le distribuzioni sono liste di coppie, mai liste di liste). Qui i due
 *  campi NON sono facoltativi: il bot li scrive sempre insieme, e i pannelli
 *  che disegnano le distribuzioni contano su `n` numerico. */
export interface ValoreN {
  valore: number | string;
  n: number;
}

export interface CoinPnl {
  coin?: string | null;
  pnl?: number | null;
}

export interface DataPnl {
  data?: string | null;
  pnl?: number | null;
}

export interface Giornata {
  data?: string | null;
  trades?: number | null;
  pnl?: number | null;
}

/** §1.1 */
export interface Meta {
  versione_schema?: number | null;
  generato_at?: number | null;
  generato_da?: 'bot' | 'github' | 'ops' | string | null;
  durata_ms?: number | null;
  precedente_at?: number | null;
  semaforo_sistema?: Semaforo | null;
  semaforo_paper?: Semaforo | null;
  errori?: string[] | null;
  fonte_impostazioni?: 'processo bot' | 'default repo' | string | null;
}

export interface CircuitBreaker {
  halted_for_day?: boolean | null;
  paused_until_ts?: number | null;
  macro_flat_until_ts?: number | null;
  consecutive_sl?: number | null;
  daily_pnl_pct?: number | null;
}

export interface Cooldown {
  nome?: string | null;
  fino_a?: number | null;
}

export interface PosizioneBreve {
  coin?: string | null;
  direzione?: string | null;
  rischio_pct?: number | null;
  upnl?: number | null;
}

/** §1.2 */
export interface Salute extends Testata {
  bot_stato?: string | null;
  heartbeat_at?: number | null;
  heartbeat_eta_s?: number | null;
  soglia_online_s?: number | null;
  avviato_at?: number | null;
  riavvii_24h?: number | null;
  errori_ciclo_1h?: number | null;
  price_stream?: boolean | null;
  dry_run?: boolean | null;
  kill_switch?: boolean | null;
  manutenzione?: boolean | null;
  regime?: string | null;
  fear_greed?: number | null;
  btc_24h_pct?: number | null;
  btc_7g_pct?: number | null;
  ultima_decisione_at?: number | null;
  ultima_decisione_esito?: 'flat' | 'aperta' | string | null;
  ultima_decisione_motivo?: string | null;
  asset_valutati?: number | null;
  segnali_trovati?: number | null;
  rifiuti_ciclo?: ContaMotivo[] | null;
  rifiuti_24h?: ContaMotivo[] | null;
  rifiuti_24h_dal?: number | null;
  gate_ultimo_giro_at?: number | null;
  gate_ultimo_giro_eta_s?: number | null;
  gate_stato?: 'in_corso' | 'finito' | 'errore' | string | null;
  gate_modalita?: string | null;
  gate_pronto?: boolean | null;
  registro_at?: number | null;
  pesi_at?: number | null;
  deriva_at?: number | null;
  calibrazione_at?: number | null;
  referti_at?: number | null;
  supervisore_at?: number | null;
  freno_globale?: boolean | null;
  freno_globale_dal?: number | null;
  circuit_breaker?: CircuitBreaker | null;
  cooldown_coin?: Cooldown[] | null;
  cooldown_strategie?: Cooldown[] | null;
  posizioni_aperte?: number | null;
  posizioni?: PosizioneBreve[] | null;
  upnl_totale?: number | null;
  tetto_posizioni?: number | null;
  tetto_posizioni_attivo?: boolean | null;
  rischio_aperto_pct?: number | null;
  rischio_long_pct?: number | null;
  rischio_short_pct?: number | null;
  tetto_direzione_pct?: number | null;
  wal_non_vuoto?: number | null;
  rtdb_degradato_s?: number | null;
  controllo_precedente_eta_s?: number | null;
  anomalie?: Anomalia[] | null;
}

export interface Ultimi30g {
  trades?: number | null;
  pnl?: number | null;
  pf?: number | null;
  win_rate?: number | null;
}

export interface Oggi {
  trades?: number | null;
  vinti?: number | null;
  pnl?: number | null;
  migliore?: CoinPnl | null;
  peggiore?: CoinPnl | null;
}

export interface Giornate {
  con_trade?: number | null;
  positive?: number | null;
  negative?: number | null;
  migliore?: DataPnl | null;
  peggiore?: DataPnl | null;
  ultime_7?: Giornata[] | null;
}

export interface Uscita {
  motivo?: string | null;
  etichetta?: string | null;
  trades?: number | null;
  quota?: number | null;
  pnl?: number | null;
}

export interface Gradino {
  gradino?: number | string | null;
  n?: number | null;
}

export interface Mfe {
  n?: number | null;
  mediana_r?: number | null;
  quota_1r?: number | null;
  quota_1_5r?: number | null;
  quota_3r?: number | null;
}

export interface Stop {
  totale?: number | null;
  sbagliati?: number | null;
  quasi?: number | null;
  oltre_primo_tp?: number | null;
  quasi_durata_mediana_h?: number | null;
  primo_gradino_r?: number | null;
  nota?: string | null;
}

export interface DirezioneStat {
  trade?: number | null;
  vinti?: number | null;
  pnl?: number | null;
  mfe_mediana?: number | null;
}

export interface Direzione {
  long?: DirezioneStat | null;
  short?: DirezioneStat | null;
}

export interface AllineamentoStat {
  trade?: number | null;
  pnl?: number | null;
}

export interface Allineamento {
  in_trend?: AllineamentoStat | null;
  contro?: AllineamentoStat | null;
  neutro?: AllineamentoStat | null;
  ignoto?: AllineamentoStat | null;
}

export interface Costi {
  totale?: number | null;
  per_trade?: number | null;
  commissioni?: number | null;
  spread?: number | null;
  funding?: number | null;
  lordo?: number | null;
  netto?: number | null;
  break_even_pct?: number | null;
  stimati?: boolean | null;
  avvisi?: string[] | null;
}

export interface Trailing {
  verdetti_totali?: number | null;
  prematuri?: number | null;
  protetti?: number | null;
  neutri?: number | null;
  verdetti_per_proposta?: number | null;
  prematuri_tf?: number | null;
  protetti_tf?: number | null;
  proposta_paper?: number | null;
  soglia?: number | null;
}

export interface Benchmark {
  btc_24h_pct?: number | null;
  btc_7g_pct?: number | null;
  nota?: string | null;
  portafoglio?: { lettura?: string | null; updated_at?: number | null } | null;
}

/** §1.3 */
export interface Paper extends Testata {
  equity?: number | null;
  equity_iniziale?: number | null;
  equity_iniziale_fonte?: 'rtdb' | 'default 1000' | string | null;
  paper_dal?: number | null;
  paper_dal_fonte?: 'rtdb' | 'primo trade' | string | null;
  giorni_paper?: number | null;
  rendimento_pct?: number | null;
  trades?: number | null;
  vinti?: number | null;
  perdite?: number | null;
  win_rate?: number | null;
  pnl_realizzato?: number | null;
  pf_vissuto?: number | null;
  expectancy?: number | null;
  ultimi_30g?: Ultimi30g | null;
  oggi?: Oggi | null;
  giornate?: Giornate | null;
  uscite?: Uscita[] | null;
  gradini?: Gradino[] | null;
  mfe?: Mfe | null;
  stop?: Stop | null;
  direzione?: Direzione | null;
  allineamento?: Allineamento | null;
  costi?: Costi | null;
  drawdown_portafoglio?: number | null;
  max_posizioni_insieme?: number | null;
  trailing?: Trailing | null;
  benchmark?: Benchmark | null;
}

export interface FrenoGlobale {
  attivo?: boolean | null;
  verdetto?: string | null;
  trades?: number | null;
  pf_vissuto?: number | null;
  pf_atteso?: number | null;
  pf_atteso_nota?: string | null;
  soglia_uscita_pf?: number | null;
  size_x?: number | null;
  leva_x_min?: number | null;
  motivo?: string | null;
  dal?: number | null;
}

export interface PesoPanchina {
  strategia?: string | null;
  regime?: string | null;
  peso?: number | null;
  campione?: number | null;
  win_rate?: number | null;
}

export interface Pesi {
  at?: number | null;
  aggiornato_da_nota?: string | null;
  versione?: number | null;
  campioni_sommati?: number | null;
  combinazioni?: number | null;
  soglia_panchina?: number | null;
  in_panchina_n?: number | null;
  spente_n?: number | null;
  in_panchina?: PesoPanchina[] | null;
}

export interface Tilt {
  trend_enabled?: boolean | null;
  trend_strength?: number | null;
  trend_floor?: number | null;
  sentiment_enabled?: boolean | null;
  sentiment_strength?: number | null;
}

export interface KeepPerCoppia {
  distribuzione?: ValoreN[] | null;
  non_rivalutate?: number | null;
}

export interface FrenoSerie {
  enabled?: boolean | null;
  perdite_soglia?: number | null;
  fattore?: number | null;
  serie?: { strategia?: string | null; perdite?: number | null }[] | null;
}

export interface Tetti {
  coin_giorno_pct?: number | null;
  direzione_pct?: number | null;
  max_posizioni?: number | null;
  max_posizioni_attivo?: boolean | null;
  correlate_max?: number | null;
}

export interface Impronta {
  freno?: boolean | null;
  panchina?: string[] | null;
  cooldown?: string[] | null;
  keep?: ValoreN[] | null;
  validate?: number | null;
  gate_pronto?: boolean | null;
}

/** §1.4 — `attivo`: cambia decisioni ORA. */
export interface LearningAttivo extends Testata {
  freno_globale?: FrenoGlobale | null;
  gate_pronto?: boolean | null;
  pesi?: Pesi | null;
  tilt?: Tilt | null;
  keep_per_coppia?: KeepPerCoppia | null;
  freno_serie?: FrenoSerie | null;
  tetti?: Tetti | null;
  cooldown_attivi?: number | null;
  calibrazione_trust?: number | null;
  impronta?: Impronta | null;
  cambiamenti_24h?: string[] | null;
}

export interface DerivaCoppia {
  coppia?: string | null;
  verdetto?: string | null;
  trades?: number | null;
  pf_vissuto?: number | null;
  pf_atteso?: number | null;
  motivo?: string | null;
}

export interface Deriva {
  at?: number | null;
  coppie_ok?: number | null;
  coppie_watch?: number | null;
  coppie_drift?: number | null;
  soglia_coppia?: number | null;
  soglia_strategia?: number | null;
  max_trades_coppia?: number | null;
  top?: DerivaCoppia[] | null;
}

export interface Calibrazione {
  at?: number | null;
  verdetto?: string | null;
  trades?: number | null;
  correlazione?: number | null;
  trust?: number | null;
  nota?: string | null;
}

export interface Referti {
  n_con_referto?: number | null;
  persi_con_referto?: number | null;
  ingresso?: number | null;
  uscita?: number | null;
  protezione?: number | null;
  stop_largo?: number | null;
  lock_mai?: number | null;
  controtrend?: number | null;
  ipotesi?: string[] | null;
}

export interface Selettore {
  at?: number | null;
  verdetti?: Record<string, string> | null;
  nota?: string | null;
}

/** §1.4 — `misurato`: solo osservato, non decide nulla. */
export interface LearningMisurato extends Testata {
  deriva?: Deriva | null;
  calibrazione?: Calibrazione | null;
  trailing?: Trailing | null;
  referti?: Referti | null;
  selettore?: Selettore | null;
  ombra_ai?: { n?: number | null; agree?: number | null; ultimo_at?: number | null } | null;
  ipotesi_ai?: { proposte?: number | null; accettate?: number | null; at?: number | null } | null;
  notturno_at?: number | null;
}

export interface Learning extends Testata {
  attivo?: LearningAttivo | null;
  misurato?: LearningMisurato | null;
}

/** §1.5 */
export interface Manca {
  evidenza?: string | null;
  perche?: string | null;
  come_avere?: string | null;
}

/** Il documento intero (`dashboard/controllo`). */
export interface Controllo {
  meta?: Meta | null;
  salute?: Salute | null;
  paper?: Paper | null;
  learning?: Learning | null;
  manca?: Manca[] | null;
}

/* ========================================================================== */
/* Attrezzi                                                                   */
/* ========================================================================== */

/**
 * Una lista, da qualunque forma sia arrivata. Il RTDB salva le liste come
 * oggetti con chiavi «0», «1», … e le rende come array solo se le chiavi sono
 * dense: con un buco (o dopo una scrittura parziale) arriva un oggetto. Qui
 * i pannelli ricevono sempre un array, vuoto se il dato manca.
 */
export function lista<T>(v: unknown): T[] {
  if (Array.isArray(v)) return v.filter((x) => x != null) as T[];
  if (v && typeof v === 'object') {
    return Object.values(v as Record<string, T>).filter((x) => x != null);
  }
  return [];
}

/** «aggiornato 12 min fa» sotto le due ore, «fermo da 3 h» oltre. */
export function etaTesto(etaS: number | null): string {
  if (etaS == null || !Number.isFinite(etaS)) return 'nessun controllo pubblicato';
  const s = Math.max(0, etaS);
  return s > FERMO_S ? `fermo da ${durata(s)}` : `aggiornato ${durata(s)} fa`;
}

/** Il colore (token CSS) di un semaforo; grigio se il semaforo non c'e'. */
export function semaforoColore(s: Semaforo | undefined | null): string {
  switch (s) {
    case 'verde':
      return 'var(--green)';
    case 'giallo':
      return 'var(--amber)';
    case 'rosso':
      return 'var(--red)';
    default:
      return 'var(--text-faint)';
  }
}

/** Il colore di una gravita' di anomalia (le `info` non colorano). */
export function gravitaColore(g: Gravita | undefined | null): string {
  if (g === 'rosso') return 'var(--red)';
  if (g === 'giallo') return 'var(--amber)';
  return 'var(--text-faint)';
}

export type StatoControllo = 'ok' | 'ritardo' | 'fermo' | 'assente';

/** Soglie dello stato: il bot scrive ogni ora (>= 3300 s), quindi sotto i 75
 *  minuti e' «ok», fino a due ore e' «ritardo» (un giro saltato), oltre e'
 *  «fermo» (anche il ripiego GitHub, ogni 2 h, non ha scritto). */
const RITARDO_S = 75 * 60;
const FERMO_S = 120 * 60;

export function statoDaEta(doc: unknown, etaS: number | null): StatoControllo {
  if (!doc || etaS == null || !Number.isFinite(etaS)) return 'assente';
  if (etaS < RITARDO_S) return 'ok';
  if (etaS <= FERMO_S) return 'ritardo';
  return 'fermo';
}

/* ========================================================================== */
/* La sottoscrizione condivisa                                                */
/* ========================================================================== */

/** Dopo quanti secondi senza un documento dal RTDB si ripiega su Firestore. */
const RIPIEGO_MS = 5000;
/** Ogni quanto i pannelli ricalcolano l'eta' (il documento non cambia, il
 *  tempo si'). */
const TICK_MS = 30000;

interface Documento {
  meta?: { generato_at?: number | null; iniziato_at?: number | null } | null;
}

export interface DocumentoVivo<T> {
  leggi(): { doc: T | null; caricamento: boolean };
  /** Registra un ascoltatore; il ritorno lo toglie. */
  abbonati(f: () => void): () => void;
}

/**
 * Un documento vivo condiviso da tutti i pannelli: UNA sottoscrizione RTDB al
 * primo che ascolta, chiusa quando l'ultimo smette. Con `n` pannelli che
 * chiamano l'hook non si aprono `n` letture dello stesso documento (che puo'
 * pesare 30-200 KB).
 */
export function creaDocumentoVivo<T extends Documento>(
  percorsoRtdb: string,
  collezione: string,
  docId: string,
): DocumentoVivo<T> {
  let doc: T | null = null;
  let caricamento = true;
  let ascoltatori = 0;
  let stopRtdb: Unsubscribe | null = null;
  let stopFs: Unsubscribe | null = null;
  let timer: ReturnType<typeof setTimeout> | null = null;
  const abbonati = new Set<() => void>();

  const avvisa = () => abbonati.forEach((f) => f());

  const generatoAt = (d: T | null): number =>
    Number(d?.meta?.generato_at ?? d?.meta?.iniziato_at ?? 0) || 0;

  /** Prende il documento solo se e' piu' nuovo di quello che gia' abbiamo:
   *  RTDB e Firestore portano la stessa scrittura, ma non nello stesso istante. */
  const accogli = (nuovo: T | null) => {
    if (nuovo && (doc == null || generatoAt(nuovo) >= generatoAt(doc))) doc = nuovo;
    caricamento = false;
    avvisa();
  };

  const ripiegaSuFirestore = () => {
    if (stopFs) return;
    try {
      stopFs = onSnapshot(
        fsDoc(getDb(), collezione, docId),
        (snap) => accogli(snap.exists() ? (snap.data() as T) : null),
        () => {
          caricamento = false;
          avvisa();
        },
      );
    } catch {
      caricamento = false;
      avvisa();
    }
  };

  const avvia = () => {
    let arrivato = false;
    try {
      stopRtdb = onValue(
        ref(getRtdb(), percorsoRtdb),
        (snap) => {
          const v = snap.exists() ? (snap.val() as T) : null;
          if (v) {
            arrivato = true;
            accogli(v);
          } else {
            // il RTDB ha risposto «niente»: non aspettiamo i 5 secondi
            ripiegaSuFirestore();
          }
        },
        () => ripiegaSuFirestore(),
      );
    } catch {
      ripiegaSuFirestore();
    }
    timer = setTimeout(() => {
      if (!arrivato) ripiegaSuFirestore();
    }, RIPIEGO_MS);
  };

  const ferma = () => {
    if (timer) clearTimeout(timer);
    timer = null;
    if (stopRtdb) stopRtdb();
    stopRtdb = null;
    if (stopFs) stopFs();
    stopFs = null;
  };

  return {
    leggi: () => ({ doc, caricamento }),
    abbonati(f: () => void): () => void {
      abbonati.add(f);
      if (ascoltatori++ === 0) avvia();
      return () => {
        abbonati.delete(f);
        if (--ascoltatori === 0) ferma();
      };
    },
  };
}

/** L'hook comune ai due documenti: documento, caricamento, eta' in secondi. */
export function useDocumentoVivo<T extends Documento>(
  store: DocumentoVivo<T>,
): { doc: T | null; caricamento: boolean; etaS: number | null } {
  const [stato, setStato] = useState<{ doc: T | null; caricamento: boolean }>(() => store.leggi());
  const [adesso, setAdesso] = useState(() => Date.now());

  useEffect(() => {
    const aggiorna = () => setStato(store.leggi());
    const stop = store.abbonati(aggiorna);
    aggiorna();
    const tick = setInterval(() => setAdesso(Date.now()), TICK_MS);
    return () => {
      stop();
      clearInterval(tick);
    };
  }, [store]);

  const at = stato.doc?.meta?.generato_at ?? stato.doc?.meta?.iniziato_at ?? null;
  const etaS = at != null && Number.isFinite(Number(at)) ? Math.max(0, Math.floor(adesso / 1000 - Number(at))) : null;
  return { doc: stato.doc, caricamento: stato.caricamento, etaS };
}

const storeControllo = creaDocumentoVivo<Controllo>('/controllo', 'dashboard', 'controllo');

/**
 * Il controllo orario, per i pannelli. `etaS` e' l'eta' di `meta.generato_at`
 * ricalcolata ogni 30 s; `stato`: ok sotto i 75 min, ritardo fino a 2 h,
 * fermo oltre, assente se il documento non c'e' (o non e' ancora arrivato).
 */
export function useControllo(): {
  doc: Controllo | null;
  caricamento: boolean;
  etaS: number | null;
  stato: StatoControllo;
} {
  const { doc, caricamento, etaS } = useDocumentoVivo<Controllo>(storeControllo);
  return { doc, caricamento, etaS, stato: statoDaEta(doc, etaS) };
}
